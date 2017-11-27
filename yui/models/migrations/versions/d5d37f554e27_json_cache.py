"""JSON Cache

Revision ID: d5d37f554e27
Revises: ffbf1a857ec8
Create Date: 2017-11-27 19:11:56.209136

"""

from alembic import op

import sqlalchemy as sa

from yui.models.type import JSONType


revision = 'd5d37f554e27'
down_revision = 'ffbf1a857ec8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'json_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('body', JSONType(), nullable=True),
        sa.Column('created_datetime', sa.DateTime(timezone=True),
                  nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )


def downgrade():
    op.drop_table('json_cache')
