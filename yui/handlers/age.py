import datetime

from ..box import box
from ..command import argument, option
from ..event import Message
from ..transform import str_to_date


@box.command('나이', ['age'])
@option('--at', dest='today', default=datetime.date.today,
        transform_func=str_to_date(datetime.date.today))
@argument('birthday', nargs=-1, concat=True,
          count_error='생일을 입력해주세요', transform_func=str_to_date(),
          transform_error='인식할 수 있는 날짜가 아니에요!')
async def age(
    bot,
    event: Message,
    today: datetime.date,
    birthday: datetime.date
):
    """
    나이 계산

    주어진 날짜를 기준으로 나이 및 생일 정보를 출력합니다.

    `{PREFIX}나이 2003년 6월 3일` (오늘을 기준으로 2003년 6월 3일생의 나이/생일 정보를 계산)
    `{PREFIX}나이 --at="2010년 1월 1일" 2003년 6월 3일 (2010년 1월 1일을 기준으로 계산)

    날짜는 `2003-06-03`/`20030603`/`2003.06.03`/`2003년06월03일` 형식을 지원합니다.
    (띄어쓰기 허용)

    """

    if today < birthday:
        await bot.say(
            event.channel,
            '기준일 기준으로 아직 태어나지 않았어요!'
        )
        return

    year_age = today.year - birthday.year
    korean_age = year_age + 1

    global_age = today.year - birthday.year
    cond1 = today.month < birthday.month
    cond2 = today.month == birthday.month and today.day < birthday.day
    if cond1 or cond2:
        global_age -= 1

    this_year_birthday = birthday.replace(today.year)
    remain = this_year_birthday.toordinal() - today.toordinal()
    if remain < 1:
        next_year_birthday = birthday.replace(today.year + 1)
        remain = next_year_birthday.toordinal() - today.toordinal()

    await bot.say(
        event.channel,
        ('{} 출생자는 {} 기준으로 다음과 같아요!\n\n'
         '* 세는 나이(한국식 나이) {}세\n'
         '* 연 나이(한국 일부 법령상 나이) {}세\n'
         '* 만 나이(전세계 표준) {}세\n\n'
         '출생일로부터 {:,}일 지났어요.'
         ' 다음 생일까지 {}일 남았어요.').format(
            birthday.strftime('%Y년 %m월 %d일'),
            today.strftime('%Y년 %m월 %d일'),
            korean_age,
            year_age,
            global_age,
            today.toordinal() - birthday.toordinal(),
            remain,
        )
    )
