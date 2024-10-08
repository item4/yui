import pytest

from yui.apps.fun.code import code_review
from yui.apps.fun.code import write_code_review


@pytest.mark.asyncio
async def test_write_code_review(bot):
    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")

    event = bot.create_message("C1", "U1", text="코드 리뷰")
    await write_code_review(bot, event, seed=100)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"

    attachments = said.data["attachments"]

    assert len(attachments) == 1
    assert (
        attachments[0]["fallback"]
        == attachments[0]["image_url"]
        == "https://i.imgur.com/btkBRvc.png"
    )


@pytest.mark.asyncio
async def test_code_review(bot):
    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")

    event = bot.create_message("C1", "U1", text="영화 리뷰")

    assert await code_review(bot, event)

    assert not bot.call_queue

    event = bot.create_message("C1", "U1", text="코드 리뷰")

    assert not await code_review(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert len(said.data["attachments"]) == 1

    event = bot.create_message("C1", "U1", text="코드 리뷰")

    assert await code_review(bot, event)
