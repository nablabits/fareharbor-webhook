import os
import json
from unittest.mock import patch
from datetime import date, datetime, timezone
import pytest

from fh_webhook import services, models


def test_save_response_as_file(app):
    json_response = dict(foo="bar", baz="gaz")
    path = app.config.get("RESPONSES_PATH")
    timestamp = datetime.now(timezone.utc)
    [os.remove(os.path.join(path, f)) for f in os.listdir(path)]

    filename = services.SaveResponseAsFile(
        json_response, path, timestamp
    ).run()

    files_in_dir = os.listdir(path)
    assert len(files_in_dir) == 1
    with open(os.path.join(path, files_in_dir[0])) as json_file:
        data = json.load(json_file)
        assert json_response == data

    assert filename == files_in_dir[0].split("/")[-1]

    # purge created files
    [os.remove(os.path.join(path, f)) for f in os.listdir(path)]


def test_get_request_id(app):
    app.config["RESPONSES_PATH"] = "tests/sample_data/"
    assert services.get_request_id_or_none("188.12.json") == 18812


@patch("fh_webhook.services.ProcessJSONResponse.run")
def test_process_file_skips_non_json_files(mock_service, app):
    app.config["RESPONSES_PATH"] = "tests/sample_data/"
    service = services.PopulateDB(app)
    service._process_file("188.12")
    assert mock_service.call_count == 0


@patch("fh_webhook.services.ProcessJSONResponse.run")
def test_process_file_skips_existing_files(
    mock_service, database, app, stored_request_factory
):
    app.config["RESPONSES_PATH"] = "tests/sample_data/"
    stored_request = stored_request_factory.run()
    service = services.PopulateDB(app)
    service._process_file(stored_request.filename)
    assert mock_service.call_count == 0


def test_populate_db_creates_stored_request(database, app, file_timestamp):
    app.config["RESPONSES_PATH"] = "tests/sample_data/"
    services.PopulateDB(app).run()
    request_id = 1626842330051856
    stored_request = models.StoredRequest.get(request_id)
    assert stored_request.filename == "1626842330.051856.json"
    assert stored_request.processed_at is not None
    assert stored_request.body[:20] == '{"booking": {"vouche'
    assert stored_request.body[-20:] == 'lay_id": "BBVBQV"}}}'


def test_populate_db_creates_item(database, app, file_timestamp):
    app.config["RESPONSES_PATH"] = "tests/sample_data/"
    services.PopulateDB(app).run()
    item = models.Item.get(159068)
    assert item.name == "Alquiler Urbana"
    assert item.created_at == item.updated_at
    assert item.updated_at == file_timestamp


def test_populate_db_creates_companies(database, app, file_timestamp):
    app.config["RESPONSES_PATH"] = "tests/sample_data/"
    services.PopulateDB(app).run()
    company, affiliate_company = models.Company.query.all()
    assert company.name == "Tourne"
    assert company.short_name == "tournebilbao"
    assert company.currency == "eur"
    assert affiliate_company.name == "Civitatis - EUR"
    assert affiliate_company.short_name == "civitatiseuro"
    assert affiliate_company.currency == "eur"
    assert affiliate_company.created_at == affiliate_company.updated_at
    assert affiliate_company.updated_at == file_timestamp


def test_populate_db_creates_availability(
        database, app, item_factory, file_timestamp
):
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
    assert av.created_at == av.updated_at
    assert av.updated_at == file_timestamp


def test_populate_db_creates_booking(
    database, app, item_factory, file_timestamp
):
    app.config["RESPONSES_PATH"] = "tests/sample_data/"
    services.PopulateDB(app).run()
    b = models.Booking.get(75125154)
    company = models.Company.get("tournebilbao")
    affiliate_company = models.Company.get("civitatiseuro")
    assert b.id == 75125154
    assert b.voucher_number == ""
    assert b.display_id == "#75125154"
    assert b.note_safe_html == ""
    assert b.agent is None
    assert b.confirmation_url == "https://fareharbor.com/embeds/book/tournebilbao/items/159068/booking/c6c1c394-3c31-4e30-bf9d-da3e1dde7d6e/"
    assert b.customer_count == 1
    assert b.uuid == "c6c1c394-3c31-4e30-bf9d-da3e1dde7d6e"
    assert b.dashboard_url == "https://fareharbor.com/tournebilbao/dashboard/?overlay=/contacts/64015149/bookings/c6c1c394-3c31-4e30-bf9d-da3e1dde7d6e/"
    assert b.note == ""
    assert b.pickup is None
    assert b.status == "booked"
    assert b.created_by == "civitatiseuro"
    assert b.created_at == b.updated_at
    assert b.updated_at == file_timestamp
    assert b.availability_id == 619118440
    assert b.company_id == company.id
    assert b.affiliate_company_id == affiliate_company.id
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
    assert b.order["display_id"] == "BBVBQV"


def test_populate_db_creates_contact(database, app, file_timestamp):
    app.config["RESPONSES_PATH"] = "tests/sample_data/"
    services.PopulateDB(app).run()

    contact = models.Contact.get(75125154)
    assert contact.phone_country == "ES"
    assert contact.name == "Foo Bar"
    assert contact.is_subscribed_for_email_updates is False
    assert contact.normalized_phone == "+34444"
    assert contact.phone == "44444"
    assert contact.email == "foo@bar.baz"
    assert contact.created_at == contact.updated_at
    assert contact.updated_at == file_timestamp


def test_populate_db_creates_cancellation_policy(
    database, app, file_timestamp
):
    app.config["RESPONSES_PATH"] = "tests/sample_data/"
    services.PopulateDB(app).run()

    cp = models.EffectiveCancellationPolicy.get(75125154)
    assert cp.cutoff.isoformat() == "2021-04-03T12:30:00+02:00"
    assert cp.cancellation_type == "hours-before-start"
    assert cp.created_at == cp.updated_at
    assert cp.updated_at == file_timestamp


def test_populate_db_creates_customer_types(database, app, file_timestamp):
    """
    Note that, 314999 is duplicated as it's the chosen one among availability
    possible customer types.
    """
    app.config["RESPONSES_PATH"] = "tests/sample_data/"
    services.PopulateDB(app).run()

    ct_ids = (314999, 314997, 314998, 314999, 315000, 315001, 315002, 315003)
    for ct_id in ct_ids:
        ct = models.CustomerType.get(ct_id)
    assert len(models.CustomerType.query.all()) == len(ct_ids) - 1
    assert ct.note == "Todas las edades"
    assert ct.singular == "D\\u00eda extra"
    assert ct.plural == "D\\u00edas extras"
    assert ct.created_at == ct.updated_at
    assert ct.updated_at == file_timestamp


def test_populate_db_creates_customer_prototypes(
    database, app, file_timestamp
):
    """
    As with customer types, note that 655990 is duplicated as it's the chosen
    one among availability possible customer prototypes.
    """
    app.config["RESPONSES_PATH"] = "tests/sample_data/"
    services.PopulateDB(app).run()

    ctp_ids = (655990, 655988, 655989, 655990, 655991, 655992, 655993, 655994)
    for ctp_id in ctp_ids:
        ctp = models.CustomerPrototype.get(ctp_id)
    assert len(models.CustomerPrototype.query.all()) == len(ctp_ids) - 1
    assert ctp.note == "Todas las edades"
    assert ctp.total == 826
    assert ctp.total_including_tax == 1000
    assert ctp.display_name == "D\\u00eda extra"
    assert ctp.created_at == ctp.updated_at
    assert ctp.updated_at == file_timestamp


def test_populate_db_creates_customer_type_rates(
    database, app, file_timestamp
):
    """
    As with customer types, note that 2576873546 is duplicated as it's the
    chosen one among availability possible customer type rates.
    """
    app.config["RESPONSES_PATH"] = "tests/sample_data/"
    services.PopulateDB(app).run()

    ctr_ids = (
        2576873544, 2576873545, 2576873546, 2576873547, 2576873548, 2576873549,
        2576873550, 2576873546
    )
    for ctr_id in ctr_ids:
        ctp = models.CustomerTypeRate.get(ctr_id)
    assert len(models.CustomerTypeRate.query.all()) == len(ctr_ids) - 1
    assert ctp.capacity == 49
    assert ctp.minimum_party_size is None
    assert ctp.maximum_party_size is None
    assert ctp.total_including_tax == 1500
    assert ctp.total == 1240
    assert ctp.created_at == ctp.updated_at
    assert ctp.updated_at == file_timestamp


def test_populate_db_creates_checkin_status(database, app, file_timestamp):
    app.config["RESPONSES_PATH"] = "tests/sample_data/"
    services.PopulateDB(app).run()

    checkin_status = models.CheckinStatus.get(83803)
    assert checkin_status.checkin_status_type == "checked-in"
    assert checkin_status.name == "checked in"
    assert checkin_status.created_at == checkin_status.updated_at
    assert checkin_status.updated_at == file_timestamp


def test_populate_db_creates_customer(database, app, file_timestamp):
    app.config["RESPONSES_PATH"] = "tests/sample_data/"
    services.PopulateDB(app).run()

    customer = models.Customer.get(224262373)
    assert customer.checkin_url == "https://fhchk.co/faYT3"
    assert customer.checkin_status_id == 83803
    assert customer.customer_type_rate_id == 2576873546
    assert customer.booking_id == 75125154
    assert customer.created_at == customer.updated_at
    assert customer.updated_at == file_timestamp


def test_populate_db_creates_custom_field(database, app, file_timestamp):
    """There were 22 custom fields attempted to save."""
    app.config["RESPONSES_PATH"] = "tests/sample_data/"
    services.PopulateDB(app).run()

    custom_field_ids = (
        922177, 922178, 637022, 6160114, 6160113, 6160118, 6999966, 6160120,
        922180, 910098, 910095, 908052, )
    for cf_id in custom_field_ids:
        cf = models.CustomField.get(cf_id)
    assert cf.is_required is False
    assert cf.description == ""
    assert cf.title == "Pago con bono"
    assert cf.booking_notes_safe_html == ""
    assert cf.is_taxable
    assert cf.modifier_kind == "offset"
    assert cf.description_safe_html == ""
    assert cf.booking_notes == ""
    assert cf.offset == 100
    assert cf.percentage == 0
    assert cf.modifier_type == "none"
    assert cf.field_type == "yes-no"
    assert cf.is_always_per_customer is False
    assert cf.name == "Pago Bono"
    assert cf.created_at == cf.updated_at
    assert cf.updated_at == file_timestamp


def test_populate_db_creates_custom_field_instance(
    database, app, file_timestamp
):
    app.config["RESPONSES_PATH"] = "tests/sample_data/"
    services.PopulateDB(app).run()

    custom_field_instance_ids = (
        4050488, 4050489, 2379541, 4050530, 3963212, 4050531, 3950663, )
    for cfi_id in custom_field_instance_ids:
        cfi = models.CustomFieldInstance.get(cfi_id)
    saved_instances = len(models.CustomFieldInstance.query.all())
    assert saved_instances == len(custom_field_instance_ids)
    assert cfi.created_at == cfi.updated_at
    assert cfi.updated_at == file_timestamp


def test_populate_db_creates_custom_field_values(
    database, app, file_timestamp
):
    """In the sample all the custom field values are under bookings."""
    app.config["RESPONSES_PATH"] = "tests/sample_data/"
    services.PopulateDB(app).run()

    custom_field_values_ids = (
        347938962, 347938963, 347938964, 347938965, 347938966,)
    for cfv_id in custom_field_values_ids:
        cfv = models.CustomFieldValue.get(cfv_id)
    saved_instances = len(models.CustomFieldValue.query.all())
    assert saved_instances == len(custom_field_values_ids)
    assert cfv.id == 347938966
    assert cfv.name == "Pago Bono"
    assert cfv.value == ""
    assert cfv.display_value == "No"
    assert cfv.custom_field_id == 908052
    assert cfv.created_at == cfv.updated_at
    assert cfv.updated_at == file_timestamp


def test_check_for_new_keys_detects_booking_new_key():
    with open("tests/sample_data/1626842330.051856.json") as f:
        data = json.load(f)

    data["booking"]["new_key"] = "some_value"

    new_keys = services.CheckForNewKeys(data).run()
    assert new_keys == [("booking", "new_key")]


def test_check_for_new_keys_detects_customer_new_key():
    with open("tests/sample_data/1626842330.051856.json") as f:
        data = json.load(f)

    data["booking"]["customers"][0]["new_key"] = "some_value"

    new_keys = services.CheckForNewKeys(data).run()
    assert new_keys == [("customer", "new_key")]


def test_check_for_new_keys_detects_checkin_new_key():
    with open("tests/sample_data/1626842330.051856.json") as f:
        data = json.load(f)

    customer = data["booking"]["customers"][0]
    customer["checkin_status"] = {"new_key": "some_value"}

    new_keys = services.CheckForNewKeys(data).run()
    assert new_keys == [("checkin status", "new_key")]


def test_check_for_new_keys_detects_custom_field_values_new_keys():
    with open("tests/sample_data/1626842330.051856.json") as f:
        data = json.load(f)

    customer = data["booking"]["customers"][0]
    cfv = customer["custom_field_values"]
    cfv.append({
        "custom_field": {
            "new_custom_field_key": "some_value",
            "extended_options": [
                {"new_extended_option_key": "some_value", },
            ],
        },
        "new_key": "some_value",
    })

    new_keys = services.CheckForNewKeys(data).run()
    assert new_keys == [
        ("custom field values", "new_key"),
        ("custom field", "new_custom_field_key"),
        ("extended options", "new_extended_option_key"),
    ]


def test_check_for_new_keys_detects_customer_type_rates_new_keys():
    with open("tests/sample_data/1626842330.051856.json") as f:
        data = json.load(f)

    customer = data["booking"]["customers"][0]
    ctr = customer["customer_type_rate"]

    ctr["new_key"] = "some_value"

    new_keys = services.CheckForNewKeys(data).run()
    assert new_keys == [("customer type rate", "new_key")]


def test_check_for_new_keys_detects_customer_prototype_new_keys():
    with open("tests/sample_data/1626842330.051856.json") as f:
        data = json.load(f)

    ctr = data["booking"]["customers"][0]["customer_type_rate"]

    ctr["customer_prototype"]["new_key"] = "some_value"

    new_keys = services.CheckForNewKeys(data).run()
    assert new_keys == [("customer prototype", "new_key")]


def test_check_for_new_keys_detects_customer_type_new_keys():
    with open("tests/sample_data/1626842330.051856.json") as f:
        data = json.load(f)

    ctr = data["booking"]["customers"][0]["customer_type_rate"]

    ctr["customer_type"]["new_key"] = "some_value"

    new_keys = services.CheckForNewKeys(data).run()
    assert new_keys == [("customer type", "new_key")]


def test_check_for_new_keys_detects_availability_new_keys():
    with open("tests/sample_data/1626842330.051856.json") as f:
        data = json.load(f)

    data["booking"]["availability"]["new_key"] = "some_value"

    new_keys = services.CheckForNewKeys(data).run()
    assert new_keys == [("availability", "new_key")]


def test_check_for_new_keys_detects_items_new_keys():
    with open("tests/sample_data/1626842330.051856.json") as f:
        data = json.load(f)

    data["booking"]["availability"]["item"]["new_key"] = "some_value"

    new_keys = services.CheckForNewKeys(data).run()
    assert new_keys == [("item", "new_key")]


def test_check_for_new_keys_detects_customer_type_rates_new_keys_under_availability():
    with open("tests/sample_data/1626842330.051856.json") as f:
        data = json.load(f)

    ctr = data["booking"]["availability"]["customer_type_rates"][0]
    ctr["new_key"] = "some_value"

    new_keys = services.CheckForNewKeys(data).run()
    assert new_keys == [("customer type rate", "new_key")]


def test_check_for_new_keys_detects_customer_prototype_new_keys_under_availability():
    with open("tests/sample_data/1626842330.051856.json") as f:
        data = json.load(f)

    ctr = data["booking"]["availability"]["customer_type_rates"][0]
    ctr["customer_prototype"]["new_key"] = "some_value"

    new_keys = services.CheckForNewKeys(data).run()
    assert new_keys == [("customer prototype", "new_key")]


def test_check_for_new_keys_detects_customer_type_new_keys_under_availability():
    with open("tests/sample_data/1626842330.051856.json") as f:
        data = json.load(f)

    ctr = data["booking"]["availability"]["customer_type_rates"][0]
    ctr["customer_type"]["new_key"] = "some_value"

    new_keys = services.CheckForNewKeys(data).run()
    assert new_keys == [("customer type", "new_key")]


def test_check_for_new_keys_detects_custom_field_instances_new_keys_under_availability():
    with open("tests/sample_data/1626842330.051856.json") as f:
        data = json.load(f)

    ctr = data["booking"]["availability"]["customer_type_rates"][0]
    cfi = ctr["custom_field_instances"]
    cfi.append({
        "custom_field": {
            "new_custom_field_key": "some_value",
            "extended_options": [
                {"new_extended_option_key": "some_value", },
            ],
        },
        "new_key": "some_value",
    })

    new_keys = services.CheckForNewKeys(data).run()
    assert new_keys == [
        ("custom field instance", "new_key"),
        ("custom field", "new_custom_field_key"),
        ("extended options", "new_extended_option_key"),
    ]


def test_check_for_new_keys_detects_affiliate_company_new_keys():
    with open("tests/sample_data/1626842330.051856.json") as f:
        data = json.load(f)

    affiliate_company = data["booking"]["affiliate_company"]
    affiliate_company["new_key"] = "some_value"

    new_keys = services.CheckForNewKeys(data).run()
    assert new_keys == [("affiliate company", "new_key")]


def test_check_for_new_keys_detects_company_new_keys():
    with open("tests/sample_data/1626842330.051856.json") as f:
        data = json.load(f)

    affiliate = data["booking"]["company"]
    affiliate["new_key"] = "some_value"

    new_keys = services.CheckForNewKeys(data).run()
    assert new_keys == [("company", "new_key")]


def test_check_for_new_keys_detects_custom_field_values_new_keys_under_booking():
    with open("tests/sample_data/1626842330.051856.json") as f:
        data = json.load(f)

    cfv = data["booking"]["custom_field_values"]

    cfv.append({
        "custom_field": {
            "new_custom_field_key": "some_value",
            "extended_options": [
                {"new_extended_option_key": "some_value", },
            ],
        },
        "new_key": "some_value",
    })

    new_keys = services.CheckForNewKeys(data).run()
    assert new_keys == [
        ("custom field value", "new_key"),
        ("custom field", "new_custom_field_key"),
        ("extended options", "new_extended_option_key"),
    ]


def test_check_for_new_keys_detects_cancellation_policy_new_keys():
    with open("tests/sample_data/1626842330.051856.json") as f:
        data = json.load(f)

    data["booking"]["effective_cancellation_policy"]["new_key"] = "some_value"

    new_keys = services.CheckForNewKeys(data).run()
    assert new_keys == [("effective cancellation policy", "new_key")]


def test_check_for_new_keys_detects_contact_new_keys():
    with open("tests/sample_data/1626842330.051856.json") as f:
        data = json.load(f)

    data["booking"]["contact"]["new_key"] = "some_value"

    new_keys = services.CheckForNewKeys(data).run()
    assert new_keys == [("contact", "new_key")]
