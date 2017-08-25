from decimal import Decimal

from typing import Type

__all__ = 'decimal_range', 'float_range', 'int_range'


def decimal_range(
    start: Decimal,
    end: Decimal,
    *,
    autofix: bool=False
) -> Type[Decimal]:
    """Helper for constraint range of decimal value."""

    class _Decimal(Decimal):

        def __new__(cls, *args, **kwargs) -> Decimal:
            val = super(_Decimal, cls).__new__(cls, *args, **kwargs)

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

    return _Decimal


def float_range(
    start: float,
    end: float,
    *,
    autofix: bool=False
) -> Type[float]:
    """Helper for constraint range of floating point number value."""

    class _Float(float):

        def __new__(cls, *args, **kwargs) -> float:
            val = super(_Float, cls).__new__(cls, *args, **kwargs)

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

    return _Float


def int_range(start: int, end: int, *, autofix: bool=False) -> Type[int]:
    """Helper for constraint range of integer value."""

    class _Int(int):

        def __new__(cls, *args, **kwargs) -> int:
            val = super(_Int, cls).__new__(cls, *args, **kwargs)

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

    return _Int
