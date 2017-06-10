import asyncio
import json

import aiohttp

from .api import SlackAPI
from .box import Box, box


__all__ = 'Bot',


class Bot:
    """Yui."""

    def __init__(self, token: str, debug: bool=False, using_box: Box=None):
        """Initialize"""

        self.token = token
        self.debug = debug
        self.box = using_box or box
        self.queue = asyncio.Queue()
        self.api = SlackAPI(self)

    def run(self):
        """Run"""

        loop = asyncio.get_event_loop()
        loop.set_debug(self.debug)

        loop.run_until_complete(
            asyncio.wait(
                (
                    self.receive(self.queue.put),
                    self.process(self.queue.get),
                )
            )
        )
        loop.close()

    async def call(self, method: str, data: dict=None):
        """Call API methods."""

        with aiohttp.ClientSession() as session:

            form = aiohttp.FormData(data or {})
            form.add_field('token', self.token)
            async with session.post(
                'https://slack.com/api/{}'.format(method),
                data=form
            ) as response:
                assert 200 == response.status, ('{0} with {1} failed.'
                                                .format(method, data))
                return await response.json()

    async def say(self, channel: str, text: str) -> dict:
        """Shortcut for bot saying."""

        return await self.api.chat.postMessage(channel, text, as_user=True)

    async def process(self, get):
        """Process messages."""

        while True:
            message = await get()

            print(message)
            type = message.get('type')

            handlers = self.box.handlers.get(type)
            if handlers:
                for name, func in handlers.items():
                    if type == 'message':
                        eq = message['text'] == name
                        startswith = message['text'].startswith(name + ' ')

                        if eq or startswith:
                            res = await func(self, message)
                            if not res:
                                break

    async def receive(self, put):
        """Receive stream from slack."""

        rtm = await self.call('rtm.start')
        assert rtm['ok'], "Error connecting to RTM."
        with aiohttp.ClientSession() as session:
            async with session.ws_connect(rtm['url']) as ws:
                async for msg in ws:
                    assert msg.tp == aiohttp.WSMsgType.text
                    message = json.loads(msg.data)
                    await put(message)
