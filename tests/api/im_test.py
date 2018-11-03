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


@pytest.mark.asyncio
async def test_slack_api_im_open():
    bot = FakeBot()
    user = bot.add_user('U1', 'item4')

    await bot.api.im.open(user=user, include_locale=True, return_im=True)
    call = bot.call_queue.pop()
    assert call.method == 'im.open'
    assert call.data == {
        'user': 'U1',
        'include_locale': '1',
        'return_im': '1',
    }

    await bot.api.im.open(user='U1')
    call = bot.call_queue.pop()
    assert call.method == 'im.open'
    assert call.data == {
        'user': 'U1',
    }
