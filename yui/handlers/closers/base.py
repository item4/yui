import datetime


SCHEDULE = [
    (0 * 60 + 29, '00:30 시작 예정'),
    (0 * 60 + 59, '00:30 -- 00:59 진행중'),
    (1 * 60 + 29, '01:30 시작 예정'),
    (1 * 60 + 59, '01:30 -- 01:59 진행중'),
    (3 * 60 + 59, '종료'),
    (9 * 60 + 59, '10:00 시작 예정'),
    (10 * 60 + 59, '10:00 -- 10:59 진행중'),
    (14 * 60 + 59, '15:00 시작 예정'),
    (15 * 60 + 59, '15:00 -- 15:59 진행중'),
    (17 * 60 + 59, '18:00 시작 예정'),
    (18 * 60 + 59, '18:00 -- 18:59 진행중'),
    (19 * 60 + 59, '20:00 시작 예정'),
    (20 * 60 + 59, '20:00 -- 20:59 진행중'),
    (22 * 60 + 59, '23:00 시작 예정'),
    (23 * 60 + 59, '23:00 -- 23:59 진행중'),
]

ITEM_PURPOSE = {
    '표면': '코어, 모듈 초월',
    '이면': '리시버 초월',
}


def get_next_overflood_info(dt: datetime.datetime):
    weekday = dt.weekday()

    time = dt.hour * 60 + dt.minute

    if time < 4 * 60:
        if weekday == 3:
            return '오버플루드: 휴무'
        type = '표면' if weekday in [1, 5] else '이면'
    else:
        if weekday == 2:
            return '오버플루드: 휴무'
        type = '표면' if weekday in [0, 4, 6] else '이면'

    description = ''
    for end, desc in SCHEDULE:
        if time <= end:
            description = desc
            break

    return f'오버플루드 {type}: {description} / {ITEM_PURPOSE[type]} 재료 획득 가능'
