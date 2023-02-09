"""Refactor datetime fields

Revision ID: 0e7bdd5c7473
Revises:
Create Date: 2020-05-10 17:28:07.620112

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy_utils import TimezoneType

# revision identifiers, used by Alembic.
revision = "0e7bdd5c7473"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "event_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ts", sa.String(), nullable=False),
        sa.Column("channel", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "memo",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("keyword", sa.String(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("author", sa.String(), nullable=False),
        sa.Column(
            "created_datetime", sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column("created_timezone", TimezoneType(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "rss_feed_url",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("channel", sa.String(), nullable=False),
        sa.Column(
            "updated_datetime", sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column("updated_timezone", TimezoneType(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("rss_feed_url")
    op.drop_table("memo")
    op.drop_table("event_log")
