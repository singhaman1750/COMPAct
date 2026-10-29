"""SSPG and CPG gearbox casings in metal mode: only the ring is steel, the rest of the casing is aluminium.

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


# ---- CPG -----------------------------------------------------------------------------------------
# The metal golden design before the split (U8_Lite, 10:1): Ns, Np big, Np small, Nr, module, planets.
OLD_CPG_METAL_DESIGN = (24, 56, 28, 108, 0.5, 3)


def build_cpg(material, design=OLD_CPG_METAL_DESIGN):
    actuator, _ = gearbox_runner.build("cpg", "U8_Lite", material)
    gb = actuator.compoundPlanetaryGearbox
    Ns, Np1, Np2, Nr, module, n = design
    gb.setNs(Ns), gb.setNpBig(Np1), gb.setNpSmall(Np2), gb.setNr(Nr)
    gb.setModuleBig(module), gb.setModuleSmall(module), gb.setNumPlanet(n)
    actuator.updateFacewidth()
    actuator.setVariables()
    actuator.getMassKG_3DP()
    return actuator


def cpg_ring_od(a):
    """The mass model's ring OD: ring pitch circle + 2 x ringRadialWidthMM (5 mm). The CAD's
    ring_OD can be larger (ring grown to the output bearing; ISSUES.md bug 17)."""
    return a.Nr * a.compoundPlanetaryGearbox.moduleSmall + 2 * a.ringRadialWidthMM


def cpg_volumes_m3(a):
    ring_id, ring_od = a.Nr * a.compoundPlanetaryGearbox.moduleSmall, cpg_ring_od(a)
    ring = math.pi / 4 * (ring_od ** 2 - ring_id ** 2) * (a.fw_r + a.clearance_planet)
    holder = math.pi / 4 * ((a.bearing_OD + 2 * a.bearing_mount_thickness) ** 2 - a.bearing_OD ** 2) \
        * (a.bearing_height + a.standard_clearance_1_5mm)
    case_od = a.motor_case_OD_base
    mounting = math.pi / 4 * (case_od ** 2 - (case_od - 2 * a.Motor_case_OD_base_to_chamfer) ** 2) * a.case_dist
    fillet = 0.5 * math.pi / 4 * (case_od ** 2 - ring_od ** 2) * a.fw_r
    return ring * 1e-9, (holder + mounting + fillet) * 1e-9


def test_cpg_metal_ring_is_steel_and_the_housing_aluminium():
    a = build_cpg("metal")
    gb = a.compoundPlanetaryGearbox
    assert (gb.densityGears, gb.densityStructure) == (7850, 2700)
    ring, housing = cpg_volumes_m3(a)
    assert a.ring_mass == pytest.approx(ring * 7850, rel=1e-9)
    assert a.gearbox_housing_mass == pytest.approx(housing * 2700, rel=1e-9)
    assert a.gearbox_casing_mass == pytest.approx(a.ring_mass + a.gearbox_housing_mass, rel=1e-12)
    assert housing * (7850 - 2700) * 1000 == pytest.approx(226, abs=2)   # the saving on this gear set


def test_cpg_3dp_casing_is_unchanged():
    a = build_cpg("3dp")
    gb = a.compoundPlanetaryGearbox
    assert gb.densityGears == gb.densityStructure
    ring, housing = cpg_volumes_m3(a)
    assert a.gearbox_casing_mass == pytest.approx((ring + housing) * gb.densityGears, rel=1e-9)


def test_cpg_metal_optimum_gets_lighter():
    """The re-recorded metal golden design: 21/54/30/105, module 0.5, at 802 g (1,032 g before)."""
    assert build_cpg("metal", (21, 54, 30, 105, 0.5, 3)).getMassKG_3DP() == pytest.approx(0.802, abs=0.001)
