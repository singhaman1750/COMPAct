"""SSPG gearbox casing in metal mode: only the ring is steel, the rest of the casing is aluminium.

The ring is the annulus from the ring pitch circle (Nr x module) to ring_OD, fw_r + clearance_planet
long. In 3D-printed mode both are PLA and the mass is the original one (the golden baselines check
that bit for bit).
"""
import math
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import gearbox_runner  # noqa: E402

# The metal golden design before the split (U8_Lite, 6.5:1): Ns, Np, Nr, module, planets.
OLD_METAL_DESIGN = (23, 52, 127, 0.6, 3)


def build(material, design=OLD_METAL_DESIGN):
    actuator, _ = gearbox_runner.build("sspg", "U8_Lite", material)
    gb = actuator.planetaryGearbox
    Ns, Np, Nr, module, n = design
    gb.setNs(Ns), gb.setNp(Np), gb.setNr(Nr), gb.setModule(module), gb.setNumPlanet(n)
    actuator.updateFacewidth()
    actuator.setVariables()
    actuator.getMassKG_3DP()
    return actuator


def ring_volume_m3(a):
    """The steel ring, from the CAD variables: ring PCD (dp_r) to ring_OD, fw_r + clearance_planet long."""
    return math.pi / 4 * (a.ring_OD ** 2 - a.dp_r ** 2) * (a.fw_r + a.clearance_planet) * 1e-9


def housing_volume_m3(a):
    """The rest of the casing, from the CAD variables: output-bearing holder, case-mounting ring
    (ring_OD to the motor case, case_dist high) and the fillet between them (half a ring, fw_r high)."""
    holder = math.pi / 4 * ((a.bearing_OD + 2 * a.bearing_mount_thickness) ** 2 - a.bearing_OD ** 2) \
        * (a.bearing_height + a.standard_clearance_1_5mm)
    mounting = math.pi / 4 * (a.motor_case_OD_base ** 2 - a.ring_OD ** 2) * a.case_dist
    fillet = 0.5 * math.pi / 4 * (a.motor_case_OD_base ** 2 - a.ring_OD ** 2) * a.fw_r
    return (holder + mounting + fillet) * 1e-9


def test_metal_ring_is_steel_and_the_housing_aluminium():
    a = build("metal")
    gb = a.planetaryGearbox
    assert (gb.densityGears, gb.densityStructure) == (7850, 2700)
    assert a.ring_mass == pytest.approx(ring_volume_m3(a) * 7850, rel=1e-9)
    assert a.gearbox_housing_mass == pytest.approx(housing_volume_m3(a) * 2700, rel=1e-9)
    assert a.gearbox_casing_mass == pytest.approx(a.ring_mass + a.gearbox_housing_mass, rel=1e-12)
    # docs/metal_sspg_mass.md: weighing the housing as aluminium instead of steel saves ~236 g here
    assert housing_volume_m3(a) * (7850 - 2700) * 1000 == pytest.approx(236, abs=2)


def test_3dp_casing_is_unchanged():
    a = build("3dp")
    gb = a.planetaryGearbox
    assert gb.densityGears == gb.densityStructure
    assert a.ring_mass == pytest.approx(ring_volume_m3(a) * gb.densityGears, rel=1e-12)
    assert a.gearbox_casing_mass == pytest.approx(a.ring_mass + a.gearbox_housing_mass, rel=1e-12)
    assert a.gearbox_housing_mass > 0


def test_metal_optimum_gets_lighter():
    """The re-recorded metal golden design: the optimiser now picks module 0.5 (25/56/137) at 979 g,
    against 1,224 g before the split."""
    a = build("metal", (25, 56, 137, 0.5, 3))
    assert a.getMassKG_3DP() == pytest.approx(0.979, abs=0.001)
