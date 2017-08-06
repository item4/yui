import random

from ..box import box
from ..command import argument


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
    '앙케': [
        '인과의 법칙검+1',
        '엔젤 클레이모어+1',
        '제미니 그라디우스+1',
        '피셔즈 소드+1',
        '원스 어픈 어 타임+1',
    ],
    '여름': [
        '릴리 망고슈',
        '아일랜드 스피어',
        '마린 샷',
        '선플라워 엣지',
        '비치 버스터',
    ],
}


@box.command('무기뽑기', ['무뽑'])
@argument('category', count_error='카테고리를 입력해주세요')
async def saomd_weapon(bot, message, category):
    """
    소드 아트 온라인 메모리 디프래그의 무기 뽑기를 시뮬레이팅합니다.

    `{PREFIX}무뽑 가속` (가속하는 리얼 11연차를 시뮬레이션)

    카테고리: 가속(가속하는 리얼), 기사(기사들의 해후), 앙케(앙케이트 인기 무기), 여름(여름빛 소녀)

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
