import pytest

from yui.apps.compute.calc.evaluator import Evaluator


@pytest.fixture
def e():
    return Evaluator()
