import pytest
from time_machine import travel

from yui.apps.info.packtpub.commands import packtpub_dotd
from yui.apps.info.packtpub.commons import PACKTPUB_URL
from yui.apps.info.packtpub.tasks import auto_packtpub_dotd
from yui.utils.datetime import datetime

from ...util import FakeBot

MOCK_BODY = """\
<!doctype html>
<html>
<main class="product">
<h3 class="product-info__title">Free eBook - {title}</h3>
<img class="product-image" src="{image_url}" alt="">
</main>
</html>
"""


@pytest.mark.asyncio
@travel(datetime(2018, 10, 7), tick=False)
async def test_no_packtpub_dotd(bot, response_mock):
    response_mock.get(
        "https://www.packtpub.com/free-learning",
        body="""\
<!doctype html>
<html>
<main class="product">
<p>Something else</p>
</main>
</html>
""",
        headers={"Content-Type": "text/html"},
    )

    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")

    event = bot.create_message("C1", "U1")

    await packtpub_dotd(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "오늘은 PACKT Book의 무료책이 없는 것 같아요"


@pytest.mark.asyncio
@travel(datetime(2018, 10, 7), tick=False)
async def test_packtpub_dotd(bot, response_mock):
    title = "test book"
    image_url = "test url"
    response_mock.get(
        "https://www.packtpub.com/free-learning",
        body=MOCK_BODY.format(title=title, image_url=image_url),
        headers={"Content-Type": "text/html"},
    )

    bot.add_channel("C1", "general")
    bot.add_user("U1", "item4")

    event = bot.create_message("C1", "U1")

    await packtpub_dotd(bot, event)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "오늘자 PACKT Book의 무료책이에요!"
    attachments = said.data["attachments"]
    assert len(attachments) == 1
    assert attachments[0]["fallback"] == f"{title} - {PACKTPUB_URL}"
    assert attachments[0]["title"] == title
    assert attachments[0]["title_link"] == PACKTPUB_URL
    assert (
        attachments[0]["text"]
        == f"오늘의 Packt Book Deal of The Day: {title} - {PACKTPUB_URL}"
    )
    assert attachments[0]["image_url"] == image_url


@pytest.mark.asyncio
@travel(datetime(2018, 10, 7), tick=False)
async def test_auto_packtpub_dotd(bot_config, response_mock):
    assert auto_packtpub_dotd.cron.spec == "5 9 * * *"
    title = "test book"
    image_url = "test url"
    response_mock.get(
        "https://www.packtpub.com/free-learning",
        body=MOCK_BODY.format(title=title, image_url=image_url),
        headers={"Content-Type": "text/html"},
    )

    bot_config.CHANNELS = {
        "general": "C1",
    }
    bot = FakeBot(bot_config)
    bot.add_channel("C1", "general")

    await auto_packtpub_dotd(bot)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == "오늘자 PACKT Book의 무료책이에요!"
    attachments = said.data["attachments"]
    assert len(attachments) == 1
    assert attachments[0]["fallback"] == f"{title} - {PACKTPUB_URL}"
    assert attachments[0]["title"] == title
    assert attachments[0]["title_link"] == PACKTPUB_URL
    assert (
        attachments[0]["text"]
        == f"오늘의 Packt Book Deal of The Day: {title} - {PACKTPUB_URL}"
    )
    assert attachments[0]["image_url"] == image_url
