import base64
import json
import os
from unittest.mock import patch

import jwt

from fh_webhook.models import StoredRequest


def get_headers():
    """Provide a one time set of valid credentials."""
    valid_credentials = base64.b64encode(b"test:test").decode("utf-8")
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


def test_bike_tracker_test_success(client, database):
    response = client.get("/bike-tracker-test/", headers=get_headers())
    token = json.loads(response.data.decode())
    d = jwt.decode(
        token,
        key=client.application.config.get("BIKE_TRACKER_SECRET"),
        algorithms=[
            "HS256",
        ],
    )

    assert d["availabilities"] == []
    assert len(d["bike_uuids"]) == 70
