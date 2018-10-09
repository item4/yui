import re

import aiohttp

import tossi

from .util import get_event_days, get_holiday_name
from ...box import box
from ...command import C
from ...event import Message
from ...transform import DATE_FORMAT_RE
from ...util import now

box.assert_config_required('TDCPROJECT_KEY', str)
box.assert_config_required('MONDAY_DOG_LIMIT', int)
box.assert_channel_required('general')

YEAR_PATTERN = re.compile(r'^(\d{4})년$')
YEAR_MONTH_PATTERN = re.compile(r'^(\d{4})년\s*(\d{1,2})월$')


@box.crontab('0 0 * * 0,2,3,4,5,6')
async def holiday_message(bot):
    holiday = None
    today = now()
    try:
        holiday = await get_holiday_name(bot.config.TDCPROJECT_KEY, today)
    except aiohttp.client_exceptions.ClientOSError:
        pass

    if holiday:
        await bot.say(
            C.general.get(),
            '오늘은 {}! 즐거운 휴일 되세요!'.format(
                tossi.postfix(holiday, '(이)에요'),
            )
        )


@box.command('day')
async def day(bot, event: Message, raw: str):
    params = {
        'api_key': bot.config.TDCPROJECT_KEY,
    }

    if raw:
        while True:
            match = YEAR_PATTERN.match(raw)
            if match:
                params['year'] = match.group(1)
                break

            match = YEAR_MONTH_PATTERN.match(raw)
            if match:
                params['year'] = match.group(1)
                params['month'] = match.group(2).zfill(2)
                break

            match = DATE_FORMAT_RE.match(raw)
            if match:
                params['year'] = match.group(1)
                params['month'] = match.group(2).zfill(2)
                params['day'] = match.group(3).zfill(2)
                break

            await bot.say(
                event.channel,
                '인식할 수 없는 날짜 표현식이에요!'
            )
            return
    else:
        year, month, day = now().strftime('%Y/%m/%d').split('/')
        params['year'] = year
        params['month'] = month
        params['day'] = day

    data = await get_event_days(**params)

    if data['results']:
        result = []
        for record in data['results']:
            type = record['type']\
                .replace(',', ', ')\
                .replace('h', '국정공휴일')\
                .replace('e', '이벤트')\
                .replace('s', '절기')\
                .replace('t', '명절')\
                .replace('k', '국경일')\
                .replace('p', '대중문화')\
                .replace('i', '대체공휴일')\
                .replace('a', '기념일')
            result.append(
                f"- {record['year']}-{record['month']}-{record['day']}:"
                f" {record['name']} ({type})"
            )

        await bot.say(
            event.channel,
            '\n'.join(result),
            thread_ts=event.ts,
        )
    else:
        await bot.say(
            event.channel,
            f"{params['year']}년 {params['month']}월 {params['day']}일은"
            " 아무일도 없는 평일이에요!"
        )
