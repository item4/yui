import random

from typing import Dict, List, NamedTuple, Optional, Tuple

import aiohttp

from fuzzywuzzy import fuzz

from lxml.html import fromstring

from ..api import Attachment
from ..box import box
from ..command import DM, argument, only
from ..event import Message
from ..util import bold

DIAMOND = '메모리 다이아'

FOUR_STAR_CHARACTERS: List[str] = [
    '[일어서는 영웅] 키리토',
    '[맞서는 결의] 아스나',
    '[어그멘트 테이머] 시리카',
    '[이피션트 스미스] 리즈벳',
    '[프로그레시브 거너] 시논',
    '[사랑의 성원] 아스나',
    '[필승 걸] 시논',
    '[터져나온 함성] 시리카',
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
    '[벚꽃 필 무렵의 소녀] 유이',
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
    '[여름 밤을 비추는 수양버들] 아스나',
    '[탄도에 피는 나팔꽃] 시논',
    '[시원한 저녁놀의 싸리꽃] 스구하',
    '[노래하는 백일홍] 세븐',
    '[춤추듯 지는 벚꽃] 레인',
    '[저편의 검객] 스구하',
    '[소생하는 검극] 키리토',
    '[마음의 섬광] 아스나',
    '[그 날의 약속] 아스나',
    '[유월의 금목서] 엘리스',
    '[맹세의 입맞춤] 리파',
    '[하이힐의 신부] 시논',
    '[부케 토스 점프] 유우키',
    '[축복의 숨결] 시리카',
    '[천승의 무희] 유우키',
    '[재회의 약속] 필리아',
    '[별 그림자의 기도] 시리카',
]


class Scout(NamedTuple):
    """NamedTuple to store saomd scout."""

    name: str
    cost: int
    cost_type: str
    result_length: int
    fixed_5star: int
    fixed_4star: int
    chance_5star: float
    chance_4star: float
    items_5star: List[str]
    items_4star: List[str]
    record_crystal: Optional[List[Tuple[int, float]]]


class Weapon(NamedTuple):
    """NamedTuple to store saomd weapon"""

    name: str
    grade: str
    ratio: int
    category: str
    attribute: str
    attack: int
    critical: int
    battle_skills: Optional[List[str]]


CHARACTER_TABLE: Dict[str, Scout] = {
    '1주년': Scout(
        name='신뢰의 증거 운명의 인연 스카우트 Step 2/4',
        cost=250,
        cost_type=DIAMOND,
        result_length=11,
        fixed_5star=0,
        fixed_4star=0,
        chance_5star=0.02,
        chance_4star=0.04,
        items_5star=[
            '[시스템을 뛰어넘는 의지] 키리토',
            '[운명을 바꾸는 의사] 아스나',
            '[마음과 마주하는 검사] 리파',
            '[과거를 극복하는 사수] 시논',
        ],
        items_4star=FOUR_STAR_CHARACTERS,
        record_crystal=None,
    ),
    '1주년1': Scout(
        name='신뢰의 증거 운명의 인연 스카우트 Step 1',
        cost=200,
        cost_type=DIAMOND,
        result_length=11,
        fixed_5star=0,
        fixed_4star=0,
        chance_5star=0.02,
        chance_4star=0.04,
        items_5star=[
            '[시스템을 뛰어넘는 의지] 키리토',
            '[운명을 바꾸는 의사] 아스나',
            '[마음과 마주하는 검사] 리파',
            '[과거를 극복하는 사수] 시논',
        ],
        items_4star=FOUR_STAR_CHARACTERS,
        record_crystal=None,
    ),
    '1주년3': Scout(
        name='신뢰의 증거 운명의 인연 스카우트 Step 3',
        cost=200,
        cost_type=DIAMOND,
        result_length=11,
        fixed_5star=0,
        fixed_4star=0,
        chance_5star=0.02*1.5,
        chance_4star=0.04,
        items_5star=[
            '[시스템을 뛰어넘는 의지] 키리토',
            '[운명을 바꾸는 의사] 아스나',
            '[마음과 마주하는 검사] 리파',
            '[과거를 극복하는 사수] 시논',
        ],
        items_4star=FOUR_STAR_CHARACTERS,
        record_crystal=None,
    ),
    '1주년5': Scout(
        name='신뢰의 증거 운명의 인연 스카우트 Step 5',
        cost=250,
        cost_type=DIAMOND,
        result_length=11,
        fixed_5star=1,
        fixed_4star=0,
        chance_5star=0.02,
        chance_4star=0.04,
        items_5star=[
            '[시스템을 뛰어넘는 의지] 키리토',
            '[운명을 바꾸는 의사] 아스나',
            '[마음과 마주하는 검사] 리파',
            '[과거를 극복하는 사수] 시논',
        ],
        items_4star=FOUR_STAR_CHARACTERS,
        record_crystal=None,
    ),
    '1주년6': Scout(
        name='신뢰의 증거 운명의 인연 스카우트 Step 6',
        cost=250,
        cost_type=DIAMOND,
        result_length=11,
        fixed_5star=0,
        fixed_4star=0,
        chance_5star=0.02*2,
        chance_4star=0.04,
        items_5star=[
            '[시스템을 뛰어넘는 의지] 키리토',
            '[운명을 바꾸는 의사] 아스나',
            '[마음과 마주하는 검사] 리파',
            '[과거를 극복하는 사수] 시논',
        ],
        items_4star=FOUR_STAR_CHARACTERS,
        record_crystal=None,
    ),
    '돌검': Scout(
        name='돌아가는 세계에 겁쳐진 검 스카우트 Step 2/4',
        cost=250,
        cost_type=DIAMOND,
        result_length=11,
        fixed_5star=0,
        fixed_4star=0,
        chance_5star=0.02,
        chance_4star=0.04,
        items_5star=[
            '[청장미의 정합기사] 유지오',
            '[금목서의 정합기사] 엘리스',
        ],
        items_4star=FOUR_STAR_CHARACTERS,
        record_crystal=None,
    ),
    '돌검1': Scout(
        name='돌아가는 세계에 겁쳐진 검 스카우트 Step 1',
        cost=200,
        cost_type=DIAMOND,
        result_length=11,
        fixed_5star=0,
        fixed_4star=0,
        chance_5star=0.02,
        chance_4star=0.04,
        items_5star=[
            '[청장미의 정합기사] 유지오',
            '[금목서의 정합기사] 엘리스',
        ],
        items_4star=FOUR_STAR_CHARACTERS,
        record_crystal=None,
    ),
    '돌검3': Scout(
        name='돌아가는 세계에 겁쳐진 검 스카우트 Step 3',
        cost=200,
        cost_type=DIAMOND,
        result_length=11,
        fixed_5star=0,
        fixed_4star=0,
        chance_5star=0.02*1.5,
        chance_4star=0.04,
        items_5star=[
            '[청장미의 정합기사] 유지오',
            '[금목서의 정합기사] 엘리스',
        ],
        items_4star=FOUR_STAR_CHARACTERS,
        record_crystal=None,
    ),
    '돌검5': Scout(
        name='돌아가는 세계에 겁쳐진 검 스카우트 Step 5',
        cost=250,
        cost_type=DIAMOND,
        result_length=11,
        fixed_5star=1,
        fixed_4star=0,
        chance_5star=0.02,
        chance_4star=0.04,
        items_5star=[
            '[청장미의 정합기사] 유지오',
            '[금목서의 정합기사] 엘리스',
        ],
        items_4star=FOUR_STAR_CHARACTERS,
        record_crystal=None,
    ),
    '돌검6': Scout(
        name='돌아가는 세계에 겁쳐진 검 스카우트 Step 6',
        cost=250,
        cost_type=DIAMOND,
        result_length=11,
        fixed_5star=0,
        fixed_4star=0,
        chance_5star=0.02*2,
        chance_4star=0.04,
        items_5star=[
            '[청장미의 정합기사] 유지오',
            '[금목서의 정합기사] 엘리스',
        ],
        items_4star=FOUR_STAR_CHARACTERS,
        record_crystal=None,
    ),
    '지나': Scout(
        name='지나가는 시간과 우정의 기억 스카우트 Step 2/4',
        cost=250,
        cost_type=DIAMOND,
        result_length=11,
        fixed_5star=0,
        fixed_4star=0,
        chance_5star=0.02,
        chance_4star=0.04,
        items_5star=[
            '[마음을 잇는 물요정] 아스나',
            '[희망을 이루는 검호] 유우키',
            '[순수한 미소의 수호자] 시리카',
            '[조화를 지키는 자] 리즈벳',
        ],
        items_4star=FOUR_STAR_CHARACTERS,
        record_crystal=None,
    ),
    '지나1': Scout(
        name='지나가는 시간과 우정의 기억 스카우트 Step 1',
        cost=200,
        cost_type=DIAMOND,
        result_length=11,
        fixed_5star=0,
        fixed_4star=0,
        chance_5star=0.02,
        chance_4star=0.04,
        items_5star=[
            '[마음을 잇는 물요정] 아스나',
            '[희망을 이루는 검호] 유우키',
            '[순수한 미소의 수호자] 시리카',
            '[조화를 지키는 자] 리즈벳',
        ],
        items_4star=FOUR_STAR_CHARACTERS,
        record_crystal=None,
    ),
    '지나3': Scout(
        name='지나가는 시간과 우정의 기억 스카우트 Step 3',
        cost=200,
        cost_type=DIAMOND,
        result_length=11,
        fixed_5star=0,
        fixed_4star=0,
        chance_5star=0.02*1.5,
        chance_4star=0.04,
        items_5star=[
            '[마음을 잇는 물요정] 아스나',
            '[희망을 이루는 검호] 유우키',
            '[순수한 미소의 수호자] 시리카',
            '[조화를 지키는 자] 리즈벳',
        ],
        items_4star=FOUR_STAR_CHARACTERS,
        record_crystal=None,
    ),
    '지나5': Scout(
        name='지나가는 시간과 우정의 기억 스카우트 Step 5',
        cost=250,
        cost_type=DIAMOND,
        result_length=11,
        fixed_5star=1,
        fixed_4star=0,
        chance_5star=0.02,
        chance_4star=0.04,
        items_5star=[
            '[마음을 잇는 물요정] 아스나',
            '[희망을 이루는 검호] 유우키',
            '[순수한 미소의 수호자] 시리카',
            '[조화를 지키는 자] 리즈벳',
        ],
        items_4star=FOUR_STAR_CHARACTERS,
        record_crystal=None,
    ),
    '지나6': Scout(
        name='지나가는 시간과 우정의 기억 스카우트 Step 6',
        cost=250,
        cost_type=DIAMOND,
        result_length=11,
        fixed_5star=0,
        fixed_4star=0,
        chance_5star=0.02*2,
        chance_4star=0.04,
        items_5star=[
            '[마음을 잇는 물요정] 아스나',
            '[희망을 이루는 검호] 유우키',
            '[순수한 미소의 수호자] 시리카',
            '[조화를 지키는 자] 리즈벳',
        ],
        items_4star=FOUR_STAR_CHARACTERS,
        record_crystal=None,
    ),
}

WEAPON_TABLE: Dict[str, Scout] = {
    '1주년': Scout(
        name='신뢰의 증거 운명의 인연 스카우트',
        cost=150,
        cost_type=DIAMOND,
        result_length=11,
        fixed_5star=0,
        fixed_4star=0,
        chance_5star=0.0,
        chance_4star=0.04,
        items_5star=[],
        items_4star=[
            '인라이트먼트 x 섀도우 엘리미네이터',
            '다즐링 블링크',
            '이레디케이트 세이버',
            '구시스나우탈',
        ],
        record_crystal=None,
    ),
    '돌검': Scout(
        name='돌아가는 세계에 겁쳐진 검 스카우트',
        cost=150,
        cost_type=DIAMOND,
        result_length=11,
        fixed_5star=0,
        fixed_4star=0,
        chance_5star=0.0,
        chance_4star=0.04,
        items_5star=[],
        items_4star=[
            '영겁불후의 검',
            '영구빙괴의 검',
        ],
        record_crystal=None,
    ),
    '지나': Scout(
        name='지나가는 시간과 우정의 기억 스카우트',
        cost=150,
        cost_type=DIAMOND,
        result_length=11,
        fixed_5star=0,
        fixed_4star=0,
        chance_5star=0.0,
        chance_4star=0.04,
        items_5star=[],
        items_4star=[
            '아틀탄티스 소드',
            '철운석의 검',
            '카른웨난',
            '플라네타리 메이스',
        ],
        record_crystal=None,
    ),
}


@box.command('캐릭뽑기', ['캐뽑'], channels=only(
    'game', 'test', DM, error='게임/테스트 채널에서만 해주세요'
))
@argument('category', count_error='카테고리를 입력해주세요')
async def saomd_character(bot, event: Message, category: str):
    """
    소드 아트 온라인 메모리 디프래그의 캐릭터 뽑기를 시뮬레이팅합니다.

    `{PREFIX}캐뽑 1주년` (신뢰의 증거 운명의 인연 스카우트 11연차를 시뮬레이션)

    카테고리는 다음과 같습니다.

    * `1주년`: 신뢰의 증거 운명의 인연 스카우트 (`1주년1`/`1주년3`/`1주년5`/`1주년6`)
    * `돌검`: 돌아가는 세계에 겁쳐진 검 스카우트 (`돌검1`/`돌검3`/`돌검5`/`돌검6`)
    * `지나`: 지나가는 시간과 우정의 기억 스카우트 (`지나1`/`지나3`/`지나5`/`지나6`)

    """

    try:
        scout = CHARACTER_TABLE[category]
    except KeyError:
        await bot.say(
            event.channel,
            '`{}`은 지원하지 않는 카테고리입니다. 도움말을 참조해주세요'.format(category)
        )
        return

    chars: List[Tuple[int, str]] = []

    five = scout.chance_5star
    four = five + scout.chance_4star
    three = four + 0.25

    result_length = scout.result_length
    for x in range(scout.fixed_5star):
        chars.append((5, bold(random.choice(scout.items_5star))))
        result_length -= 1
    for x in range(scout.fixed_4star):
        chars.append((4, bold(random.choice(scout.items_4star))))
        result_length -= 1
    for x in range(result_length):
        r = random.random()
        if r <= five:
            chars.append((5, bold(random.choice(scout.items_5star))))
        elif r <= four:
            chars.append((4, bold(random.choice(scout.items_4star))))
        elif r <= three:
            chars.append((3, '3성'))
        else:
            chars.append((2, '2성'))

    chars.sort(key=lambda x: -x[0])

    record_crystal = 0

    if scout.record_crystal:
        cases: List[int] = []
        chances: List[float] = []
        for case, chance in scout.record_crystal:
            cases.append(case)
            chances.append(chance)
        record_crystal = random.choices(cases, chances)[0]

    await bot.say(
        event.channel,
        '{} {}개를 소모하여 {} {}{}차를 시도합니다.\n결과: {}{}'.format(
            scout.cost_type,
            scout.cost,
            scout.name,
            scout.result_length,
            '연' if scout.result_length > 1 else '단',
            ', '.join(c[1] for c in chars),
            '\n기록결정 크리스탈을 {}개 획득하셨습니다.'.format(record_crystal)
            if record_crystal > 0 else ''
        )
    )


@box.command('무기뽑기', ['무뽑'], channels=only(
    'game', 'test', DM, error='게임/테스트 채널에서만 해주세요'
))
@argument('category', count_error='카테고리를 입력해주세요')
async def saomd_weapon(bot, event: Message, category: str):
    """
    소드 아트 온라인 메모리 디프래그의 무기 뽑기를 시뮬레이팅합니다.

    `{PREFIX}무뽑 1주년` (신뢰의 증거 운명의 인연 스카우트 11연차를 시뮬레이션)

    카테고리는 다음과 같습니다.

    * `1주년`: 신뢰의 증거 운명의 인연 스카우트
    * `돌검`: 돌아가는 세계에 겁쳐진 검 스카우트
    * `지나`: 지나가는 시간과 우정의 기억 스카우트

    """

    try:
        scout = WEAPON_TABLE[category]
    except KeyError:
        await bot.say(
            event.channel,
            '`{}`은 지원하지 않는 카테고리입니다. 도움말을 참조해주세요'.format(category)
        )
        return

    items = []

    five = scout.chance_5star
    four = five + scout.chance_4star
    three = four + 0.25
    result_length = scout.result_length
    for x in range(scout.fixed_5star):
        items.append(bold(random.choice(scout.items_5star)))
        result_length -= 1
    for x in range(scout.fixed_4star):
        items.append(bold(random.choice(scout.items_4star)))
        result_length -= 1
    for x in range(result_length):
        r = random.random()
        if r <= five:
            items.append(bold(random.choice(scout.items_5star)))
        elif r <= four:
            items.append(bold(random.choice(scout.items_4star)))
        elif r <= three:
            items.append('3성')
        else:
            items.append('2성')

    record_crystal = 0

    if scout.record_crystal:
        cases: List[int] = []
        chances: List[float] = []
        for case, chance in scout.record_crystal:
            cases.append(case)
            chances.append(chance)
        record_crystal = random.choices(cases, chances)[0]

    await bot.say(
        event.channel,
        '{} {}개를 소모하여 {} {}{}차를 시도합니다.\n결과: {}{}'.format(
            scout.cost_type,
            scout.cost,
            scout.name,
            scout.result_length,
            '연' if scout.result_length > 1 else '단',
            ', '.join(items),
            '\n기록결정 크리스탈을 {}개 획득하셨습니다.'.format(record_crystal)
            if record_crystal > 0 else ''
        )
    )


@box.command('캐릭정보', ['캐정'])
@argument('keyword', nargs=-1, concat=True)
async def character_info(bot, event: Message, keyword: str):
    """
    소드 아트 온라인 메모리 디프래그 DB에서 캐릭터 정보를 조회합니다.

    `{PREFIX}캐정 남국소년` (이름에 `남국소년`이 들어가는 가장 유사한 캐릭터 정보 조회)

    DB출처: 헝그리

    이 명령어는 `캐릭정보`, `캐정` 중 편한 이름으로 사용할 수 있습니다.

    """

    html = ''
    url = 'http://www.hungryapp.co.kr/bbs/game/_game_saomd_char.php'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            html = await res.text()

    h = fromstring(html)
    tr_list = h.cssselect('div table tr')[1:]

    matching: List[Tuple[float, str, str]] = []
    for tr in tr_list:
        name = tr[1].text_content().replace('★', '').strip()
        matching.append((
            fuzz.ratio(keyword, name),
            name,
            tr[1][0].get('href'),
        ))

    matching.sort(key=lambda x: -x[0])

    if matching[0][0] >= 40:
        html = ''
        url = f'http://www.hungryapp.co.kr{matching[0][2]}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                html = await res.text()

        h = fromstring(html)

        image = h.cssselect('.skill_detail b img')[0].get('src')
        name = h.cssselect('.DB_view_title span')[0].text_content()

        tables = h.cssselect('.card_info_view table')

        grade = tables[0][1][1].text_content()
        weapon = tables[0][1][3].text_content()
        attribute = tables[0][1][5].text_content()

        scout_from = tables[0][2][1].text_content()

        hp = int(tables[1][2][0].text_content())
        mp = int(tables[1][2][1].text_content())
        attack = int(tables[1][2][2].text_content())
        defence = int(tables[1][2][3].text_content())
        critical = int(tables[1][2][4].text_content())

        score = float(tables[2][2][1].text_content())

        attachment = Attachment(
            fallback=f'{name} - {url}',
            title=name,
            title_link=url,
            text=(
                f'{grade} / {weapon} / {attribute}속성 / {score}점\n'
                f'{scout_from}에서 획득 가능\n'
                f'HP {hp:,} / MP {mp:,} / '
                f'ATK {attack:,} / DEF {defence:,} / CRI {critical:,}'
            ),
            image_url=image,
        )

        await bot.api.chat.postMessage(
            channel=event.channel,
            attachments=[attachment],
            as_user=True,
        )
    else:
        await bot.say(
            event.channel,
            '주어진 키워드로 검색해서 일치하는 것을 찾을 수 없어요!\n'
            '혹시 {} 중에 하나 아닌가요?'.format(
                ', '.join(x[1] for x in matching[:3])
            )
        )


@box.command('무기정보', ['무정'])
@argument('keyword', nargs=-1, concat=True)
async def weapon_info(bot, event: Message, keyword: str):
    """
    소드 아트 온라인 메모리 디프래그 DB에서 무기 정보를 조회합니다.

    `{PREFIX}캐정 히로익` (이름에 `히로익`이 들어가는 가장 유사한 무기 정보 조회)

    DB출처: 헝그리앱

    이 명령어는 `무기정보`, `무정` 중 편한 이름으로 사용할 수 있습니다.

    """

    html = ''
    url = 'http://www.hungryapp.co.kr/bbs/game/_game_saomd_weap.php'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            html = await res.text()

    h = fromstring(html)
    tr_list = h.cssselect('div table tr')[1:]

    weapons: List[Weapon] = []

    for tr in tr_list:
        name = tr[0][0].text_content()
        grade = tr[0].text_content().replace(name, '').strip()
        ratio = fuzz.ratio(name, keyword)
        category = tr[1].text_content()
        attribute = tr[2].text_content()
        attack = int(tr[3].text_content())
        critical = int(tr[4].text_content())
        battle_skills = [x.strip() for x in tr[5].text_content().split('/')]

        weapons.append(Weapon(
            name=name,
            grade=grade,
            ratio=ratio,
            category=category,
            attribute=attribute,
            attack=attack,
            critical=critical,
            battle_skills=battle_skills,
        ))

    weapons.sort(key=lambda x: -x.ratio)

    if weapons[0].ratio >= 40:
        weapon = weapons[0]
        attachment = Attachment(
            fallback='{} {} - {} / {}속성 / ATK {:,} / CRI {:,} / {}'.format(
                weapon.grade,
                weapon.name,
                weapon.category,
                weapon.attribute,
                weapon.attack,
                weapon.critical,
                ' | '.join(weapon.battle_skills),
            ),
            title=weapon.name,
            text='{} / {} / {}속성 / ATK {:,} / CRI {:,}\n{}'.format(
                weapon.grade,
                weapon.category,
                weapon.attribute,
                weapon.attack,
                weapon.critical,
                ' | '.join(weapon.battle_skills),
            )
        )
        await bot.api.chat.postMessage(
            channel=event.channel,
            attachments=[attachment],
            as_user=True,
        )
    else:
        await bot.say(
            event.channel,
            '주어진 키워드로 검색해서 일치하는 것을 찾을 수 없어요!\n'
            '혹시 {} 중에 하나 아닌가요?'.format(
                ', '.join(x.name for x in weapons[:3])
            )
        )
