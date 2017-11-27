import enum
from typing import Dict

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Boolean, Float, Integer, String

from sqlalchemy_utils.types import ChoiceType

from .type import JSONType
from ..orm import Base


class ScoutType(enum.Enum):
    """Scout Type."""

    character = 1
    weapon = 2


class CostType(enum.Enum):
    """Cost Type."""

    diamond = 1
    record_crystal = 2


SCOUT_TYPE_LABEL: Dict[ScoutType, str] = {
    ScoutType.character: '캐릭터',
    ScoutType.weapon: '무기',
}

COST_TYPE_LABEL: Dict[CostType, str] = {
    CostType.record_crystal: '기록결정',
    CostType.diamond: '메모리 다이아',
}


class Player(Base):
    """SAOMD Player"""

    __tablename__ = 'saomd_player'

    id = Column(Integer, primary_key=True)

    user = Column(String(10), unique=True)

    characters = Column(JSONType, default={}, nullable=False)

    weapons = Column(JSONType, default={}, nullable=False)

    record_crystals = Column(JSONType, default={}, nullable=False)

    used_diamond = Column(Integer, default=0, nullable=False)

    release_crystal = Column(Integer, default=0, nullable=False)


class Scout(Base):
    """SAOMD Scout"""

    __tablename__ = 'saomd_scout'

    id = Column(Integer, primary_key=True)

    title = Column(String(100), nullable=False)

    type = Column(ChoiceType(ScoutType, impl=Integer()), nullable=False)

    version = Column(Integer, server_default='1', default=1, nullable=False)

    s4_units = Column(JSONType, default=[], nullable=False)

    s5_units = Column(JSONType, default=[], nullable=False)

    record_crystal = Column(JSONType, default=[], nullable=False)


class Step(Base):
    """SAOMD Step in Scout"""

    __tablename__ = 'saomd_step'

    id = Column(Integer, primary_key=True)

    name = Column(String(10), nullable=False)

    scout_id = Column(Integer, ForeignKey(Scout.id), nullable=False)

    scout = relationship(Scout)

    is_first = Column(Boolean, default=False, nullable=False)

    cost = Column(Integer, nullable=False)

    cost_type = Column(ChoiceType(CostType, impl=Integer()), nullable=False)

    count = Column(Integer, default=11, nullable=False)

    s4_fixed = Column(Integer, default=0, nullable=False)

    s5_fixed = Column(Integer, default=0, nullable=False)

    s4_chance = Column(Float, default=0.04, nullable=False)

    s5_chance = Column(Float, default=0.0, nullable=False)

    next_step_id = Column(Integer, ForeignKey('saomd_step.id'), nullable=True)

    next_step = relationship('Step', remote_side=id, post_update=True)


class PlayerScout(Base):
    """Player - Scout MtM"""

    __tablename__ = 'saomd_player_scout'

    player_id = Column(Integer, ForeignKey(Player.id), primary_key=True)

    scout_id = Column(Integer, ForeignKey(Scout.id), primary_key=True)

    next_step_id = Column(Integer, ForeignKey(Step.id))

    player = relationship(Player)

    scout = relationship(Scout)

    next_step = relationship(Step)
