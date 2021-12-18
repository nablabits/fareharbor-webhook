import os
from datetime import date, datetime, timezone

import jwt
from decouple import config
from flask import Flask, Response, jsonify, request
from flask_httpauth import HTTPBasicAuth
from flask_migrate import Migrate
from marshmallow.validate import ValidationError
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash

from fh_webhook.schema import AddBikesSchema, BookingSchema, ReplaceBikesSchema

from .decorators import validate_token
from .models import Availability, Booking, Item, db
from .services import GetBikeUUIDs, SaveRequestToDB, SaveResponseAsFile


def create_app(test_config=False):
    """Serve the entry points for the webhook."""
    app = Flask(__name__, instance_relative_config=True)
    if test_config:
        app.config.from_object("config.TestingConfig")
    else:
        app.config.from_object(config("APP_SETTINGS"))

    app.logger.info("Starting flask app.")
    db.init_app(app)
    Migrate(app, db)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # load auth
    auth = HTTPBasicAuth()
    fh_pass = app.config["FH_PASSWORD"]
    bike_tracker_pass = app.config["BIKE_TRACKER_PASS"]
    users = {
        "fareharbor": generate_password_hash(fh_pass),
        "bike_tracker": generate_password_hash(bike_tracker_pass),
    }
    test_pass = app.config.get("TEST_PASSWORD")
    if test_pass:
        users["test"] = generate_password_hash(test_pass)

    @auth.verify_password
    def verify_password(username, password):
        user_exists = username in users
        if user_exists and check_password_hash(users.get(username), password):
            return username
        else:
            app.logger.info("Authentication failed.")

    @app.route("/", methods=["POST"])
    @auth.login_required
    def save_content():
        """Process the requests made by FH."""
        app.logger.info("New FH request received.")
        path = app.config.get("RESPONSES_PATH")
        json_response = request.json
        timestamp = datetime.now(timezone.utc)
        if json_response:
            try:
                BookingSchema().load(json_response["booking"])
            except ValidationError as e:
                app.logger.error(f"filename={timestamp.timestamp()}.json, error={e}")
                return Response(str(e), status=400)

            # if validation succeeds we save the response right away to keep
            # the data
            filename = SaveResponseAsFile(json_response, path, timestamp).run()

        else:
            app.logger.error("The request was empty")
            return Response("The request was empty", status=400)

        stored_request = SaveRequestToDB(json_response, timestamp, filename).run()

        if stored_request:
            message = f"Request {stored_request.id} successfully processed."
            app.logger.info(message)
            return Response(status=200)
        return Response(status=500)

    @app.route("/test", methods=["GET"])
    def index():
        """Quick check that the server is running."""
        app.logger.info("New request received.")
        app_name = os.getenv("APP_NAME")
        if app_name:
            return "Hello from flask on a Docker environment"
        return "Hello from Flask"

    # TODO: change endpoint to /bike-tracker/get-services/ and add auth.
    @app.route("/bike-tracker-test/", methods=["GET"])
    def bike_tracker_test():
        """Endpoint to exchange information with the bike_tracker app."""
        bike_tracker_items = app.config["BIKE_TRACKER_ITEMS"]
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
            .filter(func.DATE(Availability.start_at) == date(2021, 8, 10))
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
        data.update({"bike_uuids": GetBikeUUIDs(app).run()})
        key = app.config.get("BIKE_TRACKER_SECRET")
        token = jwt.encode(payload=data, key=key)

        return jsonify(token)

    @app.route("/bike-tracker/add-bikes/", methods=["POST"])
    @auth.login_required
    @validate_token
    def bike_tracker_test_add_bikes(data):
        try:
            AddBikesSchema().load(data)
        except ValidationError as e:
            app.logger.error(f"Validation failed for add-bike request, error: {e}")
            return Response(str(e), status=400)
        # Add here the service that handles the data and stores it in the db.
        return Response(status=200)

    @app.route("/bike-tracker/replace-bike/", methods=["PUT"])
    @auth.login_required
    @validate_token
    def bike_tracker_test_replace_bike(data):
        try:
            ReplaceBikesSchema().load(data)
        except ValidationError as e:
            app.logger.error(f"Validation failed for add-bike request, error: {e}")
            return Response(str(e), status=400)
        # Add here the service that handles the data and stores it in the db.
        return Response(status=200)

    return app
