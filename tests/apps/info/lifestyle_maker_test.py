from datetime import timedelta

import pytest
from more_itertools import flatten

from yui.apps.info.lifestyle_maker import alert_lifestyle

from ...util import FakeBot
from ...util import assert_crontab_match
from ...util import assert_crontab_spec


def test_alert_spec():
    assert_crontab_spec(alert_lifestyle)


@pytest.mark.parametrize(
    ("delta", "result"),
    flatten(
        [
            (timedelta(days=x, hours=0, minutes=55), False),
            (timedelta(days=x, hours=7, minutes=55), False),
            (timedelta(days=x, hours=8, minutes=55), True),
            (timedelta(days=x, hours=20, minutes=55), True),
            (timedelta(days=x, hours=21, minutes=55), False),
            (timedelta(days=x, hours=23, minutes=55), False),
        ]
        for x in range(7)
    ),
)
def test_alert_match(sunday, delta, result):
    assert_crontab_match(alert_lifestyle, sunday + delta, expected=result)


@pytest.mark.anyio
async def test_alert(bot_config, channel_id):
    bot_config.CHANNELS = {
        "memo": channel_id,
    }
    bot = FakeBot(bot_config)

    await alert_lifestyle(bot)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == channel_id
    assert said.data["text"] == "메모할 시간이에요!"
