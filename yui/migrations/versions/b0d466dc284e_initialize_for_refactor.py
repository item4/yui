"""Initialize for refactor

Revision ID: b0d466dc284e
Revises:
Create Date: 2018-10-07 19:11:06.774732

"""
import enum

from alembic import op

import sqlalchemy as sa

import sqlalchemy_utils as sau

from yui.orm.types import JSONType
from yui.orm.types import TimezoneType

# revision identifiers, used by Alembic.
revision = 'b0d466dc284e'
down_revision = None
branch_labels = None
depends_on = None


@enum.unique
class Server(enum.IntEnum):
    """Server."""

    japan = 1
    worldwide = 2


def upgrade():
    op.create_table(
        'aws',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('height', sa.Integer(), nullable=False),
        sa.Column('is_raining', sa.Boolean(), nullable=True),
        sa.Column('rain15', sa.Float(), nullable=True),
        sa.Column('rain60', sa.Float(), nullable=True),
        sa.Column('rain3h', sa.Float(), nullable=True),
        sa.Column('rain6h', sa.Float(), nullable=True),
        sa.Column('rain12h', sa.Float(), nullable=True),
        sa.Column('rainday', sa.Float(), nullable=True),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('wind_direction1', sa.String(), nullable=True),
        sa.Column('wind_speed1', sa.Float(), nullable=True),
        sa.Column('wind_direction10', sa.String(), nullable=True),
        sa.Column('wind_speed10', sa.Float(), nullable=True),
        sa.Column('humidity', sa.Integer(), nullable=True),
        sa.Column('pressure', sa.Float(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('observed_datetime', sa.DateTime(), nullable=False),
        sa.Column('observed_timezone', TimezoneType(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'json_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('body', JSONType(), nullable=True),
        sa.Column('created_datetime', sa.DateTime(), nullable=False),
        sa.Column('created_timezone', TimezoneType(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_table(
        'memo',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('keyword', sa.String(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('author', sa.String(), nullable=False),
        sa.Column('created_datetime', sa.DateTime(), nullable=False),
        sa.Column('created_timezone', TimezoneType(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'rss_feed_url',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('channel', sa.String(), nullable=False),
        sa.Column('updated_datetime', sa.DateTime(), nullable=False),
        sa.Column('updated_timezone', TimezoneType(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'saomd_notice',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('notice_id', sa.Integer(), nullable=False),
        sa.Column(
            'server',
            sau.types.choice.ChoiceType(Server, impl=sa.Integer()),
            nullable=False,
        ),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('duration', sa.String(), nullable=True),
        sa.Column('short_description', sa.String(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('saomd_notice')
    op.drop_table('rss_feed_url')
    op.drop_table('memo')
    op.drop_table('json_cache')
    op.drop_table('aws')
