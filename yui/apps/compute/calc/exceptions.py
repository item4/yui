import ast


class BadSyntax(Exception):
    pass


class RuntimeErrorMixin:
    message: str

    def __str__(self) -> str:
        return self.message


class RuntimeSyntaxError(RuntimeErrorMixin, SyntaxError):
    pass


class RuntimeTypeError(RuntimeErrorMixin, TypeError):
    pass


class UnavailableSyntaxError(RuntimeSyntaxError):
    def __init__(self, node: ast.AST, *args) -> None:
        super().__init__(*args)
        self.message = (
            f"Evaluation of {type(node).__name__!r} node is unavailable."
        )


class NotIterableError(RuntimeTypeError):
    def __init__(self, value, *args) -> None:
        super().__init__(*args)
        self.message = f"{type(value).__name__!r} object is not iterable"


class NotSubscriptableError(RuntimeTypeError):
    def __init__(self, value, *args) -> None:
        super().__init__(*args)
        self.message = f"{type(value).__name__!r} object is not subscriptable"
