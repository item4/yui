"""Update to follow AWS website

Revision ID: d7af8fbe5cf9
Revises: 1adc49c97075
Create Date: 2018-06-15 19:37:01.460895

"""

from alembic import op

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd7af8fbe5cf9'
down_revision = '1adc49c97075'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('aws', sa.Column('rain3h', sa.Float(), nullable=True))


def downgrade():
    op.drop_column('aws', 'rain3h')
