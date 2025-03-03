import re

import aiohttp
import pytest
from yarl import URL

from yui.apps.animal import APIServerError
from yui.apps.animal import cat
from yui.apps.animal import dog
from yui.apps.animal import fox
from yui.apps.animal import get_cat_image_url
from yui.apps.animal import get_dog_image_url
from yui.apps.animal import get_fox_image_url

cat_cooltime_re = re.compile(
    r"아직 쿨타임이다냥! \d+시 \d+분 이후로 다시 시도해보라냥!",
)
dog_cooltime_re = re.compile(
    r"아직 쿨타임이다멍! \d+시 \d+분 이후로 다시 시도해보라멍!",
)
fox_cooltime_re = re.compile(
    r"아직 쿨타임이에요! \d+시 \d+분 이후로 다시 시도해보세요!",
)


CAT_API_URL = URL("https://thecatapi.com/api/images/get").with_query(
    format="xml",
    type="jpg,png",
)


@pytest.mark.asyncio
async def test_get_cat_image_url(response_mock):
    response_mock.get(
        CAT_API_URL,
        status=500,
    )
    response_mock.get(
        CAT_API_URL,
        exception=aiohttp.client_exceptions.ServerDisconnectedError(),
    )
    response_mock.get(
        CAT_API_URL,
        body=(
            '<?xml version="1.0"?>'
            "<response><data><images><image>"
            "<url>http://cat.com/404.jpg</url>"
            "<id>cdu</id>"
            "<source_url>http://thecatapi.com/?id=cdu</source_url>"
            "</image></images></data></response>"
        ),
        headers={"Content-Type": "text/xml"},
    )
    response_mock.get(
        CAT_API_URL,
        body=(
            '<?xml version="1.0"?>'
            "<response><data><images><image>"
            "<url>http://cannotresolve.com/200.jpg</url>"
            "<id>cdu</id>"
            "<source_url>http://thecatapi.com/?id=cdu</source_url>"
            "</image></images></data></response>"
        ),
        headers={"Content-Type": "text/xml"},
    )
    response_mock.get(
        CAT_API_URL,
        body=(
            '<?xml version="1.0"?>'
            "<response><data><images><image>"
            "<url>http://timeout.com/200.jpg</url>"
            "<id>cdu</id>"
            "<source_url>http://thecatapi.com/?id=cdu</source_url>"
            "</image></images></data></response>"
        ),
        headers={"Content-Type": "text/xml"},
    )
    response_mock.get(
        CAT_API_URL,
        body=(
            '<?xml version="1.0"?>'
            "<response><data><images><image>"
            "<url>http://cat.com/200.jpg</url>"
            "<id>cdu</id>"
            "<source_url>http://thecatapi.com/?id=cdu</source_url>"
            "</image></images></data></response>"
        ),
        headers={"Content-Type": "text/xml"},
    )
    response_mock.get(
        "http://cannotresolve.com/200.jpg",
        exception=aiohttp.ClientConnectorError(None, OSError()),
    )
    response_mock.get(
        "http://timeout.com/200.jpg",
        exception=TimeoutError(),
    )
    response_mock.get("http://cat.com/404.jpg", status=404)
    response_mock.get("http://cat.com/200.jpg")

    with pytest.raises(APIServerError):
        await get_cat_image_url(0.001)

    url = await get_cat_image_url(0.001)
    assert url == "http://cat.com/200.jpg"


@pytest.mark.asyncio
async def test_get_dog_image_url(response_mock):
    response_mock.get(
        "https://dog.ceo/api/breeds/image/random",
        status=500,
    )
    response_mock.get(
        "https://dog.ceo/api/breeds/image/random",
        exception=aiohttp.client_exceptions.ServerDisconnectedError(),
    )
    response_mock.get(
        "https://dog.ceo/api/breeds/image/random",
        payload={"status": "success", "message": "http://dog.com/404.jpg"},
    )
    response_mock.get(
        "https://dog.ceo/api/breeds/image/random",
        payload={
            "status": "success",
            "message": "http://cannotresolve.com/200.jpg",
        },
    )
    response_mock.get(
        "https://dog.ceo/api/breeds/image/random",
        payload={"status": "success", "message": "http://timeout.com/200.jpg"},
    )
    response_mock.get(
        "https://dog.ceo/api/breeds/image/random",
        payload={"status": "success", "message": "http://dog.com/200.jpg"},
    )
    response_mock.get(
        "http://cannotresolve.com/200.jpg",
        exception=aiohttp.ClientConnectorError(None, OSError()),
    )
    response_mock.get(
        "http://timeout.com/200.jpg",
        exception=TimeoutError(),
    )
    response_mock.get("http://dog.com/404.jpg", status=404)
    response_mock.get("http://dog.com/200.jpg")

    with pytest.raises(APIServerError):
        await get_dog_image_url(0.001)

    url = await get_dog_image_url(0.001)
    assert url == "http://dog.com/200.jpg"


@pytest.mark.asyncio
async def test_get_fox_image_url(response_mock):
    response_mock.get(
        "http://fox-info.net/fox-gallery",
        body="<!doctype html><html></html>",
        headers={"Content-Type": "text/html"},
    )
    response_mock.get(
        "http://fox-info.net/fox-gallery",
        body=(
            '<div id="gallery-1">'
            '<img src="http://fox.com/img1.png" class="attachment-thumbnail">'
            '<img src="http://fox.com/img2.png" class="attachment-thumbnail">'
            '<img src="http://fox.com/img3.png" class="attachment-thumbnail">'
            "</div>"
        ),
        headers={"Content-Type": "text/html"},
    )
    with pytest.raises(APIServerError):
        await get_fox_image_url(0.001)

    url = await get_fox_image_url(0.001)
    assert url == "http://fox.com/img1.png"


@pytest.mark.asyncio
async def test_cat_command(bot, response_mock):
    response_mock.get(
        CAT_API_URL,
        status=500,
    )
    response_mock.get(
        CAT_API_URL,
        body=(
            '<?xml version="1.0"?>'
            "<response><data><images><image>"
            "<url>http://cat.com/200.jpg</url>"
            "<id>cdu</id>"
            "<source_url>http://thecatapi.com/?id=cdu</source_url>"
            "</image></images></data></response>"
        ),
        headers={"Content-Type": "text/xml"},
    )
    response_mock.get(
        CAT_API_URL,
        status=500,
    )
    response_mock.get(
        CAT_API_URL,
        body=(
            '<?xml version="1.0"?>'
            "<response><data><images><image>"
            "<url>http://cat.com/200.jpg</url>"
            "<id>cdu</id>"
            "<source_url>http://thecatapi.com/?id=cdu</source_url>"
            "</image></images></data></response>"
        ),
        headers={"Content-Type": "text/xml"},
    )
    response_mock.get("http://cat.com/200.jpg")
    response_mock.get("http://cat.com/200.jpg")

    event = bot.create_message()

    assert cat.last_call.get(event.channel) is None

    await cat(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert (
        said.data["text"]
        == "냥냥이 API 서버의 상태가 좋지 않다냥! 나중에 다시 시도해보라냥!"
    )
    assert said.data["username"] == "냥짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/hIBJUMI.jpg"

    assert cat.last_call.get(event.channel) is None

    await cat(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == "http://cat.com/200.jpg"
    assert said.data["username"] == "냥짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/hIBJUMI.jpg"

    assert cat.last_call[event.channel]

    await cat(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert cat_cooltime_re.match(said.data["text"])
    assert said.data["username"] == "냥짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/hIBJUMI.jpg"

    event = bot.create_message(channel_id="D1")

    assert cat.last_call.get(event.channel) is None

    await cat(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert (
        said.data["text"]
        == "냥냥이 API 서버의 상태가 좋지 않다냥! 나중에 다시 시도해보라냥!"
    )
    assert said.data["username"] == "냥짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/hIBJUMI.jpg"

    assert cat.last_call.get(event.channel) is None

    await cat(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == "http://cat.com/200.jpg"
    assert said.data["username"] == "냥짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/hIBJUMI.jpg"

    assert cat.last_call[event.channel]

    await cat(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert cat_cooltime_re.match(said.data["text"])
    assert said.data["username"] == "냥짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/hIBJUMI.jpg"


@pytest.mark.asyncio
async def test_dog_command(bot, response_mock):
    response_mock.get(
        "https://dog.ceo/api/breeds/image/random",
        status=500,
    )
    response_mock.get(
        "https://dog.ceo/api/breeds/image/random",
        payload={"status": "success", "message": "http://dog.com/200.jpg"},
    )
    response_mock.get(
        "https://dog.ceo/api/breeds/image/random",
        status=500,
    )
    response_mock.get(
        "https://dog.ceo/api/breeds/image/random",
        payload={"status": "success", "message": "http://dog.com/200.jpg"},
    )
    response_mock.get("http://dog.com/200.jpg")
    response_mock.get("http://dog.com/200.jpg")

    event = bot.create_message()

    assert dog.last_call.get(event.channel) is None

    await dog(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert (
        said.data["text"]
        == "멍멍이 API 서버의 상태가 좋지 않다멍! 나중에 다시 시도해보라멍!"
    )
    assert said.data["username"] == "멍짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/Q9FKplO.png"

    assert dog.last_call.get(event.channel) is None

    await dog(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == "http://dog.com/200.jpg"
    assert said.data["username"] == "멍짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/Q9FKplO.png"

    assert dog.last_call[event.channel]

    await dog(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert dog_cooltime_re.match(said.data["text"])
    assert said.data["username"] == "멍짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/Q9FKplO.png"

    event = bot.create_message(channel_id="D1")

    assert dog.last_call.get(event.channel) is None

    await dog(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert (
        said.data["text"]
        == "멍멍이 API 서버의 상태가 좋지 않다멍! 나중에 다시 시도해보라멍!"
    )
    assert said.data["username"] == "멍짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/Q9FKplO.png"

    assert dog.last_call.get(event.channel) is None

    await dog(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == "http://dog.com/200.jpg"
    assert said.data["username"] == "멍짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/Q9FKplO.png"

    assert dog.last_call[event.channel]

    await dog(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert dog_cooltime_re.match(said.data["text"])
    assert said.data["username"] == "멍짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/Q9FKplO.png"


@pytest.mark.asyncio
async def test_fox_command(bot, response_mock):
    response_mock.get(
        "http://fox-info.net/fox-gallery",
        body="<!doctype html><html></html>",
        headers={"Content-Type": "text/html"},
    )
    response_mock.get(
        "http://fox-info.net/fox-gallery",
        body=(
            '<div id="gallery-1">'
            '<img src="http://fox.com/img1.png" class="attachment-thumbnail">'
            '<img src="http://fox.com/img2.png" class="attachment-thumbnail">'
            '<img src="http://fox.com/img3.png" class="attachment-thumbnail">'
            "</div>"
        ),
        headers={"Content-Type": "text/html"},
    )
    response_mock.get(
        "http://fox-info.net/fox-gallery",
        body="<!doctype html><html></html>",
        headers={"Content-Type": "text/html"},
    )
    response_mock.get(
        "http://fox-info.net/fox-gallery",
        body=(
            '<div id="gallery-1">'
            '<img src="http://fox.com/img1.png" class="attachment-thumbnail">'
            '<img src="http://fox.com/img2.png" class="attachment-thumbnail">'
            '<img src="http://fox.com/img3.png" class="attachment-thumbnail">'
            "</div>"
        ),
        headers={"Content-Type": "text/html"},
    )

    event = bot.create_message()

    assert fox.last_call.get(event.channel) is None

    await fox(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert (
        said.data["text"]
        == "여우짤 서버의 상태가 좋지 않네요! 나중에 다시 시도해보세요!"
    )
    assert said.data["username"] == "웹 브라우저의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/xFpyvpZ.png"

    assert fox.last_call.get(event.channel) is None

    await fox(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == "http://fox.com/img1.png"
    assert said.data["username"] == "웹 브라우저의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/xFpyvpZ.png"

    assert fox.last_call[event.channel]

    await fox(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert fox_cooltime_re.match(said.data["text"])
    assert said.data["username"] == "웹 브라우저의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/xFpyvpZ.png"

    event = bot.create_message(channel_id="D1")

    assert fox.last_call.get(event.channel) is None

    await fox(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert (
        said.data["text"]
        == "여우짤 서버의 상태가 좋지 않네요! 나중에 다시 시도해보세요!"
    )
    assert said.data["username"] == "웹 브라우저의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/xFpyvpZ.png"

    assert fox.last_call.get(event.channel) is None

    await fox(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == "http://fox.com/img1.png"
    assert said.data["username"] == "웹 브라우저의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/xFpyvpZ.png"

    assert fox.last_call[event.channel]

    await fox(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert fox_cooltime_re.match(said.data["text"])
    assert said.data["username"] == "웹 브라우저의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/xFpyvpZ.png"
