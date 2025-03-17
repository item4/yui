import pytest

from yui.apps.weather.commands import weather


@pytest.fixture(name="bot")
async def bot_with_cache(bot, cache):
    async with bot.use_cache(cache):
        yield bot


@pytest.mark.anyio
async def test_weather_command(bot, address):
    event = bot.create_message(ts="1234.5678")

    await weather(bot, event, address)

    weather_said = bot.call_queue.pop(0)

    assert weather_said.method == "chat.postMessage"
    assert weather_said.data["channel"] == event.channel

    if weather_said.data["text"] == "날씨 API 접근 중 에러가 발생했어요!":
        pytest.skip("Can not run test via AWS Weather API")

    assert weather_said.data["thread_ts"] == event.ts
    assert weather_said.data["username"] == "부천 날씨"

    assert weather_said.data["text"] != "해당 주소는 찾을 수 없어요!"
    assert weather_said.data["text"] != "날씨 API 접근 중 에러가 발생했어요!"
    assert weather_said.data["text"] != "해당 이름의 관측소는 존재하지 않아요!"


@pytest.mark.anyio
async def test_weather_command_too_short(bot):
    event = bot.create_message(ts="1234.5678")

    await weather(bot, event, "a")

    weather_said = bot.call_queue.pop(0)

    assert weather_said.method == "chat.postMessage"
    assert weather_said.data["channel"] == event.channel

    if weather_said.data["text"] == "날씨 API 접근 중 에러가 발생했어요!":
        pytest.skip("Can not run test via AWS Weather API")

    assert (
        weather_said.data["text"]
        == "검색어가 너무 짧아요! 2글자 이상의 검색어를 사용해주세요!"
    )


@pytest.mark.anyio
async def test_weather_command_wrong_address(
    bot,
    unavailable_address,
):
    event = bot.create_message(ts="1234.5678")

    await weather(bot, event, unavailable_address)

    weather_said = bot.call_queue.pop(0)

    assert weather_said.method == "chat.postMessage"
    assert weather_said.data["channel"] == event.channel

    if weather_said.data["text"] == "날씨 API 접근 중 에러가 발생했어요!":
        pytest.skip("Can not run test via AWS Weather API")

    assert weather_said.data["text"] == "해당 이름의 관측소는 존재하지 않아요!"


@pytest.mark.anyio
async def test_weather_command_server_error(
    response_mock,
    bot,
    address,
):
    response_mock.get(
        "https://item4.net/api/weather/",
        body="[}",
    )
    event = bot.create_message(ts="1234.5678")

    await weather(bot, event, address)

    weather_said = bot.call_queue.pop(0)

    assert weather_said.method == "chat.postMessage"
    assert weather_said.data["channel"] == event.channel

    assert (
        weather_said.data["text"]
        == "날씨 조회중 에러가 발생했어요! (JSON 파싱 실패)"
    )
