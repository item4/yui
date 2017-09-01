""":mod:`yui.command` --- decorators for making command
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Decorators and classes for making command.

"""

import functools

from typing import Any, Awaitable, Callable, List, Optional, Type, Union  # noqa: F401,E501

from .event import Event

__all__ = 'Argument', 'DM', 'Option', 'argument', 'not_', 'only', 'option'


class DM:
    """Direct Message"""


def only(*channels: Union[Type[DM], str], error: Optional[str]=None)\
        -> Callable[[Any, Event], Awaitable[bool]]:
    """Mark channel to allow to use handler."""

    allow_dm = False
    if DM in channels:
        channels = tuple(x for x in channels if x is not DM)
        allow_dm = True

    async def callback(bot, event: Event) -> bool:
        if event.channel.startswith('C'):
            if bot.channels[event.channel]['name'] in channels:
                return True
            else:
                if error:
                    await bot.say(
                        event.channel,
                        error
                    )
                return False
        elif event.channel.startswith('D'):
            if allow_dm:
                return True
            else:
                if error:
                    await bot.say(
                        event.channel,
                        error
                    )
                return False
        return False

    return callback


def not_(*channels: Union[Type[DM], str], error: Optional[str]=None) \
        -> Callable[[Any, Event], Awaitable[bool]]:
    """Mark channel to deny to use handler."""

    deny_dm = False
    if DM in channels:
        channels = tuple(x for x in channels if x is not DM)
        deny_dm = True

    async def callback(bot, event: Event) -> bool:
        if event.channel.startswith('C'):
            if bot.channels[event.channel]['name'] in channels:
                if error:
                    await bot.say(
                        event.channel,
                        error
                    )
                return False
            else:
                return True
        elif event.channel.startswith('D'):
            if deny_dm:
                if error:
                    await bot.say(
                        event.channel,
                        error
                    )
                return False
            else:
                return True
        return False

    return callback


def argument(
    name: str,
    dest: Optional[str]=None,
    nargs: int=1,
    transform_func: Optional[Callable]=None,
    type_: Optional[Type]=None,
    container_cls: Optional[Type]=None,
    concat: Optional[bool]=False,
    type_error: str='{name}: invalid type of argument value({e})',
    count_error: str=('{name}: incorrect argument value count.'
                      ' expected {expected}, {given} given.'),
    transform_error: str='{name}: fail to transform argument value ({e})'
) -> Callable:
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
    :rtype: :class:`typing.Callable`

    """

    if nargs == 1 and container_cls:
        container_cls = None
    elif nargs != 1 and container_cls is None:
        if concat:
            type_ = str
            container_cls = list
        else:
            container_cls = tuple

    if dest is None:
        dest = name.lower()

    def decorator(func):

        @functools.wraps(func)
        def internal(func_):
            if not hasattr(func_, '__arguments__'):
                func_.__arguments__ = []
            func_.__arguments__.insert(
                0,
                Argument(
                    name=name,
                    dest=dest,
                    nargs=nargs,
                    transform_func=transform_func,
                    type_=type_,
                    container_cls=container_cls,
                    concat=concat,
                    type_error=type_error,
                    count_error=count_error,
                    transform_error=transform_error,
                )
            )
            return func_

        return internal(func)

    return decorator


def option(
    *args: str,
    default: Optional[Any]=None,
    dest: Optional[str]=None,
    is_flag: bool=False,
    nargs: int=1,
    multiple: bool=False,
    container_cls: Optional[Type]=None,
    required: bool=False,
    transform_func: Optional[Callable]=None,
    type_: Optional[Type]=None,
    value: Optional[Any]=None,
    type_error: str='{name}: invalid type of option value({e})',
    count_error: str=('{name}: incorrect option value count.'
                      ' expected {expected}, {given} given.'),
    transform_error: str='{name}: fail to transform option value ({e})'
) -> Callable:
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
    :rtype: :class:`typing.Callable`

    """

    options: List[Option] = []

    if nargs == 1 and container_cls:
        container_cls = None
    elif (multiple or nargs != 1) and container_cls is None:
        container_cls = tuple

    key: str = ' '.join(args)

    if dest is None:
        dest = args[0].lstrip('-').split('/')[0].replace('-', '_')

    for name in args:
        if '/' in name:
            true_case, false_case = name.split('/')
            options.append(
                Option(
                    key=key,
                    name=true_case,
                    default=default,
                    dest=dest,
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
                )
            )
            options.append(
                Option(
                    key=key,
                    name=false_case,
                    default=default,
                    dest=dest,
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
                )
            )
        elif is_flag:
            options.append(
                Option(
                    key=key,
                    name=name,
                    default=default,
                    dest=dest,
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
                )
            )
        else:
            options.append(
                Option(
                    key=key,
                    name=name,
                    default=default,
                    dest=dest,
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
                )
            )

    def decorator(func):

        @functools.wraps(func)
        def internal(func_):
            if not hasattr(func_, '__options__'):
                func_.__options__ = []
            func_.__options__[:] = options + func_.__options__

            return func_

        return internal(func)

    return decorator


class Argument:
    """Argument"""

    def __init__(
        self,
        name: str,
        dest: str,
        nargs: int,
        transform_func: Optional[Callable],
        type_: Optional[Type],
        container_cls: Optional[Type],
        concat: bool,
        type_error: str,
        count_error: str,
        transform_error: str
    ) -> None:
        """Initialize"""

        self.name = name
        self.dest = dest
        self.nargs = nargs
        self.transform_func = transform_func
        self.type_ = type_
        self.container_cls = container_cls
        self.concat = concat
        self.type_error = type_error
        self.count_error = count_error
        self.transform_error = transform_error


class Option:
    """Option"""

    def __init__(
        self,
        key: str,
        name: str,
        default: Any,
        dest: str,
        nargs: int,
        multiple: bool,
        container_cls: Optional[Type],
        required: bool,
        transform_func: Optional[Callable],
        type_: Optional[Type],
        value: Any,
        type_error: str,
        count_error: str,
        transform_error: str
    ) -> None:
        """Initialize"""

        self.key = key
        self.name = name
        self.default = default
        self.dest = dest
        self.nargs = nargs
        self.multiple = multiple
        self.container_cls = container_cls
        self.required = required
        self.transform_func = transform_func
        self.type_ = type_
        self.value = value
        self.type_error = type_error
        self.count_error = count_error
        self.transform_error = transform_error
