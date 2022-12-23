from decimal import Decimal


def shorten(input_value: int | float) -> str:
    decimal_string = (
        str(Decimal(format(input_value, "f")).quantize(Decimal("1.00")))
        if input_value
        else "0"
    )
    return (
        decimal_string.rstrip("0").rstrip(".")
        if "." in decimal_string
        else decimal_string
    )
