from datetime import timedelta

import pytest

from yui.apps.info.lifestyle_maker import alert_lifestyle

from ...util import FakeBot


def test_alert_spec():
    assert alert_lifestyle.has_valid_spec


def test_alert_match(sunday):
    for days in range(7):
        for hours in range(8):
            assert not alert_lifestyle.match(
                sunday + timedelta(days=days, hours=hours),
            )
            assert not alert_lifestyle.match(
                sunday + timedelta(days=days, hours=hours, minutes=55),
            )
        for hours in range(8, 21):
            assert not alert_lifestyle.match(
                sunday + timedelta(days=days, hours=hours),
            )
            assert alert_lifestyle.match(
                sunday + timedelta(days=days, hours=hours, minutes=55),
            )
        for hours in range(21, 24):
            assert not alert_lifestyle.match(
                sunday + timedelta(days=days, hours=hours),
            )
            assert not alert_lifestyle.match(
                sunday + timedelta(days=days, hours=hours, minutes=55),
            )


@pytest.mark.asyncio
async def test_alert(bot_config):
    bot_config.CHANNELS = {
        "memo": "C1",
    }
    bot = FakeBot(bot_config)
    bot.add_channel("C1", "lifestyle")

    await alert_lifestyle(bot)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "메모할 시간이에요!"
