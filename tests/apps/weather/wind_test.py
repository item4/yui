import pytest

from yui.apps.weather.wind import degree_to_direction


@pytest.mark.parametrize(
    ("degree", "direction"),
    [
        (0, "N"),
        (22.5, "NNE"),
        (45, "NE"),
        (67.5, "ENE"),
        (90, "E"),
        (112.5, "ESE"),
        (135, "SE"),
        (157.5, "SSE"),
        (180, "S"),
        (202.5, "SSW"),
        (225, "SW"),
        (247.5, "WSW"),
        (270, "W"),
        (292.5, "WNW"),
        (315, "NW"),
        (337.5, "NNW"),
    ],
)
def test_degree_to_direction(degree, direction):
    assert direction == degree_to_direction(degree)
