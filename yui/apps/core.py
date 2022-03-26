import logging

from ..bot import BotReconnect
from ..box import box
from ..event import TeamMigrationStarted
from ..event import YuiSystemStart

logger = logging.getLogger(__name__)


@box.on(YuiSystemStart)
async def on_start(bot):
    bot.is_ready = True
    return True


@box.on(TeamMigrationStarted)
async def team_migration_started():
    logger.info('Slack sent team_migration_started. restart bot')
    raise BotReconnect()
