import asyncio
import importlib
import json
import traceback

import aiohttp

from attrdict import AttrDict

from .api import SlackAPI
from .box import Box, box


__all__ = 'Bot',


class Bot:
    """Yui."""

    def __init__(self, config: AttrDict, using_box: Box=None):
        """Initialize"""

        for module_name in config.HANDLERS:
            importlib.import_module(module_name)

        self.config = config
        self.box = using_box or box
        self.queue = asyncio.Queue()
        self.api = SlackAPI(self)

    def run(self):
        """Run"""

        loop = asyncio.get_event_loop()
        loop.set_debug(self.config.DEBUG)

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
            form.add_field('token', self.config.TOKEN)
            async with session.post(
                'https://slack.com/api/{}'.format(method),
                data=form
            ) as response:
                assert 200 == response.status, ('{0} with {1} failed.'
                                                .format(method, data))
                return await response.json()

    async def say(self, channel: str, text: str, **kwargs) -> dict:
        """Shortcut for bot saying."""

        return await self.api.chat.postMessage(
            channel,
            text,
            as_user=True,
            link_names=True,
            **kwargs
        )

    async def process(self, get):
        """Process messages."""

        while True:
            message = await get()

            print(message)

            type = message.get('type')
            subtype = message.get('subtype')

            handlers = self.box.handlers.get(type)
            if handlers:
                for name, handler in handlers[subtype].items():
                    if type == 'message':
                        try:
                            res = await self.process_message_handler(
                                name,
                                handler,
                                message
                            )
                            if not res:
                                break
                        except:
                            await self.say(
                                self.config.OWNER,
                                ('*Message*\n```\n{}\n```\n'
                                 '*Traceback*\n```\n{}\n```\n').format(
                                    message,
                                    traceback.format_exc(),
                                )
                            )

            if type == 'message':
                for name, alias_to in self.box.aliases[subtype].items():
                    handler = self.box.handlers[type][subtype][alias_to]
                    if handler:
                        try:
                            res = await self.process_message_handler(
                                name,
                                handler,
                                message
                            )
                            if not res:
                                break
                        except:
                            await self.say(
                                self.config.OWNER,
                                ('*Message*\n```\n{}\n```\n'
                                 '*Traceback*\n```\n{}\n```\n').format(
                                    message,
                                    traceback.format_exc(),
                                )
                            )

    async def process_message_handler(self, name: str, handler, message: dict):
        chunks = []
        if 'text' in message:
            chunks = message['text'].split(' ')
        elif 'message' in message and 'text' in message['message']:
            chunks = message['message']['text'].split(' ')

        match = True
        if handler.need_prefix:
            match = chunks[0] == self.config.PREFIX + name

        if match:
            func_params = handler.signature.parameters
            kwargs = {}
            if 'bot' in func_params:
                kwargs['bot'] = self
            if 'message' in func_params:
                kwargs['message'] = message
            if 'chunks' in func_params:
                kwargs['chunks'] = chunks
            if 'user' in func_params:
                kwargs['user'] = await self.api.users.info(message.get('user'))

            res = await handler.callback(**kwargs)
            if not res:
                return False
        return True

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
