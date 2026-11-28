"""SSPG metal ring wall (ISSUES.md, "Metal: realistic values", M7): the ring wall from the pitch circle
is max(3 mm, dedendum 1.25 x module + a rim of 1.2 tooth heights), so no module is rejected; a large
module gets a thicker ring. The ring's outer diameter still stays within the motor. 3D-printed mode
keeps the fixed 5 mm wall (the golden baselines check that bit for bit).
"""
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import gearbox_runner  # noqa: E402

# The SSPG metal golden design (U8_Lite, 6.5:1): Ns, Np, Nr, module, planets.
DESIGN = (25, 56, 137, 0.5, 3)


def build(material, design=DESIGN):
    actuator, _ = gearbox_runner.build("sspg", "U8_Lite", material)
    gb = actuator.planetaryGearbox
    Ns, Np, Nr, module, n = design
    gb.setNs(Ns), gb.setNp(Np), gb.setNr(Nr), gb.setModule(module), gb.setNumPlanet(n)
    actuator.updateFacewidth()
    actuator.setVariables()
    actuator.getMassKG_3DP()
    return actuator


@pytest.mark.parametrize("module, wall_mm", [(0.5, 3), (0.7, 3), (0.8, 3.16), (1.0, 3.95), (1.2, 4.74)])
def test_metal_ring_wall_grows_with_the_module(module, wall_mm):
    gb = build("metal").planetaryGearbox
    gb.setModule(module)
    assert gb.getRingWallMM() == pytest.approx(wall_mm)
    # the rim behind the teeth is at least 1.2 tooth heights
    assert gb.getRingWallMM() - 1.25 * module >= 1.2 * 2.25 * module - 1e-12


@pytest.mark.parametrize("module", [0.5, 0.7, 1.0, 1.2])
def test_3dp_ring_wall_stays_5_mm(module):
    gb = build("3dp").planetaryGearbox
    gb.setModule(module)
    assert gb.ring_min_rim_tooth_heights is None and gb.getRingWallMM() == 5


@pytest.mark.parametrize("material, wall_mm, max_dia_mm", [("3dp", 5, 77.1), ("metal", 3, 81.1)])
def test_cad_values_mass_and_max_diameter_use_the_wall(material, wall_mm, max_dia_mm):
    a = build(material)
    gb = a.planetaryGearbox
    assert a.maxGearboxDiameter == pytest.approx(max_dia_mm)      # U8_Lite 87.1 mm - 2 x wall
    assert a.ring_radial_thickness == pytest.approx(wall_mm)
    assert a.ring_OD == pytest.approx(gb.Nr * gb.module + 2 * wall_mm)
    assert gb.getOuterRadiusRingMM() == pytest.approx(a.ring_OD / 2)
    assert gb.getOuterRadiusRingM() == pytest.approx(a.ring_OD / 2000)


def test_metal_ring_must_fit_within_the_motor():
    # U8_Lite 87.1 mm: at module 0.5 the 3 mm wall allows a ring pitch circle up to 81.1 mm (as the
    # max-diameter rule); at module 1.0 the 3.95 mm wall allows 79.2 mm
    a = build("metal")
    gb = a.planetaryGearbox
    for module, Nr, fits in [(0.5, 162, True), (0.5, 163, False), (1.0, 79, True), (1.0, 80, False)]:
        gb.setModule(module), gb.setNr(Nr)
        assert a.ringFitsConstraint() is fits, (module, Nr)


def test_3dp_ring_fit_is_not_checked():
    a = build("3dp")
    a.planetaryGearbox.setNr(400)   # far too big, but 3dp keeps only the max-diameter rule
    assert a.ringFitsConstraint()


def test_metal_is_lighter_with_the_thinner_ring():
    # before M7 (5 mm wall): 766 g; steel ring wall becomes aluminium housing
    assert build("metal").getMassKG_3DP() * 1000 == pytest.approx(749.4, abs=1)
