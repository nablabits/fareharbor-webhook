"""empty message

Revision ID: 85403b492b5b
Revises: 1a8a80720271
Create Date: 2021-05-11 20:14:57.793874

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '85403b492b5b'
down_revision = '1a8a80720271'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('custom_field',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('modifier_kind', sa.String(length=64), nullable=False),
    sa.Column('modifier_type', sa.String(length=64), nullable=False),
    sa.Column('field_type', sa.String(length=64), nullable=False),
    sa.Column('offset', sa.Integer(), nullable=True),
    sa.Column('percentage', sa.Integer(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('booking_notes', sa.Text(), nullable=True),
    sa.Column('description_safe_html', sa.Text(), nullable=True),
    sa.Column('booking_notes_safe_html', sa.Text(), nullable=True),
    sa.Column('is_required', sa.Boolean(), nullable=False),
    sa.Column('is_taxable', sa.Boolean(), nullable=False),
    sa.Column('is_always_per_customer', sa.Boolean(), nullable=False),
    sa.Column('extended_options', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['extended_options'], ['custom_field.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('customer_prototype',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('total', sa.Integer(), nullable=True),
    sa.Column('total_including_tax', sa.Integer(), nullable=True),
    sa.Column('display_name', sa.String(length=64), nullable=False),
    sa.Column('note', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('customer_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('singular', sa.String(length=64), nullable=False),
    sa.Column('plural', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('availability',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('capacity', sa.SmallInteger(), nullable=False),
    sa.Column('minimum_party_size', sa.SmallInteger(), nullable=False),
    sa.Column('maximum_party_size', sa.SmallInteger(), nullable=False),
    sa.Column('start_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('end_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['item_id'], ['item.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('booking',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('voucher_number', sa.String(length=64), nullable=True),
    sa.Column('display_id', sa.String(length=64), nullable=False),
    sa.Column('note_safe_html', sa.Text(), nullable=True),
    sa.Column('agent', sa.String(length=64), nullable=True),
    sa.Column('confirmation_url', sa.String(length=255), nullable=True),
    sa.Column('customer_count', sa.SmallInteger(), nullable=False),
    sa.Column('affiliate_company', sa.String(length=64), nullable=True),
    sa.Column('uuid', sa.String(length=40), nullable=False),
    sa.Column('dashboard_url', sa.String(length=264), nullable=True),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('pickup', sa.String(length=64), nullable=True),
    sa.Column('status', sa.String(length=64), nullable=True),
    sa.Column('availability_id', sa.Integer(), nullable=False),
    sa.Column('receipt_subtotals', sa.Integer(), nullable=True),
    sa.Column('receipt_taxes', sa.Integer(), nullable=True),
    sa.Column('receipt_total', sa.Integer(), nullable=True),
    sa.Column('amount_paid', sa.Integer(), nullable=True),
    sa.Column('invoice_price', sa.Integer(), nullable=True),
    sa.Column('receipt_subtotal_display', sa.String(length=64), nullable=True),
    sa.Column('receipt_taxes_display', sa.String(length=64), nullable=True),
    sa.Column('receipt_total_display', sa.String(length=64), nullable=True),
    sa.Column('amount_paid_display', sa.String(length=64), nullable=True),
    sa.Column('invoice_price_display', sa.String(length=64), nullable=True),
    sa.Column('desk', sa.String(length=64), nullable=True),
    sa.Column('is_eligible_for_cancellation', sa.Boolean(), nullable=True),
    sa.Column('arrival', sa.String(length=64), nullable=True),
    sa.Column('rebooked_to', sa.String(length=64), nullable=True),
    sa.Column('rebooked_from', sa.String(length=64), nullable=True),
    sa.Column('external_id', sa.String(length=64), nullable=True),
    sa.Column('order', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['availability_id'], ['availability.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('uuid')
    )
    op.create_table('custom_field_instances',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('custom_field_id', sa.Integer(), nullable=True),
    sa.Column('availability_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['availability_id'], ['availability.id'], ),
    sa.ForeignKeyConstraint(['custom_field_id'], ['custom_field.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('company',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('short_name', sa.String(length=30), nullable=False),
    sa.Column('currency', sa.String(length=10), nullable=False),
    sa.Column('booking_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['booking_id'], ['booking.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('booking_id')
    )
    op.create_table('contact',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('email', sa.String(length=256), nullable=True),
    sa.Column('phone_country', sa.String(length=10), nullable=True),
    sa.Column('phone', sa.String(length=30), nullable=True),
    sa.Column('normalized_phone', sa.String(length=30), nullable=True),
    sa.Column('is_subscribed_for_email_updates', sa.Boolean(), nullable=False),
    sa.Column('booking_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['booking_id'], ['booking.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('booking_id')
    )
    op.create_table('customer_type_rate',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('capacity', sa.SmallInteger(), nullable=False),
    sa.Column('minimum_party_size', sa.SmallInteger(), nullable=False),
    sa.Column('maximum_party_size', sa.SmallInteger(), nullable=False),
    sa.Column('booking_id', sa.Integer(), nullable=False),
    sa.Column('availability_id', sa.Integer(), nullable=False),
    sa.Column('customer_prototype_id', sa.Integer(), nullable=False),
    sa.Column('customer_type_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['availability_id'], ['availability.id'], ),
    sa.ForeignKeyConstraint(['booking_id'], ['booking.id'], ),
    sa.ForeignKeyConstraint(['customer_prototype_id'], ['customer_prototype.id'], ),
    sa.ForeignKeyConstraint(['customer_type_id'], ['customer_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('effective_cancellation_policy',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('cutoff', sa.DateTime(timezone=True), nullable=False),
    sa.Column('cancellation_type', sa.String(length=64), nullable=False),
    sa.Column('booking_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['booking_id'], ['booking.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('booking_id')
    )
    op.create_table('customer',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('checkin_url', sa.String(length=264), nullable=True),
    sa.Column('checking_status', sa.String(length=64), nullable=True),
    sa.Column('customer_type_rate_id', sa.Integer(), nullable=False),
    sa.Column('booking_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['booking_id'], ['booking.id'], ),
    sa.ForeignKeyConstraint(['customer_type_rate_id'], ['customer_type_rate.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('custom_field_values',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('value', sa.String(length=2048), nullable=True),
    sa.Column('display_value', sa.String(length=2048), nullable=True),
    sa.Column('custom_field_id', sa.Integer(), nullable=True),
    sa.Column('booking_id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['booking_id'], ['booking.id'], ),
    sa.ForeignKeyConstraint(['custom_field_id'], ['custom_field.id'], ),
    sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('sample_table')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sample_table',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('city', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='sample_table_pkey')
    )
    op.drop_table('custom_field_values')
    op.drop_table('customer')
    op.drop_table('effective_cancellation_policy')
    op.drop_table('customer_type_rate')
    op.drop_table('contact')
    op.drop_table('company')
    op.drop_table('custom_field_instances')
    op.drop_table('booking')
    op.drop_table('availability')
    op.drop_table('item')
    op.drop_table('customer_type')
    op.drop_table('customer_prototype')
    op.drop_table('custom_field')
    # ### end Alembic commands ###
