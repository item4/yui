import datetime
from typing import Optional

from dateutil.tz import UTC
from dateutil.tz import tzfile

from sqlalchemy.ext.hybrid import Comparator
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column
from sqlalchemy.sql.expression import func
from sqlalchemy.types import DateTime

from .types import TimezoneType


def extract_timezone_name(tz) -> str:
    if isinstance(tz, str) and '/' in tz:
        return '/'.join(tz.split('/')[-2:])
    return tz


class DateTimeAtComparator(Comparator):
    def __init__(self, *args):
        length = len(args)
        if length == 1:
            maybe_dt = args[0]
            maybe_tz = None
        elif length:
            maybe_dt = args[0]
            maybe_tz = args[1]
        else:
            raise RuntimeError

        if isinstance(maybe_dt, DateTimeAtComparator):
            self.dt = maybe_dt.dt
            self.tz = maybe_dt.tz
        elif isinstance(maybe_dt, datetime.datetime):
            if maybe_tz is None:
                maybe_tz = maybe_dt.tzinfo
                maybe_dt = maybe_dt.astimezone(UTC)

            self.dt = maybe_dt.isoformat()

            if maybe_tz == UTC:
                self.tz = 'UTC'
            elif isinstance(maybe_tz, tzfile):
                self.tz = maybe_tz._filename
            elif isinstance(maybe_tz, datetime.tzinfo):
                self.tz = maybe_tz.tzname(maybe_dt)
            elif isinstance(maybe_tz, str):
                self.tz = maybe_tz
            else:
                raise RuntimeError
        elif isinstance(maybe_dt, str):
            self.dt = maybe_dt

            if maybe_tz == UTC:
                self.tz = 'UTC'
            elif isinstance(maybe_tz, tzfile):
                self.tz = maybe_tz._filename
            elif isinstance(maybe_tz, str):
                self.tz = maybe_tz
            else:
                raise RuntimeError
        else:
            self.dt = maybe_dt
            self.tz = maybe_tz

        self.tz = extract_timezone_name(self.tz)

    def operate(self, op, *other, **kwargs):
        other = [
            func.timezone(x.tz, x.dt)
            for x in [
                o
                if isinstance(o, DateTimeAtComparator)
                else DateTimeAtComparator(o)
                for o in other
            ]
        ]
        other.insert(0, func.timezone(self.tz, self.dt))
        return op(*other, **kwargs)

    def __clause_element__(self):
        return func.timezone(self.tz, self.dt)


def DateTimeAtColumn(prefix: str) -> hybrid_property:
    datetime_key = f'{prefix}_datetime'
    timezone_key = f'{prefix}_timezone'

    def getter(self) -> Optional[datetime.datetime]:
        dt: Optional[datetime.datetime] = getattr(self, datetime_key)
        tz: Optional[datetime.tzinfo] = getattr(self, timezone_key)
        if dt and tz:
            return dt.astimezone(tz)
        return dt

    def setter(self, dt: datetime.datetime):
        setattr(self, timezone_key, dt.tzinfo)
        setattr(self, datetime_key, dt.astimezone(UTC))

    def custom_comparator(cls):
        return DateTimeAtComparator(
            getattr(cls, datetime_key),
            getattr(cls, timezone_key),
        )

    return hybrid_property(
        fget=getter,
        fset=setter,
        custom_comparator=custom_comparator,
    )


def DateTimeColumn(nullable: bool = True, *args, **kwargs):
    return Column(DateTime(timezone=True), nullable=nullable, *args, **kwargs)


def TimezoneColumn(nullable: bool = True, *args, **kwargs):
    return Column(TimezoneType(), nullable=nullable, *args, **kwargs)
