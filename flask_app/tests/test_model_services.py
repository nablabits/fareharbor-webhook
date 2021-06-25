from datetime import datetime
from uuid import uuid4
from random import randint

import pytest

from fh_webhook import models, model_services
from fh_webhook.exceptions import DoesNotExist


def test_create_item(database):
    random_id = randint(1, 10_000_000)
    service = model_services.CreateItem(item_id=random_id, name="foo")
    new_item = service.run()
    new_item = models.Item.get(new_item.id)
    assert new_item.id == random_id
    assert new_item.name == "foo"


def test_update_item(database, item_factory):
    old_item = item_factory.run()
    s = model_services.UpdateItem(item_id=old_item.id, name="bar")
    s.run()
    item = models.Item.get(old_item.id)
    assert item.name == "bar"


def test_delete_item(database, item_factory):
    item = item_factory.run()
    model_services.DeleteItem(item.id).run()
    with pytest.raises(DoesNotExist):
        models.Item.get(item.id)


def test_create_availability(database, item_factory):
    item = item_factory.run()
    random_id = randint(1, 10_000_000)
    availability = model_services.CreateAvailability(
        availability_id=random_id,
        capacity=10,
        minimum_party_size=11,
        maximum_party_size=12,
        start_at=datetime.now(),
        end_at=datetime.now(),
        item_id=item.id,
    ).run()
    assert models.Availability.get(availability.id)


def test_update_availability(database, item_factory, availability_factory):
    av = availability_factory.run()
    model_services.UpdateAvailability(
        availability_id=av.id,
        capacity=20,
        minimum_party_size=21,
        maximum_party_size=22,
        start_at=datetime.now(),
        end_at=datetime.now(),
        item_id=av.item_id,
    ).run()
    av = models.Availability.get(av.id)
    assert av.capacity == 20
    assert av.minimum_party_size == 21
    assert av.maximum_party_size == 22


def test_delete_availabilty(database, availability_factory):
    av = availability_factory.run()
    model_services.DeleteAvailability(av.id).run()
    with pytest.raises(DoesNotExist):
        models.Availability.get(av.id)


def test_create_booking(database, availability_factory):
    av = availability_factory.run()
    b = model_services.CreateBooking(
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
    ).run()
    b = models.Booking.get(b.id)
    assert b.voucher_number == "foo"
    assert b.availability_id == av.id


def test_update_booking(database, booking_factory, availability_factory):
    s = booking_factory
    s.uuid = uuid4().hex
    old_booking = s.run()
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
        availability_id=old_booking.availability_id,
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
    b = models.Booking.get(old_booking.id)
    assert b.voucher_number == "roo"
    assert b.availability_id == old_booking.availability_id


def test_update_booking_raises_error(database, availability_factory):
    av = availability_factory.run()
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
    c = model_services.CreateContact(
        name="foo",
        email="foo@bar.baz",
        phone_country="49",
        phone="00000",
        normalized_phone="00000",
        is_subscribed_for_email_updates=True,
        booking_id=b.id,
    ).run()
    c = models.Contact.get(c.id)
    assert c.name == "foo"
    assert c.booking_id == b.id


def test_update_contact(database, contact_factory):
    old_contact = contact_factory()
    new_contact = model_services.UpdateContact(
        contact_id=old_contact.id,
        name="bar",
        email="foo@bar.baz",
        phone_country="49",
        phone="00000",
        normalized_phone="00000",
        is_subscribed_for_email_updates=True,
    ).run()
    new_contact = models.Contact.get(new_contact.id)
    assert new_contact.name == "bar"


def test_delete_contact(database, contact_factory):
    c = contact_factory()
    model_services.DeleteContact(c.id).run()
    with pytest.raises(DoesNotExist):
        models.Contact.get(c.id)


def test_create_company(database, booking_factory):
    s = booking_factory
    s.uuid = uuid4().hex
    b = s.run()
    c = model_services.CreateCompany(
        name="foo", short_name="bar", currency="eur", booking_id=b.id
    ).run()
    c = models.Company.get(c.id)
    assert c.name == "foo"
    assert c.booking_id == b.id


def test_update_company(database, company_factory):
    old_company = company_factory()
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
    company = company_factory()
    model_services.DeleteCompany(company.id).run()
    with pytest.raises(DoesNotExist):
        models.Company.get(company.id)


def test_create_cancellation_policy(database, booking_factory):
    s = booking_factory
    s.uuid = uuid4().hex
    b = s.run()
    new_cp = model_services.CreateCancellationPolicy(
        cutoff=datetime.utcnow(), cancellation_type="foo", booking_id=b.id
    ).run()
    cp = models.EffectiveCancellationPolicy.get(new_cp.id)
    assert cp.cancellation_type == "foo"
    assert cp.booking_id == b.id


def test_update_cancellation_policy(database, cancellation_factory):
    old_cp = cancellation_factory()
    new_date = datetime(2021, 5, 5)
    new_cp = model_services.UpdateCancellationPolicy(
        cp_id=old_cp.id, cutoff=new_date, cancellation_type="bar"
    ).run()

    # reload from db
    new_cp = models.EffectiveCancellationPolicy.get(new_cp.id)
    assert new_cp.cutoff.date() == new_date.date()
    assert new_cp.cutoff.time() == new_date.time()
    assert new_cp.cancellation_type == "bar"


def test_delete_cancellation_policy(database, cancellation_factory):
    cp = cancellation_factory()
    model_services.DeleteCancellationPolicy(cp.id).run()
    with pytest.raises(DoesNotExist):
        models.EffectiveCancellationPolicy.get(cp.id)


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

    cf = models.CustomField.get(cf.id)
    assert cf.title == "foo"
    assert cf.extended_options is None


def test_update_custom_field(database, custom_field_factory):
    old_cf = custom_field_factory()

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

    cf = models.CustomField.get(old_cf.id)
    assert cf.title == "goo"
    assert cf.name == "kar"
    assert cf.modifier_kind == "kaz"


def test_delete_custom_field(database, custom_field_factory):
    cf = custom_field_factory()

    model_services.DeleteCustomField(cf.id).run()

    with pytest.raises(DoesNotExist):
        models.CustomField.get(cf.id)


def test_create_custom_field_instances(
    database, custom_field_factory, availability_factory
):
    cf, av = custom_field_factory(), availability_factory()
    cfi = model_services.CreateCustomFieldInstance(
        custom_field_id=cf.id, availability_id=av.id
    ).run()

    cfi = models.CustomFieldInstance.get(cfi.id)
    assert cfi.custom_field_id == cf.id
    assert cfi.availability_id == av.id


def test_update_custom_field_instances(
    database, custom_field_instance_factory, availability_factory
):
    av = availability_factory()

    old_cfi = custom_field_instance_factory()
    old_av_id = old_cfi.availability_id
    new_cfi = model_services.UpdateCustomFieldInstance(
        custom_field_instance_id=old_cfi.id,
        custom_field_id=old_cfi.custom_field_id,
        availability_id=av.id,
    ).run()
    new_cfi = models.CustomFieldInstance.get(new_cfi.id)
    assert new_cfi.created_at == old_cfi.created_at
    assert new_cfi.availability_id != old_av_id


def test_delete_custom_field_instances(database, custom_field_instance_factory):
    cfi = custom_field_instance_factory()
    model_services.DeleteCustomFieldInstance(cfi.id).run()
    with pytest.raises(DoesNotExist):
        models.CustomFieldInstance.get(cfi.id)


def test_create_custom_field_value(database, custom_field_factory, customer_factory):
    c = customer_factory()
    cfv = model_services.CreateCustomFieldValue(
        name="foo",
        value="bar",
        display_value="baz",
        custom_field_id=custom_field_factory().id,
        booking_id=c.booking_id,
        customer_id=c.id,
    ).run()
    cfv = models.CustomFieldValue.get(cfv.id)
    assert cfv.name == "foo"
    assert cfv.value == "bar"
    assert cfv.display_value == "baz"
    assert cfv.booking_id == c.booking_id
    assert cfv.customer_id == c.id


def test_update_custom_field_value(
    database, custom_field_value_factory, customer_factory
):
    old_cfv = custom_field_value_factory()
    c = customer_factory()
    cfv = model_services.UpdateCustomFieldValue(
        custom_field_value_id=old_cfv.id,
        name="goo",
        value="zar",
        display_value="zaz",
        custom_field_id=old_cfv.custom_field_id,
        booking_id=c.booking_id,
        customer_id=c.id,
    ).run()
    cfv = models.CustomFieldValue.get(cfv.id)
    assert cfv.name == "goo"
    assert cfv.value == "zar"
    assert cfv.display_value == "zaz"
    assert cfv.booking_id == c.booking_id
    assert cfv.customer_id == c.id


def test_delete_custom_field_value(database, custom_field_value_factory):
    cfv = custom_field_value_factory()
    model_services.DeleteCustomFieldValue(cfv.id).run()
    with pytest.raises(DoesNotExist):
        models.CustomFieldValue.get(cfv.id)


def test_create_customer(
    database, customer_type_rate_factory, booking_factory, availability_factory
):
    s = booking_factory
    s.uuid = uuid4().hex
    b = s.run()
    ct = model_services.CreateCustomer(
        checkin_url="https://foo.bar",
        checking_status="checked_in",
        customer_type_rate_id=customer_type_rate_factory().id,
        booking_id=b.id,
    ).run()
    assert models.Customer.get(ct.id)


def test_update_customer(database, customer_factory):
    old_customer = customer_factory()
    model_services.UpdateCustomer(
        customer_id=old_customer.id,
        checkin_url="https://bar.baz",
        checking_status="checked_out",
        customer_type_rate_id=old_customer.customer_type_rate_id,
        booking_id=old_customer.booking_id,
    ).run()
    ct = models.Customer.get(old_customer.id)
    assert ct.checkin_url == "https://bar.baz"
    assert ct.checking_status == "checked_out"


def test_delete_customer(database, customer_factory):
    ct = customer_factory()

    model_services.DeleteCustomer(ct.id).run()

    with pytest.raises(DoesNotExist):
        models.Customer.get(ct.id)


def test_create_customer_type_rate(
    database,
    booking_factory,
    availability_factory,
    customer_type_factory,
    customer_prototype_factory,
):
    s = booking_factory
    s.uuid = uuid4().hex
    b = s.run()
    ctr = model_services.CreateCustomerTypeRate(
        capacity=4,
        minimum_party_size=2,
        maximum_party_size=4,
        booking_id=b.id,
        availability_id=availability_factory().id,
        customer_prototype_id=customer_prototype_factory().id,
        customer_type_id=customer_type_factory().id,
    ).run()
    assert models.CustomerTypeRate.get(ctr.id)


def test_update_customer_type_rate(database, customer_type_rate_factory):
    old_ctr = customer_type_rate_factory()
    model_services.UpdateCustomerTypeRate(
        ctr_id=old_ctr.id,
        capacity=6,
        minimum_party_size=1,
        maximum_party_size=6,
        booking_id=old_ctr.booking_id,
        availability_id=old_ctr.availability_id,
        customer_prototype_id=old_ctr.customer_prototype_id,
        customer_type_id=old_ctr.customer_type_id,
    ).run()
    updated_ctr = models.CustomerTypeRate.get(old_ctr.id)
    assert updated_ctr.capacity == 6
    assert updated_ctr.minimum_party_size == 1
    assert updated_ctr.maximum_party_size == 6


def test_delete_customer_type_rate(database, customer_type_rate_factory):
    ctr = customer_type_rate_factory()
    model_services.DeleteCustomerTypeRate(ctr.id).run()
    with pytest.raises(DoesNotExist):
        models.CustomerTypeRate.get(ctr.id)


def test_create_customer_prototype(database):
    service = model_services.CreateCustomerPrototype(
        total=10, total_including_tax=10, display_name="foo", note="bar"
    )
    new_customer_prototype = service.run()
    assert models.CustomerPrototype.get(new_customer_prototype.id)


def test_update_customer_prototype(database, customer_prototype_factory):
    old_cp = customer_prototype_factory()

    model_services.UpdateCustomerPrototype(
        customer_prototype_id=old_cp.id,
        total=20,
        total_including_tax=20,
        display_name="bar",
        note="baz",
    ).run()

    cp = models.CustomerPrototype.get(old_cp.id)
    assert cp.total == 20
    assert cp.total_including_tax == 20
    assert cp.display_name == "bar"
    assert cp.note == "baz"


def test_delete_customer_prototype(database, customer_prototype_factory):
    cp = customer_prototype_factory()
    model_services.DeleteCustomerPrototype(cp.id).run()
    with pytest.raises(DoesNotExist):
        models.CustomerPrototype.get(cp.id)


def test_create_customer_type(database):
    ct = model_services.CreateCustomerType(
        note="foo",
        singular="bar",
        plural="baz",
    ).run()
    assert models.CustomerType.get(ct.id)


def test_update_customer_type(database, customer_type_factory):
    ct = customer_type_factory()
    model_services.UpdateCustomerType(
        customer_type_id=ct.id, note="goo", singular="kar", plural="kaz"
    ).run()

    updated_ct = models.CustomerType.get(ct.id)
    assert updated_ct.note == "goo"


def test_delete_customer_type(database, customer_type_factory):
    ct = customer_type_factory()

    assert models.CustomerType.get(ct.id)
    model_services.DeleteCustomerType(ct.id).run()
    with pytest.raises(DoesNotExist):
        models.CustomerType.get(ct.id)
