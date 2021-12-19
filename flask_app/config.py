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

    # The location of the bikes information.
    BIKE_TRACKER_BIKE_SOURCE = "fh_webhook/static/bike_info.json"
    BIKE_TRACKER_SECRET = config("BIKE_TRACKER_SECRET")
    BIKE_TRACKER_ITEMS = [
        159053,
        159055,
        159056,
        234853,
        234990,  # Regular tours
        159057,
        159058,
        159060,
        159065,  # Private tours
        159068,
        159074,
        159100,
        159103,
        235262,
        265105,  # Rentals
    ]


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
