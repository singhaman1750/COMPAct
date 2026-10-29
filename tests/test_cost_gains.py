"""The cost gains live in one file, config_files/cost.json, and every gearbox type uses exactly
those. A gain copied into a type's own config or params file could silently give that type a
different cost, which would make comparisons between types (e.g. the actuator map) wrong."""
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import gearbox_runner  # noqa: E402

CONFIG_DIR = REPO / "config_files"
GAINS = json.loads((CONFIG_DIR / "cost.json").read_text(encoding="utf-8"))["Cost_gain_parameters"]
GOLDEN_MOTOR = {"framed_outrunner": "U8_Lite", "frameless_outrunner": "RO100", "frameless_inrunner": "RI100"}


def _keys(node):
    if isinstance(node, dict):
        for k, v in node.items():
            yield k
            yield from _keys(v)
    elif isinstance(node, list):
        for v in node:
            yield from _keys(v)


def test_no_other_config_file_defines_a_gain():
    gain_names = {"Cost_gain_parameters", *GAINS}
    for path in CONFIG_DIR.glob("*.json"):
        if path.name == "cost.json":
            continue
        found = gain_names & set(_keys(json.loads(path.read_text(encoding="utf-8"))))
        assert not found, f"{path.name} defines {sorted(found)}; cost gains belong in cost.json"


@pytest.mark.parametrize("gb_type", sorted(gearbox_runner.GEARBOXES))
def test_every_type_uses_the_shared_gains(gb_type):
    motor = GOLDEN_MOTOR[gearbox_runner.GEARBOXES[gb_type].motor_type]
    actuator, optimizer = gearbox_runner.build(gb_type, motor)
    assert (optimizer.K_Mass, optimizer.K_Eff, optimizer.K_Width) == (GAINS["K_Mass"], GAINS["K_Eff"], GAINS["K_Width"])
    assert actuator.design_params["K_torque_shortfall"] == GAINS["K_torque_shortfall"]
