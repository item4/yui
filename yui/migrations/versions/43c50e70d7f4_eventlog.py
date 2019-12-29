"""EventLog

Revision ID: 43c50e70d7f4
Revises: 9888ff06109d
Create Date: 2019-12-29 10:03:43.636759

"""

from alembic import op

import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '43c50e70d7f4'
down_revision = '9888ff06109d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'event_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ts', sa.String(), nullable=False),
        sa.Column('channel', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('event_log')
