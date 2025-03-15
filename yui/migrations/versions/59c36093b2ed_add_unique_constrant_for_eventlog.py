"""Add unique constrant for eventlog

Revision ID: 59c36093b2ed
Revises: 0e7bdd5c7473
Create Date: 2020-12-24 09:42:17.075631

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "59c36093b2ed"
down_revision = "0e7bdd5c7473"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(None, "event_log", ["ts", "channel"])


def downgrade():
    op.drop_constraint("", "event_log", type_="unique")
