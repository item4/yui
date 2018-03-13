from attrdict import AttrDict

import pytest

from yui.event import create_event
from yui.handlers.answer import RESPONSES, magic_conch

from ..util import FakeBot


@pytest.mark.asyncio
async def test_magic_conch():
    config = AttrDict({
        'PREFIX': '.',
    })
    bot = FakeBot(config)
    bot.add_channel('C1', 'general')

    event = create_event({
        'type': 'message',
        'channel': 'C1',
        'text': '마법의 유이님'
    })

    assert await magic_conch(bot, event)

    assert not bot.call_queue

    event = create_event({
        'type': 'message',
        'channel': 'C1',
        'text': '마법의 소라고둥님'
    })

    assert not await magic_conch(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] in RESPONSES
