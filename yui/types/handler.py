from __future__ import annotations

import inspect
from typing import Any
from typing import Callable
from typing import Coroutine
from typing import List
from typing import Mapping
from typing import Optional
from typing import TYPE_CHECKING
from typing import Type
from typing import Union

import attr

if TYPE_CHECKING:
    from ..box.tasks import CronTask


HANDLER_CALL_RETURN_TYPE = Coroutine[Any, Any, Optional[bool]]
HANDLER_CALL_TYPE = Callable[..., HANDLER_CALL_RETURN_TYPE]


@attr.dataclass(slots=True)
class Argument:
    """Argument"""

    name: str
    dest: str
    nargs: int
    transform_func: Optional[Callable]
    type_: Optional[Type]
    container_cls: Optional[Type]
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
    container_cls: Optional[Type]
    required: bool
    transform_func: Optional[Callable]
    type_: Optional[Type]
    value: Any
    type_error: str
    count_error: str
    transform_error: str


@attr.dataclass(slots=True)
class Handler:
    f: HANDLER_CALL_TYPE
    arguments: List[Argument] = attr.ib(init=False)
    options: List[Option] = attr.ib(init=False)
    cron: Optional[CronTask] = attr.ib(init=False, default=None)
    last_call: Any = attr.ib(init=False)
    doc: Optional[str] = attr.ib(init=False)
    params: Mapping[str, inspect.Parameter] = attr.ib(init=False)

    def __attrs_post_init__(self):
        self.doc = inspect.getdoc(self.f)
        self.params = inspect.signature(self.f).parameters
        self.arguments = []
        self.options = []
        self.last_call = {}

    def __call__(self, *args, **kwargs) -> HANDLER_CALL_RETURN_TYPE:
        _self = kwargs.pop('_self', None)
        if _self:
            kwargs['self'] = _self
        return self.f(*args, **kwargs)


DECORATOR_ARGS_TYPE = Union[HANDLER_CALL_TYPE, Handler]
DECORATOR_TYPE = Callable[[DECORATOR_ARGS_TYPE], Handler]
