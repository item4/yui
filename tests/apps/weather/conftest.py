import os

import pytest


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
