from decimal import Decimal


from typing import Optional, Sequence, Type

__all__ = 'decimal_range', 'float_range', 'int_range'


def choice(
    cases: Sequence[str],
    *,
    fallback: Optional[str]=None,
    case_insensitive: bool=False
) -> Type[str]:
    """Helper for constraint input value must be in cases."""

    class _Str(str):

        def __new__(cls, *args, **kwargs) -> str:  # type: ignore
            snew = super(_Str, cls).__new__
            val = snew(cls, *args, **kwargs)  # type: ignore

            if case_insensitive:
                if val.lower() in map(lambda x: x.lower(), cases):
                    return val
                else:
                    if fallback is not None:
                        return fallback
                    else:
                        raise ValueError('given value is not in allowed cases')
            else:
                if val in cases:
                    return val
                else:
                    if fallback is not None:
                        return fallback
                    else:
                        raise ValueError('given value is not in allowed cases')

    return _Str


def decimal_range(
    start: Decimal,
    end: Decimal,
    *,
    autofix: bool=False
) -> Type[Decimal]:
    """Helper for constraint range of decimal value."""

    class _Decimal(Decimal):

        def __new__(cls, *args, **kwargs) -> Decimal:  # type: ignore
            snew = super(_Decimal, cls).__new__
            val = snew(cls, *args, **kwargs)  # type: ignore

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

        def __new__(cls, *args, **kwargs) -> float:  # type: ignore
            snew = super(_Float, cls).__new__
            val = snew(cls, *args, **kwargs)  # type: ignore

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

        def __new__(cls, *args, **kwargs) -> int:  # type: ignore
            snew = super(_Int, cls).__new__
            val = snew(cls, *args, **kwargs)  # type: ignore

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
