from datetime import datetime
from uuid import uuid4

import pytest

from fh_webhook import models, model_services
from fh_webhook.exceptions import DoesNotExist


def test_create_item(database):
    service = model_services.CreateItem(name="foo")
    new_item = service.run()
    assert models.Item.query.get(new_item.id)


def test_update_item(database, item_factory):
    old_item = item_factory
    s = model_services.UpdateItem(item_id=old_item.id, name="bar")
    s.run()
    item = models.Item.query.get(old_item.id)
    assert item.name == "bar"


def test_delete_item(database, item_factory):
    item = item_factory
    model_services.DeleteItem(item.id).run()
    item = models.Item.query.get(item.id)
    assert item is None


def test_create_availabilty(database, item_factory):
    item = item_factory
    availability = model_services.CreateAvailability(
        capacity=10,
        minimum_party_size=11,
        maximum_party_size=12,
        start_at=datetime.now(),
        end_at=datetime.now(),
        item_id=item.id
    ).run()
    assert models.Availability.query.get(availability.id)


def test_update_availability(database, item_factory, availability_factory):
    item = item_factory
    av = availability_factory
    model_services.UpdateAvailability(
        availability_id=av.id,
        capacity=20,
        minimum_party_size=21,
        maximum_party_size=22,
        start_at=datetime.now(),
        end_at=datetime.now(),
        item_id=item.id
    ).run()
    av = models.Availability.query.get(av.id)
    assert av.capacity == 20
    assert av.minimum_party_size == 21
    assert av.maximum_party_size == 22


def test_delete_availabilty(database, availability_factory):
    av = availability_factory
    model_services.DeleteAvailability(av.id).run()
    av = models.Availability.query.get(av.id)
    assert av is None


def test_create_booking(database, availability_factory):
    av = availability_factory
    b = model_services.CreateBooking(
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
        order="waz",
    ).run()
    b = models.Booking.query.get(b.id)
    assert b.voucher_number == "foo"
    assert b.availability_id == av.id


def test_update_booking(database, booking_factory, availability_factory):
    old_booking = booking_factory
    av = availability_factory
    b = model_services.UpdateBooking(
        booking_id=old_booking.id,
        voucher_number="roo",
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
        order="waz",
    ).run()
    b = models.Booking.query.get(old_booking.id)
    assert b.voucher_number == "roo"
    assert b.availability_id == av.id


def test_update_booking_raises_error(database, availability_factory):
    av = availability_factory
    with pytest.raises(DoesNotExist):
        model_services.UpdateBooking(
            booking_id=1000000,
            voucher_number="roo",
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
            order="waz",
        ).run()


def test_delete_booking(database, booking_factory):
    booking = booking_factory
    model_services.DeleteBooking(booking.id).run()
    assert models.Booking.query.get(booking.id) is None


def test_delete_booking_raises_error(database):
    with pytest.raises(DoesNotExist):
        model_services.DeleteBooking(100000).run()


def test_create_contact(database, booking_factory):
    b = booking_factory
    c = model_services.CreateContact(
        name="foo",
        email="foo@bar.baz",
        phone_country="49",
        phone="00000",
        normalized_phone="00000",
        is_subscribed_for_email_updates=True,
        booking_id=b.id
    ).run()
    c = models.Contact.get(c.id)
    assert c.name == "foo"
    assert c.booking_id == b.id


def test_update_contact(database, contact_factory):
    old_contact = contact_factory
    new_contact = model_services.UpdateContact(
        contact_id=old_contact.id,
        name="bar",
        email="foo@bar.baz",
        phone_country="49",
        phone="00000",
        normalized_phone="00000",
        is_subscribed_for_email_updates=True
    ).run()
    new_contact = models.Contact.get(new_contact.id)
    assert new_contact.name == "bar"


def test_delete_contact(database, contact_factory):
    c = contact_factory
    model_services.DeleteContact(c.id).run()
    with pytest.raises(DoesNotExist):
        models.Contact.get(c.id)


def test_create_company(database, booking_factory):
    b = booking_factory
    c = model_services.CreateCompany(
        name="foo",
        short_name="bar",
        currency="eur",
        booking_id=b.id
    ).run()
    c = models.Company.get(c.id)
    assert c.name == "foo"
    assert c.booking_id == b.id


def test_update_company(database, company_factory):
    old_company = company_factory
    new_company = model_services.UpdateCompany(
        company_id=old_company.id,
        name="baz",
        short_name="bar",
        currency="eur",
    ).run()
    # reload from db
    new_company = models.Contact.get(new_company.id)
    assert new_company.name == "bar"


def test_delete_company(database, company_factory):
    company = company_factory
    model_services.DeleteCompany(company.id).run()
    with pytest.raises(DoesNotExist):
        models.Company.get(company.id)


def test_create_custom_field(database):
    service = model_services.CreateCustomField(
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

    cf = models.CustomField.query.get(cf.id)
    assert cf.title == "foo"
    assert cf.extended_options is None


def test_update_custom_field(database, custom_field_factory):
    old_cf = custom_field_factory

    model_services.UpdateCustomField(
        custom_field_id=old_cf.id,
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

    cf = models.CustomField.query.get(old_cf.id)
    assert cf.title == "goo"
    assert cf.name == "kar"
    assert cf.modifier_kind == "kaz"


def test_delete_custom_field(database, custom_field_factory):
    cf = custom_field_factory

    model_services.DeleteCustomField(cf.id).run()

    cf = models.CustomField.query.get(cf.id)
    assert cf is None


def test_create_customer_prototype(database):
    service = model_services.CreateCustomerPrototype(
        total=10,
        total_including_tax=10,
        display_name="foo",
        note="bar"
    )
    new_customer_prototype = service.run()
    assert models.CustomerPrototype.query.get(new_customer_prototype.id)


def test_update_customer_prototype(database, customer_prototype_factory):
    old_cp = customer_prototype_factory

    model_services.UpdateCustomerPrototype(
        customer_prototype_id=old_cp.id,
        total=20,
        total_including_tax=20,
        display_name="bar",
        note="baz"
    ).run()

    cp = models.CustomerPrototype.query.get(old_cp.id)
    assert cp.total == 20
    assert cp.total_including_tax == 20
    assert cp.display_name == "bar"
    assert cp.note == "baz"


def test_delete_customer_prototype(database, customer_prototype_factory):
    cp = customer_prototype_factory
    model_services.DeleteCustomerPrototype(cp.id).run()
    cp = models.CustomerPrototype.query.get(cp.id)
    assert cp is None


def test_create_customer_type(database):
    ct = model_services.CreateCustomerType(
        note="foo",
        singular="bar",
        plural="baz",
    ).run()
    assert models.CustomerType.query.get(ct.id)


def test_update_customer_type(database, customer_type_factory):
    ct = customer_type_factory
    model_services.UpdateCustomerType(
        customer_type_id=ct.id,
        note="goo",
        singular="kar",
        plural="kaz"
    ).run()

    updated_ct = models.CustomerType.query.get(ct.id)
    assert updated_ct.note == "goo"


def test_delete_customer_type(database, customer_type_factory):
    ct = customer_type_factory

    assert models.CustomerType.query.get(ct.id)
    model_services.DeleteCustomerType(ct.id).run()
    assert models.CustomerType.query.get(ct.id) is None
