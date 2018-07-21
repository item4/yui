"""Closers Notice/Event/GMNote

Revision ID: 5e8ae030c78d
Revises: d7af8fbe5cf9
Create Date: 2018-07-22 03:11:23.255361

"""

from alembic import op

import sqlalchemy as sa

from yui.models.type import TimezoneType

# revision identifiers, used by Alembic.
revision = '5e8ae030c78d'
down_revision = 'd7af8fbe5cf9'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'closers_event',
        sa.Column('article_sn', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('posted_date', sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint('article_sn'),
    )
    op.create_table(
        'closers_gm_note',
        sa.Column('article_sn', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('text', sa.String(), nullable=False),
        sa.Column('image_url', sa.String(), nullable=False),
        sa.Column('posted_date', sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint('article_sn'),
    )
    op.create_table(
        'closers_notice',
        sa.Column('article_sn', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('posted_date', sa.Date(), nullable=False),
        sa.Column('updated_datetime', sa.DateTime(), nullable=False),
        sa.Column('updated_timezone', TimezoneType(), nullable=True),
        sa.PrimaryKeyConstraint('article_sn'),
    )


def downgrade():
    op.drop_table('closers_notice')
    op.drop_table('closers_gm_note')
    op.drop_table('closers_event')
