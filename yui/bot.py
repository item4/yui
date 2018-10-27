import asyncio
import functools
import importlib
import logging
import logging.config
import traceback
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Any, Callable, Dict, List, TypeVar, Union

import aiocron

import aiohttp

import async_timeout

import ujson

from .api import SlackAPI
from .box import Box, box
from .box.tasks import CronTask
from .config import Config
from .event import create_event
from .orm import Base, EngineConfig, get_database_engine, make_session
from .session import client_session
from .types.base import ChannelID, UserID
from .types.namespace.linked import (
    BotLinkedNamespace,
    Channel,
    DirectMessageChannel,
    PrivateChannel,
    PublicChannel,
    User,
)


__all__ = 'APICallError', 'Bot', 'BotReconnect'

R = TypeVar('R')


class BotReconnect(Exception):
    """Exception for reconnect bot"""


class APICallError(Exception):
    """Fail to call API"""

    def __init__(
        self,
        message: str,
        *,
        status_code: int = None,
        result: Dict[str, Any] = None,
        headers: Any = None,
    ) -> None:
        super(APICallError, self).__init__(message)

        self.status_code = status_code
        self.result = result
        self.headers = headers


class Bot:
    """Yui."""

    loop: asyncio.AbstractEventLoop

    def __init__(
        self,
        config: Config,
        *,
        orm_base=None,
        using_box: Box = None,
    ) -> None:
        """Initialize"""

        logging.config.dictConfig(config.LOGGING)

        logger = logging.getLogger(f'{__name__}.Bot.__init__')

        logger.info('start')

        BotLinkedNamespace._bot = self

        self.process_pool_executor = ProcessPoolExecutor()
        self.thread_pool_executor = ThreadPoolExecutor()

        logger.info('connect to DB')
        config.DATABASE_ENGINE = get_database_engine(config)

        logger.info('import apps')
        for app_name in config.APPS:
            logger.debug('import apps: %s', app_name)
            importlib.import_module(app_name)

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

        self.config.check_and_cast(self.box.config_required)
        self.config.check_channel(
            self.box.channel_required,
            self.box.channels_required,
        )

        if self.config.REGISTER_CRONTAB:
            logger.info('register crontab')
            self.register_tasks()

    def register_tasks(self):
        """Register cronjob to bot from box."""

        logger = logging.getLogger(
            f'{__name__}.Bot.register_tasks'
        )

        def register(c: CronTask):
            logger.info(f'register {c}')
            lock = asyncio.Lock()
            func_params = c.handler.params
            kw: Dict[str, Any] = {}
            if 'bot' in func_params:
                kw['bot'] = self

            @aiocron.crontab(c.spec, *c.args, **c.kwargs)
            async def task():
                if lock.locked():
                    return
                async with lock:
                    if 'loop' in func_params:
                        kw['loop'] = self.loop

                    sess = make_session(bind=self.config.DATABASE_ENGINE)
                    if 'sess' in func_params:
                        kw['sess'] = sess

                    if 'engine_config' in func_params:
                        kw['engine_config'] = EngineConfig(
                            url=self.config.DATABASE_URL,
                            echo=self.config.DATABASE_ECHO,
                        )

                    logger.debug(f'hit and start to run {c}')
                    try:
                        await c.handler(**kw)
                    except:  # noqa: E722
                        logger.error(f'Error: {traceback.format_exc()}')
                        await self.say(
                            self.config.OWNER_ID,
                            '*Traceback*\n```\n{}\n```\n'.format(
                                traceback.format_exc(),
                            )
                        )
                    finally:
                        sess.close()
                    logger.debug(f'end {c}')

            c.start = task.start
            c.stop = task.stop

        for c in self.box.tasks:
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
        data: Dict[str, str] = None,
        *,
        token: str = None,
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

        async def handle(handler, event):
            try:
                return await handler.run(self, event)
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
                    self.config.OWNER_ID,
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

            for handler in self.box.apps:
                result = await handle(handler, event)
                if not result:
                    break

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
