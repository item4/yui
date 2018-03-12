from attrdict import AttrDict

import pytest

from yui.event import create_event
from yui.handlers.about import MESSAGE, about

from ..util import FakeBot


@pytest.mark.asyncio
async def test_about_command():
    config = AttrDict({
        'PREFIX': '.',
    })
    bot = FakeBot(config)
    bot.add_channel('C1', 'general')
    bot.add_user('U1', 'kirito')
    event = create_event({
        'type': 'message',
        'channel': 'C1',
    })

    await about(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == MESSAGE.format(prefix=config.PREFIX)
