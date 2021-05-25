import pytest
from fh_webhook import create_app
from fh_webhook.models import db


@pytest.fixture(scope="session")
def app():

    app = create_app(test_config=True)
    ctx = app.app_context()
    ctx.push()

    yield app

    ctx.pop()


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()


@pytest.fixture(scope="session")
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(scope='session')
def database(request):
    """
    Create a Postgres database for the tests, and drop it when the tests are done.
    """
    db.create_all()

    yield db

    db.session.connection().close()
    db.drop_all()