import pytest

from yui.apps.compute.calc.evaluator import Evaluator


@pytest.fixture
def e():
    return Evaluator()


@pytest.fixture
def ed():
    return Evaluator(decimal_mode=True)
