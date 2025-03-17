import re

import pytest
from aiohttp.client_exceptions import ClientConnectionError

from yui.apps.animal import APIServerError
from yui.apps.animal import CAT_API_URL
from yui.apps.animal import DOG_API_URL
from yui.apps.animal import FOX_GALLERY_URL
from yui.apps.animal import cat
from yui.apps.animal import dog
from yui.apps.animal import fox
from yui.apps.animal import get_cat_image_url
from yui.apps.animal import get_dog_image_url
from yui.apps.animal import get_fox_image_url

CAT_REJECTED_PATTERN = re.compile(
    r"아직 쿨타임이다냥! \d+시 \d+분 이후로 다시 시도해보라냥!",
)
DOG_REJECTED_PATTERN = re.compile(
    r"아직 쿨타임이다멍! \d+시 \d+분 이후로 다시 시도해보라멍!",
)
FOX_REJECTED_PATTERN = re.compile(
    r"아직 쿨타임이에요! \d+시 \d+분 이후로 다시 시도해보세요!",
)


@pytest.fixture(name="bot")
async def bot_with_cache(bot, cache):
    async with bot.use_cache(cache):
        yield bot


@pytest.mark.anyio
async def test_get_cat_image_url_server_error(response_mock):
    response_mock.get(
        CAT_API_URL,
        status=500,
    )
    with pytest.raises(APIServerError):
        await get_cat_image_url(1.0)


@pytest.mark.anyio
async def test_get_cat_image_url_timeout(response_mock):
    URL_TIMEOUT = "http://cat.com/timeout.jpg"
    response_mock.get(
        CAT_API_URL,
        exception=ClientConnectionError(),
    )
    response_mock.get(
        CAT_API_URL,
        body=(
            '<?xml version="1.0"?>'
            "<response><data><images><image>"
            f"<url>{URL_TIMEOUT}</url>"
            "<id>cdu</id>"
            "<source_url>http://thecatapi.com/?id=cdu</source_url>"
            "</image></images></data></response>"
        ),
        headers={"Content-Type": "text/xml"},
    )
    response_mock.get(
        URL_TIMEOUT,
        exception=TimeoutError(),
    )
    with pytest.raises(TimeoutError):
        await get_cat_image_url(10.0)


@pytest.mark.anyio
async def test_get_cat_image_url_no_url(response_mock):
    response_mock.get(
        CAT_API_URL,
        exception=ClientConnectionError(),
    )
    response_mock.get(
        CAT_API_URL,
        body=(
            '<?xml version="1.0"?>'
            "<response><data><images><image>"
            "<id>cdu</id>"
            "<source_url>http://thecatapi.com/?id=cdu</source_url>"
            "</image></images></data></response>"
        ),
        headers={"Content-Type": "text/xml"},
    )

    with pytest.raises(APIServerError):
        await get_cat_image_url(0.001)


@pytest.mark.anyio
async def test_get_cat_image_url_empty_url(response_mock):
    response_mock.get(
        CAT_API_URL,
        exception=ClientConnectionError(),
    )
    response_mock.get(
        CAT_API_URL,
        body=(
            '<?xml version="1.0"?>'
            "<response><data><images><image>"
            "<url></url>"
            "<id>cdu</id>"
            "<source_url>http://thecatapi.com/?id=cdu</source_url>"
            "</image></images></data></response>"
        ),
        headers={"Content-Type": "text/xml"},
    )
    with pytest.raises(APIServerError):
        await get_cat_image_url(0.001)


@pytest.mark.anyio
async def test_get_cat_image_url(response_mock):
    URL_200 = "http://cat.com/200.jpg"
    URL_404 = "http://cat.com/404.jpg"
    URL_CLIENT_ERROR = "http://cat.com/err.jpg"
    response_mock.get(
        CAT_API_URL,
        exception=ClientConnectionError(),
    )
    response_mock.get(
        CAT_API_URL,
        body=(
            '<?xml version="1.0"?>'
            "<response><data><images><image>"
            f"<url>{URL_404}</url>"
            "<id>cdu</id>"
            "<source_url>http://thecatapi.com/?id=cdu</source_url>"
            "</image></images></data></response>"
        ),
        headers={"Content-Type": "text/xml"},
    )
    response_mock.get(URL_404, status=404)
    response_mock.get(
        CAT_API_URL,
        body=(
            '<?xml version="1.0"?>'
            "<response><data><images><image>"
            f"<url>{URL_CLIENT_ERROR}</url>"
            "<id>cdu</id>"
            "<source_url>http://thecatapi.com/?id=cdu</source_url>"
            "</image></images></data></response>"
        ),
        headers={"Content-Type": "text/xml"},
    )
    response_mock.get(
        URL_CLIENT_ERROR,
        exception=ClientConnectionError(),
    )
    response_mock.get(
        CAT_API_URL,
        body=(
            '<?xml version="1.0"?>'
            "<response><data><images><image>"
            f"<url>{URL_200}</url>"
            "<id>cdu</id>"
            "<source_url>http://thecatapi.com/?id=cdu</source_url>"
            "</image></images></data></response>"
        ),
        headers={"Content-Type": "text/xml"},
    )
    response_mock.get(URL_200)

    url = await get_cat_image_url(0.001)
    assert url == URL_200


@pytest.mark.anyio
async def test_get_dog_image_url_server_error(response_mock):
    response_mock.get(
        DOG_API_URL,
        status=500,
    )
    with pytest.raises(APIServerError):
        await get_dog_image_url(1.0)


@pytest.mark.anyio
async def test_get_dog_image_url_timeout(response_mock):
    URL_TIMEOUT = "http://dog.com/timeout.jpg"
    response_mock.get(
        DOG_API_URL,
        payload={"status": "success", "message": URL_TIMEOUT},
    )
    response_mock.get(
        URL_TIMEOUT,
        exception=TimeoutError(),
    )
    with pytest.raises(TimeoutError):
        await get_dog_image_url(10.0)


@pytest.mark.anyio
async def test_get_dog_image_url_no_url(response_mock):
    response_mock.get(
        DOG_API_URL,
        payload={"status": "success"},
    )
    with pytest.raises(APIServerError):
        await get_dog_image_url(1.0)


@pytest.mark.anyio
async def test_get_dog_image_url_empty_url(response_mock):
    response_mock.get(
        DOG_API_URL,
        payload={"status": "success", "message": ""},
    )
    with pytest.raises(APIServerError):
        await get_dog_image_url(1.0)


@pytest.mark.anyio
async def test_get_dog_image_url(response_mock):
    URL_200 = "http://dog.com/200.jpg"
    URL_404 = "http://dog.com/404.jpg"
    URL_CLIENT_ERROR = "http://dog.com/err.jpg"
    response_mock.get(
        DOG_API_URL,
        exception=ClientConnectionError(),
    )
    response_mock.get(
        DOG_API_URL,
        payload={"status": "success", "message": URL_404},
    )
    response_mock.get(URL_404, status=404)
    response_mock.get(
        DOG_API_URL,
        payload={
            "status": "success",
            "message": URL_CLIENT_ERROR,
        },
    )
    response_mock.get(
        URL_CLIENT_ERROR,
        exception=ClientConnectionError(),
    )
    response_mock.get(
        DOG_API_URL,
        payload={"status": "success", "message": URL_200},
    )

    response_mock.get(URL_200)

    url = await get_dog_image_url(1.0)
    assert url == URL_200


@pytest.mark.anyio
async def test_get_fox_image_url_server_error(response_mock):
    response_mock.get(
        FOX_GALLERY_URL,
        status=500,
    )
    with pytest.raises(APIServerError):
        await get_fox_image_url(1.0)


@pytest.mark.anyio
async def test_get_fox_image_url_no_image(response_mock):
    response_mock.get(
        FOX_GALLERY_URL,
        body="<!doctype html><html></html>",
        headers={"Content-Type": "text/html"},
    )
    with pytest.raises(APIServerError):
        await get_fox_image_url(0.001)


@pytest.mark.anyio
async def test_get_fox_image_url(response_mock):
    IMAGE_URL = "http://fox.com/img1.png"
    response_mock.get(
        FOX_GALLERY_URL,
        body=(
            '<div id="gallery-0">'
            '<img src="http://fox.com/not-gallery-0.png" class="attachment-thumbnail">'
            "</div>"
            '<div id="gallery-1">'
            '<img src="http://fox.com/not-thumbnail.png">'
            f'<img src="{IMAGE_URL}" class="attachment-thumbnail">'
            '<img src="http://fox.com/img2.png" class="attachment-thumbnail">'
            '<img src="http://fox.com/img3.png" class="attachment-thumbnail">'
            "</div>"
        ),
        headers={"Content-Type": "text/html"},
    )
    url = await get_fox_image_url(0.001)
    assert url == IMAGE_URL


@pytest.mark.anyio
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

    last_call = await bot.cache.get(f"YUI_APPS_ANIMAL_CAT_{event.channel}")
    assert last_call is None

    await cat(bot, event)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert (
        said.data["text"]
        == "냥냥이 API 서버의 상태가 좋지 않다냥! 나중에 다시 시도해보라냥!"
    )
    assert said.data["username"] == "냥짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/hIBJUMI.jpg"

    last_call = await bot.cache.get(f"YUI_APPS_ANIMAL_CAT_{event.channel}")
    assert last_call is None

    await cat(bot, event)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == "http://cat.com/200.jpg"
    assert said.data["username"] == "냥짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/hIBJUMI.jpg"

    last_call = await bot.cache.get(f"YUI_APPS_ANIMAL_CAT_{event.channel}")
    assert isinstance(last_call, float)

    await cat(bot, event)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert CAT_REJECTED_PATTERN.match(said.data["text"])
    assert said.data["username"] == "냥짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/hIBJUMI.jpg"

    event = bot.create_message(channel_id="D1")

    last_call = await bot.cache.get(f"YUI_APPS_ANIMAL_CAT_{event.channel}")
    assert last_call is None

    await cat(bot, event)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert (
        said.data["text"]
        == "냥냥이 API 서버의 상태가 좋지 않다냥! 나중에 다시 시도해보라냥!"
    )
    assert said.data["username"] == "냥짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/hIBJUMI.jpg"

    last_call = await bot.cache.get(f"YUI_APPS_ANIMAL_CAT_{event.channel}")
    assert last_call is None

    await cat(bot, event)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == "http://cat.com/200.jpg"
    assert said.data["username"] == "냥짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/hIBJUMI.jpg"

    last_call = await bot.cache.get(f"YUI_APPS_ANIMAL_CAT_{event.channel}")
    assert isinstance(last_call, float)

    await cat(bot, event)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert CAT_REJECTED_PATTERN.match(said.data["text"])
    assert said.data["username"] == "냥짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/hIBJUMI.jpg"


@pytest.mark.anyio
async def test_dog_command(bot, response_mock):
    response_mock.get(
        DOG_API_URL,
        status=500,
    )
    response_mock.get(
        DOG_API_URL,
        payload={"status": "success", "message": "http://dog.com/200.jpg"},
    )
    response_mock.get(
        DOG_API_URL,
        status=500,
    )
    response_mock.get(
        DOG_API_URL,
        payload={"status": "success", "message": "http://dog.com/200.jpg"},
    )
    response_mock.get("http://dog.com/200.jpg")
    response_mock.get("http://dog.com/200.jpg")

    event = bot.create_message()

    last_call = await bot.cache.get(f"YUI_APPS_ANIMAL_DOG_{event.channel}")
    assert last_call is None

    await dog(bot, event)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert (
        said.data["text"]
        == "멍멍이 API 서버의 상태가 좋지 않다멍! 나중에 다시 시도해보라멍!"
    )
    assert said.data["username"] == "멍짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/Q9FKplO.png"

    last_call = await bot.cache.get(f"YUI_APPS_ANIMAL_DOG_{event.channel}")
    assert last_call is None

    await dog(bot, event)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == "http://dog.com/200.jpg"
    assert said.data["username"] == "멍짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/Q9FKplO.png"

    last_call = await bot.cache.get(f"YUI_APPS_ANIMAL_DOG_{event.channel}")
    assert isinstance(last_call, float)

    await dog(bot, event)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert DOG_REJECTED_PATTERN.match(said.data["text"])
    assert said.data["username"] == "멍짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/Q9FKplO.png"

    event = bot.create_message(channel_id="D1")

    last_call = await bot.cache.get(f"YUI_APPS_ANIMAL_DOG_{event.channel}")
    assert last_call is None

    await dog(bot, event)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert (
        said.data["text"]
        == "멍멍이 API 서버의 상태가 좋지 않다멍! 나중에 다시 시도해보라멍!"
    )
    assert said.data["username"] == "멍짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/Q9FKplO.png"

    last_call = await bot.cache.get(f"YUI_APPS_ANIMAL_DOG_{event.channel}")
    assert last_call is None

    await dog(bot, event)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == "http://dog.com/200.jpg"
    assert said.data["username"] == "멍짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/Q9FKplO.png"

    last_call = await bot.cache.get(f"YUI_APPS_ANIMAL_DOG_{event.channel}")
    assert isinstance(last_call, float)

    await dog(bot, event)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert DOG_REJECTED_PATTERN.match(said.data["text"])
    assert said.data["username"] == "멍짤의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/Q9FKplO.png"


@pytest.mark.anyio
async def test_fox_command(bot, response_mock):
    response_mock.get(
        FOX_GALLERY_URL,
        body="<!doctype html><html></html>",
        headers={"Content-Type": "text/html"},
    )
    response_mock.get(
        FOX_GALLERY_URL,
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
        FOX_GALLERY_URL,
        body="<!doctype html><html></html>",
        headers={"Content-Type": "text/html"},
    )
    response_mock.get(
        FOX_GALLERY_URL,
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

    last_call = await bot.cache.get(f"YUI_APPS_ANIMAL_FOX_{event.channel}")
    assert last_call is None

    await fox(bot, event)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert (
        said.data["text"]
        == "여우짤 서버의 상태가 좋지 않네요! 나중에 다시 시도해보세요!"
    )
    assert said.data["username"] == "웹 브라우저의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/xFpyvpZ.png"

    last_call = await bot.cache.get(f"YUI_APPS_ANIMAL_FOX_{event.channel}")
    assert last_call is None

    await fox(bot, event)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == "http://fox.com/img1.png"
    assert said.data["username"] == "웹 브라우저의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/xFpyvpZ.png"

    last_call = await bot.cache.get(f"YUI_APPS_ANIMAL_FOX_{event.channel}")
    assert isinstance(last_call, float)

    await fox(bot, event)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert FOX_REJECTED_PATTERN.match(said.data["text"])
    assert said.data["username"] == "웹 브라우저의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/xFpyvpZ.png"

    event = bot.create_message(channel_id="D1")

    last_call = await bot.cache.get(f"YUI_APPS_ANIMAL_FOX_{event.channel}")
    assert last_call is None

    await fox(bot, event)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert (
        said.data["text"]
        == "여우짤 서버의 상태가 좋지 않네요! 나중에 다시 시도해보세요!"
    )
    assert said.data["username"] == "웹 브라우저의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/xFpyvpZ.png"

    last_call = await bot.cache.get(f"YUI_APPS_ANIMAL_FOX_{event.channel}")
    assert last_call is None

    await fox(bot, event)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert said.data["text"] == "http://fox.com/img1.png"
    assert said.data["username"] == "웹 브라우저의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/xFpyvpZ.png"

    last_call = await bot.cache.get(f"YUI_APPS_ANIMAL_FOX_{event.channel}")
    assert isinstance(last_call, float)

    await fox(bot, event)

    said = bot.call_queue.pop()
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == event.channel
    assert FOX_REJECTED_PATTERN.match(said.data["text"])
    assert said.data["username"] == "웹 브라우저의 요정"
    assert said.data["icon_url"] == "https://i.imgur.com/xFpyvpZ.png"
