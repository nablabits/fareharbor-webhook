from logging.config import dictConfig

from decouple import Csv, config

dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            },
            "access": {
                "format": "%(message)s",
            },
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
                "level": "INFO",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "level": "ERROR",
                "filename": "fh_webhook/responses/log/error_responses.log",
                "maxBytes": 10000,
                "backupCount": 10,
                "delay": "True",
            },
            "email": {
                "class": "fh_webhook.services.SSLSMTPHandler",
                "formatter": "default",
                "level": "ERROR",
                "mailhost": (config("SMTP_HOST"), config("SMTP_PORT")),
                "fromaddr": config("EMAIL_FROM"),
                "toaddrs": config("EMAIL_RECIPIENTS", cast=Csv()),
                "subject": "Error Logs on FH Webhook.",
                "credentials": (config("SMTP_USERNAME"), config("SMTP_PASSWORD")),
            },
        },
        "root": {
            "handlers": ["email", "error_file"],
        },
    }
)


class Config:
    """Define a base class."""

    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = config("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = config("DB_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    FH_USER = config("FH_USER")
    FH_PASSWORD = config("FH_PASSWORD")
    BIKE_TRACKER_USER = config("BIKE_TRACKER_USER")
    BIKE_TRACKER_PASS = config("BIKE_TRACKER_PASS")
    RESPONSES_PATH = "fh_webhook/responses/"

    # The location of the bikes' information.
    BIKE_TRACKER_BIKE_SOURCE = "fh_webhook/static/bike_info.json"
    BIKE_TRACKER_SECRET = config("BIKE_TRACKER_SECRET")

    # Because how the contexts work in flask we had to hardcode these values in the tests, so if
    # you add some other id or duration, please add it to test_bike_tracker_services.
    BIKE_TRACKER_ITEMS = {
        "regular_tours": [
            159053,
            159055,
            159056,
            159061,
        ],
        "private_tours": [
            159057,
            159058,
            159060,
            248003,
        ],
        "rentals": [
            159068,
            159074,
            159100,
            159103,
            235262,
        ],
    }

    # The durations per customer type id that are used for rentals
    DURATION_MAP = {
        314997: "2.0",
        314998: "4.0",
        314999: "8.0",  # eight hours
        763051: "8.0",  # full day
        763050: "4.0",  # half day
        315000: "24.0",  # 24h hours
        315001: "24.0",  # 2 days
        315002: "24.0",  # 7 days
        690082: "24.0",  # Long rent
    }


class ProductionConfig(Config):
    """Override base class for production."""

    DEBUG = False


class DevelopmentConfig(Config):
    """Override base class for development."""

    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    """Override base class for testing."""

    TESTING = True
    TEST_PASSWORD = "test"
    SQLALCHEMY_DATABASE_URI = "postgresql:///webhook-test"
    RESPONSES_PATH = "tests/responses/"
    BIKE_TRACKER_BIKE_SOURCE = "tests/sample_data/sample_bike/bike_info.json"
