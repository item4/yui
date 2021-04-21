"""Refactor datetime fields

Revision ID: 0e7bdd5c7473
Revises:
Create Date: 2020-05-10 17:28:07.620112

"""

from alembic import op

import sqlalchemy as sa

from sqlalchemy_utils import ChoiceType
from sqlalchemy_utils import URLType

from yui.apps.info.saomd.models import Server
from yui.apps.info.toranoana.models import Stock
from yui.apps.info.toranoana.models import Target
from yui.orm.types import JSONType
from yui.orm.types import TimezoneType

# revision identifiers, used by Alembic.
revision = '0e7bdd5c7473'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'event_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ts', sa.String(), nullable=False),
        sa.Column('channel', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'json_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('body', JSONType(), nullable=True),
        sa.Column(
            'created_datetime', sa.DateTime(timezone=True), nullable=False
        ),
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
        sa.Column(
            'created_datetime', sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column('created_timezone', TimezoneType(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'rss_feed_url',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('channel', sa.String(), nullable=False),
        sa.Column(
            'updated_datetime', sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column('updated_timezone', TimezoneType(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'saomd_notice',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('notice_id', sa.Integer(), nullable=False),
        sa.Column(
            'server', ChoiceType(Server, impl=sa.Integer()), nullable=False
        ),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('duration', sa.String(), nullable=True),
        sa.Column('short_description', sa.String(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'toranoana_author',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'toranoana_character',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('name_ko', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'toranoana_circle',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'toranoana_coupling',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('name_ko', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'toranoana_genre',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('name_ko', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'toranoana_tag',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('name_ko', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'toranoana_item',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('image_url', URLType(), nullable=False),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column(
            'stock', ChoiceType(Stock, impl=sa.Integer()), nullable=False
        ),
        sa.Column('genre_id', sa.Integer(), nullable=False),
        sa.Column(
            'male_target',
            ChoiceType(Target, impl=sa.Integer()),
            nullable=False,
        ),
        sa.Column(
            'female_target',
            ChoiceType(Target, impl=sa.Integer()),
            nullable=False,
        ),
        sa.Column(
            'checked_datetime', sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column('checked_timezone', TimezoneType(), nullable=True),
        sa.Column(
            'updated_datetime', sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column('updated_timezone', TimezoneType(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ['genre_id'],
            ['toranoana_genre.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
    )
    op.create_table(
        'toranoana_watch',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('print_target_id', sa.String(), nullable=False),
        sa.Column('genre_id', sa.Integer(), nullable=True),
        sa.Column(
            'male', ChoiceType(Target, impl=sa.Integer()), nullable=False
        ),
        sa.Column(
            'female', ChoiceType(Target, impl=sa.Integer()), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ['genre_id'],
            ['toranoana_genre.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'toranoana_itemauthor',
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['author_id'],
            ['toranoana_author.id'],
        ),
        sa.ForeignKeyConstraint(
            ['item_id'],
            ['toranoana_item.id'],
        ),
        sa.PrimaryKeyConstraint('item_id', 'author_id'),
    )
    op.create_table(
        'toranoana_itemcharacter',
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['character_id'],
            ['toranoana_character.id'],
        ),
        sa.ForeignKeyConstraint(
            ['item_id'],
            ['toranoana_item.id'],
        ),
        sa.PrimaryKeyConstraint('item_id', 'character_id'),
    )
    op.create_table(
        'toranoana_itemcircle',
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('circle_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['circle_id'],
            ['toranoana_circle.id'],
        ),
        sa.ForeignKeyConstraint(
            ['item_id'],
            ['toranoana_item.id'],
        ),
        sa.PrimaryKeyConstraint('item_id', 'circle_id'),
    )
    op.create_table(
        'toranoana_itemcoupling',
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('coupling_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['coupling_id'],
            ['toranoana_coupling.id'],
        ),
        sa.ForeignKeyConstraint(
            ['item_id'],
            ['toranoana_item.id'],
        ),
        sa.PrimaryKeyConstraint('item_id', 'coupling_id'),
    )
    op.create_table(
        'toranoana_itemtag',
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['item_id'],
            ['toranoana_item.id'],
        ),
        sa.ForeignKeyConstraint(
            ['tag_id'],
            ['toranoana_tag.id'],
        ),
        sa.PrimaryKeyConstraint('item_id', 'tag_id'),
    )


def downgrade():
    op.drop_table('toranoana_itemtag')
    op.drop_table('toranoana_itemcoupling')
    op.drop_table('toranoana_itemcircle')
    op.drop_table('toranoana_itemcharacter')
    op.drop_table('toranoana_itemauthor')
    op.drop_table('toranoana_watch')
    op.drop_table('toranoana_item')
    op.drop_table('toranoana_tag')
    op.drop_table('toranoana_genre')
    op.drop_table('toranoana_coupling')
    op.drop_table('toranoana_circle')
    op.drop_table('toranoana_character')
    op.drop_table('toranoana_author')
    op.drop_table('saomd_notice')
    op.drop_table('rss_feed_url')
    op.drop_table('memo')
    op.drop_table('json_cache')
    op.drop_table('event_log')
