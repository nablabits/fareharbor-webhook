from datetime import date

import attr
import pytz
from flask import current_app
from sqlalchemy import func

from fh_webhook.models import Availability, Bike, Booking, Contact, Item, db


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

    def _get_tour_activities(self):
        tour_ids = (
            self.bike_tracker_items["regular_tours"]
            + self.bike_tracker_items["private_tours"]
        )
        return (
            db.session.query(
                Availability.id,
                Availability.headline,
                Availability.start_at,
                Item.name,
                func.sum(Booking.customer_count) + 1,
            )
            .filter(Booking.availability_id == Availability.id)
            .filter(Item.id == Availability.item_id)
            .filter(func.DATE(Availability.start_at) == self.for_date)
            .filter(Item.id.in_(tour_ids))
            .filter(Booking.status != "cancelled")
            .filter(Booking.rebooked_to.is_(None))
            .group_by(
                Availability.id, Availability.headline, Availability.start_at, Item.name
            )
            .order_by(Availability.start_at.asc())
            .all()
        )

    def _get_rental_activities(self):
        rental_ids = self.bike_tracker_items["rentals"]
        return (
            db.session.query(
                Booking.id,
                func.concat(Contact.name, "-", Item.name),
                Availability.start_at,
                Item.name,
                func.sum(Booking.customer_count),
            )
            .filter(Booking.availability_id == Availability.id)
            .filter(Booking.id == Contact.id)
            .filter(Item.id == Availability.item_id)
            .filter(func.DATE(Availability.start_at) == self.for_date)
            .filter(Item.id.in_(rental_ids))
            .filter(Booking.status != "cancelled")
            .filter(Booking.rebooked_to.is_(None))
            .group_by(Booking.id, Contact.name, Availability.start_at, Item.name)
            .order_by(Availability.start_at.asc())
            .all()
        )

    def run(self):
        activities_queryset = (
            self._get_tour_activities() + self._get_rental_activities()
        )
        mad = pytz.timezone("Europe/Madrid")
        activities = list()
        for activity in activities_queryset:
            activities.append(
                {
                    "availability_id": activity[0],
                    "headline": activity[1] or activity[3],
                    "timestamp": activity[2].astimezone(mad).strftime("%X"),
                    "no_of_bikes": activity[4],
                }
            )
        return activities


def get_available_bikes():
    query_bikes = db.session.query(Bike.uuid, Bike.readable_name).all()
    return [{"uuid": row[0], "display_name": row[1]} for row in query_bikes]
