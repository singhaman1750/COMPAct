import io
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from CommonComponents import bearing_mass_kg, restores_stdout  # noqa: E402


@pytest.mark.parametrize(
    "size, mass",
    [((40, 50, 6), 0.023), ((30, 42, 7), 0.024), ((35, 47, 7), 0.027), ((25, 37, 7), 0.021), ((15, 24, 5), 0.007)],
)
def test_bearing_mass_kg_matches_exact_size(size, mass):
    assert bearing_mass_kg(*size) == mass


def test_bearing_mass_kg_is_not_fooled_by_same_bore():
    # A 25 mm bore lookup by ID returns 25x32x4; the exact size must win.
    assert bearing_mass_kg(25, 37, 7) == 0.021
    assert bearing_mass_kg(25, 32, 4) == 0.021


def test_bearing_mass_kg_rejects_unknown_size():
    with pytest.raises(ValueError, match="No bearing 25x40x9"):
        bearing_mass_kg(25, 40, 9)


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
