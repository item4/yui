""":mod:`yui.command` --- decorators for making command
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Decorators and classes for making command.

"""

import functools
from typing import (
    Any,
    Awaitable,
    Callable,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    Union,
)

from .event import Event
from .type import (
    AllChannelsError,
    ChannelFromConfig,
    ChannelsFromConfig,
    NoChannelsError,
    PrivateChannel,
    PublicChannel,
)

__all__ = (
    'ACCEPTABLE_CHANNEL_TYPES',
    'Argument',
    'C',
    'Cs',
    'DM',
    'Option',
    'argument',
    'get_channel_names',
    'not_',
    'only',
    'option',
)


class DM:
    """Direct Message"""


class _C:
    """Magic class for create channel from config"""

    def __getattr__(self, key: str) -> ChannelFromConfig:
        return ChannelFromConfig(key)

    def __getitem__(self, key: str) -> ChannelFromConfig:
        return ChannelFromConfig(key)


class _Cs:
    """Magic class for create channels from config"""

    def __getattr__(self, key: str) -> ChannelsFromConfig:
        return ChannelsFromConfig(key)

    def __getitem__(self, key: str) -> ChannelsFromConfig:
        return ChannelsFromConfig(key)


# Magic instance for create channel from config
C = _C()

# Magic instance for create channels from config
Cs = _Cs()

ACCEPTABLE_CHANNEL_TYPES = Union[
    Type[DM],
    PrivateChannel,
    PublicChannel,
    ChannelFromConfig,
    ChannelsFromConfig,
    str,
]


def get_channel_names(channels: Sequence[ACCEPTABLE_CHANNEL_TYPES])\
        -> Tuple[Set[str], bool, bool]:
    dm = False
    channel_names = set()
    fetch_error = False
    for channel in channels:
        if isinstance(channel, (PrivateChannel, PublicChannel)):
            channel_names.add(channel.name)
        elif isinstance(channel, ChannelFromConfig):
            try:
                channel_names.add(channel.get().name)
            except KeyError:
                fetch_error = True
        elif isinstance(channel, ChannelsFromConfig):
            try:
                channel_names = channel_names.union(
                    c.name for c in channel.get()
                )
            except KeyError:
                fetch_error = True
        elif channel == DM:
            dm = True
        elif isinstance(channel, str):
            channel_names.add(channel)
    return channel_names, dm, fetch_error


def only(*channels: ACCEPTABLE_CHANNEL_TYPES, error: Optional[str] = None)\
        -> Callable[[Any, Event], Awaitable[bool]]:
    """Mark channel to allow to use handler."""

    async def callback(bot, event: Event) -> bool:
        try:
            channel_names, allow_dm, fetch_error = get_channel_names(channels)
        except AllChannelsError:
            return True
        except NoChannelsError:
            if error:
                await bot.say(
                    event.channel,
                    error
                )
            return False

        if fetch_error:
            return False

        if isinstance(event.channel, (PrivateChannel, PublicChannel)):
            if event.channel.name in channel_names:
                return True
            else:
                if error:
                    await bot.say(
                        event.channel,
                        error
                    )
                return False

        if allow_dm:
            return True
        else:
            if error:
                await bot.say(
                    event.channel,
                    error
                )
            return False

    return callback


def not_(*channels: ACCEPTABLE_CHANNEL_TYPES, error: Optional[str] = None) \
        -> Callable[[Any, Event], Awaitable[bool]]:
    """Mark channel to deny to use handler."""

    async def callback(bot, event: Event) -> bool:
        try:
            channel_names, deny_dm, fetch_error = get_channel_names(channels)
        except AllChannelsError:
            if error:
                await bot.say(
                    event.channel,
                    error
                )
            return False
        except NoChannelsError:
            return True

        if fetch_error:
            return False

        if isinstance(event.channel, (PrivateChannel, PublicChannel)):
            if event.channel.name in channel_names:
                if error:
                    await bot.say(
                        event.channel,
                        error
                    )
                return False
            else:
                return True

        if deny_dm:
            if error:
                await bot.say(
                    event.channel,
                    error
                )
            return False
        else:
            return True

    return callback


def argument(
    name: str,
    dest: Optional[str] = None,
    nargs: int = 1,
    transform_func: Optional[Callable] = None,
    type_: Optional[Type] = None,
    container_cls: Optional[Type] = None,
    concat: Optional[bool] = False,
    type_error: str = '{name}: invalid type of argument value({e})',
    count_error: str = ('{name}: incorrect argument value count.'
                        ' expected {expected}, {given} given.'),
    transform_error: str = '{name}: fail to transform argument value ({e})'
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
        else:
            container_cls = tuple

    if dest is None:
        dest = name

    dest = dest.lower()

    def decorator(func):

        @functools.wraps(func)
        def internal(func_):
            if not hasattr(func_, '__arguments__'):
                func_.__arguments__ = []

            if nargs < 0 and any(a.nargs < 0 for a in func_.__arguments__):
                raise TypeError('can not have two nargs<0')

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
    default: Optional[Any] = None,
    dest: Optional[str] = None,
    is_flag: bool = False,
    nargs: int = 1,
    multiple: bool = False,
    container_cls: Optional[Type] = None,
    required: bool = False,
    transform_func: Optional[Callable] = None,
    type_: Optional[Type] = None,
    value: Optional[Any] = None,
    type_error: str = '{name}: invalid type of option value({e})',
    count_error: str = ('{name}: incorrect option value count.'
                        ' expected {expected}, {given} given.'),
    transform_error: str = '{name}: fail to transform option value ({e})',
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
        self.typing_has_container = False
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
