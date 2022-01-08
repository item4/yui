"""Drop shared cache app

Revision ID: 2d8d76d94b27
Revises: 59c36093b2ed
Create Date: 2021-01-02 10:59:32.722200

"""
from alembic import op

import sqlalchemy as sa

from yui.orm.types import JSONType
from yui.orm.types import TimezoneType


# revision identifiers, used by Alembic.
revision = '2d8d76d94b27'
down_revision = '59c36093b2ed'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('json_cache')


def downgrade():
    op.create_table(
        'json_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('body', JSONType(), nullable=True),
        sa.Column(
            'created_datetime', sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column('created_timezone', TimezoneType(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
