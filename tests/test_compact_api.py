"""compact_api.py, the module other projects (co-design) import: the released map as the default,
nearest_design() from the map's table, final_design() through the real optimiser (RO100 ISSPG
compact, about 0.1 s), and pyproject.toml's module list for `pip install -e`.
"""
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import compact_api  # noqa: E402
from compact_api import ActuatorMap, final_design, nearest_design  # noqa: E402


def test_pyproject_lists_every_root_module():
    text = (REPO / "pyproject.toml").read_text(encoding="utf-8")
    block = re.search(r"py-modules = \[(.*?)\]", text, re.S).group(1)
    listed = set(re.findall(r'"(\w+)"', block))
    assert listed == {p.stem for p in REPO.glob("*.py")}


def test_default_map_is_the_latest_release():
    amap = ActuatorMap()
    assert amap.path == compact_api.released_maps()[-1]
    assert amap.meta["format"] == 1
    a = amap.actuator("RO100", 6.0, "3dp")
    assert a.gb_type in amap.types("RO100", "3dp") and a.mass > 0


def test_nearest_design_gives_the_best_swept_design():
    d = nearest_design("RO100", 6.2, "3dp")
    assert d["best_by_real_width"] and d["ratio"] == pytest.approx(6.0, abs=0.5)
    assert set(d["gears"]) >= {"ns", "np", "nr", "module", "n_planets"}
    assert all(isinstance(d["gears"][k], int) for k in ("ns", "np", "nr", "n_planets"))
    own = nearest_design("RO100", 6.2, "3dp", gb_type="icpg")
    assert own["gb_type"] == "icpg" and "np_small" in own["gears"]
    with pytest.raises(ValueError):
        nearest_design("RO100", 6.0, "3dp", gb_type="sspg")  # framed type, not swept for RO100


def test_final_design_runs_the_optimiser_and_writes_the_cad_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    d = final_design("RO100", 6.0, "3dp", gb_type="isspg_compact", cad_dir="out/knee")  # relative
    assert d["gb_type"] == "isspg_compact" and d["ratio"] == pytest.approx(6.0, abs=0.2)
    assert set(d["gears"]) == {"ns", "np", "nr", "module", "n_planets"}
    assert d["gears"]["nr"] == d["gears"]["ns"] + 2 * d["gears"]["np"]
    assert "fw_p" in d["face_widths_mm"] and d["face_widths_mm"]["fw_p"] > 0
    assert d["mass_kg"] > 0 and 0 < d["efficiency"] < 1 and d["peak_torque_out_Nm"] > 0
    assert not {"ns", "ratio_requested", "best_by_real_width"} & set(d)
    assert d["cad_files"] == [str(tmp_path / "out" / "knee" / "ISSPG" / "isspg_compact_equations_onshape.txt")]
    assert Path(d["cad_files"][0]).is_file()


def test_final_design_defaults_to_the_maps_best_type():
    amap = ActuatorMap()
    d = final_design("RO100", 6.0, "3dp", amap=amap)
    assert d["gb_type"] == amap.actuator("RO100", 6.0, "3dp").gb_type and d["cad_files"] == []


def test_final_design_without_a_design_raises(monkeypatch):
    from tools.actuator_map import case
    monkeypatch.setattr(case, "run_case", lambda *a, **k: {"feasible": False, "error": None})
    with pytest.raises(ValueError, match="no design"):
        final_design("RO100", 6.0, "3dp", gb_type="isspg_compact")
