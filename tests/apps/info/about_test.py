import pytest

from yui.apps.info.about import MESSAGE, about
from yui.event import create_event

from ...util import FakeBot


@pytest.mark.asyncio
async def test_about_command():
    bot = FakeBot()
    bot.add_channel('C1', 'general')
    event = create_event({
        'type': 'message',
        'channel': 'C1',
        'ts': '1234.56',
    })

    await about(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == MESSAGE.format(prefix=bot.config.PREFIX)
    assert said.data['thread_ts'] == '1234.56'
