import os

from decouple import config


class Config(object):
    """Define a base class."""

    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = config("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = config("DB_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FH_PASSWORD = config("FH_PASSWORD")


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
