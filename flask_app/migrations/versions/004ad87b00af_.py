"""
2. Add new found fields: headline, language and is_subscribed_for_sms_updates

Revision ID: 004ad87b00af
Revises: f92bf8b73e44
Create Date: 2021-08-23 17:34:41.221155

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004ad87b00af'
down_revision = 'f92bf8b73e44'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('availability', sa.Column('headline', sa.String(length=255), nullable=True))
    op.add_column('booking', sa.Column('is_subscribed_for_sms_updates', sa.Boolean(), nullable=True))
    op.add_column('contact', sa.Column('language', sa.String(length=256), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('contact', 'language')
    op.drop_column('booking', 'is_subscribed_for_sms_updates')
    op.drop_column('availability', 'headline')
    # ### end Alembic commands ###
