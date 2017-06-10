import click

from .bot import Bot
from .box import box


__all__ = 'main', 'yui'


@click.group()
def yui():
    """YUI, Slack Bot for item4.slack.com"""


@yui.command()
@click.argument('token')
def run(token):
    @box.command('안녕')
    async def hi(bot, message):
        user = await bot.api.users.info(message.get('user'))
        await bot.say(
            'test',
            '안녕하세요! {}'.format(user['user']['name'])
        )

    debug = True
    bot = Bot(token, debug)
    bot.run()

main = yui
