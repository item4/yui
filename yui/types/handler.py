from __future__ import annotations

import inspect
from collections.abc import Callable
from collections.abc import Coroutine
from collections.abc import Mapping
from typing import Any
from typing import TYPE_CHECKING
from typing import TypeAlias
from typing import get_type_hints

from attrs import define
from croniter import croniter

from ..utils.attrs import field
from ..utils.attrs import field_transformer

if TYPE_CHECKING:
    from datetime import datetime

    from ..box.tasks import CronTask


HANDLER_CALL_RETURN_TYPE: TypeAlias = Coroutine[Any, Any, bool | None]
HANDLER_CALL_TYPE: TypeAlias = Callable[..., HANDLER_CALL_RETURN_TYPE]


@define(kw_only=True, field_transformer=field_transformer)
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


@define(kw_only=True, field_transformer=field_transformer)
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


@define(kw_only=True, field_transformer=field_transformer)
class Handler:
    f: HANDLER_CALL_TYPE
    arguments: list[Argument] = field(init=False)
    options: list[Option] = field(init=False)
    cron: CronTask | None = field(init=False, default=None)
    last_call: Any = field(init=False)
    doc: str | None = field(init=False)
    params: Mapping[str, inspect.Parameter] = field(init=False)
    annotations: dict[str, Any] = field(init=False)
    is_prepared: bool = field(init=False, default=False)
    bound: Any = field(init=False)

    def __attrs_post_init__(self):
        self.doc = inspect.getdoc(self.f)
        self.params = inspect.signature(self.f).parameters
        self.annotations = get_type_hints(self.f)
        self.arguments = []
        self.options = []
        self.last_call = {}

    def prepare(self):
        from ..box.utils import is_container

        for o in self.options:
            if o.type_ is None:
                type_ = self.annotations.get(o.dest, None)

                if type_ is None or o.transform_func:
                    type_ = str

                o.type_ = type_

        for a in self.arguments:
            if a.type_ is None:
                type_ = self.annotations.get(a.dest, None)

                if type_ is None or a.transform_func:
                    type_ = str

                a.type_ = type_
                if is_container(a.type_):
                    a.container_cls = None
                    a.typing_has_container = True
        self.is_prepared = True

    def __call__(self, *args, **kwargs) -> HANDLER_CALL_RETURN_TYPE:
        if self.bound:
            return self.f(self.bound, *args, **kwargs)
        return self.f(*args, **kwargs)

    def __repr__(self) -> str:
        return f"{self.f.__module__}.{self.f.__name__}"

    def has_valid_spec(self) -> bool:
        return self.cron is not None and croniter.is_valid(self.cron.spec)

    def match(self, dt: datetime) -> bool:
        return self.cron is not None and croniter.match(self.cron.spec, dt)


DECORATOR_ARGS_TYPE: TypeAlias = HANDLER_CALL_TYPE | Handler
DECORATOR_TYPE: TypeAlias = Callable[[DECORATOR_ARGS_TYPE], Handler]
