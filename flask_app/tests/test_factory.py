import base64
import json
import os
from datetime import datetime, timedelta
from random import randint
from unittest.mock import patch
from uuid import uuid4

import jwt
from decouple import config

from fh_webhook.models import Booking, StoredRequest
from fh_webhook.result import Result
from tests.conftest import randomizer


def get_headers():
    """Provide a one time set of valid credentials."""
    test_user = config("TEST_USER")
    test_pass = config("TEST_PASS")
    auth = bytes(f"{test_user}:{test_pass}", "utf-8")
    valid_credentials = base64.b64encode(auth).decode("utf-8")
    return {"Authorization": "Basic " + valid_credentials}


def test_dummy_webhook_only_accepts_POST(client):
    path = client.application.config.get("RESPONSES_PATH")
    [os.remove(os.path.join(path, f)) for f in os.listdir(path)]

    response = client.get("/", headers=get_headers())
    assert response.status == "405 METHOD NOT ALLOWED"

    response = client.post("/", headers=get_headers())
    assert response.status_code == 400  # Since the request was empty

    # purge created files
    [os.remove(os.path.join(path, f)) for f in os.listdir(path)]


def test_dummy_webhook_auth_error(client):
    wrong_user = base64.b64encode(b"void:test").decode("utf-8")
    headers = {"Authorization": "Basic " + wrong_user}
    response = client.post(
        "/",
        json={
            "name": "foo",
            "age": 45,
        },
        headers=headers,
    )

    assert response.status_code == 401
    assert response.data == b"Unauthorized Access"


@patch("fh_webhook.services.ProcessJSONResponse.run")
def test_dummy_webhook_saves_content_to_a_file(keys_svc, client, database):
    path = client.application.config.get("RESPONSES_PATH")
    [os.remove(os.path.join(path, f)) for f in os.listdir(path)]

    with open("tests/sample_data/sample_booking/1626842330.051856.json") as f:
        data = json.load(f)

    response = client.post(
        "/",
        headers=get_headers(),
        json=data,
    )

    files_in_dir = os.listdir(path)
    assert response.status_code == 200
    assert len(files_in_dir) == 1
    with open(os.path.join(path, files_in_dir[0])) as json_file:
        written_data = json.load(json_file)
        assert written_data == data

    assert keys_svc.call_count == 1
    assert len(StoredRequest.query.all()) == 1

    # purge created files
    [os.remove(os.path.join(path, f)) for f in os.listdir(path)]


@patch("fh_webhook.services.ProcessJSONResponse.run")
@patch(
    "fh_webhook.services.SaveResponseAsFile.run", return_value="1626842330.051856.json"
)
def test_dummy_webhook_does_not_find_new_keys(
    save_file_svc, process_svc, client, database, caplog
):
    with open("tests/sample_data/sample_booking/1626842330.051856.json") as f:
        data = json.load(f)

    response = client.post(
        "/",
        headers=get_headers(),
        json=data,
    )

    assert len(caplog.records) == 0
    assert response.status_code == 200
    assert process_svc.call_count == 1
    assert save_file_svc.call_count == 1
    assert len(StoredRequest.query.all()) == 1


@patch(
    "fh_webhook.services.SaveResponseAsFile.run", return_value="1626842330.051856.json"
)
def test_dummy_webhook_trows_requests_with_missing_data_to_a_log(
    file_svc, client, database, caplog
):

    with open("tests/sample_data/sample_booking/1626842330.051856.json") as f:
        data = json.load(f)

    del data["booking"]["display_id"]

    response = client.post(
        "/",
        headers=get_headers(),
        json=data,
    )

    response_msg = "{'display_id': ['Missing data for required field.']}"
    assert response.status_code == 400
    assert response.data.decode() == response_msg
    assert caplog.records[0].msg.startswith("filename=")


def test_dummy_webhook_trows_empty_requests_to_a_log(client, caplog):
    response = client.post(
        "/",
        headers=get_headers(),
    )

    assert response.status_code == 400  # Since the request was empty
    assert caplog.records[0].msg == "The request was empty"


def test_bike_tracker_only_accepts_GET(client):
    response = client.post("/bike-tracker/get-services/", headers=get_headers())
    assert response.status == "405 METHOD NOT ALLOWED"


def test_bike_tracker_auth_error(client):
    wrong_user = base64.b64encode(b"void:test").decode("utf-8")
    headers = {"Authorization": "Basic " + wrong_user}
    response = client.get("/bike-tracker/get-services/", headers=headers)

    assert response.status_code == 401
    assert response.data == b"Unauthorized Access"


def test_bike_tracker_get_services_success_for_current_date(
    client, database, bike_factory, booking_factory, item_factory, availability_factory
):
    bikes = [
        bike_factory(uuid=uuid4().hex, readable_name=f"r bike{n}") for n in range(3)
    ]
    bike_uuids = [{"uuid": b.uuid, "display_name": b.readable_name} for b in bikes]
    ts0 = datetime.now()
    ts1 = ts0 + timedelta(hours=1)

    # Create the booking that will appear in the results
    item_id = client.application.config.get("BIKE_TRACKER_ITEMS")[0]
    s = item_factory
    s.item_id = item_id
    s.name = "item 1"
    item = s.run()
    b0, b0_id = randomizer(booking_factory.run())
    b0.customer_count = 10
    b0.availability.start_at = ts0
    b0.availability.end_at = ts0
    b0.availability.headline = "service 1"
    b0.availability.item = item
    b0.rebooked_to = None
    database.session.commit()

    # Create another booking to test the group by
    s = availability_factory
    s.availability_id = randint(1, 1e4)
    s.start_at = ts1
    s.end_at = ts1
    s.headline = "service 2"
    av = s.run()
    av.item = item
    av.item.name = "item 2"
    b1, b1_id = randomizer(booking_factory.run())
    b1.customer_count = 20
    b1.availability = av
    b1.rebooked_to = None
    database.session.commit()

    # Create alternative bookings that shouldn't appear
    # this happens some other day.
    s = availability_factory
    s.availability_id = randint(1, 1e4)
    s.start_at = ts0 + timedelta(days=1)
    s.end_at = ts0 + timedelta(days=1)
    av = s.run()
    b2, _ = randomizer(booking_factory.run())
    av.item = item
    b2.availability = av
    database.session.commit()

    # Create a cancelled booking
    b3, _ = randomizer(booking_factory.run())
    b3.availability = b0.availability
    b3.status = "cancelled"
    database.session.commit()

    # create a rebooked booking
    b4, _ = randomizer(booking_factory.run())
    b4.availability = b0.availability
    b4.rebooked_to = uuid4().hex
    database.session.commit()

    # Finally create a booking that does not contain a valid item
    s = availability_factory
    s.availability_id = randint(1, 1e4)
    s.start_at = ts0
    s.end_at = ts0
    av = s.run()
    s = item_factory
    s.item_id = randint(1, 1e4)
    item = s.run()
    av.item = item
    b4, _ = randomizer(booking_factory.run())
    b4.availability = av
    database.session.commit()

    response = client.get("/bike-tracker/get-services/", headers=get_headers())
    token = json.loads(response.data.decode())
    d = jwt.decode(
        token,
        key=client.application.config.get("BIKE_TRACKER_SECRET"),
        algorithms=[
            "HS256",
        ],
    )

    for n, booking_id in enumerate((b0_id, b1_id)):
        b = Booking.get(booking_id)
        tss = [ts0, ts1]
        expected0 = {
            "availability_id": b.availability_id,
            "headline": b.availability.headline,
            "timestamp": str(tss[n].time()).split(".")[0],
            "no_of_bikes": b.customer_count,
        }

        assert d["availabilities"][n] == expected0

    assert d["bike_uuids"] == bike_uuids


def test_add_bikes_only_accepts_POST(client):
    response = client.get("/bike-tracker/add-bikes/", headers=get_headers())
    assert response.status == "405 METHOD NOT ALLOWED"


def test_add_bikes_auth_error(client):
    wrong_user = base64.b64encode(b"void:test").decode("utf-8")
    headers = {"Authorization": "Basic " + wrong_user}
    data = {
        "availability_id": 123,
        "bikes": [f"bike{n}" for n in range(3)],
    }
    key = client.application.config.get("BIKE_TRACKER_SECRET")
    token = jwt.encode(payload=data, key=key)
    response = client.post("/bike-tracker/add-bikes/", headers=headers, json=token)

    assert response.status_code == 401
    assert response.data == b"Unauthorized Access"


def test_add_bikes_token_error(client, caplog):
    data = {
        "availability_id": 123,
        "bikes": [f"bike{n}" for n in range(3)],
    }
    key = "void_key"
    token = jwt.encode(payload=data, key=key)
    response = client.post(
        "/bike-tracker/add-bikes/", headers=get_headers(), json=token
    )

    assert response.status_code == 403
    assert response.data == b"Signature verification failed"
    assert caplog.messages == [
        "Unable to decode the token, error: Signature verification failed"
    ]


def test_add_bikes_schema_error(client, caplog):
    data = {
        "availability_id": "12r",
        "bikes": [f"bike{n}" for n in range(3)],
    }
    key = client.application.config.get("BIKE_TRACKER_SECRET")
    token = jwt.encode(payload=data, key=key)
    response = client.post(
        "/bike-tracker/add-bikes/", headers=get_headers(), json=token
    )

    assert response.status_code == 400
    assert response.data == b"{'availability_id': ['Not a valid integer.']}"
    assert caplog.messages == [
        "Validation failed for add-bike request, error: "
        "{'availability_id': ['Not a valid integer.']}"
    ]


def test_add_bikes_success(client):
    data = {"availability_id": 123, "bikes": [f"bike{n}" for n in range(3)]}
    key = client.application.config.get("BIKE_TRACKER_SECRET")
    token = jwt.encode(payload=data, key=key)

    rv = Result.from_success("👍")
    with patch(
        "fh_webhook.model_services.CreateBikeUsages.run", return_value=rv
    ) as mock_svc:
        response = client.post(
            "/bike-tracker/add-bikes/", headers=get_headers(), json=token
        )

    assert response.status_code == 200
    assert mock_svc.call_count == 1


def test_add_bikes_failure(client):
    data = {"availability_id": 123, "bikes": [f"bike{n}" for n in range(3)]}
    key = client.application.config.get("BIKE_TRACKER_SECRET")
    token = jwt.encode(payload=data, key=key)

    rv = Result.from_failure({"error": "some error"})
    with patch(
        "fh_webhook.model_services.CreateBikeUsages.run", return_value=rv
    ) as mock_svc:
        response = client.post(
            "/bike-tracker/add-bikes/", headers=get_headers(), json=token
        )

    assert response.status_code == 404
    assert mock_svc.call_count == 1
    assert response.json == {"error": "some error"}


def test_replace_bikes_only_accepts_PUT(client):
    response = client.post("/bike-tracker/replace-bike/", headers=get_headers())
    assert response.status == "405 METHOD NOT ALLOWED"


def test_replace_bikes_auth_error(client):
    wrong_user = base64.b64encode(b"void:test").decode("utf-8")
    headers = {"Authorization": "Basic " + wrong_user}
    data = {
        "availability_id": 123,
        "bikes": [f"bike{n}" for n in range(3)],
    }
    key = client.application.config.get("BIKE_TRACKER_SECRET")
    token = jwt.encode(payload=data, key=key)
    response = client.put("/bike-tracker/replace-bike/", headers=headers, json=token)

    assert response.status_code == 401
    assert response.data == b"Unauthorized Access"


def test_replace_bikes_token_error(client, caplog):
    data = {
        "availability_id": 123,
        "bikes": [f"bike{n}" for n in range(3)],
    }
    key = "void_key"
    token = jwt.encode(payload=data, key=key)
    response = client.put(
        "/bike-tracker/replace-bike/", headers=get_headers(), json=token
    )

    assert response.status_code == 403
    assert response.data == b"Signature verification failed"
    assert caplog.messages == [
        "Unable to decode the token, error: Signature verification failed"
    ]


def test_replace_bikes_schema_error(client, caplog):
    data = {"availability_id": 1, "bike_picked": 123, "bike_returned": "some-string"}
    key = client.application.config.get("BIKE_TRACKER_SECRET")
    token = jwt.encode(payload=data, key=key)
    response = client.put(
        "/bike-tracker/replace-bike/", headers=get_headers(), json=token
    )

    assert response.status_code == 400
    assert response.data == b"{'bike_picked': ['Not a valid string.']}"
    assert caplog.messages == [
        "Validation failed for add-bike request, error: "
        "{'bike_picked': ['Not a valid string.']}"
    ]


def test_replace_bikes_success(client):
    data = {
        "availability_id": 1,
        "bike_picked": "some-string",
        "bike_returned": "some-other-string",
    }
    key = client.application.config.get("BIKE_TRACKER_SECRET")
    token = jwt.encode(payload=data, key=key)

    rv = Result.from_success("👍")
    with patch(
        "fh_webhook.model_services.UpdateBikeUsage.run", return_value=rv
    ) as mock_svc:
        response = client.put(
            "/bike-tracker/replace-bike/", headers=get_headers(), json=token
        )

    assert response.status_code == 200
    assert mock_svc.call_count == 1


def test_replace_bikes_failure(client):
    data = {
        "availability_id": 1,
        "bike_picked": "some-string",
        "bike_returned": "some-other-string",
    }
    key = client.application.config.get("BIKE_TRACKER_SECRET")
    token = jwt.encode(payload=data, key=key)

    rv = Result.from_failure({"error": "some error"})
    with patch(
        "fh_webhook.model_services.UpdateBikeUsage.run", return_value=rv
    ) as mock_svc:
        response = client.put(
            "/bike-tracker/replace-bike/", headers=get_headers(), json=token
        )

    assert response.status_code == 404
    assert mock_svc.call_count == 1
    assert response.json == {"error": "some error"}
