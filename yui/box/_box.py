from typing import Any, Dict, List, Optional, Set, Type, Union

from .apps.base import BaseApp
from .apps.basic import App
from .tasks import CronTask
from ..command.validators import VALIDATOR_TYPE
from ..event import Event
from ..types.handler import DECORATOR_ARGS_TYPE, DECORATOR_TYPE, Handler
from ..utils.handler import get_handler


class Box:
    """Box, collection of apps and tasks"""

    def __init__(self) -> None:
        """Initialize"""

        self.config_required: Dict[str, Any] = {}
        self.channel_required: Set[str] = set()
        self.channels_required: Set[str] = set()
        self.user_required: Set[str] = set()
        self.users_required: Set[str] = set()
        self.apps: List[BaseApp] = []
        self.tasks: List[CronTask] = []

    def register(self, app: BaseApp):
        """Register App manually."""

        self.apps.append(app)

    def assert_config_required(self, key: str, type_):
        """Mark required configuration key and type."""

        self.config_required[key] = type_

    def assert_channel_required(self, key: str):
        """Mark required channel name in configuration."""

        self.channel_required.add(key)

    def assert_channels_required(self, key: str):
        """Mark required channels name in configuration."""

        self.channels_required.add(key)

    def assert_user_required(self, key: str):
        """Mark required user name in configuration."""

        self.user_required.add(key)

    def assert_users_required(self, key: str):
        """Mark required users name in configuration."""

        self.users_required.add(key)

    def command(
        self,
        name: str,
        aliases: Optional[List[str]] = None,
        *,
        subtype: Optional[str] = None,
        short_help: Optional[str] = None,
        help: Optional[str] = None,
        use_shlex: bool = True,
        channels: Optional[VALIDATOR_TYPE] = None,
    ) -> DECORATOR_TYPE:
        """Shortcut decorator for make command easily."""

        def decorator(target: DECORATOR_ARGS_TYPE) -> Handler:
            handler = get_handler(target)

            self.apps.append(
                App(
                    'message',
                    subtype,
                    handler,
                    name=name,
                    aliases=aliases,
                    short_help=short_help,
                    help=help,
                    is_command=True,
                    use_shlex=use_shlex,
                    channel_validator=channels,
                )
            )

            return handler

        return decorator

    def on(
        self,
        type_: Union[str, Type[Event]],
        *,
        subtype: Optional[str] = None,
        channels: Optional[VALIDATOR_TYPE] = None,
    ) -> DECORATOR_TYPE:
        """Decorator for make app."""

        if isinstance(type_, str):
            event_type = type_
        else:
            event_type = type_.type

        def decorator(target: DECORATOR_ARGS_TYPE) -> Handler:
            handler = get_handler(target)

            self.apps.append(
                App(event_type, subtype, handler, channel_validator=channels,)
            )

            return handler

        return decorator

    def cron(self, spec: str, *args, **kwargs) -> CronTask:
        """Decorator for cron task."""

        c = CronTask(self, spec, args, kwargs)
        self.tasks.append(c)
        return c
