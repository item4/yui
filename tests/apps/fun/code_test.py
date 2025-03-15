import pytest
import pytest_asyncio

from yui.apps.fun.code import code_review
from yui.apps.fun.code import write_code_review


@pytest_asyncio.fixture(name="bot")
async def bot_with_cache(bot, cache):
    async with bot.use_cache(cache):
        yield bot


@pytest.mark.asyncio
async def test_write_code_review(bot):
    event = bot.create_message(text="코드 리뷰")
    await write_code_review(bot, event, seed=100)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel

    attachments = said.data["attachments"]

    assert len(attachments) == 1
    assert (
        attachments[0]["fallback"]
        == attachments[0]["image_url"]
        == "https://i.imgur.com/btkBRvc.png"
    )


@pytest.mark.asyncio
async def test_code_review(bot, channel_id):
    event = bot.create_message(channel_id=channel_id, text="영화 리뷰")

    assert await code_review(bot, event)

    last_call = await bot.cache.get(f"YUI_APPS_FUN_CODE_REVIEW_{event.channel}")
    assert last_call is None

    assert not bot.call_queue

    event = bot.create_message(channel_id=channel_id, text="코드 리뷰")

    assert not await code_review(bot, event)

    last_call = await bot.cache.get(f"YUI_APPS_FUN_CODE_REVIEW_{event.channel}")
    assert isinstance(last_call, float)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert len(said.data["attachments"]) == 1

    event = bot.create_message(channel_id=channel_id, text="코드 리뷰")

    assert await code_review(bot, event)
