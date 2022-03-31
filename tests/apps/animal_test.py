import asyncio
import re

import aiohttp

import pytest

from yui.apps.animal import APIServerError
from yui.apps.animal import cat
from yui.apps.animal import dog
from yui.apps.animal import fox
from yui.apps.animal import get_cat_image_url
from yui.apps.animal import get_dog_image_url
from yui.apps.animal import get_fox_image_url
from yui.utils import json


cat_cooltime_re = re.compile(r"아직 쿨타임이다냥! \d+시 \d+분 이후로 다시 시도해보라냥!")
dog_cooltime_re = re.compile(r"아직 쿨타임이다멍! \d+시 \d+분 이후로 다시 시도해보라멍!")
fox_cooltime_re = re.compile(r"아직 쿨타임이에요! \d+시 \d+분 이후로 다시 시도해보세요!")


@pytest.mark.asyncio
async def test_get_cat_image_url(response_mock):
    response_mock.get(
        "http://thecatapi.com/api/images/get?format=xml&type=jpg,png",
        body="",
        status=500,
    )
    response_mock.get(
        "http://thecatapi.com/api/images/get?format=xml&type=jpg,png",
        exception=aiohttp.client_exceptions.ServerDisconnectedError(),
    )
    response_mock.get(
        "http://thecatapi.com/api/images/get?format=xml&type=jpg,png",
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
        "http://thecatapi.com/api/images/get?format=xml&type=jpg,png",
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
        "http://thecatapi.com/api/images/get?format=xml&type=jpg,png",
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
        "http://thecatapi.com/api/images/get?format=xml&type=jpg,png",
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
        exception=asyncio.TimeoutError(),
    )
    response_mock.get("http://cat.com/404.jpg", status=404)
    response_mock.get("http://cat.com/200.jpg", status=200)

    with pytest.raises(APIServerError):
        await get_cat_image_url(0.001)

    url = await get_cat_image_url(0.001)
    assert url == "http://cat.com/200.jpg"


@pytest.mark.asyncio
async def test_get_dog_image_url(response_mock):
    response_mock.get(
        "https://dog.ceo/api/breeds/image/random",
        body="",
        status=500,
    )
    response_mock.get(
        "https://dog.ceo/api/breeds/image/random",
        exception=aiohttp.client_exceptions.ServerDisconnectedError(),
    )
    response_mock.get(
        "https://dog.ceo/api/breeds/image/random",
        body=json.dumps(
            {"status": "success", "message": "http://dog.com/404.jpg"}
        ),
        headers={"Content-Type": "application/json"},
    )
    response_mock.get(
        "https://dog.ceo/api/breeds/image/random",
        body=json.dumps(
            {
                "status": "success",
                "message": "http://cannotresolve.com/200.jpg",
            }
        ),
        headers={"Content-Type": "application/json"},
    )
    response_mock.get(
        "https://dog.ceo/api/breeds/image/random",
        body=json.dumps(
            {"status": "success", "message": "http://timeout.com/200.jpg"}
        ),
        headers={"Content-Type": "application/json"},
    )
    response_mock.get(
        "https://dog.ceo/api/breeds/image/random",
        body=json.dumps(
            {"status": "success", "message": "http://dog.com/200.jpg"}
        ),
        headers={"Content-Type": "application/json"},
    )
    response_mock.get(
        "http://cannotresolve.com/200.jpg",
        exception=aiohttp.ClientConnectorError(None, OSError()),
    )
    response_mock.get(
        "http://timeout.com/200.jpg",
        exception=asyncio.TimeoutError(),
    )
    response_mock.get("http://dog.com/404.jpg", status=404)
    response_mock.get("http://dog.com/200.jpg", status=200)

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
        "http://thecatapi.com/api/images/get?format=xml&type=jpg,png",
        body="",
        status=500,
    )
    response_mock.get(
        "http://thecatapi.com/api/images/get?format=xml&type=jpg,png",
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
        "http://thecatapi.com/api/images/get?format=xml&type=jpg,png",
        body="",
        status=500,
    )
    response_mock.get(
        "http://thecatapi.com/api/images/get?format=xml&type=jpg,png",
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
    response_mock.get("http://cat.com/200.jpg", status=200)
    response_mock.get("http://cat.com/200.jpg", status=200)

    bot.add_channel("C1", "general")
    user = bot.add_user("U1", "kirito")
    bot.add_dm("D1", user)

    event = bot.create_message("C1", "U1")

    assert cat.last_call.get("C1") is None

    await cat(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == ("냥냥이 API 서버의 상태가 좋지 않다냥! 나중에 다시 시도해보라냥!")
    assert not said.data["as_user"]
    assert said.data["username"] == "냥짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/hIBJUMI.jpg"

    assert cat.last_call.get("C1") is None

    await cat(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "http://cat.com/200.jpg"
    assert not said.data["as_user"]
    assert said.data["username"] == "냥짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/hIBJUMI.jpg"

    assert cat.last_call["C1"]

    await cat(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert cat_cooltime_re.match(said.data["text"])
    assert not said.data["as_user"]
    assert said.data["username"] == "냥짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/hIBJUMI.jpg"

    event = event = bot.create_message("D1", "U1")

    assert cat.last_call.get("D1") is None

    await cat(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "D1"
    assert said.data["text"] == ("냥냥이 API 서버의 상태가 좋지 않다냥! 나중에 다시 시도해보라냥!")
    assert not said.data["as_user"]
    assert said.data["username"] == "냥짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/hIBJUMI.jpg"

    assert cat.last_call.get("D1") is None

    await cat(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "D1"
    assert said.data["text"] == "http://cat.com/200.jpg"
    assert not said.data["as_user"]
    assert said.data["username"] == "냥짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/hIBJUMI.jpg"

    assert cat.last_call["D1"]

    await cat(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "D1"
    assert cat_cooltime_re.match(said.data["text"])
    assert not said.data["as_user"]
    assert said.data["username"] == "냥짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/hIBJUMI.jpg"


@pytest.mark.asyncio
async def test_dog_command(bot, response_mock):
    response_mock.get(
        "https://dog.ceo/api/breeds/image/random",
        body="",
        status=500,
    )
    response_mock.get(
        "https://dog.ceo/api/breeds/image/random",
        body=json.dumps(
            {"status": "success", "message": "http://dog.com/200.jpg"}
        ),
        headers={"Content-Type": "application/json"},
    )
    response_mock.get(
        "https://dog.ceo/api/breeds/image/random",
        body="",
        status=500,
    )
    response_mock.get(
        "https://dog.ceo/api/breeds/image/random",
        body=json.dumps(
            {"status": "success", "message": "http://dog.com/200.jpg"}
        ),
        headers={"Content-Type": "application/json"},
    )
    response_mock.get("http://dog.com/200.jpg", status=200)
    response_mock.get("http://dog.com/200.jpg", status=200)

    bot.add_channel("C1", "general")
    user = bot.add_user("U1", "kirito")
    bot.add_dm("D1", user)

    event = bot.create_message("C1", "U1")

    assert dog.last_call.get("C1") is None

    await dog(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == ("멍멍이 API 서버의 상태가 좋지 않다멍! 나중에 다시 시도해보라멍!")
    assert not said.data["as_user"]
    assert said.data["username"] == "멍짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/Q9FKplO.png"

    assert dog.last_call.get("C1") is None

    await dog(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "http://dog.com/200.jpg"
    assert not said.data["as_user"]
    assert said.data["username"] == "멍짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/Q9FKplO.png"

    assert dog.last_call["C1"]

    await dog(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert dog_cooltime_re.match(said.data["text"])
    assert not said.data["as_user"]
    assert said.data["username"] == "멍짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/Q9FKplO.png"

    event = bot.create_message("D1", "U1")

    assert dog.last_call.get("D1") is None

    await dog(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "D1"
    assert said.data["text"] == ("멍멍이 API 서버의 상태가 좋지 않다멍! 나중에 다시 시도해보라멍!")
    assert not said.data["as_user"]
    assert said.data["username"] == "멍짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/Q9FKplO.png"

    assert dog.last_call.get("D1") is None

    await dog(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "D1"
    assert said.data["text"] == "http://dog.com/200.jpg"
    assert not said.data["as_user"]
    assert said.data["username"] == "멍짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/Q9FKplO.png"

    assert dog.last_call["D1"]

    await dog(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "D1"
    assert dog_cooltime_re.match(said.data["text"])
    assert not said.data["as_user"]
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

    bot.add_channel("C1", "general")
    user = bot.add_user("U1", "kirito")
    bot.add_dm("D1", user)

    event = bot.create_message("C1", "U1")

    assert fox.last_call.get("C1") is None

    await fox(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == ("여우짤 서버의 상태가 좋지 않네요! 나중에 다시 시도해보세요!")
    assert not said.data["as_user"]
    assert said.data["username"] == "웹 브라우저의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/xFpyvpZ.png"

    assert fox.last_call.get("C1") is None

    await fox(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "http://fox.com/img1.png"
    assert not said.data["as_user"]
    assert said.data["username"] == "웹 브라우저의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/xFpyvpZ.png"

    assert fox.last_call["C1"]

    await fox(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert fox_cooltime_re.match(said.data["text"])
    assert not said.data["as_user"]
    assert said.data["username"] == "웹 브라우저의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/xFpyvpZ.png"

    event = bot.create_message("D1", "U1")

    assert fox.last_call.get("D1") is None

    await fox(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "D1"
    assert said.data["text"] == ("여우짤 서버의 상태가 좋지 않네요! 나중에 다시 시도해보세요!")
    assert not said.data["as_user"]
    assert said.data["username"] == "웹 브라우저의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/xFpyvpZ.png"

    assert fox.last_call.get("D1") is None

    await fox(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "D1"
    assert said.data["text"] == "http://fox.com/img1.png"
    assert not said.data["as_user"]
    assert said.data["username"] == "웹 브라우저의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/xFpyvpZ.png"

    assert fox.last_call["D1"]

    await fox(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "D1"
    assert fox_cooltime_re.match(said.data["text"])
    assert not said.data["as_user"]
    assert said.data["username"] == "웹 브라우저의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/xFpyvpZ.png"
