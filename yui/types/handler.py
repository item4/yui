from __future__ import annotations

import inspect
from collections.abc import Callable
from collections.abc import Coroutine
from collections.abc import Mapping
from typing import Any
from typing import TYPE_CHECKING
from typing import TypeAlias

from ..utils.attrs import define
from ..utils.attrs import field

if TYPE_CHECKING:
    from ..box.tasks import CronTask


HANDLER_CALL_RETURN_TYPE: TypeAlias = Coroutine[Any, Any, bool | None]
HANDLER_CALL_TYPE: TypeAlias = Callable[..., HANDLER_CALL_RETURN_TYPE]


@define
class Argument:
    """Argument"""

    name: str
    dest: str
    nargs: int
    transform_func: Callable | None
    type_: type | None
    container_cls: type | None
    concat: bool
    type_error: str
    count_error: str
    transform_error: str
    typing_has_container: bool = field(init=False, default=False)


@define
class Option:
    """Option"""

    key: str
    name: str
    default: Any
    dest: str
    nargs: int
    multiple: bool
    container_cls: type | None
    required: bool
    transform_func: Callable | None
    type_: type | None
    value: Any
    type_error: str
    count_error: str
    transform_error: str


@define
class Handler:
    f: HANDLER_CALL_TYPE
    arguments: list[Argument] = field(init=False)
    options: list[Option] = field(init=False)
    cron: CronTask | None = field(init=False, default=None)
    last_call: Any = field(init=False)
    doc: str | None = field(init=False)
    params: Mapping[str, inspect.Parameter] = field(init=False)
    is_prepared: bool = field(init=False, default=False)

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

                if type_ == inspect._empty or o.transform_func:
                    type_ = str

                o.type_ = type_

        for a in self.arguments:
            if a.type_ is None:
                type_ = self.params[a.dest].annotation

                if type_ == inspect._empty or a.transform_func:
                    type_ = str

                a.type_ = type_
                if is_container(a.type_):
                    a.container_cls = None
                    a.typing_has_container = True
        self.is_prepared = True

    def __call__(self, *args, **kwargs) -> HANDLER_CALL_RETURN_TYPE:
        _self = kwargs.pop("_self", None)
        if _self:
            kwargs["self"] = _self
        return self.f(*args, **kwargs)

    def __repr__(self) -> str:
        return f"{self.f.__module__}.{self.f.__name__}"


DECORATOR_ARGS_TYPE: TypeAlias = HANDLER_CALL_TYPE | Handler
DECORATOR_TYPE: TypeAlias = Callable[[DECORATOR_ARGS_TYPE], Handler]
