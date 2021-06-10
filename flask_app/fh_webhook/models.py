"""Define the models in the database."""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from .exceptions import DoesNotExist

metadata = MetaData()
db = SQLAlchemy(metadata=metadata)


class BaseMixin:
    """Provide common methods for models."""

    @classmethod
    def get(cls, id):
        """Try to get an instace or raise an error."""
        instance = cls.query.get(id)
        if instance:
            return instance
        else:
            raise DoesNotExist(cls.__table_name__)


class Booking(db.Model, BaseMixin):
    """Store the information about the booking."""

    __table_name__ = "booking"
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    voucher_number = db.Column(db.String(64))
    display_id = db.Column(db.String(64), nullable=False)
    note_safe_html = db.Column(db.Text)
    agent = db.Column(db.String(64))
    confirmation_url = db.Column(db.String(255))
    customer_count = db.Column(db.SmallInteger, nullable=False)
    affiliate_company = db.Column(db.String(64))
    uuid = db.Column(db.String(40), nullable=False, unique=True)
    dashboard_url = db.Column(db.String(264))
    note = db.Column(db.Text)
    pickup = db.Column(db.String(64))
    status = db.Column(db.String(64))

    # Foreign key fields
    availability_id = db.Column(
        db.Integer, db.ForeignKey("availability.id"), nullable=False)

    # price fields
    receipt_subtotals = db.Column(db.Integer)
    receipt_taxes = db.Column(db.Integer)
    receipt_total = db.Column(db.Integer)
    amount_paid = db.Column(db.Integer)
    invoice_price = db.Column(db.Integer)

    # Price displays
    receipt_subtotal_display = db.Column(db.String(64))
    receipt_taxes_display = db.Column(db.String(64))
    receipt_total_display = db.Column(db.String(64))
    amount_paid_display = db.Column(db.String(64))
    invoice_price_display = db.Column(db.String(64))

    desk = db.Column(db.String(64))
    is_eligible_for_cancellation = db.Column(db.Boolean)
    arrival = db.Column(db.String(64))
    rebooked_to = db.Column(db.String(64))
    rebooked_from = db.Column(db.String(64))
    external_id = db.Column(db.String(64))
    order = db.Column(db.String(64))


class Availability(db.Model):
    """Store availabilities.

    Each booking belongs to one and only availability
    """
    __table_name__ = "availability"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    capacity = db.Column(db.SmallInteger, nullable=False)
    minimum_party_size = db.Column(db.SmallInteger, nullable=False)
    maximum_party_size = db.Column(db.SmallInteger, nullable=False)
    start_at = db.Column(db.DateTime(timezone=True), nullable=False)
    end_at = db.Column(db.DateTime(timezone=True), nullable=False)

    # foreign key fields
    item_id = db.Column(
        db.Integer, db.ForeignKey("item.id"), nullable=False)


class Item(db.Model):
    """Items are the products we sell in the business."""
    __table_name__ = "item"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(200))


class Customer(db.Model):
    """Store the customer chosen by the booking.

    Acts as a M2M between customer type rate and bookings as a booking can have
    several customers chosen (3 Adults, 2 children) and the defined customer
    type rate can appear in different bookings as they are defined by the
    availability.
    """
    __table_name__ = "customer"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    checkin_url = db.Column(db.String(264))
    checking_status = db.Column(db.String(64))

    # Foreign Key fields
    customer_type_rate_id = db.Column(
        db.Integer, db.ForeignKey("customer_type_rate.id"), nullable=False
    )
    # M2M to booking
    booking_id = db.Column(
        db.Integer, db.ForeignKey("booking.id"), nullable=False
    )


class CustomerTypeRate(db.Model):
    """Store each customer type rate.

    Every availability can have several customer type rates that are based on
    customer prototypes (the ones defined in the settings).
    It acts as a M2M between the availability and the customer prototype.
    """
    __table_name__ = "customer_type_rate"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    capacity = db.Column(db.SmallInteger, nullable=False)
    minimum_party_size = db.Column(db.SmallInteger, nullable=False)
    maximum_party_size = db.Column(db.SmallInteger, nullable=False)

    # Foreign key fields
    booking_id = db.Column(db.Integer, db.ForeignKey("booking.id"), nullable=False)
    availability_id = db.Column(db.Integer, db.ForeignKey("availability.id"), nullable=False)
    customer_prototype_id = db.Column(
        db.Integer, db.ForeignKey("customer_prototype.id"), nullable=False
    )
    customer_type_id = db.Column(
        db.Integer, db.ForeignKey("customer_type.id"), nullable=False
    )


class CustomerPrototype(db.Model):
    """Store the customer prototypes.

    We define general customer types (like Adult, child, 2hours) that
    afterwards can be added to the availabilities.
    """
    __table_name__ = "customer_prototype"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    total = db.Column(db.Integer)
    total_including_tax = db.Column(db.Integer)
    display_name = db.Column(db.String(64), nullable=False)
    note = db.Column(db.Text)


class CustomerType(db.Model):
    """Store the customer type.

    This model is an extension of the customer Prototype storing the notes and
    the names in singular plural.
    """
    __table_name__ = "customer_type"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    note = db.Column(db.Text)
    singular = db.Column(db.String(64), nullable=False)
    plural = db.Column(db.String(64), nullable=False)


class CustomFieldInstances(db.Model):
    """Make the M2M between Availability and Custom field models.

    An availability can have several custom fields defined and the same custom
    field can appear in different availabilities.
    """
    __table_name__ = "custom_field_instance"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    custom_field_id = db.Column(
        db.Integer, db.ForeignKey("custom_field.id"))
    availability_id = db.Column(
        db.Integer, db.ForeignKey("availability.id"))


class CustomFieldValues(db.Model):
    """Store the chosen values for each booking/customer.

    Acts as M2M among bookings-custom_fields and customer-custom_fields.
    """
    __table_name__ = "custom_field_values"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    value = db.Column(db.String(2048))
    display_value = db.Column(db.String(2048))

    # Foreign key fields
    custom_field_id = db.Column(
        db.Integer, db.ForeignKey("custom_field.id")
    )
    # M2M to booking and customer
    booking_id = db.Column(
        db.Integer, db.ForeignKey("booking.id"), nullable=False
    )
    customer_id = db.Column(
        db.Integer, db.ForeignKey("customer.id"), nullable=False
    )


class CustomField(db.Model):
    """Store the types of custom fields available."""
    __table_name__ = "custom_field"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    modifier_kind = db.Column(db.String(64), nullable=False)
    modifier_type = db.Column(db.String(64), nullable=False)
    field_type = db.Column(db.String(64), nullable=False)
    offset = db.Column(db.Integer)
    percentage = db.Column(db.Integer)

    # text fields
    description = db.Column(db.Text)
    booking_notes = db.Column(db.Text)
    description_safe_html = db.Column(db.Text)
    booking_notes_safe_html = db.Column(db.Text)

    # bool fields
    is_required = db.Column(db.Boolean, nullable=False)
    is_taxable = db.Column(db.Boolean, nullable=False)
    is_always_per_customer = db.Column(db.Boolean, nullable=False)

    extended_options = db.Column(
        db.Integer, db.ForeignKey("custom_field.id"), nullable=True)


class Contact(db.Model):
    """Store the contact details for the booking.

    Is a 1:1 on bookings.
    """
    __table_name__ = "contact"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256))
    phone_country = db.Column(db.String(10))
    phone = db.Column(db.String(30))
    normalized_phone = db.Column(db.String(30))
    is_subscribed_for_email_updates = db.Column(db.Boolean, nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey("booking.id"), unique=True, nullable=False)


class Company(db.Model):
    """Store the company details for the booking.

    Is a 1:1 on bookings.
    """
    __table_name__ = "company"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(256), nullable=False)
    short_name = db.Column(db.String(30), nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey("booking.id"), unique=True, nullable=False)


class EffectiveCancellationPolicy(db.Model):
    """Store the cancellation policy for the booking.

    Is a 1:1 on bookings.
    """
    __table_name__ = "effective_cancellation_policy"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    cutoff = db.Column(db.DateTime(timezone=True), nullable=False)
    cancellation_type = db.Column(db.String(64), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey("booking.id"), unique=True, nullable=False)
