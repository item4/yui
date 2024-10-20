import pytest

from yui.apps.core import on_start
from yui.apps.core import team_migration_started
from yui.bot import BotReconnect


@pytest.mark.asyncio
async def test_on_start(bot):
    assert await on_start(bot)
    assert bot.is_ready.is_set()


@pytest.mark.asyncio
async def test_team_migration_started():
    with pytest.raises(BotReconnect):
        await team_migration_started()
