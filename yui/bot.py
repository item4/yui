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
import emcache
from aiohttp.client_exceptions import ClientError
from aiohttp.client_exceptions import ContentTypeError
from aiohttp.client_ws import ClientWebSocketResponse
from dateutil.tz import tzoffset

from .api import SlackAPI
from .box import Box
from .box import box
from .box.tasks import CronTask
from .cache import Cache
from .config import Config
from .event import create_event
from .orm import Base
from .orm import create_database_engine
from .orm import sessionmaker
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
        using_box: Box | None = None,
    ) -> None:
        """Initialize"""

        logging.config.dictConfig(config.LOGGING)

        logger = logging.getLogger(f"{__name__}.Bot.__init__")

        logger.info("start")

        self.process_pool_executor = ProcessPoolExecutor()
        self.thread_pool_executor = ThreadPoolExecutor()

        logger.info("connect to DB")
        self.database_engine = create_database_engine(
            config.DATABASE_URL,
            echo=config.DATABASE_ECHO,
        )
        self.session_maker = sessionmaker(self.database_engine)

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
                log = logging.getLogger(repr(c.handler))

                if not bot.is_ready:
                    log.debug("cron condition hit but not ready")
                    return
                log.debug("cron condition hit")
                if not is_runnable:
                    log.debug("cron skip by lock")
                    return

                is_runnable.pop()
                if "loop" in func_params:
                    kw["loop"] = asyncio.get_running_loop()

                sess = bot.session_maker()
                if "sess" in func_params:
                    kw["sess"] = sess

                log.debug("cron run")
                try:
                    await c.handler(**kw)
                except APICallError as e:
                    await report(self, exception=e)
                except:  # noqa: E722
                    await report(self)
                finally:
                    await sess.close()
                    is_runnable.append(1)
                log.debug("cron end")

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

            tasks = [
                asyncio.create_task(self.connect()),
                asyncio.create_task(self.process()),
            ]
            await asyncio.wait(
                tasks,
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
        data: dict[str, Any] | None = None,
        *,
        throttle_check: bool = True,
        token: str | None = None,
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
                headers["Content-Type"] = "application/json; charset=utf-8"
                headers["Authorization"] = "Bearer {}".format(
                    token or self.config.BOT_TOKEN
                )
            else:
                payload = aiohttp.FormData(data or {})
                payload.add_field("token", token or self.config.BOT_TOKEN)

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
                logger.exception("APICallError on app handle process")
                await report(self, event=event, exception=e)
                return False
            except:  # noqa: E722
                logger.exception("Unexpected exception on app handle process")
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
            await ws.ping()
            await asyncio.sleep(10)

    async def acknowledge(self, ws: ClientWebSocketResponse, envelope_id: str):
        if not ws.closed:
            await ws.send_json(
                {"envelope_id": envelope_id},
                dumps=json.dumps,
            )

    async def receive(self, ws: ClientWebSocketResponse):
        logger = logging.getLogger(f"{__name__}.Bot.receive")

        while not ws.closed:
            if self.restart:
                self.restart = False
                await ws.close()
                break
            elif ws.closed:
                await ws.close()
                break

            msg: aiohttp.WSMessage = await ws.receive()

            if msg == aiohttp.http.WS_CLOSED_MESSAGE:
                break

            if msg.type == aiohttp.WSMsgType.TEXT:
                source = msg.json(loads=json.loads)
                envelope_id = source.pop("envelope_id", None)
                payload = source.pop("payload", {})
                event = payload.pop("event", None)
                if envelope_id:
                    await self.acknowledge(ws, envelope_id)
                if not event:
                    continue
                type_ = event.pop("type", None)
                try:
                    event = create_event(type_, event)
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
                resp = await self.api.apps.connections.open(
                    token=self.config.APP_TOKEN
                )
            except Exception as e:
                logger.exception(e)
                continue
            if not resp.body["ok"]:
                if resp.body["error"] in {
                    "invalid_auth",
                    "missing_args",
                    "insecure_request",
                    "forbidden_team",
                    "not_authed",
                    "access_denied",
                    "account_inactive",
                    "token_revoked",
                    "token_expired",
                    "no_permission",
                    "not_allowed_token_type",
                    "invalid_charset",
                }:
                    logger.error(resp.body["error"])
                    break

                if resp.body["error"] in {
                    "migration_in_progress",
                    "ratelimited",
                    "accesslimited",
                    "request_timeout",
                    "service_unavailable",
                    "fatal_error",
                    "internal_error",
                }:
                    await asyncio.sleep(60)
                continue

            try:
                logger.info("Connected to Slack")
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(resp.body["url"]) as ws:
                        tasks = [
                            asyncio.create_task(self.ping(ws)),
                            asyncio.create_task(self.receive(ws)),
                        ]
                        await asyncio.wait(
                            tasks,
                            return_when=asyncio.FIRST_COMPLETED,
                        )

                raise BotReconnect()
            except BotReconnect:
                logger.info("BotReconnect raised. I will reconnect soon.")
                continue
            except:  # noqa
                logger.exception("Unexpected Exception raised")
                continue

    async def get_user(self, user_id: UserID) -> User:
        resp = await self.api.users.info(user=user_id)
        if isinstance(resp.body, dict):
            return User(**resp.body["user"])
        raise ValueError("Unexpected response")
