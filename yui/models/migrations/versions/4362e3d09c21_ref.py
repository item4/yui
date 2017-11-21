"""Ref

Revision ID: 4362e3d09c21
Revises: a48384d2e66c
Create Date: 2017-11-21 17:25:06.495624

"""

from alembic import op

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4362e3d09c21'
down_revision = 'a48384d2e66c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'ref',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('body', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )


def downgrade():
    op.drop_table('ref')
