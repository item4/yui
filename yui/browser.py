from aiocontext import async_contextmanager

import aiohttp

from pyppeteer.launcher import connect

from .utils import json


@async_contextmanager
async def new_page(bot):
    async with aiohttp.ClientSession() as session:
        async with session.get(bot.config.WEBSOCKETDEBUGGERURL) as resp:
            data = await resp.json(loads=json.loads)

    browser = await connect(
        {'browserWSEndpoint': data['webSocketDebuggerUrl']}
    )

    page = await browser.newPage()

    yield page

    await page.close()
