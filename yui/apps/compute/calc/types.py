import decimal
from collections.abc import Iterable
from typing import Final
from typing import Protocol
from typing import TypeGuard
from typing import runtime_checkable

TO_DECIMAL: Final[tuple[type, ...]] = (int, float)


class PLACEHOLDER:
    pass


class Decimal(decimal.Decimal):
    def __abs__(self):
        return Decimal(super().__abs__())

    def __add__(self, other, /):
        if isinstance(other, TO_DECIMAL):
            other = Decimal(other)
        return Decimal(super().__add__(other))

    def __divmod__(self, other, /):
        if isinstance(other, TO_DECIMAL):
            other = Decimal(other)
        quotient, remainder = super().__divmod__(other)
        return Decimal(quotient), Decimal(remainder)

    def __floordiv__(self, other, /):
        if isinstance(other, TO_DECIMAL):
            other = Decimal(other)
        return Decimal(super().__floordiv__(other))

    def __mod__(self, other, /):
        if isinstance(other, TO_DECIMAL):
            other = Decimal(other)
        return Decimal(super().__mod__(other))

    def __mul__(self, other, /):
        if isinstance(other, TO_DECIMAL):
            other = Decimal(other)
        return Decimal(super().__mul__(other))

    def __neg__(self):
        return Decimal(super().__neg__())

    def __pos__(self):
        return Decimal(super().__pos__())

    def __pow__(
        self,
        other,
        mod=None,
        /,
    ):
        if isinstance(other, TO_DECIMAL):
            other = Decimal(other)
        if isinstance(mod, TO_DECIMAL):
            mod = Decimal(mod)
        return Decimal(super().__pow__(other, mod))

    def __radd__(self, other, /):
        if isinstance(other, TO_DECIMAL):
            other = Decimal(other)
        return Decimal(other.__add__(self))

    def __rdivmod__(self, other, /):
        if isinstance(other, TO_DECIMAL):
            other = Decimal(other)
        quotient, remainder = other.__divmod__(self)
        return Decimal(quotient), Decimal(remainder)

    def __rfloordiv__(self, other, /):
        if isinstance(other, TO_DECIMAL):
            other = Decimal(other)
        return Decimal(other.__floordiv__(self))

    def __rmod__(self, other, /):
        if isinstance(other, TO_DECIMAL):
            other = Decimal(other)
        return Decimal(other.__mod__(self))

    def __rmul__(self, other, /):
        if isinstance(other, TO_DECIMAL):
            other = Decimal(other)
        return Decimal(other.__mul__(self))

    def __rsub__(self, other, /):
        if isinstance(other, TO_DECIMAL):
            other = Decimal(other)
        return Decimal(other.__sub__(self))

    def __rtruediv__(self, other, /):
        if isinstance(other, TO_DECIMAL):
            other = Decimal(other)
        return Decimal(other.__truediv__(self))

    def __sub__(self, other, /):
        if isinstance(other, TO_DECIMAL):
            other = Decimal(other)
        return Decimal(super().__sub__(other))

    def __truediv__(self, other, /):
        if isinstance(other, TO_DECIMAL):
            other = Decimal(other)
        return Decimal(super().__truediv__(other))

    def __rpow__(self, other, context=None, /):
        if isinstance(other, TO_DECIMAL):
            other = Decimal(other)
        return Decimal(other.__pow__(self))


@runtime_checkable
class SupportsGetSubscript(Protocol):
    def __getitem__(self, key, default=None): ...


@runtime_checkable
class SupportsSubscript(SupportsGetSubscript, Protocol):
    def __setitem__(self, key, value): ...
    def __delitem__(self, key): ...


def is_iterable(x) -> TypeGuard[Iterable]:
    return isinstance(x, Iterable)


def is_get_subscriptable(x) -> TypeGuard[SupportsGetSubscript]:
    return isinstance(x, SupportsGetSubscript)


def is_subscriptable(x) -> TypeGuard[SupportsSubscript]:
    return isinstance(x, SupportsSubscript)
