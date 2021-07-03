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

    def _save_company(self, booking_id):
        """
        Save company information contained in the data.
        """
        c_data = self.data["booking"]["company"]
        company = models.Company.get_object_or_none(booking_id)
        if company:
            service = model_services.UpdateCompany
        else:
            service = model_services.CreateCompany

        return service(
            company_id=booking_id,
            name=c_data["name"],
            short_name=c_data["shortname"],
            currency=c_data["currency"]
        ).run()

    def _save_cancellation_policy(self, booking_id):
        """
        Save cancellation policy information contained in the data.
        """
        c_data = self.data["booking"]["effective_cancellation_policy"]
        cp = models.EffectiveCancellationPolicy.get_object_or_none(
            booking_id)
        if cp:
            service = model_services.UpdateCancellationPolicy
        else:
            service = model_services.CreateCancellationPolicy

        return service(
            cp_id=booking_id,
            cutoff=c_data["cutoff"],
            cancellation_type=c_data["type"]
        ).run()

    def _save_customer_type(self, ct_data):
        """
        Save the customer type information contained in the data.

        In the json we can find customer types under bookings__customers and
        under booking__availability__customer_type_rates arrays so we should
        iterate through to get all of them.
        """
        cp = models.CustomerType.get_object_or_none(ct_data["pk"])
        if cp:
            service = model_services.UpdateCustomerType
        else:
            service = model_services.CreateCustomerType

        return service(
            customer_type_id=ct_data["pk"],
            note=ct_data["note"],
            singular=ct_data["singular"],
            plural=ct_data["plural"]
        ).run()

    def _save_customer_prototype(self, ct_data):
        """
        Save the customer prototype information contained in the data.

        In the json we can find customer prototypes in a similar way to that of
        customer types: under bookings__customers and under
        booking__availability__customer_type_rates
        """
        cpt = models.CustomerPrototype.get_object_or_none(ct_data["pk"])
        if cpt:
            service = model_services.UpdateCustomerPrototype
        else:
            service = model_services.CreateCustomerPrototype

        return service(
            customer_prototype_id=ct_data["pk"],
            note=ct_data["note"],
            total=ct_data["total"],
            total_including_tax=ct_data["total_including_tax"],
            display_name=ct_data["display_name"]
        ).run()

    def _save_customer_type_rate(self, ctr_data, ct, cpt, av):
        """
        Save the customer prototype information contained in the data.

        In the json we can find customer prototypes in a similar way to that of
        customer types: under bookings__customers and under
        booking__availability__customer_type_rates
        """
        ctr = models.CustomerTypeRate.get_object_or_none(ctr_data["pk"])
        if ctr:
            service = model_services.UpdateCustomerTypeRate
        else:
            service = model_services.CreateCustomerTypeRate

        return service(
            ctr_id=ctr_data["pk"],
            capacity=ctr_data["capacity"],
            minimum_party_size=ctr_data["minimum_party_size"],
            maximum_party_size=ctr_data["maximum_party_size"],
            total=ctr_data["total"],
            total_including_tax=ctr_data["total_including_tax"],
            availability_id=av.id,
            customer_prototype_id=cpt.id,
            customer_type_id=ct.id,
        ).run()

    def _save_customer(self, c_data, ctr_id, booking_id):
        """
        Save the customer information contained in the data.
        """
        ctr = models.Customer.get_object_or_none(c_data["pk"])
        if ctr:
            service = model_services.UpdateCustomer
        else:
            service = model_services.CreateCustomer

        return service(
            customer_id=c_data["pk"],
            checkin_url=c_data["checkin_url"],
            checkin_status=c_data["checkin_status"],
            customer_type_rate_id=ctr_id,
            booking_id=booking_id,
        ).run()

    def run(self):
        item = self._save_item()
        av = self._save_availability(item.id)
        b = self._save_booking(av.id)
        self._save_contact(b.id)
        self._save_company(b.id)
        self._save_cancellation_policy(b.id)

        bookings = self.data["booking"]
        customers = bookings["customers"]
        customer_type_rates = bookings["availability"]["customer_type_rates"]
        for ctr_data in customer_type_rates:
            ct_data = ctr_data["customer_type"]
            cpt_data = ctr_data["customer_prototype"]
            ct = self._save_customer_type(ct_data)
            cpt = self._save_customer_prototype(cpt_data)
            self._save_customer_type_rate(ctr_data, ct, cpt, av)

        for c_data in customers:
            ct_data = c_data["customer_type_rate"]["customer_type"]
            cpt_data = c_data["customer_type_rate"]["customer_prototype"]
            ct = self._save_customer_type(ct_data)
            cpt = self._save_customer_prototype(cpt_data)
            ctr = self._save_customer_type_rate(
                c_data["customer_type_rate"], ct, cpt, av)
            self._save_customer(c_data, ctr.id, b.id)

