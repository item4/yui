from types import SimpleNamespace

__all__ = 'Namespace',


class Namespace(SimpleNamespace):
    """Typed Namespace."""

    def __init__(self, **kwargs) -> None:
        from ...utils.cast import cast  # circular dependency

        annotations = {}
        for cls in self.__class__.mro():
            try:
                annotations.update({
                    k: v for k, v in cls.__annotations__.items()
                    if not k.startswith('_')
                })
            except AttributeError:
                break

        for k, v in kwargs.items():
            t = annotations.get(k)
            if t:
                kwargs[k] = cast(t, v)

        super(Namespace, self).__init__(**kwargs)  # type: ignore
