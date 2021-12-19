import os
from datetime import date

import jwt
from flask import Blueprint, Response, current_app, jsonify, request
from marshmallow.validate import ValidationError
from sqlalchemy import func

from fh_webhook.auth import get_auth
from fh_webhook.decorators import validate_token
from fh_webhook.models import Availability, Booking, Item, db
from fh_webhook.schema import AddBikesSchema, ReplaceBikesSchema
from fh_webhook.services import GetBikeUUIDs

bp = Blueprint("bike_tracker", __name__, url_prefix="/bike-tracker")


auth = get_auth()


@bp.route("/get-services/", methods=["GET"])
@auth.login_required
def get_services():
    """Send the services of the day to the bike_tracker app."""
    logger = current_app.logger
    bike_tracker_items = current_app.config["BIKE_TRACKER_ITEMS"]
    default_date = date.today()
    if request.args.get("test"):
        default_date = date(2021, 8, 10)
    activities = (
        db.session.query(
            Availability.id,
            Availability.headline,
            Availability.start_at,
            Item.name,
            func.sum(Booking.customer_count),
        )
        .filter(Booking.availability_id == Availability.id)
        .filter(Item.id == Availability.item_id)
        .filter(func.DATE(Availability.start_at) == default_date)
        .filter(Item.id.in_(bike_tracker_items))
        .filter(Booking.status != "cancelled")
        .filter(Booking.rebooked_to is not None)
        .group_by(
            Availability.id, Availability.headline, Availability.start_at, Item.name
        )
        .all()
    )
    data = {
        "availabilities": list(),
    }
    for activity in activities:
        data["availabilities"].append(
            {
                "availability_id": activity[0],
                "headline": activity[1] or activity[3],
                "timestamp": activity[2].strftime("%X"),
                "no_of_bikes": activity[4],
            }
        )
    data.update({"bike_uuids": GetBikeUUIDs().run()})
    key = current_app.config.get("BIKE_TRACKER_SECRET")
    token = jwt.encode(payload=data, key=key)

    logger.info(f"Successful request: {request}")
    return jsonify(token)


@bp.route("/add-bikes/", methods=["POST"])
@auth.login_required
@validate_token
def bike_tracker_test_add_bikes(data):
    logger = current_app.logger
    try:
        AddBikesSchema().load(data)
    except ValidationError as e:
        logger.error(f"Validation failed for add-bike request, error: {e}")
        return Response(str(e), status=400)
    # Add here the service that handles the data and stores it in the db.
    logger.info(f"Successful request: {request}")
    return Response(status=200)


@bp.route("/replace-bike/", methods=["PUT"])
@auth.login_required
@validate_token
def bike_tracker_test_replace_bike(data):
    logger = current_app.logger
    try:
        ReplaceBikesSchema().load(data)
    except ValidationError as e:
        logger.error(f"Validation failed for add-bike request, error: {e}")
        return Response(str(e), status=400)
    # Add here the service that handles the data and stores it in the db.
    logger.info(f"Successful request: {request}")
    return Response(status=200)
