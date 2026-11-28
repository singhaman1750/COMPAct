"""SSPG metal planets (ISSUES.md, "Metal: realistic values", M1): one planet bearing (NSK 688, 8 x 16
x 5 mm, 4.02 g) instead of two 8 x 12 x 3.5 mm ones, and a rim check that the planet can hold it.
3D-printed mode keeps two bearings and no rim check (the golden baselines check that bit for bit).
"""
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import gearbox_runner  # noqa: E402

# The SSPG metal golden design (U8_Lite, 6.5:1): Ns, Np, Nr, module, planets. In steel its stress
# width is below the bearing width, so the bearing sets the planet width; in PLA the stress does.
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


@pytest.mark.parametrize("material, bearings, min_width_mm, bearing_g, planet_hole_mm", [
    ("3dp", 2, 2 * 3.5 + 1.0, 1.0, 10),   # two bearings with a 1 mm gap, as before
    ("metal", 1, 5, 4.02, 16),            # one 688
])
def test_planet_width_and_bearing_mass_follow_the_bearings(material, bearings, min_width_mm, bearing_g, planet_hole_mm):
    a = build(material)
    assert a.planet_bearings_per_planet == bearings
    assert a.fw_p >= min_width_mm and a.fw_r == pytest.approx(a.fw_p)
    if material == "metal":   # steel: the bearing, not the stress, sets the width
        assert a.fw_p == pytest.approx(min_width_mm)
    assert a.planet_bearing_combined_mass == pytest.approx(3 * bearings * bearing_g / 1000)
    assert a.planet_bore == planet_hole_mm


def test_metal_is_lighter_and_narrower_with_one_bearing():
    # this design with two bearings (before M1): 65.05 mm, 979 g (the old metal golden baseline);
    # 886 g after M1, 850 g with the 2 mm motor-to-case gap (M2), 812 g with thinner plates (M3)
    metal = build("metal")
    assert metal.actuator_width == pytest.approx(65.05 - 3.0 - 3.0)   # planet 8 -> 5 mm; plates (M3) 3 mm
    assert metal.getMassKG_3DP() * 1000 == pytest.approx(812.2, abs=1)


@pytest.mark.parametrize("Np, holds", [(45, True), (40, True), (39, False), (30, False)])
def test_metal_planet_must_hold_its_bearing(Np, holds):
    # root circle module x (Np - 2.5) >= 16 mm bearing + 2 x 1.2 x 2.25 x module rim: Np >= 39.9 at module 0.5
    gb = build("metal").planetaryGearbox
    gb.setNp(Np), gb.setModule(0.5)
    assert gb.planetHoldsBearingConstraint() is holds


def test_3dp_planet_rim_is_not_checked():
    gb = build("3dp").planetaryGearbox
    gb.setNp(20), gb.setModule(0.5)   # far too small for its bearings, but 3dp has no rim check
    assert gb.planet_min_rim_tooth_heights is None and gb.planetHoldsBearingConstraint()
