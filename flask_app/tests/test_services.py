import json
from datetime import date
import pytest

from fh_webhook import services, models


def test_populate_db_creates_item(database, app):
    app.config["RESPONSES_PATH"] = "tests/sample_data/"
    services.PopulateDB(app).run()
    item = models.Item.get(159068)
    assert item.name == "Alquiler Urbana"


def test_populate_db_creates_availability(database, app, item_factory):
    """
    Although the first test actually saves all the data contained in
    sample_data, we split the tests into manageable chunks for readability.
    This comes with the trade off of speed as to avoid unique field exceptions,
    the scope of the database has to be set to function and therefore an empty
    database is used per test that increases the running time.
    """
    app.config["RESPONSES_PATH"] = "tests/sample_data/"
    services.PopulateDB(app).run()
    av = models.Availability.get(619118440)
    assert av.capacity == 49
    assert av.minimum_party_size == 1
    assert av.maximum_party_size is None
    assert av.start_at.isoformat() == "2021-04-05T12:30:00+02:00"
    assert av.end_at.isoformat() == "2021-04-05T13:00:00+02:00"


def test_populate_db_creates_booking(database, app, item_factory):
    """
    Although the first test actually saves all the data contained in
    sample_data, we split the tests into manageable chunks for readability.
    This comes with the trade off of speed as to avoid unique field exceptions,
    the scope of the database has to be set to function and therefore an empty
    database is used per test that increases the running time.
    """
    app.config["RESPONSES_PATH"] = "tests/sample_data/"
    services.PopulateDB(app).run()
    b = models.Booking.get(75125154)
    assert b.id == 75125154
    assert b.voucher_number == ""
    assert b.display_id == "#75125154"
    assert b.note_safe_html == ""
    assert b.agent is None
    assert b.confirmation_url == "https://fareharbor.com/embeds/book/tournebilbao/items/159068/booking/c6c1c394-3c31-4e30-bf9d-da3e1dde7d6e/"
    assert b.customer_count == 1
    assert b.affiliate_company is None
    assert b.uuid == "c6c1c394-3c31-4e30-bf9d-da3e1dde7d6e"
    assert b.dashboard_url == "https://fareharbor.com/tournebilbao/dashboard/?overlay=/contacts/64015149/bookings/c6c1c394-3c31-4e30-bf9d-da3e1dde7d6e/"
    assert b.note == ""
    assert b.pickup is None
    assert b.status == "booked"
    assert b.availability_id == 619118440
    assert b.receipt_subtotal == 1240
    assert b.receipt_taxes == 260
    assert b.receipt_total == 1500
    assert b.amount_paid == 0
    assert b.invoice_price == 0
    assert b.receipt_subtotal_display == "12,40\\u00a0"
    assert b.receipt_taxes_display == "2,60\\u00a0"
    assert b.receipt_total_display == "15,00\\u00a0"
    assert b.amount_paid_display == "0,00\\u00a0"
    assert b.invoice_price_display == "0,00\\u00a0"
    assert b.desk is None
    assert b.is_eligible_for_cancellation is True
    assert b.arrival is None
    assert b.rebooked_to is None
    assert b.rebooked_from is None
    assert b.external_id == ""
    assert b.order is None


def test_populate_db_creates_contact(database, app):
    """
    Although the first test actually saves all the data contained in
    sample_data, we split the tests into manageable chunks for readability.
    This comes with the trade off of speed as to avoid unique field exceptions,
    the scope of the database has to be set to function and therefore an empty
    database is used per test that increases the running time.
    """
    app.config["RESPONSES_PATH"] = "tests/sample_data/"
    services.PopulateDB(app).run()

    contact = models.Contact.get(75125154)
    assert contact.phone_country == "ES"
    assert contact.name == "Foo Bar"
    assert contact.is_subscribed_for_email_updates is False
    assert contact.normalized_phone == "+34444"
    assert contact.phone == "44444"
    assert contact.email == "foo@bar.baz"


def test_populate_db_creates_company(database, app):
    """
    Although the first test actually saves all the data contained in
    sample_data, we split the tests into manageable chunks for readability.
    This comes with the trade off of speed as to avoid unique field exceptions,
    the scope of the database has to be set to function and therefore an empty
    database is used per test that increases the running time.
    """
    app.config["RESPONSES_PATH"] = "tests/sample_data/"
    services.PopulateDB(app).run()

    company = models.Company.get(75125154)
    assert company.name == "Tourne"
    assert company.short_name == "tournebilbao"
    assert company.currency == "eur"


def test_populate_db_creates_cancellation_policy(database, app):
    """
    Although the first test actually saves all the data contained in
    sample_data, we split the tests into manageable chunks for readability.
    This comes with the trade off of speed as to avoid unique field exceptions,
    the scope of the database has to be set to function and therefore an empty
    database is used per test that increases the running time.
    """
    app.config["RESPONSES_PATH"] = "tests/sample_data/"
    services.PopulateDB(app).run()

    cp = models.EffectiveCancellationPolicy.get(75125154)
    assert cp.cutoff.isoformat() == "2021-04-03T12:30:00+02:00"
    assert cp.cancellation_type == "hours-before-start"
