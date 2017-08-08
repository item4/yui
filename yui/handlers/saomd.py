import random
import typing

from ..box import box
from ..command import argument


class Scout(typing.NamedTuple):
    """NamedTuple to store saomd scout."""

    name: str
    cost: int
    chance: float
    items: typing.List[str]


CHARACTER_TABLE: typing.List[Scout] = {
    '가속': Scout(
        name='가속하는 리얼',
        cost=250,
        chance=0.04,
        items=[
            '[어그멘트 테이머] 시리카',
            '[이피션트 스미스] 리즈벳',
            '[프로그레시브 거너] 시논',
            '[일어서는 영웅] 키리토',
            '[맞서는 결의] 아스나',
        ],
    ),
    '기사': Scout(
        name='기사들의 해후',
        cost=250,
        chance=0.04,
        items=[
            '[천부의 재능] 유지오',
            '[정합기사] 엘리스',
        ],
    ),
    '여름': Scout(
        name='여름빛 소녀',
        cost=250,
        chance=0.04,
        items=[
            '[치유의 여름 미인] 아스나',
            '[두근거리는 여름 처녀] 스구하',
            '[장난스런 여름 소녀] 시논',
            '[태양의 여름 소녀] 리즈벳',
            '[해바라기 여름소녀] 시리카',
        ],
    ),
    '축제': Scout(
        name='여름밤의 축제 Step 2 or 4',
        cost=250,
        chance=0.04,
        items=[
            '[장사수완 좋은 노점상] 리즈벳',
            '[여름밤에 울리는 소리] 리파',
            '[신락의 춤] 프리미어',
        ],
    ),
    '축제1': Scout(
        name='여름밤의 축제 Step 1',
        cost=200,
        chance=0.04,
        items=[
            '[장사수완 좋은 노점상] 리즈벳',
            '[여름밤에 울리는 소리] 리파',
            '[신락의 춤] 프리미어',
        ],
    ),
    '축제3': Scout(
        name='여름밤의 축제 Step 3',
        cost=200,
        chance=0.04*1.5,
        items=[
            '[장사수완 좋은 노점상] 리즈벳',
            '[여름밤에 울리는 소리] 리파',
            '[신락의 춤] 프리미어',
        ],
    ),
    '축제5': Scout(
        name='여름밤의 축제 Step 5',
        cost=250,
        chance=0.04*2,
        items=[
            '[장사수완 좋은 노점상] 리즈벳',
            '[여름밤에 울리는 소리] 리파',
            '[신락의 춤] 프리미어',
        ],
    ),
}

WEAPON_TABLE: typing.List[Scout] = {
    '가속': Scout(
        name='가속하는 리얼',
        cost=150,
        chance=0.04,
        items=[
            '히로익 프로미스',
            '컬리지',
            '어드밴서',
            '엣지 오브 리펜트',
            '에레터',
        ],
    ),
    '기사': Scout(
        name='기사들의 해후',
        cost=150,
        chance=0.04,
        items=[
            '청장미의 검',
            '금목서의 검',
        ],
    ),
    '여름': Scout(
        name='여름빛 소녀',
        cost=150,
        chance=0.04,
        items=[
            '릴리 망고슈',
            '아일랜드 스피어',
            '마린 샷',
            '선플라워 엣지',
            '비치 버스터',
        ],
    ),
    '축제': Scout(
        name='여름밤의 축제',
        cost=150,
        chance=0.04,
        items=[
            '풍차의 신검',
            '천신의 폭풍검',
            '보구의 신창',
        ],
    ),
}


@box.command('캐릭뽑기', ['캐뽑'])
@argument('category', count_error='카테고리를 입력해주세요')
async def saomd_character(bot, message, category):
    """
    소드 아트 온라인 메모리 디프래그의 캐릭터 뽑기를 시뮬레이팅합니다.

    `{PREFIX}캐뽑 가속` (가속하는 리얼 11연차를 시뮬레이션)

    카테고리: 가속(가속하는 리얼), 기사(기사들의 해후), 여름(여름빛 소녀) 축제(여름밤의 축제)

    축제의 경우 뒤에 1, 3, 5를 붙이면 해당하는 Step 기준의 시뮬이 가능합니다. (ex. `축제5`)

    """

    try:
        scout = CHARACTER_TABLE[category]
    except KeyError:
        await bot.say(
            message['channel'],
            '`{}`은 지원하지 않는 카테고리입니다. 도움말을 참조해주세요'.format(category)
        )
        return

    chars = []

    for x in range(11):
        r = random.random()
        if r <= scout.chance:
            chars.append(random.choice(scout.items))
        elif r <= scout.chance + 0.25:
            chars.append('3성')
        else:
            chars.append('2성')

    await bot.say(
        message['channel'],
        '메모리 다이아 {}개를 소모하여 {} 11연차에 시도합니다.\n결과: {}'.format(
            scout.cost,
            scout.name,
            ', '.join(chars),
        )
    )


@box.command('무기뽑기', ['무뽑'])
@argument('category', count_error='카테고리를 입력해주세요')
async def saomd_weapon(bot, message, category):
    """
    소드 아트 온라인 메모리 디프래그의 무기 뽑기를 시뮬레이팅합니다.

    `{PREFIX}무뽑 가속` (가속하는 리얼 11연차를 시뮬레이션)

    카테고리: 가속(가속하는 리얼), 기사(기사들의 해후), 여름(여름빛 소녀), 축제(여름밤의 축제)

    """

    try:
        scout = WEAPON_TABLE[category]
    except KeyError:
        await bot.say(
            message['channel'],
            '`{}`은 지원하지 않는 카테고리입니다. 도움말을 참조해주세요'.format(category)
        )
        return

    items = []

    for x in range(11):
        if random.random() <= scout.chance:
            items.append(random.choice(scout.items))
        else:
            items.append('꽝')

    await bot.say(
        message['channel'],
        '메모리 다이아 {}개를 소모하여 {} 11연차에 시도합니다.\n결과: {}'.format(
            scout.cost,
            scout.name,
            ', '.join(items),
        )
    )
