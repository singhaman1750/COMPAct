"""
Fast checks (seconds) that run on every push. The slow golden-output check
lives in tests/golden/golden.py.
"""

import importlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "tests" / "golden"))

import golden  # noqa: E402

import actOpt  # noqa: E402
import gearbox_runner  # noqa: E402

GEARBOXES = gearbox_runner.GEARBOXES


@pytest.mark.parametrize("gb_type", sorted(GEARBOXES))
def test_gearbox_spec_classes_and_files_exist(gb_type):
    spec = GEARBOXES[gb_type]
    module = importlib.import_module(spec.module)
    for name in (spec.gearbox_cls, spec.actuator_cls, spec.optimizer_cls):
        assert isinstance(getattr(module, name, None), type), f"{spec.module}.{name}"
    for name in (spec.config_file, spec.params_file):
        assert (REPO_ROOT / "config_files" / name).exists(), name
    assert spec.optimizer_kind in gearbox_runner.OPTIMIZER_LIMITS


@pytest.mark.parametrize("gb_type", sorted(GEARBOXES))
def test_gearbox_builds_with_a_golden_motor(gb_type):
    actuator, optimizer = gearbox_runner.build(gb_type, golden.GOLDEN_MOTORS[gb_type][0])
    assert hasattr(optimizer, "optimizeActuator")


@pytest.mark.parametrize("gb_type", sorted(GEARBOXES))
def test_every_gearbox_type_has_a_print_layout(gb_type):
    assert GEARBOXES[gb_type].optimizer_kind in actOpt.TEETH_LAYOUTS


def test_golden_motors_cover_every_gearbox_type():
    assert set(golden.GOLDEN_MOTORS) == set(GEARBOXES)


def test_unknown_gearbox_type_is_rejected():
    with pytest.raises(ValueError, match="Unknown gearbox type"):
        gearbox_runner.build("xyz", "U8_Lite")


@pytest.mark.parametrize("gb_type", sorted(GEARBOXES))
def test_psc_mode_fails_clearly(gb_type):
    spec = GEARBOXES[gb_type]
    cls = getattr(importlib.import_module(spec.module), spec.optimizer_cls)
    # The guard runs before any other attribute is used, so a bare object works as self.
    with pytest.raises(NotImplementedError, match="UsePSCasVariable=1 is not available"):
        cls.optimizeActuator(SimpleNamespace(), UsePSCasVariable=1)


@pytest.mark.parametrize(
    "path", sorted((REPO_ROOT / "config_files").glob("*.json")), ids=lambda p: p.name
)
def test_config_file_is_valid_json(path):
    json.loads(path.read_text(encoding="utf-8"))


def test_every_case_has_a_golden_baseline():
    missing = [
        golden.case_id(c)
        for c in golden.all_cases()
        if not (golden.BASELINE_DIR / f"{golden.case_id(c)}.json").exists()
    ]
    assert not missing, (
        "No golden baseline for: " + ", ".join(missing)
        + "\nRecord with: python tests/golden/golden.py record --only <gb_type>"
    )


@pytest.mark.parametrize("gb_type", sorted(GEARBOXES))
def test_metal_mode_uses_steel_gears_and_aluminium_structure(gb_type):
    spec = GEARBOXES[gb_type]
    materials = json.loads((REPO_ROOT / "config_files" / "config.json").read_text())["Material_properties"]
    for material, (gear_name, structure_name), suffix in (("3dp", ("PLA", "PLA"), ""), ("metal", ("Steel", "Aluminum"), "_metal")):
        actuator, _ = gearbox_runner.build(gb_type, golden.GOLDEN_MOTORS[gb_type][0], material)
        gearbox = getattr(actuator, spec.gearbox_arg)
        assert gearbox.densityGears == materials[gear_name]["density"]
        assert gearbox.densityStructure == materials[structure_name]["density"]
        assert gearbox.maxGearAllowableStressMPa == materials[gear_name]["maxAllowableStressMPa"]
        assert actuator.results_suffix == suffix


def test_unknown_material_mode_is_rejected():
    with pytest.raises(ValueError, match="Unknown material mode"):
        gearbox_runner.build("sspg", "U8_Lite", "wood")
