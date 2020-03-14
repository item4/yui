from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Optional
from typing import Sequence
from typing import Set
from typing import Tuple
from typing import Type
from typing import Union

from .helpers import C
from .helpers import Cs
from ..event import Message
from ..exceptions import AllChannelsError
from ..exceptions import NoChannelsError
from ..types.channel import PrivateChannel
from ..types.channel import PublicChannel


class DM:
    """Direct Message"""


ACCEPTABLE_CHANNEL_TYPES = Union[
    Type[DM], PrivateChannel, PublicChannel, C, Cs, str,
]

VALIDATOR_TYPE = Callable[[Any, Message], Awaitable[bool]]


def get_channel_names(
    channels: Sequence[ACCEPTABLE_CHANNEL_TYPES],
) -> Tuple[Set[str], bool, bool]:
    dm = False
    channel_names = set()
    fetch_error = False
    for channel in channels:
        if isinstance(channel, (PrivateChannel, PublicChannel)):
            channel_names.add(channel.name)
        elif isinstance(channel, C):
            try:
                channel_names.add(channel.get().name)
            except KeyError:
                fetch_error = True
        elif isinstance(channel, Cs):
            try:
                channel_names = channel_names.union(
                    c.name for c in channel.gets()
                )
            except KeyError:
                fetch_error = True
        elif channel == DM:
            dm = True
        elif isinstance(channel, str):
            channel_names.add(channel)
    return channel_names, dm, fetch_error


def only(
    *channels: ACCEPTABLE_CHANNEL_TYPES, error: Optional[str] = None,
) -> VALIDATOR_TYPE:
    """Mark channel to allow to use handler."""

    async def callback(bot, event: Message) -> bool:
        try:
            channel_names, allow_dm, fetch_error = get_channel_names(channels)
        except AllChannelsError:
            return True
        except NoChannelsError:
            if error:
                await bot.say(event.channel, error)
            return False

        if fetch_error:
            return False

        if isinstance(event.channel, (PrivateChannel, PublicChannel)):
            if event.channel.name in channel_names:
                return True
            else:
                if error:
                    await bot.say(event.channel, error)
                return False

        if allow_dm:
            return True
        else:
            if error:
                await bot.say(event.channel, error)
            return False

    return callback


def not_(
    *channels: ACCEPTABLE_CHANNEL_TYPES, error: Optional[str] = None,
) -> VALIDATOR_TYPE:
    """Mark channel to deny to use handler."""

    async def callback(bot, event: Message) -> bool:
        try:
            channel_names, deny_dm, fetch_error = get_channel_names(channels)
        except AllChannelsError:
            if error:
                await bot.say(event.channel, error)
            return False
        except NoChannelsError:
            return True

        if fetch_error:
            return False

        if isinstance(event.channel, (PrivateChannel, PublicChannel)):
            if event.channel.name in channel_names:
                if error:
                    await bot.say(event.channel, error)
                return False
            else:
                return True

        if deny_dm:
            if error:
                await bot.say(event.channel, error)
            return False
        else:
            return True

    return callback
