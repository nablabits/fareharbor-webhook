import functools

from marshmallow import Schema, fields

requiredString = functools.partial(fields.String, required=True)
requiredInteger = functools.partial(fields.Integer, required=True)
requiredBool = functools.partial(fields.Bool, required=True)
requiredFloat = functools.partial(fields.Float, required=True)
requiredEmail = functools.partial(fields.Email, required=True)
requiredDate = functools.partial(fields.Date, required=True)
requiredDateTime = functools.partial(fields.DateTime, required=True)
requiredNested = functools.partial(fields.Nested, required=True)


class IdentifierSchemaMixin(Schema):
    pk = fields.Integer(required=True)


class ExtendedOptionsSchema(IdentifierSchemaMixin):
    name = requiredString()
    is_taxable = requiredBool()
    modifier_kind = requiredString()
    description_safe_html = requiredString()
    offset = requiredInteger()
    pk = requiredInteger()
    percentage = requiredInteger()
    modifier_type = requiredString()
    is_always_per_customer = requiredBool()
    description = requiredString()


class CustomFieldSchema(IdentifierSchemaMixin):
    name = requiredString()
    is_required = requiredBool()
    description = requiredString()
    title = requiredString()
    booking_notes_safe_html = requiredString()
    is_taxable = requiredBool()
    modifier_kind = requiredString()
    description_safe_html = requiredString()
    booking_notes = requiredString()
    offset = requiredInteger()
    percentage = requiredInteger()
    modifier_type = requiredString()
    field_type = requiredString(data_key="type")
    is_always_per_customer = requiredBool()
    extended_options = fields.Nested(ExtendedOptionsSchema, many=True)


class CustomFieldValueSchema(IdentifierSchemaMixin):
    custom_field = requiredNested(CustomFieldSchema)
    name = requiredString()
    display_value = requiredString()
    value = requiredString()


class CustomFieldInstanceSchema(IdentifierSchemaMixin):
    custom_field = requiredNested(CustomFieldSchema)


class CustomerPrototypeSchema(IdentifierSchemaMixin):
    note = requiredString()
    total = requiredInteger()
    display_name = requiredString()
    total_including_tax = requiredInteger()


class CustomerTypeSchema(IdentifierSchemaMixin):
    note = requiredString()
    singular = requiredString()
    plural = requiredString()


class CustomerTypeRateSchema(IdentifierSchemaMixin):
    customer_prototype = requiredNested(CustomerPrototypeSchema)
    customer_type = requiredNested(CustomerTypeSchema)
    custom_field_instances = fields.Nested(
        CustomFieldInstanceSchema, many=True, allow_none=True
    )
    capacity = requiredInteger()
    minimum_party_size = requiredInteger(allow_none=True)
    maximum_party_size = requiredInteger(allow_none=True)
    total_including_tax = requiredInteger()
    total = requiredInteger()


class CompanySchema(Schema):
    currency = requiredString()
    short_name = fields.String()
    shortname = fields.String()
    name = requiredString()


class CheckinStatusSchema(IdentifierSchemaMixin):
    checkin_status_type = requiredString(data_key="type")
    name = requiredString()

    # these below are not used for the moment.
    unicode = fields.String()
    is_hidden = fields.String()
    cls_name = fields.String()
    company = fields.Field()
    uri = fields.String()
    sortable_index = fields.Integer()
    is_hidden = fields.Boolean()
    cls_ = fields.String(data_key="cls")


class CustomerSchema(IdentifierSchemaMixin):
    checkin_url = requiredString()
    checkin_status = requiredNested(CheckinStatusSchema, allow_none=True)
    custom_field_values = requiredNested(
        CustomFieldValueSchema, allow_none=True, many=True
    )
    customer_type_rate = requiredNested(CustomerTypeRateSchema)


class ItemSchema(IdentifierSchemaMixin):
    name = requiredString()


class AvailabilitySchema(IdentifierSchemaMixin):
    capacity = requiredInteger()
    minimum_party_size = requiredInteger(allow_none=True)
    maximum_party_size = requiredInteger(allow_none=True)
    start_at = requiredDateTime()
    end_at = requiredDateTime()
    custom_field_instances = requiredNested(CustomFieldInstanceSchema, many=True)
    customer_type_rates = requiredNested(CustomerTypeRateSchema, many=True)
    item = requiredNested(ItemSchema)
    headline = fields.String()


class ContactSchema(Schema):
    phone_country = requiredString()
    name = requiredString()
    is_subscribed_for_email_updates = requiredBool()
    normalized_phone = requiredString()
    phone = requiredString()
    email = requiredString()
    language = fields.String()


class EffectiveCancellationPolicySchema(Schema):
    cutoff = requiredString(allow_none=True)
    cancellation_type = requiredString(data_key="type")


class OrderSchema(Schema):
    display_id = requiredString()


class BookingSchema(IdentifierSchemaMixin):
    agent = requiredString(allow_none=True)
    arrival = requiredString(allow_none=True)
    confirmation_url = requiredString()
    customer_count = requiredInteger()
    dashboard_url = requiredString()
    desk = requiredString(allow_none=True)
    display_id = requiredString()
    external_id = requiredString()
    note = requiredString()
    note_safe_html = requiredString()
    pickup = requiredString(allow_none=True)
    pk = requiredInteger()
    rebooked_from = requiredString(allow_none=True)
    rebooked_to = requiredString(allow_none=True)
    status = requiredString()
    uuid = requiredString()
    voucher_number = requiredString()

    # price fields
    receipt_subtotal = requiredInteger()
    receipt_taxes = requiredInteger()
    receipt_total = requiredInteger()
    amount_paid = requiredInteger()
    invoice_price = requiredInteger()

    # Price displays
    receipt_subtotal_display = requiredString()
    receipt_taxes_display = requiredString()
    receipt_total_display = requiredString()
    amount_paid_display = requiredString()
    invoice_price_display = requiredString()

    # Boolean fields
    is_eligible_for_cancellation = requiredBool()
    is_subscribed_for_sms_updates = requiredBool()

    # Nested fields
    order = requiredNested(OrderSchema, allow_none=True)
    customers = fields.Nested(CustomerSchema, many=True)
    availability = requiredNested(AvailabilitySchema)
    affiliate_company = requiredNested(CompanySchema, allow_none=True)
    company = requiredNested(CompanySchema)
    custom_field_values = requiredNested(CustomFieldValueSchema, many=True)
    effective_cancellation_policy = requiredNested(EffectiveCancellationPolicySchema)
    contact = requiredNested(ContactSchema)


class AddBikesSchema(Schema):
    """Validate the schema for the add-bikes requests."""

    availability_id = requiredInteger()
    bikes = fields.List(fields.String(), required=True)


class ReplaceBikesSchema(Schema):
    """Validate the schema for the replace-bikes requests."""

    availability_id = requiredInteger()
    bike_picked = requiredString()
    bike_returned = requiredString()
