from datetime import datetime
import pytest
from fh_webhook import models, model_services, create_app
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
    app = create_app(test_config=True)
    ctx = app.app_context()
    ctx.push()
    db.create_all()

    yield db

    db.session.connection().close()
    db.drop_all()
    ctx.pop()


# Model Factories


@pytest.fixture
def item_factory():
    return model_services.CreateItem(name="foo").run()


@pytest.fixture
def availability_factory(item_factory):
    item = item_factory

    return model_services.CreateAvailability(
        capacity=10,
        minimum_party_size=11,
        maximum_party_size=12,
        start_at=datetime.now(),
        end_at=datetime.now(),
        item_id=item.id
    ).run()


@pytest.fixture
def custom_field_factory():

    return model_services.CreateCustomField(
        title="foo",
        name="bar",
        modifier_kind="baz",
        modifier_type="kar",
        field_type="kaz",
        offset=1,
        percentage=2,
        description="lorem ipsum",
        booking_notes="doloret sit amesquet",
        description_safe_html="totus oprobium",
        booking_notes_safe_html="parabellum qui est",
        is_required=True,
        is_taxable=False,
        is_always_per_customer=False,
    ).run()


@pytest.fixture
def customer_prototype_factory():
    return model_services.CreateCustomerPrototype(
        total=10,
        total_including_tax=10,
        display_name="foo",
        note="bar"
    ).run()


@pytest.fixture
def customer_type_factory():
    return model_services.CreateCustomerType(
        note="foo",
        singular="bar",
        plural="baz",
    ).run()
