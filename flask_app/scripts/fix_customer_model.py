"""
Fix the customer_type_rate relationship with customer model. Because of the bug
found on 2021-09-30, we should fix the customer type rates with the data we
find in the stored responses.

## To execute this script:
$> export FLASK_APP=run.py
$> flask shell < fix_customer_model.py
Pray.
"""
import os
import json

from fh_webhook import models


# Create a dict with customer_id: customer_type_rate_id, this way, in case
# there's already a customer pk, the ctr it points to will be updated.
update = dict()

# load the files
path = app.config.get("RESPONSES_PATH")  # app is loaded with the shell
files = sorted([f for f in os.listdir(path) if f.endswith(".json")])

# Fill the dict.
for n, f in enumerate(files):
    filename = os.path.join(path, f)
    with open(filename, "r") as response:
        data = json.load(response)
    try:
        customers = data["booking"]["customers"]
    except KeyError:
        app.logger.info(
            f"Skipping {filename} as it does not contain valid data"
        )
    for c in customers:
        update[c["pk"]] = c["customer_type_rate"]["pk"]

app.logger.info(f"Collected {len(update)} customers so far, now updating.")

# Select the affected customers
customers = models.db.session.query(models.Customer).filter(
    models.Customer.id.in_(update.keys())
)

# Update the values
for customer in customers:
    customer.customer_type_rate_id = update[customer.id]

# Finish the transaction
models.db.session.commit()
