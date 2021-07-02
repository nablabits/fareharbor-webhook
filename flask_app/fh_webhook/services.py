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

    def _save_availability(self, item_id):
        """Save the availability contained in the data."""
        av_data = self.data["booking"]["availability"]
        av = models.Availability.get_object_or_none(av_data["pk"])
        if av:
            service = model_services.UpdateAvailability
        else:
            service = model_services.CreateAvailability

        return service(
            availability_id=av_data["pk"],
            capacity=av_data["capacity"],
            minimum_party_size=av_data["minimum_party_size"],
            maximum_party_size=av_data["maximum_party_size"],
            start_at=av_data["start_at"],
            end_at=av_data["end_at"],
            item_id=item_id
        ).run()

    def _save_booking(self, av_id):
        """Save the booking information contained in the data."""
        b_data = self.data["booking"]
        booking = models.Booking.get_object_or_none(b_data["pk"])
        if booking:
            service = model_services.UpdateBooking
        else:
            service = model_services.CreateBooking
        return service(
            booking_id=b_data["pk"],
            voucher_number=b_data["voucher_number"],
            display_id=b_data["display_id"],
            note_safe_html=b_data["note_safe_html"],
            agent=b_data["agent"],
            confirmation_url=b_data["confirmation_url"],
            customer_count=b_data["customer_count"],
            affiliate_company=b_data["affiliate_company"],
            uuid=b_data["uuid"],
            dashboard_url=b_data["dashboard_url"],
            note=b_data["note"],
            pickup=b_data["pickup"],
            status=b_data["status"],
            availability_id=av_id,
            receipt_subtotal=b_data["receipt_subtotal"],
            receipt_taxes=b_data["receipt_taxes"],
            receipt_total=b_data["receipt_total"],
            amount_paid=b_data["amount_paid"],
            invoice_price=b_data["invoice_price"],
            receipt_subtotal_display=b_data["receipt_subtotal_display"],
            receipt_taxes_display=b_data["receipt_taxes_display"],
            receipt_total_display=b_data["receipt_total_display"],
            amount_paid_display=b_data["amount_paid_display"],
            invoice_price_display=b_data["invoice_price_display"],
            desk=b_data["desk"],
            is_eligible_for_cancellation=b_data["is_eligible_for_cancellation"],
            arrival=b_data["arrival"],
            rebooked_to=b_data["rebooked_to"],
            rebooked_from=b_data["rebooked_from"],
            external_id=b_data["external_id"],
            order=b_data["order"],
        ).run()

    def _save_contact(self, booking_id):
        """
        Save the contact information contained in the data.

        Contacts have no id so we will use the booking_id as is a 1:1
        relationship.
        """
        c_data = self.data["booking"]["contact"]
        contact = models.Contact.get_object_or_none(booking_id)
        if contact:
            service = model_services.UpdateContact
        else:
            service = model_services.CreateContact

        opt_in = c_data["is_subscribed_for_email_updates"]
        return service(
            id=booking_id,
            name=c_data["name"],
            email=c_data["email"],
            phone_country=c_data["phone_country"],
            phone=c_data["phone"],
            normalized_phone=c_data["normalized_phone"],
            is_subscribed_for_email_updates=opt_in,
        ).run()

    def run(self):
        item = self._save_item()
        av = self._save_availability(item.id)
        booking = self._save_booking(av.id)
        self._save_contact(booking.id)
