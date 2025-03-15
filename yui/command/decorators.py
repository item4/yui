from __future__ import annotations

from typing import Any
from typing import TYPE_CHECKING

from ..types.handler import Argument
from ..types.handler import Handler
from ..types.handler import Option
from ..utils.handler import get_handler

if TYPE_CHECKING:
    from collections.abc import Callable

    from ..types.handler import DECORATOR_ARGS_TYPE
    from ..types.handler import DECORATOR_TYPE


ARGUMENT_TYPE_ERROR = "{name}: invalid type of argument value({e})"
ARGUMENT_COUNT_ERROR = (
    "{name}: incorrect argument value count. expected {expected}, {given}"
    " given."
)
ARGUMENT_TRANSFORM_ERROR = "{name}: fail to transform argument value ({e})"
OPTION_TYPE_ERROR = "{name}: invalid type of option value({e})"
OPTION_COUNT_ERROR = (
    "{name}: incorrect option value count. expected {expected}, {given} given."
)
OPTION_TRANSFORM_ERROR = "{name}: fail to transform option value ({e})"


def argument(
    name: str,
    *,
    dest: str | None = None,
    nargs: int = 1,
    transform_func: Callable | None = None,
    type_: type | None = None,
    container_cls: type | None = None,
    concat: bool = False,
    type_error: str = ARGUMENT_TYPE_ERROR,
    count_error: str = ARGUMENT_COUNT_ERROR,
    transform_error: str = ARGUMENT_TRANSFORM_ERROR,
) -> DECORATOR_TYPE:
    """
    Add argument to command.

    :param name: argument name
    :type name: :class:`str`
    :param dest: destination name to assign value
    :type dest: :class:`str`
    :param nargs: :class:`str`
    :type nargs: :class:`int`
    :param transform_func: function for transform value to correct type
    :type transform_func: :class:`Callable`
    :param type_: type of argument value
    :type type_: :class:`type` or `None`
    :param container_cls: type of arguments container. It use if nargs!=1.
    :type container_cls: :class:`type`
    :param concat: flag to concat arguments
    :type concat: :class:`bool`
    :param type_error: error message for wrong type
    :type type_error: :class:`str`
    :param count_error: error message for wrong value count
    :type count_error: :class:`str`
    :param transform_error: error message for fail transform value
    :type transform_error: :class:`str`

    :return: decorator
    :rtype: `DECORATOR_TYPE`

    """

    if nargs == 1 and container_cls:
        container_cls = None
    elif nargs != 1 and container_cls is None:
        if concat:
            type_ = str
        else:
            container_cls = tuple

    _dest = name if dest is None else dest

    _dest = _dest.lower()

    def decorator(target: DECORATOR_ARGS_TYPE) -> Handler:
        handler = get_handler(target)

        if nargs < 0 and any(a.nargs < 0 for a in handler.arguments):
            raise TypeError("can not have two nargs<0")

        handler.arguments.insert(
            0,
            Argument(
                name=name,
                dest=_dest,
                nargs=nargs,
                transform_func=transform_func,
                type_=type_,
                container_cls=container_cls,
                concat=concat,
                type_error=type_error,
                count_error=count_error,
                transform_error=transform_error,
            ),
        )
        return handler

    return decorator


def option(
    *args: str,
    default: Any | None = None,
    dest: str | None = None,
    is_flag: bool = False,
    nargs: int = 1,
    multiple: bool = False,
    container_cls: type | None = None,
    required: bool = False,
    transform_func: Callable | None = None,
    type_: type | None = None,
    value: Any | None = None,
    type_error: str = OPTION_TYPE_ERROR,
    count_error: str = OPTION_COUNT_ERROR,
    transform_error: str = OPTION_TRANSFORM_ERROR,
) -> DECORATOR_TYPE:
    """
    Add option parameter to command.

    :param args: names
    :type args: :class:`tuple` of :class:`str`
    :param default: default value
    :param dest: destination name to assign value
    :type dest: :class:`str`
    :param is_flag: set to flag option
    :type is_flag: :class:`bool`
    :param nargs: count of argument what option needed
    :type nargs: :class:`int`
    :param multiple: flag for assume values as list
    :type multiple: :class:`bool`
    :param container_cls: type of options container. It use if nargs!=1.
    :type container_cls: :class:`type`
    :param required: set to required option
    :type required: :class:`bool`
    :param transform_func: function for transform value to correct type
    :type transform_func: :class:`typing.Callable`
    :param type_: type of argument value
    :type type_: :class:`type` or `None`
    :param value: value to store flag
    :param type_error: error message for wrong type
    :type type_error: :class:`str`
    :param count_error: error message for wrong value count
    :type count_error: :class:`str`
    :param transform_error: error message for fail transform value
    :type transform_error: :class:`str`

    :return: real decorator
    :rtype: `DECORATOR_TYPE`

    """

    options: list[Option] = []

    if nargs == 1 and container_cls:
        container_cls = None
    elif (multiple or nargs != 1) and container_cls is None:
        container_cls = tuple

    key: str = " ".join(args)

    _dest = (
        args[0].lstrip("-").split("/")[0].replace("-", "_")
        if dest is None
        else dest
    )

    for name in args:
        if "/" in name:
            true_case, false_case = name.split("/")
            options.append(
                Option(
                    key=key,
                    name=true_case,
                    default=default,
                    dest=_dest,
                    nargs=0,
                    multiple=multiple,
                    container_cls=container_cls,
                    required=required,
                    transform_func=transform_func,
                    type_=bool,
                    value=True,
                    type_error=type_error,
                    count_error=count_error,
                    transform_error=transform_error,
                ),
            )
            options.append(
                Option(
                    key=key,
                    name=false_case,
                    default=default,
                    dest=_dest,
                    nargs=0,
                    multiple=multiple,
                    container_cls=container_cls,
                    required=required,
                    transform_func=transform_func,
                    type_=bool,
                    value=False,
                    type_error=type_error,
                    count_error=count_error,
                    transform_error=transform_error,
                ),
            )
        elif is_flag:
            options.append(
                Option(
                    key=key,
                    name=name,
                    default=default,
                    dest=_dest,
                    nargs=0,
                    multiple=multiple,
                    container_cls=container_cls,
                    required=required,
                    transform_func=transform_func,
                    type_=bool,
                    value=True if value is None else value,
                    type_error=type_error,
                    count_error=count_error,
                    transform_error=transform_error,
                ),
            )
        else:
            options.append(
                Option(
                    key=key,
                    name=name,
                    default=default,
                    dest=_dest,
                    nargs=nargs,
                    multiple=multiple,
                    container_cls=container_cls,
                    required=required,
                    transform_func=transform_func,
                    type_=type_,
                    value=value,
                    type_error=type_error,
                    count_error=count_error,
                    transform_error=transform_error,
                ),
            )

    def decorator(target: DECORATOR_ARGS_TYPE) -> Handler:
        handler = get_handler(target)
        handler.options[:] = options + handler.options
        return handler

    return decorator
