from yui.apps.info.d2tz.commons import tz_id_to_names


def test_tz_id_to_names():
    items = [str(x) for x in range(1, 12 + 1)]
    assert len(set(tz_id_to_names(items))) == len(items)
    assert tz_id_to_names(["9", "13"]) == ["동굴"]
    assert tz_id_to_names(["10", "14"]) == ["지하 통로"]
    assert tz_id_to_names(["11", "15"]) == ["구렁"]
    assert tz_id_to_names(["12", "16"]) == ["구덩이"]

    items = [str(x) for x in range(13, 19 + 1)]
    assert len(set(tz_id_to_names(items))) == len(items)
    assert tz_id_to_names(["20"]) == ["잊힌 탑"]
    assert tz_id_to_names(["21", "22", "23", "24", "25"]) == [
        "탑 지하 1층",
        "탑 지하 2층",
        "탑 지하 3층",
        "탑 지하 4층",
        "탑 지하 5층",
    ]
    assert tz_id_to_names(["20", "21", "22", "23", "24", "25"]) == ["잊힌 탑"]

    items = [str(x) for x in range(26, 28 + 1)]
    assert len(set(tz_id_to_names(items))) == len(items)
    assert tz_id_to_names(["29"]) == ["감옥 1층"]
    assert tz_id_to_names(["30"]) == ["감옥 2층"]
    assert tz_id_to_names(["31"]) == ["감옥 3층"]
    assert tz_id_to_names(["29", "30", "31"]) == ["감옥"]

    items = [str(x) for x in range(32, 33 + 1)]
    assert len(set(tz_id_to_names(items))) == len(items)
    assert tz_id_to_names(["34"]) == ["지하 묘지 1층"]
    assert tz_id_to_names(["35"]) == ["지하 묘지 2층"]
    assert tz_id_to_names(["36"]) == ["지하 묘지 3층"]
    assert tz_id_to_names(["37"]) == ["지하 묘지 4층"]
    assert tz_id_to_names(["34", "35", "36", "37"]) == ["지하 묘지"]

    items = [str(x) for x in range(38, 46 + 1)]
    assert len(set(tz_id_to_names(items))) == len(items)
    assert tz_id_to_names(["47"]) == ["루트 골레인 하수도 1층"]
    assert tz_id_to_names(["48"]) == ["루트 골레인 하수도 2층"]
    assert tz_id_to_names(["49"]) == ["루트 골레인 하수도 3층"]
    assert tz_id_to_names(["47", "48", "49"]) == ["루트 골레인 하수도"]
    assert tz_id_to_names(["50"]) == ["하렘 1층"]
    assert tz_id_to_names(["51"]) == ["하렘 2층"]
    assert tz_id_to_names(["50", "51"]) == ["하렘"]
    assert tz_id_to_names(["52"]) == ["궁전 지하 1층"]
    assert tz_id_to_names(["53"]) == ["궁전 지하 2층"]
    assert tz_id_to_names(["54"]) == ["궁전 지하 3층"]
    assert tz_id_to_names(["52", "53", "54"]) == ["궁전 지하"]

    items = [str(x) for x in range(55, 58 + 1)]
    assert len(set(tz_id_to_names(items))) == len(items)
    assert tz_id_to_names(["55", "59"]) == ["바위 무덤"]
    assert tz_id_to_names(["56", "57", "60"]) == ["망자의 전당"]
    assert tz_id_to_names(["58", "61"]) == ["발톱 독사 사원"]

    items = [str(x) for x in range(59, 63 + 1)]
    assert len(set(tz_id_to_names(items))) == len(items)
    assert tz_id_to_names(["62", "63", "64"]) == ["구더기 굴"]
    assert tz_id_to_names(["65"]) == ["고대 토굴"]
    assert tz_id_to_names(["66", "67", "68", "69", "70", "71", "72"]) == [
        "탈 라샤의 무덤",
    ]

    items = [str(x) for x in range(73, 89 + 1)]
    assert len(set(tz_id_to_names(items))) == len(items)
    assert tz_id_to_names(["86", "87", "90"]) == ["습한 구덩이"]
    assert tz_id_to_names(["88", "89", "91"]) == ["약탈자 소굴"]
    assert tz_id_to_names(["92"]) == ["쿠라스트 하수도 1층"]
    assert tz_id_to_names(["93"]) == ["쿠라스트 하수도 2층"]
    assert tz_id_to_names(["92", "93"]) == ["쿠라스트 하수도"]

    items = [str(x) for x in range(94, 99 + 1)]
    assert len(set(tz_id_to_names(items))) == len(items)
    assert tz_id_to_names(["100"]) == ["증오의 억류지 1층"]
    assert tz_id_to_names(["101"]) == ["증오의 억류지 2층"]
    assert tz_id_to_names(["102"]) == ["증오의 억류지 3층"]
    assert tz_id_to_names(["100", "101", "102"]) == ["증오의 억류지"]

    items = [str(x) for x in range(103, 127 + 1)]
    assert len(set(tz_id_to_names(items))) == len(items)
    assert tz_id_to_names(["128"]) == ["세계석 성채 1층"]
    assert tz_id_to_names(["129"]) == ["세계석 성채 2층"]
    assert tz_id_to_names(["130"]) == ["세계석 성채 3층"]
    assert tz_id_to_names(["128", "129", "130"]) == ["세계석 성채"]

    items = [str(x) for x in range(131, 136 + 1)]
    assert len(set(tz_id_to_names(items))) == len(items)
