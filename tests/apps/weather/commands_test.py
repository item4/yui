import asyncio

import pytest

from tests.util import FakeBot

from yui.apps.weather.commands import weather


@pytest.mark.asyncio()
async def test_weather_command(bot_config, cache, address):
    bot = FakeBot(bot_config, loop=asyncio.get_running_loop(), cache=cache)
    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")

    event = bot.create_message("C1", "U1", "1234.5678")

    async with bot.begin():
        await weather(bot, event, address)

    weather_said = bot.call_queue.pop(0)

    assert weather_said.method == "chat.postMessage"
    assert weather_said.data["channel"] == "C1"

    if weather_said.data["text"] == "날씨 API 접근 중 에러가 발생했어요!":
        pytest.skip("Can not run test via AWS Weather API")

    assert weather_said.data["thread_ts"] == "1234.5678"
    assert weather_said.data["username"] == "부천 날씨"

    assert weather_said.data["text"] != "해당 주소는 찾을 수 없어요!"
    assert weather_said.data["text"] != "날씨 API 접근 중 에러가 발생했어요!"
    assert weather_said.data["text"] != "해당 이름의 관측소는 존재하지 않아요!"
