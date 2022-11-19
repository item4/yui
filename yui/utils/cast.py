import types
from typing import Any
from typing import TypeVar
from typing import get_args
from typing import get_origin

from ..utils.attrs import make_instance

KNOWN_TYPES = {
    bytes,
    float,
    int,
    str,
}


class CastError(Exception):
    pass


class BaseCaster:
    def check(self, t, value):
        raise NotImplementedError

    def cast(self, caster_box, t, value):
        raise NotImplementedError


class BoolCaster(BaseCaster):
    def check(self, t, value):
        return t == bool

    def cast(self, caster_box, t, value):
        return t(value)


class KnownTypesCaster(BaseCaster):
    def check(self, t, value):
        if t in KNOWN_TYPES and value is not None:
            try:
                t(value)
            except ValueError:
                return False
            return True
        return False

    def cast(self, caster_box, t, value):
        return t(value)


class TypeVarCaster(BaseCaster):
    def check(self, t, value):
        return isinstance(t, TypeVar)

    def cast(self, caster_box, t, value):
        if t.__constraints__:
            types = caster_box.sort(t.__constraints__)
            for ty in types:
                try:
                    return caster_box.cast(ty, value)
                except CastError:
                    continue
            raise CastError
        else:
            return value


class NewTypeCaster(BaseCaster):
    def check(self, t, value):
        return hasattr(t, "__supertype__")

    def cast(self, caster_box, t, value):
        return caster_box.cast(t.__supertype__, value)


class AnyCaster(BaseCaster):
    def check(self, t, value):
        return t == Any

    def cast(self, caster_box, t, value):
        return value


class UnionCaster(BaseCaster):
    def check(self, t, value):
        return get_origin(t) is types.UnionType  # noqa: E721

    def cast(self, caster_box, t, value):
        types = caster_box.sort(get_args(t), value)
        for ty in types:
            try:
                return caster_box.cast(ty, value)
            except CastError:
                continue
        raise ValueError


class TupleCaster(BaseCaster):
    def check(self, t, value):
        return t == tuple or get_origin(t) == tuple

    def cast(self, caster_box, t, value):
        if args := get_args(t):
            return tuple(caster_box.cast(ty, x) for ty, x in zip(args, value))
        else:
            return tuple(value)


class SetCaster(BaseCaster):
    def check(self, t, value):
        return t == set or get_origin(t) == set

    def cast(self, caster_box, t, value):
        if args := get_args(t):
            return {caster_box.cast(args[0], x) for x in value}
        else:
            return set(value)


class ListCaster(BaseCaster):
    def check(self, t, value):
        return t == list or get_origin(t) == list

    def cast(self, caster_box, t, value):
        if args := get_args(t):
            return [caster_box.cast(args[0], x) for x in value]
        else:
            return list(value)


class DictCaster(BaseCaster):
    def check(self, t, value):
        return t == dict or get_origin(t) == dict

    def cast(self, caster_box, t, value):
        if args := get_args(t):
            return {
                caster_box.cast(
                    args[0],
                    k,
                ): caster_box.cast(args[1], v)
                for k, v in value.items()
            }
        else:
            return dict(value)


class NoHandleCaster(BaseCaster):
    def check(self, t, value):
        try:
            return isinstance(value, t)
        except TypeError:
            return False

    def cast(self, caster_box, t, value):
        return value


class NoneTypeCaster(BaseCaster):
    def check(self, t, value):
        return t is types.NoneType  # noqa: E721

    def cast(self, caster_box, t, value):
        return None


class AttrCaster(BaseCaster):
    def check(self, t, value):
        return hasattr(t, "__attrs_attrs__")

    def cast(self, caster_box, t, value):
        return make_instance(t, **value)


class CasterBox:
    def __init__(self, caster_box: list[BaseCaster]) -> None:
        self.caster_box = caster_box

    def __call__(self, t, value):
        return self.cast(t, value)

    def sort(self, types, value):
        return [t for t in types for c in self.caster_box if c.check(t, value)]

    def cast(self, t, value):
        for caster_box in self.caster_box:
            if caster_box.check(t, value):
                return caster_box.cast(self, t, value)
        raise CastError("Can not find matching caster")


cast = CasterBox(
    [
        NoHandleCaster(),
        BoolCaster(),
        KnownTypesCaster(),
        AnyCaster(),
        TypeVarCaster(),
        NewTypeCaster(),
        UnionCaster(),
        TupleCaster(),
        SetCaster(),
        ListCaster(),
        DictCaster(),
        AttrCaster(),
    ]
)
