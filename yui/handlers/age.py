import datetime
import re

from typing import Optional

from ..box import box
from ..command import argument, option
from ..event import Message


FORMAT_RE = re.compile(
    '(\d{4})\s*[-\.년]?\s*(\d{1,2})\s*[-\.월]?\s*(\d{1,2})\s*일?'
)


@box.command('나이', ['age'])
@option('--at')
@argument('birthday_string', nargs=-1, concat=True,
          count_error='생일을 입력해주세요')
async def age(bot, event: Message, at: Optional[str], birthday_string: str):
    """
    나이 계산

    주어진 날짜를 기준으로 나이 및 생일 정보를 출력합니다.

    `{PREFIX}나이 2003년 6월 3일` (오늘을 기준으로 2003년 6월 3일생의 나이/생일 정보를 계산)
    `{PREFIX}나이 --at="2010년 1월 1일" 2003년 6월 3일 (2010년 1월 1일을 기준으로 계산)

    날짜는 `2003-06-03`/`20030603`/`2003.06.03`/`2003년06월03일` 형식을 지원합니다.
    (띄어쓰기 허용)

    """

    today = datetime.date.today()
    birthday = None
    if at:
        at_match = FORMAT_RE.match(at)
        if at_match:
            try:
                today = datetime.date(
                    int(at_match.group(1)),
                    int(at_match.group(2)),
                    int(at_match.group(3)),
                )
            except ValueError:
                pass
    birthday_match = FORMAT_RE.match(birthday_string)
    if birthday_match:
        try:
            birthday = datetime.date(
                int(birthday_match.group(1)),
                int(birthday_match.group(2)),
                int(birthday_match.group(3)),
            )
        except ValueError:
            await bot.say(
                event.channel,
                '정상적인 날짜가 아니에요!'
            )
            return
    else:
        await bot.say(
            event.channel,
            '인식할 수 는 날짜가 아니에요!'
        )
        return

    if today < birthday:
        await bot.say(
            event.channel,
            '기준일 기준으로 아직 태어나지 않았어요!'
        )
        return

    korean_age = today.year - birthday.year + 1

    western_age = today.year - birthday.year
    cond1 = today.month < birthday.month
    cond2 = today.month == birthday.month and today.day < birthday.day
    if cond1 or cond2:
        western_age -= 1

    this_year_birthday = birthday.replace(today.year)
    remain = this_year_birthday.toordinal() - today.toordinal()
    if remain < 1:
        next_year_birthday = birthday.replace(today.year + 1)
        remain = next_year_birthday.toordinal() - today.toordinal()

    await bot.say(
        event.channel,
        ('{} 출생자는 {} 기준으로 {}세 (만 {}세)에요!'
         ' 출생일로부터 {:,}일 지났어요.'
         ' 다음 생일까지 {}일 남았어요.').format(
            birthday.strftime('%Y년 %m월 %d일'),
            today.strftime('%Y년 %m월 %d일'),
            korean_age,
            western_age,
            today.toordinal() - birthday.toordinal(),
            remain,
        )
    )
