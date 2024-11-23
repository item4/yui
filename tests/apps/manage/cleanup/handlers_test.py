import pytest
from sqlalchemy.sql.expression import func
from sqlalchemy.sql.expression import select

from yui.apps.manage.cleanup.handlers import make_log
from yui.apps.manage.cleanup.models import EventLog

from ....util import FakeBot


@pytest.mark.asyncio
async def test_make_log(bot_config, fx_sess):
    channel_1 = "C111"
    channel_2 = "C222"
    channel_3 = "C333"
    bot_config.CHANNELS["auto_cleanup_targets"] = [channel_1, channel_2]
    bot = FakeBot(bot_config)
    assert (
        await fx_sess.scalar(
            select(func.count(EventLog.id)),
        )
        == 0
    )
    event = bot.create_message(channel_id=channel_3, ts="11111.1")
    await make_log(bot, event, fx_sess)
    assert (
        await fx_sess.scalar(
            select(func.count(EventLog.id)),
        )
        == 0
    )

    event = bot.create_message(channel_id=channel_1, ts="11112.2")
    await make_log(bot, event, fx_sess)
    assert (
        await fx_sess.scalar(
            select(func.count(EventLog.id)),
        )
        == 1
    )
    await make_log(bot, event, fx_sess)
    assert (
        await fx_sess.scalar(
            select(func.count(EventLog.id)),
        )
        == 1
    )

    event = bot.create_message(
        subtype="message_deleted",
        channel_id=channel_2,
        ts="11113.3",
    )
    await make_log(bot, event, fx_sess)
    assert (
        await fx_sess.scalar(
            select(func.count(EventLog.id)),
        )
        == 1
    )
