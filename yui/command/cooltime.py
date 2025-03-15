from datetime import datetime
from datetime import timedelta

from ..bot import Bot
from ..utils.datetime import now


class Cooltime:
    def __init__(self, *, bot: Bot, key: str, cooltime: timedelta) -> None:
        self.bot = bot
        self.key = key
        self.cooltime = cooltime
        self.now = now()

    async def rejected(self) -> datetime | None:
        last_call = await self.bot.cache.get_dt(self.key)
        if last_call and self.now - last_call < self.cooltime:
            return last_call + self.cooltime
        return None

    async def record(self):
        await self.bot.cache.set_dt(self.key, self.now)
