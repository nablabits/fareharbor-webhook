import pytest
from fh_webhook import create_app


def test_dummy_webhook_only_accepts_POST(client):
    response = client.get("/test_webhook")
    assert response.status == "405 METHOD NOT ALLOWED"

    response = client.post("/test_webhook")
    assert response.status_code == 202  # Since the request was empty


def test_dummy_webhook_saves_content_to_a_file(client):
    response = client.post("/test_webhook", json={
        "name": "foo", "age": 45, "test": True, })
    assert response.status_code == 200
    with open(bytes.decode(response.data), "r") as f:
        assert f.readline() == '{"age": 45, "name": "foo", "test": true}'

def test_dummy_webhook_returns_200(client):
    response = client.post("/test_webhook", json={
        "name": "foo", "age": 45, })
    assert response.status_code == 200


def test_dummy_webhook_trows_empty_requests_to_a_log(client):
    try:
        with open("fh_webhook/responses/errors.log", "r") as f:
            entries = len(f.readlines())
    except FileNotFoundError:
        entries = 0
    response = client.post("/test_webhook")
    assert response.status_code == 202  # Since the request was empty

    with open("fh_webhook/responses/errors.log", "r") as f:
        entries_plus_error = len(f.readlines())

    assert entries + 1 == entries_plus_error


def test_webhook_endpoint_only_accepts_POST(client):
    response = client.get("/webhook")
    assert response.status == "405 METHOD NOT ALLOWED"
    assert response.status_code == 405

    response = client.post("/webhook")
    assert response.status == "200 OK"
