import json
import os
from . import models, model_services

import attr


class PopulateDB:
    """
    Populate the database using json files.

    For the last months we were collecting FH responses in JSON files, this
    service populates the database with such responses.
    """

    def __init__(self, app):
        """
        Class constructor.

        We need the app instance to get the path where the files are stored.
        """
        self.path = app.config.get("RESPONSES_PATH")

    def run(self):
        n = 0
        for f in os.listdir(self.path):
            if f.endswith(".json"):
                filename = os.path.join(self.path, f)
                with open(filename, "r") as response:
                    data = json.load(response)
                    ProcessJSONResponse(data).run()
            else:
                print(f"Non json file found ({f}) in the dir, skipping...")
        print(f"located {n} JSON files")


@attr.s
class ProcessJSONResponse:
    """
    The main service that process the JSON responses sent by FareHarbor.

    The constructor argument should be a python object created
    out of the json response in the webhook endpoint or the stored data.
    """

    data = attr.ib(type=dict)

    def _save_item(self):
        """Save the item contained in the data."""
        item_data = self.data["booking"]["availability"]["item"]
        item = models.Item.get_object_or_none(item_data["pk"])
        if item:
            service = model_services.UpdateItem
        else:
            service = model_services.CreateItem
        return service(item_id=item_data["pk"], name=item_data["name"]).run()

    def run(self):
        item = self._save_item()
