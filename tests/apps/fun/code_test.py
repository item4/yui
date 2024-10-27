import pytest

from yui.apps.fun.code import code_review
from yui.apps.fun.code import write_code_review


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

    assert not bot.call_queue

    event = bot.create_message(channel_id=channel_id, text="코드 리뷰")

    assert not await code_review(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert len(said.data["attachments"]) == 1

    event = bot.create_message(channel_id=channel_id, text="코드 리뷰")

    assert await code_review(bot, event)
