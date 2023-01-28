from datetime import datetime, timedelta, timezone
from random import randint
from uuid import uuid4

import pytest

from fh_webhook import create_app, model_services
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
    db.drop_all()
    db.create_all()

    yield db

    db.session.connection().close()
    db.drop_all()
    ctx.pop()


def randomizer(entity, booking=True):
    """
    Given a db entity randomize the id (and the uuid if it's a booking) so tests won't crash.

    Also return the randomized_id so we can use it afterwards to retrieve the original entity from
    the database without hitting the lazy load error.
    """
    random_id = randint(1, 1e4)
    entity.id = random_id
    if booking:
        entity.uuid = uuid4().hex
    return entity, random_id


# Model Factories


@pytest.fixture
def stored_request_factory():
    timestamp = datetime.now(timezone.utc) - timedelta(minutes=1)
    unix_timestamp = str(timestamp.timestamp())
    return model_services.CreateStoredRequest(
        request_id=int(unix_timestamp.replace(".", "")),
        filename=unix_timestamp + ".json",
        body='{"foo": "bar", "baz": "gaz"}',
        timestamp=timestamp,
    )


@pytest.fixture
def item_factory():
    random_id = randint(1, 10_000_000)
    return model_services.CreateItem(
        item_id=random_id,
        name="foo",
        timestamp=datetime.now(timezone.utc) - timedelta(days=1),
    )


@pytest.fixture
def availability_factory(item_factory):
    s = item_factory
    s.item_id = randint(1, 10_000)
    item = s.run()
    timestamp = datetime.now(timezone.utc) - timedelta(days=1)

    return model_services.CreateAvailability(
        availability_id=randint(1, 10_000_000),
        timestamp=timestamp,
        capacity=10,
        minimum_party_size=11,
        maximum_party_size=12,
        start_at=timestamp,
        end_at=timestamp,
        item_id=item.id,
        headline="Some Headline",
    )


@pytest.fixture
def file_timestamp():
    """Return the datetime object represented by the sample filename."""
    return datetime(2021, 7, 21, 4, 38, 50, 51856, tzinfo=timezone.utc)


@pytest.fixture
def booking_factory(availability_factory, company_factory):
    s = availability_factory
    s.availability_id = (randint(1, 10_000_000),)
    av = s.run()
    company = company_factory.run()
    s_affiliate_company = company_factory
    s_affiliate_company.short_name = uuid4().hex[:30]
    affiliate_company = s_affiliate_company.run()
    return model_services.CreateBooking(
        booking_id=randint(1, 10_000_000),
        timestamp=datetime.now(timezone.utc) - timedelta(days=1),
        voucher_number="foo",
        display_id="bar",
        note_safe_html="baz",
        agent="goo",
        confirmation_url="kar",
        customer_count=5,
        uuid=uuid4().hex,
        dashboard_url="taz",
        note="moo",
        pickup="mar",
        status="maz",
        created_by="staff",
        availability_id=av.id,
        company_id=company.id,
        affiliate_company_id=affiliate_company.id,
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
        is_subscribed_for_sms_updates=True,
        arrival="sar",
        rebooked_to="",
        rebooked_from="woo",
        external_id="war",
        order={"waz": "raz"},
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
        timestamp=datetime.now(timezone.utc) - timedelta(days=1),
        language="ES",
    ).run


@pytest.fixture
def editable_contact():
    return contact_instance


def contact_instance(
    booking_id,
    name="foo",
    email="foo@bar.baz",
    phone_country="49",
    phone="00000",
    normalized_phone="00000",
    is_subscribed_for_email_updates=True,
    language="ES",
):
    return model_services.CreateContact(
        id=booking_id,
        name=name,
        email=email,
        phone_country=phone_country,
        phone=phone,
        normalized_phone=normalized_phone,
        is_subscribed_for_email_updates=is_subscribed_for_email_updates,
        timestamp=datetime.now(timezone.utc) - timedelta(days=1),
        language=language,
    ).run()


@pytest.fixture
def company_factory():
    return model_services.CreateCompany(
        name="foo",
        short_name=uuid4().hex[:30],
        currency="eur",
        timestamp=datetime.now(timezone.utc) - timedelta(days=1),
    )


@pytest.fixture
def cancellation_factory(booking_factory):
    """Create a cancellation policy for tests."""
    s = booking_factory
    s.uuid = uuid4().hex
    b = s.run()
    return model_services.CreateCancellationPolicy(
        cutoff=datetime.utcnow(),
        cancellation_type="foo",
        cp_id=b.id,
        timestamp=datetime.now(timezone.utc) - timedelta(days=1),
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
        timestamp=datetime.now(timezone.utc) - timedelta(days=1),
    ).run


@pytest.fixture
def custom_field_instance_factory(database, custom_field_factory, availability_factory):
    cf = custom_field_factory()
    s = availability_factory
    s.availability_id = (randint(1, 10_000_000),)
    av = s.run()
    return model_services.CreateCustomFieldInstance(
        custom_field_instance_id=randint(1, 10_000_000),
        custom_field_id=cf.id,
        availability_id=av.id,
        customer_type_rate_id=None,
        timestamp=datetime.now(timezone.utc) - timedelta(days=1),
    ).run


@pytest.fixture
def custom_field_value_factory(database, custom_field_factory, customer_factory):
    s = customer_factory
    s.customer_id = randint(1, 10_000_000)
    c = s.run()
    return model_services.CreateCustomFieldValue(
        custom_field_value_id=randint(1, 10_000_000),
        name="foo",
        value="bar",
        display_value="baz",
        custom_field_id=custom_field_factory().id,
        booking_id=None,
        customer_id=c.id,
        timestamp=datetime.now(timezone.utc) - timedelta(days=1),
    ).run


@pytest.fixture
def checkin_status_factory():
    return model_services.CreateCheckinStatus(
        checkin_status_id=randint(1, 10_000_000),
        checkin_status_type="checked-in",
        name="checked in",
        timestamp=datetime.now(timezone.utc) - timedelta(days=1),
    )


@pytest.fixture
def customer_factory(
    customer_type_rate_factory, booking_factory, checkin_status_factory
):
    s = booking_factory
    s.uuid = uuid4().hex
    b = s.run()
    return model_services.CreateCustomer(
        customer_id=randint(1, 10_000_000),
        checkin_url="https://foo.bar",
        checkin_status_id=checkin_status_factory.run().id,
        customer_type_rate_id=customer_type_rate_factory.run().id,
        booking_id=b.id,
        timestamp=datetime.now(timezone.utc) - timedelta(days=1),
    )


@pytest.fixture
def customer_type_rate_factory(
    availability_factory,
    customer_type_factory,
    customer_prototype_factory,
):
    s = availability_factory
    s.availability_id = (randint(1, 10_000_000),)
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
        timestamp=datetime.now(timezone.utc) - timedelta(days=1),
    )


@pytest.fixture
def customer_prototype_factory():
    return customer_prototype_instance


def customer_prototype_instance(
    total=10, total_including_tax=10, display_name="foo", note="bar"
):
    random_id = randint(1, 10_000_000)
    return model_services.CreateCustomerPrototype(
        customer_prototype_id=random_id,
        total=total,
        total_including_tax=total_including_tax,
        display_name=display_name,
        note=note,
        timestamp=datetime.now(timezone.utc) - timedelta(days=1),
    ).run()


@pytest.fixture
def customer_type_factory():
    return customer_type_instance


def customer_type_instance(
    note="foo", singular="bar", plural="baz", customer_type_id=None
):
    if not customer_type_id:
        customer_type_id = randint(1, 10_000_000)
    return model_services.CreateCustomerType(
        customer_type_id=customer_type_id,
        note=note,
        singular=singular,
        plural=plural,
        timestamp=datetime.now(timezone.utc) - timedelta(days=1),
    ).run()


@pytest.fixture
def bike_factory():
    return bikeinstance


def bikeinstance(
    readable_name="default_bike", uuid=None, timestamp=datetime.now(timezone.utc)
):
    """A convenience wrapper that lets us create several different bikes in a test."""
    if not uuid:
        uuid = uuid4().hex
    return model_services.CreateBike(
        uuid=uuid, readable_name=readable_name, timestamp=timestamp
    ).run()
