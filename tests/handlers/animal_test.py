from mocket.mocket import Mocketizer
from mocket.mockhttp import Entry, Response

import pytest

import ujson

from yui.handlers.animal import get_cat_image_url, get_dog_image_url


@pytest.mark.asyncio
async def test_get_cat_image_url():
    with Mocketizer(None):
        Entry.register(
            Entry.GET,
            'http://thecatapi.com/api/images/get',
            Response(
                '<response><data><images><image>'
                '<url>http://cat.com/404.jpg</url>'
                '<id>cdu</id>'
                '<source_url>http://thecatapi.com/?id=cdu</source_url>'
                '</image></images></data></response>',
                headers={'Content-Type': 'text/xml'},
            ),
            Response(
                '<response><data><images><image>'
                '<url>http://cannotresolve.com/200.jpg</url>'
                '<id>cdu</id>'
                '<source_url>http://thecatapi.com/?id=cdu</source_url>'
                '</image></images></data></response>',
                headers={'Content-Type': 'text/xml'},
            ),
            Response(
                '<response><data><images><image>'
                '<url>http://cat.com/200.jpg</url>'
                '<id>cdu</id>'
                '<source_url>http://thecatapi.com/?id=cdu</source_url>'
                '</image></images></data></response>',
                headers={'Content-Type': 'text/xml'},
            ),
            match_querystring=False,
        )
        Entry.single_register(
            Entry.GET,
            'http://cat.com/404.jpg',
            status=404,
        )
        Entry.single_register(
            Entry.GET,
            'http://cat.com/200.jpg',
        )

        url = await get_cat_image_url()
        assert url == 'http://cat.com/200.jpg'


@pytest.mark.asyncio
async def test_get_dog_image_url():
    with Mocketizer(None):
        Entry.register(
            Entry.GET,
            'https://dog.ceo/api/breeds/image/random',
            Response(
                ujson.dumps({
                    'status': 'success',
                    'message': 'http://dog.com/404.jpg',
                }),
                headers={'Content-Type': 'application/json'},
            ),
            Response(
                ujson.dumps({
                    'status': 'success',
                    'message': 'http://cannotresolve.com/200.jpg',
                }),
                headers={'Content-Type': 'application/json'},
            ),
            Response(
                ujson.dumps({
                    'status': 'success',
                    'message': 'http://dog.com/200.jpg',
                }),
                headers={'Content-Type': 'application/json'},
            ),
        )
        Entry.single_register(
            Entry.GET,
            'http://dog.com/404.jpg',
            status=404,
        )
        Entry.single_register(
            Entry.GET,
            'http://dog.com/200.jpg',
        )

        url = await get_dog_image_url()
        assert url == 'http://dog.com/200.jpg'
