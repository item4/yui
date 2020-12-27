import asyncio
import functools
import importlib
import logging
import logging.config
import traceback
from concurrent.futures import BrokenExecutor
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Callable
from typing import Optional
from typing import TypeVar
from typing import Union

import aiocron

import aiohttp
from aiohttp.client_exceptions import ClientConnectorError
from aiohttp.client_exceptions import ContentTypeError
from aiohttp.client_ws import ClientWebSocketResponse

import aiomcache

import async_timeout

from dateutil.tz import tzoffset

from .api import SlackAPI
from .box import Box
from .box import box
from .box.tasks import CronTask
from .cache import Cache
from .config import Config
from .event import create_event
from .orm import Base
from .orm import EngineConfig
from .orm import get_database_engine
from .orm import make_session
from .types.base import ChannelID
from .types.channel import Channel
from .types.channel import DirectMessageChannel
from .types.channel import PrivateChannel
from .types.channel import PublicChannel
from .types.namespace import Namespace
from .types.slack.response import APIResponse
from .types.user import User
from .utils import json
from .utils.api import retry
from .utils.report import report


R = TypeVar('R')
UTC9 = tzoffset('UTC9', timedelta(hours=9))


class BotReconnect(Exception):
    """Exception for reconnect bot"""


class APICallError(Exception):
    """Fail to call API"""

    def __init__(
        self,
        method: str,
        headers: dict[str, str],
        data: dict[str, str],
        tb: str,
    ) -> None:
        super(APICallError, self).__init__()

        self.method = method
        self.headers = headers
        self.data = data
        self.tb = tb


class Bot:
    """Yui."""

    api: SlackAPI
    cache: Cache
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

        Namespace._bot = self

        self.process_pool_executor = ProcessPoolExecutor()
        self.thread_pool_executor = ThreadPoolExecutor()

        logger.info('connect to DB')
        config.DATABASE_ENGINE = get_database_engine(config)

        logger.info('connect to memcache')
        self.mc = aiomcache.Client(
            host=config.CACHE['HOST'],
            port=config.CACHE['PORT'],
        )
        self.cache = Cache(self.mc, config.CACHE.get('PREFIX', 'YUI_'))

        logger.info('import apps')
        for app_name in config.APPS:
            logger.debug('import apps: %s', app_name)
            importlib.import_module(app_name)

        self.config = config

        self.orm_base = orm_base or Base
        self.box = using_box or box
        self.queue: asyncio.Queue = asyncio.Queue()
        self.api = SlackAPI(self)
        self.channels: list[PublicChannel] = []
        self.ims: list[DirectMessageChannel] = []
        self.groups: list[PrivateChannel] = []
        self.users: list[User] = []
        self.restart = False
        self.is_ready = False

        self.config.check(
            self.box.config_required,
            self.box.channel_required,
            self.box.channels_required,
            self.box.user_required,
            self.box.users_required,
        )

        if self.config.REGISTER_CRONTAB:
            logger.info('register crontab')
            self.register_tasks()

    def register_tasks(self):
        """Register cronjob to bot from box."""

        logger = logging.getLogger(f'{__name__}.Bot.register_tasks')

        def register(c: CronTask):
            logger.info(f'register {c}')
            lock = asyncio.Lock()
            func_params = c.handler.params
            kw: dict[str, Any] = {}
            if 'bot' in func_params:
                kw['bot'] = self

            @aiocron.crontab(c.spec, tz=UTC9, *c.args, **c.kwargs)
            async def task():
                if lock.locked() or not self.is_ready:
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
                        await report(self, traceback.format_exc())
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
                        self.connect(),
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
        try:
            return await self.loop.run_in_executor(
                executor=self.process_pool_executor,
                func=functools.partial(f, *args, **kwargs),
            )
        except BrokenExecutor:
            self.process_pool_executor = ProcessPoolExecutor()
            raise

    async def run_in_other_thread(
        self,
        f: Callable[..., R],
        *args,
        **kwargs,
    ) -> R:
        try:
            return await self.loop.run_in_executor(
                executor=self.thread_pool_executor,
                func=functools.partial(f, *args, **kwargs),
            )
        except BrokenExecutor:
            self.thread_pool_executor = ThreadPoolExecutor()
            raise

    async def call(
        self,
        method: str,
        data: dict[str, Any] = None,
        *,
        token: str = None,
        json_mode: bool = False,
    ) -> APIResponse:
        """Call API methods."""

        async with aiohttp.ClientSession() as session:
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            payload: Union[str, aiohttp.FormData]
            if json_mode:
                payload = json.dumps(data)
                headers['Content-Type'] = 'application/json'
                headers['Authorization'] = 'Bearer {}'.format(
                    token or self.config.TOKEN
                )
            else:
                payload = aiohttp.FormData(data or {})
                payload.add_field('token', token or self.config.TOKEN)

            try:
                async with session.post(
                    'https://slack.com/api/{}'.format(method),
                    data=payload,
                    headers=headers,
                ) as response:
                    try:
                        result = await response.json(loads=json.loads)
                    except ContentTypeError:
                        result = await response.text()
                    return APIResponse(
                        body=result,
                        status=response.status,
                        headers=response.headers,
                    )
            except ClientConnectorError:
                raise APICallError(
                    method=method,
                    headers=headers,
                    data=data,
                    tb=traceback.format_exc(),
                )

    async def say(
        self,
        channel: Union[Channel, ChannelID],
        text: str,
        *,
        retry_until_send: bool = False,
        length_limit: Optional[int] = 2000,
        **kwargs,
    ) -> APIResponse:
        """Shortcut for bot saying."""

        coro = self.api.chat.postMessage(
            channel,
            text[:length_limit],
            as_user=True,
            link_names=True,
            **kwargs,
        )
        if retry_until_send:
            return await retry(coro)
        return await coro

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
            except APICallError as e:
                await report(self, e.tb, event=event, exception=e)
                return False
            except:  # noqa: E722
                await report(self, traceback.format_exc(), event=event)
                return False

        while True:
            event = await self.queue.get()

            logger.info(event)

            for handler in self.box.apps:
                result = await handle(handler, event)
                if not result:
                    break

    async def ping(self, ws: ClientWebSocketResponse):
        while not ws.closed:
            await ws.send_json(
                {'id': datetime.now().toordinal(), 'type': 'ping'},
                dumps=json.dumps,
            )  # type: ignore
            await asyncio.sleep(60)

    async def receive(self, ws: ClientWebSocketResponse):
        timeout = self.config.RECEIVE_TIMEOUT
        logger = logging.getLogger(f'{__name__}.Bot.receive')

        while not ws.closed:
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
                source = msg.json(loads=json.loads)
                type_ = source.pop('type', None)
                try:
                    event = create_event(type_, source)
                except:  # noqa:
                    logger.exception(msg.data)
                else:
                    await self.queue.put(event)
            elif msg.type in (
                aiohttp.WSMsgType.CLOSE,
                aiohttp.WSMsgType.CLOSED,
                aiohttp.WSMsgType.CLOSING,
            ):
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

    async def connect(self):
        """Connect Slack RTM."""
        logger = logging.getLogger(f'{__name__}.Bot.connect')
        sleep = 0

        while True:
            await self.queue.put(create_event('chatterbox_system_start', {}))
            while not self.is_ready:
                await asyncio.sleep(0.1)

            try:
                rtm = await self.call('rtm.start')
            except Exception as e:
                logger.exception(e)
                await asyncio.sleep((sleep + 1) * 10)
                sleep += 1
                continue

            if not rtm.body['ok']:
                await asyncio.sleep((sleep + 1) * 10)
                sleep += 1
                continue
            else:
                sleep = 0

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(rtm.body['url']) as ws:
                        await asyncio.wait(
                            (
                                self.ping(ws),
                                self.receive(ws),
                            ),
                            return_when=asyncio.FIRST_COMPLETED,
                        )

                raise BotReconnect()
            except BotReconnect:
                logger.info('BotReconnect raised. I will reconnect to rtm.')
                continue
            except:  # noqa
                logger.exception('Unexpected Exception raised')
                continue
