import calendar
import datetime

import pytz

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column
from sqlalchemy.types import Boolean, DateTime, Float, Integer, String

import tzlocal

from .type import TimezoneType
from ..orm import Base


class AWS(Base):
    """AWS Weather record."""

    __tablename__ = 'aws'

    id = Column(Integer, nullable=False, primary_key=True)

    # 지역명
    name = Column(String, nullable=False)

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
    wind_direction1 = Column(String)

    # 풍속1
    wind_speed1 = Column(Float)

    # 풍향10
    wind_direction10 = Column(String)

    # 풍속10
    wind_speed10 = Column(Float)

    # 습도
    humidity = Column(Integer)

    # 해면기압
    pressure = Column(Float)

    # 위치
    location = Column(String)

    # 관측 시간
    observed_datetime = Column(DateTime(timezone=False), nullable=False)
    observed_timezone = Column(TimezoneType())

    @hybrid_property
    def observed_at(self):
        if self.observed_timezone:
            return self.observed_timezone.localize(self.observed_datetime)
        else:
            return self.observed_datetime

    @observed_at.setter  # type: ignore
    def observed_at(self, dt: datetime.datetime):
        if dt.tzinfo is pytz.UTC:
            d = datetime.datetime.fromtimestamp(
                calendar.timegm(dt.timetuple())
            )
            self.observed_datetime = d - tzlocal.get_localzone().utcoffset(d)
            self.observed_timezone = pytz.UTC
        else:
            self.observed_timezone = dt.tzinfo
            self.observed_datetime = dt.replace(tzinfo=None)
