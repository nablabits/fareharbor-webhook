from datetime import date, datetime, timezone

import jwt
from flask import Blueprint, Response, current_app, jsonify, request
from marshmallow.validate import ValidationError

from fh_webhook.auth import get_auth
from fh_webhook.bike_tracker_services import DailyActivities, get_available_bikes
from fh_webhook.decorators import validate_token
from fh_webhook.model_services import CreateBikeUsages, UpdateBikeUsage
from fh_webhook.schema import AddBikesSchema, ReplaceBikesSchema

bp = Blueprint("bike_tracker", __name__, url_prefix="/bike-tracker")


auth = get_auth()


@bp.route("/get-services/", methods=["GET"])
@auth.login_required
def get_services():
    """Send the services of the day to the bike_tracker app."""
    logger = current_app.logger
    default_date = date.today()
    if request.args.get("test"):
        default_date = date(2021, 8, 10)

    # Get the relevant data
    data = {
        "availabilities": DailyActivities(for_date=default_date).run(),
        "bike_uuids": get_available_bikes(),
    }

    # Encode the information
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

    # Despite what the argument suggests, this service works as well for booking ids. Still, we
    # keep the `data["availability_id"]` for compatibility reasons.
    result = CreateBikeUsages(
        instance_id=data["availability_id"],
        bike_uuids=data["bikes"],
        timestamp=datetime.now(timezone.utc),
    ).run()
    if result.failure:
        logger.error(f"Request failed: {result.errors}")
        return result.errors, 404
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
    result = UpdateBikeUsage(
        instance_id=data["availability_id"],
        bike_picked_uuid=data["bike_picked"],
        bike_returned_uuid=data["bike_returned"],
        timestamp=datetime.now(timezone.utc),
    ).run()

    if result.failure:
        logger.error(f"Request failed: {result.errors}")
        return result.errors, 404
    logger.info(f"Successful request: {request}")
    return Response(status=200)
