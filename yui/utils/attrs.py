import datetime
from functools import partial
from typing import TYPE_CHECKING
from typing import TypeVar
from typing import get_args

import attrs

from .datetime import fromtimestamp

if TYPE_CHECKING:
    from attr import AttrsInstance
else:
    AttrsInstance = None


_C = TypeVar("_C", bound=AttrsInstance)


def make_instance(
    cls: type[_C],
    **kwargs,
) -> _C:
    expected_attrs = {x.name for x in attrs.fields(cls)}
    actual_attrs = set(kwargs.keys())
    for key in actual_attrs - expected_attrs:
        del kwargs[key]
    return cls(**kwargs)


def _attrs_converter(t):
    def innner(value):
        if value:
            try:
                return make_instance(t, **value)
            except TypeError:
                return value
        return None

    return innner


def _datetime_converter(value):
    if value:
        return fromtimestamp(value)
    return None


def _field_transformer(cls, fields):
    results = []
    for field in fields:
        t = field.type
        if get_args(t):
            t = get_args(t)[0]
        if field.converter is None:
            if hasattr(t, "__attrs_attrs__"):
                results.append(field.evolve(converter=_attrs_converter(t)))
            elif t is datetime.datetime:
                results.append(field.evolve(converter=_datetime_converter))
            else:
                results.append(field)
        else:
            results.append(field)
    return results


define = partial(
    attrs.define,
    kw_only=True,
    field_transformer=_field_transformer,
)
channel_id_field = partial(attrs.field, repr=True)
user_id_field = partial(attrs.field, repr=True)
name_field = partial(attrs.field, repr=True)
ts_field = partial(attrs.field, repr=True)
field = partial(attrs.field, default=None, repr=False)
