import base64
import pytest
from fh_webhook import create_app


def get_headers():
    """Provide a one time set of valid credentials."""
    valid_credentials = base64.b64encode(b"test:test").decode("utf-8")
    return {"Authorization": "Basic " + valid_credentials}


def test_dummy_webhook_only_accepts_POST(client):
    response = client.get("/test_webhook", headers=get_headers())
    assert response.status == "405 METHOD NOT ALLOWED"

    response = client.post("/test_webhook", headers=get_headers())
    assert response.status_code == 400  # Since the request was empty


def test_dummy_webhook_auth_error(client):
    wrong_user = base64.b64encode(b"void:test").decode("utf-8")
    headers = {"Authorization": "Basic " + wrong_user}
    response = client.post(
        "/test_webhook",
        json={
            "name": "foo",
            "age": 45,
            "test": True,
        },
        headers=headers,
    )

    assert response.status_code == 401
    assert response.data == b"Unauthorized Access"

    wrong_pass = base64.b64encode(b"test:void").decode("utf-8")
    headers = {"Authorization": "Basic " + wrong_user}
    response = client.post(
        "/test_webhook",
        json={
            "name": "foo",
            "age": 45,
            "test": True,
        },
        headers=headers,
    )

    assert response.status_code == 401
    assert response.data == b"Unauthorized Access"


def test_dummy_webhook_saves_content_to_a_file(client):
    response = client.post(
        "/test_webhook",
        headers=get_headers(),
        json={
            "name": "foo",
            "age": 45,
            "test": True,
        },
    )
    assert response.status_code == 200
    with open(bytes.decode(response.data), "r") as f:
        assert f.readline() == '{"age": 45, "name": "foo", "test": true}'


def test_dummy_webhook_returns_200(client):
    response = client.post(
        "/test_webhook",
        headers=get_headers(),
        json={
            "name": "foo",
            "age": 45,
        },
    )
    assert response.status_code == 200


def test_dummy_webhook_trows_empty_requests_to_a_log(client):
    try:
        with open("fh_webhook/responses/errors.log", "r") as f:
            entries = len(f.readlines())
    except FileNotFoundError:
        entries = 0
    response = client.post(
        "/test_webhook",
        headers=get_headers(),
    )
    # breakpoint()
    assert response.status_code == 400  # Since the request was empty

    with open("fh_webhook/responses/errors.log", "r") as f:
        entries_plus_error = len(f.readlines())

    assert entries + 1 == entries_plus_error


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
