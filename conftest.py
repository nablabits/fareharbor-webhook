import os
import pytest
from fh_webhook import create_app
# from fh_webhook.db import get_db, init_db

# with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
#     _data_sql = f.read().decode('utf8')


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
