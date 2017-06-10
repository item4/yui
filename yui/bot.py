import asyncio
import json

import aiohttp

from .api import SlackAPI


class Bot:
    """Yui."""

    def __init__(self, token: str, debug: bool=False):
        """Initialize"""

        self.token = token
        self.debug = debug
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
            if message.get('type') == 'message':
                if message['text'].startswith('안녕 '):
                    user = await self.api.users.info(message.get('user'))
                    await self.say(
                        'test',
                        '안녕하세요! {}'.format(user['user']['name'])
                    )

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
