import os

from decouple import config
from flask import Flask
from flask_migrate import Migrate

from .models import db
from .views import bike_tracker_views, webhook_views


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

    app.register_blueprint(webhook_views.bp)
    app.register_blueprint(bike_tracker_views.bp)
    return app
