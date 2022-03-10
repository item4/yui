import datetime
import re
from collections.abc import Callable
from collections.abc import Sequence
from decimal import Decimal
from typing import Any
from typing import TypeVar

from .types.namespace import channel_id_convert
from .types.namespace import name_convert
from .types.namespace import user_id_convert
from .types.namespace import user_name_convert

T = TypeVar('T', int, float, Decimal)

DATE_FORMAT_RE = re.compile(
    r'(\d{4})\s*[-\.년]?\s*(\d{1,2})\s*[-\.월]?\s*(\d{1,2})\s*일?'
)


def str_to_date(
    fallback: Callable[[], datetime.date] | None = None,
) -> Callable[[str], Any]:
    """Helper to make date object from given string."""

    def callback(value: str) -> datetime.date:
        match = DATE_FORMAT_RE.match(value)
        if match:
            try:
                return datetime.date(
                    int(match.group(1)),
                    int(match.group(2)),
                    int(match.group(3)),
                )
            except ValueError:
                if fallback is None:
                    raise
                else:
                    return fallback()
        raise ValueError('Incorrect date string')

    return callback


def _extract(text: str) -> str:
    if text.startswith('<') and text.endswith('>'):
        if '|' in text:
            return text[1:-1].split('|', 1)[1]
        else:
            return text[1:-1]
    return text


def extract_url(text: str) -> str:
    """Helper to extract URL from given text."""

    return _extract(text)


def get_channel(text: str):
    """Helper to get Channel from given text."""

    result = _extract(text)

    if result.startswith('#'):
        result = result[1:]
    try:
        return channel_id_convert(result)
    except KeyError:
        try:
            return name_convert(result)
        except KeyError:
            raise ValueError('Given channel was not found')


def get_user(text: str):
    """Helper to get User from given text."""

    result = _extract(text)

    if result.startswith('@'):
        result = result[1:]
    try:
        return user_id_convert(result)
    except KeyError:
        try:
            return user_name_convert(result)
        except KeyError:
            raise ValueError('Given user was not found')


def enum_getitem(
    cls,
    *,
    fallback: str | None = None,
) -> Callable[[str], Any]:
    """
    Helper to transform item to enum object by name from given enum

    .. warning::
       Do not use it in type annotation or `type_` value.

       .. sourcecode:: python
          @box.command('ok')
          @option('--key', transform_func=enum_getitem(KeyEnum))
          async def ok(key: KeyEnum):  # It's OK
              pass

          @box.command('no')
          @option('--key')
          async def no(key: enum_getitem(KeyEnum)):  # Do not this
              pass

    """

    def callback(keyword: str):
        try:
            return cls[keyword]
        except KeyError as e:
            if fallback:
                return cls[fallback]
            else:
                raise ValueError(e)

    return callback


def choice(
    items: Sequence[str],
    *,
    fallback: str | None = None,
    case_insensitive: bool = False,
    case: str | None = None,
) -> Callable[[str], str]:
    """
    Helper to constraint value to in items or raise error.

    .. warning::
       Do not use it in type annotation or `type_` value.

       .. sourcecode:: python
          @box.command('ok')
          @option('--key', transform_func=choice('A', 'B'))
          async def ok(key: str):  # It's OK
              pass

          @box.command('no')
          @option('--key')
          async def no(key: choice('A', 'B')):  # Do not this
              pass

    """

    def transform_case(val):
        if case is not None and hasattr(val, case):
            return getattr(val, case)()
        return val

    def callback(val):
        if case_insensitive:
            if val.lower() in map(lambda x: x.lower(), items):
                return transform_case(val)
            else:
                if fallback is not None:
                    return transform_case(fallback)
                else:
                    raise ValueError('given value is not in allowed cases')
        else:
            if val in items:
                return transform_case(val)
            else:
                if fallback is not None:
                    return transform_case(fallback)
                else:
                    raise ValueError('given value is not in allowed cases')

    return callback


def value_range(
    start: T,
    end: T,
    *,
    autofix: bool = False,
) -> Callable[[T], T]:
    """
    Helper to constraint value to in range or raise error.

    .. warning::
       Do not use it in type annotation or `type_` value.

       .. sourcecode:: python
          @box.command('ok')
          @option('--key', transform_func=value_range(1, 10))
          async def ok(key: int):  # It's OK
              pass

          @box.command('no')
          @option('--key')
          async def no(key: value_range(1, 10)):  # Do not this
              pass

    """

    def callback(val: T) -> T:
        if start <= val <= end:
            return val
        elif start > val:
            if autofix:
                return start
            else:
                raise ValueError('given value is too small.')
        else:
            if autofix:
                return end
            else:
                raise ValueError('given value is too big.')

    return callback
