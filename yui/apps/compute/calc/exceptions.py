class BadSyntax(Exception):
    pass


class RuntimeTypeError(TypeError):
    message: str

    def __str__(self) -> str:
        return self.message


class NotIterableError(RuntimeTypeError):
    def __init__(self, value, *args) -> None:
        super().__init__(*args)
        self.message = f"{type(value).__name__!r} object is not iterable"


class NotSubscriptableError(RuntimeTypeError):
    def __init__(self, value, *args) -> None:
        super().__init__(*args)
        self.message = f"{type(value).__name__!r} object is not subscriptable"
