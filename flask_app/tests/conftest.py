from datetime import datetime
from uuid import uuid4
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
def booking_factory(availability_factory):
    av = availability_factory
    return model_services.CreateBooking(
        voucher_number="foo",
        display_id="bar",
        note_safe_html="baz",
        agent="goo",
        confirmation_url="kar",
        customer_count=5,
        affiliate_company="roo",
        uuid=uuid4().hex,
        dashboard_url="taz",
        note="moo",
        pickup="mar",
        status="maz",
        availability_id=av.id,
        receipt_subtotals=10,
        receipt_taxes=11,
        receipt_total=12,
        amount_paid=13,
        invoice_price=14,
        receipt_subtotal_display="10",
        receipt_taxes_display="11",
        receipt_total_display="12",
        amount_paid_display="13",
        invoice_price_display="14",
        desk="soo",
        is_eligible_for_cancellation=True,
        arrival="sar",
        rebooked_to="saz",
        rebooked_from="woo",
        external_id="war",
        order="waz"
    ).run()


@pytest.fixture
def contact_factory(booking_factory):
    return model_services.CreateContact(
        name="foo",
        email="foo@bar.baz",
        phone_country="49",
        phone="00000",
        normalized_phone="00000",
        is_subscribed_for_email_updates=True,
        booking_id=booking_factory.id
    ).run()


@pytest.fixture
def company_factory(booking_factory):
    return model_services.CreateCompany(
        name="foo",
        short_name="bar",
        currency="eur",
        booking_id=booking_factory.id
    ).run()


@pytest.fixture
def cancellation_factory(booking_factory):
    """Create a cancellation policy for tests."""
    return model_services.CreateCancellationPolicy(
        cutoff=datetime.utcnow(),
        cancellation_type="foo",
        booking_id=booking_factory.id
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
def customer_factory(customer_type_rate_factory, booking_factory):
    return model_services.CreateCustomer(
        checkin_url="https://foo.bar",
        checking_status="checked_in",
        customer_type_rate_id=customer_type_rate_factory.id,
        booking_id=booking_factory.id
    ).run()


@pytest.fixture
def customer_type_rate_factory(
    booking_factory, availability_factory, customer_type_factory,
    customer_prototype_factory
):
    return model_services.CreateCustomerTypeRate(
        capacity=4,
        minimum_party_size=2,
        maximum_party_size=4,
        booking_id=booking_factory.id,
        availability_id=availability_factory.id,
        customer_prototype_id=customer_prototype_factory.id,
        customer_type_id=customer_type_factory.id
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
