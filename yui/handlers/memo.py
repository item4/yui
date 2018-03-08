from ..box import box
from ..command import argument
from ..event import Message
from ..models.memo import Memo
from ..util import now


@box.command('기억')
@argument('keyword')
@argument('text', nargs=-1, concat=True)
async def memo_add(bot, event: Message, sess, keyword: str, text: str):
    """
    기억 레코드 생성

    `{PREFIX}기억 키리토 귀엽다` (`키리토`라는 단어를 `귀엽다`라는 내용으로 저장)
    `{PREFIX}기억 "키리가야 카즈토" 키리토의 본명` (`키리가야 카즈토`에 대한 정보를 저장)

    """

    memo = Memo()
    memo.keyword = keyword
    memo.author = event.user.id
    memo.text = text
    memo.created_at = now()

    with sess.begin():
        sess.add(memo)

    await bot.say(
        event.channel,
        f'`{keyword}`로 기억 레코드를 생성했어요!'
    )


@box.command('알려')
@argument('keyword', nargs=-1, concat=True)
async def memo_show(bot, event: Message, sess, keyword: str):
    """
    기억 레코드 출력

    `{PREFIX}알려 키리토` (`키리토`에 관한 모든 기억 레코드를 출력)

    """

    memos = sess.query(Memo).filter_by(keyword=keyword)\
        .order_by(Memo.created_at).all()

    if memos:
        await bot.say(
            event.channel,
            f'`{keyword}`: ' + ' | '.join(x.text for x in memos)
        )
    else:
        await bot.say(
            event.channel,
            f'`{keyword}`란 이름을 가진 기억 레코드가 없어요!'
        )


@box.command('잊어')
@argument('keyword', nargs=-1, concat=True)
async def memo_delete(bot, event: Message, sess, keyword: str):
    """
    기억 레코드 삭제

    `{PREFIX}잊어 키리토` (`키리토`에 관한 모든 기억 레코드를 삭제)

    """

    sess.query(Memo).filter_by(keyword=keyword).delete()

    await bot.say(
        event.channel,
        f'`{keyword}`에 관한 기억 레코드를 모두 삭제했어요!'
    )
