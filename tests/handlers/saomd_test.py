import pytest

from yui.handlers.saomd import (
    choice_units,
    get_or_create_player,
    get_or_create_player_scout,
    get_record_crystal,
    get_similar_scout_by_title,
    process_release_crystal_and_deck,
    process_step_cost,
    process_weapon_inventory,
)
from yui.models.saomd import (
    CostType,
    Player,
    PlayerScout,
    Scout,
    ScoutType,
    Step,
)
from yui.util import get_count


@pytest.fixture()
def kirito_char_scout():
    scout = Scout()
    scout.title = '검은 검사 키리토 스카우트'
    scout.type = ScoutType.character
    scout.s4_units = [
        '[비터] 키리토',
    ]
    scout.s5_units = [
        '[검은 검사] 키리토',
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
    return scout


@pytest.fixture()
def kirito_weapon_scout():
    scout = Scout()
    scout.title = '검은 검사 키리토 스카우트'
    scout.type = ScoutType.weapon
    scout.s4_units = [
        '어닐 블레이드',
    ]
    scout.s5_units = [
        '일루시데이터',
        '다크리펄서',
    ]
    return scout


@pytest.fixture()
def asuna_char_scout():
    scout = Scout()
    scout.title = '섬광 아스나 스카우트'
    scout.type = ScoutType.character
    scout.s4_units = [
        '[공략의 화신] 아스나',
    ]
    scout.s5_units = [
        '[섬광] 아스나',
    ]
    return scout


@pytest.fixture()
def asuna_weapon_scout():
    scout = Scout()
    scout.title = '섬광 아스나 스카우트'
    scout.type = ScoutType.weapon
    scout.s4_units = [
        '윈드 플뢰레',
    ]
    scout.s5_units = [
        '램번트 라이트',
    ]
    return scout


def test_get_or_create_player(fx_sess):
    assert get_count(fx_sess.query(Player)) == 0

    player1 = get_or_create_player(fx_sess, 'uitem4')

    assert get_count(fx_sess.query(Player)) == 1

    player2 = get_or_create_player(fx_sess, 'uitem4')

    assert get_count(fx_sess.query(Player)) == 1
    assert player1 == player2


def test_get_similar_scout_by_title(
    fx_sess,
    kirito_char_scout,
    kirito_weapon_scout,
    asuna_char_scout,
    asuna_weapon_scout,
):
    with fx_sess.begin():
        fx_sess.add(kirito_char_scout)
        fx_sess.add(kirito_weapon_scout)
        fx_sess.add(asuna_char_scout)
        fx_sess.add(asuna_weapon_scout)

    scout = get_similar_scout_by_title(fx_sess, ScoutType.character, '키리토')
    assert scout == kirito_char_scout

    scout = get_similar_scout_by_title(fx_sess, ScoutType.character, '아스나')
    assert scout == asuna_char_scout

    scout = get_similar_scout_by_title(fx_sess, ScoutType.weapon, '키리토')
    assert scout == kirito_weapon_scout

    scout = get_similar_scout_by_title(fx_sess, ScoutType.weapon, '아스나')
    assert scout == asuna_weapon_scout


def test_get_or_create_player_scout(fx_sess, kirito_char_scout):
    player = get_or_create_player(fx_sess, 'uitem4')

    step = Step()
    step.scout = kirito_char_scout
    step.name = '일반'
    step.cost = 250
    step.cost_type = CostType.diamond
    step.is_first = True

    with fx_sess.begin():
        fx_sess.add(kirito_char_scout)
        fx_sess.add(step)

    assert get_count(fx_sess.query(PlayerScout)) == 0

    ps1 = get_or_create_player_scout(fx_sess, player, kirito_char_scout)

    assert get_count(fx_sess.query(PlayerScout)) == 1
    assert ps1.player == player
    assert ps1.scout == kirito_char_scout
    assert ps1.next_step == step

    ps2 = get_or_create_player_scout(fx_sess, player, kirito_char_scout)

    assert get_count(fx_sess.query(PlayerScout)) == 1
    assert ps1 == ps2


def test_choice_units(fx_sess, kirito_char_scout, kirito_weapon_scout):
    player = get_or_create_player(fx_sess, 'uitem4')

    cstep = Step()
    cstep.scout = kirito_char_scout
    cstep.name = 'Step 1'
    cstep.is_first = True
    cstep.cost = 250
    cstep.cost_type = CostType.diamond
    cstep.s5_fixed = 1
    cstep.s4_fixed = 1
    cstep.s5_chance = 0.2
    cstep.s4_chance = 0.5

    wstep = Step()
    wstep.scout = kirito_weapon_scout
    wstep.name = 'Step 1'
    wstep.is_first = True
    wstep.cost = 150
    wstep.cost_type = CostType.diamond
    wstep.s5_fixed = 1
    wstep.s4_fixed = 1
    wstep.s5_chance = 0.2
    wstep.s4_chance = 0.5

    with fx_sess.begin():
        fx_sess.add(kirito_char_scout)
        fx_sess.add(kirito_weapon_scout)
        fx_sess.add(cstep)
        fx_sess.add(wstep)

    ps = get_or_create_player_scout(fx_sess, player, kirito_char_scout)
    step = ps.next_step

    s3_units = [
        '3성 키리토',
        '3성 아스나',
        '3성 클라인',
        '3성 에길',
    ]
    s2_units = [
        '2성 키리토',
        '2성 아스나',
        '2성 클라인',
        '2성 에길',
    ]

    chars = choice_units(kirito_char_scout, step, s3_units, s2_units, 100)
    assert chars == [
        (5, '[검은 검사] 키리토'),
        (5, '[검은 검사] 키리토'),
        (4, '[비터] 키리토'),
        (4, '[비터] 키리토'),
        (4, '[비터] 키리토'),
        (4, '[비터] 키리토'),
        (4, '[비터] 키리토'),
        (3, '3성 클라인'),
        (3, '3성 클라인'),
        (3, '3성 아스나'),
        (2, '2성 아스나'),
    ]

    ps = get_or_create_player_scout(fx_sess, player, kirito_weapon_scout)
    step = ps.next_step

    s3_units = [
        '3성 한손검',
        '3성 양손검',
        '3성 세검',
        '3성 둔기',
    ]
    s2_units = [
        '2성 한손검',
        '2성 양손검',
        '2성 세검',
        '2성 둔기',
    ]

    weapons = choice_units(kirito_weapon_scout, step, s3_units, s2_units, 100)
    assert weapons == [
        (5, '일루시데이터'),
        (4, '어닐 블레이드'),
        (4, '어닐 블레이드'),
        (3, '3성 세검'),
        (4, '어닐 블레이드'),
        (4, '어닐 블레이드'),
        (3, '3성 세검'),
        (5, '일루시데이터'),
        (4, '어닐 블레이드'),
        (3, '3성 양손검'),
        (2, '2성 양손검'),
    ]


def test_get_record_crystal(fx_sess, kirito_char_scout, kirito_weapon_scout):
    with fx_sess.begin():
        fx_sess.add(kirito_char_scout)
        fx_sess.add(kirito_weapon_scout)

    assert get_record_crystal(kirito_weapon_scout, 100) == 0
    assert get_record_crystal(kirito_char_scout, 100) == 2


def test_process_release_crystal_and_deck(fx_sess):
    player = get_or_create_player(fx_sess, 'uitem4')

    chars = [
        (5, '[검은 검사] 키리토'),
        (5, '[검은 검사] 키리토'),
        (4, '[비터] 키리토'),
        (4, '[비터] 키리토'),
        (4, '[비터] 키리토'),
        (4, '[비터] 키리토'),
        (4, '[비터] 키리토'),
        (3, '3성 클라인'),
        (3, '3성 클라인'),
        (3, '3성 아스나'),
        (2, '2성 아스나'),
    ]

    results, release_crystal = process_release_crystal_and_deck(player, chars)
    assert results == [
        '★5 *[검은 검사] 키리토*',
        '★5 ~[검은 검사] 키리토~ → 해방결정 100개',
        '★4 *[비터] 키리토*',
        '★4 ~[비터] 키리토~ → 해방결정 50개',
        '★4 ~[비터] 키리토~ → 해방결정 50개',
        '★4 ~[비터] 키리토~ → 해방결정 50개',
        '★4 ~[비터] 키리토~ → 해방결정 50개',
        '★3 3성 클라인',
        '★3 ~3성 클라인~ → 해방결정 2개',
        '★3 3성 아스나',
        '★2 2성 아스나',
    ]
    assert release_crystal == 302

    assert player.characters['[검은 검사] 키리토'] == {'rarity': 5}
    assert player.characters['[비터] 키리토'] == {'rarity': 4}
    assert player.characters['3성 클라인'] == {'rarity': 3}
    assert player.characters['3성 아스나'] == {'rarity': 3}
    assert player.characters['2성 아스나'] == {'rarity': 2}
    assert player.release_crystal == 302

    chars2 = [
        (5, '[검은 검사] 키리토'),
        (5, '[검은 검사] 키리토'),
        (5, '[비터] 키리토'),
        (5, '[비터] 키리토'),
        (5, '[비터] 키리토'),
        (5, '[비터] 키리토'),
        (5, '[비터] 키리토'),
        (3, '3성 클라인'),
        (3, '3성 클라인'),
        (3, '3성 아스나'),
        (2, '2성 아스나'),
    ]

    results, release_crystal = process_release_crystal_and_deck(player, chars2)
    assert results == [
        '★5 ~[검은 검사] 키리토~ → 해방결정 100개',
        '★5 ~[검은 검사] 키리토~ → 해방결정 100개',
        '★4→5 *[비터] 키리토* + 해방결정 50개',
        '★5 ~[비터] 키리토~ → 해방결정 100개',
        '★5 ~[비터] 키리토~ → 해방결정 100개',
        '★5 ~[비터] 키리토~ → 해방결정 100개',
        '★5 ~[비터] 키리토~ → 해방결정 100개',
        '★3 ~3성 클라인~ → 해방결정 2개',
        '★3 ~3성 클라인~ → 해방결정 2개',
        '★3 ~3성 아스나~ → 해방결정 2개',
        '★2 ~2성 아스나~ → 해방결정 1개',
    ]
    assert release_crystal == 657

    assert player.characters['[검은 검사] 키리토'] == {'rarity': 5}
    assert player.characters['[비터] 키리토'] == {'rarity': 5}
    assert player.characters['3성 클라인'] == {'rarity': 3}
    assert player.characters['3성 아스나'] == {'rarity': 3}
    assert player.characters['2성 아스나'] == {'rarity': 2}
    assert player.release_crystal == 302+657


def test_process_weapon_inventory(fx_sess):
    player = get_or_create_player(fx_sess, 'uitem4')

    weapons = [
        (5, '일루시데이터'),
        (4, '어닐 블레이드'),
        (4, '어닐 블레이드'),
        (3, '3성 세검'),
        (4, '어닐 블레이드'),
        (4, '어닐 블레이드'),
        (3, '3성 세검'),
        (5, '일루시데이터'),
        (4, '어닐 블레이드'),
        (3, '3성 양손검'),
        (2, '2성 양손검'),
    ]

    results = process_weapon_inventory(player, weapons)

    assert results == [
        '★5 *일루시데이터*',
        '★4 *어닐 블레이드*',
        '★4 *어닐 블레이드*',
        '★3 3성 세검',
        '★4 *어닐 블레이드*',
        '★4 *어닐 블레이드*',
        '★3 3성 세검',
        '★5 *일루시데이터*',
        '★4 *어닐 블레이드*',
        '★3 3성 양손검',
        '★2 2성 양손검',
    ]

    assert player.weapons['5']['일루시데이터'] == {'count': 2}
    assert player.weapons['4']['어닐 블레이드'] == {'count': 5}
    assert player.weapons['3']['3성 세검'] == {'count': 2}
    assert player.weapons['3']['3성 양손검'] == {'count': 1}
    assert player.weapons['2']['2성 양손검'] == {'count': 1}

    results = process_weapon_inventory(player, weapons)

    assert results == [
        '★5 *일루시데이터*',
        '★4 *어닐 블레이드*',
        '★4 *어닐 블레이드*',
        '★3 3성 세검',
        '★4 *어닐 블레이드*',
        '★4 *어닐 블레이드*',
        '★3 3성 세검',
        '★5 *일루시데이터*',
        '★4 *어닐 블레이드*',
        '★3 3성 양손검',
        '★2 2성 양손검',
    ]

    assert player.weapons['5']['일루시데이터'] == {'count': 4}
    assert player.weapons['4']['어닐 블레이드'] == {'count': 10}
    assert player.weapons['3']['3성 세검'] == {'count': 4}
    assert player.weapons['3']['3성 양손검'] == {'count': 2}
    assert player.weapons['2']['2성 양손검'] == {'count': 2}


def test_process_step_cost(
    fx_sess,
    kirito_char_scout,
    kirito_weapon_scout,
    asuna_char_scout,
    asuna_weapon_scout,
):
    player = get_or_create_player(fx_sess, 'uitem4')

    cstep = Step()
    cstep.scout = kirito_char_scout
    cstep.name = 'Step 1'
    cstep.is_first = True
    cstep.cost = 250
    cstep.cost_type = CostType.diamond
    cstep.s5_fixed = 1
    cstep.s4_fixed = 1
    cstep.s5_chance = 0.2
    cstep.s4_chance = 0.5

    wstep = Step()
    wstep.scout = kirito_weapon_scout
    wstep.name = 'Step 1'
    wstep.is_first = True
    wstep.cost = 150
    wstep.cost_type = CostType.diamond
    wstep.s5_fixed = 1
    wstep.s4_fixed = 1
    wstep.s5_chance = 0.2
    wstep.s4_chance = 0.5

    cstep2 = Step()
    cstep2.scout = asuna_char_scout
    cstep2.name = 'Step 1'
    cstep2.is_first = True
    cstep2.cost = 10
    cstep2.cost_type = CostType.record_crystal
    cstep2.s5_fixed = 1
    cstep2.s4_fixed = 1
    cstep2.s5_chance = 0.2
    cstep2.s4_chance = 0.5

    wstep2 = Step()
    wstep2.scout = asuna_weapon_scout
    wstep2.name = 'Step 1'
    wstep.is_first = True
    wstep2.cost = 5
    wstep2.cost_type = CostType.record_crystal
    wstep2.s5_fixed = 1
    wstep2.s4_fixed = 1
    wstep2.s5_chance = 0.2
    wstep2.s4_chance = 0.5

    with fx_sess.begin():
        fx_sess.add(kirito_char_scout)
        fx_sess.add(kirito_weapon_scout)
        fx_sess.add(cstep)
        fx_sess.add(wstep)

    process_step_cost(player, kirito_weapon_scout, wstep, 0)

    assert player.used_diamond == 150
    assert player.record_crystals == {}

    process_step_cost(player, kirito_char_scout, cstep, 5)

    assert player.used_diamond == 400
    assert player.record_crystals['검은 검사 키리토 스카우트 기록결정'] == 5

    process_step_cost(player, kirito_char_scout, cstep, 3)

    assert player.used_diamond == 650
    assert player.record_crystals['검은 검사 키리토 스카우트 기록결정'] == 8

    process_step_cost(player, asuna_weapon_scout, wstep2, 0)

    assert player.used_diamond == 650
    assert player.record_crystals['검은 검사 키리토 스카우트 기록결정'] == 8
    assert player.record_crystals['섬광 아스나 스카우트 기록결정'] == -5

    process_step_cost(player, asuna_char_scout, cstep2, 0)

    assert player.used_diamond == 650
    assert player.record_crystals['검은 검사 키리토 스카우트 기록결정'] == 8
    assert player.record_crystals['섬광 아스나 스카우트 기록결정'] == -15
