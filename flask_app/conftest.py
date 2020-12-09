import pytest
from fh_webhook import create_app


@pytest.fixture
def app():

    app = create_app(test_config=True)

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
