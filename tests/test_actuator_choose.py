"""Actuator select (tools/actuator_map/choose.py): a motor, gearbox type and ratio for an output peak
torque and no-load speed. The helpers are checked on hand-made designs; one small real ask (RO100,
the fast ISSPG / ICPG types) goes through screening with the released map, confirmation with the
optimiser, and --no-map.
"""
import json
import math
import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.actuator_map import choose  # noqa: E402
from tools.actuator_map.map import RPM_TO_RAD_S  # noqa: E402
from tools.actuator_map.table import load_gains, load_motors  # noqa: E402

MOTOR = {"type": "frameless_outrunner",
         "electrical": {"peak_torque_Nm": 12.0, "rated_torque_Nm": 4.0, "no_load_speed_rpm": 2400.0,
                        "rated_speed_rpm": 2000.0},
         "mechanical": {"rotor_inertia_kgm2": 1e-3, "rotor_inertia_basis": "datasheet"}}
W0 = 2400.0 * RPM_TO_RAD_S
GAINS = {"K_Mass": 1, "K_Eff": -2, "K_Width": 0.2, "K_torque_shortfall": 10, "K_Width_real": 0.05}


def case(ratio, requested=None, eff=0.9, fraction=1.0, mass=1.0, cost=3.0, gb="icpg", motor="M"):
    return {"gb_type": gb, "motor": motor, "material": "3dp", "ratio_requested": requested or ratio,
            "feasible": True, "error": None, "gear_ratio": ratio, "cost": cost, "mass_kg": mass, "efficiency": eff,
            "torque_carried_fraction": fraction, "width_body_mm": 71.0, "width_with_driver_mm": 80.0,
            "dia_body_mm": 120.0, "dia_widest_mm": 130.0, "geometry_notes": [], "opt_parameters": [ratio],
            "cad_vars": {"Ns": 20, "Np_b": 40, "Np_s": 30, "Nr": 90, "module": 0.5, "num_planet": 3}}


def test_evaluate_gives_the_verdict_and_drops_the_ratio_error():
    row = choose.evaluate(case(10.2, requested=10.0), MOTOR, GAINS, torque=100.0, speed=20.0, rule="real_width")
    t = 12.0 * 10.2 * 0.9
    assert row["peak_torque_out_Nm"] == pytest.approx(t)
    assert row["meets"] and row["shortfall"] == 0 and row["torque_margin"] == pytest.approx(t / 100 - 1)
    assert row["score"] == pytest.approx(1.0 - 2 * 0.9 + 0.05 * 80)          # no |ratio - requested| term
    assert choose.evaluate(case(10.2, requested=10.0), MOTOR, GAINS, 100.0, 20.0, "compact_cost")["score"] == pytest.approx(2.8)
    short = choose.evaluate(case(10.0, fraction=0.5), MOTOR, GAINS, torque=100.0, speed=30.0, rule="real_width")
    assert not short["meets"]
    assert short["shortfall"] == pytest.approx((1 - 54.0 / 100) + (1 - W0 / 10 / 30))


def test_corrected_ratio_fixes_one_target_without_breaking_the_other():
    torque_short = choose.evaluate(case(9.0), MOTOR, GAINS, torque=100.0, speed=20.0, rule="real_width")
    r = choose.corrected_ratio(torque_short, MOTOR, 100.0, 20.0)
    assert r == pytest.approx(9.0 * 100 / (12 * 9 * 0.9) * choose.RATIO_NUDGE, abs=1e-3)
    assert 12 * r * 0.9 >= 100 and W0 / r >= 20
    speed_short = choose.evaluate(case(14.0), MOTOR, GAINS, torque=100.0, speed=20.0, rule="real_width")
    r = choose.corrected_ratio(speed_short, MOTOR, 100.0, 20.0)
    assert W0 / r >= 20 and r == pytest.approx(W0 / 20 / choose.RATIO_NUDGE, abs=1e-3)
    # more torque would need a ratio past the speed limit: nothing to try
    assert choose.corrected_ratio(choose.evaluate(case(12.0), MOTOR, GAINS, 140.0, 20.5, "real_width"), MOTOR, 140.0, 20.5) is None


def test_no_map_ratios_cover_the_window_or_the_one_closest_ratio():
    rs = choose.no_map_ratios(MOTOR, torque=60.0, speed=25.0, min_ratio=4.0, max_ratio=40.0)
    assert rs[0] == 5.0 and rs[-1] == math.floor(W0 / 25 * 100) / 100 and rs[-2] == 10.0   # 5 = 60 / 12
    assert choose.no_map_ratios(MOTOR, 30.0, 25.0, 4.0, 40.0)[0] == 4.0                   # min_ratio holds
    (r,) = choose.no_map_ratios(MOTOR, torque=400.0, speed=25.0, min_ratio=4.0, max_ratio=40.0)
    assert r == pytest.approx(math.sqrt(400 / 12 * W0 / 25), abs=0.01)


def test_ranking_meets_first_then_closest_miss_and_one_row_per_pair():
    rows = [choose.evaluate(case(r, mass=m, gb=gb, motor=mo), MOTOR, GAINS, 100.0, 20.0, "real_width")
            for r, m, gb, mo in ((10.0, 1.2, "icpg", "A"), (10.5, 1.0, "icpg", "A"), (10.0, 0.9, "idspg", "A"),
                                 (8.0, 0.5, "icpg", "B"), (9.0, 0.5, "icpg", "C"))]
    best = choose.best_per_pair(rows)
    assert [(r["motor"], r["gb_type"]) for r in best] == [("A", "idspg"), ("A", "icpg"), ("C", "icpg"), ("B", "icpg")]
    assert best[1]["mass_kg"] == 1.0 and [r["meets"] for r in best] == [True, True, False, False]


def test_latest_map_is_the_highest_version():
    assert choose.latest_map().name == max((p.name for p in choose.MAPS_DIR.glob("v*") if (p / "fits.json").is_file()),
                                           key=lambda n: int(n[1:]))


@pytest.fixture()
def runs(tmp_path, monkeypatch):
    monkeypatch.setattr(choose, "RUNS_DIR", tmp_path)
    return tmp_path


def test_end_to_end_with_the_map_and_without(runs):
    """RO100 3dp, 30 N m and 25 rad/s (ratios about 2.5-10.7), ISSPG and ICPG only: a few seconds."""
    ask = ["--torque", "30", "--speed", "25", "--motors", "RO100", "--types", "isspg_compact", "icpg",
           "--workers", str(min(4, os.cpu_count() or 1))]
    ranked = choose.main([*ask, "--name", "e2e", "--shortlist", "2"])
    result = json.loads((runs / "select_e2e" / "result.json").read_text())
    motor = load_motors()["RO100"]
    assert ranked and ranked == result["ranked"] and {r["gb_type"] for r in ranked} <= {"isspg_compact", "icpg"}
    for r in ranked:
        assert r["meets"] and r["peak_torque_out_Nm"] >= 30 and r["no_load_speed_out_rad_s"] >= 25
        el = motor["electrical"]
        assert r["peak_torque_out_Nm"] == pytest.approx(el["peak_torque_Nm"] * r["ratio"] * r["efficiency"]
                                                        * r["torque_carried_fraction"])
        assert (Path(r["cad_dir"]) / ("ISSPG" if r["gb_type"] == "isspg_compact" else "ICPG")).is_dir()
    assert [r["score"] for r in ranked] == sorted(r["score"] for r in ranked)
    assert result["map"]["path"].endswith(choose.latest_map().name) and len(result["screened"]) == 2

    no_map = choose.main([*ask, "--name", "e2e_nomap", "--no-map"])
    # the same answer without the map (the lowest-score design that meets the ask)
    assert (no_map[0]["gb_type"], no_map[0]["meets"]) == (ranked[0]["gb_type"], True)
    assert no_map[0]["score"] <= ranked[0]["score"] + 1e-9
    gains = load_gains()
    assert no_map[0]["score"] == pytest.approx(
        gains["K_Mass"] * no_map[0]["mass_kg"] + gains["K_Eff"] * no_map[0]["efficiency"]
        + gains["K_Width_real"] * 1000 * no_map[0]["width_with_driver_m"]
        + gains["K_torque_shortfall"] * (1 - no_map[0]["torque_carried_fraction"]))
