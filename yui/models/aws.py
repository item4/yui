from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column
from sqlalchemy.types import Boolean, DateTime, Float, Integer, String

from ..orm import Base
from ..util import tz_none_to_kst, tz_none_to_utc


class AWS(Base):
    """AWS Weather record."""

    __tablename__ = 'aws'

    id = Column(Integer, nullable=False, primary_key=True)

    # 지역명
    name = Column(String(15), nullable=False)

    # 고도
    height = Column(Integer, nullable=False)

    # 강수
    is_raining = Column(Boolean)

    # 강수15
    rain15 = Column(Float)

    # 강수60
    rain60 = Column(Float)

    # 강수6H
    rain6h = Column(Float)

    # 강수12H
    rain12h = Column(Float)

    # 일강수
    rainday = Column(Float)

    # 기온
    temperature = Column(Float)

    # 풍향1
    wind_direction1 = Column(String(3))

    # 풍속1
    wind_speed1 = Column(Float)

    # 풍향10
    wind_direction10 = Column(String(3))

    # 풍속10
    wind_speed10 = Column(Float)

    # 습도
    humidity = Column(Integer)

    # 해면기압
    pressure = Column(Float)

    # 위치
    location = Column(String(50))

    # 관측 시간
    observed_datetime = Column(DateTime(timezone=True), nullable=False)

    @hybrid_property
    def observed_at(self):
        """관측 시간."""

        return tz_none_to_kst(self.observed_datetime)

    @observed_at.setter
    def observed_at(self, value):
        """관측 시간."""

        self.observed_datetime = tz_none_to_utc(value)
