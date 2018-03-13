import calendar
import datetime

import pytz

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, Integer, String, Text

import tzlocal

from .type import JSONType, TimezoneType
from ..orm import Base


class WebPageCache(Base):
    """Cache for web page"""

    __tablename__ = 'web_page_cache'

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)

    body = Column(Text)

    created_datetime = Column(DateTime(timezone=False), nullable=False)
    created_timezone = Column(TimezoneType())

    @hybrid_property
    def created_at(self):
        if self.created_timezone:
            return self.created_timezone.localize(self.created_datetime)
        else:
            return self.created_datetime

    @created_at.setter  # type: ignore
    def created_at(self, dt: datetime.datetime):
        if dt.tzinfo is pytz.UTC:
            d = datetime.datetime.fromtimestamp(
                calendar.timegm(dt.timetuple())
            )
            self.created_datetime = d - tzlocal.get_localzone().utcoffset(d)
            self.created_timezone = pytz.UTC
        else:
            self.created_timezone = dt.tzinfo
            self.created_datetime = dt.replace(tzinfo=None)


class JSONCache(Base):

    __tablename__ = 'json_cache'

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)

    body = Column(JSONType)

    created_datetime = Column(DateTime(timezone=False), nullable=False)
    created_timezone = Column(TimezoneType())

    @hybrid_property
    def created_at(self):
        if self.created_timezone:
            return self.created_timezone.localize(self.created_datetime)
        else:
            return self.created_datetime

    @created_at.setter  # type: ignore
    def created_at(self, dt: datetime.datetime):
        if dt.tzinfo is pytz.UTC:
            d = datetime.datetime.fromtimestamp(
                calendar.timegm(dt.timetuple())
            )
            self.created_datetime = d - tzlocal.get_localzone().utcoffset(d)
            self.created_timezone = pytz.UTC
        else:
            self.created_timezone = dt.tzinfo
            self.created_datetime = dt.replace(tzinfo=None)
