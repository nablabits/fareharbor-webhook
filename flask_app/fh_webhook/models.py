"""Define the models in the database."""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy_json import mutable_json_type

from .exceptions import DoesNotExist

metadata = MetaData()
db = SQLAlchemy(metadata=metadata)


class BaseMixin:
    """Provide common methods for models."""

    # add a timestamp to all models
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False)

    @classmethod
    def get(cls, id):
        """
        Try to get an instance or raise an error.

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


class StoredRequest(db.Model, BaseMixin):
    """
    Store the raw content of the requests made by FH.

    The target of this model is to spot files that are not correctly processed
    as they will show created_at field but not processed_at one. Also we might
    want to avoid processing a file twice when populating the database.
    """

    __table_name__ = "stored_request"
    id = db.Column(db.BigInteger, primary_key=True)
    processed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    filename = db.Column(db.String(64))
    body = db.Column(db.Text)


class Booking(db.Model, BaseMixin):
    """Store the information about the booking.

    Note that FH does not provide for the time being the created_by value so we
    have to make it up out of the value we find in affiliate_company in the
    response. Otherwise we assume it as booked by a generic staff user.
    """

    __table_name__ = "booking"
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
    created_by = db.Column(db.String(64), nullable=False, default="staff")

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
    is_subscribed_for_sms_updates = db.Column(db.Boolean)
    arrival = db.Column(db.String(64))
    rebooked_to = db.Column(db.String(64))
    rebooked_from = db.Column(db.String(64))
    external_id = db.Column(db.String(64))

    # implement Postgres' JSONB field
    MutableJson = mutable_json_type(dbtype=JSONB, nested=False)
    order = db.Column(MutableJson)

    # Foreign key fields
    availability_id = db.Column(
        db.BigInteger, db.ForeignKey("availability.id"), nullable=False
    )
    company_id = db.Column(db.BigInteger, db.ForeignKey("company.id"), nullable=False)
    affiliate_company_id = db.Column(db.BigInteger, db.ForeignKey("company.id"))

    # Reverse relationships
    availability = db.relationship("Availability", back_populates="bookings")
    customers = db.relationship("Customer", back_populates="booking")


bike_usages = db.Table(
    "bike_usages",
    db.Column("bike_id", db.BigInteger, db.ForeignKey("bike.id"), primary_key=True),
    db.Column(
        "availability_id",
        db.BigInteger,
        db.ForeignKey("availability.id"),
        primary_key=True,
    ),
)


class Bike(db.Model, BaseMixin):
    """Store the uuids of the bikes as they appear on Odoo."""

    __table_name__ = "bike"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(32), unique=True, index=True, nullable=False)
    readable_name = db.Column(db.String(255), unique=True, nullable=False)

    @classmethod
    def get_uuid(cls, uuid):
        """
        Get a bike entity by uuid.

        While strings are not as effective as integers to make lookups, most of the times we will
        use the uuid for a given bike to fetch it.
        """
        instance = cls.query.filter(cls.uuid == uuid).first()
        if instance:
            return instance
        else:
            raise DoesNotExist(cls.__table_name__)
        return instance


class Availability(db.Model, BaseMixin):
    """Store availabilities.

    Each booking belongs to one and only availability
    """

    __table_name__ = "availability"
    id = db.Column(db.BigInteger, primary_key=True)
    capacity = db.Column(db.Integer, nullable=False)
    minimum_party_size = db.Column(db.SmallInteger)
    maximum_party_size = db.Column(db.SmallInteger)
    start_at = db.Column(db.DateTime(timezone=True), nullable=False)
    end_at = db.Column(db.DateTime(timezone=True), nullable=False)
    headline = db.Column(db.String(255))

    # foreign key fields
    item_id = db.Column(db.BigInteger, db.ForeignKey("item.id"), nullable=False)

    # reverse relationships
    bookings = db.relationship("Booking", back_populates="availability")
    item = db.relationship("Item", back_populates="availabilities")
    bike_usages = db.relationship(
        "Bike",
        secondary=bike_usages,
        lazy="subquery",
        backref=db.backref("availabilities", lazy=True),
    )


class Item(db.Model, BaseMixin):
    """Items are the products we sell in the business."""

    __table_name__ = "item"
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(200))

    # reverse relationships
    availabilities = db.relationship("Availability", back_populates="item")


class CheckinStatus(db.Model, BaseMixin):
    __table_name__ = "checkin_status"
    id = db.Column(db.BigInteger, primary_key=True)
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
    checkin_url = db.Column(db.String(264))

    # Foreign Key fields
    customer_type_rate_id = db.Column(
        db.BigInteger, db.ForeignKey("customer_type_rate.id"), nullable=False
    )
    checkin_status_id = db.Column(db.BigInteger, db.ForeignKey("checkin_status.id"))
    # M2M to booking
    booking_id = db.Column(db.BigInteger, db.ForeignKey("booking.id"), nullable=False)
    booking = db.relationship("Booking", back_populates="customers")


class CustomerTypeRate(db.Model, BaseMixin):
    """Store each customer type rate.

    Every availability can have several customer type rates that are based on
    customer prototypes (the ones defined in the settings).
    It acts as a M2M between the availability and the customer prototype.

    Then each customer type rate can be selected from `Customer` model to match
    the one picked from the availability for that specific customer.
    """

    __table_name__ = "customer_type_rate"
    id = db.Column(db.BigInteger, primary_key=True)
    capacity = db.Column(db.Integer)
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
    custom_field_id = db.Column(
        db.BigInteger, db.ForeignKey("custom_field.id"), nullable=False
    )
    availability_id = db.Column(db.BigInteger, db.ForeignKey("availability.id"))
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
                "Custom field instance needs either availability or "
                + "customer type rate"
            )

        if self.availability_id and self.customer_type_rate_id:
            raise ValueError(
                "Availability and customer type rate can't have value at the"
                + " same time."
            )


class CustomFieldValue(db.Model, BaseMixin):
    """Store the chosen values for each booking/customer.

    Acts as M2M among bookings-custom_fields and customer-custom_fields.
    """

    __table_name__ = "custom_field_values"
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    value = db.Column(db.String(2048))
    display_value = db.Column(db.String(2048))

    # Foreign key fields
    custom_field_id = db.Column(db.BigInteger, db.ForeignKey("custom_field.id"))
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
            raise ValueError("Booking and customer can't have value at the same time.")


class CustomField(db.Model, BaseMixin):
    """Store the types of custom fields available."""

    __table_name__ = "custom_field"
    id = db.Column(db.BigInteger, primary_key=True)
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

    It's a 1:1 on bookings.
    """

    __table_name__ = "contact"
    id = db.Column(db.BigInteger, db.ForeignKey("booking.id"), primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256))
    language = db.Column(db.String(256))
    phone_country = db.Column(db.String(10))
    phone = db.Column(db.String(256), nullable=False)
    normalized_phone = db.Column(db.String(256), nullable=False)
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
    name = db.Column(db.String(256), nullable=False)
    short_name = db.Column(db.String(64), nullable=False, unique=True)
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
    cutoff = db.Column(db.DateTime(timezone=True))
    cancellation_type = db.Column(db.String(64), nullable=False)
