import asyncio
from typing import Any
from typing import Coroutine

from ..types.slack.response import APIResponse


async def retry(coro: Coroutine[Any, Any, APIResponse]) -> APIResponse:
    sleep = 1
    while True:
        resp = await coro
        if isinstance(resp.body, dict) and resp.body['ok']:
            return resp
        if sleep > 16:
            return resp
        if resp.status == 429:
            seconds = int(resp.headers['Retry-After']) + 0.5
            await asyncio.sleep(seconds)
        else:
            await asyncio.sleep(sleep)
            sleep += 1
