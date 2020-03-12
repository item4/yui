from __future__ import annotations

import contextlib
import inspect
from typing import Mapping, TYPE_CHECKING

from ...event import Event
from ...orm import EngineConfig, make_session

if TYPE_CHECKING:
    from ...bot import Bot


class BaseApp:
    """Base class of App"""

    def get_short_help(self, prefix: str) -> str:
        raise NotImplementedError

    def get_full_help(self, prefix: str) -> str:
        return self.get_short_help(prefix)

    @property
    def has_short_help(self) -> bool:
        try:
            self.get_short_help('')
        except NotImplementedError:
            return False
        return True

    @property
    def has_full_help(self) -> bool:
        try:
            self.get_full_help('')
        except NotImplementedError:
            return False
        return True

    async def run(self, bot: Bot, event: Event):
        raise NotImplementedError

    @contextlib.contextmanager
    def prepare_kwargs(
        self,
        *,
        bot: Bot,
        event: Event,
        func_params: Mapping[str, inspect.Parameter],
        **kwargs,
    ):
        sess = make_session(bind=bot.config.DATABASE_ENGINE)
        if 'self' in func_params:
            kwargs['_self'] = self
        if 'bot' in func_params:
            kwargs['bot'] = bot
        if 'loop' in func_params:
            kwargs['loop'] = bot.loop
        if 'event' in func_params:
            kwargs['event'] = event
        if 'sess' in func_params:
            kwargs['sess'] = sess
        if 'engine_config' in func_params:
            kwargs['engine_config'] = EngineConfig(
                url=bot.config.DATABASE_URL, echo=bot.config.DATABASE_ECHO,
            )

        try:
            yield kwargs
        finally:
            sess.close()
