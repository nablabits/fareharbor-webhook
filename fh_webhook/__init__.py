import os

from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from fh_webhook.models import db, sampleTable

from decouple import config


def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config("APP_SETTINGS"))
    db.init_app(app)
    migrate = Migrate(app, db)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def hello():
        return "Hello World!"

    @app.route('/webhook', methods=['POST'])
    def respond():
        print(request.json)
        return Response(status=200)

    return app
