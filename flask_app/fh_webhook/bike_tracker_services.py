import logging
from datetime import date
from decimal import Decimal

import attr
import pytz
from flask import current_app
from sqlalchemy import func

from fh_webhook.models import (
    Availability,
    Bike,
    Booking,
    Contact,
    Customer,
    CustomerType,
    CustomerTypeRate,
    Item,
    db,
    bike_usages,
)


@attr.s
class DailyActivities:
    """
    Get the set of activities that are subject to be tracked for a given date.

    We need to provide the activities available for the day to the app, so the user can assign the
    bikes that belong to that booking.
    """

    for_date = attr.ib(validator=attr.validators.instance_of(date))

    def __attrs_post_init__(self):
        self.bike_tracker_items = current_app.config["BIKE_TRACKER_ITEMS"]

    def _get_tour_activities(self, tracked_availability_ids):
        tour_ids = (
            self.bike_tracker_items["regular_tours"]
            + self.bike_tracker_items["private_tours"]
        )

        return (
            db.session.query(
                Availability.id,
                Availability.headline,
                Availability.start_at,
                Availability.end_at - Availability.start_at,
                Item.name,
                func.sum(Booking.customer_count) + 1,
            )
            .filter(Booking.availability_id == Availability.id)
            .filter(Item.id == Availability.item_id)
            .filter(func.DATE(Availability.start_at) == self.for_date)
            .filter(Item.id.in_(tour_ids))
            .filter(Booking.status != "cancelled")
            .filter(Booking.rebooked_to.is_(None))
            .filter(Availability.id.notin_(tracked_availability_ids))
            .group_by(
                Availability.id,
                Availability.headline,
                Availability.start_at,
                Availability.end_at,
                Item.name,
            )
            .order_by(Availability.start_at.asc())
            .all()
        )

    def _get_rental_activities(self, tracked_availability_ids):
        rental_ids = self.bike_tracker_items["rentals"]

        return (
            db.session.query(
                Booking.id,
                func.concat(Contact.name, "-", Item.name),
                Availability.start_at,
                Availability.end_at - Availability.start_at,
                Item.name,
                func.count(Booking.id),
                CustomerType.id,
            )
            # Join
            .filter(Booking.availability_id == Availability.id)
            .filter(Booking.id == Contact.id)
            .filter(Item.id == Availability.item_id)
            .filter(Customer.booking_id == Booking.id)
            .filter(CustomerTypeRate.id == Customer.customer_type_rate_id)
            .filter(CustomerType.id == CustomerTypeRate.customer_type_id)
            # Where
            .filter(func.DATE(Availability.start_at) == self.for_date)
            .filter(Item.id.in_(rental_ids))
            .filter(Booking.status != "cancelled")
            .filter(Booking.rebooked_to.is_(None))
            .filter(Availability.id.notin_(tracked_availability_ids))
            .group_by(
                Booking.id,
                Contact.name,
                Availability.start_at,
                Availability.end_at,
                CustomerType.id,
                Item.name,
            )
            .order_by(Availability.start_at.asc())
            .all()
        )

    def _get_availabilities_with_bike_assigned(self):
        results = (
            db.session.query(Availability.id)
            .join(bike_usages, Availability.id == bike_usages.c.availability_id)
            .filter(func.DATE(Availability.start_at) == self.for_date)
            .filter(bike_usages.c.bike_id.isnot(None))
        )
        return [row[0] for row in results]

    @staticmethod
    def _compute_duration(activity):
        """
        Compute the booking duration

        We need to know how long the activity last in order to release bikes so, they can be picked
        up again the same day. For tours, we get that duration right from the start and
        end date of the availability. However, for rentals, it's a bit trickier as the duration is
        represented by the customer type so, we need a mapping to ct ids. If, for some reason, the
        ct is not in this mapping, we assign the default of 2h
        """
        if len(activity) == 6:
            return round(Decimal(activity[3].seconds) / 3600, 1)

        duration_map = current_app.config["DURATION_MAP"]
        duration = duration_map.get(activity[6])
        if not duration:
            logging.error(
                "The customer type does not exist. Sending default duration (2h)"
            )
            duration = "2.0"
        return Decimal(duration)

    def run(self):
        tracked_availability_ids = self._get_availabilities_with_bike_assigned()
        activities_queryset = self._get_tour_activities(
            tracked_availability_ids
        ) + self._get_rental_activities(tracked_availability_ids)
        mad = pytz.timezone("Europe/Madrid")
        activities = list()
        for activity in activities_queryset:
            activities.append(
                {
                    "availability_id": activity[0],
                    "headline": activity[1] or activity[4],
                    "timestamp": activity[2].astimezone(mad).strftime("%X"),
                    "no_of_bikes": activity[5],
                    "duration": str(self._compute_duration(activity)),
                }
            )
        return activities


def get_available_bikes():
    query_bikes = db.session.query(Bike.uuid, Bike.readable_name).all()
    return [{"uuid": row[0], "display_name": row[1]} for row in query_bikes]
