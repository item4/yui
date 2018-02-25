import asyncio

import aiohttp

import pytest

import ujson

from yui.handlers.animal import get_cat_image_url, get_dog_image_url


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
