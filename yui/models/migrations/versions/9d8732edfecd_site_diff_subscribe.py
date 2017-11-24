"""Watch - subscribe diff of website

Revision ID: 9d8732edfecd
Revises: 4362e3d09c21
Create Date: 2017-11-23 01:20:07.923507

"""

from alembic import op

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d8732edfecd'
down_revision = '4362e3d09c21'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'site_sub',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('user', sa.String(length=10), nullable=False),
        sa.Column('body', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('site_sub')
