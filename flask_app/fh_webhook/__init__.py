import os
import json
from datetime import datetime, timezone

from flask import Flask, request, Response
from flask_migrate import Migrate
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db
from .model_services import CreateStoredRequest, CloseStoredRequest
from .services import (
    ProcessJSONResponse, SaveResponseAsFile, get_request_id_or_none,
    CheckForNewKeys, SSLSMTPHandler
)

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
            filename = SaveResponseAsFile(json_response, path, timestamp).run()
        else:
            app.logger.error("The request was empty")
            return Response("The request was empty", status=400)

        stored_request = CreateStoredRequest(
            request_id=get_request_id_or_none(filename),
            filename=filename,
            body=json.dumps(json_response),
            timestamp=timestamp,
        ).run()
        try:
            ProcessJSONResponse(json_response, timestamp).run()
        except KeyError as e:
            # It can happen that we got less data than expected
            app.logger.error(
                "The request was missing data " +
                f"(stored_request_id={stored_request.id}, error={e.args})"

            )
            return Response(
                f"The request was missing data. ({e.args})",
                status=400)

        CloseStoredRequest(stored_request).run()

        # Finally check for new keys that FH friends could skneakily insert.
        new_keys = CheckForNewKeys(json_response).run()
        if new_keys:
            for name, key in new_keys:
                app.logger.warning(f"New key found in {name}: {key}")

        app.logger.info(
            f"Request {stored_request.id} successfully processed."
        )
        return Response(status=200)

    @app.route("/test", methods=["GET"])
    def index():
        """Quick check that the server is running."""
        app.logger.info("New request received.")
        app_name = os.getenv("APP_NAME")
        if app_name:
            return "Hello from flask on a Docker environment"
        return "Hello from Flask"

    return app
