import os
from datetime import datetime, timezone

from flask import Flask, request, Response
from flask_migrate import Migrate
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db
from .services import SaveResponseAsFile, SaveRequestToDB
from fh_webhook.schema import BookingSchema
from marshmallow.validate import ValidationError

from decouple import config


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
    users = {
        "fareharbor": generate_password_hash(fh_pass),
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
                app.logger.error(
                    f"filename={timestamp.timestamp()}.json, error={e}"
                )
                return Response(str(e), status=400)

            # if validation succeeds we save the response right away to keep
            # the data
            filename = SaveResponseAsFile(json_response, path, timestamp).run()

        else:
            app.logger.error("The request was empty")
            return Response("The request was empty", status=400)

        stored_request = SaveRequestToDB(
            json_response, timestamp, filename
        ).run()

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

    return app
