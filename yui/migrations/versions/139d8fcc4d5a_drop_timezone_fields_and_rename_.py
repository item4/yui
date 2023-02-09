"""Drop timezone fields and rename datetime fields

Revision ID: 139d8fcc4d5a
Revises: 75c91e7af605
Create Date: 2023-02-09 09:43:29.021093

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy_utils import TimezoneType

# revision identifiers, used by Alembic.
revision = "139d8fcc4d5a"
down_revision = "75c91e7af605"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("memo", "created_datetime", new_column_name="created_at")
    op.alter_column(
        "rss_feed_url", "updated_datetime", new_column_name="updated_at"
    )
    op.drop_column("memo", "created_timezone")
    op.drop_column("rss_feed_url", "updated_timezone")


def downgrade():
    op.alter_column("memo", "created_at", new_column_name="created_datetime")
    op.alter_column(
        "rss_feed_url", "updated_at", new_column_name="updated_datetime"
    )
    op.add_column("memo", sa.Column("created_timezone", TimezoneType()))
    op.add_column(
        "rss_feed_url", sa.Column("updated_timezone", TimezoneType())
    )
