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


# ---- the map table (tools/actuator_map/table.py) ----------------------------------------------

from tools.actuator_map.table import GEAR_VARS, build_rows, summary  # noqa: E402

MOTOR = {"type": "frameless_outrunner",
         "electrical": {"peak_torque_Nm": 12.0, "rated_torque_Nm": 4.0, "no_load_speed_rpm": 2400.0,
                        "rated_speed_rpm": 2000.0},
         "mechanical": {"rotor_inertia_kgm2": 1e-3, "rotor_inertia_basis": "datasheet"}}
GAINS_FOR_TABLE = {"K_Mass": 1, "K_Eff": -2, "K_Width": 0.2, "K_torque_shortfall": 10, "K_Width_real": 0.05}


def fake_case(gb_type, ratio, cost, fraction=1.0, width_drv=80.0, mass=1.0, eff=0.9, notes=()):
    return {"gb_type": gb_type, "motor": "M", "material": "3dp", "ratio_requested": ratio, "feasible": True,
            "error": None, "gear_ratio": ratio, "cost": cost, "mass_kg": mass, "efficiency": eff,
            "torque_carried_fraction": fraction, "width_body_mm": width_drv - 9, "width_with_driver_mm": width_drv,
            "dia_body_mm": 120.0, "dia_widest_mm": 130.0, "geometry_notes": list(notes), "commit": "abc",
            "cad_vars": {"Ns": 20, "Np": 40, "Nr": 100, "module": 0.5, "num_planet": 3,
                         "Np_b": 40, "Np_s": 30, "a1_Ns": 20, "a1_Np": 30, "a1_Nr": 80, "a1_module": 0.5,
                         "a1_num_planet": 3, "a2_Ns": 25, "a2_Np": 35, "a2_Nr": 95, "a2_module": 0.8,
                         "a2_num_planet": 4}}


def test_table_formulas_and_capped_derating():
    capped = fake_case("isspg_inside", 6.0, cost=5.0, fraction=0.5, width_drv=70.0)
    (row,) = build_rows([capped], motors={"M": MOTOR}, gains=GAINS_FOR_TABLE)
    assert row["peak_torque_out_Nm"] == pytest.approx(12.0 * 6 * 0.9 * 0.5)
    # gears carry 0.5 x 12 = 6 N m >= rated 4, so the rated torque is not reduced
    assert row["rated_torque_out_Nm"] == pytest.approx(4.0 * 6 * 0.9)
    assert row["no_load_speed_out_rpm"] == pytest.approx(400.0)
    assert row["rated_speed_out_rad_s"] == pytest.approx(2000 * 2 * 3.141592653589793 / 60 / 6)
    assert row["reflected_inertia_kgm2"] == pytest.approx(36e-3)
    assert row["width_with_driver_m"] == pytest.approx(0.070)
    assert row["real_width_score"] == pytest.approx(1.0 - 2 * 0.9 + 0.05 * 70 + 0 + 10 * 0.5)
    assert row["torque_capped"] and row["best_by_compact_cost"] and row["best_by_real_width"]
    # capped below the rated torque: 0.25 x 12 = 3 N m < 4
    (low,) = build_rows([fake_case("isspg_inside", 6.0, cost=5.0, fraction=0.25)], {"M": MOTOR}, GAINS_FOR_TABLE)
    assert low["rated_torque_out_Nm"] == pytest.approx(3.0 * 6 * 0.9)


def test_table_best_rows_cad_flags_and_gear_columns():
    cases = [fake_case("idspg", 10.0, cost=3.0, width_drv=120.0),   # lowest compact cost, long
             fake_case("icpg", 10.0, cost=4.0, width_drv=70.0, notes=["approx"]),  # shorter: wins real width
             {**fake_case("isspg_inside", 10.0, cost=9.0), "feasible": False, "error": None}]
    rows = {r["gb_type"]: r for r in build_rows(cases, {"M": MOTOR}, GAINS_FOR_TABLE)}
    assert set(rows) == {"idspg", "icpg"}  # no-design cases are not rows
    assert rows["idspg"]["best_by_compact_cost"] and not rows["icpg"]["best_by_compact_cost"]
    assert rows["icpg"]["best_by_real_width"] and not rows["idspg"]["best_by_real_width"]
    assert rows["idspg"]["cad_issues"] == "CAD6" and rows["icpg"]["cad_issues"] == ""
    assert rows["icpg"]["geometry_approx"] and not rows["idspg"]["geometry_approx"]
    assert (rows["idspg"]["ns"], rows["idspg"]["ns_2"], rows["idspg"]["n_planets_2"], rows["idspg"]["module_2"]) == (20, 25, 4, 0.8)
    assert (rows["icpg"]["np"], rows["icpg"]["np_small"], rows["icpg"]["ns_2"]) == (40, 30, None)
    text = summary(cases, list(rows.values()))
    assert "10 idspg" in text and "10 icpg" in text and "| isspg_inside | 3dp | 1 | 0 |" in text


def test_every_gearbox_type_has_gear_columns():
    import gearbox_runner
    assert set(GEAR_VARS) == set(gearbox_runner.GEARBOXES)


def test_best_needs_80_percent_torque_unless_nothing_has_it():
    # capped 70 % design scores best but can't win while an 85 % one exists
    cases = [fake_case("isspg_inside", 5.0, cost=1.0, fraction=0.70, width_drv=60.0),
             fake_case("icpg", 5.0, cost=2.0, fraction=0.85, width_drv=75.0),
             # ratio 6: nothing reaches 80 %, so the best of all is given and the group is flagged
             fake_case("isspg_inside", 6.0, cost=1.0, fraction=0.55),
             fake_case("icpg", 6.0, cost=2.0, fraction=0.50)]
    rows = build_rows(cases, {"M": MOTOR}, GAINS_FOR_TABLE)
    best5 = [r["gb_type"] for r in rows if r["ratio_requested"] == 5.0 and r["best_by_real_width"]]
    best6 = [r for r in rows if r["ratio_requested"] == 6.0 and r["best_by_compact_cost"]]
    assert best5 == ["icpg"]
    assert [r["gb_type"] for r in best6] == ["isspg_inside"]
    assert all(r["no_full_torque_design"] for r in rows if r["ratio_requested"] == 6.0)
    assert not any(r["no_full_torque_design"] for r in rows if r["ratio_requested"] == 5.0)


def test_near_best_lists_types_within_2_percent():
    cases = [fake_case("dspg", 20.0, cost=3.00), fake_case("wpg", 20.0, cost=3.05),   # 1.7 % worse: near
             fake_case("cpg", 20.0, cost=3.20)]                                         # 6.7 % worse: not
    rows = build_rows(cases, {"M": MOTOR}, GAINS_FOR_TABLE)
    assert {r["near_best_compact"] for r in rows} == {"dspg wpg"}


# ---- fits over the gear ratio (tools/actuator_map/fit.py) -------------------------------------

import numpy as np  # noqa: E402

from tools.actuator_map.fit import best_type, fit_quantity, switch_points, valid_intervals  # noqa: E402


def test_fit_picks_the_lowest_degree_that_fits():
    x = np.arange(4, 31, 1.0)
    quad = fit_quantity(x, 1 + 0.5 * x + 0.02 * x ** 2)
    assert quad["degree"] == 2 and np.allclose(quad["coef"], [1, 0.5, 0.02])
    assert fit_quantity(x, np.full_like(x, 0.1))["degree"] == 0
    # 4 points allow at most a straight line (no bending through every point)
    assert fit_quantity([4, 5, 6, 7], [0.49, 0.55, 0.60, 0.58])["degree"] <= 1


def test_valid_intervals_follow_gaps_and_requested_ratios():
    # designs at requested 4-6 and 9-10 (none at 7, 8); real ratio 9.9 for request 10
    pts = [(4, 4.0), (5, 5.0), (6, 6.1), (9, 9.0), (10, 9.9)]
    assert valid_intervals(pts, 1.0) == [[4.0, 6.1], [9.0, 10.0]]


def _type(mass, width_mm=80.0, fraction=1.0, lo=4.0, hi=30.0):
    def q(coef):
        return {"coef": coef}
    return {"valid_intervals": [[lo, hi]],
            "quantities": {"mass_kg": q(mass), "efficiency": q([0.9]), "width_with_driver_m": q([width_mm / 1000]),
                           "torque_carried_fraction": q([fraction]), "compact_cost": q(mass)}}


def test_switch_where_fitted_scores_cross():
    # same efficiency and width: the score difference is the mass difference, equal at ratio 10
    types = {"cpg": _type([1.0, 0.1]), "dspg": _type([2.0])}
    intervals, switches = switch_points(types, GAINS_FOR_TABLE, 4.0, 30.0)
    assert [iv[2] for iv in intervals] == ["cpg", "dspg"]
    assert switches[0]["ratio"] == pytest.approx(10.0, abs=1e-3)


def test_best_between_grid_points_uses_the_80_percent_rule():
    types = {"isspg_inside": _type([0.5], fraction=0.6), "icpg": _type([1.5], fraction=0.9)}
    assert best_type(types, 6.3, GAINS_FOR_TABLE) == "icpg"          # 60 % can't win while 90 % exists
    only_capped = {"isspg_inside": _type([0.5], fraction=0.6), "icpg": _type([1.5], fraction=0.5)}
    assert best_type(only_capped, 6.3, GAINS_FOR_TABLE) == "isspg_inside"
    assert best_type(types, 31.0, GAINS_FOR_TABLE) is None             # outside every valid range
