import json
import re
import sys
import traceback
from typing import Optional
from typing import TYPE_CHECKING

from .format import bold
from .format import code
from .format import preformatted
from ..event import Event

if TYPE_CHECKING:
    from ..bot import APICallError
    from ..bot import Bot


LIMIT = 3500
SITE_PACKAGES = re.compile(r'(?:\s*File ")?/.+?/site-packages/')
BUILTIN_PACKAGES = re.compile(r'(?:\s*File ")?/.+?/lib/python[^/]+?/')
IN_YUI = re.compile(r'(?:\s*File ")?/.+?/yui/yui/')
START_SPACE = re.compile(r' {4,}')


def get_simple_tb_text(tb: list[str]) -> list[str]:
    result: list[str] = []
    for line in tb:
        line = SITE_PACKAGES.sub('File "site-packages/', line)
        line = BUILTIN_PACKAGES.sub('File "python/', line)
        line = IN_YUI.sub('File "proj/yui/', line)
        line = START_SPACE.sub('  ', line)
        result.append(line)

    return result


async def report(
    bot: 'Bot',
    *,
    event: Optional[Event] = None,
    exception: Optional['APICallError'] = None,
):
    tb_lines = get_simple_tb_text(traceback.format_exception(*sys.exc_info()))
    messages: list[str] = []
    message = ''
    if event:
        message += f"""\
{bold('Event')}
{preformatted(str(event))}
"""
    if exception:
        message += f"""\
{bold('Method')}: {code(exception.method)}
{bold('Data')}
{preformatted(json.dumps(exception.data, ensure_ascii=False, indent=2))}
{bold('Headers')}
{preformatted(json.dumps(exception.headers, ensure_ascii=False, indent=2))}
"""
    message += bold('Traceback')
    message += '\n'
    length = len(message) + 6

    block = ''
    for line in tb_lines:
        if length + len(block) >= LIMIT:
            message += preformatted(block)
            messages.append(message)
            message = ''
            block = ''
            length = 6
        block += line
        length += len(line)

    for message in messages:
        await bot.say(
            bot.config.USERS['owner'],
            message,
            length_limit=None,
        )
