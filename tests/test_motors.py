import inspect
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from CommonComponents import MOTOR_CLASSES, MOTORS_JSON, load_motor, max_gearbox_dia_mult_factor  # noqa: E402

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


def test_rated_rating_needs_rated_data(tmp_path):
    # Every motor now has rated values; check the error with a copy that lacks them.
    data = json.loads(Path(MOTORS_JSON).read_text(encoding="utf-8"))
    for key in ("rated_torque_Nm", "rated_speed_rpm"):
        del data["motors"]["U8_Lite"]["electrical"][key]
    path = tmp_path / "motors.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="no rated torque"):
        load_motor("U8_Lite", rating="rated", path=str(path))


@pytest.mark.parametrize("name", NAMES)
def test_every_motor_has_rated_values(name):
    el = MOTORS[name]["electrical"]
    assert 0 < el["rated_current_A"] < el["peak_current_A"]
    assert 0 < el["rated_torque_Nm"] < el["peak_torque_Nm"]
    assert 0 < el["rated_speed_rpm"] < el["no_load_speed_rpm"]
    motor = load_motor(name, rating="rated")
    assert (motor.maxMotorTorque, motor.maxMotorAngVelRPM) == (el["rated_torque_Nm"], el["rated_speed_rpm"])


@pytest.mark.parametrize("name", NAMES)
def test_rotor_inertia_is_plausible(name):
    entry = MOTORS[name]
    mech = entry["mechanical"]
    inertia = mech["rotor_inertia_kgm2"]
    assert mech["rotor_inertia_basis"].split(":")[0] in ("datasheet", "measured", "estimate")
    assert mech["rotor_inertia_source"]
    # Less than the whole motor's mass at its outer radius.
    radius_m = (entry["geometry"].get("motorDia") or entry["geometry"].get("motor_OD")
                or entry["geometry"]["stator_OD"]) / 2000
    assert 0 < inertia < entry["mass_kg"] * radius_m ** 2


def test_rated_values_of_framed_motors_say_where_they_come_from():
    for name in by_type("framed_outrunner"):
        el = MOTORS[name]["electrical"]
        for key in ("rated_current_basis", "rated_torque_basis", "rated_speed_basis"):
            assert el[key].split(":")[0] in ("datasheet", "measured", "estimate"), (name, key)


def test_unknown_rating_is_rejected():
    with pytest.raises(ValueError, match="rating must be"):
        load_motor("U8_Lite", rating="continuous")


def test_unknown_motor_lists_known_names():
    with pytest.raises(ValueError, match="Known motors: .*U8_Lite"):
        load_motor("U8")


def test_golden_motors_exist():
    assert set(golden.FRAMED_GOLDEN_MOTORS) <= set(MOTORS)


def test_small_motors_get_the_wider_gearbox_factor():
    params = {"MAX_GB_DIA_MULT_FACTOR": 1, "MAX_GB_DIA_MULT_FACTOR_SMALL_MOTOR": 1.25, "SMALL_MOTOR_DIA_MM": 80}
    assert max_gearbox_dia_mult_factor(load_motor("MAD_M6C12_KV170"), params) == 1.25  # 72 mm
    assert max_gearbox_dia_mult_factor(load_motor("U8_Lite"), params) == 1             # 87.1 mm


def test_wrong_motor_type_is_rejected():
    with pytest.raises(ValueError, match="needs a frameless_outrunner motor: RO100, RO60, RO80"):
        load_motor("RI100", motor_type="frameless_outrunner")
