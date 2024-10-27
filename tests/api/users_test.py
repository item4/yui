import pytest

from yui.api.encoder import bool2str


@pytest.mark.asyncio
async def test_slack_api_users_info(bot):
    user_id = "U1234"
    user = bot.create_user(user_id, "item4")

    await bot.api.users.info(user_id)

    call = bot.call_queue.pop()
    assert call.method == "users.info"
    assert call.data == {"user": user_id}

    await bot.api.users.info(user)

    call = bot.call_queue.pop()
    assert call.method == "users.info"
    assert call.data == {"user": user_id}


@pytest.mark.asyncio
async def test_slack_api_users_list(bot):
    await bot.api.users.list(
        curser="asdf1234",
        include_locale=True,
        limit=20,
        presence=True,
    )

    call = bot.call_queue.pop()
    assert call.method == "users.list"
    assert call.data == {
        "cursor": "asdf1234",
        "include_locale": bool2str(True),
        "limit": "20",
        "presence": bool2str(True),
    }
