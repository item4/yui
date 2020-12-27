import json
import re
from typing import Optional
from typing import TYPE_CHECKING

from more_itertools import chunked

from .format import bold
from .format import code
from .format import preformatted
from ..event import Event

if TYPE_CHECKING:
    from ..bot import APICallError
    from ..bot import Bot


LIMIT = 3500
SITE_PACKAGES = re.compile(r'\s*File "/.+?/site-packages/')
IN_YUI = re.compile(r'\s*File "/.+?/yui/yui/')
START_SPACE = re.compile(r'^\s{4,}')


def get_simple_tb_text(tb_text: str) -> str:
    tb_text = tb_text.split('\n', 1)[1]
    tb_text = SITE_PACKAGES.sub('File "python/', tb_text)
    tb_text = IN_YUI.sub('File "proj/yui/', tb_text)
    tb_text = START_SPACE.sub('  ', tb_text)
    return tb_text


async def report(
    bot: 'Bot',
    tb_text: str,
    *,
    event: Optional[Event] = None,
    exception: Optional['APICallError'] = None,
):
    tb_text = get_simple_tb_text(tb_text)
    tb_lines = list(chunked(tb_text.split('\n'), 2))
    messages: list[str] = []
    message = ''
    if event:
        message += f"""\
{bold('Event')}
{preformatted(str(event))}
"""
    if exception:
        message += f"""\
{bold('Method')}
{code(exception.method)}
{bold('Data')}
{preformatted(json.dumps(exception.data, ensure_ascii=False, indent=2))}
{bold('Headers')}
{preformatted(json.dumps(exception.headers, ensure_ascii=False, indent=2))}
"""
    message += bold('Traceback')
    message += '\n'
    length = len(message) + 6

    block = ''
    for lines in tb_lines:
        line = '\n'.join(lines)
        if length + len(block) >= LIMIT:
            message += preformatted(block)
            messages.append(message)
            message = ''
            block = ''
            length = 6
        block += '\n'
        block += line
        length += len(line) + 1

    for message in messages:
        await bot.say(
            bot.config.USERS['owner'],
            message,
            length_limit=None,
        )
