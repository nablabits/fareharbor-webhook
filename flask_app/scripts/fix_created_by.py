"""
Fix the created_by default value to a more appropiate one.

With the introduction of the new created_by we filled all the existing bookings
with "staff" default value. However, this should be changed for the bookings
that have an affiliate company to the short name in it.

To execute this script:
$> export FLASK_APP=run.py
$> flask shell < fix_created_by.py
Pray.
"""

from fh_webhook.models import Booking, Company, db

query = (
    db.session.query(Booking, Company)
    .filter(Booking.affiliate_company_id == Company.id)
    .filter(Booking.affiliate_company_id is not None)
)

for pair in query:
    booking, company = pair
    if not booking or not company:
        print("warning", booking.id)
        continue
    booking.created_by = company.short_name


db.session.commit()
