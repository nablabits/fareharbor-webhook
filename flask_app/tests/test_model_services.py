from datetime import datetime, timezone
from uuid import uuid4
from random import randint

import pytest

from fh_webhook import models, model_services
from fh_webhook.exceptions import DoesNotExist

from sqlalchemy.exc import IntegrityError


def test_create_item(database):
    random_id = randint(1, 10_000_000)
    timestamp = datetime.now(timezone.utc)
    service = model_services.CreateItem(
        item_id=random_id, name="foo", timestamp=timestamp)
    new_item = service.run()
    new_item = models.Item.get(new_item.id)
    assert new_item.id == random_id
    assert new_item.name == "foo"
    assert new_item.created_at == timestamp
    assert new_item.updated_at == timestamp


def test_update_item(database, item_factory):
    old_item = item_factory.run()
    timestamp = datetime.now(timezone.utc)
    s = model_services.UpdateItem(
        item_id=old_item.id, name="bar", timestamp=timestamp)
    s.run()
    item = models.Item.get(old_item.id)
    assert item.name == "bar"
    assert item.created_at != item.updated_at
    assert item.updated_at == timestamp


def test_delete_item(database, item_factory):
    item = item_factory.run()
    model_services.DeleteItem(item.id).run()
    with pytest.raises(DoesNotExist):
        models.Item.get(item.id)


def test_create_availability(database, item_factory):
    item = item_factory.run()
    random_id = randint(1, 10_000_000)
    timestamp = datetime.now(timezone.utc)
    availability = model_services.CreateAvailability(
        timestamp=timestamp,
        availability_id=random_id,
        capacity=10,
        minimum_party_size=11,
        maximum_party_size=12,
        start_at=timestamp,
        end_at=timestamp,
        item_id=item.id,
    ).run()
    availability = models.Availability.get(random_id)
    assert availability.created_at == timestamp
    assert availability.updated_at == timestamp


def test_update_availability(database, item_factory, availability_factory):
    av = availability_factory.run()
    timestamp = datetime.now(timezone.utc)
    model_services.UpdateAvailability(
        availability_id=av.id,
        timestamp=timestamp,
        capacity=20,
        minimum_party_size=21,
        maximum_party_size=22,
        start_at=timestamp,
        end_at=timestamp,
        item_id=av.item_id,
    ).run()
    av = models.Availability.get(av.id)
    assert av.capacity == 20
    assert av.minimum_party_size == 21
    assert av.maximum_party_size == 22
    assert av.created_at != av.updated_at
    assert av.updated_at == timestamp


def test_delete_availabilty(database, availability_factory):
    av = availability_factory.run()
    model_services.DeleteAvailability(av.id).run()
    with pytest.raises(DoesNotExist):
        models.Availability.get(av.id)


def test_create_booking(database, availability_factory, company_factory):
    av = availability_factory.run()
    company = company_factory.run()
    s_affiliate_company = company_factory
    s_affiliate_company.short_name = uuid4().hex[:30]
    affiliate_company = s_affiliate_company.run()
    timestamp = datetime.now(timezone.utc)
    b = model_services.CreateBooking(
        booking_id=randint(1, 10_000_000),
        timestamp=timestamp,
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
        arrival="sar",
        rebooked_to="saz",
        rebooked_from="woo",
        external_id="war",
        order={"waz": "raz"},
    ).run()
    b = models.Booking.get(b.id)
    assert b.voucher_number == "foo"
    assert b.order == {"waz": "raz"}
    assert b.availability_id == av.id
    assert b.company_id == company.id
    assert b.affiliate_company_id == affiliate_company.id
    assert b.created_at == b.updated_at
    assert b.created_at == timestamp


def test_update_booking(database, booking_factory, availability_factory):
    s = booking_factory
    s.uuid = uuid4().hex
    old_booking = s.run()
    timestamp = datetime.now(timezone.utc)
    b = model_services.UpdateBooking(
        booking_id=old_booking.id,
        voucher_number="roo",
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
        timestamp=timestamp,
        availability_id=old_booking.availability_id,
        company_id=old_booking.company_id,
        affiliate_company_id=old_booking.affiliate_company_id,
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
        order={"waz": "updated_raz"},
    ).run()
    b = models.Booking.get(old_booking.id)
    assert b.voucher_number == "roo"
    assert b.availability_id == old_booking.availability_id
    assert b.company_id == old_booking.company_id
    assert b.affiliate_company_id == old_booking.affiliate_company_id
    assert b.order["waz"] == "updated_raz"
    assert b.created_at != b.updated_at
    assert b.updated_at == timestamp


def test_update_booking_raises_error(database):
    with pytest.raises(DoesNotExist):
        model_services.UpdateBooking(
            booking_id=1000000,
            voucher_number="roo",
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
            timestamp=datetime.now(timezone.utc),
            availability_id=1,
            company_id=1,
            affiliate_company_id=1,
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
        ).run()


def test_delete_booking(database, booking_factory):
    s = booking_factory
    s.uuid = uuid4().hex
    booking = s.run()
    model_services.DeleteBooking(booking.id).run()
    with pytest.raises(DoesNotExist):
        models.Booking.get(booking.id)


def test_delete_booking_raises_error(database):
    with pytest.raises(DoesNotExist):
        model_services.DeleteBooking(100000).run()


def test_create_contact(database, booking_factory):
    s = booking_factory
    s.uuid = uuid4().hex
    b = s.run()
    timestamp = datetime.now(timezone.utc)
    c = model_services.CreateContact(
        id=b.id,
        timestamp=timestamp,
        name="foo",
        email="foo@bar.baz",
        phone_country="49",
        phone="00000",
        normalized_phone="00000",
        is_subscribed_for_email_updates=True,
    ).run()
    c = models.Contact.get(c.id)
    assert c.name == "foo"
    assert c.id == b.id
    assert c.created_at == c.updated_at
    assert c.created_at == timestamp


def test_update_contact(database, contact_factory):
    old_contact = contact_factory()
    timestamp = datetime.now(timezone.utc)
    new_contact = model_services.UpdateContact(
        id=old_contact.id,
        timestamp=timestamp,
        name="bar",
        email="foo@bar.baz",
        phone_country="49",
        phone="00000",
        normalized_phone="00000",
        is_subscribed_for_email_updates=True,
    ).run()
    new_contact = models.Contact.get(new_contact.id)
    assert new_contact.name == "bar"
    assert new_contact.created_at == old_contact.created_at
    assert new_contact.created_at != new_contact.updated_at
    assert new_contact.updated_at == timestamp


def test_delete_contact(database, contact_factory):
    c = contact_factory()
    model_services.DeleteContact(c.id).run()
    with pytest.raises(DoesNotExist):
        models.Contact.get(c.id)


def test_create_company(database):
    timestamp = datetime.now(timezone.utc)
    c = model_services.CreateCompany(
        name="foo", short_name="baz", currency="eur", timestamp=timestamp
    ).run()
    c = models.Company.get("baz")
    assert c.name == "foo"
    assert c.created_at == c.updated_at
    assert c.created_at == timestamp


def test_create_company_raises_unique_exception(database):
    timestamp = datetime.now(timezone.utc)
    model_services.CreateCompany(
        name="foo", short_name="baz", currency="eur", timestamp=timestamp
    ).run()
    with pytest.raises(IntegrityError) as e:
        model_services.CreateCompany(
            name="foo", short_name="baz", currency="eur", timestamp=timestamp
        ).run()
    assert e.match("foo")

    # We have to rollback because we caught the exception and when flushing
    # the database after the test it will throw an error as the change is still
    # there.
    database.session.rollback()


def test_update_company(database, company_factory):
    old_company = company_factory.run()
    old_name = old_company.name
    timestamp = datetime.now(timezone.utc)
    new_company = model_services.UpdateCompany(
        name="some different name we came up with",
        short_name=old_company.short_name,
        currency="eur",
        timestamp=timestamp,
    ).run()

    # reload from db
    new_company = models.Company.get(old_company.short_name)
    assert new_company.name == "some different name we came up with"
    assert new_company.name != old_name
    assert new_company.created_at != new_company.updated_at
    assert new_company.updated_at == timestamp


def test_delete_company(database, company_factory):
    company = company_factory.run()
    model_services.DeleteCompany(company.short_name).run()
    with pytest.raises(DoesNotExist):
        models.Company.get(company.short_name)


def test_create_cancellation_policy(database, booking_factory):
    s = booking_factory
    s.uuid = uuid4().hex
    b = s.run()
    timestamp = datetime.now(timezone.utc)
    new_cp = model_services.CreateCancellationPolicy(
        cutoff=datetime.utcnow(),
        cancellation_type="foo",
        cp_id=b.id,
        timestamp=timestamp,
    ).run()
    cp = models.EffectiveCancellationPolicy.get(new_cp.id)
    assert cp.cancellation_type == "foo"
    assert cp.id == b.id
    assert cp.created_at == cp.updated_at
    assert cp.created_at == timestamp


def test_update_cancellation_policy(database, cancellation_factory):
    old_cp = cancellation_factory()
    new_date = datetime(2021, 5, 5)
    timestamp = datetime.now(timezone.utc)
    new_cp = model_services.UpdateCancellationPolicy(
        cp_id=old_cp.id,
        cutoff=new_date,
        cancellation_type="bar",
        timestamp=timestamp,
    ).run()

    # reload from db
    new_cp = models.EffectiveCancellationPolicy.get(new_cp.id)
    assert new_cp.cutoff.date() == new_date.date()
    assert new_cp.cutoff.time() == new_date.time()
    assert new_cp.cancellation_type == "bar"
    assert new_cp.created_at != new_cp.updated_at
    assert new_cp.updated_at == timestamp


def test_delete_cancellation_policy(database, cancellation_factory):
    cp = cancellation_factory()
    model_services.DeleteCancellationPolicy(cp.id).run()
    with pytest.raises(DoesNotExist):
        models.EffectiveCancellationPolicy.get(cp.id)


def test_create_custom_field(database):
    timestamp = datetime.now(timezone.utc)
    service = model_services.CreateCustomField(
        custom_field_id=randint(1, 10_000_000),
        timestamp=timestamp,
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
    )
    cf = service.run()

    cf = models.CustomField.get(cf.id)
    assert cf.title == "foo"
    assert cf.extended_options is None
    assert cf.created_at == cf.updated_at
    assert cf.updated_at == timestamp


def test_update_custom_field(database, custom_field_factory):
    old_cf = custom_field_factory()
    timestamp = datetime.now(timezone.utc)

    model_services.UpdateCustomField(
        custom_field_id=old_cf.id,
        timestamp=timestamp,
        title="goo",
        name="kar",
        modifier_kind="kaz",
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

    cf = models.CustomField.get(old_cf.id)
    assert cf.title == "goo"
    assert cf.name == "kar"
    assert cf.modifier_kind == "kaz"
    assert cf.created_at != cf.updated_at
    assert cf.updated_at == timestamp


def test_delete_custom_field(database, custom_field_factory):
    cf = custom_field_factory()

    model_services.DeleteCustomField(cf.id).run()

    with pytest.raises(DoesNotExist):
        models.CustomField.get(cf.id)


def test_create_custom_field_instances(
    database, custom_field_factory, availability_factory,
    customer_type_rate_factory
):
    cf = custom_field_factory()
    s = availability_factory
    s.availability_id = randint(1, 10_000_000),
    av = s.run()
    timestamp = datetime.now(timezone.utc)
    cfi = model_services.CreateCustomFieldInstance(
        custom_field_instance_id=randint(1, 10_000_000),
        timestamp=timestamp,
        custom_field_id=cf.id,
        availability_id=av.id,
        customer_type_rate_id=None
    ).run()

    cfi = models.CustomFieldInstance.get(cfi.id)
    assert cfi.custom_field_id == cf.id
    assert cfi.availability_id == av.id
    assert cfi.created_at == cfi.updated_at
    assert cfi.updated_at == timestamp


def test_create_custom_field_instances_raises_error_with_av_and_ctr(
    database, custom_field_factory, availability_factory,
    customer_type_rate_factory
):
    cf = custom_field_factory()
    s = availability_factory
    s.availability_id = randint(1, 10_000_000),
    av = s.run()
    ctr = customer_type_rate_factory()
    with pytest.raises(ValueError) as e:
        model_services.CreateCustomFieldInstance(
            timestamp=datetime.now(timezone.utc),
            custom_field_instance_id=randint(1, 10_000_000),
            custom_field_id=cf.id,
            availability_id=av.id,
            customer_type_rate_id=ctr.id
        ).run()
    assert e.match(
        "Availability and customer type rate can't have value at the same time"
    )


def test_create_custom_field_instances_raises_error_without_av_and_ctr(
    database, custom_field_factory, availability_factory,
    customer_type_rate_factory
):
    cf = custom_field_factory()
    s = availability_factory
    s.availability_id = randint(1, 10_000_000),
    with pytest.raises(ValueError) as e:
        model_services.CreateCustomFieldInstance(
            custom_field_instance_id=randint(1, 10_000_000),
            timestamp=datetime.now(timezone.utc),
            custom_field_id=cf.id,
            availability_id=None,
            customer_type_rate_id=None
        ).run()
    assert e.match(
        "Custom field instance needs either availability or customer type rate"
    )


def test_update_custom_field_instances(
    database, custom_field_instance_factory, availability_factory
):

    old_cfi = custom_field_instance_factory()
    s = availability_factory
    s.availability_id = randint(1, 10_000_000),
    av = s.run()
    old_av_id = old_cfi.availability_id
    timestamp = datetime.now(timezone.utc)
    new_cfi = model_services.UpdateCustomFieldInstance(
        custom_field_instance_id=old_cfi.id,
        timestamp=timestamp,
        custom_field_id=old_cfi.custom_field_id,
        availability_id=av.id,
        customer_type_rate_id=None
    ).run()
    new_cfi = models.CustomFieldInstance.get(new_cfi.id)
    assert new_cfi.created_at == old_cfi.created_at
    assert new_cfi.availability_id != old_av_id
    assert new_cfi.created_at != new_cfi.updated_at
    assert new_cfi.updated_at == timestamp


def test_delete_custom_field_instances(database, custom_field_instance_factory):
    cfi = custom_field_instance_factory()
    model_services.DeleteCustomFieldInstance(cfi.id).run()
    with pytest.raises(DoesNotExist):
        models.CustomFieldInstance.get(cfi.id)


def test_create_custom_field_value(
    database, custom_field_factory, customer_factory
):
    c = customer_factory.run()
    timestamp = datetime.now(timezone.utc)
    cfv = model_services.CreateCustomFieldValue(
        custom_field_value_id=randint(1, 10_000_000),
        timestamp=timestamp,
        name="foo",
        value="bar",
        display_value="baz",
        custom_field_id=custom_field_factory().id,
        booking_id=None,
        customer_id=c.id,
    ).run()
    cfv = models.CustomFieldValue.get(cfv.id)
    assert cfv.name == "foo"
    assert cfv.value == "bar"
    assert cfv.display_value == "baz"
    assert cfv.booking_id is None
    assert cfv.customer_id == c.id
    assert cfv.created_at == cfv.updated_at
    assert cfv.updated_at == timestamp


def test_create_custom_field_value_raises_error_if_booking_and_customer(
        database, custom_field_factory, customer_factory
):
    cfv = model_services.CreateCustomFieldValue(
        custom_field_value_id=randint(1, 10_000_000),
        timestamp=datetime.now(timezone.utc),
        name="foo",
        value="bar",
        display_value="baz",
        custom_field_id=custom_field_factory().id,
        booking_id=10,
        customer_id=20,
    )
    with pytest.raises(ValueError) as e:
        cfv.run()

    assert len(models.CustomFieldValue.query.all()) == 0
    assert e.match("Booking and customer can't have value at the same time.")


def test_create_custom_field_value_raises_error_if_no_booking_and_no_customer(
        database, custom_field_factory, customer_factory
):
    cfv = model_services.CreateCustomFieldValue(
        custom_field_value_id=randint(1, 10_000_000),
        timestamp=datetime.now(timezone.utc),
        name="foo",
        value="bar",
        display_value="baz",
        custom_field_id=custom_field_factory().id,
        booking_id=None,
        customer_id=None,
    )
    with pytest.raises(ValueError) as e:
        cfv.run()

    assert len(models.CustomFieldValue.query.all()) == 0
    assert e.match(
        "Custom field value needs either booking or customer instances")


def test_update_custom_field_value(
    database, custom_field_value_factory, customer_factory
):
    old_cfv = custom_field_value_factory()
    s = customer_factory
    s.customer_id = randint(1, 10_000_000)
    c = s.run()
    timestamp = datetime.now(timezone.utc)

    cfv = model_services.UpdateCustomFieldValue(
        custom_field_value_id=old_cfv.id,
        timestamp=timestamp,
        name="goo",
        value="zar",
        display_value="zaz",
        custom_field_id=old_cfv.custom_field_id,
        booking_id=None,
        customer_id=c.id,
    ).run()
    cfv = models.CustomFieldValue.get(cfv.id)
    assert cfv.name == "goo"
    assert cfv.value == "zar"
    assert cfv.display_value == "zaz"
    assert cfv.booking_id is None
    assert cfv.customer_id == c.id
    assert cfv.created_at != cfv.updated_at
    assert cfv.updated_at == timestamp


def test_delete_custom_field_value(database, custom_field_value_factory):
    cfv = custom_field_value_factory()
    model_services.DeleteCustomFieldValue(cfv.id).run()
    with pytest.raises(DoesNotExist):
        models.CustomFieldValue.get(cfv.id)


def test_create_checkin_status(database, ):
    timestamp = datetime.now(timezone.utc)
    ct = model_services.CreateCheckinStatus(
        checkin_status_id=randint(1, 10_000_000),
        checkin_status_type="checked-in",
        timestamp=timestamp,
        name="checked in"
    ).run()
    cs = models.CheckinStatus.get(ct.id)
    assert cs.created_at == cs.updated_at
    assert cs.updated_at == timestamp


def test_update_checkin_status(
    database, checkin_status_factory, file_timestamp
):
    old_cs = checkin_status_factory.run()
    timestamp = datetime.now(timezone.utc)
    cs = model_services.UpdateCheckinStatus(
        checkin_status_id=old_cs.id,
        checkin_status_type="checked-out",
        name="checked out",
        timestamp=timestamp,
    ).run()
    assert cs.checkin_status_type == "checked-out"
    assert cs.name == "checked out"
    assert cs.created_at == old_cs.created_at
    assert cs.created_at != cs.updated_at
    assert cs.updated_at == timestamp


def test_delete_checkin_status(database, checkin_status_factory):
    cs = checkin_status_factory.run()

    model_services.DeleteCheckinStatus(cs.id).run()

    with pytest.raises(DoesNotExist):
        models.CheckinStatus.get(cs.id)


def test_create_customer(
    database, customer_type_rate_factory, booking_factory,
    availability_factory, checkin_status_factory
):
    s = booking_factory
    s.uuid = uuid4().hex
    b = s.run()
    timestamp = datetime.now(timezone.utc)
    ct = model_services.CreateCustomer(
        customer_id=randint(1, 10_000_000),
        checkin_url="https://foo.bar",
        timestamp=timestamp,
        checkin_status_id=checkin_status_factory.run().id,
        customer_type_rate_id=customer_type_rate_factory().id,
        booking_id=b.id,
    ).run()
    customer = models.Customer.get(ct.id)
    assert customer.created_at == customer.updated_at
    assert customer.updated_at == timestamp


def test_update_customer(database, customer_factory, checkin_status_factory):
    s = customer_factory
    s.customer_id = randint(1, 10_000_000)
    old_customer = s.run()
    timestamp = datetime.now(timezone.utc)
    model_services.UpdateCustomer(
        customer_id=old_customer.id,
        timestamp=timestamp,
        checkin_url="https://bar.baz",
        checkin_status_id=None,
        customer_type_rate_id=old_customer.customer_type_rate_id,
        booking_id=old_customer.booking_id,
    ).run()
    ct = models.Customer.get(old_customer.id)
    assert ct.checkin_url == "https://bar.baz"
    assert ct.checkin_status_id is None
    assert ct.created_at != ct.updated_at
    assert ct.updated_at == timestamp


def test_delete_customer(database, customer_factory):
    ct = customer_factory.run()

    model_services.DeleteCustomer(ct.id).run()

    with pytest.raises(DoesNotExist):
        models.Customer.get(ct.id)


def test_create_customer_type_rate(
    database,
    availability_factory,
    customer_type_factory,
    customer_prototype_factory,
):
    av = availability_factory.run()
    timestamp = datetime.now(timezone.utc)
    ctr = model_services.CreateCustomerTypeRate(
        ctr_id=randint(1, 10_000_000),
        timestamp=timestamp,
        capacity=4,
        minimum_party_size=2,
        maximum_party_size=4,
        total=10,
        total_including_tax=10,
        availability_id=av.id,
        customer_prototype_id=customer_prototype_factory().id,
        customer_type_id=customer_type_factory().id,
    ).run()
    ctr = models.CustomerTypeRate.get(ctr.id)
    assert ctr.created_at == ctr.updated_at
    assert ctr.updated_at == timestamp


def test_update_customer_type_rate(database, customer_type_rate_factory):
    old_ctr = customer_type_rate_factory()
    timestamp = datetime.now(timezone.utc)
    model_services.UpdateCustomerTypeRate(
        timestamp=timestamp,
        ctr_id=old_ctr.id,
        capacity=6,
        minimum_party_size=1,
        maximum_party_size=6,
        total=11,
        total_including_tax=11,
        availability_id=old_ctr.availability_id,
        customer_prototype_id=old_ctr.customer_prototype_id,
        customer_type_id=old_ctr.customer_type_id,
    ).run()
    updated_ctr = models.CustomerTypeRate.get(old_ctr.id)
    assert updated_ctr.capacity == 6
    assert updated_ctr.minimum_party_size == 1
    assert updated_ctr.maximum_party_size == 6
    assert updated_ctr.total == 11
    assert updated_ctr.total_including_tax == 11
    assert updated_ctr.created_at != updated_ctr.updated_at
    assert updated_ctr.updated_at == timestamp


def test_delete_customer_type_rate(database, customer_type_rate_factory):
    ctr = customer_type_rate_factory()
    model_services.DeleteCustomerTypeRate(ctr.id).run()
    with pytest.raises(DoesNotExist):
        models.CustomerTypeRate.get(ctr.id)


def test_create_customer_prototype(database):
    timestamp = datetime.now(timezone.utc)
    service = model_services.CreateCustomerPrototype(
        customer_prototype_id=randint(1, 10_000_000),
        total=10,
        total_including_tax=10,
        display_name="foo",
        note="bar",
        timestamp=timestamp,
    )
    new_customer_prototype = service.run()
    cp = models.CustomerPrototype.get(new_customer_prototype.id)
    assert cp.created_at == cp.updated_at
    assert cp.updated_at == timestamp


def test_update_customer_prototype(database, customer_prototype_factory):
    old_cp = customer_prototype_factory()

    timestamp = datetime.now(timezone.utc)
    model_services.UpdateCustomerPrototype(
        customer_prototype_id=old_cp.id,
        total=20,
        total_including_tax=20,
        display_name="bar",
        note="baz",
        timestamp=timestamp,
    ).run()

    cp = models.CustomerPrototype.get(old_cp.id)
    assert cp.total == 20
    assert cp.total_including_tax == 20
    assert cp.display_name == "bar"
    assert cp.note == "baz"
    assert cp.created_at != cp.updated_at
    assert cp.updated_at == timestamp


def test_delete_customer_prototype(database, customer_prototype_factory):
    cp = customer_prototype_factory()
    model_services.DeleteCustomerPrototype(cp.id).run()
    with pytest.raises(DoesNotExist):
        models.CustomerPrototype.get(cp.id)


def test_create_customer_type(database):
    timestamp = datetime.now(timezone.utc)
    ct = model_services.CreateCustomerType(
        customer_type_id=randint(1, 10_000_000),
        note="foo",
        singular="bar",
        plural="baz",
        timestamp=timestamp,
    ).run()
    ct = models.CustomerType.get(ct.id)
    assert ct.created_at == ct.updated_at
    assert ct.updated_at == timestamp


def test_update_customer_type(database, customer_type_factory):
    ct = customer_type_factory()
    timestamp = datetime.now(timezone.utc)
    model_services.UpdateCustomerType(
        customer_type_id=ct.id,
        note="goo",
        singular="kar",
        plural="kaz",
        timestamp=timestamp,
    ).run()

    updated_ct = models.CustomerType.get(ct.id)
    assert updated_ct.note == "goo"
    assert updated_ct.created_at != updated_ct.updated_at
    assert updated_ct.updated_at == timestamp


def test_delete_customer_type(database, customer_type_factory):
    ct = customer_type_factory()

    assert models.CustomerType.get(ct.id)
    model_services.DeleteCustomerType(ct.id).run()
    with pytest.raises(DoesNotExist):
        models.CustomerType.get(ct.id)
