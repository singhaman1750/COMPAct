import io
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from CommonComponents import restores_stdout  # noqa: E402


def test_restores_stdout_after_exception():
    @restores_stdout
    def crashes_while_redirected():
        sys.stdout = io.StringIO()
        raise RuntimeError("boom")

    before = sys.stdout
    with pytest.raises(RuntimeError):
        crashes_while_redirected()
    assert sys.stdout is before


def test_restores_stdout_keeps_return_value():
    @restores_stdout
    def redirects_and_returns():
        sys.stdout = io.StringIO()
        return 42

    before = sys.stdout
    assert redirects_and_returns() == 42
    assert sys.stdout is before
