from datetime import datetime

import attr

from . import models
from .models import db
from .exceptions import DoesNotExist


@attr.s
class CreateItem:
    name = attr.ib()

    def run(self):
        new_item = models.Item(
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            name=self.name
        )
        db.session.add(new_item)
        db.session.commit()
        return new_item


@attr.s
class UpdateItem:
    item_id = attr.ib(type=int)
    name = attr.ib()

    def run(self):
        item = models.Item.query.get(self.item_id)
        item.name = self.name
        item.updated_at = datetime.utcnow()
        db.session.commit()
        return item


@attr.s
class DeleteItem:
    item_id = attr.ib(type=int)

    def run(self):
        item = models.Item.query.get(self.item_id)
        db.session.delete(item)
        db.session.commit()


# Availability services


@attr.s
class CreateAvailability:
    capacity = attr.ib(type=int)
    minimum_party_size = attr.ib(type=int)
    maximum_party_size = attr.ib(type=int)
    start_at = attr.ib(type=datetime)
    end_at = attr.ib(type=datetime)
    item_id = attr.ib(type=int)

    def run(self):
        new_availability = models.Availability(
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            capacity=self.capacity,
            minimum_party_size=self.minimum_party_size,
            maximum_party_size=self.maximum_party_size,
            start_at=self.start_at,
            end_at=self.end_at,
            item_id=self.item_id
        )
        db.session.add(new_availability)
        db.session.commit()
        return new_availability


@attr.s
class UpdateAvailability:
    availability_id = attr.ib(type=int)
    capacity = attr.ib(type=int)
    minimum_party_size = attr.ib(type=int)
    maximum_party_size = attr.ib(type=int)
    start_at = attr.ib(type=datetime)
    end_at = attr.ib(type=datetime)
    item_id = attr.ib(type=int)

    def run(self):
        availability = models.Availability.query.get(self.availability_id)
        availability.updated_at = datetime.utcnow()
        availability.capacity = self.capacity
        availability.minimum_party_size = self.minimum_party_size
        availability.maximum_party_size = self.maximum_party_size
        availability.start_at = self.start_at
        availability.end_at = self.end_at
        availability.item_id = self.item_id

        db.session.add(availability)
        db.session.commit()
        return availability


@attr.s
class DeleteAvailability:
    availability_id = attr.ib(type=int)

    def run(self):
        availability = models.Availability.query.get(self.availability_id)
        db.session.delete(availability)
        db.session.commit()


# Booking services


@attr.s
class CreateBooking:
    voucher_number = attr.ib(type=str)
    display_id = attr.ib(type=str)
    note_safe_html = attr.ib(type=str)
    agent = attr.ib(type=str)
    confirmation_url = attr.ib(type=str)
    customer_count = attr.ib(type=int)
    affiliate_company = attr.ib(type=str)
    uuid = attr.ib(type=str)
    dashboard_url = attr.ib(type=str)
    note = attr.ib(type=str)
    pickup = attr.ib(type=str)
    status = attr.ib(type=str)

    # Foreign key fields
    availability_id = attr.ib(type=int)

    # price fields
    receipt_subtotals = attr.ib(type=int)
    receipt_taxes = attr.ib(type=int)
    receipt_total = attr.ib(type=int)
    amount_paid = attr.ib(type=int)
    invoice_price = attr.ib(type=int)

    # Price displays
    receipt_subtotal_display = attr.ib(type=str)
    receipt_taxes_display = attr.ib(type=str)
    receipt_total_display = attr.ib(type=str)
    amount_paid_display = attr.ib(type=str)
    invoice_price_display = attr.ib(type=str)

    desk = attr.ib(type=str)
    is_eligible_for_cancellation = attr.ib(type=bool)
    arrival = attr.ib(type=str)
    rebooked_to = attr.ib(type=str)
    rebooked_from = attr.ib(type=str)
    external_id = attr.ib(type=str)
    order = attr.ib(type=str)

    def run(self):
        new_booking = models.Booking(
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            voucher_number=self.voucher_number,
            display_id=self.display_id,
            note_safe_html=self.note_safe_html,
            agent=self.agent,
            confirmation_url=self.confirmation_url,
            customer_count=self.customer_count,
            affiliate_company=self.affiliate_company,
            uuid=self.uuid,
            dashboard_url=self.dashboard_url,
            note=self.note,
            pickup=self.pickup,
            status=self.status,
            availability_id=self.availability_id,
            receipt_subtotals=self.receipt_subtotals,
            receipt_taxes=self.receipt_taxes,
            receipt_total=self.receipt_total,
            amount_paid=self.amount_paid,
            invoice_price=self.invoice_price,
            receipt_subtotal_display=self.receipt_subtotal_display,
            receipt_taxes_display=self.receipt_taxes_display,
            receipt_total_display=self.receipt_total_display,
            amount_paid_display=self.amount_paid_display,
            invoice_price_display=self.invoice_price_display,
            desk=self.desk,
            is_eligible_for_cancellation=self.is_eligible_for_cancellation,
            arrival=self.arrival,
            rebooked_to=self.rebooked_to,
            rebooked_from=self.rebooked_from,
            external_id=self.external_id,
            order=self.order
        )
        db.session.add(new_booking)
        db.session.commit()
        return new_booking


@attr.s
class UpdateBooking:
    booking_id = attr.ib(type=int)
    voucher_number = attr.ib(type=str)
    display_id = attr.ib(type=str)
    note_safe_html = attr.ib(type=str)
    agent = attr.ib(type=str)
    confirmation_url = attr.ib(type=str)
    customer_count = attr.ib(type=int)
    affiliate_company = attr.ib(type=str)
    uuid = attr.ib(type=str)
    dashboard_url = attr.ib(type=str)
    note = attr.ib(type=str)
    pickup = attr.ib(type=str)
    status = attr.ib(type=str)
    availability_id = attr.ib(type=int)
    receipt_subtotals = attr.ib(type=int)
    receipt_taxes = attr.ib(type=int)
    receipt_total = attr.ib(type=int)
    amount_paid = attr.ib(type=int)
    invoice_price = attr.ib(type=int)
    receipt_subtotal_display = attr.ib(type=str)
    receipt_taxes_display = attr.ib(type=str)
    receipt_total_display = attr.ib(type=str)
    amount_paid_display = attr.ib(type=str)
    invoice_price_display = attr.ib(type=str)
    desk = attr.ib(type=str)
    is_eligible_for_cancellation = attr.ib(type=bool)
    arrival = attr.ib(type=str)
    rebooked_to = attr.ib(type=str)
    rebooked_from = attr.ib(type=str)
    external_id = attr.ib(type=str)
    order = attr.ib(type=str)

    def run(self):
        booking = models.Booking.get(self.booking_id)
        booking.updated_at = datetime.utcnow()
        booking.voucher_number = self.voucher_number
        booking.display_id = self.display_id
        booking.note_safe_html = self.note_safe_html
        booking.agent = self.agent
        booking.confirmation_url = self.confirmation_url
        booking.customer_count = self.customer_count
        booking.affiliate_company = self.affiliate_company
        booking.uuid = self.uuid
        booking.dashboard_url = self.dashboard_url
        booking.note = self.note
        booking.pickup = self.pickup
        booking.status = self.status
        booking.availability_id = self.availability_id
        booking.receipt_subtotals = self.receipt_subtotals
        booking.receipt_taxes = self.receipt_taxes
        booking.receipt_total = self.receipt_total
        booking.amount_paid = self.amount_paid
        booking.invoice_price = self.invoice_price
        booking.receipt_subtotal_display = self.receipt_subtotal_display
        booking.receipt_taxes_display = self.receipt_taxes_display
        booking.receipt_total_display = self.receipt_total_display
        booking.amount_paid_display = self.amount_paid_display
        booking.invoice_price_display = self.invoice_price_display
        booking.desk = self.desk
        booking.is_eligible_for_cancellation = self.is_eligible_for_cancellation
        booking.arrival = self.arrival
        booking.rebooked_to = self.rebooked_to
        booking.rebooked_from = self.rebooked_from
        booking.external_id = self.external_id
        booking.order = self.order
        db.session.add(booking)
        db.session.commit()
        return booking


@attr.s
class DeleteBooking:
    booking_id = attr.ib(type=int)

    def run(self):
        booking = models.Booking.get(self.booking_id)
        db.session.delete(booking)
        db.session.commit()

# Contact services


@attr.s
class CreateContact:
    name = attr.ib(type=str)
    email = attr.ib(type=str)
    phone_country = attr.ib(type=str)
    phone = attr.ib(type=str)
    normalized_phone = attr.ib(type=str)
    is_subscribed_for_email_updates = attr.ib(type=bool)
    booking_id = attr.ib(type=int)

    def run(self):
        opt_in = self.is_subscribed_for_email_updates
        new_contact = models.Contact(
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            name=self.name,
            email=self.email,
            phone_country=self.phone_country,
            phone=self.phone,
            normalized_phone=self.normalized_phone,
            is_subscribed_for_email_updates=opt_in,
            booking_id=self.booking_id
        )
        db.session.add(new_contact)
        db.session.commit()
        return new_contact


@attr.s
class UpdateContact:
    contact_id = attr.ib(type=int)
    name = attr.ib(type=str)
    email = attr.ib(type=str)
    phone_country = attr.ib(type=str)
    phone = attr.ib(type=str)
    normalized_phone = attr.ib(type=str)
    is_subscribed_for_email_updates = attr.ib(type=bool)

    def run(self):
        opt_in = self.is_subscribed_for_email_updates
        contact = models.Contact.get(self.contact_id)
        contact.updated_at = datetime.utcnow(),
        contact.name = self.name,
        contact.email = self.email,
        contact.phone_country = self.phone_country,
        contact.phone = self.phone,
        contact.normalized_phone = self.normalized_phone,
        contact.is_subscribed_for_email_updates = opt_in
        db.session.add(contact)
        db.session.commit()
        return contact


@attr.s
class DeleteContact:
    contact_id = attr.ib(type=int)

    def run(self):
        contact = models.Contact.get(self.contact_id)
        db.session.delete(contact)
        db.session.commit()


# company services


@attr.s
class CreateCompany:
    name = attr.ib(type=str)
    short_name = attr.ib(type=str)
    currency = attr.ib(type=str)
    booking_id = attr.ib(type=int)

    def run(self):
        new_company = models.Company(
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            name=self.name,
            short_name=self.short_name,
            currency=self.currency,
            booking_id=self.booking_id
        )
        db.session.add(new_company)
        db.session.commit()
        return new_company


@attr.s
class UpdateCompany:
    company_id = attr.ib(type=int)
    name = attr.ib(type=str)
    short_name = attr.ib(type=str)
    currency = attr.ib(type=str)
    # booking_id = attr.ib(type=int)
    # as companies are a 1:1 to bookings we can't update right away the booking_id. We
    # leave aside this action and we will implement it if neccessary

    def run(self):
        company = models.Company.get(self.company_id)
        company.updated_at = datetime.utcnow()
        company.name = self.name
        company.short_name = self.short_name
        company.currency = self.currency

        db.session.add(company)
        db.session.commit()
        return company


@attr.s
class DeleteCompany:
    company_id = attr.ib(type=int)

    def run(self):
        company = models.Company.get(self.company_id)
        db.session.delete(company)
        db.session.commit()


# Cancellation policy services

@attr.s
class CreateCancellationPolicy:
    cutoff = attr.ib(type=datetime)
    cancellation_type = attr.ib(type=str)
    booking_id = attr.ib(type=int)

    def run(self):
        new_cp = models.EffectiveCancellationPolicy(
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            cutoff=self.cutoff,
            cancellation_type=self.cancellation_type,
            booking_id=self.booking_id
        )
        db.session.add(new_cp)
        db.session.commit()
        return new_cp


@attr.s
class UpdateCancellationPolicy:
    cp_id = attr.ib(type=int)
    cutoff = attr.ib(type=datetime)
    cancellation_type = attr.ib(type=str)
    # booking_id = attr.ib(type=int)
    # as cancellations are a 1:1 to bookings we can't update right away the booking_id. We
    # leave aside this action and we will implement it if neccessary

    def run(self):
        cp = models.EffectiveCancellationPolicy.get(self.cp_id)
        cp.cutoff = self.cutoff
        cp.cancellation_type = self.cancellation_type

        db.session.add(cp)
        db.session.commit()
        return cp


@attr.s
class DeleteCancellationPolicy:
    cp_id = attr.ib(type=int)

    def run(self):
        cp = models.EffectiveCancellationPolicy.get(self.cp_id)
        db.session.delete(cp)
        db.session.commit()


# Custom Field services


@attr.s
class CreateCustomField:
    title = attr.ib(type=str)
    name = attr.ib(type=str)
    modifier_kind = attr.ib(type=str)
    modifier_type = attr.ib(type=str)
    field_type = attr.ib(type=str)
    offset = attr.ib(type=int)
    percentage = attr.ib(type=int)

    # text fields
    description = attr.ib(type=str)
    booking_notes = attr.ib(type=str)
    description_safe_html = attr.ib(type=str)
    booking_notes_safe_html = attr.ib(type=str)

    # bool fields
    is_required = attr.ib(type=bool)
    is_taxable = attr.ib(type=bool)
    is_always_per_customer = attr.ib(type=bool)

    extended_options = attr.ib(type=int, default=None)

    def run(self):
        new_custom_field = models.CustomField(
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            title=self.title,
            name=self.name,
            modifier_kind=self.modifier_kind,
            modifier_type=self.modifier_type,
            field_type=self.field_type,
            offset=self.offset,
            percentage=self.percentage,
            description=self.description,
            booking_notes=self.booking_notes,
            description_safe_html=self.description_safe_html,
            booking_notes_safe_html=self.booking_notes_safe_html,
            is_required=self.is_required,
            is_taxable=self.is_taxable,
            is_always_per_customer=self.is_always_per_customer,
            extended_options=self.extended_options
        )
        db.session.add(new_custom_field)
        db.session.commit()
        return new_custom_field


@attr.s
class UpdateCustomField:
    custom_field_id = attr.ib(type=int)
    title = attr.ib(type=str)
    name = attr.ib(type=str)
    modifier_kind = attr.ib(type=str)
    modifier_type = attr.ib(type=str)
    field_type = attr.ib(type=str)
    offset = attr.ib(type=int)
    percentage = attr.ib(type=int)

    # text fields
    description = attr.ib(type=str)
    booking_notes = attr.ib(type=str)
    description_safe_html = attr.ib(type=str)
    booking_notes_safe_html = attr.ib(type=str)

    # bool fields
    is_required = attr.ib(type=bool)
    is_taxable = attr.ib(type=bool)
    is_always_per_customer = attr.ib(type=bool)

    extended_options = attr.ib(type=int, default=None)

    def run(self):
        cf = models.CustomField.query.get(self.custom_field_id)
        cf.updated_at = datetime.utcnow()
        cf.title = self.title
        cf.name = self.name
        cf.modifier_kind = self.modifier_kind
        cf.modifier_type = self.modifier_type
        cf.field_type = self.field_type
        cf.offset = self.offset
        cf.percentage = self.percentage
        cf.description = self.description
        cf.booking_notes = self.booking_notes
        cf.description_safe_html = self.description_safe_html
        cf.booking_notes_safe_html = self.booking_notes_safe_html
        cf.is_required = self.is_required
        cf.is_taxable = self.is_taxable
        cf.is_always_per_customer = self.is_always_per_customer
        cf.extended_options = self.extended_options

        db.session.add(cf)
        db.session.commit()
        return cf


@attr.s
class DeleteCustomField:
    custom_field_id = attr.ib(type=int)

    def run(self):
        cf = models.CustomField.query.get(self.custom_field_id)
        db.session.delete(cf)
        db.session.commit()


# Customers' services


@attr.s
class CreateCustomerPrototype:
    total = attr.ib(type=int)
    total_including_tax = attr.ib(type=int)
    display_name = attr.ib(type=str)
    note = attr.ib(type=str)

    def run(self):
        new_customer_prototype = models.CustomerPrototype(
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            total=self.total,
            total_including_tax=self.total_including_tax,
            display_name=self.display_name,
            note=self.note
        )
        db.session.add(new_customer_prototype)
        db.session.commit()
        return new_customer_prototype


@attr.s
class UpdateCustomerPrototype:
    customer_prototype_id = attr.ib(type=int)
    total = attr.ib(type=int)
    total_including_tax = attr.ib(type=int)
    display_name = attr.ib(type=str)
    note = attr.ib(type=str)

    def run(self):
        customer_prototype = models.CustomerPrototype.query.get(
            self.customer_prototype_id)
        customer_prototype.updated_at = datetime.utcnow()
        customer_prototype.total = self.total
        customer_prototype.total_including_tax = self.total_including_tax
        customer_prototype.display_name = self.display_name
        customer_prototype.note = self.note

        db.session.commit()
        return customer_prototype


@attr.s
class DeleteCustomerPrototype:
    customer_prototype_id = attr.ib(type=int)

    def run(self):
        customer_prototype = models.CustomerPrototype.query.get(
            self.customer_prototype_id
        )
        db.session.delete(customer_prototype)
        db.session.commit()


@attr.s
class CreateCustomerType:
    note = attr.ib(type=str)
    singular = attr.ib(type=str)
    plural = attr.ib(type=str)

    def run(self):
        new_customer_type = models.CustomerType(
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            note=self.note,
            singular=self.singular,
            plural=self.plural
        )
        db.session.add(new_customer_type)
        db.session.commit()
        return new_customer_type


@attr.s
class UpdateCustomerType:
    customer_type_id = attr.ib(type=int)
    note = attr.ib(type=str)
    singular = attr.ib(type=str)
    plural = attr.ib(type=str)

    def run(self):
        customer_type = models.CustomerType.query.get(self.customer_type_id)
        customer_type.updated_at = datetime.utcnow()
        customer_type.note = self.note
        customer_type.singular = self.singular
        customer_type.plural = self.plural

        db.session.commit()
        return customer_type


@attr.s
class DeleteCustomerType:
    customer_type_id = attr.ib(type=int)

    def run(self):
        customer_type = models.CustomerType.query.get(self.customer_type_id)
        db.session.delete(customer_type)
        db.session.commit()

