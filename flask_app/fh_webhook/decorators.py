from functools import wraps

import jwt
from flask import Response, current_app, request
from jwt.exceptions import InvalidTokenError


def validate_token(view_func):
    @wraps(view_func)
    def inner(*args, **kwargs):
        key = current_app.config.get("BIKE_TRACKER_SECRET")
        try:
            data = jwt.decode(
                request.json,
                key=key,
                algorithms=[
                    "HS256",
                ],
            )
        except InvalidTokenError as e:
            current_app.logger.error(f"Unable to decode the token, error: {e}")
            return Response(str(e), status=403)
        return view_func(data)

    return inner
