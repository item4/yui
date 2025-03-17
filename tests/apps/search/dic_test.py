import re

import pytest

from yui.apps.search.dic import dic

MULTIPLE_PATTERN = re.compile(r"검색결과 (\d+)개의 링크를 찾았어요!")


@pytest.mark.anyio
async def test_dic_multiple(
    bot,
):
    event = bot.create_message(ts="1234.5678")

    await dic(bot, event, "영어", "bad")

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    matched = MULTIPLE_PATTERN.match(said.data["text"])
    assert matched
    assert int(matched[1]) == len(said.data["attachments"])


@pytest.mark.anyio
async def test_dic_redirect(
    bot,
):
    event = bot.create_message(ts="1234.5678")

    await dic(bot, event, "영어", "apple")

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert (
        said.data["text"]
        == "https://dic.daum.net/word/view.do?wordid=ekw000008211&q=apple"
    )
