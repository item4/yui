import asyncio
import functools
import html
import importlib
import inspect
import logging
import logging.config
import re
import shlex
import traceback
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Any, Callable, Dict, List, TypeVar, Union

import aiocron

import aiohttp

import async_timeout

from sqlalchemy.orm import sessionmaker

import ujson

from .api import SlackAPI
from .box import Box, Crontab, Handler, box
from .config import Config
from .event import Event, Message, create_event
from .orm import Base, get_database_engine
from .session import client_session
from .type import (
    BotLinkedNamespace,
    Channel,
    ChannelID,
    DirectMessageChannel,
    PrivateChannel,
    PublicChannel,
    User,
    UserID,
)


__all__ = 'APICallError', 'Bot', 'BotReconnect', 'Session'

Session = sessionmaker(autocommit=True)

SPACE_RE = re.compile('\s+')

R = TypeVar('R')


class BotReconnect(Exception):
    """Exception for reconnect bot"""


class APICallError(Exception):
    """Fail to call API"""

    def __init__(
        self,
        message: str,
        *,
        status_code: int=None,
        result: Dict[str, Any]=None,
        headers: Any=None,
    ) -> None:
        super(APICallError, self).__init__(message)

        self.status_code = status_code
        self.result = result
        self.headers = headers


class Bot:
    """Yui."""

    def __init__(
        self,
        config: Config,
        *,
        orm_base=None,
        using_box: Box=None
    ) -> None:
        """Initialize"""

        logging.config.dictConfig(config['LOGGING'])

        logger = logging.getLogger(f'{__name__}.Bot.__init__')

        logger.info('start')

        BotLinkedNamespace._bot = self

        self.loop = None
        self.process_pool_executor = ProcessPoolExecutor()
        self.thread_pool_executor = ThreadPoolExecutor()

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
        self.channels: List[PublicChannel] = []
        self.ims: List[DirectMessageChannel] = []
        self.groups: List[PrivateChannel] = []
        self.users: Dict[UserID, User] = {}
        self.restart = False

        if self.config.get('REGISTER_CRONTAB', True):
            logger.info('register crontab')
            self.register_crontab()

    def register_crontab(self):
        """Register cronjob to bot from box."""

        logger = logging.getLogger(
            f'{__name__}.Bot.register_crontab'
        )

        def register(c: Crontab):
            logger.info(f'register {c}')
            func_params = inspect.signature(c.func).parameters
            kw = {}
            if 'bot' in func_params:
                kw['bot'] = self

            @aiocron.crontab(c.spec, *c.args, **c.kwargs)
            async def task():
                if 'loop' in func_params:
                    kw['loop'] = self.loop

                sess = Session(bind=self.config.DATABASE_ENGINE)
                if 'sess' in func_params:
                    kw['sess'] = sess

                logger.debug(f'hit and start to run {c}')
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
                logger.debug(f'end {c}')

            c.start = task.start
            c.stop = task.stop

        for c in self.box.crontabs:
            register(c)

    def run(self):
        """Run"""

        while True:
            loop = asyncio.get_event_loop()
            loop.set_debug(self.config.DEBUG)
            self.loop = loop
            loop.run_until_complete(
                asyncio.wait(
                    (
                        self.receive(),
                        self.process(),
                    ),
                    return_when=asyncio.FIRST_EXCEPTION,
                )
            )
            loop.close()

    async def run_in_other_process(
        self,
        f: Callable[..., R],
        *args,
        **kwargs,
    ) -> R:
        return await self.loop.run_in_executor(
            executor=self.process_pool_executor,
            func=functools.partial(f, *args, **kwargs),
        )

    async def run_in_other_thread(
        self,
        f: Callable[..., R],
        *args,
        **kwargs,
    ) -> R:
        return await self.loop.run_in_executor(
            executor=self.thread_pool_executor,
            func=functools.partial(f, *args, **kwargs),
        )

    async def call(
        self,
        method: str,
        data: Dict[str, str]=None,
        *,
        token: str=None,
    ) -> Dict[str, Any]:
        """Call API methods."""

        async with client_session() as session:
            form = aiohttp.FormData(data or {})
            form.add_field('token', token or self.config.TOKEN)
            try:
                async with session.post(
                    'https://slack.com/api/{}'.format(method),
                    data=form
                ) as response:
                    try:
                        result = await response.json(loads=ujson.loads)
                    except aiohttp.client_exceptions.ContentTypeError:
                        raise APICallError(
                            'fail to call {} with {}'.format(
                                method, data
                            ),
                            status_code=response.status,
                            result=await response.text(),
                            headers=response.headers,
                        )
                    if response.status == 200:
                        return result
                    else:
                        raise APICallError(
                            'fail to call {} with {}'.format(
                                method, data
                            ),
                            status_code=response.status,
                            result=result,
                            headers=response.headers,
                        )
            except aiohttp.client_exceptions.ClientConnectorError:
                raise APICallError('fail to call {} with {}'.format(
                    method, data
                ))

    async def say(
        self,
        channel: Union[Channel, ChannelID],
        text: str,
        **kwargs
    ) -> Dict[str, Any]:
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

        async def handle(func, args, event):
            try:
                return await func(
                    *args,
                    event=event,
                )
            except SystemExit:
                logger.info('SystemExit')
                raise
            except BotReconnect:
                logger.info('BotReconnect raised.')
                self.restart = True
                return False
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
                return False

        while True:
            event = await self.queue.get()

            logger.info(event)

            type = event.type
            subtype = event.subtype
            handlers = self.box.handlers[type]

            if type == 'message':
                running = True
                for name, handler in handlers[subtype].items():
                    result = await handle(
                        self.process_message_handler,
                        (name, handler),
                        event,
                    )
                    if not result:
                        running = False
                        break
                if running:
                    for name, alias_to in self.box.aliases[subtype].items():
                        handler = self.box.handlers[type][subtype][alias_to]
                        if handler:
                            result = await handle(
                                self.process_message_handler,
                                (name, handler),
                                event,
                            )
                            if not result:
                                break
            else:
                for name, handler in handlers[subtype].items():
                    result = await handle(
                        self.process_handler,
                        (handler,),
                        event,
                    )
                    if not result:
                        break

    async def process_handler(
        self,
        handler: Handler,
        event: Event
    ):
        func_params = handler.signature.parameters
        kwargs: Dict[str, Any] = {}

        sess = Session(bind=self.config.DATABASE_ENGINE)

        if 'bot' in func_params:
            kwargs['bot'] = self
        if 'loop' in func_params:
            kwargs['loop'] = self.loop
        if 'event' in func_params:
            kwargs['event'] = event
        if 'sess' in func_params:
            kwargs['sess'] = sess

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
        elif hasattr(event, 'message') and event.message and \
                hasattr(event.message, 'text'):
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
                    annotation = func_params['remain_chunks'].annotation
                    if annotation in [str, inspect._empty]:  # type: ignore
                        kwargs['remain_chunks'] = ' '.join(remain_chunks)
                    else:
                        kwargs['remain_chunks'] = remain_chunks

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
        timeout = self.config.RECEIVE_TIMEOUT

        sleep = 0
        while True:
            try:
                rtm = await self.call('rtm.start')
            except Exception as e:
                logger.exception(e)
                await asyncio.sleep((sleep + 1) * 10)
                sleep += 1
                continue

            if not rtm['ok']:
                await asyncio.sleep((sleep+1)*10)
                sleep += 1
                continue
            else:
                sleep = 0

            await self.queue.put(create_event({
                'type': 'chatterbox_system_start',
            }))
            try:
                async with client_session() as session:
                    async with session.ws_connect(rtm['url']) as ws:
                        while True:
                            if self.restart:
                                self.restart = False
                                await ws.close()
                                break

                            try:
                                async with async_timeout.timeout(timeout):
                                    msg: aiohttp.WSMessage = await ws.receive()
                            except asyncio.TimeoutError:
                                logger.error(f'receive timeout({timeout})')
                                await ws.close()
                                break

                            if msg == aiohttp.http.WS_CLOSED_MESSAGE:
                                break

                            if msg.type == aiohttp.WSMsgType.TEXT:
                                try:
                                    event = create_event(
                                        msg.json(loads=ujson.loads)
                                    )
                                except:  # noqa: F722
                                    logger.exception(msg.data)
                                else:
                                    await self.queue.put(event)
                            elif msg.type in (aiohttp.WSMsgType.CLOSE,
                                              aiohttp.WSMsgType.CLOSED,
                                              aiohttp.WSMsgType.CLOSING):
                                logger.info('websocket closed')
                                break
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                logger.error(msg.data)
                                break
                            else:
                                logger.error(
                                    'Type: %s / MSG: %s',
                                    msg.type,
                                    msg,
                                )
                                break
                raise BotReconnect()
            except BotReconnect:
                logger.info('BotReconnect raised. I will reconnect to rtm.')
                continue
            except:  # noqa
                logger.exception('Unexpected Exception raised')
                continue
