import pytest

from yui.apps.search.dic import dic


@pytest.mark.asyncio()
async def test_dic_redirect(
    bot,
):
    event = bot.create_message("C1", "U1", "1234.5678")

    await dic(bot, event, "영어", "apple")

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert (
        said.data["text"]
        == "https://dic.daum.net/word/view.do?wordid=ekw000008211&q=apple"
    )
