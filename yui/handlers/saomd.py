import copy
import random

from typing import List, NamedTuple, Optional, Tuple

import aiohttp

from lxml.html import fromstring

from sqlalchemy.orm.exc import NoResultFound

from ..api import Attachment
from ..box import box
from ..command import DM, argument, only
from ..event import Message
from ..models.saomd import (
    COST_TYPE_LABEL,
    CostType,
    Player,
    PlayerScout,
    Scout,
    ScoutType,
    Step,
)
from ..util import bold, fuzzy_korean_ratio, strike

THREE_STAR_CHARACTERS: List[str] = [
    '[검은 스프리건] 키리토',
    '[고독한 공략조] 키리토',
    '[검사] 클라인',
    '[불요정 사무라이] 클라인',
    '스메라기',
    '[혈맹 기사단 단장] 히스클리프',
    '붉은 눈의 자자',
    '크라딜',
    '유진',
    '[자유분방한 땅요정] 스트레아',
    '[컨버트 성공] 사치',
    '[공략의 화신] 아스나',
    '[싸우는 대장장이 요정] 리즈벳',
    '[아이템 마스터] 레인',
    '룩스',
    '[중간층의 아이돌] 시리카',
    '[신속한 정보상] 아르고',
    '[고양이 요정의 정보] 아르고',
    '[강인한 방어자] 에길',
    '[수수께끼의 여전사] 유우키',
    '[명장을 목표로] 리즈벳',
    '[총의 세계] 시논',
    '[고양이 궁사] 시논',
    '[날렵한 고양이 요정] 시리카',
    '[탐구하는 그림자 요정] 필리아',
    '사쿠야',
    '[바람의 마법사] 리파',
    '[어린 음악 요정] 세븐',
    '알리샤 루',
    '시우네',
]

TWO_STAR_CHARACTERS: List[str] = [
    '[전 베타 테스터] 키리토',
    '클라인',
    '디어벨',
    '코바츠',
    '싱커',
    '시구르드',
    '스트레아',
    '사치',
    '아스나',
    '요루코',
    '유리엘',
    '시리카',
    '필리아',
    '아르고',
    '사샤',
    '에길',
    '키바오',
    '카게무네',
    '리즈벳',
    '로자리아',
    '시논',
]

THREE_STAR_WEAPONS: List[str] = [
    '문릿 소드',
    '명장의 롱 소드',
    '홍염도',
    '아이스 블레이드',
    '명장의 롱 소드x2',
    '시밸릭 레이피어',
    '지룡의 스팅어',
    '브레이브 레이피어',
    '문라이트 쿠크리',
    '미세리코르데',
    '미드나이트 크리스',
    '바르바로이 메이스',
    '게일 자그널',
    '블러디 클럽',
    '화이트 슈터',
    '롱 레인지 배럿',
    '자이언트 스나이퍼',
    '시밸릭 보우',
    '페트라 보우',
    '팔콘 슈터',
    '에메랄드 로드',
    '타이들 로드',
    '결정의 마법 지팡이',
    '게일 할버드',
    '페트라 트윈스',
]

TWO_STAR_WEAPONS: List[str] = [
    '퀸즈 나이트소드',
    '브레이브 젬 소드',
    '바람이 깃든 칼',
    'Q 나이트 소드 x B 젬 소드',
    '플레임 레이피어',
    '미스릴 레이피어',
    '스트라이크  대거',
    '윈드 대거',
    '플레임 나이프',
    '워 픽',
    '아쿠아 메이스',
    '미스릴 메이스',
    '스텔스 라이플',
    '프리시전 라이플',
    '더블칼럼 매거진',
    '아쿠아 스프레드',
    '플레임 슈터',
    '다크 보우',
    '플레임 완드',
    '이블 완드',
    '에텔 스태프',
    '미스릴 스피어',
    '다크니스 글레이브',
]


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


@box.command('캐릭뽑기', ['캐뽑'], channels=only(
    'game', 'test', DM, error='게임/테스트 채널에서만 해주세요'
))
@argument('scout_title', nargs=-1, concat=True,
          count_error='스카우트 타이틀을 입력해주세요')
async def saomd_character_scout(bot, event: Message, sess, scout_title: str):
    """
    소드 아트 온라인 메모리 디프래그의 캐릭터 뽑기를 시뮬레이팅합니다.

    `{PREFIX}캐뽑 두근두근` (두근두근 수증기와 미인의 온천 스카우트 11연차를 시뮬레이션)

    지원되는 스카우트 타이틀은 `{PREFIX}캐뽑종류` 로 확인하세요.

    """

    try:
        player = sess.query(Player).filter_by(user=event.user).one()
    except NoResultFound:
        player = Player()
        player.user = event.user
        with sess.begin():
            sess.add(player)

    scouts = sess.query(Scout).filter_by(type=ScoutType.character).all()

    scout = scouts[0]
    ratio = fuzzy_korean_ratio(scout.title, scout_title)
    for s in scouts[1:]:
        _ratio = fuzzy_korean_ratio(s.title, scout_title)
        if ratio < _ratio:
            ratio = _ratio
            scout = s

    try:
        player_scout = sess.query(PlayerScout).filter(
            PlayerScout.player == player,
            PlayerScout.scout == scout,
        ).one()
    except NoResultFound:
        first = sess.query(Step).filter(
            Step.scout == scout,
            Step.is_first == True,  # noqa
        ).one()
        player_scout = PlayerScout()
        player_scout.player = player
        player_scout.scout = scout
        player_scout.next_step = first

        with sess.begin():
            sess.add(player_scout)

    step: Step = player_scout.next_step

    chars: List[Tuple[int, str]] = []

    five = step.s5_chance
    four = five + step.s4_chance
    three = four + 0.25

    result_length = step.count
    for x in range(step.s5_fixed):
        chars.append((5, random.choice(scout.s5_units)))
        result_length -= 1
    for x in range(step.s4_fixed):
        chars.append((4, random.choice(scout.s4_units)))
        result_length -= 1
    for x in range(result_length):
        r = random.random()
        if r <= five:
            chars.append((5, random.choice(scout.s5_units)))
        elif r <= four:
            chars.append((4, random.choice(scout.s4_units)))
        elif r <= three:
            chars.append((3, random.choice(THREE_STAR_CHARACTERS)))
        else:
            chars.append((2, random.choice(TWO_STAR_CHARACTERS)))

    chars.sort(key=lambda x: -x[0])

    record_crystal = 0

    if scout.record_crystal:
        cases: List[int] = []
        chances: List[float] = []
        for case, chance in scout.record_crystal:
            cases.append(case)
            chances.append(chance)
        record_crystal = random.choices(cases, chances)[0]

    results: List[str] = []
    release_crystal = 0
    characters = copy.deepcopy(player.characters)
    for c in chars:
        character = characters.get(c[1])
        if character:
            if c[0] == 5:
                if character['rarity'] == 5:
                    release_crystal += 100
                    results.append(f'★5 {strike(c[1])} → 해방결정 100개')
                else:
                    release_crystal += 50
                    character['rarity'] = 5
                    results.append(f'★4→5 {bold(c[1])} + 해방결정 50개')
            elif c[0] == 4:
                release_crystal += 50
                results.append(f'★4 {strike(c[1])} → 해방결정 50개')
            elif c[0] == 3:
                release_crystal += 2
                results.append(f'★3 {strike(c[1])} → 해방결정 2개')
            else:
                release_crystal += 1
                results.append(f'★2 {strike(c[1])} → 해방결정 1개')
        else:
            characters[c[1]] = {
                'rarity': c[0],
            }
            if c[0] in [4, 5]:
                results.append(f'★{c[0]} {bold(c[1])}')
            else:
                results.append(f'★{c[0]} {c[1]}')

    player.characters = characters
    player.release_crystal += release_crystal

    record_crystal_name = (
        f'{scout.title} {COST_TYPE_LABEL[CostType.record_crystal]}'
    )
    record_crystals = copy.deepcopy(player.record_crystals)
    if step.cost_type == CostType.diamond:
        player.used_diamond += step.cost

        if record_crystal:
            if record_crystal_name in player.record_crystals:
                record_crystals[record_crystal_name] += record_crystal
            else:
                record_crystals[record_crystal_name] = record_crystal
    elif step.cost_type == CostType.record_crystal:
        if record_crystal_name in player.record_crystals:
            record_crystals[record_crystal_name] += (
                record_crystal - step.cost
            )
        else:
            record_crystals[record_crystal_name] = (
                record_crystal - step.cost
            )

    player.record_crystals = record_crystals
    player_scout.next_step = step.next_step or step

    with sess.begin():
        sess.add(player)
        sess.add(player_scout)

    await bot.say(
        event.channel,
        ('{cost_type} {cost}개를 소모하여 {title} {step} {count}{c}차를 시도합니다.'
         '\n\n{result}\n\n해방 결정을 {release_crystal}개'
         '{record_crystal} 획득했습니다.').format(
            cost_type=COST_TYPE_LABEL[step.cost_type],
            cost=step.cost,
            title=scout.title,
            step=step.name,
            count=step.count,
            c='연' if step.count > 1 else '단',
            result='\n'.join(results),
            release_crystal=release_crystal,
            record_crystal=(
                f', 기록결정 크리스탈을 {record_crystal}개'
                if record_crystal > 0 else ''
            ),
        )
    )


@box.command('무기뽑기', ['무뽑'], channels=only(
    'game', 'test', DM, error='게임/테스트 채널에서만 해주세요'
))
@argument('scout_title', nargs=-1, concat=True,
          count_error='스카우트 타이틀을 입력해주세요')
async def saomd_weapon_scout(bot, event: Message, sess, scout_title: str):
    """
    소드 아트 온라인 메모리 디프래그의 무기 뽑기를 시뮬레이팅합니다.

    `{PREFIX}무뽑 두근두근` (두근두근 수증기와 미인의 온천 스카우트 11연차를 시뮬레이션)

    지원되는 스카우트 타이틀은 `{PREFIX}무뽑종류` 로 확인하세요.

    """

    try:
        player = sess.query(Player).filter_by(user=event.user).one()
    except NoResultFound:
        player = Player()
        player.user = event.user
        with sess.begin():
            sess.add(player)

    scouts = sess.query(Scout).filter_by(type=ScoutType.weapon).all()

    scout = scouts[0]
    ratio = fuzzy_korean_ratio(scout.title, scout_title)
    for s in scouts[1:]:
        _ratio = fuzzy_korean_ratio(s.title, scout_title)
        if ratio < _ratio:
            ratio = _ratio
            scout = s

    try:
        player_scout = sess.query(PlayerScout).filter(
            PlayerScout.player == player,
            PlayerScout.scout == scout,
            ).one()
    except NoResultFound:
        first = sess.query(Step).filter(
            Step.scout == scout,
            Step.is_first == True,  # noqa
        ).one()
        player_scout = PlayerScout()
        player_scout.player = player
        player_scout.scout = scout
        player_scout.next_step = first

        with sess.begin():
            sess.add(player_scout)

    step: Step = player_scout.next_step

    weapons: List[Tuple[int, str]] = []

    five = step.s5_chance
    four = five + step.s4_chance
    three = four + 0.25

    result_length = step.count
    for x in range(step.s5_fixed):
        weapons.append((5, random.choice(scout.s5_units)))
        result_length -= 1
    for x in range(step.s4_fixed):
        weapons.append((4, random.choice(scout.s4_units)))
        result_length -= 1
    for x in range(result_length):
        r = random.random()
        if r <= five:
            weapons.append((5, random.choice(scout.s5_units)))
        elif r <= four:
            weapons.append((4, random.choice(scout.s4_units)))
        elif r <= three:
            weapons.append((3, random.choice(THREE_STAR_WEAPONS)))
        else:
            weapons.append((2, random.choice(TWO_STAR_WEAPONS)))

    record_crystal = 0

    if scout.record_crystal:
        cases: List[int] = []
        chances: List[float] = []
        for case, chance in scout.record_crystal:
            cases.append(case)
            chances.append(chance)
        record_crystal = random.choices(cases, chances)[0]

    results: List[str] = []
    player_weapons = copy.deepcopy(player.weapons)
    for w in weapons:
        weapon = player_weapons.get(w[1])
        if weapon:
            player_weapons[w[1]]['count'] += 1
        else:
            player_weapons[w[1]] = {
                'rarity': w[0],
                'count': 1,
            }

        if w[0] in [4, 5]:
            results.append(f'★{w[0]} {bold(w[1])}')
        else:
            results.append(f'★{w[0]} {w[1]}')

    player.weapons = player_weapons

    record_crystal_name = (
        f'{scout.title} {COST_TYPE_LABEL[CostType.record_crystal]}'
    )
    record_crystals = copy.deepcopy(player.record_crystals)
    if step.cost_type == CostType.diamond:
        player.used_diamond += step.cost

        if record_crystal:
            if record_crystal_name in player.record_crystals:
                record_crystals[record_crystal_name] += record_crystal
            else:
                record_crystals[record_crystal_name] = record_crystal
    elif step.cost_type == CostType.record_crystal:
        if record_crystal_name in player.record_crystals:
            record_crystals[record_crystal_name] += (
                record_crystal - step.cost
            )
        else:
            record_crystals[record_crystal_name] = (
                record_crystal - step.cost
            )

    player.record_crystals = record_crystals
    player_scout.next_step = step.next_step or step

    with sess.begin():
        sess.add(player)
        sess.add(player_scout)

    await bot.say(
        event.channel,
        ('{cost_type} {cost}개를 소모하여 {title} {step} {count}{c}차를 시도합니다.'
         '\n\n{result}\n\n{record_crystal}').format(
            cost_type=COST_TYPE_LABEL[step.cost_type],
            cost=step.cost,
            title=scout.title,
            step=step.name,
            count=step.count,
            c='연' if step.count > 1 else '단',
            result='\n'.join(results),
            record_crystal=(
                f'기록결정 크리스탈을 {record_crystal}개 획득했습니다.'
                if record_crystal > 0 else ''
            ),
        )
    )


@box.command('캐릭뽑기종류', ['캐뽑종류'])
async def saomd_character_scouts_list(bot, event: Message, sess):
    """
    SAOMD 캐릭뽑기 스카우트 타이틀 목록

    `{PREFIX}캐뽑종류` (목록을 thread로 전송)

    """

    scouts = sess.query(Scout).filter_by(type=ScoutType.character).all()
    await bot.say(
        event.channel,
        '\n'.join(f'- {s.title}' for s in scouts),
        thread_ts=event.ts,
    )


@box.command('무기뽑기종류', ['무뽑종류'])
async def saomd_weapon_scouts_list(bot, event: Message, sess):
    """
    SAOMD 무기뽑기 스카우트 타이틀 목록

    `{PREFIX}무뽑종류` (목록을 thread로 전송)

    """

    scouts = sess.query(Scout).filter_by(type=ScoutType.weapon).all()
    await bot.say(
        event.channel,
        '\n'.join(f'- {s.title}' for s in scouts),
        thread_ts=event.ts,
    )


@box.command('시뮬결과')
async def saomd_sim_result(bot, event: Message, sess):
    """
    SAOMD 시뮬레이션 결과

    `{PREFIX}시뮬결과` (SAOMD 시뮬레이션 결과를 thread로 출력)

    """

    try:
        player = sess.query(Player).filter_by(user=event.user).one()
    except NoResultFound:
        await bot.say(
            event.channel,
            '시뮬을 해보신 적 없으신 것 같아요!'
        )
        return

    await bot.say(
        event.channel,
        ('소모한 메모리 다이아: {used_diamond:,}\n'
         '소지중인 해방 결정: {release_crystal}\n'
         '소지중인 캐릭터:\n{characters}\n'
         '소지중인 무기:\n{weapons}\n'
         '소지중인 기록 결정:\n{record_crystals}').format(
            used_diamond=player.used_diamond,
            release_crystal=player.release_crystal,
            characters='\n'.join(
                f"- ★{data['rarity']} {bold(name)}"
                if data['rarity'] >= 4 else f"* ★{data['rarity']} {name}"
                for name, data in sorted(
                    player.characters.items(),
                    key=lambda x: -x[1]['rarity'],
                )
            ),
            weapons='\n'.join(
                f"- ★{data['rarity']} {bold(name)}: {data['count']:,}개"
                if data['rarity'] >= 4 else
                f"- ★{data['rarity']} {name}: {data['count']:,}개"
                for name, data in sorted(
                    player.weapons.items(),
                    key=lambda x: -x[1]['rarity'],
                )
            ),
            record_crystals='\n'.join(
                f"- {name}: {count:,}"
                for name, count in player.record_crystals.items()
            ),
        ),
        thread_ts=event.ts,
    )


@box.command('시뮬결과리셋')
async def saomd_sim_result_reset(bot, event: Message, sess):
    """
    SAOMD 시뮬 결과 리셋

    `{PREFIX}시뮬결과리셋` (SAOMD 시뮬레이션 결과를 모두 삭제)

    """

    try:
        player = sess.query(Player).filter_by(user=event.user).one()
    except NoResultFound:
        await bot.say(
            event.channel,
            '리셋할 데이터가 없어요!'
        )
        return

    sess.query(PlayerScout).filter_by(player=player).delete()

    player.record_crystals = {}
    player.weapons = {}
    player.characters = {}
    player.release_crystal = 0
    player.used_diamond = 0

    with sess.begin():
        sess.add(player)

    await bot.say(
        event.channel,
        '리셋했어요!'
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
            fuzzy_korean_ratio(keyword, name),
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
        ratio = fuzzy_korean_ratio(name, keyword)
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
