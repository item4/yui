import aiohttp

from ....bot import Bot
from ....types.slack.attachment import Attachment
from ....utils.html import get_root
from ....utils.http import USER_AGENT

PACKTPUB_URL = "https://www.packtpub.com/free-learning"
HEADERS = {
    "User-Agent": USER_AGENT,
}


async def say_packtpub_dotd(bot: Bot, channel):
    attachments: list[Attachment] = []
    url = "https://www.packtpub.com/free-learning"
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(url) as resp:
            data = await resp.read()

    h = get_root(data)

    try:
        container = h.cssselect("main.product")[0]
        title = str(
            container.cssselect("h3.product-info__title")[0].text_content()
        ).replace("Free eBook - ", "")
        image_url = str(container.cssselect("img.product-image")[0].get("src"))

        attachments.append(
            Attachment(
                fallback=f"{title} - {PACKTPUB_URL}",
                title=title,
                title_link=PACKTPUB_URL,
                text="오늘의 Packt Book Deal of The Day:"
                f" {title} - {PACKTPUB_URL}",
                image_url=image_url,
            )
        )
    except IndexError:
        pass

    if attachments:
        await bot.api.chat.postMessage(
            channel=channel,
            text="오늘자 PACKT Book의 무료책이에요!",
            attachments=attachments,
        )
    else:
        await bot.say(channel, "오늘은 PACKT Book의 무료책이 없는 것 같아요")
