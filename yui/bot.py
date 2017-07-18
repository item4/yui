import asyncio
import html
import importlib
import json
import re
import shlex
import sys
import traceback

import aiohttp

from attrdict import AttrDict

from .api import SlackAPI
from .box import Box, box


__all__ = 'Bot', 'BotReconnect'

SPACE_RE = re.compile('\s+')


class BotReconnect(Exception):
    """Exception for reconnect bot"""


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
                    self.receive(),
                    self.process(),
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

    async def process(self):
        """Process messages."""

        while True:
            message = await self.queue.get()

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
                        except SystemExit as e:
                            raise e
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
                        except SystemExit as e:
                            raise e
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
        call = ''
        args = ''
        if 'text' in message:
            try:
                call, args = SPACE_RE.split(message['text'], 1)
            except ValueError:
                call = message['text']
        elif 'message' in message and 'text' in message['message']:
            try:
                call, args = SPACE_RE.split(message['message']['text'], 1)
            except ValueError:
                call = message['message']['text']

        match = True
        if handler.is_command:
            match = call == self.config.PREFIX + name

        if match:
            func_params = handler.signature.parameters
            kwargs = {}
            options = {}
            arguments = {}
            raw = html.unescape(args)
            try:
                option_chunks = shlex.split(raw)
            except ValueError:
                await self.say(
                    message['channel'],
                    '*Error*: Can not parse this command'
                )
                return False

            try:
                options, argument_chunks = handler.parse_options(option_chunks)
            except SyntaxError as e:
                await self.say(message['channel'], '*Error*\n{}'.format(e))
                return False

            try:
                arguments, remain_chunks = handler.parse_arguments(
                    argument_chunks
                )
            except SyntaxError as e:
                await self.say(message['channel'], '*Error*\n{}'.format(e))
                return False
            else:
                kwargs.update(options)
                kwargs.update(arguments)

                if 'bot' in func_params:
                    kwargs['bot'] = self
                if 'message' in func_params:
                    kwargs['message'] = message
                if 'raw' in func_params:
                    kwargs['raw'] = raw
                if 'remain_chunks' in func_params:
                    kwargs['remain_chunks'] = remain_chunks
                if 'user' in func_params:
                    kwargs['user'] = await self.api.users.info(
                        message.get('user'))

                res = await handler.callback(**kwargs)
                if not res:
                    return False
        return True

    async def receive(self):
        """Receive stream from slack."""

        sleep = 0
        while True:
            try:
                rtm = await self.call('rtm.start')

                if not rtm['ok']:
                    await asyncio.sleep((sleep+1)*10)
                    sleep += 1
                    raise BotReconnect()
                else:
                    sleep = 0

                with aiohttp.ClientSession() as session:
                    async with session.ws_connect(rtm['url']) as ws:
                        async for msg in ws:
                            if msg.tp == aiohttp.WSMsgType.TEXT:
                                message = json.loads(msg.data)
                                await self.queue.put(message)
                            elif msg.tp in (aiohttp.WSMsgType.ERROR,
                                            aiohttp.WSMsgType.CLOSED):
                                raise BotReconnect()
                            else:
                                print(msg.tp, msg, file=sys.stderr)
            except BotReconnect:
                continue
