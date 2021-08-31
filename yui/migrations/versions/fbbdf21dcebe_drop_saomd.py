"""Drop SAOMD

Revision ID: fbbdf21dcebe
Revises: 2d8d76d94b27
Create Date: 2021-08-31 12:32:51.183992

"""

import enum

from alembic import op

import sqlalchemy as sa

from sqlalchemy_utils import ChoiceType

# revision identifiers, used by Alembic.
revision = 'fbbdf21dcebe'
down_revision = '2d8d76d94b27'
branch_labels = None
depends_on = None


@enum.unique
class Server(enum.IntEnum):
    pass


def upgrade():
    op.drop_table('saomd_notice')


def downgrade():
    op.create_table(
        'saomd_notice',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('notice_id', sa.Integer(), nullable=False),
        sa.Column(
            'server', ChoiceType(Server, impl=sa.Integer()), nullable=False
        ),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('duration', sa.String(), nullable=True),
        sa.Column('short_description', sa.String(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
