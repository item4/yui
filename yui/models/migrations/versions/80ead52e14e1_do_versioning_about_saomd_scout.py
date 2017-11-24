"""Do versioning about SAOMD Scout

Revision ID: 80ead52e14e1
Revises: 9d8732edfecd
Create Date: 2017-11-25 00:13:18.378014

"""

from alembic import op

import sqlalchemy as sa


revision = '80ead52e14e1'
down_revision = '9d8732edfecd'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'saomd_scout',
        sa.Column(
            'version',
            sa.Integer(),
            server_default='1',
            default=1,
            nullable=False
        )
    )


def downgrade():
    op.drop_column('saomd_scout', 'version')
