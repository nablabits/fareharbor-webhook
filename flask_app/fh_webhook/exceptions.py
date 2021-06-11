"""
The core exceptions for the flask app.
"""

class BaseFHWebhookException(Exception):
    """Base Exception for the app."""
    pass


class DoesNotExist(BaseFHWebhookException):
    """Raised when attempting to get a non-existent object from the db."""

    def __init__(self, model):
        super().__init__(f"This instance of {model} model does not exist")


