"""Actuator map end to end: a small real sweep goes through every step of the tool
(sweep.py -> table.py -> fit.py -> map.py) with the same command-line entry points a user runs.

RO100, 3dp, ratios 4-9: two capped single-stage types (ISSPG) and ICPG. 18 real optimiser runs,
about half a minute. Ratio 6 has no design carrying 80 % of the peak torque, so the 80 % rule and
its flag are exercised on real designs too. The run goes to a temporary folder, not runs/.
"""
import csv
import json
import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.actuator_map import fit, sweep, table  # noqa: E402
from tools.actuator_map.map import ActuatorMap  # noqa: E402

MOTOR, MATERIAL = "RO100", "3dp"
TYPES = ["isspg_compact", "isspg_inside", "icpg"]
RATIOS = "4:9:1"
NAME = "e2e"


@pytest.fixture(scope="module")
def run_dir(tmp_path_factory):
    runs = tmp_path_factory.mktemp("runs")
    mp = pytest.MonkeyPatch()
    for module in (sweep, table, fit):
        mp.setattr(module, "RUNS_DIR", runs)
    try:
        sweep.main(["--name", NAME, "--motors", MOTOR, "--ratios", RATIOS, "--materials", MATERIAL,
                    "--types", *TYPES, "--workers", str(min(4, os.cpu_count() or 1))])
        table.main(["--name", NAME])
        fit.main(["--name", NAME, "--no-plots"])
    finally:
        mp.undo()
    return runs / NAME


@pytest.fixture(scope="module")
def cases(run_dir):
    return table.load_cases(run_dir)


@pytest.fixture(scope="module")
def rows(run_dir):
    with open(run_dir / f"table_{MATERIAL}.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def amap(run_dir):
    return ActuatorMap(run_dir)


def test_sweep_ran_every_case_cleanly(run_dir, cases):
    assert len(cases) == len(TYPES) * len(sweep.parse_ratios(RATIOS))
    assert not [c for c in cases if c.get("error")]
    assert all(c["same_cad_file"] for c in cases if c["feasible"])
    feasible = {(c["gb_type"], c["ratio_requested"]) for c in cases if c["feasible"]}
    # single-stage stops at 7 (ring-gear size), the compound type reaches 9
    assert {r for gb, r in feasible if gb == "icpg"} == {4.0, 5.0, 6.0, 7.0, 8.0, 9.0}
    assert {r for gb, r in feasible if gb == "isspg_inside"} == {4.0, 5.0, 6.0, 7.0}
    for name in ("table_3dp.csv", "summary.md", "fits.json", "fits.md"):
        assert (run_dir / name).is_file(), name


def test_table_has_one_row_per_feasible_case_and_the_80_percent_flag(cases, rows):
    assert len(rows) == sum(c["feasible"] for c in cases)
    by_ratio = {}
    for r in rows:
        by_ratio.setdefault(float(r["ratio_requested"]), []).append(r)
    for ratio, group in by_ratio.items():
        assert sum(r["best_by_real_width"] == "True" for r in group) == 1, ratio
        full = any(float(r["torque_carried_fraction"]) >= table.MIN_CARRIED_FRACTION_FOR_BEST for r in group)
        assert all((r["no_full_torque_design"] == "True") == (not full) for r in group), ratio
    assert all(r["no_full_torque_design"] == "True" for r in by_ratio[6.0])


def test_map_interp_reproduces_every_table_row(amap, rows):
    for r in rows:
        a = amap.actuator(MOTOR, float(r["ratio"]), MATERIAL, gb_type=r["gb_type"], method="interp")
        for attr, col in (("mass", "mass_kg"), ("width", "width_with_driver_m"), ("dia", "dia_body_m"),
                          ("efficiency", "efficiency"), ("torque_fraction", "torque_carried_fraction"),
                          ("peak_torque", "peak_torque_out_Nm"), ("rated_torque", "rated_torque_out_Nm"),
                          ("no_load_speed", "no_load_speed_out_rad_s"),
                          ("reflected_inertia", "reflected_inertia_kgm2")):
            assert getattr(a, attr) == pytest.approx(float(r[col]), rel=1e-9), (r["gb_type"], r["ratio"], attr)


def test_map_fit_equals_fit_py_and_stays_within_its_reported_error(amap, run_dir, rows):
    # A type with few designs can have a real fit error of several % (capped ISSPG's width: 4
    # designs, flat once capped), so each fit is held to the error fit.py reports for it.
    types = json.loads((run_dir / "fits.json").read_text(encoding="utf-8"))["motors"][MOTOR][MATERIAL]["types"]
    for r in rows:
        x = float(r["ratio"])
        a = amap.actuator(MOTOR, x, MATERIAL, gb_type=r["gb_type"])
        for attr, q in (("mass", "mass_kg"), ("width", "width_with_driver_m"), ("dia", "dia_body_m"),
                        ("efficiency", "efficiency")):
            f = types[r["gb_type"]]["quantities"][q]
            assert getattr(a, attr) == pytest.approx(fit.evaluate(f, x), rel=1e-12), (r["gb_type"], x, attr)
            assert abs(getattr(a, attr) - float(r[q])) <= f["max_abs"] * (1 + 1e-9) + 1e-12, (r["gb_type"], x, attr)


def test_map_best_type_matches_the_switch_ratios(amap):
    intervals, switches = amap.best_types(MOTOR, MATERIAL)
    assert intervals[0][0] == 4.0 and intervals[-1][1] == 9.0
    for lo, hi, gb in intervals:
        assert amap.actuator(MOTOR, (lo + hi) / 2, MATERIAL).gb_type == gb, (lo, hi)
    for s in switches:
        assert amap.actuator(MOTOR, s["ratio"] - 1e-4, MATERIAL).gb_type == s["from"], s
        assert amap.actuator(MOTOR, s["ratio"] + 1e-4, MATERIAL).gb_type != s["from"], s


def test_map_best_type_matches_the_table_except_where_fit_py_says(amap, run_dir, rows):
    entry = json.loads((run_dir / "fits.json").read_text(encoding="utf-8"))["motors"][MOTOR][MATERIAL]
    differs = {d["ratio"]: d["fitted"] for d in entry["differs_from_table"]}
    for r in rows:
        if r["best_by_real_width"] != "True":
            continue
        ratio = float(r["ratio_requested"])
        assert amap.actuator(MOTOR, ratio, MATERIAL).gb_type == differs.get(ratio, r["gb_type"]), ratio


def test_map_flags_and_limits_on_real_designs(amap, run_dir):
    assert amap.motors() == [MOTOR] and amap.types(MOTOR, MATERIAL) == sorted(TYPES)
    assert amap.meta["commit"] == json.loads((run_dir / "run.json").read_text())["commit"]
    assert amap.actuator(MOTOR, 6.0, MATERIAL).flags["no_full_torque_design"]
    low = amap.actuator(MOTOR, 4.0, MATERIAL)
    assert not low.flags["no_full_torque_design"] and low.torque_fraction >= table.MIN_CARRIED_FRACTION_FOR_BEST
    assert amap.actuator(MOTOR, 8.5, MATERIAL).gb_type == "icpg"          # the only type past 7
    with pytest.raises(ValueError):
        amap.actuator(MOTOR, 10.5, MATERIAL)                               # outside the sweep
