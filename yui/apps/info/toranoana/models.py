import enum
from typing import Dict

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Boolean
from sqlalchemy.types import Integer
from sqlalchemy.types import String

from sqlalchemy_utils.types import ChoiceType
from sqlalchemy_utils.types import URLType

from ....orm import Base
from ....orm.columns import DateTimeAtColumn
from ....orm.columns import DateTimeColumn
from ....orm.columns import TimezoneColumn


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


STOCK_LABEL: Dict[Stock, str] = {
    Stock.soldout: '재고 없음',
    Stock.few: '재고 조금 남음',
    Stock.ok: '재고 있음',
}
TARGET_LABEL: Dict[Target, str] = {
    Target.nobody: '구독안함',
    Target.common: '전연령',
    Target.adult: '성인전용',
    Target.wildcard: '전연령+성인전용',
}


class Genre(Base):
    """Genre."""

    __tablename__ = 'toranoana_genre'

    id = Column(Integer, primary_key=True)

    code = Column(String, nullable=False)

    name = Column(String, nullable=False)

    name_ko = Column(String)

    @hybrid_property
    def easy_name(self) -> str:
        return self.name_ko or self.name


class Watch(Base):
    """Watch target and user."""

    __tablename__ = 'toranoana_watch'

    id = Column(Integer, primary_key=True)

    print_target_id = Column(String, nullable=False)

    genre_id = Column(Integer, ForeignKey(Genre.id))

    genre = relationship(Genre)

    male = Column(ChoiceType(Target, impl=Integer()), nullable=False,)

    female = Column(ChoiceType(Target, impl=Integer()), nullable=False,)

    @hybrid_property
    def male_text(self) -> str:
        return TARGET_LABEL[self.male]

    @hybrid_property
    def female_text(self) -> str:
        return TARGET_LABEL[self.female]


class Tag(Base):
    """Tag"""

    __tablename__ = 'toranoana_tag'

    id = Column(Integer, primary_key=True)

    code = Column(String, nullable=False)

    name = Column(String, nullable=False)

    name_ko = Column(String)


class Author(Base):
    """Author"""

    __tablename__ = 'toranoana_author'

    id = Column(Integer, primary_key=True)

    code = Column(String, nullable=False)

    name = Column(String, nullable=False)


class Circle(Base):
    """Circle"""

    __tablename__ = 'toranoana_circle'

    id = Column(Integer, primary_key=True)

    code = Column(String, nullable=False)

    name = Column(String, nullable=False)


class Coupling(Base):
    """Coupling"""

    __tablename__ = 'toranoana_coupling'

    id = Column(Integer, primary_key=True)

    code = Column(String, nullable=False)

    name = Column(String, nullable=False)

    name_ko = Column(String)


class Character(Base):
    """Character"""

    __tablename__ = 'toranoana_character'

    id = Column(Integer, primary_key=True)

    code = Column(String, nullable=False)

    name = Column(String, nullable=False)

    name_ko = Column(String)


class Item(Base):
    """Item."""

    __tablename__ = 'toranoana_item'

    id = Column(Integer, primary_key=True)

    code = Column(String, unique=True, nullable=False)

    title = Column(String, nullable=False)

    image_url = Column(URLType(), nullable=False)

    price = Column(Integer, nullable=False)

    stock = Column(ChoiceType(Stock, impl=Integer()), nullable=False,)

    genre_id = Column(Integer, ForeignKey(Genre.id), nullable=False)

    genre = relationship(Genre)

    male_target = Column(
        ChoiceType(Target, impl=Integer()),
        nullable=False,
        default=Target.nobody,
    )

    female_target = Column(
        ChoiceType(Target, impl=Integer()),
        nullable=False,
        default=Target.nobody,
    )

    authors = relationship(
        Author, secondary='toranoana_itemauthor', backref='items',
    )

    circles = relationship(
        Circle, secondary='toranoana_itemcircle', backref='items',
    )

    tags = relationship(Tag, secondary='toranoana_itemtag', backref='items',)

    couplings = relationship(
        Coupling, secondary='toranoana_itemcoupling', backref='items',
    )

    characters = relationship(
        Character, secondary='toranoana_itemcharacter', backref='items',
    )

    checked_datetime = DateTimeColumn(nullable=False)

    checked_timezone = TimezoneColumn()

    checked_at = DateTimeAtColumn('checked')

    updated_datetime = DateTimeColumn(nullable=False)

    updated_timezone = TimezoneColumn()

    updated_at = DateTimeAtColumn('updated')

    is_deleted = Column(Boolean, default=False, nullable=False)

    @hybrid_property
    def url(self) -> str:
        if self.male_target != Target.nobody:
            return {
                Target.common: (
                    'https://ec.toranoana.shop/tora/ec/item/{code}/'
                ),
                Target.adult: 'https://ec.toranoana.jp/tora_r/ec/item/{code}/',
            }[self.male_target].format(code=self.code)

        return {
            Target.common: 'https://ec.toranoana.shop/joshi/ec/item/{code}/',
            Target.adult: 'https://ec.toranoana.jp/joshi_r/ec/item/{code}/',
        }[self.female_target].format(code=self.code)


class ItemTag(Base):
    """Item : Tag M:N"""

    __tablename__ = 'toranoana_itemtag'

    item_id = Column(Integer, ForeignKey(Item.id), primary_key=True)

    tag_id = Column(Integer, ForeignKey(Tag.id), primary_key=True)

    item = relationship(Item)

    tag = relationship(Tag)


class ItemAuthor(Base):
    """Item : Author M:N"""

    __tablename__ = 'toranoana_itemauthor'

    item_id = Column(Integer, ForeignKey(Item.id), primary_key=True)

    author_id = Column(Integer, ForeignKey(Author.id), primary_key=True)

    item = relationship(Item)

    author = relationship(Author)


class ItemCircle(Base):
    """Item : Circle M:N"""

    __tablename__ = 'toranoana_itemcircle'

    item_id = Column(Integer, ForeignKey(Item.id), primary_key=True)

    circle_id = Column(Integer, ForeignKey(Circle.id), primary_key=True)

    item = relationship(Item)

    circle = relationship(Circle)


class ItemCoupling(Base):
    """Item : Coupling M:N"""

    __tablename__ = 'toranoana_itemcoupling'

    item_id = Column(Integer, ForeignKey(Item.id), primary_key=True)

    coupling_id = Column(Integer, ForeignKey(Coupling.id), primary_key=True)

    item = relationship(Item)

    coupling = relationship(Coupling)


class ItemCharacter(Base):
    """Item : Label M:N"""

    __tablename__ = 'toranoana_itemcharacter'

    item_id = Column(Integer, ForeignKey(Item.id), primary_key=True)

    character_id = Column(Integer, ForeignKey(Character.id), primary_key=True)

    item = relationship(Item)

    character = relationship(Character)
