from typing import Callable, List, Tuple

from .models.saomd import CostType, Scout, ScoutType, Step


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
    '[정합기사] 앨리스',
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
    '[황금의 기사] 앨리스',
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
    '[볼 빨간 여름의 프린세스] 앨리스',
    '[여름 밤을 비추는 수양버들] 아스나',
    '[탄도에 피는 나팔꽃] 시논',
    '[시원한 저녁놀의 싸리꽃] 스구하',
    '[노래하는 백일홍] 세븐',
    '[춤추듯 지는 벚꽃] 레인',
    '[저편의 검객] 스구하',
    '[소생하는 검극] 키리토',
    '[마음의 섬광] 아스나',
    '[그 날의 약속] 아스나',
    '[유월의 금목서] 앨리스',
    '[맹세의 입맞춤] 리파',
    '[하이힐의 신부] 시논',
    '[부케 토스 점프] 유우키',
    '[축복의 숨결] 시리카',
    '[천승의 무희] 유우키',
    '[재회의 약속] 필리아',
    '[별 그림자의 기도] 시리카',
    '[치유의 여름 미인] 아스나',
    '[두근거리는 여름 처녀] 스구하',
    '[장난스런 여름 소녀] 시논',
    '[해바라기 여름소녀] 시리카',
    '[장사수완 좋은 노점상] 리즈벳',
    '[여름밤에 울리는 소리] 리파',
    '[신락의 춤] 프리미어',
    '[긍지 높은 선장] 키리토',
    '[갑판을 채색하는 부선장] 아스나',
    '[감시대의 명저격수] 시논',
    '[직감의 조타수] 유우키',
]


def 두근두근_수증기와_미인의_온천_캐릭터(sess):
    scout = Scout()
    scout.title = '두근두근 수증기와 미인의 온천 스카우트'
    scout.type = ScoutType.character
    scout.s4_units = FOUR_STAR_CHARACTERS
    scout.s5_units = [
        '[고운 피부의 여신] 아스나',
        '[되돌아보는 미인] 시논',
        '[비밀탕의 미인] 리파',
        '[단풍탕의 미인] 시리카',
    ]
    scout.record_crystal = [
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
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = 'Step 1'
    step1.is_first = True
    step1.cost = 125
    step1.cost_type = CostType.diamond
    step1.s5_chance = 0.02

    step2 = Step()
    step2.scout = scout
    step2.name = 'Step 2+'
    step2.cost = 250
    step2.cost_type = CostType.diamond
    step2.s5_chance = 0.02

    step1.next_step = step2
    step2.next_step = None

    with sess.begin():
        sess.add(scout)
        sess.add(step1)
        sess.add(step2)


def 두근두근_수증기와_미인의_온천_무기(sess):
    scout = Scout()
    scout.title = '두근두근 수증기와 미인의 온천 스카우트'
    scout.type = ScoutType.weapon
    scout.s4_units = [
        '성화의 레이피어',
        '신을 섬기는 미창',
        '붉게 칠한 비도',
        '빛나는 물의 검',
    ]

    step1 = Step()
    step1.is_first = True
    step1.scout = scout
    step1.name = 'Step 1'
    step1.cost = 100
    step1.cost_type = CostType.diamond

    step2 = Step()
    step2.scout = scout
    step2.name = 'Step 2'
    step2.cost = 150
    step2.cost_type = CostType.diamond

    step3 = Step()
    step3.scout = scout
    step3.name = 'Step 3'
    step3.cost = 150
    step3.cost_type = CostType.diamond
    step3.s4_chance = 0.04 * 2

    step1.next_step = step2
    step2.next_step = step3
    step3.next_step = step1

    with sess.begin():
        sess.add(scout)
        sess.add(step1)
        sess.add(step2)
        sess.add(step3)


def 우정의_바톤_가을_대운동회_스카우트_캐릭터(sess):
    scout = Scout()
    scout.title = '우정의 바톤! 가을 대운동회 스카우트'
    scout.type = ScoutType.character
    scout.s4_units = FOUR_STAR_CHARACTERS
    scout.s5_units = [
        '[화려한 골] 아스나',
        '[일등상을 목표로] 유이',
        '[빛나는 땀과 청춘의 빛] 리파',
        '[네버 기브업] 리즈벳',
    ]
    scout.record_crystal = [
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
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = 'Step 1'
    step1.is_first = True
    step1.cost = 125
    step1.cost_type = CostType.diamond
    step1.s5_chance = 0.02

    step2 = Step()
    step2.scout = scout
    step2.name = 'Step 2+'
    step2.cost = 250
    step2.cost_type = CostType.diamond
    step2.s5_chance = 0.02

    step1.next_step = step2
    step2.next_step = None

    with sess.begin():
        sess.add(scout)
        sess.add(step1)
        sess.add(step2)


def 우정의_바톤_가을_대운동회_스카우트_무기(sess):
    scout = Scout()
    scout.title = '우정의 바톤! 가을 대운동회 스카우트'
    scout.type = ScoutType.weapon
    scout.s4_units = [
        '빅토리 플뢰레',
        '챔피언 대거',
        '글로리어스 블레이드',
        '위너즈 스피어',
    ]

    step1 = Step()
    step1.is_first = True
    step1.scout = scout
    step1.name = '일반'
    step1.cost = 150
    step1.cost_type = CostType.diamond

    with sess.begin():
        sess.add(scout)
        sess.add(step1)


def 일주년기념_5성진화_앙케이트_스카우트_캐릭터(sess):
    scout = Scout()
    scout.title = '1주년기념 5성진화 앙케이트 스카우트'
    scout.type = ScoutType.character
    scout.s4_units = list(set(FOUR_STAR_CHARACTERS) - {
        '[일어서는 영웅] 키리토',
        '[맞서는 결의] 아스나',
        '[황금의 기사] 앨리스',
        '[떨어지는 빗방울의 처녀] 레인',
    })
    scout.s5_units = [
        '[일어서는 영웅] 키리토',
        '[맞서는 결의] 아스나',
        '[황금의 기사] 앨리스',
        '[떨어지는 빗방울의 처녀] 레인',
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = 'Step 1'
    step1.is_first = True
    step1.cost = 125
    step1.cost_type = CostType.diamond
    step1.s5_chance = 0.02

    step2 = Step()
    step2.scout = scout
    step2.name = 'Step 2'
    step2.cost = 250
    step2.cost_type = CostType.diamond
    step2.s5_chance = 0.02

    step3 = Step()
    step3.scout = scout
    step3.name = 'Step 3'
    step3.cost = 250
    step3.cost_type = CostType.diamond
    step3.s5_chance = 0.04

    step1.next_step = step2
    step2.next_step = step3
    step3.next_step = step1

    with sess.begin():
        sess.add(scout)
        sess.add(step1)
        sess.add(step2)
        sess.add(step3)


def 일주년기념_5성진화_앙케이트_스카우트_무기(sess):
    scout = Scout()
    scout.title = '1주년기념 5성진화 앙케이트 스카우트'
    scout.type = ScoutType.weapon
    scout.s4_units = [
        '하이드런지아 소드+1x2',
        '히로익 프로미스+1',
        '컬리지+1',
        '금목서의 검+1',
    ]

    step1 = Step()
    step1.is_first = True
    step1.scout = scout
    step1.name = '일반'
    step1.cost = 150
    step1.cost_type = CostType.diamond

    with sess.begin():
        sess.add(scout)
        sess.add(step1)


def 키리토_아스나_결혼기념일_스카우트_캐릭터(sess):
    scout = Scout()
    scout.title = '키리토 & 아스나 결혼기념일 스카우트'
    scout.type = ScoutType.character
    scout.s4_units = list(set(FOUR_STAR_CHARACTERS) - {
        '[그 날의 약속] 아스나',
    })
    scout.s5_units = [
        '[그 날의 약속] 키리토',
        '[그 날의 약속] 아스나',
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = 'Step 1'
    step1.is_first = True
    step1.cost = 125
    step1.cost_type = CostType.diamond
    step1.s5_chance = 0.02

    step2 = Step()
    step2.scout = scout
    step2.name = 'Step 2'
    step2.cost = 250
    step2.cost_type = CostType.diamond
    step2.s5_chance = 0.02

    step3 = Step()
    step3.scout = scout
    step3.name = 'Step 3'
    step3.cost = 250
    step3.cost_type = CostType.diamond
    step3.s5_chance = 0.04

    step1.next_step = step2
    step2.next_step = step3
    step3.next_step = step1

    with sess.begin():
        sess.add(scout)
        sess.add(step1)
        sess.add(step2)
        sess.add(step3)


def 환영의_탄환이_쌓는_두사람의_인연_스카우트_캐릭터(sess):
    scout = Scout()
    scout.title = '환영의 탄환이 쌓는 두사람의 인연 스카우트'
    scout.type = ScoutType.character
    scout.s4_units = FOUR_STAR_CHARACTERS
    scout.s5_units = [
        '[황야에 내려선 검사] 키리토',
        '[그리움에 기대는 저격수] 시논',
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = 'Step 1'
    step1.is_first = True
    step1.cost = 125
    step1.cost_type = CostType.diamond
    step1.s5_chance = 0.02

    step2 = Step()
    step2.scout = scout
    step2.name = 'Step 2'
    step2.cost = 250
    step2.cost_type = CostType.diamond
    step2.s5_chance = 0.02

    step3 = Step()
    step3.scout = scout
    step3.name = 'Step 3'
    step3.cost = 250
    step3.cost_type = CostType.diamond
    step3.s5_chance = 0.04

    step1.next_step = step2
    step2.next_step = step3
    step3.next_step = step1

    with sess.begin():
        sess.add(scout)
        sess.add(step1)
        sess.add(step2)
        sess.add(step3)


def 환영의_탄환이_쌓는_두사람의_인연_스카우트_무기(sess):
    scout = Scout()
    scout.title = '환영의 탄환이 쌓는 두사람의 인연 스카우트'
    scout.type = ScoutType.weapon
    scout.s4_units = [
        '츠키카게',
        '헤카테 겐나이온',
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = 'Step 1'
    step1.is_first = True
    step1.cost = 100
    step1.cost_type = CostType.diamond

    step2 = Step()
    step2.scout = scout
    step2.name = 'Step 2'
    step2.cost = 150
    step2.cost_type = CostType.diamond

    step3 = Step()
    step3.scout = scout
    step3.name = 'Step 3'
    step3.cost = 150
    step3.cost_type = CostType.diamond
    step3.s4_chance = 0.08

    step1.next_step = step2
    step2.next_step = step3
    step3.next_step = step1

    with sess.begin():
        sess.add(scout)
        sess.add(step1)
        sess.add(step2)
        sess.add(step3)


def 장난스런_할로윈_나이트_스카우트_캐릭터(sess):
    scout = Scout()
    scout.title = '장난스런 할로윈 나이트 스카우트'
    scout.type = ScoutType.character
    scout.s4_units = FOUR_STAR_CHARACTERS
    scout.s5_units = [
        '[사랑에 빠진 뱀파이어] 유우키',
        '[상냥한 몬스터] 리파',
        '[스파이더 위치] 시논',
        '[새끼고양이 마녀] 시리카',
    ]
    scout.record_crystal = [
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
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = 'Step 1'
    step1.is_first = True
    step1.cost = 125
    step1.cost_type = CostType.diamond
    step1.s5_chance = 0.02

    step2 = Step()
    step2.scout = scout
    step2.name = 'Step 2+'
    step2.cost = 250
    step2.cost_type = CostType.diamond
    step2.s5_chance = 0.02

    step1.next_step = step2

    with sess.begin():
        sess.add(scout)
        sess.add(step1)
        sess.add(step2)


def 장난스런_할로윈_나이트_스카우트_무기(sess):
    scout = Scout()
    scout.title = '장난스런 할로윈 나이트 스카우트'
    scout.type = ScoutType.weapon
    scout.s4_units = [
        '트릭 오어 바렛',
        '샤노와르',
        '데빌 스태프',
        '머시너리 소드',
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = '일반'
    step1.is_first = True
    step1.cost = 150
    step1.cost_type = CostType.diamond

    with sess.begin():
        sess.add(scout)
        sess.add(step1)


def 달밤의_할로윈_퍼레이드_스카우트_캐릭터(sess):
    scout = Scout()
    scout.title = '달밤의 할로윈 퍼레이드 스카우트'
    scout.type = ScoutType.character
    scout.s4_units = FOUR_STAR_CHARACTERS
    scout.s5_units = [
        '[생피를 바쳐라] 키리토',
        '[달밤의 포효] 유지오',
        '[한밤중의 유혹] 아스나',
        '[호박의 기사] 앨리스',
    ]
    scout.record_crystal = [
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
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = 'Step 1'
    step1.is_first = True
    step1.cost = 125
    step1.cost_type = CostType.diamond
    step1.s5_chance = 0.02

    step2 = Step()
    step2.scout = scout
    step2.name = 'Step 2+'
    step2.cost = 250
    step2.cost_type = CostType.diamond
    step2.s5_chance = 0.02

    step1.next_step = step2

    with sess.begin():
        sess.add(scout)
        sess.add(step1)
        sess.add(step2)


def 달밤의_할로윈_퍼레이드_스카우트_무기(sess):
    scout = Scout()
    scout.title = '달밤의 할로윈 퍼레이드 스카우트'
    scout.type = ScoutType.weapon
    scout.s4_units = [
        '웨어울프팡',
        '데몬즈 블레이트x배트 에스파다',
        '펌프킨 블레이드',
        '나이트메어 완드',
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = '일반'
    step1.is_first = True
    step1.cost = 150
    step1.cost_type = CostType.diamond

    with sess.begin():
        sess.add(scout)
        sess.add(step1)


def 남자들의_광연_스카우트_캐릭터(sess):
    scout = Scout()
    scout.title = '남자들의 광연 스카우트'
    scout.type = ScoutType.character
    scout.s4_units = list(set(FOUR_STAR_CHARACTERS) - {
        '[치유의 여름 미인] 아스나',
        '[두근거리는 여름 처녀] 스구하',
        '[장난스런 여름 소녀] 시논',
        '[해바라기 여름소녀] 시리카',
        '[장사수완 좋은 노점상] 리즈벳',
        '[여름밤에 울리는 소리] 리파',
        '[신락의 춤] 프리미어',
        '[긍지 높은 선장] 키리토',
        '[갑판을 채색하는 부선장] 아스나',
        '[감시대의 명저격수] 시논',
        '[직감의 조타수] 유우키',
    })
    scout.s5_units = [
        '[꺾이지 않는 마음] 클라인',
        '[결속의 힘] 에길',
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = 'Step 1'
    step1.is_first = True
    step1.cost = 200
    step1.cost_type = CostType.diamond
    step1.s5_chance = 0.02

    step2 = Step()
    step2.scout = scout
    step2.name = 'Step 2'
    step2.cost = 250
    step2.cost_type = CostType.diamond
    step2.s5_chance = 0.02

    step3 = Step()
    step3.scout = scout
    step3.name = 'Step 3'
    step3.cost = 200
    step3.cost_type = CostType.diamond
    step3.s5_chance = 0.02 * 1.5

    step4 = Step()
    step4.scout = scout
    step4.name = 'Step 4'
    step4.cost = 250
    step4.cost_type = CostType.diamond
    step4.s5_chance = 0.02

    step5 = Step()
    step5.scout = scout
    step5.name = 'Step 5'
    step5.cost = 250
    step5.cost_type = CostType.diamond
    step5.s5_chance = 0.02
    step5.s5_fixed = 1

    step6 = Step()
    step6.scout = scout
    step6.name = 'Step 6'
    step6.cost = 250
    step6.cost_type = CostType.diamond
    step6.s5_chance = 0.04

    step1.next_step = step2
    step2.next_step = step3
    step3.next_step = step4
    step4.next_step = step5
    step5.next_step = step6

    with sess.begin():
        sess.add(scout)
        sess.add(step1)
        sess.add(step2)
        sess.add(step3)
        sess.add(step4)
        sess.add(step5)
        sess.add(step6)


def 남자들의_광연_스카우트_무기(sess):
    scout = Scout()
    scout.title = '남자들의 광연 스카우트'
    scout.type = ScoutType.weapon
    scout.s4_units = [
        '명도 아카츠키',
        '그레이트 넘버',
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = '일반'
    step1.is_first = True
    step1.cost = 150
    step1.cost_type = CostType.diamond

    with sess.begin():
        sess.add(scout)
        sess.add(step1)


def 지나가는_시간과_우정의_기억_스카우트_캐릭터(sess):
    scout = Scout()
    scout.title = '지나가는 시간과 우정의 기억 스카우트'
    scout.type = ScoutType.character
    scout.s4_units = list(set(FOUR_STAR_CHARACTERS) - {
        '[치유의 여름 미인] 아스나',
        '[두근거리는 여름 처녀] 스구하',
        '[장난스런 여름 소녀] 시논',
        '[해바라기 여름소녀] 시리카',
        '[장사수완 좋은 노점상] 리즈벳',
        '[여름밤에 울리는 소리] 리파',
        '[신락의 춤] 프리미어',
        '[긍지 높은 선장] 키리토',
        '[갑판을 채색하는 부선장] 아스나',
        '[감시대의 명저격수] 시논',
        '[직감의 조타수] 유우키',
    })
    scout.s5_units = [
        '[마음을 잇는 물요정] 아스나',
        '[희망을 이루는 검호] 유우키',
        '[순수한 미소의 수호자] 시리카',
        '[조화를 지키는 자] 리즈벳',
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = 'Step 1'
    step1.is_first = True
    step1.cost = 200
    step1.cost_type = CostType.diamond
    step1.s5_chance = 0.02

    step2 = Step()
    step2.scout = scout
    step2.name = 'Step 2'
    step2.cost = 250
    step2.cost_type = CostType.diamond
    step2.s5_chance = 0.02

    step3 = Step()
    step3.scout = scout
    step3.name = 'Step 3'
    step3.cost = 200
    step3.cost_type = CostType.diamond
    step3.s5_chance = 0.02 * 1.5

    step4 = Step()
    step4.scout = scout
    step4.name = 'Step 4'
    step4.cost = 250
    step4.cost_type = CostType.diamond
    step4.s5_chance = 0.02

    step5 = Step()
    step5.scout = scout
    step5.name = 'Step 5'
    step5.cost = 250
    step5.cost_type = CostType.diamond
    step5.s5_chance = 0.02
    step5.s5_fixed = 1

    step6 = Step()
    step6.scout = scout
    step6.name = 'Step 6'
    step6.cost = 250
    step6.cost_type = CostType.diamond
    step6.s5_chance = 0.04

    step1.next_step = step2
    step2.next_step = step3
    step3.next_step = step4
    step4.next_step = step5
    step5.next_step = step6

    with sess.begin():
        sess.add(scout)
        sess.add(step1)
        sess.add(step2)
        sess.add(step3)
        sess.add(step4)
        sess.add(step5)
        sess.add(step6)


def 지나가는_시간과_우정의_기억_스카우트_무기(sess):
    scout = Scout()
    scout.title = '지나가는 시간과 우정의 기억 스카우트'
    scout.type = ScoutType.weapon
    scout.s4_units = [
        '아틀탄티스 소드',
        '철운석의 검',
        '카른웨난',
        '플라네타리 메이스',
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = '일반'
    step1.is_first = True
    step1.cost = 150
    step1.cost_type = CostType.diamond

    with sess.begin():
        sess.add(scout)
        sess.add(step1)


def 돌아가는_세계에_겁쳐진_검_스카우트_캐릭터(sess):
    scout = Scout()
    scout.title = '돌아가는 세계에 겁쳐진 검 스카우트'
    scout.type = ScoutType.character
    scout.s4_units = list(set(FOUR_STAR_CHARACTERS) - {
        '[치유의 여름 미인] 아스나',
        '[두근거리는 여름 처녀] 스구하',
        '[장난스런 여름 소녀] 시논',
        '[해바라기 여름소녀] 시리카',
        '[장사수완 좋은 노점상] 리즈벳',
        '[여름밤에 울리는 소리] 리파',
        '[신락의 춤] 프리미어',
        '[긍지 높은 선장] 키리토',
        '[갑판을 채색하는 부선장] 아스나',
        '[감시대의 명저격수] 시논',
        '[직감의 조타수] 유우키',
    })
    scout.s5_units = [
        '[청장미의 정합기사] 유지오',
        '[금목서의 정합기사] 엘리스',
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = 'Step 1'
    step1.is_first = True
    step1.cost = 200
    step1.cost_type = CostType.diamond
    step1.s5_chance = 0.02

    step2 = Step()
    step2.scout = scout
    step2.name = 'Step 2'
    step2.cost = 250
    step2.cost_type = CostType.diamond
    step2.s5_chance = 0.02

    step3 = Step()
    step3.scout = scout
    step3.name = 'Step 3'
    step3.cost = 200
    step3.cost_type = CostType.diamond
    step3.s5_chance = 0.02 * 1.5

    step4 = Step()
    step4.scout = scout
    step4.name = 'Step 4'
    step4.cost = 250
    step4.cost_type = CostType.diamond
    step4.s5_chance = 0.02

    step5 = Step()
    step5.scout = scout
    step5.name = 'Step 5'
    step5.cost = 250
    step5.cost_type = CostType.diamond
    step5.s5_chance = 0.02
    step5.s5_fixed = 1

    step6 = Step()
    step6.scout = scout
    step6.name = 'Step 6'
    step6.cost = 250
    step6.cost_type = CostType.diamond
    step6.s5_chance = 0.04

    step1.next_step = step2
    step2.next_step = step3
    step3.next_step = step4
    step4.next_step = step5
    step5.next_step = step6

    with sess.begin():
        sess.add(scout)
        sess.add(step1)
        sess.add(step2)
        sess.add(step3)
        sess.add(step4)
        sess.add(step5)
        sess.add(step6)


def 돌아가는_세계에_겁쳐진_검_스카우트_무기(sess):
    scout = Scout()
    scout.title = '돌아가는 세계에 겁쳐진 검 스카우트'
    scout.type = ScoutType.weapon
    scout.s4_units = [
        '영겁불후의 검',
        '영구빙괴의 검',
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = '일반'
    step1.is_first = True
    step1.cost = 150
    step1.cost_type = CostType.diamond

    with sess.begin():
        sess.add(scout)
        sess.add(step1)


def 신뢰의_증거_운명의_인연_스카우트_캐릭터(sess):
    scout = Scout()
    scout.title = '신뢰의 증거 운명의 인연 스카우트'
    scout.type = ScoutType.character
    scout.s4_units = list(set(FOUR_STAR_CHARACTERS) - {
        '[치유의 여름 미인] 아스나',
        '[두근거리는 여름 처녀] 스구하',
        '[장난스런 여름 소녀] 시논',
        '[해바라기 여름소녀] 시리카',
        '[장사수완 좋은 노점상] 리즈벳',
        '[여름밤에 울리는 소리] 리파',
        '[신락의 춤] 프리미어',
        '[긍지 높은 선장] 키리토',
        '[갑판을 채색하는 부선장] 아스나',
        '[감시대의 명저격수] 시논',
        '[직감의 조타수] 유우키',
    })
    scout.s5_units = [
        '[시스템을 뛰어넘는 의지] 키리토',
        '[운명을 바꾸는 의사] 아스나',
        '[마음과 마주하는 검사] 리파',
        '[과거를 극복하는 사수] 시논',
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = 'Step 1'
    step1.is_first = True
    step1.cost = 200
    step1.cost_type = CostType.diamond
    step1.s5_chance = 0.02

    step2 = Step()
    step2.scout = scout
    step2.name = 'Step 2'
    step2.cost = 250
    step2.cost_type = CostType.diamond
    step2.s5_chance = 0.02

    step3 = Step()
    step3.scout = scout
    step3.name = 'Step 3'
    step3.cost = 200
    step3.cost_type = CostType.diamond
    step3.s5_chance = 0.02 * 1.5

    step4 = Step()
    step4.scout = scout
    step4.name = 'Step 4'
    step4.cost = 250
    step4.cost_type = CostType.diamond
    step4.s5_chance = 0.02

    step5 = Step()
    step5.scout = scout
    step5.name = 'Step 5'
    step5.cost = 250
    step5.cost_type = CostType.diamond
    step5.s5_chance = 0.02
    step5.s5_fixed = 1

    step6 = Step()
    step6.scout = scout
    step6.name = 'Step 6'
    step6.cost = 250
    step6.cost_type = CostType.diamond
    step6.s5_chance = 0.04

    step1.next_step = step2
    step2.next_step = step3
    step3.next_step = step4
    step4.next_step = step5
    step5.next_step = step6

    with sess.begin():
        sess.add(scout)
        sess.add(step1)
        sess.add(step2)
        sess.add(step3)
        sess.add(step4)
        sess.add(step5)
        sess.add(step6)


def 신뢰의_증거_운명의_인연_스카우트_무기(sess):
    scout = Scout()
    scout.title = '신뢰의 증거 운명의 인연 스카우트'
    scout.type = ScoutType.weapon
    scout.s4_units = [
        '인라이트먼트 x 섀도우 엘리미네이터',
        '다즐링 블링크',
        '이레디케이트 세이버',
        '구시스나우탈',
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = '일반'
    step1.is_first = True
    step1.cost = 150
    step1.cost_type = CostType.diamond

    with sess.begin():
        sess.add(scout)
        sess.add(step1)


def 일주년_카운트다운_앙케이트_스카우트_캐릭터(sess):
    scout = Scout()
    scout.title = '1주년 카운트다운! 앙케이트 스카우트'
    scout.type = ScoutType.character
    scout.s4_units = [
        '[일어서는 영웅] 키리토',
        '[맞서는 결의] 아스나',
        '[황금의 기사] 엘리스',
        '[숙련된 손님 맞이 메이드] 레인',
        '[고고히 포효하는 레오] 시논',
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = 'Step 1'
    step1.is_first = True
    step1.cost = 200
    step1.cost_type = CostType.diamond

    step2 = Step()
    step2.scout = scout
    step2.name = 'Step 2'
    step2.cost = 250
    step2.cost_type = CostType.diamond

    step3 = Step()
    step3.scout = scout
    step3.name = 'Step 3'
    step3.cost = 200
    step3.cost_type = CostType.diamond
    step3.s4_chance = 0.04 * 1.5

    step4 = Step()
    step4.scout = scout
    step4.name = 'Step 4'
    step4.cost = 250
    step4.cost_type = CostType.diamond

    step5 = Step()
    step5.scout = scout
    step5.name = 'Step 5'
    step5.cost = 250
    step5.cost_type = CostType.diamond
    step5.s4_chance = 0.08

    step1.next_step = step2
    step2.next_step = step3
    step3.next_step = step4
    step4.next_step = step5
    step5.next_step = step1

    with sess.begin():
        sess.add(scout)
        sess.add(step1)
        sess.add(step2)
        sess.add(step3)
        sess.add(step4)
        sess.add(step5)


def 일주년_카운트다운_앙케이트_스카우트_무기(sess):
    scout = Scout()
    scout.title = '1주년 카운트다운! 앙케이트 스카우트'
    scout.type = ScoutType.weapon
    scout.s4_units = [
        '히로익 프로미스+1',
        '컬리지+1',
        '금목서의 검+1',
        '티타임 세이버+1',
        '레오의 창+1',
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = '일반'
    step1.is_first = True
    step1.cost = 150
    step1.cost_type = CostType.diamond

    with sess.begin():
        sess.add(scout)
        sess.add(step1)


def 폭풍에_휘날리는_해적기_스카우트_캐릭터(sess):
    scout = Scout()
    scout.title = '폭풍에 휘날리는 해적기 스카우트'
    scout.type = ScoutType.character
    scout.s4_units = [
        '[긍지 높은 선장] 키리토',
        '[갑판을 채색하는 부선장] 아스나',
        '[감시대의 명저격수] 시논',
        '[쾌활한 항해사] 리파',
        '[직감의 조타수] 유우키',
    ]
    scout.record_crystal = [
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
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = '일반'
    step1.is_first = True
    step1.cost = 250
    step1.cost_type = CostType.diamond

    with sess.begin():
        sess.add(scout)
        sess.add(step1)


def 폭풍에_휘날리는_해적기_스카우트_무기(sess):
    scout = Scout()
    scout.title = '폭풍에 휘날리는 해적기 스카우트'
    scout.type = ScoutType.weapon
    scout.s4_units = [
        '오션 에스파다',
        '파이어릿 대거',
        '하버 라이플',
        '졸리 로저 사벨',
        '인쇼어 소드 x 오프쇼어 소드',
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = '일반'
    step1.is_first = True
    step1.cost = 150
    step1.cost_type = CostType.diamond

    with sess.begin():
        sess.add(scout)
        sess.add(step1)


def 여름밤의_축제_스카우트_캐릭터(sess):
    scout = Scout()
    scout.title = '여름밤의 축제 스카우트'
    scout.type = ScoutType.character
    scout.s4_units = [
        '[신락의 춤] 프리미어',
        '[여름밤에 울리는 소리] 리파',
        '[장사수완 좋은 노점상 리즈벳',
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = '일반'
    step1.is_first = True
    step1.cost = 250
    step1.cost_type = CostType.diamond

    with sess.begin():
        sess.add(scout)
        sess.add(step1)


def 여름밤의_축제_스카우트_무기(sess):
    scout = Scout()
    scout.title = '여름밤의 축제 스카우트'
    scout.type = ScoutType.weapon
    scout.s4_units = [
        '천신의 폭풍검',
        '풍차의 신검',
        '보구의 신창',
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = '일반'
    step1.is_first = True
    step1.cost = 150
    step1.cost_type = CostType.diamond

    with sess.begin():
        sess.add(scout)
        sess.add(step1)


def 매력분출_여름빛_소녀_스카우트_캐릭터(sess):
    scout = Scout()
    scout.title = '매력분출 여름빛 소녀 스카우트'
    scout.type = ScoutType.character
    scout.s4_units = [
        '[해바라기 여름 소녀] 시리카',
        '[태양의 여름 소녀] 리즈벳',
        '[장난스런 여름 소녀] 시논',
        '[두근거리는 여름 처녀] 스구하',
        '[치유의 여름 미인] 아스나',
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = '일반'
    step1.is_first = True
    step1.cost = 250
    step1.cost_type = CostType.diamond

    with sess.begin():
        sess.add(scout)
        sess.add(step1)


def 매력분출_여름빛_소녀_스카우트_무기(sess):
    scout = Scout()
    scout.title = '매력분출 여름빛 소녀 스카우트'
    scout.type = ScoutType.weapon
    scout.s4_units = [
        '비치 버스터',
        '선플라워 엣지',
        '마린 샷',
        '아일랜드 스피어',
        '릴리 망고슈',
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = '일반'
    step1.is_first = True
    step1.cost = 150
    step1.cost_type = CostType.diamond

    with sess.begin():
        sess.add(scout)
        sess.add(step1)


def 유카타_NIGHT_스카우트_캐릭터(sess):
    scout = Scout()
    scout.title = '유카타 NIGHT 스카우트'
    scout.type = ScoutType.character
    scout.s4_units = [
        '[여름 밤을 비추는 수양버들] 아스나',
        '[탄도에 피는 나팔꽃] 시논',
        '[시원한 저녁놀의 싸리꽃] 스구하',
        '[노래하는 백일홍] 세븐',
        '[춤추듯 지는 벚꽃] 레인',
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = '일반'
    step1.is_first = True
    step1.cost = 250
    step1.cost_type = CostType.diamond

    with sess.begin():
        sess.add(scout)
        sess.add(step1)


def 유카타_NIGHT_스카우트_무기(sess):
    scout = Scout()
    scout.title = '유카타 NIGHT 스카우트'
    scout.type = ScoutType.weapon
    scout.s4_units = [
        '麗刀・流れ柳 (세검)',
        '妖刀・雅文の調べ × 雅文の奏で (쌍검)',
        '祝槍・八重の繚乱 (창)',
        '宝銃・咲くや朝霧 (총)',
        '霊刀・萩の露 (단검)',
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = '일반'
    step1.is_first = True
    step1.cost = 150
    step1.cost_type = CostType.diamond

    with sess.begin():
        sess.add(scout)
        sess.add(step1)


def 인기_캐릭터_강화_앙케이트_스카우트_캐릭터(sess):
    scout = Scout()
    scout.title = '인기 캐릭터! 강화 앙케이트 스카우트'
    scout.type = ScoutType.character
    scout.s4_units = [
        '[참영비검] 아스나',
        '[인연의 제미니] 유우키',
        '[섬광의 무도] 아스나',
        '[천사의 성원] 유이',
        '[초여름을 장식하는 처녀] 스구하',
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = '일반'
    step1.is_first = True
    step1.cost = 250
    step1.cost_type = CostType.diamond

    with sess.begin():
        sess.add(scout)
        sess.add(step1)


def 인기_캐릭터_강화_앙케이트_스카우트_무기(sess):
    scout = Scout()
    scout.title = '인기 캐릭터! 강화 앙케이트 스카우트'
    scout.type = ScoutType.weapon
    scout.s4_units = [
        '인과의 법칙검+1',
        '엔젤 클레이모어+1',
        '제미니 그라디우스+1',
        '피셔즈 소드+1',
        '원스 어픈 어 타임+1',
    ]

    step1 = Step()
    step1.scout = scout
    step1.name = '일반'
    step1.is_first = True
    step1.cost = 150
    step1.cost_type = CostType.diamond

    with sess.begin():
        sess.add(scout)
        sess.add(step1)


SCOUT: List[Tuple[str, ScoutType, Callable]] = [
    (
        '두근두근 수증기와 미인의 온천 스카우트',
        ScoutType.character,
        두근두근_수증기와_미인의_온천_캐릭터,
    ),
    (
        '두근두근 수증기와 미인의 온천 스카우트',
        ScoutType.weapon,
        두근두근_수증기와_미인의_온천_무기,
    ),
    (
        '우정의 바톤! 가을 대운동회 스카우트',
        ScoutType.character,
        우정의_바톤_가을_대운동회_스카우트_캐릭터,
    ),
    (
        '우정의 바톤! 가을 대운동회 스카우트',
        ScoutType.weapon,
        우정의_바톤_가을_대운동회_스카우트_무기,
    ),
    (
        '1주년기념 5성진화 앙케이트 스카우트',
        ScoutType.character,
        일주년기념_5성진화_앙케이트_스카우트_캐릭터,
    ),
    (
        '1주년기념 5성진화 앙케이트 스카우트',
        ScoutType.weapon,
        일주년기념_5성진화_앙케이트_스카우트_무기,
    ),
    (
        '키리토 & 아스나 결혼기념일 스카우트',
        ScoutType.character,
        키리토_아스나_결혼기념일_스카우트_캐릭터,
    ),
    (
        '환영의 탄환이 쌓는 두사람의 인연 스카우트',
        ScoutType.character,
        환영의_탄환이_쌓는_두사람의_인연_스카우트_캐릭터,
    ),
    (
        '환영의 탄환이 쌓는 두사람의 인연 스카우트',
        ScoutType.weapon,
        환영의_탄환이_쌓는_두사람의_인연_스카우트_무기,
    ),
    (
        '장난스런 할로윈 나이트 스카우트',
        ScoutType.character,
        장난스런_할로윈_나이트_스카우트_캐릭터,
    ),
    (
        '장난스런 할로윈 나이트 스카우트',
        ScoutType.weapon,
        장난스런_할로윈_나이트_스카우트_무기,
    ),
    (
        '달밤의 할로윈 퍼레이드 스카우트',
        ScoutType.character,
        달밤의_할로윈_퍼레이드_스카우트_캐릭터,
    ),
    (
        '달밤의 할로윈 퍼레이드 스카우트',
        ScoutType.weapon,
        달밤의_할로윈_퍼레이드_스카우트_무기,
    ),
    (
        '남자들의 광연 스카우트',
        ScoutType.character,
        남자들의_광연_스카우트_캐릭터,
    ),
    (
        '남자들의 광연 스카우트',
        ScoutType.weapon,
        남자들의_광연_스카우트_무기,
    ),
    (
        '지나가는 시간과 우정의 기억 스카우트',
        ScoutType.character,
        지나가는_시간과_우정의_기억_스카우트_캐릭터,
    ),
    (
        '지나가는 시간과 우정의 기억 스카우트',
        ScoutType.weapon,
        지나가는_시간과_우정의_기억_스카우트_무기,
    ),
    (
        '돌아가는 세계에 겁쳐진 검 스카우트',
        ScoutType.character,
        돌아가는_세계에_겁쳐진_검_스카우트_캐릭터,
    ),
    (
        '돌아가는 세계에 겁쳐진 검 스카우트',
        ScoutType.weapon,
        돌아가는_세계에_겁쳐진_검_스카우트_무기,
    ),
    (
        '신뢰의 증거 운명의 인연 스카우트',
        ScoutType.character,
        신뢰의_증거_운명의_인연_스카우트_캐릭터,
    ),
    (
        '신뢰의 증거 운명의 인연 스카우트',
        ScoutType.weapon,
        신뢰의_증거_운명의_인연_스카우트_무기,
    ),
    (
        '1주년 카운트다운! 앙케이트 스카우트',
        ScoutType.character,
        일주년_카운트다운_앙케이트_스카우트_캐릭터,
    ),
    (
        '1주년 카운트다운! 앙케이트 스카우트',
        ScoutType.weapon,
        일주년_카운트다운_앙케이트_스카우트_무기,
    ),
    (
        '폭풍에 휘날리는 해적기 스카우트',
        ScoutType.character,
        폭풍에_휘날리는_해적기_스카우트_캐릭터,
    ),
    (
        '폭풍에 휘날리는 해적기 스카우트',
        ScoutType.weapon,
        폭풍에_휘날리는_해적기_스카우트_무기,
    ),
    (
        '여름밤의 축제 스카우트',
        ScoutType.character,
        여름밤의_축제_스카우트_캐릭터,
    ),
    (
        '여름밤의 축제 스카우트',
        ScoutType.weapon,
        여름밤의_축제_스카우트_무기,
    ),
    (
        '매력분출 여름빛 소녀 스카우트',
        ScoutType.character,
        매력분출_여름빛_소녀_스카우트_캐릭터,
    ),
    (
        '매력분출 여름빛 소녀 스카우트',
        ScoutType.weapon,
        매력분출_여름빛_소녀_스카우트_무기,
    ),
    (
        '유카타 NIGHT 스카우트',
        ScoutType.character,
        유카타_NIGHT_스카우트_캐릭터,
    ),
    (
        '유카타 NIGHT 스카우트',
        ScoutType.weapon,
        유카타_NIGHT_스카우트_무기,
    ),
    (
        '인기 캐릭터! 강화 앙케이트 스카우트',
        ScoutType.character,
        인기_캐릭터_강화_앙케이트_스카우트_캐릭터,
    ),
    (
        '인기 캐릭터! 강화 앙케이트 스카우트',
        ScoutType.weapon,
        인기_캐릭터_강화_앙케이트_스카우트_무기,
    ),
]
