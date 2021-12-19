import base64
import json
import os
from unittest.mock import patch

import jwt
from decouple import config

from fh_webhook.models import StoredRequest


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


def test_bike_tracker_test_success(client, database):
    rv = [
        {"uuid": "b90af693-975b-4b95-9a32-699afd6beae1", "display_name": "bike-01"},
    ]
    with patch("fh_webhook.services.GetBikeUUIDs.run", return_value=rv):
        response = client.get("/bike-tracker/get-services/", headers=get_headers())
    token = json.loads(response.data.decode())
    d = jwt.decode(
        token,
        key=client.application.config.get("BIKE_TRACKER_SECRET"),
        algorithms=[
            "HS256",
        ],
    )

    assert d["availabilities"] == []
    assert d["bike_uuids"] == rv


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
    data = {
        "availability_id": 123,
        "bikes": [f"bike{n}" for n in range(3)],
    }
    key = client.application.config.get("BIKE_TRACKER_SECRET")
    token = jwt.encode(payload=data, key=key)
    response = client.post(
        "/bike-tracker/add-bikes/", headers=get_headers(), json=token
    )

    assert response.status_code == 200


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
    data = {"bike_picked": 123, "bike_returned": "some-string"}
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
    data = {"bike_picked": "some-string", "bike_returned": "some-other-string"}
    key = client.application.config.get("BIKE_TRACKER_SECRET")
    token = jwt.encode(payload=data, key=key)
    response = client.put(
        "/bike-tracker/replace-bike/", headers=get_headers(), json=token
    )

    assert response.status_code == 200
