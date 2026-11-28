"""SSPG metal motor case (ISSUES.md, "Metal: realistic values", M4): case wall 2.5 -> 2 mm and base
plate 4 -> 2.5 mm (machined aluminium); the case mounting surface stays 4 mm (lowering it only moves
material from the motor case to the gearbox housing). 3D-printed mode keeps 2.5 / 4 / 4 mm (the golden
baselines check that bit for bit).
"""
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import gearbox_runner  # noqa: E402

# The SSPG metal golden design (U8_Lite, 6.5:1): Ns, Np, Nr, module, planets.
DESIGN = (25, 56, 137, 0.5, 3)


def build(material):
    actuator, _ = gearbox_runner.build("sspg", "U8_Lite", material)
    gb = actuator.planetaryGearbox
    Ns, Np, Nr, module, n = DESIGN
    gb.setNs(Ns), gb.setNp(Np), gb.setNr(Nr), gb.setModule(module), gb.setNumPlanet(n)
    actuator.updateFacewidth()
    actuator.setVariables()
    actuator.getMassKG_3DP()
    return actuator


@pytest.mark.parametrize("material, wall, base_plate, mounting_surface", [("3dp", 2.5, 4, 4), ("metal", 2, 2.5, 4)])
def test_case_thicknesses_per_material(material, wall, base_plate, mounting_surface):
    a = build(material)
    assert (a.Motor_case_thickness, a.base_plate_thickness, a.case_mounting_surface_height) \
        == (wall, base_plate, mounting_surface)
    assert a.motor_case_OD_base == pytest.approx(a.Motor_case_ID + 2 * wall)


def test_metal_case_is_smaller_narrower_and_lighter():
    # before M4 (2.5 mm wall, 4 mm base plate): case 96.1 mm, 59.05 mm wide, 812 g
    a = build("metal")
    assert a.motor_case_OD_base == pytest.approx(96.1 - 2 * 0.5)
    assert a.actuator_width == pytest.approx(59.05 - 1.5)
    assert a.getMassKG_3DP() * 1000 == pytest.approx(766.2 - 16.7, abs=1)   # M7: 3 mm ring wall
