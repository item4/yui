from typing import NoReturn


class BadSyntax(Exception):
    pass


class RuntimeSyntaxError(SyntaxError):
    pass


class RuntimeTypeError(TypeError):
    pass


class UnavailableSyntaxError(RuntimeSyntaxError):
    pass


class AsyncComprehensionError(RuntimeSyntaxError):
    pass


class NotCallableError(RuntimeTypeError):
    pass


class NotIterableError(RuntimeTypeError):
    pass


class NotSubscriptableError(RuntimeTypeError):
    pass


class CallableKeywordsError(RuntimeTypeError):
    pass


class UnavailableTypeError(RuntimeTypeError):
    pass


def error_maker(
    exc_cls: type[RuntimeSyntaxError] | type[RuntimeTypeError],
    *args,
) -> NoReturn:
    if exc_cls is UnavailableSyntaxError:
        x = args[0]
        error = f"Evaluation of {type(x).__name__!r} node is unavailable."
        raise UnavailableSyntaxError(error)

    if exc_cls is AsyncComprehensionError:
        x = args[0]
        error = f"Async syntax with {type(x).__name__!r} node is unavailable."
        raise AsyncComprehensionError(error)

    if exc_cls is NotCallableError:
        x = args[0]
        error = f"{type(x).__name__!r} object is not callable"
        raise NotCallableError(error)

    if exc_cls is NotIterableError:
        x = args[0]
        error = f"{type(x).__name__!r} object is not iterable"
        raise NotIterableError(error)

    if exc_cls is NotSubscriptableError:
        x = args[0]
        error = f"{type(x).__name__!r} object is not subscriptable"
        raise NotSubscriptableError(error)

    if exc_cls is CallableKeywordsError:
        error = "keywords must be strings"
        raise CallableKeywordsError(error)

    if exc_cls is UnavailableTypeError:
        x = args[0]
        error = f"{type(x).__name__!r} type is unavailable"
        raise UnavailableTypeError(error)

    error = "Unknown exception"  # pragma: no cover
    raise TypeError(error)  # pragma: no cover
