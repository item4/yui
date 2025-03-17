import pytest

from yui.apps.owner.quit import quit


@pytest.mark.anyio
async def test_quit_command(bot, owner_id):
    event = bot.create_message(user_id=owner_id)

    with pytest.raises(SystemExit):
        await quit(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == "안녕히 주무세요!"

    event = bot.create_message()

    await quit(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert (
        said.data["text"]
        == f"<@{event.user}> 이 명령어는 아빠만 사용할 수 있어요!"
    )
