from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from .models import AWS
from ....box import box
from ....command import argument, option
from ....event import Message
from ....transform import choice


@box.command('날씨', ['aws', 'weather'])
@argument('keyword', nargs=-1, concat=True)
async def aws(bot, event: Message, sess: Session, keyword: str):
    """
    지역의 현재 기상상태를 조회합니다.

    `{PREFIX}날씨 부천` (부천지역의 현재 기상상태를 출력)

    """

    record = None
    try:
        record = sess.query(AWS).filter_by(name=keyword).one()
    except NoResultFound:
        await bot.say(
            event.channel,
            '검색 결과가 없어요!'
        )
        return
    except MultipleResultsFound:
        await bot.say(
            event.channel,
            '검색 결과가 여러가지 있어요! 시스템 관리자에게 문의해주세요!'
        )
        return

    rain = {
        True: '예(15min: {}/일일: {})'.format(
            record.rain15,
            record.rainday,
        ),
        False: '아니오',
        None: '모름',
    }.get(record.is_raining)

    temperature = None
    if record.temperature is not None:
        temperature = '{}℃'.format(record.temperature)

    wind = None
    if record.wind_speed1 is not None and record.wind_direction1 is not None:
        wind = '{} {}㎧'.format(
            record.wind_direction1
                  .replace('N', '북')
                  .replace('S', '남')
                  .replace('W', '서')
                  .replace('E', '동'),
            record.wind_speed1,
        )

    humidity = None
    if record.humidity is not None:
        humidity = '{}%'.format(record.humidity)

    pressure = None
    if record.pressure is not None:
        pressure = '{}hPa'.format(record.pressure)

    res = '[{}@{}/{}] 강수: {}'.format(
        record.observed_at.strftime('%Y년 %m월 %d일 %H시 %M분'),
        record.name,
        record.location,
        rain,
    )

    if temperature:
        res += ' / {}'.format(temperature)

    if wind:
        res += ' / 바람: {}'.format(wind)

    if humidity:
        res += ' / 습도: {}'.format(humidity)

    if pressure:
        res += ' / 해면기압: {}'.format(pressure)

    if record.is_raining:
        if record.temperature < 0:
            emoji = ':snowflake:'
        else:
            emoji = ':umbrella_with_rain_drops:'
    elif record.is_raining is None:
        emoji = ':thinking_face:'
    else:
        if record.observed_at.hour in [21, 22, 23, 0, 1, 2, 3, 4, 5, 6]:
            emoji = ':crescent_moon:'
        else:
            emoji = ':sunny:'

    await bot.api.chat.postMessage(
        channel=event.channel,
        text=res,
        username=f'{record.name} 날씨',
        icon_emoji=emoji,
    )


@box.command('날씨지역검색', ['search-aws-zone'])
@option('--by', transform_func=choice(['name', 'location']), default='name',
        type_error='`{name}`의 값으로는 `name` 이나 `location`만 가능합니다.')
@argument('keyword', nargs=-1, concat=True)
async def search_aws_zone(
    bot,
    event: Message,
    sess: Session,
    by: str,
    keyword: str,
):
    """
    날씨 명령어에 사용되는 지역명 검색기능

    주어진 키워드를 기준으로 비슷한 지역명을 모두 출력합니다.
    해당 명령어는 DB에 `like '%keyword%'` 연산을 사용합니다.

    `{PREFIX}날씨지역검색 부산` (이름에 `부산` 이 들어가는 모든 지역 검색)
    `{PREFIX}날씨지역검색 --by location 서울` (관측기 위치 주소에 `서울`이 들어가는 모든 지역 검색)

    """

    q = sess.query(AWS)
    if by == 'location':
        q = q.filter(AWS.location.contains(keyword))
    else:
        q = q.filter(AWS.name.contains(keyword))

    result = q.all()

    if result:
        await bot.say(
            event.channel,
            '검색 결과는 다음과 같습니다.\n\n{}'.format(
                '\n'.join('{}({})'.format(x.name, x.location) for x in result)
            ),
            thread_ts=event.ts,
        )
    else:
        await bot.say(
            event.channel,
            '검색 결과가 없어요!',
            thread_ts=event.ts,
        )
