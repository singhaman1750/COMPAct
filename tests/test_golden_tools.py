import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests" / "golden"))

import golden  # noqa: E402
from _run_case import drop_timing_lines  # noqa: E402

CSV = """Motor Parameters:
maxMotorAngVelRPM, motorMass
2825 , 0.5

iter, gearRatio, mass, eff, Cost
64 , 19.82 , 1.483 , 0.888 , 7.74


Running Time (sec)
4.426697015762329
motorMassKG : 0.5
ring_gear_mass_stg2 : 0.1959
"""


def test_drop_timing_lines_removes_run_time_and_its_value():
    text = drop_timing_lines(CSV + "Running Time (sec):  0.0238\n")
    assert "Running Time" not in text
    assert "4.426697015762329" not in text
    assert "0.0238" not in text
    assert "ring_gear_mass_stg2 : 0.1959" in text


def test_named_values_reads_tables_and_pairs():
    values = golden.named_values(CSV)
    assert values["mass"] == "1.483"
    assert values["eff"] == "0.888"
    assert values["motorMass"] == "0.5"
    assert values["ring_gear_mass_stg2"] == "0.1959"


def test_describe_value_changes_names_the_changed_values():
    after = CSV.replace("1.483", "1.192").replace("0.1959", "0.0900")
    changes = golden.describe_value_changes(CSV, after)
    assert "mass: 1.483 -> 1.192" in changes
    assert "ring_gear_mass_stg2: 0.1959 -> 0.0900" in changes
    assert len(changes) == 2
