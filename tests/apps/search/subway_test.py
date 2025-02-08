from datetime import timedelta

import pytest
import pytest_asyncio
from more_itertools import flatten

from yui.apps.search.subway import REGION_TABLE
from yui.apps.search.subway import fetch_all_station_db
from yui.apps.search.subway import on_start
from yui.apps.search.subway import refresh_db

from ...util import FakeBot


@pytest_asyncio.fixture()
async def bot(cache) -> FakeBot:
    return FakeBot(cache=cache)


@pytest.mark.asyncio
async def test_fetch_all_station_db(bot):
    async with bot.begin():
        for service_region, api_version in REGION_TABLE.values():
            data = await bot.cache.get(f"SUBWAY_{service_region}_{api_version}")
            assert data is None

        await fetch_all_station_db(bot)

        for service_region, api_version in REGION_TABLE.values():
            data = await bot.cache.get(f"SUBWAY_{service_region}_{api_version}")
            assert isinstance(data, list)
            assert isinstance(data[0], dict)


@pytest.mark.asyncio
async def test_on_start(bot, monkeypatch):
    async def fake_fetch(bot_):
        assert bot is bot_

    monkeypatch.setattr(
        "yui.apps.search.subway.fetch_all_station_db",
        fake_fetch,
    )

    async with bot.begin():
        assert await on_start(bot)


def test_refresh_db_spec():
    assert refresh_db.has_valid_spec


@pytest.mark.parametrize(
    ("delta", "result"),
    flatten(
        [
            (timedelta(days=x, hours=0), False),
            (timedelta(days=x, hours=2), False),
            (timedelta(days=x, hours=3), True),
            (timedelta(days=x, hours=3, minutes=30), False),
            (timedelta(days=x, hours=4), False),
        ]
        for x in range(7)
    ),
)
def test_refresh_db_match(sunday, delta, result):
    assert refresh_db.match(sunday + delta) is result


@pytest.mark.asyncio
async def test_refresh_db(bot, monkeypatch):
    async def fake_fetch(bot_):
        assert bot is bot_

    monkeypatch.setattr(
        "yui.apps.search.subway.fetch_all_station_db",
        fake_fetch,
    )

    async with bot.begin():
        await refresh_db(bot)
