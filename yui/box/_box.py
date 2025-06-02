from collections.abc import Callable
from typing import Any

from ..event import Event
from ..types.handler import FuncType
from ..types.handler import Handler
from .apps.base import BaseApp
from .apps.basic import App
from .tasks import CronTask
from .tasks import PollingTask

type Decorator = Callable[[FuncType | Handler], Handler]


class Box:
    """Box, collection of apps and tasks"""

    def __init__(self) -> None:
        """Initialize"""

        self.config_required: dict[str, Any] = {}
        self.channel_required: set[str] = set()
        self.channels_required: set[str] = set()
        self.user_required: set[str] = set()
        self.users_required: set[str] = set()
        self.apps: list[BaseApp] = []
        self.cron_tasks: list[CronTask] = []
        self.polling_tasks: list[PollingTask] = []

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
        aliases: list[str] | None = None,
        *,
        subtype: str | None = None,
        short_help: str | None = None,
        help: str | None = None,
        use_shlex: bool = True,
    ) -> Decorator:
        """Shortcut decorator for make command easily."""

        def decorator(target: FuncType | Handler) -> Handler:
            handler = Handler.from_callable(target)

            self.apps.append(
                App(
                    "message",
                    subtype,
                    handler,
                    name=name,
                    aliases=aliases,
                    short_help=short_help,
                    help=help,
                    is_command=True,
                    use_shlex=use_shlex,
                ),
            )

            return handler

        return decorator

    def on(
        self,
        type_: str | type[Event],
        *,
        subtype: str | None = None,
    ) -> Decorator:
        """Decorator for make app."""

        event_type = type_ if isinstance(type_, str) else type_.type

        def decorator(target: FuncType | Handler) -> Handler:
            handler = Handler.from_callable(target)

            self.apps.append(
                App(
                    event_type,
                    subtype,
                    handler,
                ),
            )

            return handler

        return decorator

    def cron(self, spec: str, *args, **kwargs) -> CronTask:
        """Decorator for cron task."""

        c = CronTask(self, spec, args, kwargs)
        self.cron_tasks.append(c)
        return c

    def polling_task(self, /) -> PollingTask:
        """Decorator for polling task."""

        p = PollingTask(self)
        self.polling_tasks.append(p)
        return p
