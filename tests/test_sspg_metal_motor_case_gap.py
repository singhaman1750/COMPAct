"""SSPG metal motor-to-case gap (ISSUES.md, "Metal: realistic values", M2): 2 mm instead of the 3D
printed 5 mm, since a machined case bore is concentric with the motor mount. Only the code's case
sizes and masses change; metal writes no CAD files.
"""
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import gearbox_runner  # noqa: E402

# The SSPG metal golden design (U8_Lite, 6.5:1): Ns, Np, Nr, module, planets. Its ring (78.5 mm) is
# smaller than the motor (87.1 mm), so the gap is the minimum.
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


@pytest.mark.parametrize("material, gap_mm", [("3dp", 5), ("metal", 2)])
def test_motor_case_gap_per_material(material, gap_mm):
    a = build(material)
    assert a.clearance_motor_and_case_min == gap_mm
    assert a.clearance_motor_and_case == gap_mm   # ring smaller than the motor
    assert a.Motor_case_ID == pytest.approx(a.motor_OD + 2 * gap_mm)


def test_metal_case_is_smaller_by_twice_the_gap_change():
    # 5 mm before M2: case 102.1 mm, mounting PCD and outer diameter 6 mm larger (the case wall is
    # 0.5 mm thinner since M4)
    a = build("metal")
    assert a.motor_case_OD_base == pytest.approx(102.1 - 2 * 3 - 2 * 0.5)
    assert a.Motor_case_OD_max == pytest.approx(111.6 - 2 * 3 - 2 * 0.5)
