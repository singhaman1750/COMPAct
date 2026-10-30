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


# ---- DSPG ----------------------------------------------------------------------------------------
# The metal golden design (U8_Lite, 20:1), per stage: Ns, Np, Nr, module, planets. The split does not
# change the optimum here, only its mass.
DSPG_METAL_DESIGN = ((33, 45, 123, 0.5, 3), (27, 30, 87, 0.6, 3))


def build_dspg(material, design=DSPG_METAL_DESIGN):
    actuator, _ = gearbox_runner.build("dspg", "U8_Lite", material)
    gb = actuator.doubleStagePlanetaryGearbox
    for stage, (Ns, Np, Nr, module, n) in zip((gb.Stage1, gb.Stage2), design):
        stage.setNs(Ns), stage.setNp(Np), stage.setNr(Nr), stage.setModule(module), stage.setNumPlanet(n)
    actuator.updateFacewidth()
    actuator.getMassKG_3DP()
    return actuator


def dspg_ring_volume_m3(a, stage):
    """The steel ring of one stage: ring PCD (Nr x module) to + 2 x ring_radial_thickness, fw_r + clearance_planet long."""
    s = getattr(a.doubleStagePlanetaryGearbox, f"Stage{stage}")
    ring_id = s.Nr * s.module
    ring_od = ring_id + 2 * a.ring_radial_thickness
    return math.pi / 4 * (ring_od ** 2 - ring_id ** 2) * (s.fwRingMM + a.clearance_planet) * 1e-9


def dspg_casing_volume_m3(a, stage):
    """The whole casing volume of one stage, from the mass model run with one density for everything."""
    gb = a.doubleStagePlanetaryGearbox
    densities = gb.densityGears, gb.densityStructure
    gb.densityStructure = gb.densityGears
    try:
        a.getMassKG_3DP()
        return getattr(a, f"gearbox_casing_mass_stg{stage}") / gb.densityGears
    finally:
        gb.densityGears, gb.densityStructure = densities
        a.getMassKG_3DP()


@pytest.mark.parametrize("stage", [1, 2])
def test_dspg_metal_ring_is_steel_and_the_housing_aluminium(stage):
    a = build_dspg("metal")
    gb = a.doubleStagePlanetaryGearbox
    assert (gb.densityGears, gb.densityStructure) == (7850, 2700)
    ring, casing = dspg_ring_volume_m3(a, stage), dspg_casing_volume_m3(a, stage)
    assert 0 < ring < casing
    assert getattr(a, f"ring_mass_stg{stage}") == pytest.approx(ring * 7850, rel=1e-9)
    assert getattr(a, f"gearbox_housing_mass_stg{stage}") == pytest.approx((casing - ring) * 2700, rel=1e-9)
    assert getattr(a, f"gearbox_casing_mass_stg{stage}") == pytest.approx(
        getattr(a, f"ring_mass_stg{stage}") + getattr(a, f"gearbox_housing_mass_stg{stage}"), rel=1e-12)


@pytest.mark.parametrize("stage", [1, 2])
def test_dspg_3dp_casing_is_unchanged(stage):
    a = build_dspg("3dp")
    gb = a.doubleStagePlanetaryGearbox
    assert gb.densityGears == gb.densityStructure
    assert getattr(a, f"ring_mass_stg{stage}") == pytest.approx(dspg_ring_volume_m3(a, stage) * gb.densityGears, rel=1e-12)
    assert getattr(a, f"gearbox_housing_mass_stg{stage}") > 0


def test_dspg_metal_optimum_gets_lighter():
    """The re-recorded metal golden design (same gear sets) at 1,241 g, against 1,743 g before the split."""
    assert build_dspg("metal").getMassKG_3DP() == pytest.approx(1.241, abs=0.001)


# ---- INSSPG --------------------------------------------------------------------------------------
# The metal golden designs (RI100, 6.5:1): Ns, Np, Nr, module, planets. The split does not change
# the optimum here, only its mass. "ring_mass" is the whole ring housing in INSSPG; its steel part is
# ring_gear_mass. Type 2 still uses the older ring-housing formula (ISSUES bug 4); the split is the
# same either way.
INSSPG_METAL_DESIGNS = {"insspg_type_1": ((24, 54, 132, 0.6, 3), 1.524),
                        "insspg_type_2": ((25, 56, 137, 0.5, 3), 1.304)}


def build_insspg(gb_type, material):
    actuator, _ = gearbox_runner.build(gb_type, "RI100", material)
    gb = actuator.planetaryGearbox
    Ns, Np, Nr, module, n = INSSPG_METAL_DESIGNS[gb_type][0]
    gb.setNs(Ns), gb.setNp(Np), gb.setNr(Nr), gb.setModule(module), gb.setNumPlanet(n)
    actuator.updateFacewidth()
    actuator.getMassKG_3DP()
    return actuator


def insspg_ring_gear_volume_m3(a):
    """The steel ring: ring PCD (Nr x module) to + 2 x ringRadialWidthMM, fw_r long."""
    gb = a.planetaryGearbox
    ring_id = gb.Nr * gb.module
    return math.pi / 4 * ((ring_id + 2 * a.ringRadialWidthMM) ** 2 - ring_id ** 2) * gb.fwRingMM * 1e-9


def insspg_ring_housing_volume_m3(a):
    """The whole ring-housing volume, from the mass model run with one density for everything."""
    gb = a.planetaryGearbox
    densities = gb.densityGears, gb.densityStructure
    gb.densityStructure = gb.densityGears
    try:
        a.getMassKG_3DP()
        return a.ring_mass / gb.densityGears
    finally:
        gb.densityGears, gb.densityStructure = densities
        a.getMassKG_3DP()


@pytest.mark.parametrize("gb_type", INSSPG_METAL_DESIGNS)
def test_insspg_metal_ring_is_steel_and_the_housing_aluminium(gb_type):
    a = build_insspg(gb_type, "metal")
    gb = a.planetaryGearbox
    assert (gb.densityGears, gb.densityStructure) == (7850, 2700)
    ring, whole = insspg_ring_gear_volume_m3(a), insspg_ring_housing_volume_m3(a)
    assert 0 < ring < whole
    assert a.ring_gear_mass == pytest.approx(ring * 7850, rel=1e-9)
    assert a.ring_housing_mass == pytest.approx((whole - ring) * 2700, rel=1e-9)
    assert a.ring_mass == pytest.approx(a.ring_gear_mass + a.ring_housing_mass, rel=1e-12)


@pytest.mark.parametrize("gb_type", INSSPG_METAL_DESIGNS)
def test_insspg_3dp_ring_is_unchanged(gb_type):
    a = build_insspg(gb_type, "3dp")
    gb = a.planetaryGearbox
    assert gb.densityGears == gb.densityStructure
    assert a.ring_gear_mass == pytest.approx(insspg_ring_gear_volume_m3(a) * gb.densityGears, rel=1e-12)
    assert a.ring_housing_mass > 0


@pytest.mark.parametrize("gb_type", INSSPG_METAL_DESIGNS)
def test_insspg_metal_optimum_gets_lighter(gb_type):
    """The re-recorded metal golden designs (same gear sets): type 1 1,861 -> 1,524 g, type 2 1,616 -> 1,304 g."""
    assert build_insspg(gb_type, "metal").getMassKG_3DP() == pytest.approx(INSSPG_METAL_DESIGNS[gb_type][1], abs=0.001)
