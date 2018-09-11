"""Add is_deleted flag for SAO MD Notice

Revision ID: e27cf538f420
Revises: c77609c62c8c
Create Date: 2018-09-11 14:09:36.593872

"""

from alembic import op

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e27cf538f420'
down_revision = 'c77609c62c8c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'saomd_notice',
        sa.Column('is_deleted', sa.Boolean(), nullable=True)
    )


def downgrade():
    op.drop_column('saomd_notice', 'is_deleted')
