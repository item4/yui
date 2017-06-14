import pathlib

import pytest


@pytest.fixture()
def fx_tmpdir(tmpdir):
    return pathlib.Path(tmpdir)
