"""
Backfill the new fields found on Aug 10th.

By Aug 10th some new fields were discovered on these models:
- Avalilability: headline
- Contact: language
- Booking: is_subscribed_for_sms_updates
So we need to back fill these values in the database.

To execute this script:
$> export FLASK_APP=run.py
$> flask shell < backfill_new_fields.py
Pray.
"""
import os
import json

from fh_webhook import models

path = app.config.get("RESPONSES_PATH")  # app is loaded with the shell
files = sorted([f for f in os.listdir(path)])

headlines = dict()  # availability_id: headline
languages = dict()  # booking_id: language
opt_in = dict()  # booking_id: is_subscribed_for_sms_updates

for n, f in enumerate(files):
    filename = os.path.join(path, f)
    with open(filename, "r") as response:
        data = json.load(response)
    b = data["booking"]
    av = b["availability"]
    c = b["contact"]
    if b.get("is_subscribed_for_sms_updates"):
        opt_in[b["pk"]] = b["is_subscribed_for_sms_updates"]
    if av.get("headline"):
        headlines[av["pk"]] = av["headline"]
    if c.get("language"):
        languages[b["pk"]] = c["language"]

# get the bookings
ids = [pk for pk in opt_in.keys()]
bookings = models.db.session.query(models.Booking).filter(
    models.Booking.id.in_(ids)
).all()

ids = [pk for pk in headlines.keys()]
availabilities = models.db.session.query(models.Availability).filter(
    models.Availability.id.in_(ids)
)

ids = [pk for pk in languages.keys()]
contacts = models.db.session.query(models.Contact).filter(
    models.Contact.id.in_(ids)
)

for booking in bookings:
    booking.is_subscribed_for_sms_updates = opt_in[booking.id]
for availability in availabilities:
    availability.headline = headlines[availability.id]
for contact in contacts:
    contact.language = languages[contact.id]

models.db.session.commit()

# Print some outcomes
print(f"{n} files processed")
print(f"{len(headlines)} headlines found")  # 235
print(f"{len(languages)} languages found")  # 544
print(f"{len(opt_in)} subscriptions found")  # 22
