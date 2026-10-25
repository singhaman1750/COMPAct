import io
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from CommonComponents import CAD_DIR_ENV, bearing_mass_kg, cad_path, restores_stdout  # noqa: E402


@pytest.mark.parametrize(
    "size, mass",
    [((40, 50, 6), 0.023), ((30, 42, 7), 0.024), ((35, 47, 7), 0.027), ((25, 37, 7), 0.021), ((15, 24, 5), 0.007), ((20, 27, 4), 0.005)],
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


def test_cad_path_defaults_to_the_repo_cads_folder(monkeypatch):
    monkeypatch.delenv(CAD_DIR_ENV, raising=False)
    assert Path(cad_path("SSPG", "sspg_equations.txt")) == REPO_ROOT / "CADs" / "SSPG" / "sspg_equations.txt"


def test_cad_path_uses_and_creates_the_folder_from_the_environment(monkeypatch, tmp_path):
    monkeypatch.setenv(CAD_DIR_ENV, str(tmp_path / "CADs"))
    path = Path(cad_path("DSPG", "Equation_Files", "U8_Lite", "dspg_equations.txt"))
    assert path == tmp_path / "CADs" / "DSPG" / "Equation_Files" / "U8_Lite" / "dspg_equations.txt"
    assert path.parent.is_dir()


@pytest.mark.parametrize(
    "module",
    sorted(p.name for p in REPO_ROOT.glob("Actuator*Gearbox*.py")),
)
def test_gearbox_modules_write_cad_files_through_cad_path(module):
    # A path built by hand would write into the repo's CADs/ even during the
    # golden check, where every case has its own folder.
    code = (REPO_ROOT / module).read_text(encoding="utf-8")
    assert not re.search(r"""['"]CADs['"]""", code), f"{module}: use cad_path()"
