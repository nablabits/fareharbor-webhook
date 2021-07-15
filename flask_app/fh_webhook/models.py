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
        """
        Try to get an instace or raise an error.

        Useful when we try to update an object that does not exist.
        """
        instance = cls.query.get(id)
        if instance:
            return instance
        else:
            raise DoesNotExist(cls.__table_name__)

    @classmethod
    def get_object_or_none(cls, id):
        """
        Get the object or none.

        This method is a wrapper of query.get() that is less readable.
        """
        return cls.query.get(id)


class Booking(db.Model, BaseMixin):
    """Store the information about the booking."""

    __table_name__ = "booking"
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    id = db.Column(db.BigInteger, primary_key=True)
    voucher_number = db.Column(db.String(64))
    display_id = db.Column(db.String(64), nullable=False)
    note_safe_html = db.Column(db.Text)
    agent = db.Column(db.String(64))
    confirmation_url = db.Column(db.String(255))
    customer_count = db.Column(db.SmallInteger, nullable=False)
    uuid = db.Column(db.String(40), nullable=False, unique=True)
    dashboard_url = db.Column(db.String(264))
    note = db.Column(db.Text)
    pickup = db.Column(db.String(64))
    status = db.Column(db.String(64))

    # Foreign key fields
    availability_id = db.Column(
        db.BigInteger, db.ForeignKey("availability.id"), nullable=False
    )
    company_id = db.Column(
        db.BigInteger, db.ForeignKey("company.id"), nullable=False
    )
    affiliate_company_id = db.Column(
        db.BigInteger, db.ForeignKey("company.id")
    )

    # price fields
    receipt_subtotal = db.Column(db.Integer)
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


class Availability(db.Model, BaseMixin):
    """Store availabilities.

    Each booking belongs to one and only availability
    """

    __table_name__ = "availability"
    id = db.Column(db.BigInteger, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    capacity = db.Column(db.SmallInteger, nullable=False)
    minimum_party_size = db.Column(db.SmallInteger)
    maximum_party_size = db.Column(db.SmallInteger)
    start_at = db.Column(db.DateTime(timezone=True), nullable=False)
    end_at = db.Column(db.DateTime(timezone=True), nullable=False)

    # foreign key fields
    item_id = db.Column(db.BigInteger, db.ForeignKey("item.id"), nullable=False)


class Item(db.Model, BaseMixin):
    """Items are the products we sell in the business."""

    __table_name__ = "item"
    id = db.Column(db.BigInteger, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(200))


class CheckinStatus(db.Model, BaseMixin):
    __table_name__ = "checkin_status"
    id = db.Column(db.BigInteger, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    checkin_status_type = db.Column(db.String(64))
    name = db.Column(db.String(64))


class Customer(db.Model, BaseMixin):
    """Store the customer chosen by the booking.

    Acts as a M2M between customer type rate and bookings as a booking can have
    several customers chosen (3 Adults, 2 children) and the defined customer
    type rate can appear in different bookings as they are defined by the
    availability.
    """

    __table_name__ = "customer"
    id = db.Column(db.BigInteger, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    checkin_url = db.Column(db.String(264))

    # Foreign Key fields
    customer_type_rate_id = db.Column(
        db.BigInteger, db.ForeignKey("customer_type_rate.id"), nullable=False
    )
    checkin_status_id = db.Column(
        db.BigInteger, db.ForeignKey("checkin_status.id"))
    # M2M to booking
    booking_id = db.Column(
        db.BigInteger, db.ForeignKey("booking.id"), nullable=False)


class CustomerTypeRate(db.Model, BaseMixin):
    """Store each customer type rate.

    Every availability can have several customer type rates that are based on
    customer prototypes (the ones defined in the settings).
    It acts as a M2M between the availability and the customer prototype.
    """

    __table_name__ = "customer_type_rate"
    id = db.Column(db.BigInteger, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    capacity = db.Column(db.SmallInteger)
    minimum_party_size = db.Column(db.SmallInteger)
    maximum_party_size = db.Column(db.SmallInteger)
    total = db.Column(db.Integer)
    total_including_tax = db.Column(db.Integer)

    # Foreign key fields
    availability_id = db.Column(
        db.BigInteger, db.ForeignKey("availability.id"), nullable=False
    )
    customer_prototype_id = db.Column(
        db.BigInteger, db.ForeignKey("customer_prototype.id"), nullable=False
    )
    customer_type_id = db.Column(
        db.BigInteger, db.ForeignKey("customer_type.id"), nullable=False
    )


class CustomerPrototype(db.Model, BaseMixin):
    """Store the customer prototypes.

    We define general customer types (like Adult, child, 2hours) that
    afterwards can be added to the availabilities.
    """

    __table_name__ = "customer_prototype"
    id = db.Column(db.BigInteger, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    total = db.Column(db.Integer)
    total_including_tax = db.Column(db.Integer)
    display_name = db.Column(db.String(64), nullable=False)
    note = db.Column(db.Text)


class CustomerType(db.Model, BaseMixin):
    """Store the customer type.

    This model is an extension of the customer Prototype storing the notes and
    the names in singular plural.
    """

    __table_name__ = "customer_type"
    id = db.Column(db.BigInteger, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    note = db.Column(db.Text)
    singular = db.Column(db.String(64), nullable=False)
    plural = db.Column(db.String(64), nullable=False)


class CustomFieldInstance(db.Model, BaseMixin):
    """Make the M2M between Availability and Custom field models.

    An availability can have several custom fields defined and the same custom
    field can appear in different availabilities. Likewise, each type rate can
    have several custom field and the same custom field can appear in different
    customer type rates. It should always point to a custom field object but
    can either point to an availability or to a customer type rate.
    """

    __table_name__ = "custom_field_instance"
    id = db.Column(db.BigInteger, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    custom_field_id = db.Column(
        db.BigInteger, db.ForeignKey("custom_field.id"), nullable=False
    )
    availability_id = db.Column(
        db.BigInteger, db.ForeignKey("availability.id"))
    customer_type_rate_id = db.Column(
        db.BigInteger, db.ForeignKey("customer_type_rate.id")
    )

    def clean(self):
        """
        Ensure either availability or customer type rate have value but not
        both at the same time.
        """
        if self.availability_id is None and self.customer_type_rate_id is None:
            raise ValueError(
                "Custom field instance needs either availability or " +
                "customer type rate"
            )

        if self.availability_id and self.customer_type_rate_id:
            raise ValueError(
                "Availability and customer type rate can't have value at the" +
                " same time."
            )


class CustomFieldValue(db.Model, BaseMixin):
    """Store the chosen values for each booking/customer.

    Acts as M2M among bookings-custom_fields and customer-custom_fields.
    """

    __table_name__ = "custom_field_values"
    id = db.Column(db.BigInteger, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    value = db.Column(db.String(2048))
    display_value = db.Column(db.String(2048))

    # Foreign key fields
    custom_field_id = db.Column(
        db.BigInteger, db.ForeignKey("custom_field.id"))
    # M2M to booking and customer
    booking_id = db.Column(db.BigInteger, db.ForeignKey("booking.id"))
    customer_id = db.Column(db.BigInteger, db.ForeignKey("customer.id"))

    def clean(self):
        """
        Ensure either booking or customer have value but not both at the same
        time.
        """
        if self.booking_id is None and self.customer_id is None:
            raise ValueError(
                "Custom field value needs either booking or customer instances"
            )

        if self.booking_id and self.customer_id:
            raise ValueError(
                "Booking and customer can't have value at the same time."
            )


class CustomField(db.Model, BaseMixin):
    """Store the types of custom fields available."""

    __table_name__ = "custom_field"
    id = db.Column(db.BigInteger, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.String(64))
    name = db.Column(db.String(64), nullable=False)
    modifier_kind = db.Column(db.String(64), nullable=False)
    modifier_type = db.Column(db.String(64), nullable=False)
    field_type = db.Column(db.String(64))
    offset = db.Column(db.Integer)
    percentage = db.Column(db.Integer)

    # text fields
    description = db.Column(db.Text)
    booking_notes = db.Column(db.Text)
    description_safe_html = db.Column(db.Text)
    booking_notes_safe_html = db.Column(db.Text)

    # bool fields
    is_required = db.Column(db.Boolean)
    is_taxable = db.Column(db.Boolean)
    is_always_per_customer = db.Column(db.Boolean)

    extended_options = db.Column(
        db.BigInteger, db.ForeignKey("custom_field.id"), nullable=True
    )


class Contact(db.Model, BaseMixin):
    """Store the contact details for the booking.

    Is a 1:1 on bookings.
    """

    __table_name__ = "contact"
    id = db.Column(db.BigInteger, db.ForeignKey("booking.id"), primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256))
    phone_country = db.Column(db.String(10))
    phone = db.Column(db.String(30))
    normalized_phone = db.Column(db.String(30))
    is_subscribed_for_email_updates = db.Column(db.Boolean, nullable=False)


class Company(db.Model, BaseMixin):
    """Store the company details.

    It turns out that each booking has two FK to this model, one for the owner
    company (company) and another for the affiliate company (affiliate_company)

    FH does not provide pk for this model like it does for the others, which
    means that we have to rely on short_name to retrieve existing instances.
    """

    __table_name__ = "company"
    id = db.Column(db.BigInteger, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(256), nullable=False)
    short_name = db.Column(db.String(30), nullable=False, unique=True)
    currency = db.Column(db.String(10), nullable=False)

    @classmethod
    def get(cls, short_name):
        """Override the default get method so we retrieve by short_name."""
        instance = cls.query.filter_by(short_name=short_name).first()
        if instance:
            return instance
        else:
            raise DoesNotExist(cls.__table_name__)

    @classmethod
    def get_object_or_none(cls, short_name):
        """
        Get the object or none.

        This method is a wrapper of query.get() that is less readable.
        """
        return cls.query.filter_by(short_name=short_name).first()


class EffectiveCancellationPolicy(db.Model, BaseMixin):
    """Store the cancellation policy for the booking.

    Is a 1:1 on bookings.
    """

    __table_name__ = "effective_cancellation_policy"
    id = db.Column(db.BigInteger, db.ForeignKey("booking.id"), primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    cutoff = db.Column(db.DateTime(timezone=True) )
    cancellation_type = db.Column(db.String(64), nullable=False)
