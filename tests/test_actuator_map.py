"""Actuator map (tools/actuator_map): its sweep must give exactly what the plain optimiser gives,
and its width / diameter formulas must keep matching the Onshape measurements.

Both use the golden baselines (tests/golden/baselines), which hold the plain optimiser's output:
the CAD files and results CSV of each golden case.
"""
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tests" / "golden"))

from golden import BASELINE_DIR, named_values, values_match  # noqa: E402
from tools.actuator_map.case import parse_cad_vars, run_case  # noqa: E402
from tools.actuator_map.geometry import geometry  # noqa: E402
from tools.actuator_map.sweep import parse_ratios, types_for  # noqa: E402


def baseline(case_name):
    return json.loads((BASELINE_DIR / f"{case_name}.json").read_text(encoding="utf-8"))


def baseline_cad_vars(b):
    (text,) = [t for p, t in b["cad_files"].items() if p.endswith(f"{b['gb_type']}_equations_onshape.txt")]
    return parse_cad_vars(text)


def baseline_csv_values(b):
    (text,) = [t for p, t in b["results_files"].items() if "_Motor_Params" not in p]
    return named_values(text)


# ---- the sweep reproduces the plain optimiser ---------------------------------------------------
# Fast cases: a framed type, two capped ones (ISSPG, ICPG) and INSSPG (two CSV files). All 58
# golden cases matched when the tool was written (2026-10-29).
SWEEP_CASES = ["sspg__U8_Lite__6.5", "isspg_inside__RO100__6.5", "insspg_type_2__RI100__6.5", "icpg__RO100__10"]


@pytest.mark.parametrize("case_name", SWEEP_CASES)
def test_sweep_case_equals_the_plain_optimiser(case_name):
    b = baseline(case_name)
    r = run_case(b["gb_type"], b["motor"], b["gear_ratio"], b.get("material", "3dp"))
    assert r["feasible"] and r["same_cad_file"]
    # Baselines were recorded on Windows; other platforms (CI runs Linux) can differ in the last
    # floating-point digit, so values are compared with the golden check's tolerance (values_match).
    assert values_match(b["opt_parameters"], r["opt_parameters"])
    expected_vars = baseline_cad_vars(b)
    assert expected_vars.keys() == r["cad_vars"].keys()
    assert values_match(expected_vars, r["cad_vars"]),         [k for k in expected_vars if not values_match(expected_vars[k], r["cad_vars"][k])]
    csv = baseline_csv_values(b)
    assert values_match(float(csv["gearRatio"]), r["gear_ratio"])
    # the CSV keeps 3 decimals; allow a last-digit rounding difference
    assert float(csv["mass"]) == pytest.approx(r["mass_kg"], abs=1e-3)
    assert float(csv["eff"]) == pytest.approx(r["efficiency"], abs=1e-3)
    if "Torque_carried_fraction" in csv:
        assert values_match(float(csv["Torque_carried_fraction"]), r["torque_carried_fraction"])


def test_no_design_is_reported_not_raised():
    # ISSPG finds no design with RO60 (golden baseline has none either)
    r = run_case("isspg_inside", "RO60", 6.5)
    assert r["feasible"] is False and r["error"] is None


# ---- width and diameter match Onshape -----------------------------------------------------------
# Measured in Onshape "Assembly 1" (2026-10-29) on exactly the golden designs:
# (width_body, width_with_driver, dia_body, dia_widest) in mm; None = not measured.
# Framed types: diameters from the Onshape sketch rules, SSPG width measured.
ONSHAPE_MM = {
    "isspg_inside__RO100__6.5":       (63.90, 72.90, 126.5, 139.11),
    "isspg_compact__RO100__6.5":      (67.40, 71.90, 126.5, 139.11),
    "icpg__RO100__10":                (66.80, 75.80, 125.5, 138.59),
    "idspg__RO100__20":               (103.64, 110.00, 126.5, 146.5),
    "insspg_type_1__RI100__6.5":      (69.56, 77.56, 111.0, 123.0),
    "insspg_type_2__RI100__6.5":      (63.59, 72.59, 111.0, 123.0),
    "incpg_dependent__RI100__10":     (96.27, 105.27, 112.0, 124.0),
    "incpg_independent__RI100__10":   (96.42, 105.42, 111.0, 123.0),
    "inwpg_dependent__RI100__20":     (100.25, None, None, None),
    "inwpg_independent__RI100__20":   (110.25, None, None, None),
    "indspg__RI100__20":              (74.64, 81.01, 111.0, 123.0),
    "sspg__U8_Lite__6.5":             (None, 75.62, 102.1, 113.6),
    "cpg__U8_Lite__10":               (None, None, 102.1, 113.6),
    "wpg__U8_Lite__20":               (None, None, 111.0, 113.6),
    "dspg__U8_Lite__20":              (None, None, 106.0, 113.6),
}


@pytest.mark.parametrize("case_name", sorted(ONSHAPE_MM))
def test_geometry_matches_onshape(case_name):
    b = baseline(case_name)
    code_width = baseline_csv_values(b).get("Actuator_width")
    g = geometry(b["gb_type"], baseline_cad_vars(b), code_width and float(code_width))
    keys = ("width_body_mm", "width_with_driver_mm", "dia_body_mm", "dia_widest_mm")
    for key, measured in zip(keys, ONSHAPE_MM[case_name]):
        if measured is not None:
            assert g[key] == pytest.approx(measured, abs=0.02), key
    assert g["geometry_notes"] == []


# ---- small helpers --------------------------------------------------------------------------------

def test_ratio_grid():
    assert parse_ratios("4:6:0.5") == [4, 4.5, 5, 5.5, 6]
    assert parse_ratios("6.5 10") == [6.5, 10]


def test_each_motor_type_gets_its_gearbox_types():
    assert types_for("framed_outrunner") == ["sspg", "cpg", "wpg", "dspg"]
    assert set(types_for("frameless_outrunner")) == {"isspg_inside", "isspg_compact", "icpg", "idspg"}
    assert len(types_for("frameless_inrunner")) == 7
