# About scripts

Inside this dir, you will find several utilities created to fix issues ad hoc.
This is the quick list of the scripts although each of them carry more detailed instructions.

## backfill_new_fields
Backfill the new fields found on Aug 10th.

By Aug 10th some new fields were discovered on these models:
- Avalilability: headline
- Contact: language
- Booking: is_subscribed_for_sms_updates

## fix_created_by
Fix the created_by default value to a more appropiate one.

With the introduction of the new created_by we filled all the existing bookings with "staff" default value. However, this should be changed for the bookings that have an affiliate company to the short name in it.

## fix_customer_model
Fix the customer_type_rate relationship with customer model. Because of the bug found on 2021-09-30, we should fix the customer type rates with the data we find in the stored responses.

## populate_created_by
Update the db values for created_by with the data on FH.

As FH does not send the origin data on the webhook, once in a while we have to populate it manually. To do so we download a csv with the content for the year for booking_id & created_by fields.

## validate_responses_with_schema
A convenience script used to check all the responses collected (~3200) under marshmallow validation.

