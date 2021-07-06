from datetime import datetime
from uuid import uuid4
from random import randint
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


@pytest.fixture()
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
    random_id = randint(1, 10_000_000)
    return model_services.CreateItem(item_id=random_id, name="foo")


@pytest.fixture
def availability_factory(item_factory):
    s = item_factory
    s.item_id = randint(1, 10_000)
    item = s.run()

    return model_services.CreateAvailability(
        availability_id=randint(1, 10_000_000),
        capacity=10,
        minimum_party_size=11,
        maximum_party_size=12,
        start_at=datetime.now(),
        end_at=datetime.now(),
        item_id=item.id,
    )


@pytest.fixture
def booking_factory(availability_factory):
    s = availability_factory
    s.availability_id = randint(1, 10_000_000),
    av = s.run()
    return model_services.CreateBooking(
        booking_id=randint(1, 10_000_000),
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
        receipt_subtotal=10,
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
        order="waz",
    )


@pytest.fixture
def contact_factory(booking_factory):
    s = booking_factory
    s.uuid = uuid4().hex
    b = s.run()
    return model_services.CreateContact(
        id=b.id,
        name="foo",
        email="foo@bar.baz",
        phone_country="49",
        phone="00000",
        normalized_phone="00000",
        is_subscribed_for_email_updates=True,
    ).run


@pytest.fixture
def company_factory(booking_factory):
    s = booking_factory
    s.uuid = uuid4().hex
    b = s.run()
    return model_services.CreateCompany(
        name="foo", short_name="bar", currency="eur", company_id=b.id
    ).run


@pytest.fixture
def cancellation_factory(booking_factory):
    """Create a cancellation policy for tests."""
    s = booking_factory
    s.uuid = uuid4().hex
    b = s.run()
    return model_services.CreateCancellationPolicy(
        cutoff=datetime.utcnow(), cancellation_type="foo", cp_id=b.id
    ).run


@pytest.fixture
def custom_field_factory():

    return model_services.CreateCustomField(
        custom_field_id=randint(1, 10_000_000),
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
    ).run


@pytest.fixture
def custom_field_instance_factory(database, custom_field_factory, availability_factory):
    cf = custom_field_factory()
    s = availability_factory
    s.availability_id = randint(1, 10_000_000),
    av = s.run()
    return model_services.CreateCustomFieldInstance(
        custom_field_instance_id=randint(1, 10_000_000),
        custom_field_id=cf.id,
        availability_id=av.id,
        customer_type_rate_id=None
    ).run


@pytest.fixture
def custom_field_value_factory(database, custom_field_factory, customer_factory):
    c = customer_factory()
    return model_services.CreateCustomFieldValue(
        name="foo",
        value="bar",
        display_value="baz",
        custom_field_id=custom_field_factory().id,
        booking_id=c.booking_id,
        customer_id=c.id,
    ).run


@pytest.fixture
def customer_factory(customer_type_rate_factory, booking_factory):
    s = booking_factory
    s.uuid = uuid4().hex
    b = s.run()
    return model_services.CreateCustomer(
        customer_id=randint(1, 10_000_000),
        checkin_url="https://foo.bar",
        checkin_status="checked_in",
        customer_type_rate_id=customer_type_rate_factory().id,
        booking_id=b.id,
    ).run


@pytest.fixture
def customer_type_rate_factory(
    availability_factory,
    customer_type_factory,
    customer_prototype_factory,
):
    s = availability_factory
    s.availability_id = randint(1, 10_000_000),
    av = s.run()
    return model_services.CreateCustomerTypeRate(
        ctr_id=randint(1, 10_000_000),
        capacity=4,
        minimum_party_size=2,
        maximum_party_size=4,
        availability_id=av.id,
        total=10,
        total_including_tax=10,
        customer_prototype_id=customer_prototype_factory().id,
        customer_type_id=customer_type_factory().id,
    ).run


@pytest.fixture
def customer_prototype_factory():
    return model_services.CreateCustomerPrototype(
        customer_prototype_id=randint(1, 10_000_000),
        total=10, total_including_tax=10, display_name="foo", note="bar"
    ).run


@pytest.fixture
def customer_type_factory():
    return model_services.CreateCustomerType(
        customer_type_id=randint(1, 10_000_000),
        note="foo",
        singular="bar",
        plural="baz",
    ).run
