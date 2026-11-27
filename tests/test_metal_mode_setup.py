"""Metal mode's own settings and its CAD files (ISSUES.md, "Metal: realistic values", M0): the
params file's metal sections override the 3D-printed values in metal mode only, and metal runs
never write into CADs/ or push to Onshape.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import CommonComponents  # noqa: E402
import gearbox_runner  # noqa: E402
from compact_api import final_design  # noqa: E402


@pytest.fixture
def metal_sections(monkeypatch):
    """Adds metal sections to sspg_params.json as build() reads it; returns the dict to fill."""
    sections = {}
    load = gearbox_runner._load_json

    def with_sections(name):
        data = load(name)
        return {**data, **sections} if name == "sspg_params.json" else data

    monkeypatch.setattr(gearbox_runner, "_load_json", with_sections)
    return sections


def test_metal_sections_override_only_in_metal_mode(metal_sections):
    metal_sections["sspg_metal_design_parameters"] = {"clearance_motor_and_case_min": 2}
    metal_sections["sspg_metal_optimization_parameters"] = {"MODULE_MIN": 0.4}
    actuator, optimizer = gearbox_runner.build("sspg", "U8_Lite", "metal")
    assert actuator.clearance_motor_and_case_min == 2 and optimizer.MODULE_MIN == 0.4
    actuator, optimizer = gearbox_runner.build("sspg", "U8_Lite", "3dp")
    assert actuator.clearance_motor_and_case_min == 5 and optimizer.MODULE_MIN == 0.5


@pytest.mark.parametrize("key", ["sspg_metal_design_parameters", "sspg_metal_optimization_parameters"])
def test_unknown_metal_key_is_an_error(metal_sections, key):
    metal_sections[key] = {"clearance_motor_and_case_minn": 2}
    with pytest.raises(ValueError, match="unknown keys clearance_motor_and_case_minn"):
        gearbox_runner.build("sspg", "U8_Lite", "metal")


def test_metal_run_writes_no_cad_files(tmp_path, monkeypatch):
    repo_cads = tmp_path / "CADs"  # stands in for the repo's CADs/ folder
    monkeypatch.setattr(CommonComponents, "REPO_CAD_DIR", str(repo_cads))
    monkeypatch.delenv(CommonComponents.CAD_DIR_ENV, raising=False)
    monkeypatch.chdir(tmp_path)   # the results CSVs go here
    _, params = gearbox_runner.run("sspg", "U8_Lite", 6.5, "metal")
    assert params is not None and not repo_cads.exists()
    assert CommonComponents.CAD_DIR_ENV not in os.environ
    gearbox_runner.run("sspg", "U8_Lite", 6.5, "3dp")
    assert (repo_cads / "SSPG" / "sspg_equations_onshape.txt").is_file()


def test_onshape_push_refuses_metal():
    out = subprocess.run([sys.executable, str(REPO / "actOpt.py"), "--motor", "U8_Lite", "--gb_type", "sspg",
                          "--gr", "6.5", "--material", "metal", "--onshape"],
                         capture_output=True, text=True, cwd=REPO)
    assert out.returncode == 2 and "metal designs have no CAD model" in out.stderr


def test_final_design_writes_no_cad_files_for_metal(tmp_path):
    d = final_design("RO100", 6.0, "metal", gb_type="isspg_compact", cad_dir=tmp_path / "knee")
    assert d["mass_kg"] > 0 and d["cad_vars"]   # the CAD values are still computed (for the sizes)
    assert d["cad_files"] == [] and "no CAD model" in d["cad_note"] and not (tmp_path / "knee").exists()
