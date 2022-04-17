import asyncio
import functools
import importlib
import logging
import logging.config
import random
import string
from collections import defaultdict
from collections.abc import Callable
from concurrent.futures import BrokenExecutor
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import ParamSpec
from typing import TypeVar

import aiocron

import aiohttp
from aiohttp.client_exceptions import ClientError
from aiohttp.client_exceptions import ContentTypeError
from aiohttp.client_ws import ClientWebSocketResponse

import async_timeout

from dateutil.tz import tzoffset

import emcache

from .api import SlackAPI
from .box import Box
from .box import box
from .box.tasks import CronTask
from .cache import Cache
from .config import Config
from .event import create_event
from .orm import Base
from .orm import get_database_engine
from .orm import make_session
from .types.base import ChannelID
from .types.base import UserID
from .types.channel import DirectMessageChannel
from .types.channel import PrivateChannel
from .types.channel import PublicChannel
from .types.slack.response import APIResponse
from .types.user import User
from .utils import json
from .utils.datetime import now
from .utils.report import report


P = ParamSpec("P")
R = TypeVar("R")
UTC9 = tzoffset("UTC9", timedelta(hours=9))


class BotReconnect(Exception):
    """Exception for reconnect bot"""


class APICallError(Exception):
    """Fail to call API"""

    def __init__(
        self,
        method: str,
        headers: dict[str, str],
        data: dict[str, str] | None,
    ) -> None:
        super(APICallError, self).__init__()

        self.method = method
        self.headers = headers
        self.data = data


class Bot:
    """Yui."""

    api: SlackAPI
    mc: emcache.Client
    cache: Cache

    def __init__(
        self,
        config: Config,
        *,
        orm_base=None,
        using_box: Box = None,
    ) -> None:
        """Initialize"""

        logging.config.dictConfig(config.LOGGING)

        logger = logging.getLogger(f"{__name__}.Bot.__init__")

        logger.info("start")

        self.process_pool_executor = ProcessPoolExecutor()
        self.thread_pool_executor = ThreadPoolExecutor()

        logger.info("connect to DB")
        config.DATABASE_ENGINE = get_database_engine(config)

        logger.info("connect to memcache")

        logger.info("import apps")
        for app_name in config.APPS:
            logger.debug("import apps: %s", app_name)
            importlib.import_module(app_name)

        self.config = config

        try:
            loop = asyncio.get_running_loop()
            loop.set_debug(self.config.DEBUG)
        except RuntimeError:
            pass

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
        self.method_last_call: defaultdict[str, datetime] = defaultdict(now)
        self.method_queue: defaultdict[str, list] = defaultdict(list)

        self.config.check(
            self.box.config_required,
            self.box.channel_required,
            self.box.channels_required,
            self.box.user_required,
            self.box.users_required,
        )

    async def register_tasks(self):
        """Register cronjob to bot from box."""

        logger = logging.getLogger(f"{__name__}.Bot.register_tasks")
        loop = asyncio.get_running_loop()

        def register(bot, c: CronTask):
            logger.info(f"register {c}")
            is_runnable = [1]
            func_params = c.handler.params
            kw: dict[str, Any] = {}
            if "bot" in func_params:
                kw["bot"] = bot

            @aiocron.crontab(c.spec, tz=UTC9, loop=loop, *c.args, **c.kwargs)
            async def task():
                if not bot.is_ready:
                    logger.debug(f"cron condition hit but not ready {c}")
                    return
                logger.debug(f"cron condition hit {c}")
                if not is_runnable:
                    logger.debug(f"cron skip(lock) {c}")
                    return

                is_runnable.pop()
                if "loop" in func_params:
                    kw["loop"] = asyncio.get_running_loop()

                sess = make_session(bind=bot.config.DATABASE_ENGINE)
                if "sess" in func_params:
                    kw["sess"] = sess

                logger.debug(f"cron run {c}")
                try:
                    await c.handler(**kw)
                except APICallError as e:
                    await report(self, exception=e)
                except:  # noqa: E722
                    await report(self)
                finally:
                    await sess.close()
                    is_runnable.append(1)
                logger.debug(f"cron end {c}")

            c.start = task.start
            c.stop = task.stop

        for c in self.box.tasks:
            register(self, c)

    async def run(self):
        """Run"""

        logger = logging.getLogger(f"{__name__}.Bot.run")

        if self.config.REGISTER_CRONTAB:
            logger.info("register crontab")
            await self.register_tasks()

        while True:
            self.mc = await emcache.create_client(
                [
                    emcache.MemcachedHostAddress(
                        self.config.CACHE["HOST"],
                        self.config.CACHE["PORT"],
                    )
                ]
            )
            self.cache = Cache(
                self.mc,
                self.config.CACHE.get("PREFIX", "YUI_"),
            )

            await asyncio.wait(
                (
                    self.connect(),
                    self.process(),
                ),
                return_when=asyncio.FIRST_EXCEPTION,
            )

    async def run_in_other_process(
        self,
        f: Callable[P, R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        loop = asyncio.get_running_loop()
        try:
            return await loop.run_in_executor(
                executor=self.process_pool_executor,
                func=functools.partial(f, *args, **kwargs),
            )
        except BrokenExecutor:
            self.process_pool_executor = ProcessPoolExecutor()
            raise

    async def run_in_other_thread(
        self,
        f: Callable[P, R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        loop = asyncio.get_running_loop()
        try:
            return await loop.run_in_executor(
                executor=self.thread_pool_executor,
                func=functools.partial(f, *args, **kwargs),
            )
        except BrokenExecutor:
            self.thread_pool_executor = ThreadPoolExecutor()
            raise

    async def throttle(self, method: str):
        name = "".join(random.choice(string.printable) for _ in range(16))
        q = self.method_queue[method]
        q.append(name)
        while q and q[0] != name:
            await asyncio.sleep(0.05)

        method_dt = self.method_last_call[method]
        tier_min = self.api.throttle_interval[method]
        if (gap := now() - method_dt) < tier_min:
            await asyncio.sleep(delay=gap.microseconds / 1_000_000)
        self.method_last_call[method] = now()
        try:
            q.pop(0)
        except KeyError:
            pass

    async def call(
        self,
        method: str,
        data: dict[str, Any] = None,
        *,
        throttle_check: bool = True,
        token: str = None,
        json_mode: bool = False,
    ) -> APIResponse:
        """Call API methods."""
        if throttle_check:
            await self.throttle(method)
        async with aiohttp.ClientSession() as session:
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
            }
            payload: str | aiohttp.FormData
            if json_mode:
                payload = json.dumps(data)
                headers["Content-Type"] = "application/json"
                headers["Authorization"] = "Bearer {}".format(
                    token or self.config.TOKEN
                )
            else:
                payload = aiohttp.FormData(data or {})
                payload.add_field("token", token or self.config.TOKEN)

            try:
                async with session.post(
                    "https://slack.com/api/{}".format(method),
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
            except ClientError as e:
                raise APICallError(
                    method=method,
                    headers=headers,
                    data=data,
                ) from e

    async def say(
        self,
        channel: ChannelID,
        text: str,
        *,
        length_limit: int | None = 3000,
        **kwargs,
    ) -> APIResponse:
        """Shortcut for bot saying."""

        return await self.api.chat.postMessage(
            channel,
            text[:length_limit],
            as_user=True,
            link_names=True,
            **kwargs,
        )

    async def process(self):
        """Process messages."""

        logger = logging.getLogger(f"{__name__}.Bot.process")

        async def handle(handler, event):
            try:
                return await handler.run(self, event)
            except SystemExit:
                logger.info("SystemExit")
                raise
            except BotReconnect:
                logger.info("BotReconnect raised.")
                self.restart = True
                return False
            except APICallError as e:
                await report(self, event=event, exception=e)
                return False
            except:  # noqa: E722
                await report(self, event=event)
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
                {"id": datetime.now().toordinal(), "type": "ping"},
                dumps=json.dumps,
            )
            await asyncio.sleep(60)

    async def receive(self, ws: ClientWebSocketResponse):
        timeout = self.config.RECEIVE_TIMEOUT
        logger = logging.getLogger(f"{__name__}.Bot.receive")

        while not ws.closed:
            if self.restart:
                self.restart = False
                await ws.close()
                break

            try:
                async with async_timeout.timeout(timeout):
                    msg: aiohttp.WSMessage = await ws.receive()
            except asyncio.TimeoutError:
                logger.error(f"receive timeout({timeout})")
                await ws.close()
                break

            if msg == aiohttp.http.WS_CLOSED_MESSAGE:
                break

            if msg.type == aiohttp.WSMsgType.TEXT:
                source = msg.json(loads=json.loads)
                type_ = source.pop("type", None)
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
                logger.info("websocket closed")
                break
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.error(msg.data)
                break
            else:
                logger.error(
                    "Type: %s / MSG: %s",
                    msg.type,
                    msg,
                )
                break

    async def connect(self):
        """Connect Slack RTM."""
        logger = logging.getLogger(f"{__name__}.Bot.connect")

        while True:
            await self.queue.put(create_event("yui_system_start", {}))
            while not self.is_ready:
                await asyncio.sleep(0.1)

            try:
                rtm = await self.call("rtm.connect")
            except Exception as e:
                logger.exception(e)
                continue
            if not rtm.body["ok"]:
                if rtm.body["error"] in {
                    "migration_in_progress",
                    "ratelimited",
                    "accesslimited",
                    "service_unavailable",
                    "fatal_error",
                    "internal_error",
                }:
                    await asyncio.sleep(60)
                continue

            try:
                logger.info("Connected to Slack RTM.")
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(rtm.body["url"]) as ws:
                        await asyncio.wait(
                            (
                                self.ping(ws),
                                self.receive(ws),
                            ),
                            return_when=asyncio.FIRST_COMPLETED,
                        )

                raise BotReconnect()
            except BotReconnect:
                logger.info("BotReconnect raised. I will reconnect to rtm.")
                continue
            except:  # noqa
                logger.exception("Unexpected Exception raised")
                continue

    async def get_user(self, user_id: UserID) -> User:
        resp = await self.api.users.info(user=user_id)
        if isinstance(resp.body, dict):
            return User(**resp.body["user"])
        raise ValueError("Unexpected response")
