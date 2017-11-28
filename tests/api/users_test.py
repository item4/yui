import pytest

from ..util import FakeBot


@pytest.mark.asyncio
async def test_slack_api_users_info():
    user = 'U1234'

    bot = FakeBot()

    await bot.api.users.info(user)

    call = bot.call_queue.pop()
    assert call.method == 'users.info'
    assert call.data == {'user': user}
