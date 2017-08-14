import random

from typing import List, NamedTuple, Optional, Tuple

from ..box import box
from ..command import DM, argument, only

DIAMOND = '메모리 다이아'


class Scout(NamedTuple):
    """NamedTuple to store saomd scout."""

    name: str
    cost: int
    cost_type: str
    count: int
    chance: float
    items: List[str]
    record_crystal: Optional[List[Tuple[int, float]]]


CHARACTER_TABLE: List[Scout] = {
    '가속': Scout(
        name='가속하는 리얼',
        cost=250,
        cost_type=DIAMOND,
        count=11,
        chance=0.04,
        items=[
            '[어그멘트 테이머] 시리카',
            '[이피션트 스미스] 리즈벳',
            '[프로그레시브 거너] 시논',
            '[일어서는 영웅] 키리토',
            '[맞서는 결의] 아스나',
        ],
        record_crystal=None,
    ),
    '기사': Scout(
        name='기사들의 해후',
        cost=250,
        cost_type=DIAMOND,
        count=11,
        chance=0.04,
        items=[
            '[천부의 재능] 유지오',
            '[정합기사] 엘리스',
        ],
        record_crystal=None,
    ),
    '여름': Scout(
        name='매력 분출★여름빛 소녀',
        cost=250,
        cost_type=DIAMOND,
        count=11,
        chance=0.04,
        items=[
            '[치유의 여름 미인] 아스나',
            '[두근거리는 여름 처녀] 스구하',
            '[장난스런 여름 소녀] 시논',
            '[태양의 여름 소녀] 리즈벳',
            '[해바라기 여름소녀] 시리카',
        ],
        record_crystal=[
            (1, 3.0),
            (2, 37.0),
            (3, 40.0),
            (4, 10.0),
            (5, 3.5),
            (6, 3.5),
            (7, 1.0),
            (8, 1.0),
            (9, 0.5),
            (10, 0.5),
        ],
    ),
    '축제': Scout(
        name='여름밤의 축제 Step 2 or 4',
        cost=250,
        cost_type=DIAMOND,
        count=11,
        chance=0.04,
        items=[
            '[장사수완 좋은 노점상] 리즈벳',
            '[여름밤에 울리는 소리] 리파',
            '[신락의 춤] 프리미어',
        ],
        record_crystal=None,
    ),
    '축제1': Scout(
        name='여름밤의 축제 Step 1',
        cost=200,
        cost_type=DIAMOND,
        count=11,
        chance=0.04,
        items=[
            '[장사수완 좋은 노점상] 리즈벳',
            '[여름밤에 울리는 소리] 리파',
            '[신락의 춤] 프리미어',
        ],
        record_crystal=None,
    ),
    '축제3': Scout(
        name='여름밤의 축제 Step 3',
        cost=200,
        cost_type=DIAMOND,
        count=11,
        chance=0.04*1.5,
        items=[
            '[장사수완 좋은 노점상] 리즈벳',
            '[여름밤에 울리는 소리] 리파',
            '[신락의 춤] 프리미어',
        ],
        record_crystal=None,
    ),
    '축제5': Scout(
        name='여름밤의 축제 Step 5',
        cost=250,
        cost_type=DIAMOND,
        count=11,
        chance=0.04*2,
        items=[
            '[장사수완 좋은 노점상] 리즈벳',
            '[여름밤에 울리는 소리] 리파',
            '[신락의 춤] 프리미어',
        ],
        record_crystal=None,
    ),
    '여름기록결정': Scout(
        name='매력 분출★여름빛 소녀 기록결정 스카우트',
        cost=10,
        cost_type='매력 분출★여름빛 소녀 기록결정',
        count=1,
        chance=1,
        items=[
            '[치유의 여름 미인] 아스나',
            '[해바라기 여름소녀] 시리카',
            '[태양의 여름 소녀] 리즈벳',
            '[장난스런 여름 소녀] 시논',
            '[두근거리는 여름 처녀] 스구하',
            '[일어서는 영웅] 키리토',
            '[맞서는 결의] 아스나',
            '[어그멘트 테이머] 시리카',
            '[이피션트 스미스] 리즈벳',
            '[프로그레시브 거너] 시논',
            '[사랑의 성원] 아스나',
            '[필승 걸] 시논',
            '[터져나온 환성] 시리카',
            '[반짝이는 청춘] 스트레아',
            '[천사의 성원] 유이',
            '[천부의 재능] 유지오',
            '[정합기사] 엘리스',
            '[참영비검] 아스나',
            '[허공질주] 리파',
            '[절영비상] 유우키',
            '[용술인법] 시리카',
            '[어둠속의 검무] 리즈벳',
            '[사랑과 노력의 히트 아이돌] 아스나',
            '[반짝이는 그라비아 아이돌] 리파',
            '[변화무쌍한 아티스트] 시논',
            '[천성의 팝스타] 유우키',
            '[미소녀 차일드] 시리카',
            '[매혹의 MC퍼포머] 리즈벳',
            '[벚꽃빛 소녀] 스트레아',
            '[흔들리는 청춘] 필리아',
            '[빚꽃 필 무렵의 소녀] 유이',
            '[섬광의 무도] 아스나',
            '[진주의 눈물] 유이',
            '[인어의 마음] 리파',
            '[작은 연인] 시리카',
            '[위험한 키스] 시논',
            '[파격의 빨간망토] 유우키',
            '[청은의 기사] 유지오',
            '[황금의 기사] 엘리스',
            '[순애의 메이드] 아스나',
            '[순심의 다과 담당 메이드] 시논',
            '[트위니 메이드] 유우키',
            '[달콤한 낙농 메이드] 리파',
            '[숙련된 손님맞이 메이드] 레인',
            '[박식한 접시닦이 메이드] 세븐',
            '[초여름을 장식하는 처녀] 스구하',
            '[수면에 비친 미소] 리즈벳',
            '[맑은 헌터의 혼] 필리아',
            '[천상의 심판 리브라] 아스나',
            '[고고히 포효하는 레오] 시논',
            '[인연의 제미니] 유우키',
            '[깊은 자비의 아리에스] 리파',
            '[떨어지는 빗방울의 처녀] 레인',
            '[장마철의 즐거움] 리파',
            '[지붕 아래의 즐거움] 사쿠야',
            '[주사 시간입니다] 아스나',
            '[신참 경찰] 시논',
            '[어텐션 플리즈] 시리카',
            '[스파르타 여교사] 스트레아',
            '[출발합니다!!] 유이',
            '[롤러 웨이트리스] 유나',
            '[해변의 남국소년] 키리토',
            '[여름의 연인] 아스나',
            '[생기발랄 여름빛 소녀] 유우키',
            '[파도 타는 소년] 유지오',
            '[볼 빨간 여름의 프린세스] 엘리스',
        ],
        record_crystal=None,
    ),
    '해적': Scout(
        name='폭풍에 휘날리는 해적기',
        cost=250,
        cost_type=DIAMOND,
        count=11,
        chance=0.04,
        items=[
            '[긍지 높은 선장] 키리토',
            '[갑판을 채색하는 부선장] 아스나',
            '[감시대의 명저격수] 시논',
            '[쾌활한 항해사] 리파',
            '[직감의 조타수] 유우키',
        ],
        record_crystal=[
            (1, 3.0),
            (2, 37.0),
            (3, 40.0),
            (4, 10.0),
            (5, 3.5),
            (6, 3.5),
            (7, 1.0),
            (8, 1.0),
            (9, 0.5),
            (10, 0.5),
        ],
    ),
    '해적기록결정': Scout(
        name='폭풍에 휘날리는 해적기 기록결정 스카우트',
        cost=10,
        cost_type='폭풍에 휘날리는 해적기 기록결정',
        count=1,
        chance=1,
        items=[
            '[긍지 높은 선장] 키리토',
            '[갑판을 채색하는 부선장] 아스나',
            '[감시대의 명저격수] 시논',
            '[쾌활한 항해사] 리파',
            '[직감의 조타수] 유우키',
            '[일어서는 영웅] 키리토',
            '[맞서는 결의] 아스나',
            '[어그멘트 테이머] 시리카',
            '[이피션트 스미스] 리즈벳',
            '[프로그레시브 거너] 시논',
            '[사랑의 성원] 아스나',
            '[필승 걸] 시논',
            '[터져나온 환성] 시리카',
            '[반짝이는 청춘] 스트레아',
            '[천사의 성원] 유이',
            '[천부의 재능] 유지오',
            '[정합기사] 엘리스',
            '[참영비검] 아스나',
            '[허공질주] 리파',
            '[절영비상] 유우키',
            '[용술인법] 시리카',
            '[어둠속의 검무] 리즈벳',
            '[사랑과 노력의 히트 아이돌] 아스나',
            '[반짝이는 그라비아 아이돌] 리파',
            '[변화무쌍한 아티스트] 시논',
            '[천성의 팝스타] 유우키',
            '[미소녀 차일드] 시리카',
            '[매혹의 MC퍼포머] 리즈벳',
            '[벚꽃빛 소녀] 스트레아',
            '[흔들리는 청춘] 필리아',
            '[빚꽃 필 무렵의 소녀] 유이',
            '[섬광의 무도] 아스나',
            '[진주의 눈물] 유이',
            '[인어의 마음] 리파',
            '[작은 연인] 시리카',
            '[위험한 키스] 시논',
            '[파격의 빨간망토] 유우키',
            '[청은의 기사] 유지오',
            '[황금의 기사] 엘리스',
            '[순애의 메이드] 아스나',
            '[순심의 다과 담당 메이드] 시논',
            '[트위니 메이드] 유우키',
            '[달콤한 낙농 메이드] 리파',
            '[숙련된 손님맞이 메이드] 레인',
            '[박식한 접시닦이 메이드] 세븐',
            '[초여름을 장식하는 처녀] 스구하',
            '[수면에 비친 미소] 리즈벳',
            '[맑은 헌터의 혼] 필리아',
            '[천상의 심판 리브라] 아스나',
            '[고고히 포효하는 레오] 시논',
            '[인연의 제미니] 유우키',
            '[깊은 자비의 아리에스] 리파',
            '[떨어지는 빗방울의 처녀] 레인',
            '[장마철의 즐거움] 리파',
            '[지붕 아래의 즐거움] 사쿠야',
            '[주사 시간입니다] 아스나',
            '[신참 경찰] 시논',
            '[어텐션 플리즈] 시리카',
            '[스파르타 여교사] 스트레아',
            '[출발합니다!!] 유이',
            '[롤러 웨이트리스] 유나',
            '[해변의 남국소년] 키리토',
            '[여름의 연인] 아스나',
            '[생기발랄 여름빛 소녀] 유우키',
            '[파도 타는 소년] 유지오',
            '[볼 빨간 여름의 프린세스] 엘리스',
        ],
        record_crystal=None,
    ),
}

WEAPON_TABLE: List[Scout] = {
    '가속': Scout(
        name='가속하는 리얼',
        cost=150,
        cost_type=DIAMOND,
        count=11,
        chance=0.04,
        items=[
            '히로익 프로미스',
            '컬리지',
            '어드밴서',
            '엣지 오브 리펜트',
            '에레터',
        ],
        record_crystal=None,
    ),
    '기사': Scout(
        name='기사들의 해후',
        cost=150,
        cost_type=DIAMOND,
        count=11,
        chance=0.04,
        items=[
            '청장미의 검',
            '금목서의 검',
        ],
        record_crystal=None,
    ),
    '여름': Scout(
        name='여름빛 소녀',
        cost=150,
        cost_type=DIAMOND,
        count=11,
        chance=0.04,
        items=[
            '릴리 망고슈',
            '아일랜드 스피어',
            '마린 샷',
            '선플라워 엣지',
            '비치 버스터',
        ],
        record_crystal=None,
    ),
    '축제': Scout(
        name='여름밤의 축제',
        cost=150,
        cost_type=DIAMOND,
        count=11,
        chance=0.04,
        items=[
            '풍차의 신검',
            '천신의 폭풍검',
            '보구의 신창',
        ],
        record_crystal=None,
    ),
    '해적': Scout(
        name='폭풍에 휘날리는 해적기',
        cost=150,
        cost_type=DIAMOND,
        count=11,
        chance=0.04,
        items=[
            '오션 에스파다',
            '파이어릿 대거',
            '하버 라이플',
            '졸리 로저 사벨',
            '인쇼어 소드 x 오프쇼어 소드',
        ],
        record_crystal=None,
    ),
}


@box.command('캐릭뽑기', ['캐뽑'], channels=only(
    'game', 'test', DM, error='게임/테스트 채널에서만 해주세요'
))
@argument('category', count_error='카테고리를 입력해주세요')
async def saomd_character(bot, message, category):
    """
    소드 아트 온라인 메모리 디프래그의 캐릭터 뽑기를 시뮬레이팅합니다.

    `{PREFIX}캐뽑 가속` (가속하는 리얼 11연차를 시뮬레이션)

    카테고리는 다음과 같습니다.

    * `가속`: 가속하는 리얼 스카우트
    * `기사`: 기사들의 해후 스카우트
    * 여름: 매력 분출★여름빛 소녀 스카우트
    * `여름기록결정`: 매력 분출★여름빛 소녀 기록결정 스카우트
    * `축제`: 여름밤의 축제 스카우트 (`축제1`/`축제3`/`축제5`)
    * `해적`: 폭풍에 휘날리는 해적기
    * `해적기록결정`: 폭풍에 휘날리는 해적기 기록결정 스카우트

    """

    try:
        scout = CHARACTER_TABLE[category]
    except KeyError:
        await bot.say(
            message['channel'],
            '`{}`은 지원하지 않는 카테고리입니다. 도움말을 참조해주세요'.format(category)
        )
        return

    chars: List[Tuple[int, str]] = []

    for x in range(scout.count):
        r = random.random()
        if r <= scout.chance:
            chars.append((4, random.choice(scout.items)))
        elif r <= scout.chance + 0.25:
            chars.append((3, '3성'))
        else:
            chars.append((2, '2성'))

    chars.sort(key=lambda x: -x[0])

    record_crystal = 0

    if scout.record_crystal:
        record_crystal = random.choices(
            [x[0] for x in scout.record_crystal],
            [x[1] for x in scout.record_crystal]
        )[0]

    await bot.say(
        message['channel'],
        '{} {}개를 소모하여 {} {}{}차를 시도합니다.\n결과: {}{}'.format(
            scout.cost_type,
            scout.cost,
            scout.name,
            scout.count,
            '연' if scout.count > 1 else '단',
            ', '.join(c[1] for c in chars),
            '\n기록결정 크라스탈을 {}개 획득하셨습니다.'.format(record_crystal)
            if record_crystal > 0 else ''
        )
    )


@box.command('무기뽑기', ['무뽑'], channels=only(
    'game', 'test', DM, error='게임/테스트 채널에서만 해주세요'
))
@argument('category', count_error='카테고리를 입력해주세요')
async def saomd_weapon(bot, message, category):
    """
    소드 아트 온라인 메모리 디프래그의 무기 뽑기를 시뮬레이팅합니다.

    `{PREFIX}무뽑 가속` (가속하는 리얼 11연차를 시뮬레이션)

    카테고리는 다음과 같습니다.

    * `가속`: 가속하는 리얼 스카우트
    * `기사`: 기사들의 해후 스카우트
    * 여름: 매력 분출★여름빛 소녀 스카우트
    * `축제`: 여름밤의 축제 스카우트
    * `해적`: 폭풍에 휘날리는 해적기

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

    for x in range(scout.count):
        if random.random() <= scout.chance:
            items.append(random.choice(scout.items))
        else:
            items.append('꽝')

    record_crystal = 0

    if scout.record_crystal:
        record_crystal = random.choices(
            [x[0] for x in scout.record_crystal],
            [x[1] for x in scout.record_crystal]
        )[0]

    await bot.say(
        message['channel'],
        '{} {}개를 소모하여 {} {}{}차를 시도합니다.\n결과: {}{}'.format(
            scout.cost_type,
            scout.cost,
            scout.name,
            scout.count,
            '연' if scout.count > 1 else '단',
            ', '.join(items),
            '\n기록결정 크라스탈을 {}개 획득하셨습니다.'.format(record_crystal)
            if record_crystal > 0 else ''
        )
    )
