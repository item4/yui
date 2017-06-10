import asyncio
import click

from .bot import Bot


@click.group()
def yui():
    """YUI, Slack Bot for item4.slack.com"""


@yui.command()
@click.argument('token')
def run(token):
    debug = True
    loop = asyncio.get_event_loop()
    loop.set_debug(debug)

    bot = Bot(loop, token, debug)
    bot.run()
    loop.close()

main = yui
