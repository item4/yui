from contextlib import asynccontextmanager

import aiohttp
from pyppeteer.launcher import connect

from .utils import json


@asynccontextmanager
async def new_page(bot):
    async with aiohttp.ClientSession() as session, session.get(
        bot.config.WEBSOCKETDEBUGGERURL
    ) as resp:
        data = await resp.json(loads=json.loads)

    browser = await connect({"browserWSEndpoint": data["webSocketDebuggerUrl"]})

    page = await browser.newPage()

    yield page

    await page.close()
