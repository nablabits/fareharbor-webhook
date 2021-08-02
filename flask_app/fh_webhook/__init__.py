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
    ProcessJSONResponse, SaveResponseAsFile, get_request_id_or_none
)

from decouple import config


def create_app(test_config=False):
    """Serve the entry points for the webhook."""
    app = Flask(__name__, instance_relative_config=True)
    if test_config:
        app.config.from_object("config.TestingConfig")
    else:
        app.config.from_object(config("APP_SETTINGS"))
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

    @app.route("/", methods=["POST"])
    @auth.login_required
    def save_content():
        """Process the requests made by FH."""
        path = app.config.get("RESPONSES_PATH")
        json_response = request.json
        timestamp = datetime.now(timezone.utc)
        if json_response:
            filename = SaveResponseAsFile(json_response, path, timestamp).run()
        else:
            # Log this in a proper way.
            with open(os.path.join(path, "errors.log"), "a") as f:
                f.write("{} - the request was empty\n".format(datetime.now()))
            return Response("The request was empty", status=400)

        stored_request = CreateStoredRequest(
            request_id=get_request_id_or_none(filename),
            filename=filename,
            body=json.dumps(json_response),
            timestamp=timestamp,
        ).run()
        ProcessJSONResponse(json_response, timestamp).run()
        CloseStoredRequest(stored_request).run()

        return Response(status=200)

    @app.route("/webhook", methods=["POST"])
    def respond():
        """Future official entry point."""

        return Response(status=200)

    @app.route("/test", methods=["GET"])
    def index():
        """Quick check that the server is running."""
        app_name = os.getenv("APP_NAME")
        if app_name:
            return "Hello from flask on a Docker environment"
        return "Hello from Flask"

    return app
