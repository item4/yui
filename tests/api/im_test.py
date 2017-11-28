import pytest

from ..util import FakeBot


@pytest.mark.asyncio
async def test_slack_api_im_list():
    bot = FakeBot()

    await bot.api.im.list(cursor='asdf', limit=10)
    call = bot.call_queue.pop()
    assert call.method == 'im.list'
    assert call.data == {
        'cursor': 'asdf',
        'limit': '10',
    }
