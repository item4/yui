from __future__ import annotations

import asyncio
import contextlib
import functools
import importlib
import logging
import logging.config
import random
import string
from collections import defaultdict
from concurrent.futures import BrokenExecutor
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import ParamSpec
from typing import TYPE_CHECKING
from typing import TypeVar

import aiocron
import aiohttp
from aiohttp.client_exceptions import ClientError
from dateutil.tz import tzoffset
from redis.asyncio.client import Redis

from .api import SlackAPI
from .box import Box
from .box import box
from .cache import Cache
from .event import create_event
from .log import GetLoggerMixin
from .orm import Base
from .orm import create_database_engine
from .orm import sessionmaker
from .types.slack.response import APIResponse
from .types.user import User
from .utils import json
from .utils.datetime import now
from .utils.report import report

if TYPE_CHECKING:
    from collections.abc import Callable

    from aiohttp.client_ws import ClientWebSocketResponse

    from .box.tasks import CronTask
    from .config import Config
    from .types.base import ChannelID
    from .types.base import UserID


P = ParamSpec("P")
R = TypeVar("R")
UTC9 = tzoffset("UTC9", timedelta(hours=9))

FATAL_ERROR_CODES = frozenset(
    {
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
    },
)
RECONNECT_ERROR_CODES = frozenset(
    {
        "migration_in_progress",
        "ratelimited",
        "accesslimited",
        "request_timeout",
        "service_unavailable",
        "fatal_error",
        "internal_error",
    },
)


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
        super().__init__()

        self.method = method
        self.headers = headers
        self.data = data


class Bot(GetLoggerMixin):
    """Yui."""

    api: SlackAPI
    redis_client: Redis
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

        logger = self.get_logger("__init__")

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
        self.restart = False
        self.is_ready = asyncio.Event()
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

        logger = self.get_logger("register_tasks")
        loop = asyncio.get_running_loop()

        def register(bot, c: CronTask):
            logger.info(f"register {c}")
            is_runnable = [1]
            func_params = c.handler.params
            kw: dict[str, Any] = {}
            if "bot" in func_params:
                kw["bot"] = bot

            @aiocron.crontab(c.spec, *c.args, **c.kwargs, tz=UTC9, loop=loop)
            async def task():
                log = logging.getLogger(repr(c.handler))

                if not bot.is_ready.is_set():
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

        logger = self.get_logger("run")

        if self.config.REGISTER_CRONTAB:
            logger.info("register crontab")
            await self.register_tasks()

        redis_retries = 0

        while True:
            self.redis_client = Redis.from_url(self.config.CACHE["URL"])
            self.cache = Cache(
                self.redis_client,
                self.config.CACHE.get("PREFIX", "YUI_"),
            )
            try:
                await self.cache.set("__test__", 1)
            except (
                RuntimeError,
                TimeoutError,
                asyncio.CancelledError,
            ) as e:
                logger.exception("fail to connect to redis")
                redis_retries += 1
                if redis_retries < 3:
                    await self.cache.close()
                    await asyncio.sleep(redis_retries * 5)
                    continue
                logger.fatal("can not connect to redis. stop to run")
                raise SystemExit from e

            redis_retries = 0

            tasks = [
                asyncio.create_task(self.connect()),
                asyncio.create_task(self.process()),
            ]
            await asyncio.wait(
                tasks,
                return_when=asyncio.FIRST_EXCEPTION,
            )

            await self.cache.close()

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
        except BrokenExecutor:  # pragma: no cover
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
        except BrokenExecutor:  # pragma: no cover
            self.thread_pool_executor = ThreadPoolExecutor()
            raise

    async def throttle(self, method: str):
        name = "".join(random.choice(string.printable) for _ in range(16))
        q = self.method_queue[method]
        q.append(name)
        # FIXME: https://docs.astral.sh/ruff/rules/async-busy-wait/
        while q and q[0] != name:  # noqa: ASYNC110
            await asyncio.sleep(0.05)

        method_dt = self.method_last_call[method]
        tier_min = self.api.throttle_interval[method]
        if (gap := now() - method_dt) < tier_min:
            await asyncio.sleep(delay=gap.microseconds / 1_000_000)
        self.method_last_call[method] = now()
        with contextlib.suppress(KeyError):
            q.pop(0)

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

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        payload: str | aiohttp.FormData
        if json_mode:
            payload = json.dumps(data)
            headers["Content-Type"] = "application/json; charset=utf-8"
            headers["Authorization"] = (
                f"Bearer {token or self.config.BOT_TOKEN}"
            )
        else:
            payload = aiohttp.FormData(data or {})
            payload.add_field("token", token or self.config.BOT_TOKEN)

        async with aiohttp.ClientSession(headers=headers) as session:
            try:
                async with session.post(
                    f"https://slack.com/api/{method}",
                    data=payload,
                ) as response:
                    result = await response.json(loads=json.loads)
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

        logger = self.get_logger("process")

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
        logger = self.get_logger("receive")

        while not ws.closed:
            if self.restart:
                self.restart = False
                await ws.close()
                break
            if ws.closed:
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
                except:  # noqa: E722
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
        """Connect Slack Socket Mode."""
        logger = self.get_logger("connect")

        await self.queue.put(create_event("yui_system_start", {}))
        await self.is_ready.wait()

        while True:
            try:
                resp = await self.api.apps.connections.open(
                    token=self.config.APP_TOKEN,
                )
            except Exception:
                logger.exception("Failed to connect Slack")
                await asyncio.sleep(60)
                continue
            if not resp.body["ok"]:
                if resp.body["error"] in FATAL_ERROR_CODES:
                    logger.error(resp.body["error"])
                    break

                if resp.body["error"] in RECONNECT_ERROR_CODES:
                    await asyncio.sleep(60)
                continue

            try:
                logger.info("Connected to Slack")
                async with aiohttp.ClientSession() as session, session.ws_connect(
                    resp.body["url"],
                ) as ws:
                    tasks = [
                        asyncio.create_task(self.ping(ws)),
                        asyncio.create_task(self.receive(ws)),
                    ]
                    await asyncio.wait(
                        tasks,
                        return_when=asyncio.FIRST_COMPLETED,
                    )

                raise BotReconnect
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
