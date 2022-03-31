from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import delete
from sqlalchemy.sql.expression import select

import tossi

from .models import Memo
from ....box import box
from ....command import argument
from ....event import Message
from ....utils import format
from ....utils.datetime import now


@box.command("기억")
@argument("keyword")
@argument("text")
async def memo_add(
    bot, event: Message, sess: AsyncSession, keyword: str, text: str
):
    """
    기억 레코드 생성

    `{PREFIX}기억 키리토 귀엽다` (`키리토`라는 단어를 `귀엽다`라는 내용으로 저장)
    `{PREFIX}기억 "키리가야 카즈토" "키리토의 본명"` (`키리가야 카즈토`에 대한 정보를 저장)

    """

    if len(keyword) > 20:
        await bot.say(
            event.channel,
            "기억하려는 키워드가 너무 길어요! 20자 이하의 키워드만 가능해요!",
        )
        return
    if len(text) > 500:
        await bot.say(
            event.channel,
            "기억하려는 내용이 너무 길어요! 500자 이하의 내용만 가능해요!",
        )
        return

    memo = Memo()
    memo.keyword = keyword
    memo.author = event.user
    memo.text = text
    memo.created_at = now()

    sess.add(memo)
    await sess.commit()

    await bot.say(
        event.channel,
        "{}{} 기억 레코드를 생성했어요!".format(
            format.code(keyword),
            tossi.pick(keyword, "(으)로"),
        ),
    )


@box.command("알려")
@argument("keyword", nargs=-1, concat=True)
async def memo_show(bot, event: Message, sess: AsyncSession, keyword: str):
    """
    기억 레코드 출력

    `{PREFIX}알려 키리토` (`키리토`에 관한 모든 기억 레코드를 출력)

    """

    memos = (
        await sess.scalars(
            select(Memo)
            .where(Memo.keyword == keyword)
            .order_by(Memo.created_at.asc())
        )
    ).all()
    if memos:
        await bot.say(
            event.channel,
            f"{format.code(keyword)}: " + " | ".join(x.text for x in memos),
        )
    else:
        await bot.say(
            event.channel,
            "{}{} 이름을 가진 기억 레코드가 없어요!".format(
                format.code(keyword),
                tossi.pick(keyword, "(이)란"),
            ),
        )


@box.command("잊어")
@argument("keyword", nargs=-1, concat=True)
async def memo_delete(bot, event: Message, sess: AsyncSession, keyword: str):
    """
    기억 레코드 삭제

    `{PREFIX}잊어 키리토` (`키리토`에 관한 모든 기억 레코드를 삭제)

    """

    await sess.execute(delete(Memo).where(Memo.keyword == keyword))
    await sess.commit()

    await bot.say(
        event.channel, f"{format.code(keyword)}에 관한 기억 레코드를 모두 삭제했어요!"
    )
