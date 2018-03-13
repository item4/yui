"""Refactor models for datetime+tz

Revision ID: 1adc49c97075
Revises:
Create Date: 2018-03-14 05:02:51.506053

"""
import enum

from alembic import op

import sqlalchemy as sa

import sqlalchemy_utils as sau

from yui.models.type import JSONType, TimezoneType


# revision identifiers, used by Alembic.
revision = '1adc49c97075'
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
        'feed',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('channel', sa.String(), nullable=False),
        sa.Column('updated_datetime', sa.DateTime(), nullable=False),
        sa.Column('updated_timezone', TimezoneType(), nullable=True),
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
        'saomd_notice',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('notice_id', sa.Integer(), nullable=False),
        sa.Column('server', sau.types.ChoiceType(Server, impl=sa.Integer()),
                  nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('duration', sa.String(), nullable=True),
        sa.Column('short_description', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'site_sub',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('user', sa.String(), nullable=False),
        sa.Column('body', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'web_page_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('body', sa.Text(), nullable=True),
        sa.Column('created_datetime', sa.DateTime(), nullable=False),
        sa.Column('created_timezone', TimezoneType(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )


def downgrade():
    op.drop_table('web_page_cache')
    op.drop_table('site_sub')
    op.drop_table('saomd_notice')
    op.drop_table('memo')
    op.drop_table('json_cache')
    op.drop_table('feed')
    op.drop_table('aws')
