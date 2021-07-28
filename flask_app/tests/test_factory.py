import json
import os
import base64
import pytest
from fh_webhook import create_app
from fh_webhook.models import StoredRequest
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
def test_dummy_webhook_saves_content_to_a_file(service, client, database):
    path = client.application.config.get("RESPONSES_PATH")
    [os.remove(os.path.join(path, f)) for f in os.listdir(path)]
    data = {
        "name": "foo",
        "age": 45,
    }
    response = client.post(
        "/",
        headers=get_headers(),
        json=data,
    )

    files_in_dir = os.listdir(path)
    assert response.status_code == 200
    assert len(files_in_dir) == 1
    with open(os.path.join(path, files_in_dir[0])) as json_file:
        data = json.load(json_file)
        assert data == data

    assert service.call_count == 1
    assert len(StoredRequest.query.all()) == 1

    # purge created files
    [os.remove(os.path.join(path, f)) for f in os.listdir(path)]


def test_dummy_webhook_trows_empty_requests_to_a_log(client):
    path = client.application.config.get("RESPONSES_PATH")
    response = client.post(
        "/",
        headers=get_headers(),
    )

    files_in_dir = os.listdir(path)
    assert response.status_code == 400  # Since the request was empty
    assert len(files_in_dir) == 1
    assert files_in_dir[0] == "errors.log"
    with open(os.path.join(path, files_in_dir[0])) as error_file:
        content = error_file.readlines()
        # get the last 22 chars as the others depend on datetime.now()
        assert content[0][-22:] == "the request was empty\n"

    # purge created files
    [os.remove(os.path.join(path, f)) for f in os.listdir(path)]


def test_webhook_endpoint_only_accepts_POST(client):
    response = client.get(
        "/webhook",
        headers=get_headers(),
    )
    assert response.status == "405 METHOD NOT ALLOWED"
    assert response.status_code == 405

    response = client.post(
        "/webhook",
        headers=get_headers(),
    )
    assert response.status == "200 OK"
