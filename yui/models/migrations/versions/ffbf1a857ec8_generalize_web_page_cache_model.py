"""Generalize web page cache model

Revision ID: ffbf1a857ec8
Revises: 80ead52e14e1
Create Date: 2017-11-25 21:19:24.794473

"""

from alembic import op

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ffbf1a857ec8'
down_revision = '80ead52e14e1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'web_page_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('body', sa.Text(), nullable=True),
        sa.Column('created_datetime', sa.DateTime(timezone=True),
                  nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.drop_table('ref')


def downgrade():
    op.create_table(
        'ref',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('name', sa.VARCHAR(), nullable=False),
        sa.Column('body', sa.TEXT(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.drop_table('web_page_cache')
