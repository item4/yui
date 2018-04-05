import asyncio
import re

import aiohttp

import pytest

import ujson

from yui.event import create_event
from yui.handlers.animal import cat, dog, get_cat_image_url, get_dog_image_url

from ..util import FakeBot

cat_cooltime_re = re.compile('아직 쿨타임이다냥! \d+시 \d+분 이후로 다시 시도해보라냥!')
dog_cooltime_re = re.compile('아직 쿨타임이다멍! \d+시 \d+분 이후로 다시 시도해보라멍!')


@pytest.mark.asyncio
async def test_get_cat_image_url(response_mock):
    response_mock.get(
        'http://thecatapi.com/api/images/get?format=xml&type=jpg,png',
        body=(
            '<?xml version="1.0"?>'
            '<response><data><images><image>'
            '<url>http://cat.com/404.jpg</url>'
            '<id>cdu</id>'
            '<source_url>http://thecatapi.com/?id=cdu</source_url>'
            '</image></images></data></response>'
        ),
        headers={'Content-Type': 'text/xml'},
    )
    response_mock.get(
        'http://thecatapi.com/api/images/get?format=xml&type=jpg,png',
        body=(
            '<?xml version="1.0"?>'
            '<response><data><images><image>'
            '<url>http://cannotresolve.com/200.jpg</url>'
            '<id>cdu</id>'
            '<source_url>http://thecatapi.com/?id=cdu</source_url>'
            '</image></images></data></response>'
        ),
        headers={'Content-Type': 'text/xml'},
    )
    response_mock.get(
        'http://thecatapi.com/api/images/get?format=xml&type=jpg,png',
        body=(
            '<?xml version="1.0"?>'
            '<response><data><images><image>'
            '<url>http://timeout.com/200.jpg</url>'
            '<id>cdu</id>'
            '<source_url>http://thecatapi.com/?id=cdu</source_url>'
            '</image></images></data></response>'
        ),
        headers={'Content-Type': 'text/xml'},
    )
    response_mock.get(
        'http://thecatapi.com/api/images/get?format=xml&type=jpg,png',
        body=(
            '<?xml version="1.0"?>'
            '<response><data><images><image>'
            '<url>http://cat.com/200.jpg</url>'
            '<id>cdu</id>'
            '<source_url>http://thecatapi.com/?id=cdu</source_url>'
            '</image></images></data></response>'
        ),
        headers={'Content-Type': 'text/xml'},
    )
    response_mock.get(
        'http://cannotresolve.com/200.jpg',
        exception=aiohttp.ClientConnectorError(None, OSError()),
    )
    response_mock.get(
        'http://timeout.com/200.jpg',
        exception=asyncio.TimeoutError(),
    )
    response_mock.get('http://cat.com/404.jpg', status=404)
    response_mock.get('http://cat.com/200.jpg', status=200)

    url = await get_cat_image_url(0.001)
    assert url == 'http://cat.com/200.jpg'


@pytest.mark.asyncio
async def test_get_dog_image_url(response_mock):
    response_mock.get(
        'https://dog.ceo/api/breeds/image/random',
        body=ujson.dumps({
            'status': 'success',
            'message': 'http://dog.com/404.jpg',
        }),
        headers={'Content-Type': 'application/json'},
    )
    response_mock.get(
        'https://dog.ceo/api/breeds/image/random',
        body=ujson.dumps({
            'status': 'success',
            'message': 'http://cannotresolve.com/200.jpg',
        }),
        headers={'Content-Type': 'application/json'},
    )
    response_mock.get(
        'https://dog.ceo/api/breeds/image/random',
        body=ujson.dumps({
            'status': 'success',
            'message': 'http://timeout.com/200.jpg',
        }),
        headers={'Content-Type': 'application/json'},
    )
    response_mock.get(
        'https://dog.ceo/api/breeds/image/random',
        body=ujson.dumps({
            'status': 'success',
            'message': 'http://dog.com/200.jpg',
        }),
        headers={'Content-Type': 'application/json'},
    )
    response_mock.get(
        'http://cannotresolve.com/200.jpg',
        exception=aiohttp.ClientConnectorError(None, OSError()),
    )
    response_mock.get(
        'http://timeout.com/200.jpg',
        exception=asyncio.TimeoutError(),
    )
    response_mock.get('http://dog.com/404.jpg', status=404)
    response_mock.get('http://dog.com/200.jpg', status=200)

    url = await get_dog_image_url(0.001)
    assert url == 'http://dog.com/200.jpg'


@pytest.mark.asyncio
async def test_cat_command(response_mock):
    response_mock.get(
        'http://thecatapi.com/api/images/get?format=xml&type=jpg,png',
        body=(
            '<?xml version="1.0"?>'
            '<response><data><images><image>'
            '<url>http://cat.com/200.jpg</url>'
            '<id>cdu</id>'
            '<source_url>http://thecatapi.com/?id=cdu</source_url>'
            '</image></images></data></response>'
        ),
        headers={'Content-Type': 'text/xml'},
    )
    response_mock.get(
        'http://thecatapi.com/api/images/get?format=xml&type=jpg,png',
        body=(
            '<?xml version="1.0"?>'
            '<response><data><images><image>'
            '<url>http://cat.com/200.jpg</url>'
            '<id>cdu</id>'
            '<source_url>http://thecatapi.com/?id=cdu</source_url>'
            '</image></images></data></response>'
        ),
        headers={'Content-Type': 'text/xml'},
    )
    response_mock.get('http://cat.com/200.jpg', status=200)
    response_mock.get('http://cat.com/200.jpg', status=200)

    bot = FakeBot()
    bot.add_channel('C1', 'general')
    user = bot.add_user('U1', 'kirito')
    bot.add_dm('D1', user)

    event = create_event({
        'type': 'message',
        'channel': 'C1',
    })

    assert cat.last_call.get('C1') is None

    await cat(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == 'http://cat.com/200.jpg'
    assert said.data['as_user'] == '0'
    assert said.data['username'] == '냥짤의 요정'
    assert said.data['icon_url'] == 'https://i.imgur.com/hIBJUMI.jpg'

    assert cat.last_call['C1']

    await cat(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'].startswith('아직 쿨타임이다냥! ')
    assert said.data['text'].endswith(' 이후로 다시 시도해보라냥!')
    assert said.data['as_user'] == '0'
    assert said.data['username'] == '냥짤의 요정'
    assert said.data['icon_url'] == 'https://i.imgur.com/hIBJUMI.jpg'

    event = create_event({
        'type': 'message',
        'channel': 'D1',
    })

    assert cat.last_call.get('D1') is None

    await cat(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'D1'
    assert said.data['text'] == 'http://cat.com/200.jpg'
    assert said.data['as_user'] == '0'
    assert said.data['username'] == '냥짤의 요정'
    assert said.data['icon_url'] == 'https://i.imgur.com/hIBJUMI.jpg'

    assert cat.last_call['D1']

    await cat(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'D1'
    assert cat_cooltime_re.match(said.data['text'])
    assert said.data['as_user'] == '0'
    assert said.data['username'] == '냥짤의 요정'
    assert said.data['icon_url'] == 'https://i.imgur.com/hIBJUMI.jpg'


@pytest.mark.asyncio
async def test_dog_command(response_mock):
    response_mock.get(
        'https://dog.ceo/api/breeds/image/random',
        body=ujson.dumps({
            'status': 'success',
            'message': 'http://dog.com/200.jpg',
        }),
        headers={'Content-Type': 'application/json'},
    )
    response_mock.get(
        'https://dog.ceo/api/breeds/image/random',
        body=ujson.dumps({
            'status': 'success',
            'message': 'http://dog.com/200.jpg',
        }),
        headers={'Content-Type': 'application/json'},
    )
    response_mock.get('http://dog.com/200.jpg', status=200)
    response_mock.get('http://dog.com/200.jpg', status=200)

    bot = FakeBot()
    bot.add_channel('C1', 'general')
    user = bot.add_user('U1', 'kirito')
    bot.add_dm('D1', user)

    event = create_event({
        'type': 'message',
        'channel': 'C1',
    })

    assert dog.last_call.get('C1') is None

    await dog(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == 'http://dog.com/200.jpg'
    assert said.data['as_user'] == '0'
    assert said.data['username'] == '멍짤의 요정'
    assert said.data['icon_url'] == 'https://i.imgur.com/Q9FKplO.png'

    assert dog.last_call['C1']

    await dog(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'].startswith('아직 쿨타임이다멍! ')
    assert said.data['text'].endswith(' 이후로 다시 시도해보라멍!')
    assert said.data['as_user'] == '0'
    assert said.data['username'] == '멍짤의 요정'
    assert said.data['icon_url'] == 'https://i.imgur.com/Q9FKplO.png'

    event = create_event({
        'type': 'message',
        'channel': 'D1',
    })

    assert dog.last_call.get('D1') is None

    await dog(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'D1'
    assert said.data['text'] == 'http://dog.com/200.jpg'
    assert said.data['as_user'] == '0'
    assert said.data['username'] == '멍짤의 요정'
    assert said.data['icon_url'] == 'https://i.imgur.com/Q9FKplO.png'

    assert dog.last_call['D1']

    await dog(bot, event, 0.001)

    said = bot.call_queue.pop()
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'D1'
    assert dog_cooltime_re.match(said.data['text'])
    assert said.data['as_user'] == '0'
    assert said.data['username'] == '멍짤의 요정'
    assert said.data['icon_url'] == 'https://i.imgur.com/Q9FKplO.png'
