import functools
import pathlib

import click

from .bot import Bot
from .box import box
from .config import load


__all__ = 'error', 'load_config', 'main', 'yui'


def error(message: str):
    """Echo and die with error message"""

    click.echo('Error: ' + message, err=True)
    raise SystemExit(1)


def load_config(func):
    """Decorator for add load config file option"""

    @functools.wraps(func)
    def internal(*args, **kwargs):
        filename = kwargs.pop('config')
        if filename is None:
            click.echo('--config option is required.', err=True)
            raise SystemExit(1)

        config = load(pathlib.Path(filename))
        kwargs['config'] = config
        return func(*args, **kwargs)

    decorator = click.option(
        '--config',
        '-c',
        type=click.Path(exists=True),
        envvar='YUI_CONFIG_FILE_PATH',
    )

    return decorator(internal)


@click.group()
def yui():
    """YUI, Slack Bot for item4.slack.com"""


@yui.command()
@load_config
def run(config):
    """Run YUI."""

    @box.on('message')
    async def hi(bot, message):
        if message['text'] in ['안녕', '안녕 유이', '유이 안녕']:
            user = await bot.api.users.info(message.get('user'))
            await bot.say(
                message['channel'],
                '안녕하세요! @{}'.format(user['user']['name'])
            )
            return False
        return True

    @box.command('ping', ['핑'])
    async def ping(bot, message):
        user = await bot.api.users.info(message.get('user'))
        await bot.say(
            message['channel'],
            '@{}, pong!'.format(user['user']['name'])
        )

    bot = Bot(config)
    bot.run()

main = yui
