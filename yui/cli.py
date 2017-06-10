import click

from .bot import Bot


@click.group()
def yui():
    """YUI, Slack Bot for item4.slack.com"""


@yui.command()
@click.argument('token')
def run(token):
    debug = True
    bot = Bot(token, debug)
    bot.run()

main = yui
