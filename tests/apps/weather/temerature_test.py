from yui.apps.weather.temperature import clothes_by_temperature


def test_clothes_by_temperature():
    cases = [
        clothes_by_temperature(5),
        clothes_by_temperature(9),
        clothes_by_temperature(11),
        clothes_by_temperature(16),
        clothes_by_temperature(19),
        clothes_by_temperature(22),
        clothes_by_temperature(26),
        clothes_by_temperature(30),
    ]
    assert len(cases) == len(set(cases))
