from decouple import config
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash


def get_auth():
    auth = HTTPBasicAuth()
    fh_user = config("FH_USER")
    fh_password = config("FH_PASSWORD")
    bike_tracker_user = config("BIKE_TRACKER_USER")
    bike_tracker_pass = config("BIKE_TRACKER_PASS")
    test_user = config("TEST_USER")
    test_pass = config("TEST_PASS")
    users = {
        fh_user: generate_password_hash(fh_password),
        bike_tracker_user: generate_password_hash(bike_tracker_pass),
        test_user: generate_password_hash(test_pass),
    }

    @auth.verify_password
    def verify_password(username, password):
        user_exists = username in users
        if user_exists and check_password_hash(users.get(username), password):
            return username
        else:
            pass

    return auth
