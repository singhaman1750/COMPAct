import inspect
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from CommonComponents import MOTOR_CLASSES, MOTORS_JSON, load_motor  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent / "golden"))
import golden  # noqa: E402

MOTORS_DATA = json.loads(Path(MOTORS_JSON).read_text(encoding="utf-8"))
MOTORS = MOTORS_DATA["motors"]
NAMES = sorted(MOTORS)
# Set by load_motor from the electrical data, not stored in "geometry".
PERFORMANCE_ARGS = {"maxMotorAngVelRPM", "maxMotorTorque", "maxMotorPower", "motorMass", "motorName"}
MOTEUS_MAX_CURRENT_A = 120


def by_type(motor_type):
    return [n for n in NAMES if MOTORS[n]["type"] == motor_type]


def test_file_settings():
    assert MOTORS_DATA["rating"] in ("peak", "rated")
    assert MOTORS_DATA["system_voltage_V"] == 48


@pytest.mark.parametrize("name", NAMES)
def test_motor_loads_as_its_class(name):
    motor = load_motor(name)
    assert isinstance(motor, MOTOR_CLASSES[MOTORS[name]["type"]])
    assert motor.motorName == name
    assert motor.maxMotorTorque == MOTORS[name]["electrical"]["peak_torque_Nm"]
    assert motor.maxMotorAngVelRPM == MOTORS[name]["electrical"]["no_load_speed_rpm"]
    assert motor.massKG == MOTORS[name]["mass_kg"]


@pytest.mark.parametrize("name", NAMES)
def test_geometry_sets_every_class_argument(name):
    # Every geometry argument comes from motors.json, never from a class default.
    cls = MOTOR_CLASSES[MOTORS[name]["type"]]
    class_args = set(inspect.signature(cls.__init__).parameters) - {"self"} - PERFORMANCE_ARGS
    assert set(MOTORS[name]["geometry"]) == class_args


@pytest.mark.parametrize("name", NAMES)
def test_values_are_positive_numbers(name):
    entry = MOTORS[name]
    numbers = {**entry["geometry"], "mass_kg": entry["mass_kg"]}
    numbers.update({k: v for k, v in entry["electrical"].items() if not k.endswith("_basis")})
    for key, value in numbers.items():
        assert isinstance(value, (int, float)) and value > 0, f"{name}.{key} = {value!r}"
    assert entry["source"]


@pytest.mark.parametrize("name", NAMES)
def test_electrical_limits(name):
    el = MOTORS[name]["electrical"]
    assert el["peak_current_A"] <= MOTEUS_MAX_CURRENT_A
    assert el["peak_torque_basis"] in ("measured", "estimate", "datasheet")
    if "rated_torque_Nm" in el:
        assert el["rated_torque_Nm"] <= el["peak_torque_Nm"]
        assert el["rated_speed_rpm"] <= el["no_load_speed_rpm"]


@pytest.mark.parametrize("name", by_type("framed_outrunner"))
def test_framed_motor_geometry(name):
    el, g = MOTORS[name]["electrical"], MOTORS[name]["geometry"]
    radius = g["motorDia"] / 2
    assert el["no_load_speed_rpm"] == el["kv_rpm_per_V"] * MOTORS_DATA["system_voltage_V"]
    # Slots for wires that leave through the rim may reach the rim, so only the centre must be inside.
    assert g["wire_slot_dist_from_center"] < radius
    assert g["motor_mount_hole_PCD"] / 2 + g["motor_mount_hole_dia"] / 2 < radius
    assert g["motor_output_hole_PCD"] / 2 + g["motor_output_hole_dia"] / 2 < radius
    for key in ("motor_mount_hole_num", "motor_output_hole_num"):
        assert isinstance(g[key], int)


@pytest.mark.parametrize("name", by_type("frameless_outrunner"))
def test_frameless_outrunner_geometry(name):
    g = MOTORS[name]["geometry"]
    assert g["stator_ID"] < g["stator_hole_PCD"] < g["stator_OD"] < g["rotor_ID"] < g["motor_OD"]
    assert g["motor_rotor_base_ID"] < g["motor_rotor_hole_PCD"] < g["rotor_ID"]
    assert g["stator_height"] < g["motor_height"]


@pytest.mark.parametrize("name", by_type("frameless_inrunner"))
def test_frameless_inrunner_geometry(name):
    g = MOTORS[name]["geometry"]
    assert g["rotor_ID"] < g["rotor_OD"] < g["stator_ID"] < g["stator_OD"]
    assert g["stator_wire_ID"] < g["stator_wire_OD"] <= g["stator_OD"]


def test_rated_rating_uses_rated_values():
    motor = load_motor("RO100", rating="rated")
    el = MOTORS["RO100"]["electrical"]
    assert (motor.maxMotorTorque, motor.maxMotorAngVelRPM) == (el["rated_torque_Nm"], el["rated_speed_rpm"])


def test_rated_rating_needs_rated_data():
    with pytest.raises(ValueError, match="no rated torque"):
        load_motor("U8_Lite", rating="rated")


def test_unknown_rating_is_rejected():
    with pytest.raises(ValueError, match="rating must be"):
        load_motor("U8_Lite", rating="continuous")


def test_unknown_motor_lists_known_names():
    with pytest.raises(ValueError, match="Known motors: .*U8_Lite"):
        load_motor("U8")


def test_golden_motors_exist():
    assert set(golden.FRAMED_GOLDEN_MOTORS) <= set(MOTORS)
