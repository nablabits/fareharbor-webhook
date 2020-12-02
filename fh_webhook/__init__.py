import os
import json
from datetime import datetime

from flask import Flask, request, Response
from flask_migrate import Migrate
from config import TestingConfig
from fh_webhook.models import db

from decouple import config


def create_app(test_config=False):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    if test_config:
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(config("APP_SETTINGS"))
    db.init_app(app)
    migrate = Migrate(app, db)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/test_webhook', methods=["POST"])
    def save_content():
        """Save the content of the POST method in a JSON file.

        If the response is empty it logs the event.

        Before storing the data on the db we should know how that data looks
        to create the tables accordingly. So we need a way to store the data
        to inspect it.
        """
        path = "fh_webhook/responses/"
        try:
            os.makedirs(path)
        except OSError:
            pass
        now = datetime.now()
        name = str(now.timestamp()) + ".json"
        if request.json:
            filename = os.path.join(path, name)
            with open(filename, "w") as fp:
                json.dump(request.json, fp)

            # if we are testing we should return the filename somehow
            try:
                request.json["test"]
                return app.make_response(filename)
            except KeyError:
                return Response(status=200)
        else:
            with open(os.path.join(path, "errors.log"), "a") as f:
                f.write("{} - the request was empty\n".format(now))
            return Response(status=202)  # Accepted

    @app.route('/webhook', methods=["POST"])
    def respond():
        return Response(status=200)

    return app
