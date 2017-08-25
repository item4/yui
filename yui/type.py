from decimal import Decimal

from typing import Generic, Type, TypeVar

__all__ = 'DecimalRange', 'FloatRange', 'IntRange', 'Range'

T = TypeVar('T', int, float, Decimal)


class Range(Generic[T]):
    """Range."""

    def __init__(
        self,
        type: Type[T],
        min: T,
        max: T,
        *,
        autofix: bool=False
    ) -> None:
        """Initialize"""

        self.type: Type[T] = type

        self.min: T = min
        self.max: T = max
        self.autofix: bool = autofix

    def __call__(self, value: str) -> T:

        val = self.type(value)
        if self.min <= val <= self.max:
            return val
        elif self.min > val:
            if self.autofix:
                return self.min
            else:
                raise ValueError('given value is too small.')
        else:
            if self.autofix:
                return self.max
            else:
                raise ValueError('given value is too big.')


class DecimalRange(Range[Decimal]):
    """Shortcut of Range[Decimal](Decimal, ...)"""

    def __init__(
        self,
        min: Decimal,
        max: Decimal,
        *,
        autofix: bool=False
    ) -> None:
        super(DecimalRange, self).__init__(Decimal, min, max, autofix=autofix)


class FloatRange(Range[float]):
    """Shortcut of Range[float](float, ...)"""

    def __init__(self, min: float, max: float, *, autofix: bool=False) -> None:
        super(FloatRange, self).__init__(float, min, max, autofix=autofix)


class IntRange(Range[int]):
    """Shortcut of Range[int](int, ...)"""

    def __init__(self, min: int, max: int, *, autofix: bool=False) -> None:
        super(IntRange, self).__init__(int, min, max, autofix=autofix)
