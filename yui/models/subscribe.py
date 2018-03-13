import calendar
import datetime

import pytz

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, Integer, String, Text

import tzlocal

from .type import TimezoneType
from ..orm import Base


class RssFeedSub(Base):
    """RSS Feed Subscribe"""

    __tablename__ = 'feed'

    id = Column(Integer, primary_key=True)

    url = Column(String, nullable=False)

    channel = Column(String, nullable=False)

    updated_at = Column(DateTime(timezone=True), nullable=False)

    updated_datetime = Column(DateTime(timezone=False), nullable=False)
    updated_timezone = Column(TimezoneType())

    @hybrid_property
    def updated_at(self):
        if self.updated_timezone:
            return self.updated_timezone.localize(self.updated_datetime)
        else:
            return self.updated_datetime

    @updated_at.setter  # type: ignore
    def updated_at(self, dt: datetime.datetime):
        if dt.tzinfo is pytz.UTC:
            d = datetime.datetime.fromtimestamp(
                calendar.timegm(dt.timetuple())
            )
            self.updated_datetime = d - tzlocal.get_localzone().utcoffset(d)
            self.updated_timezone = pytz.UTC
        else:
            self.updated_timezone = dt.tzinfo
            self.updated_datetime = dt.replace(tzinfo=None)


class SiteSub(Base):
    """Site diff Subscribe"""

    __tablename__ = 'site_sub'

    id = Column(Integer, primary_key=True)

    url = Column(String, nullable=False)

    user = Column(String, nullable=False)

    body = Column(Text)
