from typing import Final

DIRECTION_NAME: Final[list[str]] = [
    "N",
    "NNE",
    "NE",
    "ENE",
    "E",
    "ESE",
    "SE",
    "SSE",
    "S",
    "SSW",
    "SW",
    "WSW",
    "W",
    "WNW",
    "NW",
    "NNW",
    "N",
]


def degree_to_direction(degree: int) -> str:
    # 북에서 다시 북으로, 360으로 나누면서 index로 계산
    return DIRECTION_NAME[round((degree % 360) / 22.5)]
