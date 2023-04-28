import os
from datetime import datetime, timezone

from flask import Blueprint, Response, current_app, request
from marshmallow.validate import ValidationError

from fh_webhook.auth import get_auth
from fh_webhook.schema import BookingSchema
from fh_webhook.services import SaveRequestToDB, SaveResponseAsFile

bp = Blueprint("webhook", __name__, url_prefix="/")
auth = get_auth()


@bp.route("test/", methods=["GET"])
def index():
    """Quick check that the server is running."""
    logger = current_app.logger
    logger.info("New request received.")
    app_name = os.getenv("APP_NAME")
    if app_name:
        return "Hello from flask on a Docker environment"
    return "Hello from Flask"


@bp.route("/", methods=["POST"])
@auth.login_required
def save_content():
    """Process the requests made by FH."""
    logger = current_app.logger
    logger.info("New FH request received.")
    path = current_app.config.get("RESPONSES_PATH")
    json_response = request.json
    timestamp = datetime.now(timezone.utc)
    if json_response:
        # Let's save the data first of all, so we can populate the database if some error occurs.
        filename = SaveResponseAsFile(json_response, path, timestamp).run()

        try:
            BookingSchema().load(json_response["booking"])
        except ValidationError as e:
            logger.error(f"filename={timestamp.timestamp()}.json, error={e}")
            return Response(str(e), status=400)

    else:
        logger.error("The request was empty")
        return Response("The request was empty", status=400)

    stored_request = SaveRequestToDB(json_response, timestamp, filename).run()

    if stored_request:
        message = f"Request {stored_request.id} successfully processed."
        logger.info(message)
        return Response(status=200)
    return Response(status=500)
