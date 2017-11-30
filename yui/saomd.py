import enum
from typing import List, Tuple

from sqlalchemy.orm.exc import NoResultFound

from .models.saomd import CostType, PlayerScout, Scout, ScoutType, Step


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

RECORD_CRYSTAL_DEFAULT: List[Tuple[int, float]] = [
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


class MigrationStatus(enum.Enum):

    passed = 0
    create = 1
    update = 2


class ScoutMigration:

    version: int = 0
    title: str = None
    type: ScoutType = None

    def patch(self, sess) -> MigrationStatus:
        try:
            scout = sess.query(Scout).filter_by(
                title=self.title,
                type=self.type,
            ).one()
        except NoResultFound:
            self.create(sess)
            return MigrationStatus.create

        if self.version != scout.version:
            self.delete(sess)
            self.create(sess)
            return MigrationStatus.update

        return MigrationStatus.passed

    def create(self, sess):
        raise NotImplementedError()

    def create_base_scout(self) -> Scout:
        scout = Scout()
        scout.version = self.version
        scout.type = self.type
        scout.title = self.title
        return scout

    def delete(self, sess):
        scout = sess.query(Scout).filter_by(
            title=self.title,
            type=self.type,
        ).one()
        sess.query(PlayerScout).filter_by(scout=scout).delete()
        sess.query(Step).filter_by(scout=scout).delete()

        with sess.begin():
            sess.delete(scout)

    def __str__(self) -> str:
        return f'ScoutMigration({self.title!r}, {self.type!r})'


class 두근두근_수증기와_미인의_온천_캐릭터(ScoutMigration):

    version = 1
    title = '두근두근 수증기와 미인의 온천 스카우트'
    type = ScoutType.character

    def create(self, sess):
        scout = self.create_base_scout()
        scout.s4_units = FOUR_STAR_CHARACTERS
        scout.s5_units = [
            '[고운 피부의 여신] 아스나',
            '[되돌아보는 미인] 시논',
            '[비밀탕의 미인] 리파',
            '[단풍탕의 미인] 시리카',
        ]
        scout.record_crystal = RECORD_CRYSTAL_DEFAULT

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


class 두근두근_수증기와_미인의_온천_무기(ScoutMigration):

    version = 1
    title = '두근두근 수증기와 미인의 온천 스카우트'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
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


class 우정의_바톤_가을_대운동회_스카우트_캐릭터(ScoutMigration):

    version = 1
    title = '우정의 바톤! 가을 대운동회 스카우트'
    type = ScoutType.character

    def create(self, sess):
        scout = self.create_base_scout()
        scout.s4_units = FOUR_STAR_CHARACTERS
        scout.s5_units = [
            '[화려한 골] 아스나',
            '[일등상을 목표로] 유이',
            '[빛나는 땀과 청춘의 빛] 리파',
            '[네버 기브업] 리즈벳',
        ]
        scout.record_crystal = RECORD_CRYSTAL_DEFAULT

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


class 우정의_바톤_가을_대운동회_스카우트_무기(ScoutMigration):

    version = 1
    title = '우정의 바톤! 가을 대운동회 스카우트'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
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


class 일주년기념_5성진화_앙케이트_스카우트_캐릭터(ScoutMigration):

    version = 1
    title = '1주년기념 5성진화 앙케이트 스카우트'
    type = ScoutType.character

    def create(self, sess):
        scout = self.create_base_scout()
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


class 일주년기념_5성진화_앙케이트_스카우트_무기(ScoutMigration):

    version = 1
    title = '1주년기념 5성진화 앙케이트 스카우트'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
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


class 키리토_아스나_결혼기념일_스카우트_캐릭터(ScoutMigration):

    version = 1
    title = '키리토 & 아스나 결혼기념일 스카우트'
    type = ScoutType.character

    def create(self, sess):
        scout = self.create_base_scout()
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


class 환영의_탄환이_쌓는_두사람의_인연_스카우트_캐릭터(ScoutMigration):

    version = 1
    title = '환영의 탄환이 쌓는 두사람의 인연 스카우트'
    type = ScoutType.character

    def create(self, sess):
        scout = self.create_base_scout()
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


class 환영의_탄환이_쌓는_두사람의_인연_스카우트_무기(ScoutMigration):

    version = 1
    title = '환영의 탄환이 쌓는 두사람의 인연 스카우트'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
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


class 장난스런_할로윈_나이트_스카우트_캐릭터(ScoutMigration):

    version = 1
    title = '장난스런 할로윈 나이트 스카우트'
    type = ScoutType.character

    def create(self, sess):
        scout = self.create_base_scout()
        scout.s4_units = FOUR_STAR_CHARACTERS
        scout.s5_units = [
            '[사랑에 빠진 뱀파이어] 유우키',
            '[상냥한 몬스터] 리파',
            '[스파이더 위치] 시논',
            '[새끼고양이 마녀] 시리카',
        ]
        scout.record_crystal = RECORD_CRYSTAL_DEFAULT

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


class 장난스런_할로윈_나이트_스카우트_무기(ScoutMigration):

    version = 1
    title = '장난스런 할로윈 나이트 스카우트'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
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


class 달밤의_할로윈_퍼레이드_스카우트_캐릭터(ScoutMigration):

    version = 1
    title = '달밤의 할로윈 퍼레이드 스카우트'
    type = ScoutType.character

    def create(self, sess):
        scout = self.create_base_scout()
        scout.s4_units = FOUR_STAR_CHARACTERS
        scout.s5_units = [
            '[생피를 바쳐라] 키리토',
            '[달밤의 포효] 유지오',
            '[한밤중의 유혹] 아스나',
            '[호박의 기사] 앨리스',
        ]
        scout.record_crystal = RECORD_CRYSTAL_DEFAULT

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


class 달밤의_할로윈_퍼레이드_스카우트_무기(ScoutMigration):

    version = 1
    title = '달밤의 할로윈 퍼레이드 스카우트'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
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


class 남자들의_광연_스카우트_캐릭터(ScoutMigration):

    version = 1
    title = '남자들의 광연 스카우트'
    type = ScoutType.character

    def create(self, sess):
        scout = self.create_base_scout()
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


class 남자들의_광연_스카우트_무기(ScoutMigration):

    version = 1
    title = '남자들의 광연 스카우트'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
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


class 지나가는_시간과_우정의_기억_스카우트_캐릭터(ScoutMigration):

    version = 1
    title = '지나가는 시간과 우정의 기억 스카우트'
    type = ScoutType.character

    def create(self, sess):
        scout = self.create_base_scout()
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


class 지나가는_시간과_우정의_기억_스카우트_무기(ScoutMigration):

    version = 1
    title = '지나가는 시간과 우정의 기억 스카우트'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
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


class 돌아가는_세계에_겁쳐진_검_스카우트_캐릭터(ScoutMigration):

    version = 1
    title = '돌아가는 세계에 겁쳐진 검 스카우트'
    type = ScoutType.character

    def create(self, sess):
        scout = self.create_base_scout()
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


class 돌아가는_세계에_겁쳐진_검_스카우트_무기(ScoutMigration):

    version = 1
    title = '돌아가는 세계에 겁쳐진 검 스카우트'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
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


class 신뢰의_증거_운명의_인연_스카우트_캐릭터(ScoutMigration):

    version = 1
    title = '신뢰의 증거 운명의 인연 스카우트'
    type = ScoutType.character

    def create(self, sess):
        scout = self.create_base_scout()
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


class 신뢰의_증거_운명의_인연_스카우트_무기(ScoutMigration):

    version = 1
    title = '신뢰의 증거 운명의 인연 스카우트'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
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


class 일주년_카운트다운_앙케이트_스카우트_캐릭터(ScoutMigration):

    version = 1
    title = '1주년 카운트다운! 앙케이트 스카우트'
    type = ScoutType.character

    def create(self, sess):
        scout = self.create_base_scout()
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


class 일주년_카운트다운_앙케이트_스카우트_무기(ScoutMigration):

    version = 1
    title = '1주년 카운트다운! 앙케이트 스카우트'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
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


class 폭풍에_휘날리는_해적기_스카우트_캐릭터(ScoutMigration):

    version = 1
    title = '폭풍에 휘날리는 해적기 스카우트'
    type = ScoutType.character

    def create(self, sess):
        scout = self.create_base_scout()
        scout.s4_units = [
            '[긍지 높은 선장] 키리토',
            '[갑판을 채색하는 부선장] 아스나',
            '[감시대의 명저격수] 시논',
            '[쾌활한 항해사] 리파',
            '[직감의 조타수] 유우키',
        ]
        scout.record_crystal = RECORD_CRYSTAL_DEFAULT

        step1 = Step()
        step1.scout = scout
        step1.name = '일반'
        step1.is_first = True
        step1.cost = 250
        step1.cost_type = CostType.diamond

        with sess.begin():
            sess.add(scout)
            sess.add(step1)


class 폭풍에_휘날리는_해적기_스카우트_무기(ScoutMigration):

    version = 1
    title = '폭풍에 휘날리는 해적기 스카우트'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
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


class 여름밤의_축제_스카우트_캐릭터(ScoutMigration):

    version = 1
    title = '여름밤의 축제 스카우트'
    type = ScoutType.character

    def create(self, sess):
        scout = self.create_base_scout()
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


class 여름밤의_축제_스카우트_무기(ScoutMigration):

    version = 1
    title = '여름밤의 축제 스카우트'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
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


class 매력분출_여름빛_소녀_스카우트_캐릭터(ScoutMigration):

    version = 1
    title = '매력분출 여름빛 소녀 스카우트'
    type = ScoutType.character

    def create(self, sess):
        scout = self.create_base_scout()
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


class 매력분출_여름빛_소녀_스카우트_무기(ScoutMigration):

    version = 1
    title = '매력분출 여름빛 소녀 스카우트'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
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


class 유카타_NIGHT_스카우트_캐릭터(ScoutMigration):

    version = 1
    title = '유카타 NIGHT 스카우트'
    type = ScoutType.character

    def create(self, sess):
        scout = self.create_base_scout()
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


class 유카타_NIGHT_스카우트_무기(ScoutMigration):

    version = 2
    title = '유카타 NIGHT 스카우트'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
        scout.s4_units = [
            '흐르는 버들',
            '우아한 문장의 조율 x 우아한 문장의 연주',
            '팔중요란',
            '피어나는 아침 안개',
            '싸리 안개',
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


class 인기_캐릭터_강화_앙케이트_스카우트_캐릭터(ScoutMigration):

    version = 1
    title = '인기 캐릭터! 강화 앙케이트 스카우트'
    type = ScoutType.character

    def create(self, sess):
        scout = self.create_base_scout()
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


class 인기_캐릭터_강화_앙케이트_스카우트_무기(ScoutMigration):

    version = 1
    title = '인기 캐릭터! 강화 앙케이트 스카우트'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
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


class 한여름의_트로피컬_드림_스카우트_캐릭터(ScoutMigration):

    version = 1
    title = '한여름의 트로피컬★드림 스카우트'
    type = ScoutType.character

    def create(self, sess):
        scout = self.create_base_scout()
        scout.s4_units = [
            '[해변의 남국소년] 키리토',
            '[여름의 연인] 아스나',
            '[생기발랄 여름빛 소녀] 유우키',
            '[파도 타는 소년] 유지오',
            '[볼 빨간 여름의 프린세스] 앨리스',
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


class 한여름의_트로피컬_드림_스카우트_무기(ScoutMigration):

    version = 2
    title = '한여름의 트로피컬★드림 스카우트'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
        scout.s4_units = [
            '앵커즈 소드',
            '다크 팜 소드 x 덴파레 슬라이서',
            '하이비스커스 커터',
            '비치 스팅거',
            '시호스 세이버',
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


class 가속하는_리얼_스카우트_캐릭터(ScoutMigration):

    version = 1
    title = '가속하는 리얼 스카우트'
    type = ScoutType.character

    def create(self, sess):
        scout = self.create_base_scout()
        scout.s4_units = [
            '[일어서는 영웅] 키리토',
            '[맞서는 결의] 아스나',
            '[어그멘트 테이머] 시리카',
            '[이피션트 스미스] 리즈벳',
            '[프로그레시브 거너] 시논',
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


class 가속하는_리얼_스카우트_무기(ScoutMigration):

    version = 1
    title = '가속하는 리얼 스카우트'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
        scout.s4_units = [
            '히로익 프로미스',
            '컬리지',
            '에레타',
            '엣지 오브 리펜트',
            '어드밴서',
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


class 홍련의_트럼프_스카우트_캐릭터(ScoutMigration):

    version = 1
    title = '홍련의 트럼프 스카우트'
    type = ScoutType.character

    def create(self, sess):
        scout = self.create_base_scout()
        scout.s4_units = FOUR_STAR_CHARACTERS
        scout.s5_units = [
            '[포커 킹] 키리토',
            '[레드하트 퀸] 아스나',
            '[버니 에이스] 유우키',
            '[와일드 조커] 시논',
        ]
        scout.record_crystal = RECORD_CRYSTAL_DEFAULT

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


class 홍련의_트럼프_스카우트_무기(ScoutMigration):

    version = 1
    title = '홍련의 트럼프 스카우트'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
        scout.s4_units = [
            '버닝 하트',
            '러시안루트 x 저지먼트 느와르',
            '잭팟 스파다',
            '데스티니 롯소',
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


class SAO_게임_클리어_기념_5성진화_앙케이트_스카우트_캐릭터(ScoutMigration):

    version = 1
    title = 'SAO 게임 클리어 기념 5성진화 앙케이트 스카우트'
    type = ScoutType.character

    def create(self, sess):
        scout = self.create_base_scout()
        scout.s4_units = list(set(FOUR_STAR_CHARACTERS) - {
            '[천승의 무희] 유우키',
            '[춤추듯 지는 벚꽃] 레인',
            '[유월의 금목서] 앨리스',
            '[마음의 섬광] 아스나',
        })
        scout.s5_units = [
            '[천승의 무희] 유우키',
            '[춤추듯 지는 벚꽃] 레인',
            '[유월의 금목서] 앨리스',
            '[마음의 섬광] 아스나',
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


class SAO_게임_클리어_기념_5성진화_앙케이트_스카우트_무기(ScoutMigration):

    version = 1
    title = 'SAO 게임 클리어 기념 5성진화 앙케이트 스카우트'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
        scout.s4_units = [
            '텐구의 쌍검+1x2',
            '우아한 문장의 조율x우아한 문장의 연주+1',
            '준 블레이드+1',
            '컬리지+1',
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


class 한손_몽둥이_강화_기념_5성_진화_스카우트_캐릭터(ScoutMigration):

    version = 1
    title = '한손 몽둥이 강화 기념 5성 진화 스카우트'
    type = ScoutType.character

    def create(self, sess):
        scout = self.create_base_scout()
        scout.s4_units = list(set(FOUR_STAR_CHARACTERS) - {
            '[부케 토스 점프] 유우키',
            '[이피션트 스미스] 리즈벳',
            '[작은 연인] 시리카',
            '[벚꽃 필 무렵의 소녀] 유이',
        })
        scout.s5_units = [
            '[부케 토스 점프] 유우키',
            '[이피션트 스미스] 리즈벳',
            '[작은 연인] 시리카',
            '[벚꽃 필 무렵의 소녀] 유이',
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


class 한손_몽둥이_강화_기념_5성_진화_스카우트_무기(ScoutMigration):

    version = 2
    title = '한손 몽둥이 강화 기념 5성 진화 스카우트'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
        scout.s4_units = [
            '어린 벚꽃의 헤비 스태프+1',
            '에레터+1',
            '퍼펙트 러버+1',
            '프로미스 하트+1',
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


class 블랙_프라이데이_4성무기_확정_스카우트_한손검(ScoutMigration):

    version = 2
    title = '블랙 프라이데이 4성무기 확정 스카우트 - 한손검'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
        scout.s4_units = [
            '히로익 프로미스',
            '엔젤 클레이모어',
            '종언의 용인',
            '청장미의 검',
            '금목서의 검',
            '원스 어픈 어 타임',
            '벚꽃 태도',
            '티타임 세이버',
            '알아리에스 그라디우스',
            '준 블레이드',
            '레일웨이 소드',
            '피셔즈 소드',
            '앵커즈 소드',
            '풍차의 신검',
            '시호스 세이버',
            '졸리 로저 사벨',
            '영겁불후의 검',
            '영구빙괴의 검',
            '철운석의 검',
            '명도 아카츠키',
            '이레이디케이트 세이버',
            '파라과스 블레이드',
            '샤이닝 글라디우스',
            '글로리어스 블레이드',
        ]

        step1 = Step()
        step1.scout = scout
        step1.name = '1회 한정'
        step1.is_first = True
        step1.cost = 150
        step1.cost_type = CostType.diamond
        step1.s4_fixed = 1

        with sess.begin():
            sess.add(scout)
            sess.add(step1)


class 블랙_프라이데이_4성무기_확정_스카우트_세검(ScoutMigration):

    version = 2
    title = '블랙 프라이데이 4성무기 확정 스카우트 - 세검'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
        scout.s4_units = [
            '컬리지',
            '옐로우 망고슈',
            '인과의 법칙검',
            '펄 버터플라이',
            '크레스티드 에스파다',
            '제미니 그라디우스',
            '이터널 심포니',
            '인젝션 레이피어',
            '비치 스팅거',
            '선녀의 성검',
            '흐르는 버들',
            '천신의 폭풍검',
            '릴리 망고슈',
            '오션 에스파다',
            '아틀란티스 소드',
            '다즐링 블링크',
            '소드 댄스 에스파다',
            '빅토리 플뢰레',
        ]

        step1 = Step()
        step1.scout = scout
        step1.name = '1회 한정'
        step1.is_first = True
        step1.cost = 150
        step1.cost_type = CostType.diamond
        step1.s4_fixed = 1

        with sess.begin():
            sess.add(scout)
            sess.add(step1)


class 블랙_프라이데이_4성무기_확정_스카우트_쌍검(ScoutMigration):

    version = 2
    title = '블랙 프라이데이 4성무기 확정 스카우트 - 쌍검'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
        scout.s4_units = [
            '다크 팜 소드 x 덴파레 슬라이서',
            '텐구의 쌍검x2',
            '우아한 문장의 조율 x 우아한 문장의 연주',
            '인쇼어소드 x 오프쇼어소드',
            '인라이트먼트 x 섀도우 엘리미네이터',
            '하이드런지아 소드x2',
        ]

        step1 = Step()
        step1.scout = scout
        step1.name = '1회 한정'
        step1.is_first = True
        step1.cost = 150
        step1.cost_type = CostType.diamond
        step1.s4_fixed = 1

        with sess.begin():
            sess.add(scout)
            sess.add(step1)


class 블랙_프라이데이_4성무기_확정_스카우트_단검(ScoutMigration):

    version = 2
    title = '블랙 프라이데이 4성무기 확정 스카우트 - 단검'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
        scout.s4_units = [
            '엣지 오브 리펜트',
            '릴팅 호른',
            '찰나의 요도',
            '머메이드 송',
            '슈가 쿠크리',
            '위싱 부케',
            '에어플레인 대거',
            '스플래쉬 대거',
            '하이비스커스 커터',
            '맹세의 검',
            '싸리 안개',
            '선플라워 엣지',
            '파이어릿 대거',
            '카른웨난',
            '챔피언 대거',
            '퍼플 스타 바셀라드',
        ]

        step1 = Step()
        step1.scout = scout
        step1.name = '1회 한정'
        step1.is_first = True
        step1.cost = 150
        step1.cost_type = CostType.diamond
        step1.s4_fixed = 1

        with sess.begin():
            sess.add(scout)
            sess.add(step1)


class 블랙_프라이데이_4성무기_확정_스카우트_한손몽둥이(ScoutMigration):

    version = 2
    title = '블랙 프라이데이 4성무기 확정 스카우트 - 한손몽둥이(둔기)'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
        scout.s4_units = [
            '에레터',
            '트월링 메이스',
            '농락하는 연꽃',
            '퍼펙트 러버',
            '어린 벚꽃의 헤비 스태프',
            '스매시 브러쉬',
            '프로미스 하트',
            '듀 클럽 파페',
            '콕스 해머',
            '비치 버스터',
            '플라네타리 메이스',
            '그레이트 넘버',
            '글로리어스 마이크',
        ]

        step1 = Step()
        step1.scout = scout
        step1.name = '1회 한정'
        step1.is_first = True
        step1.cost = 150
        step1.cost_type = CostType.diamond
        step1.s4_fixed = 1

        with sess.begin():
            sess.add(scout)
            sess.add(step1)


class 블랙_프라이데이_4성무기_확정_스카우트_총(ScoutMigration):

    version = 2
    title = '블랙 프라이데이 4성무기 확정 스카우트 - 총'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
        scout.s4_units = [
            '어드밴서',
            '애플 오브 페이트',
            '폴리스 샷',
            '피어나는 아침 안개',
            '마린 샷',
            '하버 라이플',
        ]

        step1 = Step()
        step1.scout = scout
        step1.name = '1회 한정'
        step1.is_first = True
        step1.cost = 150
        step1.cost_type = CostType.diamond
        step1.s4_fixed = 1

        with sess.begin():
            sess.add(scout)
            sess.add(step1)


class 블랙_프라이데이_4성무기_확정_스카우트_활(ScoutMigration):

    version = 2
    title = '블랙 프라이데이 4성무기 확정 스카우트 - 활'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
        scout.s4_units = [
            '러블리 파리티안',
            '흩날리는 벚꽃의 장궁',
            '스위티 슈터',
            '키스 오브 큐피드',
            '구시스나우탈',
            '기우사의 장궁',
            '코발트 트리스탄',
        ]

        step1 = Step()
        step1.scout = scout
        step1.name = '1회 한정'
        step1.is_first = True
        step1.cost = 150
        step1.cost_type = CostType.diamond
        step1.s4_fixed = 1

        with sess.begin():
            sess.add(scout)
            sess.add(step1)


class 블랙_프라이데이_4성무기_확정_스카우트_지팡이(ScoutMigration):

    version = 2
    title = '블랙 프라이데이 4성무기 확정 스카우트 - 지팡이'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
        scout.s4_units = [
            '윤회의 여섯 꽃잎'
            '레드 울프 버스터'
            '캔들 스틱'
            '비너스 하트',
        ]

        step1 = Step()
        step1.scout = scout
        step1.name = '1회 한정'
        step1.is_first = True
        step1.cost = 150
        step1.cost_type = CostType.diamond
        step1.s4_fixed = 1

        with sess.begin():
            sess.add(scout)
            sess.add(step1)


class 블랙_프라이데이_4성무기_확정_스카우트_창(ScoutMigration):

    version = 2
    title = '블랙 프라이데이 4성무기 확정 스카우트 - 창'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
        scout.s4_units = [
            '리브라의 창',
            '레오의 창',
            '위즈덤 스피어',
            '팔중요란',
            '보구의 신창',
            '아일랜드 스피어',
            '위너즈 스피어',
        ]

        step1 = Step()
        step1.scout = scout
        step1.name = '1회 한정'
        step1.is_first = True
        step1.cost = 150
        step1.cost_type = CostType.diamond
        step1.s4_fixed = 1

        with sess.begin():
            sess.add(scout)
            sess.add(step1)


class 화이트_크리스마스가_연주하는_음색_스카우트_캐릭터(ScoutMigration):

    version = 1
    title = '화이트 크리스마스가 연주하는 음색 스카우트'
    type = ScoutType.character

    def create(self, sess):
        scout = self.create_base_scout()
        scout.s4_units = FOUR_STAR_CHARACTERS
        scout.s5_units = [
            '[산타의 선물] 아스나',
            '[눈내리는 밤의 방문자] 리파',
            '[크리스마스의 울림] 앨리스',
            '[성급한 순록] 유지오',
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


class 화이트_크리스마스가_연주하는_음색_스카우트_무기(ScoutMigration):

    version = 1
    title = '화이트 크리스마스가 연주하는 음색 스카우트'
    type = ScoutType.weapon

    def create(self, sess):
        scout = self.create_base_scout()
        scout.s4_units = [
            '프레젠트 포 유',
            '리스 온 침니',
            '레인디어 혼',
            '트윙클 이브',
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
