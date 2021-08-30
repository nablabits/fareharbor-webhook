from logging.config import dictConfig

from decouple import config, Csv


dictConfig({
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        },
        "access": {
            "format": "%(message)s",
        }
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
    }
})


class Config:
    """Define a base class."""

    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = config("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = config("DB_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FH_PASSWORD = config("FH_PASSWORD")
    RESPONSES_PATH = "fh_webhook/responses/"


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
