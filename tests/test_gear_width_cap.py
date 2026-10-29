"""ISSPG and ICPG gears sit inside the frameless outrunner, so their face width is capped at the
stator height minus a margin; INWPG's planet stack is capped at planet_stack_stator_heights x the
stator height. The torque is derated by the same factor (the MIT face width is proportional to the
tooth force). Checks the cap, the derating and that fitting designs are untouched."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import gearbox_runner  # noqa: E402


def isspg(gb_type, material):
    actuator, _ = gearbox_runner.build(gb_type, "RO100", material)
    g = actuator.planetaryGearbox
    g.setModule(0.5), g.setNs(24), g.setNp(54), g.setNr(132), g.setNumPlanet(3)
    return actuator, lambda: g.fwRingMM


def icpg(material):
    actuator, _ = gearbox_runner.build("icpg", "RO100", material)
    g = actuator.internalcompoundPlanetaryGearbox
    g.setModuleBig(0.6), g.setModuleSmall(0.6), g.setNs(18), g.setNpBig(49), g.setNpSmall(29), g.setNr(96)
    g.setNumPlanet(3)
    gap = actuator.design_params["planet_step_gap_mm"]
    return actuator, lambda: g.fwPlanetBigMM + g.fwPlanetSmallMM + gap


def inwpg(gb_type, material):
    actuator, _ = gearbox_runner.build(gb_type, "RI100", material)
    g = actuator.inrunnerWolfromPlanetaryGearbox
    g.setModuleBig(0.6), g.setModuleSmall(0.6), g.setNs(28), g.setNpBig(44), g.setNpSmall(28)
    g.setNrBig(116), g.setNrSmall(100), g.setNumPlanet(4)
    return actuator, lambda: g.fwRingBigMM + g.fwRingSmallMM + actuator.clearance_planet  # CAD planet stack


def limit_mm(actuator, gb_type):
    if gb_type.startswith("inwpg"):
        return actuator.design_params["planet_stack_stator_heights"] * actuator.motor.stator_height
    return actuator.motor.stator_height - actuator.design_params["gear_axial_margin_mm"]


CASES = {"isspg_inside": lambda m: isspg("isspg_inside", m), "isspg_compact": lambda m: isspg("isspg_compact", m),
         "icpg": icpg, "inwpg_dependent": lambda m: inwpg("inwpg_dependent", m),
         "inwpg_independent": lambda m: inwpg("inwpg_independent", m)}


@pytest.mark.parametrize("gb_type", sorted(CASES))
def test_too_wide_gears_are_capped_and_the_torque_derated(gb_type):
    actuator, width = CASES[gb_type]("3dp")  # PLA gears at peak torque: far wider than the limit
    actuator.updateFacewidth()
    limit = limit_mm(actuator, gb_type)
    fraction = actuator.torque_carried_fraction
    assert actuator.fw_limit_mm == pytest.approx(limit)
    assert width() == pytest.approx(limit)
    assert 0 < fraction < 1
    # The derating is exact: at the carried torque, the uncapped gears are exactly as wide as the limit.
    actuator.motor.maxMotorTorque *= fraction
    actuator.updateFacewidth()
    assert actuator.torque_carried_fraction == pytest.approx(1.0)
    assert width() == pytest.approx(limit)


@pytest.mark.parametrize("gb_type", sorted(CASES))
def test_gears_that_fit_are_not_changed(gb_type):
    actuator, width = CASES[gb_type]("metal")  # steel gears at half the peak torque: well inside the stator
    actuator.motor.maxMotorTorque *= 0.5
    actuator.updateFacewidth()
    assert actuator.torque_carried_fraction == 1.0
    assert width() < actuator.fw_limit_mm
