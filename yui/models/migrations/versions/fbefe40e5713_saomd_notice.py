"""SAOMD Notice

Revision ID: fbefe40e5713
Revises: d5d37f554e27
Create Date: 2017-11-29 17:21:45.072734

"""
import enum

from alembic import op

import sqlalchemy as sa

from sqlalchemy_utils.types import ChoiceType


# revision identifiers, used by Alembic.
revision = 'fbefe40e5713'
down_revision = 'd5d37f554e27'
branch_labels = None
depends_on = None


class Server(enum.Enum):
    """Server."""

    japan = 1
    worldwide = 2


def upgrade():
    op.create_table(
        'saomd_notice',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('notice_id', sa.Integer(), nullable=False),
        sa.Column('server', ChoiceType(Server, impl=sa.Integer()),
                  nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('duration', sa.String(), nullable=True),
        sa.Column('short_description', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('saomd_notice')
