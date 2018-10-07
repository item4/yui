import datetime

from ...box import box
from ...command import argument, option
from ...event import Message
from ...transform import str_to_date


@box.command('dday', ['디데이', 'd-day'])
@option('--at', default=datetime.date.today,
        transform_func=str_to_date(datetime.date.today))
@argument('date', nargs=-1, concat=True, transform_func=str_to_date(),
          count_error='날짜를 입력해주세요',
          transform_error='인식할 수 있는 날짜가 아니에요')
async def dday(
    bot,
    event: Message,
    at: datetime.date,
    date: datetime.date
):
    """
    D-Day 계산

    주어진 날짜를 기준으로 날짜의 차이를 출력합니다.

    `{PREFIX}dday 2003년 6월 3일` (오늘을 기준으로 2003년 6월 3일로부터 며칠 지났는지 계산)
    `{PREFIX}dday --at="2010년 1월 1일" 2003년 6월 3일 (2010년 1월 1일을 기준으로 계산)

    날짜는 `2003-06-03`/`20030603`/`2003.06.03`/`2003년06월03일` 형식을 지원합니다.
    (띄어쓰기 허용)

    """

    diff = (date-at).days
    if diff > 0:
        await bot.say(
            event.channel,
            '{}로부터 {}까지 {:,}일 남았어요!'.format(
                at.strftime('%Y년 %m월 %d일'),
                date.strftime('%Y년 %m월 %d일'),
                diff,
            )
        )
    else:
        await bot.say(
            event.channel,
            '{}로부터 {}까지 {:,}일 지났어요!'.format(
                date.strftime('%Y년 %m월 %d일'),
                at.strftime('%Y년 %m월 %d일'),
                -diff,
            )
        )
