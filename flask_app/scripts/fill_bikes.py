"""
Update the db values for bikes using a csv

The data can be downlowaded from query 91 on redash and it should look like this:

uuid,display_name
c10ec10ec10ec10ec10ec10ec10ec10e,bike_memorable_name

The script is expecting the csv to be in ./scripts/data/

To execute this script:
$> export FLASK_APP=run.py
$> flask shell < scripts/fill_bikes.py
Pray.
"""

import csv
import os
from datetime import datetime

from fh_webhook.models import Bike, db

path = "scripts/data/bikes_qrs.csv"

if not os.path.isfile(path):
    raise ValueError("Ensure there's a file called created_by.csv in scripts/data dir")

# Prepare data
with open(path) as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            uuid = row["uuid"]
            readable_name = row["display_name"]
        except KeyError as e:
            app.logger.exception(f"The key was not found {e}")
            exit()
        now = datetime.utcnow()
        new_bike = Bike(
            uuid=uuid, readable_name=readable_name, created_at=now, updated_at=now
        )
        db.session.add(new_bike)
db.session.commit()
