"""
Update the db values for created_by with the data on FH.

As FH does not send the origin data on the webhook, once in a while we have to
populate it manually. To do so we download a csv with the content for the year
for booking_id & created_by fields.

The csv should look like this:
"Bookings",""
"Booking ID","Created By"
"#xxxxxxxx","John Doe"

The script is expecting the csv to be in ./scripts/data/

We want only to fill the bookings whose `created_by` is staff as the others
carry the value of the company.

To execute this script:
$> export FLASK_APP=run.py
$> flask shell < populate_created_by.py
Pray.
"""

import os
import csv
from collections import defaultdict

from fh_webhook.models import db, Booking

path = "scripts/data/created_by.csv"

if not os.path.isfile(path):
    raise ValueError("Ensure there's a file called created_by.csv in scripts/data dir")

# Prepare data
res = defaultdict(list)
with open(path) as f:
    reader = csv.DictReader(f)
    f.readline()  # usually FH downloads have an extra top line.
    for row in reader:
        try:
            b_id = row["Booking ID"]
            creator = row["Created By"]
        except KeyError as e:
            app.logger.exception(f"The key was not found {e}")
            exit()
        else:
            res[creator].append(b_id)

# Update db
for user, bookings in res.items():
    query = (
        db.session.query(Booking)
        .filter(Booking.created_by == "staff")
        .filter(Booking.display_id.in_(bookings))
    )
    query.update({"created_by": user}, synchronize_session="fetch")

db.session.commit()
