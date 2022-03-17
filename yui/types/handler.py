from __future__ import annotations

import inspect
from collections.abc import Callable
from collections.abc import Coroutine
from collections.abc import Mapping
from typing import Any
from typing import TYPE_CHECKING
from typing import Type
from typing import TypeAlias

import attr

if TYPE_CHECKING:
    from ..box.tasks import CronTask


HANDLER_CALL_RETURN_TYPE: TypeAlias = Coroutine[Any, Any, bool | None]
HANDLER_CALL_TYPE: TypeAlias = Callable[..., HANDLER_CALL_RETURN_TYPE]


@attr.dataclass(slots=True)
class Argument:
    """Argument"""

    name: str
    dest: str
    nargs: int
    transform_func: Callable | None
    type_: Type | None
    container_cls: Type | None
    concat: bool
    type_error: str
    count_error: str
    transform_error: str
    typing_has_container: bool = attr.ib(init=False, default=False)


@attr.dataclass(slots=True)
class Option:
    """Option"""

    key: str
    name: str
    default: Any
    dest: str
    nargs: int
    multiple: bool
    container_cls: Type | None
    required: bool
    transform_func: Callable | None
    type_: Type | None
    value: Any
    type_error: str
    count_error: str
    transform_error: str


@attr.dataclass(slots=True)
class Handler:
    f: HANDLER_CALL_TYPE
    arguments: list[Argument] = attr.ib(init=False)
    options: list[Option] = attr.ib(init=False)
    cron: CronTask | None = attr.ib(init=False, default=None)
    last_call: Any = attr.ib(init=False)
    doc: str | None = attr.ib(init=False)
    params: Mapping[str, inspect.Parameter] = attr.ib(init=False)
    is_prepared: bool = attr.ib(init=False, default=False)

    def __attrs_post_init__(self):
        self.doc = inspect.getdoc(self.f)
        self.params = inspect.signature(self.f).parameters
        self.arguments = []
        self.options = []
        self.last_call = {}

    def prepare(self):
        from ..box.utils import is_container

        for o in self.options:
            if o.type_ is None:
                type_ = self.params[o.dest].annotation

                if type_ == inspect._empty:
                    type_ = str
                else:
                    if o.transform_func:
                        type_ = str

                o.type_ = type_

        for a in self.arguments:
            if a.type_ is None:
                type_ = self.params[a.dest].annotation

                if type_ == inspect._empty:
                    type_ = str
                else:
                    if a.transform_func:
                        type_ = str

                a.type_ = type_
                if is_container(a.type_):
                    a.container_cls = None
                    a.typing_has_container = True
        self.is_prepared = True

    def __call__(self, *args, **kwargs) -> HANDLER_CALL_RETURN_TYPE:
        _self = kwargs.pop('_self', None)
        if _self:
            kwargs['self'] = _self
        return self.f(*args, **kwargs)


DECORATOR_ARGS_TYPE: TypeAlias = HANDLER_CALL_TYPE | Handler
DECORATOR_TYPE: TypeAlias = Callable[[DECORATOR_ARGS_TYPE], Handler]
