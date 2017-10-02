"""Memo

Revision ID: 722ab69c73d1
Revises: c02aadebef95
Create Date: 2017-10-03 04:09:06.441998

"""

from alembic import op

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '722ab69c73d1'
down_revision = 'c02aadebef95'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'memo',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('keyword', sa.String(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('author', sa.String(), nullable=False),
        sa.Column('created_datetime', sa.DateTime(timezone=True),
                  nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('memo')
