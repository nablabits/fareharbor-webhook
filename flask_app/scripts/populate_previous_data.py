"""
TL;DR: upload legacy data to the webhook database.

We had a couple of data sources for all our bookings so far, one containg the numbers collected
throughout the years through excel spreadsheets, odoo and fareharbor (before the webhook started
working), and the second with the data collected through the webhook.

In order to run queries over the whole dataset, we need to unify it, so we have been cleaning all
that legacy data to fit in the models provided by the webhook.

This is the last step that uploads that cleaned data to fareharbor webhook db.

This script is expecting two csvs to be in ./scripts/data/
    - availabilities_final_data.csv
    - bookings_final_data.csv

To execute this script:
$> source .env
$> export FLASK_APP=run.py
$> flask shell < populate_previous_data.py
Pray.
"""

import csv
import json
import os
import re
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from fh_webhook.models import Booking, Availability, db, Contact, Item

# get some ids from env
THREE_HOUR_ARTICLES = [s_id for s_id in os.getenv("THREE_HOUR_ARTICLES")]
THIRTY_MIN_ARTICLES = [s_id for s_id in os.getenv("THIRTY_MIN_ARTICLES")]
AFFILIATE_MAP = json.loads(os.get_env("AFFILIATE_MAP", "{}"))


# Prepare data


def get_timestamp(row):
    """Create a datetime object out of two strings that contain date and time."""
    return (datetime.fromisoformat(f"{row['create_date']} {row['create_time']}+00:00"),)


def get_int_prices(raw_amount):
    """Create an int price (stripe style) out of a string containig a variable float."""
    amount = re.findall(r"^\d+\.\d{1,2}", raw_amount)[0]
    if len(amount.split(".")[1]) < 2:
        amount += "0"
    normalised_amount = Decimal(amount) * 100
    return int(normalised_amount)


def create_missing_item():
    """Create a missing item in the target db."""
    item_name = os.getenv("MISSING_ITEM")
    item_id = os.getenv("MISSING_ITEM_ID")
    if not Item.get_object_or_none(item_id):
        print(f"Creating {item_name}")
        ts = datetime.fromisoformat("2020-05-20 16:31:00+00:00")
        it = Item(created_at=ts, updated_at=ts, id=item_id, name=item_name)
        db.session.add(it)
        db.session.commit()
        return
    print(f"{item_name} found.")


def update_availability(row, ts):
    start_at = datetime.fromisoformat(f"{row['start_date']} {row['start_hour']}+00:00")
    article = row["article_id"]
    if article in THIRTY_MIN_ARTICLES:
        end_at = start_at + timedelta(seconds=1800)  # 30'
    elif article in THREE_HOUR_ARTICLES:
        end_at = start_at + timedelta(seconds=10800)  # 3h
    else:
        end_at = start_at + timedelta(seconds=86400)  # 24h
    return Availability(
        created_at=ts,
        updated_at=ts,
        id=row["av_id"],
        capacity=50,
        minimum_party_size=2,
        maximum_party_size=10,
        start_at=start_at,
        end_at=end_at,
        headline=row["public_header"],
        item_id=int(row["article_id"].replace("#", "")),
    )


def update_booking(row, ts):
    """Create a booking out of the data provided in row."""
    pk = int(row["id"])
    status = "booked"
    if row["cancelled"] == "Cancelled":
        status = "cancelled"
    return Booking(
        created_at=ts,
        updated_at=ts,
        id=pk,
        voucher_number=row["voucher"],
        display_id=f"#{pk}",
        customer_count=row["pax"],
        uuid=uuid.uuid4().hex,
        note=row["notes"],
        status=status,
        receipt_subtotal=get_int_prices(row["subtotal"]),
        receipt_taxes=get_int_prices(row["tax_total"]),
        receipt_total=get_int_prices(row["total"]),
        invoice_price=get_int_prices(row["invoice_total"]),
        is_subscribed_for_sms_updates=row["opt_in_txt"] == "Subscribed",
        availability_id=row["av_id"],
        company_id=1,
        affiliate_company_id=AFFILIATE_MAP.get(row["affiliate"]),
    )


def update_contact(row, ts):
    pk = int(row["id"])
    return Contact(
        created_at=ts,
        updated_at=ts,
        id=pk,
        name=row["contact"] or "",
        email=row["email"],
        phone_country=row["language"],
        phone=row["phone"],
        normalized_phone=row["phone"],
        is_subscribed_for_email_updates=row["opt_in_email"] == "Subscribed",
    )


# Update all elements.
av_path = "scripts/data/availabilities_final_data.csv"
b_path = "scripts/data/bookings_final_data.csv"

create_missing_item()


with open(av_path) as f:
    reader = csv.DictReader(f)
    for row in reader:
        ts = get_timestamp(row)
        av = update_availability(row=row, ts=ts)
        db.session.add_all(av)
    db.session.commit()


with open(b_path) as f:
    reader = csv.DictReader(f)
    for row in reader:
        if (
            row["id"] == "65266356"
        ):  # this was rebooked to march and was picked by the webhook.
            print("Skipping 65266356")
            continue
        ts = get_timestamp(row)
        b = update_booking(row=row, ts=ts)
        db.session.add_all(b)
    db.session.commit()

with open(b_path) as f:
    reader = csv.DictReader(f)
    for row in reader:
        if (
            row["id"] == "65266356"
        ):  # this was rebooked to march and was picked by the webhook.
            print("Skipping 65266356")
            continue
        ts = get_timestamp(row)
        c = update_contact(row=row, ts=ts)
        db.session.add_all(c)
    db.session.commit()
