"""
The core exceptions for the flask app.
"""


class BaseFHWebhookException(Exception):
    """Base Exception for the app."""

    pass


class DoesNotExist(BaseFHWebhookException):
    """Raised when attempting to get a non-existent object from the db."""

    def __init__(self, model):
        super().__init__(f"This instance of {model} model does not exist.")


class TooManyInstances(BaseFHWebhookException):
    """Raised when a query returns several objects and only one was expected."""

    def __init__(self, model):
        super().__init__(f"The query returned several entries.")
