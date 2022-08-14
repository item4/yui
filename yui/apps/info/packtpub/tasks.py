from .commons import say_packtpub_dotd
from ....box import box


@box.cron("5 9 * * *")
async def auto_packtpub_dotd(bot):
    await say_packtpub_dotd(bot, bot.config.CHANNELS["general"])
