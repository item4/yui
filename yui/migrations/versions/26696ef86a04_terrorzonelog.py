"""TerrorZoneLog

Revision ID: 26696ef86a04
Revises: 139d8fcc4d5a
Create Date: 2025-06-01 19:10:52.374654

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "26696ef86a04"
down_revision = "139d8fcc4d5a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "terrorzonelog",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("levels", sa.ARRAY(sa.Integer()), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("broadcasted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_fetch_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("start_at"),
    )


def downgrade():
    op.drop_table("terrorzonelog")
