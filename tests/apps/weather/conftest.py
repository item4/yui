import asyncio
import os

import pytest


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
def google_api_key():
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        pytest.skip("Can not test this without GOOGLE_API_KEY envvar")
    return key


@pytest.fixture(scope="session")
def address() -> str:
    return "부천"


@pytest.fixture(scope="session")
def unavailable_address() -> str:
    return "WRONG"
