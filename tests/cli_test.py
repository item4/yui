import pytest

from yui.cli import error


def test_error(capsys):
    with pytest.raises(SystemExit):
        error("test error")
    captured = capsys.readouterr()
    assert captured.err == "Error: test error\n"
