import asyncio
import html
import importlib
import inspect
import logging
import logging.config
import re
import shlex
import traceback
from typing import Any, Dict

import aiocron

import aiohttp

from attrdict import AttrDict

from sqlalchemy.orm import sessionmaker

import ujson

from .api import SlackAPI
from .box import Box, Crontab, Handler, box
from .event import Event, Message, create_event
from .orm import Base, get_database_engine


__all__ = 'APICallError', 'Bot', 'BotReconnect', 'Session'

Session = sessionmaker(autocommit=True)

SPACE_RE = re.compile('\s+')


class BotReconnect(Exception):
    """Exception for reconnect bot"""


class APICallError(Exception):
    """Fail to call API"""


class Bot:
    """Yui."""

    def __init__(
        self,
        config: AttrDict,
        *,
        orm_base=None,
        using_box: Box=None
    ) -> None:
        """Initialize"""

        logging.config.dictConfig(config['LOGGING'])

        logger = logging.getLogger(f'{__name__}.Bot.__init__')

        logger.info('start')

        self.loop = None

        logger.info('connect to DB')
        config.DATABASE_ENGINE = get_database_engine(config)

        logger.info('import handlers')
        for module_name in config.HANDLERS:
            logger.debug('import handlers: %s', module_name)
            importlib.import_module(module_name)

        logger.info('import models')
        for module_name in config.MODELS:
            logger.debug('import models: %s', module_name)
            importlib.import_module(module_name)

        self.config = config

        self.orm_base = orm_base or Base
        self.box = using_box or box
        self.queue: asyncio.Queue = asyncio.Queue()
        self.api = SlackAPI(self)
        self.channels: Dict[str, Dict[str, Any]] = {}
        self.restart = False

        logger.info('register crontab')
        self.register_crontab()

    def register_crontab(self):
        """Register cronjob to bot from box."""

        logger = logging.getLogger(
            f'{__name__}.Bot.register_crontab'
        )

        def register(c: Crontab):
            func_params = inspect.signature(c.func).parameters
            kw = {}
            if 'bot' in func_params:
                kw['bot'] = self

            @aiocron.crontab(c.spec, *c.args, **c.kwargs)
            async def task():
                sess = Session(bind=self.config.DATABASE_ENGINE)
                if 'sess' in func_params:
                    kw['sess'] = sess
                try:
                    await c.func(**kw)
                except:  # noqa: E722
                    logger.error(f'Error: {traceback.format_exc()}')
                    await self.say(
                        self.config.OWNER,
                        '*Traceback*\n```\n{}\n```\n'.format(
                            traceback.format_exc(),
                        )
                    )
                finally:
                    sess.close()

            c.start = task.start
            c.stop = task.stop

        for c in self.box.crontabs:
            register(c)

    def run(self):
        """Run"""

        loop = asyncio.get_event_loop()
        loop.set_debug(self.config.DEBUG)
        self.loop = loop

        loop.run_until_complete(
            asyncio.wait(
                (
                    self.receive(),
                    self.process(),
                )
            )
        )
        loop.close()

    async def call(self, method: str, data: Dict[str, str]=None):
        """Call API methods."""

        with aiohttp.ClientSession() as session:

            form = aiohttp.FormData(data or {})
            form.add_field('token', self.config.TOKEN)
            async with session.post(
                'https://slack.com/api/{}'.format(method),
                data=form
            ) as response:
                if response.status == 200:
                    return await response.json(loads=ujson.loads)
                else:
                    raise APICallError('fail to call {} with {}'.format(
                        method, data
                    ))

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

        logger = logging.getLogger(f'{__name__}.Bot.process')

        while True:
            event = await self.queue.get()

            logger.info(event)

            type = event.type
            subtype = event.subtype

            handlers = self.box.handlers.get(type)
            if handlers:
                for name, handler in handlers[subtype].items():
                    if type == 'message':
                        try:
                            res = await self.process_message_handler(
                                name,
                                handler,
                                event
                            )
                            if not res:
                                break
                        except SystemExit as e:
                            logger.info('SystemExit')
                            raise e
                        except BotReconnect:
                            self.restart = True
                        except:  # noqa: E722
                            logger.error(
                                f'Event: {event} / '
                                f'Traceback: {traceback.format_exc()}'
                            )
                            await self.say(
                                self.config.OWNER,
                                ('*Event*\n```\n{}\n```\n'
                                 '*Traceback*\n```\n{}\n```\n').format(
                                    event,
                                    traceback.format_exc(),
                                )
                            )
                    else:
                        try:
                            res = await self.process_handler(
                                name,
                                handler,
                                event
                            )
                            if not res:
                                break
                        except SystemExit as e:
                            logger.info('SystemExit')
                            raise e
                        except BotReconnect:
                            self.restart = True
                        except:  # noqa: E722
                            logger.error(
                                f'Event: {event} / '
                                f'Traceback: {traceback.format_exc()}'
                            )
                            await self.say(
                                self.config.OWNER,
                                ('*Event*\n```\n{}\n```\n'
                                 '*Traceback*\n```\n{}\n```\n').format(
                                    event,
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
                                event
                            )
                            if not res:
                                break
                        except SystemExit as e:
                            logger.info('SystemExit')
                            raise e
                        except BotReconnect:
                            self.restart = True
                        except:  # noqa: E722
                            logger.error(
                                f'Event: {event} / '
                                f'Traceback: {traceback.format_exc()}'
                            )
                            await self.say(
                                self.config.OWNER,
                                ('*Event*\n```\n{}\n```\n'
                                 '*Traceback*\n```\n{}\n```\n').format(
                                    event,
                                    traceback.format_exc(),
                                )
                            )

    async def process_handler(
        self,
        name: str,
        handler: Handler,
        event: Event
    ):
        func_params = handler.signature.parameters
        kwargs = {}

        sess = Session(bind=self.config.DATABASE_ENGINE)

        if 'bot' in func_params:
            kwargs['bot'] = self
        if 'loop' in func_params:
            kwargs['loop'] = self.loop
        if 'event' in func_params:
            kwargs['event'] = event
        if 'sess' in func_params:
            kwargs['sess'] = sess
        if 'user' in func_params:
            kwargs['user'] = await self.api.users.info(event.user)

        validation = True
        if handler.channel_validator:
            validation = await handler.channel_validator(self, event)

        if validation:
            try:
                res = await handler.callback(**kwargs)
            finally:
                sess.close()
        else:
            sess.close()
            return True

        if not res:
            return False

        return True

    async def process_message_handler(
        self,
        name: str,
        handler: Handler,
        event: Message
    ):

        call = ''
        args = ''
        if hasattr(event, 'text'):
            try:
                call, args = SPACE_RE.split(event.text, 1)
            except ValueError:
                call = event.text
        elif hasattr(event, 'message') and 'text' in event.message:
            try:
                call, args = SPACE_RE.split(event.message.text, 1)
            except ValueError:
                call = event.message.text

        match = True
        if handler.is_command:
            match = call == self.config.PREFIX + name

        if match:
            func_params = handler.signature.parameters
            kwargs = {}
            options: Dict[str, Any] = {}
            arguments: Dict[str, Any] = {}
            raw = html.unescape(args)
            if handler.use_shlex:
                try:
                    option_chunks = shlex.split(raw)
                except ValueError:
                    await self.say(
                        event.channel,
                        '*Error*: Can not parse this command'
                    )
                    return False
            else:
                option_chunks = raw.split(' ')

            try:
                options, argument_chunks = handler.parse_options(option_chunks)
            except SyntaxError as e:
                await self.say(event.channel, '*Error*\n{}'.format(e))
                return False

            try:
                arguments, remain_chunks = handler.parse_arguments(
                    argument_chunks
                )
            except SyntaxError as e:
                await self.say(event.channel, '*Error*\n{}'.format(e))
                return False
            else:
                kwargs.update(options)
                kwargs.update(arguments)

                sess = Session(bind=self.config.DATABASE_ENGINE)

                if 'bot' in func_params:
                    kwargs['bot'] = self
                if 'loop' in func_params:
                    kwargs['loop'] = self.loop
                if 'event' in func_params:
                    kwargs['event'] = event
                if 'sess' in func_params:
                    kwargs['sess'] = sess
                if 'raw' in func_params:
                    kwargs['raw'] = raw
                if 'remain_chunks' in func_params:
                    kwargs['remain_chunks'] = remain_chunks
                if 'user' in func_params:
                    kwargs['user'] = await self.api.users.info(event.user)

                validation = True
                if handler.channel_validator:
                    validation = await handler.channel_validator(self, event)

                if validation:
                    try:
                        res = await handler.callback(**kwargs)
                    finally:
                        sess.close()
                else:
                    sess.close()
                    return True

                if not res:
                    return False
        return True

    async def receive(self):
        """Receive stream from slack."""

        logger = logging.getLogger(f'{__name__}.Bot.receive')

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

                self.channels = {c['id']: c for c in rtm['channels']}

                with aiohttp.ClientSession() as session:
                    async with session.ws_connect(rtm['url']) as ws:
                        async for msg in ws:
                            if self.restart:
                                self.restart = False
                                raise BotReconnect()

                            if msg.tp == aiohttp.WSMsgType.TEXT:
                                event = create_event(ujson.loads(msg.data))
                                await self.queue.put(event)
                            elif msg.tp in (aiohttp.WSMsgType.ERROR,
                                            aiohttp.WSMsgType.CLOSED):
                                logger.error(
                                    f'Error: {traceback.format_exc()}'
                                )
                                raise BotReconnect()
                            else:
                                logger.error('Type: %s / MSG: %s', msg.tp, msg)
            except BotReconnect:
                continue
