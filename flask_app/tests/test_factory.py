import json
import os
import base64
import pytest
from fh_webhook import create_app
from fh_webhook.models import StoredRequest
from fh_webhook.services import CheckForNewKeys
from unittest.mock import patch


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
@patch("fh_webhook.services.CheckForNewKeys.run", return_value=None)
def test_dummy_webhook_saves_content_to_a_file(
    keys_svc, process_svc, client, database
):
    path = client.application.config.get("RESPONSES_PATH")
    [os.remove(os.path.join(path, f)) for f in os.listdir(path)]

    with open("tests/sample_data/1626842330.051856.json") as f:
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

    assert process_svc.call_count == 1
    assert keys_svc.call_count == 1
    assert len(StoredRequest.query.all()) == 1

    # purge created files
    [os.remove(os.path.join(path, f)) for f in os.listdir(path)]


@patch("fh_webhook.services.ProcessJSONResponse.run")
@patch(
    "fh_webhook.services.SaveResponseAsFile.run",
    return_value="1626842330.051856.json"
)
def test_dummy_webhook_finds_new_keys(
    save_file_svc, process_svc, client, database, caplog
):
    with open("tests/sample_data/1626842330.051856.json") as f:
        data = json.load(f)

    # Add some extra data
    data["booking"]["new_key"] = "new_value"

    response = client.post(
        "/",
        headers=get_headers(),
        json=data,
    )

    assert response.status_code == 200
    assert len(caplog.records) == 1
    assert caplog.records[0].msg == "New key found in booking: new_key"

    assert process_svc.call_count == 1
    assert save_file_svc.call_count == 1
    assert len(StoredRequest.query.all()) == 1


@patch("fh_webhook.services.ProcessJSONResponse.run")
@patch(
    "fh_webhook.services.SaveResponseAsFile.run",
    return_value="1626842330.051856.json"
)
def test_dummy_webhook_does_not_find_new_keys(
    save_file_svc, process_svc, client, database, caplog
):
    with open("tests/sample_data/1626842330.051856.json") as f:
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


@patch("fh_webhook.services.CheckForNewKeys.run", return_value=None)
@patch(
    "fh_webhook.services.SaveResponseAsFile.run",
    return_value="1626842330.051856.json"
)
def test_dummy_webhook_trows_requests_with_missing_data_to_a_log(
    process_svc, file_svc, client, database, caplog
):

    with open("tests/sample_data/1626842330.051856.json") as f:
        data = json.load(f)

    del data["booking"]["display_id"]

    response = client.post(
        "/",
        headers=get_headers(),
        json=data,
    )

    sr = StoredRequest.query.first()

    assert response.status_code == 400
    response_msg = "The request was missing data. (('display_id',))"
    log_msg = (
        f"The request was missing data (stored_request_id={sr.id}, " +
        "error=('display_id',))"
    )
    assert response.data.decode() == response_msg
    assert caplog.records[0].msg == log_msg


def test_dummy_webhook_trows_empty_requests_to_a_log(client, caplog):
    response = client.post(
        "/",
        headers=get_headers(),
    )

    assert response.status_code == 400  # Since the request was empty
    assert caplog.records[0].msg == "The request was empty"
