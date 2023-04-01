import pytest
from sqlalchemy.sql.expression import func
from sqlalchemy.sql.expression import select

from yui.apps.info.memo.commands import memo_add
from yui.apps.info.memo.commands import memo_delete
from yui.apps.info.memo.commands import memo_show
from yui.apps.info.memo.models import Memo


@pytest.mark.asyncio
async def test_memo_flow(bot, fx_sess):
    keyword1 = "키리토"
    keyword2 = "밥"
    text1 = "키리가야 카즈토의 게임 아이디"
    text2 = "귀엽다"
    text3 = "먹어야한다"

    bot.add_channel("C1", "test")
    bot.add_user("U1", "tester")
    event = bot.create_message("C1", "U1")

    await memo_show(bot, event, fx_sess, keyword1)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert (
        said.data["text"] == f"`{keyword1}`란 이름을 가진 기억 레코드가 없어요!"
    )

    assert (
        await fx_sess.scalar(
            select(func.count(Memo.id)).where(Memo.keyword == keyword1)
        )
        == 0
    )

    await memo_show(bot, event, fx_sess, keyword2)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert (
        said.data["text"]
        == f"`{keyword2}`이란 이름을 가진 기억 레코드가 없어요!"
    )

    assert (
        await fx_sess.scalar(
            select(func.count(Memo.id)).where(Memo.keyword == keyword2)
        )
        == 0
    )

    await memo_add(bot, event, fx_sess, keyword1, text1)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == f"`{keyword1}`로 기억 레코드를 생성했어요!"

    assert (
        await fx_sess.scalar(
            select(func.count(Memo.id)).where(Memo.keyword == keyword1)
        )
        == 1
    )

    await memo_add(bot, event, fx_sess, keyword2, text3)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == f"`{keyword2}`으로 기억 레코드를 생성했어요!"

    assert (
        await fx_sess.scalar(
            select(func.count(Memo.id)).where(Memo.keyword == keyword2)
        )
        == 1
    )

    await memo_add(bot, event, fx_sess, keyword1, text2)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == f"`{keyword1}`로 기억 레코드를 생성했어요!"

    assert (
        await fx_sess.scalar(
            select(func.count(Memo.id)).where(Memo.keyword == keyword1)
        )
        == 2
    )

    await memo_show(bot, event, fx_sess, keyword1)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == f"`{keyword1}`: {text1} | {text2}"

    await memo_show(bot, event, fx_sess, keyword2)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert said.data["text"] == f"`{keyword2}`: {text3}"

    await memo_delete(bot, event, fx_sess, keyword1)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert (
        said.data["text"]
        == f"`{keyword1}`에 관한 기억 레코드를 모두 삭제했어요!"
    )

    assert (
        await fx_sess.scalar(
            select(func.count(Memo.id)).where(Memo.keyword == keyword1)
        )
        == 0
    )
    assert (
        await fx_sess.scalar(
            select(func.count(Memo.id)).where(Memo.keyword == keyword2)
        )
        == 1
    )

    await memo_delete(bot, event, fx_sess, keyword2)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert (
        said.data["text"]
        == f"`{keyword2}`에 관한 기억 레코드를 모두 삭제했어요!"
    )

    assert (
        await fx_sess.scalar(
            select(func.count(Memo.id)).where(Memo.keyword == keyword1)
        )
        == 0
    )
    assert (
        await fx_sess.scalar(
            select(func.count(Memo.id)).where(Memo.keyword == keyword2)
        )
        == 0
    )


@pytest.mark.asyncio
async def test_length_limit(bot, fx_sess):
    bot.add_channel("C1", "test")
    bot.add_user("U1", "tester")
    event = bot.create_message("C1", "U1")

    await memo_add(bot, event, fx_sess, "long" * 100, "test")

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert (
        said.data["text"]
        == "기억하려는 키워드가 너무 길어요! 20자 이하의 키워드만 가능해요!"
    )

    await memo_add(bot, event, fx_sess, "test", "long" * 1000)

    said = bot.call_queue.pop(0)
    assert said.method == "chat.postMessage"
    assert said.data["channel"] == "C1"
    assert (
        said.data["text"]
        == "기억하려는 내용이 너무 길어요! 500자 이하의 내용만 가능해요!"
    )
