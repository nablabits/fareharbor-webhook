"""
A convenience script used to check all the responses collected (~3200) under
marshmallow validation.
"""


import os
import json

from fh_webhook.schema import BookingSchema

path = app.config.get("RESPONSES_PATH")  # app is loaded with the shell
files = sorted([f for f in os.listdir(path) if f.endswith(".json")])

for n, f in enumerate(files):
    filename = os.path.join(path, f)
    with open(filename, "r") as response:
        data = json.load(response)
    try:
        valid = BookingSchema().load(data["booking"])
    except Exception as e:
        print(n, f)
        raise e

