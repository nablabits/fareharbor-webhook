"""
3. Add a new field created_by and populate it with default value.

Revision ID: 6c4f84fc263e
Revises: 004ad87b00af
Create Date: 2021-09-15 18:47:24.978205

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "6c4f84fc263e"
down_revision = "004ad87b00af"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "booking", sa.Column("created_by", sa.String(length=64), nullable=True)
    )
    op.execute("UPDATE booking SET created_by = 'staff'")
    op.alter_column("booking", "created_by", nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("booking", "created_by")
    # ### end Alembic commands ###
