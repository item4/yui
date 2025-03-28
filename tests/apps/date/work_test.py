from datetime import timedelta

import pytest
from time_machine import travel

from yui.apps.date.utils import APIDoesNotSupport
from yui.apps.date.utils import get_holiday_names
from yui.apps.date.work import work_end
from yui.apps.date.work import work_start
from yui.utils.datetime import datetime
from yui.utils.datetime import now

from ...util import FakeBot
from ...util import assert_crontab_match
from ...util import assert_crontab_spec


@pytest.fixture(autouse=True)
async def _api_server_check(anyio_backend):
    try:
        await get_holiday_names(now())
    except APIDoesNotSupport:
        pytest.skip("API server is not available")


@pytest.fixture
def bot(bot_config, channel_id):
    bot_config.CHANNELS["general"] = channel_id
    return FakeBot(bot_config)


@pytest.fixture(scope="session")
def sunday_9(sunday):
    return sunday + timedelta(hours=9)


@pytest.fixture(scope="session")
def sunday_18(sunday):
    return sunday + timedelta(hours=18)


@pytest.fixture(scope="session")
def sunday_19(sunday):
    return sunday + timedelta(hours=19)


def test_work_start_task_spec():
    assert_crontab_spec(work_start)


@pytest.mark.parametrize(
    ("delta", "result"),
    [
        (timedelta(days=0), False),
        (timedelta(days=1), True),
        (timedelta(days=1, minutes=11), False),
        (timedelta(days=2), True),
        (timedelta(days=3), True),
        (timedelta(days=4), True),
        (timedelta(days=5), True),
        (timedelta(days=6), False),
    ],
)
def test_work_start_task_match(sunday_9, delta, result):
    assert_crontab_match(work_start, sunday_9 + delta, expected=result)


def test_work_end_task_spec():
    assert_crontab_spec(work_end)


@pytest.mark.parametrize(
    ("delta", "result"),
    [
        (timedelta(days=0), False),
        (timedelta(days=1), True),
        (timedelta(days=1, minutes=11), False),
        (timedelta(days=2), True),
        (timedelta(days=3), True),
        (timedelta(days=4), True),
        (timedelta(days=5), True),
        (timedelta(days=6), False),
    ],
)
def test_work_end_task_match_at_18(sunday_18, delta, result):
    assert_crontab_match(work_end, sunday_18 + delta, expected=result)


@pytest.mark.parametrize(
    ("delta", "result"),
    [
        (timedelta(days=0), False),
        (timedelta(days=1), True),
        (timedelta(days=1, minutes=11), False),
        (timedelta(days=2), True),
        (timedelta(days=3), True),
        (timedelta(days=4), True),
        (timedelta(days=5), True),
        (timedelta(days=6), False),
    ],
)
def test_work_end_task_match_at_19(sunday_19, delta, result):
    assert_crontab_match(work_end, sunday_19 + delta, expected=result)


@pytest.mark.anyio
@travel(datetime(2018, 10, 8, 9), tick=False)
async def test_work_start_monday(bot, channel_id):
    await work_start(bot)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == channel_id
    assert said.data["username"] == "현실부정중인 직장인"
    assert said.data["attachments"]


@pytest.mark.anyio
@travel(datetime(2018, 10, 10, 9), tick=False)
async def test_work_start_normal(bot, channel_id):
    await work_start(bot)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == channel_id
    assert said.data["username"] == "노동자 핫산"
    assert (
        said.data["text"]
        == "한국인들은 세계 누구보다 출근을 사랑하면서 왜 본심을 숨기는 걸까?"
    )


@pytest.mark.anyio
@travel(datetime(2018, 10, 9, 9), tick=False)
async def test_work_start_holiday(bot, channel_id):
    await work_start(bot)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == channel_id
    assert said.data["username"] == "너굴맨"
    assert (
        said.data["text"]
        == "오늘은 한글날! 출근하라는 상사는 이 너굴맨이 처리했으니 안심하라구!"
    )


@pytest.mark.anyio
@travel(datetime(2018, 10, 8, 18), tick=False)
async def test_work_end_18_normal(bot, channel_id):
    await work_end(bot)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == channel_id
    assert said.data["username"] == "칼퇴의 요정"
    assert (
        said.data["text"]
        == "6시가 되었습니다. 9시에 출근하신 분들은 칼같이 퇴근하시길 바랍니다."
    )


@pytest.mark.anyio
@travel(datetime(2018, 10, 9, 18), tick=False)
async def test_work_end_18_holiday(bot, channel_id):
    await work_end(bot)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == channel_id
    assert said.data["username"] == "집사가 집에 있어서 기분 좋은 고양이"
    assert (
        said.data["text"]
        == "한글날 만세! 6시인데 집사 퇴근 안 기다려도 되니까 좋다냥!"
    )


@pytest.mark.anyio
@travel(datetime(2018, 10, 8, 19), tick=False)
async def test_work_end_19_normal(bot, channel_id):
    await work_end(bot)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == channel_id
    assert said.data["username"] == "칼퇴의 요정"
    assert (
        said.data["text"]
        == "7시가 되었습니다. 10시에 출근하신 분들은 칼같이 퇴근하시길 바랍니다."
    )


@pytest.mark.anyio
@travel(datetime(2018, 10, 9, 19), tick=False)
async def test_work_end_19_holiday(bot, channel_id):
    await work_end(bot)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == channel_id
    assert said.data["username"] == "집사가 집에 있어서 기분 좋은 고양이"
    assert (
        said.data["text"]
        == "한글날 만세! 7시인데 집사 퇴근 안 기다려도 되니까 좋다냥!"
    )
