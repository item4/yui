"""Goodbye closers

Revision ID: 8561310bbaab
Revises: e27cf538f420
Create Date: 2018-09-20 21:41:01.790424

"""

from alembic import op

import sqlalchemy as sa

from yui.models.type import TimezoneType

# revision identifiers, used by Alembic.
revision = '8561310bbaab'
down_revision = 'e27cf538f420'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('closers_event')
    op.drop_table('closers_notice')
    op.drop_table('closers_gm_note')


def downgrade():
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
