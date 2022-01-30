"""The result library."""


class Result:
    """
    Construct Result objects.

    Result is the basic answer for services that encapsulates the outcome of the service in a clear
    and consistent pattern across services. It was added after creating some services, so there are
    a few of them that do not make use of it. Eventually we might want to replace the responses for
    those services.
    """

    @staticmethod
    def from_success(value):
        """Return a successful response to a given service."""
        return Success(value)

    @staticmethod
    def from_failure(errors):
        """Return a failure response for a given service."""
        return Failure(errors)

    def __repr__(self):
        return self.__str__()


class Failure:
    """Construct the Failure object for failed services."""

    def __init__(self, errors):
        self.success = False
        self.failure = True
        self.errors = errors

    def __str__(self):
        return "Failure: `{}`".format(str(self.errors))

    def __bool__(self):
        return False

    def map(self, fn):
        return self


class Success:
    """Construct the Success object for successful services."""

    def __init__(self, value):
        self.success = True
        self.failure = False
        self.value = value

    def __str__(self) -> str:
        return "Success: `{}`".format(str(self.value))

    def __repr__(self) -> str:
        return self.__str__()

    def __bool__(self):
        return True

    def map(self, fn):
        return Success(fn(self.value))
