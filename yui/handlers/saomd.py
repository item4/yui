import random

from ..box import box
from ..command import argument


CHARACTER_TABLE = {
    '가속': [
        '[어그멘트 테이머] 시리카',
        '[이피션트 스미스] 리즈벳',
        '[프로그레시브 거너] 시논',
        '[일어서는 영웅] 키리토',
        '[맞서는 결의] 아스나',
    ],
    '기사': [
        '[천부의 재능] 유지오',
        '[정합기사] 엘리스',
    ],
    '여름': [
        '[치유의 여름 미인] 아스나',
        '[두근거리는 여름 처녀] 스구하',
        '[장난스런 여름 소녀] 시논',
        '[태양의 여름 소녀] 리즈벳',
        '[해바라기 여름소녀] 시리카',
    ],
}

WEAPON_TABLE = {
    '가속': [
        '히로익 프로미스',
        '컬리지',
        '어드밴서',
        '엣지 오브 리펜트',
        '에레터',
    ],
    '기사': [
        '청장미의 검',
        '금목서의 검',
    ],
    '여름': [
        '릴리 망고슈',
        '아일랜드 스피어',
        '마린 샷',
        '선플라워 엣지',
        '비치 버스터',
    ],
}


@box.command('캐릭뽑기', ['캐뽑'])
@argument('category', count_error='카테고리를 입력해주세요')
async def saomd_character(bot, message, category):
    """
    소드 아트 온라인 메모리 디프래그의 캐릭터 뽑기를 시뮬레이팅합니다.

    `{PREFIX}캐뽑 가속` (가속하는 리얼 11연차를 시뮬레이션)

    카테고리: 가속(가속하는 리얼), 기사(기사들의 해후), 여름(여름빛 소녀)

    """

    try:
        table = CHARACTER_TABLE[category]
    except KeyError:
        await bot.say(
            message['channel'],
            '`{}`은 지원하지 않는 카테고리입니다. 도움말을 참조해주세요'.format(category)
        )
        return

    chars = []

    for x in range(11):
        r = random.random()
        if r <= 0.04:
            chars.append(random.choice(table))
        elif r <= 0.04 + 0.25:
            chars.append('3성')
        else:
            chars.append('2성')

    await bot.say(
        message['channel'],
        ', '.join(chars)
    )


@box.command('무기뽑기', ['무뽑'])
@argument('category', count_error='카테고리를 입력해주세요')
async def saomd_weapon(bot, message, category):
    """
    소드 아트 온라인 메모리 디프래그의 무기 뽑기를 시뮬레이팅합니다.

    `{PREFIX}무뽑 가속` (가속하는 리얼 11연차를 시뮬레이션)

    카테고리: 가속(가속하는 리얼), 기사(기사들의 해후), 여름(여름빛 소녀)

    """

    try:
        table = WEAPON_TABLE[category]
    except KeyError:
        await bot.say(
            message['channel'],
            '`{}`은 지원하지 않는 카테고리입니다. 도움말을 참조해주세요'.format(category)
        )
        return

    items = []

    for x in range(11):
        if random.random() <= 0.04:
            items.append(random.choice(table))
        else:
            items.append('꽝')

    await bot.say(
        message['channel'],
        ', '.join(items)
    )
