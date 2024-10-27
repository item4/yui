import pytest

from yui.apps.owner.update import FLAG_MAP
from yui.apps.owner.update import update

from ...util import FakeBot


@pytest.mark.asyncio
async def test_update_command(bot_config, channel_id):
    bot_config.USERS["owner"] = "U1"
    bot_config.CHANNELS["notice"] = channel_id
    bot = FakeBot(bot_config)

    event = bot.create_message("C1", "U1")

    await update(
        bot,
        event,
        """
TITLE=패치
FLAG=PATCH
LINK=<https://item4.github.io>
본문1
본문2
본문3
---
TITLE=테스트
FLAG=test
- 테스트 코드가 작성되었습니다.
---
TITLE=새 기능
FLAG=NEW
1. 리스트1
2. 리스트2
3. 리스트3
---
TITLE=위험
FLAG=DANGER
- 위험
- 위험!
- 위험!!
---
TITLE=커스텀
COLOR=123456
임의의 색상 지정
PRETEXT=유이 업데이트 명령 테스트
---
---
본문만 있음
---
TITLE=타이틀만 있음
""",
    )
    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == channel_id
    assert said.data["text"] == "유이 업데이트 명령 테스트"
    assert said.data["attachments"] == [
        {
            "fallback": "[patch] 패치: 본문1 본문2 본문3",
            "title": "[patch] 패치",
            "title_link": "https://item4.github.io",
            "color": FLAG_MAP["patch"],
            "text": "본문1\n본문2\n본문3",
        },
        {
            "fallback": "[test] 테스트: - 테스트 코드가 작성되었습니다.",
            "title": "[test] 테스트",
            "color": FLAG_MAP["test"],
            "text": "- 테스트 코드가 작성되었습니다.",
        },
        {
            "fallback": "[new] 새 기능: 1. 리스트1 2. 리스트2 3. 리스트3",
            "title": "[new] 새 기능",
            "color": FLAG_MAP["new"],
            "text": "1. 리스트1\n2. 리스트2\n3. 리스트3",
        },
        {
            "fallback": "[danger] 위험: - 위험 - 위험! - 위험!!",
            "title": "[danger] 위험",
            "color": FLAG_MAP["danger"],
            "text": "- 위험\n- 위험!\n- 위험!!",
        },
        {
            "fallback": "커스텀: 임의의 색상 지정",
            "title": "커스텀",
            "color": "123456",
            "text": "임의의 색상 지정",
        },
        {
            "fallback": "본문만 있음",
            "text": "본문만 있음",
        },
        {
            "fallback": "타이틀만 있음:",
            "title": "타이틀만 있음",
        },
    ]

    event = bot.create_message("C1", "U2")

    await update(bot, event, "")

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == "<@U2> 이 명령어는 아빠만 사용할 수 있어요!"
