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
    SECURITY_TOKEN = config("SECURITY_TOKEN")


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
    SECURITY_TOKEN = "test"
