"""Drop toranoana

Revision ID: 75c91e7af605
Revises: fbbdf21dcebe
Create Date: 2022-01-08 14:41:53.252409

"""
import enum

from alembic import op

import sqlalchemy as sa

from sqlalchemy_utils.types import ChoiceType
from sqlalchemy_utils.types import URLType

from yui.orm.types import TimezoneType


# revision identifiers, used by Alembic.
revision = "75c91e7af605"
down_revision = "fbbdf21dcebe"
branch_labels = None
depends_on = None


@enum.unique
class Stock(enum.IntEnum):
    """Stock of Item."""

    soldout = 0
    few = 1
    ok = 2


@enum.unique
class Target(enum.IntEnum):
    """Target"""

    nobody = 0
    common = 1
    adult = 2
    wildcard = 3


def upgrade():
    op.drop_table("toranoana_itemauthor")
    op.drop_table("toranoana_itemcharacter")
    op.drop_table("toranoana_itemcircle")
    op.drop_table("toranoana_itemcoupling")
    op.drop_table("toranoana_itemtag")
    op.drop_table("toranoana_author")
    op.drop_table("toranoana_character")
    op.drop_table("toranoana_circle")
    op.drop_table("toranoana_coupling")
    op.drop_table("toranoana_tag")
    op.drop_table("toranoana_item")
    op.drop_table("toranoana_watch")
    op.drop_table("toranoana_genre")


def downgrade():
    op.create_table(
        "toranoana_author",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "toranoana_character",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("name_ko", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "toranoana_circle",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "toranoana_coupling",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("name_ko", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "toranoana_genre",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("name_ko", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "toranoana_tag",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("name_ko", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "toranoana_item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("image_url", URLType(), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column(
            "stock", ChoiceType(Stock, impl=sa.Integer()), nullable=False
        ),
        sa.Column("genre_id", sa.Integer(), nullable=False),
        sa.Column(
            "male_target",
            ChoiceType(Target, impl=sa.Integer()),
            nullable=False,
        ),
        sa.Column(
            "female_target",
            ChoiceType(Target, impl=sa.Integer()),
            nullable=False,
        ),
        sa.Column(
            "checked_datetime", sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column("checked_timezone", TimezoneType(), nullable=True),
        sa.Column(
            "updated_datetime", sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column("updated_timezone", TimezoneType(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["genre_id"],
            ["toranoana_genre.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "toranoana_watch",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("print_target_id", sa.String(), nullable=False),
        sa.Column("genre_id", sa.Integer(), nullable=True),
        sa.Column(
            "male", ChoiceType(Target, impl=sa.Integer()), nullable=False
        ),
        sa.Column(
            "female", ChoiceType(Target, impl=sa.Integer()), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["genre_id"],
            ["toranoana_genre.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "toranoana_itemauthor",
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["toranoana_author.id"],
        ),
        sa.ForeignKeyConstraint(
            ["item_id"],
            ["toranoana_item.id"],
        ),
        sa.PrimaryKeyConstraint("item_id", "author_id"),
    )
    op.create_table(
        "toranoana_itemcharacter",
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("character_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["character_id"],
            ["toranoana_character.id"],
        ),
        sa.ForeignKeyConstraint(
            ["item_id"],
            ["toranoana_item.id"],
        ),
        sa.PrimaryKeyConstraint("item_id", "character_id"),
    )
    op.create_table(
        "toranoana_itemcircle",
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("circle_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["circle_id"],
            ["toranoana_circle.id"],
        ),
        sa.ForeignKeyConstraint(
            ["item_id"],
            ["toranoana_item.id"],
        ),
        sa.PrimaryKeyConstraint("item_id", "circle_id"),
    )
    op.create_table(
        "toranoana_itemcoupling",
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("coupling_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["coupling_id"],
            ["toranoana_coupling.id"],
        ),
        sa.ForeignKeyConstraint(
            ["item_id"],
            ["toranoana_item.id"],
        ),
        sa.PrimaryKeyConstraint("item_id", "coupling_id"),
    )
    op.create_table(
        "toranoana_itemtag",
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["item_id"],
            ["toranoana_item.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["toranoana_tag.id"],
        ),
        sa.PrimaryKeyConstraint("item_id", "tag_id"),
    )
