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
INSSPG_METAL_DESIGNS = {"insspg_type_1": ((24, 54, 132, 0.6, 3), 1.499),
                        "insspg_type_2": ((25, 56, 137, 0.5, 3), 1.274)}


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
    """The re-recorded metal golden designs (same gear sets): type 1 1,861 -> 1,499 g, type 2 1,616 -> 1,274 g
    (ring split: 1,524 / 1,304 g; then the sun hub as aluminium)."""
    assert build_insspg(gb_type, "metal").getMassKG_3DP() == pytest.approx(INSSPG_METAL_DESIGNS[gb_type][1], abs=0.001)


# ---- WPG -----------------------------------------------------------------------------------------
# Two rings: ring gear 1 (fixed, in gearbox_casing_mass) and ring gear 2 (the output ring, small_ring_mass).
# Designs (U8_Lite, 20:1): Ns, Np big, Np small, Nr big, Nr small, module, planets.
WPG_OLD_METAL_DESIGN = (36, 56, 36, 148, 128, 0.5, 4)   # the metal golden design before the split
WPG_NEW_METAL_DESIGN = (56, 48, 36, 152, 140, 0.5, 4)   # re-recorded: lower cost (ratio 20.0, narrower gears)


def build_wpg(material, design=WPG_OLD_METAL_DESIGN):
    actuator, _ = gearbox_runner.build("wpg", "U8_Lite", material)
    gb = actuator.wolfromPlanetaryGearbox
    Ns, Np1, Np2, Nr1, Nr2, module, n = design
    gb.setNs(Ns), gb.setNpBig(Np1), gb.setNpSmall(Np2), gb.setNrBig(Nr1), gb.setNrSmall(Nr2)
    gb.setModuleBig(module), gb.setModuleSmall(module), gb.setNumPlanet(n)
    actuator.updateFacewidth()
    actuator.setVariables()
    actuator.getMassKG_3DP()
    return actuator


def wpg_ring_volumes_m3(a):
    """The two steel rings: ring gear 1 from its PCD to bearing_ID + 6 (the mass model's ring_gear1_OD),
    fw_r_b long; ring gear 2 from its PCD to + 2 x module + 2 x small_ring_case_thickness, fw_r_s long."""
    gb = a.wolfromPlanetaryGearbox
    pcd1, pcd2 = gb.NrBig * gb.moduleBig, gb.NrSmall * gb.moduleSmall
    ring1 = math.pi / 4 * ((a.bearing_ID + 4 * a.standard_clearance_1_5mm) ** 2 - pcd1 ** 2) * gb.fwRingBigMM
    od2 = pcd2 + 2 * gb.moduleSmall + 2 * a.small_ring_case_thickness
    ring2 = math.pi / 4 * (od2 ** 2 - pcd2 ** 2) * gb.fwRingSmallMM
    return ring1 * 1e-9, ring2 * 1e-9


def wpg_whole_volumes_m3(a):
    """The whole casing and small-ring volumes, from the mass model run with one density for everything."""
    gb = a.wolfromPlanetaryGearbox
    densities = gb.densityGears, gb.densityStructure
    gb.densityStructure = gb.densityGears
    try:
        a.getMassKG_3DP()
        return a.gearbox_casing_mass / gb.densityGears, a.small_ring_mass / gb.densityGears
    finally:
        gb.densityGears, gb.densityStructure = densities
        a.getMassKG_3DP()


def test_wpg_metal_rings_are_steel_and_the_housings_aluminium():
    a = build_wpg("metal")
    gb = a.wolfromPlanetaryGearbox
    assert (gb.densityGears, gb.densityStructure) == (7850, 2700)
    ring1, ring2 = wpg_ring_volumes_m3(a)
    casing, small_ring = wpg_whole_volumes_m3(a)
    assert 0 < ring1 < casing and 0 < ring2 < small_ring
    assert a.ring_gear1_mass == pytest.approx(ring1 * 7850, rel=1e-9)
    assert a.gearbox_housing_mass == pytest.approx((casing - ring1) * 2700, rel=1e-9)
    assert a.gearbox_casing_mass == pytest.approx(a.ring_gear1_mass + a.gearbox_housing_mass, rel=1e-12)
    assert a.small_ring_gear_mass == pytest.approx(ring2 * 7850, rel=1e-9)
    assert a.small_ring_housing_mass == pytest.approx((small_ring - ring2) * 2700, rel=1e-9)
    assert a.small_ring_mass == pytest.approx(a.small_ring_gear_mass + a.small_ring_housing_mass, rel=1e-12)


def test_wpg_3dp_rings_are_unchanged():
    a = build_wpg("3dp")
    gb = a.wolfromPlanetaryGearbox
    assert gb.densityGears == gb.densityStructure
    ring1, ring2 = wpg_ring_volumes_m3(a)
    assert a.ring_gear1_mass == pytest.approx(ring1 * gb.densityGears, rel=1e-12)
    assert a.small_ring_gear_mass == pytest.approx(ring2 * gb.densityGears, rel=1e-12)
    assert a.gearbox_housing_mass > 0 and a.small_ring_housing_mass > 0


def test_wpg_metal_optimum_gets_lighter():
    """The old metal golden gear set drops from 1,748 g to 1,167 g; the re-recorded optimum
    (56/48/36/152/140) is 1,238 g."""
    assert build_wpg("metal").getMassKG_3DP() == pytest.approx(1.167, abs=0.001)
    assert build_wpg("metal", WPG_NEW_METAL_DESIGN).getMassKG_3DP() == pytest.approx(1.238, abs=0.001)


# ---- INWPG ---------------------------------------------------------------------------------------
# As WPG: ring gear 1 (fixed, in gearbox_casing_mass) and ring gear 2 (the output ring, small_ring_mass).
# Golden metal designs (RI100, 20:1): Ns, Np big, Nr big, Np small, Nr small, module big, module small,
# planets (the order of tests/test_fresh_design_state.py); the split does not change the optimum here.
INWPG_METAL = {"inwpg_dependent": ((18, 36, 90, 21, 75, 0.8, 0.8, 3), 1.673),
               "inwpg_independent": ((54, 30, 114, 24, 108, 0.6, 0.6, 6), 1.802)}


def build_inwpg(gb_type, material):
    sys.path.insert(0, str(REPO / "tests"))
    from test_fresh_design_state import set_design
    actuator, _ = gearbox_runner.build(gb_type, "RI100", material)
    set_design(actuator, gb_type, INWPG_METAL[gb_type][0])
    actuator.updateFacewidth()
    actuator.getMassKG_3DP()
    return actuator


def inwpg_ring_volumes_m3(a):
    """The two steel rings: ring gear 1 from its PCD to + 2 x module + 2 x ringRadialWidthMMBig (the code's
    ring_OD), fw_r_b long; ring gear 2 from its PCD to + 2 x module + 2 x ringRadialWidthMMSmall, fw_r_s long."""
    gb = a.inrunnerWolfromPlanetaryGearbox
    m = gb.moduleBig
    pcd1, pcd2 = gb.NrBig * m, gb.NrSmall * m
    ring1 = math.pi / 4 * ((pcd1 + 2 * m + 2 * a.ring1RadialWidthMM) ** 2 - pcd1 ** 2) * gb.fwRingBigMM
    ring2 = math.pi / 4 * ((pcd2 + 2 * m + 2 * a.small_ring_radial_width) ** 2 - pcd2 ** 2) * gb.fwRingSmallMM
    return ring1 * 1e-9, ring2 * 1e-9


def inwpg_whole_volumes_m3(a):
    """The whole casing and small-ring volumes, from the mass model run with one density for everything."""
    gb = a.inrunnerWolfromPlanetaryGearbox
    densities = gb.densityGears, gb.densityStructure
    gb.densityStructure = gb.densityGears
    try:
        a.getMassKG_3DP()
        return a.gearbox_casing_mass / gb.densityGears, a.small_ring_mass / gb.densityGears
    finally:
        gb.densityGears, gb.densityStructure = densities
        a.getMassKG_3DP()


@pytest.mark.parametrize("gb_type", INWPG_METAL)
def test_inwpg_metal_rings_are_steel_and_the_housings_aluminium(gb_type):
    a = build_inwpg(gb_type, "metal")
    gb = a.inrunnerWolfromPlanetaryGearbox
    assert (gb.densityGears, gb.densityStructure) == (7850, 2700)
    ring1, ring2 = inwpg_ring_volumes_m3(a)
    casing, small_ring = inwpg_whole_volumes_m3(a)
    assert 0 < ring1 < casing and 0 < ring2 < small_ring
    assert a.ring_gear1_mass == pytest.approx(ring1 * 7850, rel=1e-9)
    assert a.gearbox_housing_mass == pytest.approx((casing - ring1) * 2700, rel=1e-9)
    assert a.gearbox_casing_mass == pytest.approx(a.ring_gear1_mass + a.gearbox_housing_mass, rel=1e-12)
    assert a.small_ring_gear_mass == pytest.approx(ring2 * 7850, rel=1e-9)
    assert a.small_ring_housing_mass == pytest.approx((small_ring - ring2) * 2700, rel=1e-9)
    assert a.small_ring_mass == pytest.approx(a.small_ring_gear_mass + a.small_ring_housing_mass, rel=1e-12)


@pytest.mark.parametrize("gb_type", INWPG_METAL)
def test_inwpg_3dp_rings_are_unchanged(gb_type):
    a = build_inwpg(gb_type, "3dp")
    gb = a.inrunnerWolfromPlanetaryGearbox
    assert gb.densityGears == gb.densityStructure
    ring1, ring2 = inwpg_ring_volumes_m3(a)
    assert a.ring_gear1_mass == pytest.approx(ring1 * gb.densityGears, rel=1e-12)
    assert a.small_ring_gear_mass == pytest.approx(ring2 * gb.densityGears, rel=1e-12)
    assert a.gearbox_housing_mass > 0 and a.small_ring_housing_mass > 0


@pytest.mark.parametrize("gb_type", INWPG_METAL)
def test_inwpg_metal_optimum_gets_lighter(gb_type):
    """The re-recorded metal golden designs (same gear sets): dependent 2,410 -> 1,673 g,
    independent 2,517 -> 1,802 g (rings: 1,718 / 1,854 g; then the sun hub as aluminium)."""
    assert build_inwpg(gb_type, "metal").getMassKG_3DP() == pytest.approx(INWPG_METAL[gb_type][1], abs=0.001)


# ---- IDSPG ---------------------------------------------------------------------------------------
# Stage 1's ring housing reaches the stator bore; only pitch -> pitch + 2 x ring1RadialWidthMM is steel (the
# stage-1 search keeps that inside the bore). Stage 2's ring_gear_volume is the steel ring (as DSPG).
# Golden metal design (RO100, 20:1), per stage: Ns, Np, Nr, module, planets; the split keeps the optimum.
IDSPG_METAL_DESIGN = ((30, 45, 120, 0.5, 3), (41, 41, 123, 0.8, 4))


def build_idspg(material):
    sys.path.insert(0, str(REPO / "tests"))
    from test_fresh_design_state import set_design
    actuator, _ = gearbox_runner.build("idspg", "RO100", material)
    set_design(actuator, "idspg", IDSPG_METAL_DESIGN)
    actuator.updateFacewidth()
    actuator.getMassKG_3DP()
    return actuator


def idspg_steel_volumes_m3(a):
    gb = a.internaldoubleStagePlanetaryGearbox
    s1, s2 = gb.Stage1, gb.Stage2
    pcd1, pcd2 = s1.Nr * s1.module, s2.Nr * s2.module
    od1 = pcd1 + 2 * a.ring1RadialWidthMM
    assert od1 <= a.Stator_ID                       # inside the stator bore, as the search guarantees
    ring1 = math.pi / 4 * (od1 ** 2 - pcd1 ** 2) * (s1.fwRingMM + 0.5 * a.clearance_planet + a.standard_clearance_1_5mm)
    ring2 = math.pi / 4 * ((pcd2 + 2 * a.ring_radial_thickness) ** 2 - pcd2 ** 2) \
        * (s2.fwRingMM + a.clearance_planet + a.standard_clearance_1_5mm)
    return ring1 * 1e-9, ring2 * 1e-9


def idspg_ring_housing_volumes_m3(a):
    """Each stage's whole ring-housing volume, from the mass model run with one density for everything."""
    gb = a.internaldoubleStagePlanetaryGearbox
    densities = gb.densityGears, gb.densityStructure
    gb.densityStructure = gb.densityGears
    try:
        a.getMassKG_3DP()
        return a.ring_gear_mass_stg1 / gb.densityGears, a.ring_gear_mass_stg2 / gb.densityGears
    finally:
        gb.densityGears, gb.densityStructure = densities
        a.getMassKG_3DP()


@pytest.mark.parametrize("stage", [1, 2])
def test_idspg_metal_ring_is_steel_and_the_housing_aluminium(stage):
    a = build_idspg("metal")
    gb = a.internaldoubleStagePlanetaryGearbox
    assert (gb.densityGears, gb.densityStructure) == (7850, 2700)
    ring = idspg_steel_volumes_m3(a)[stage - 1]
    whole = idspg_ring_housing_volumes_m3(a)[stage - 1]
    assert 0 < ring < whole
    assert getattr(a, f"ring_gear_steel_mass_stg{stage}") == pytest.approx(ring * 7850, rel=1e-9)
    assert getattr(a, f"ring_housing_mass_stg{stage}") == pytest.approx((whole - ring) * 2700, rel=1e-9)
    assert getattr(a, f"ring_gear_mass_stg{stage}") == pytest.approx(
        getattr(a, f"ring_gear_steel_mass_stg{stage}") + getattr(a, f"ring_housing_mass_stg{stage}"), rel=1e-12)


@pytest.mark.parametrize("stage", [1, 2])
def test_idspg_3dp_ring_is_unchanged(stage):
    a = build_idspg("3dp")
    gb = a.internaldoubleStagePlanetaryGearbox
    assert gb.densityGears == gb.densityStructure
    ring = idspg_steel_volumes_m3(a)[stage - 1]
    assert getattr(a, f"ring_gear_steel_mass_stg{stage}") == pytest.approx(ring * gb.densityGears, rel=1e-12)
    assert getattr(a, f"ring_housing_mass_stg{stage}") > 0


def idspg_sun1_hub_volume_m3(a):
    """The stage-1 sun's coupler hub (aluminium in metal mode): a disc of the hub diameter, minus its
    share of the central bolt hole (the hole runs through the sun gear and the hub). The hub is the CAD's:
    the rotor's mount-hole circle + hole + sun_hub_clearance_multiple (5) x standard_clearance_1_5mm."""
    hub_dia = a.rotor_mount_hole_PCD + a.rotor_mount_hole_dia + a.sun_hub_clearance_multiple * a.standard_clearance_1_5mm
    assert hub_dia == a.sun_hub_dia1
    t, fw = a.sun_coupler_hub_thickness1, a.fw_s1_used
    hub = math.pi / 4 * hub_dia ** 2 * t
    bolt_share = math.pi / 4 * a.sun_central_bolt_dia1 ** 2 * (fw + t) * t / (fw + t)
    return (hub - bolt_share) * 1e-9


def test_idspg_metal_stage1_sun_is_steel_and_its_hub_aluminium():
    a = build_idspg("metal")
    gb = a.internaldoubleStagePlanetaryGearbox
    densities = gb.densityGears, gb.densityStructure
    gb.densityStructure = gb.densityGears
    a.getMassKG_3DP()
    whole = a.sun_mass_stg1 / gb.densityGears
    gb.densityGears, gb.densityStructure = densities
    a.getMassKG_3DP()
    hub = idspg_sun1_hub_volume_m3(a)
    assert 0 < hub < whole
    assert a.sun_hub_mass_stg1 == pytest.approx(hub * 2700, rel=1e-9)
    assert a.sun_steel_mass_stg1 == pytest.approx((whole - hub) * 7850, rel=1e-9)
    assert a.sun_mass_stg1 == pytest.approx(a.sun_steel_mass_stg1 + a.sun_hub_mass_stg1, rel=1e-12)


def test_idspg_3dp_stage1_sun_is_unchanged():
    a = build_idspg("3dp")
    gb = a.internaldoubleStagePlanetaryGearbox
    assert a.sun_hub_mass_stg1 == pytest.approx(idspg_sun1_hub_volume_m3(a) * gb.densityGears, rel=1e-12)


def test_idspg_metal_optimum_gets_lighter():
    """The re-recorded metal golden design (same gear sets): 3,003 -> 2,429 g (rings 2,543 g, plus the
    stage-1 sun hub as aluminium), then 2,431 g once the mass code weighs the CAD's wider sun hub."""
    assert build_idspg("metal").getMassKG_3DP() == pytest.approx(2.431, abs=0.001)


# ---- INDSPG --------------------------------------------------------------------------------------
# Stage 1's ring housing reaches the rotor bore; only pitch -> pitch + 2 x ring_radial_thickness is steel,
# clipped at the bore (the stage-1 search only guarantees ~2.2 mm there). Stage 2's ring_gear_volume is
# the steel ring (as DSPG). The stage-1 sun hub is aluminium. Golden metal design (RI100, 20:1), per stage:
# Ns, Np, Nr, module, planets; the split keeps the optimum.
INDSPG_METAL_DESIGN = ((21, 24, 69, 0.5, 3), (27, 36, 99, 0.6, 3))


def build_indspg(material):
    sys.path.insert(0, str(REPO / "tests"))
    from test_fresh_design_state import set_design
    actuator, _ = gearbox_runner.build("indspg", "RI100", material)
    set_design(actuator, "indspg", INDSPG_METAL_DESIGN)
    actuator.updateFacewidth()
    actuator.getMassKG_3DP()
    return actuator


def indspg_steel_volumes_m3(a):
    """Stage-1 ring, stage-2 ring and the stage-1 sun hub (aluminium) volumes."""
    gb = a.inrunnerdoubleStagePlanetaryGearbox
    s1, s2 = gb.Stage1, gb.Stage2
    pcd1, pcd2 = s1.Nr * s1.module, s2.Nr * s2.module
    od1 = min(pcd1 + 2 * a.ring_radial_thickness, a.rotor_ID - 2 * a.loose_clearance_3DP)
    ring1 = math.pi / 4 * (od1 ** 2 - pcd1 ** 2) * s1.fwRingMM
    ring2 = math.pi / 4 * ((pcd2 + 2 * a.ring_radial_thickness) ** 2 - pcd2 ** 2) * a.fw_r2
    hub = math.pi / 4 * a.sun_hub_dia1 ** 2 * a.sun_coupler_hub_thickness1
    return ring1 * 1e-9, ring2 * 1e-9, hub * 1e-9


def indspg_whole_volumes_m3(a):
    """Stage-1 / stage-2 ring housings and the stage-1 sun, from the mass model run with one density."""
    gb = a.inrunnerdoubleStagePlanetaryGearbox
    densities = gb.densityGears, gb.densityStructure
    gb.densityStructure = gb.densityGears
    try:
        a.getMassKG_3DP()
        return tuple(m / gb.densityGears for m in (a.ring_gear_mass_stg1, a.ring_gear_mass_stg2, a.sun_mass_stg1))
    finally:
        gb.densityGears, gb.densityStructure = densities
        a.getMassKG_3DP()


@pytest.mark.parametrize("stage", [1, 2])
def test_indspg_metal_ring_is_steel_and_the_housing_aluminium(stage):
    a = build_indspg("metal")
    gb = a.inrunnerdoubleStagePlanetaryGearbox
    assert (gb.densityGears, gb.densityStructure) == (7850, 2700)
    ring = indspg_steel_volumes_m3(a)[stage - 1]
    whole = indspg_whole_volumes_m3(a)[stage - 1]
    assert 0 < ring < whole
    assert getattr(a, f"ring_gear_steel_mass_stg{stage}") == pytest.approx(ring * 7850, rel=1e-9)
    assert getattr(a, f"ring_housing_mass_stg{stage}") == pytest.approx((whole - ring) * 2700, rel=1e-9)
    assert getattr(a, f"ring_gear_mass_stg{stage}") == pytest.approx(
        getattr(a, f"ring_gear_steel_mass_stg{stage}") + getattr(a, f"ring_housing_mass_stg{stage}"), rel=1e-12)


def test_indspg_metal_stage1_sun_is_steel_and_its_hub_aluminium():
    a = build_indspg("metal")
    hub = indspg_steel_volumes_m3(a)[2]
    whole = indspg_whole_volumes_m3(a)[2]
    assert 0 < hub < whole
    assert a.sun_hub_mass_stg1 == pytest.approx(hub * 2700, rel=1e-9)
    assert a.sun_steel_mass_stg1 == pytest.approx((whole - hub) * 7850, rel=1e-9)


def test_indspg_3dp_is_unchanged():
    a = build_indspg("3dp")
    gb = a.inrunnerdoubleStagePlanetaryGearbox
    assert gb.densityGears == gb.densityStructure
    ring1, ring2, hub = indspg_steel_volumes_m3(a)
    assert a.ring_gear_steel_mass_stg1 == pytest.approx(ring1 * gb.densityGears, rel=1e-12)
    assert a.ring_gear_steel_mass_stg2 == pytest.approx(ring2 * gb.densityGears, rel=1e-12)
    assert a.sun_hub_mass_stg1 == pytest.approx(hub * gb.densityGears, rel=1e-12)


def test_indspg_metal_optimum_gets_lighter():
    """The re-recorded metal golden design (same gear sets): 2,032 -> 1,445 g."""
    assert build_indspg("metal").getMassKG_3DP() == pytest.approx(1.445, abs=0.001)


# ---- ISSPG ---------------------------------------------------------------------------------------
# The ring housing reaches the stator bore; only pitch -> pitch + 2 x module + 2 x ring_stator_case_thickness
# (the ring maxRingGearOD() allows) is steel. Golden metal design (RO100, 6.5:1) for both types:
# Ns, Np, Nr, module, planets; the split keeps the optimum.
ISSPG_METAL = {"isspg_compact": 1.702, "isspg_inside": 1.782}
ISSPG_METAL_DESIGN = (24, 54, 132, 0.5, 3)


def build_isspg(gb_type, material):
    actuator, _ = gearbox_runner.build(gb_type, "RO100", material)
    gb = actuator.planetaryGearbox
    Ns, Np, Nr, module, n = ISSPG_METAL_DESIGN
    gb.setNs(Ns), gb.setNp(Np), gb.setNr(Nr), gb.setModule(module), gb.setNumPlanet(n)
    actuator.updateFacewidth()
    actuator.getMassKG_3DP()
    return actuator


def isspg_ring_steel_volume_m3(a, gb_type):
    gb = a.planetaryGearbox
    pcd = gb.Nr * gb.module
    od = pcd + 2 * gb.module + 2 * a.ring_stator_case_thickness
    assert od <= a.stator_ID                         # maxRingGearOD() keeps it inside the bore
    length = gb.fwRingMM + (a.clearance_planet if gb_type == "isspg_compact" else 0)
    return math.pi / 4 * (od ** 2 - pcd ** 2) * length * 1e-9


def isspg_ring_housing_volume_m3(a):
    gb = a.planetaryGearbox
    densities = gb.densityGears, gb.densityStructure
    gb.densityStructure = gb.densityGears
    try:
        a.getMassKG_3DP()
        return a.ring_mass / gb.densityGears
    finally:
        gb.densityGears, gb.densityStructure = densities
        a.getMassKG_3DP()


@pytest.mark.parametrize("gb_type", ISSPG_METAL)
def test_isspg_metal_ring_is_steel_and_the_housing_aluminium(gb_type):
    a = build_isspg(gb_type, "metal")
    gb = a.planetaryGearbox
    assert (gb.densityGears, gb.densityStructure) == (7850, 2700)
    ring, whole = isspg_ring_steel_volume_m3(a, gb_type), isspg_ring_housing_volume_m3(a)
    assert 0 < ring < whole
    assert a.ring_gear_steel_mass == pytest.approx(ring * 7850, rel=1e-9)
    assert a.ring_housing_mass == pytest.approx((whole - ring) * 2700, rel=1e-9)
    assert a.ring_mass == pytest.approx(a.ring_gear_steel_mass + a.ring_housing_mass, rel=1e-12)


@pytest.mark.parametrize("gb_type", ISSPG_METAL)
def test_isspg_3dp_ring_is_unchanged(gb_type):
    a = build_isspg(gb_type, "3dp")
    gb = a.planetaryGearbox
    assert gb.densityGears == gb.densityStructure
    assert a.ring_gear_steel_mass == pytest.approx(isspg_ring_steel_volume_m3(a, gb_type) * gb.densityGears, rel=1e-12)
    assert a.ring_housing_mass > 0


def isspg_sun_steel_volume_m3(a, gb_type):
    """The steel part of the sun: gear + sun-1 bearing shaft (+ the input-bearing journal in compact), each
    minus the central bolt hole over its length. The hub (minus its recess) and, in inside, the encoder
    magnet holder are aluminium."""
    gb = a.planetaryGearbox
    pieces = [(gb.Ns * gb.module, a.fw_s_used), (a.sun1_bearing_ID, a.sun1_bearing_width + a.bearing_step_width)]
    if gb_type == "isspg_compact":
        pieces.append((a.input_bearing_ID, a.input_bearing_width + a.bearing_step_width))
    solid = sum(d ** 2 * h for d, h in pieces)
    bolt = a.sun_central_bolt_dia ** 2 * sum(h for _, h in pieces)
    return math.pi / 4 * (solid - bolt) * 1e-9


@pytest.mark.parametrize("gb_type", ISSPG_METAL)
def test_isspg_metal_sun_is_steel_and_its_hub_aluminium(gb_type):
    a = build_isspg(gb_type, "metal")
    gb = a.planetaryGearbox
    densities = gb.densityGears, gb.densityStructure
    gb.densityStructure = gb.densityGears
    a.getMassKG_3DP()
    whole = a.sun_mass / gb.densityGears
    gb.densityGears, gb.densityStructure = densities
    a.getMassKG_3DP()
    steel = isspg_sun_steel_volume_m3(a, gb_type)
    assert 0 < steel < whole
    assert a.sun_steel_mass == pytest.approx(steel * 7850, rel=1e-9)
    assert a.sun_hub_mass == pytest.approx((whole - steel) * 2700, rel=1e-9)


@pytest.mark.parametrize("gb_type", ISSPG_METAL)
def test_isspg_3dp_sun_is_unchanged(gb_type):
    a = build_isspg(gb_type, "3dp")
    gb = a.planetaryGearbox
    assert a.sun_steel_mass == pytest.approx(isspg_sun_steel_volume_m3(a, gb_type) * gb.densityGears, rel=1e-12)
    assert a.sun_hub_mass > 0


@pytest.mark.parametrize("gb_type", ISSPG_METAL)
def test_isspg_metal_optimum_gets_lighter(gb_type):
    """The re-recorded metal golden designs (same gear set): compact 2,117 -> 1,702 g, inside 2,192 -> 1,782 g
    (rings: 1,939 / 2,025 g; then the sun hub as aluminium)."""
    assert build_isspg(gb_type, "metal").getMassKG_3DP() == pytest.approx(ISSPG_METAL[gb_type], abs=0.001)


# ---- INCPG ---------------------------------------------------------------------------------------
# The ring piece runs out to the bearing holder / case mounting; only pitch -> the code's ring_OD
# (pitch + module + 2 x ringRadialWidthMM) is steel. The sun hub (and the magnet-carrying journal / shaft)
# is aluminium. Golden metal design (RI100, 10:1) for both: Ns, Np big, Np small, Nr, modules, planets.
INCPG_METAL = {"incpg_dependent": 1.320, "incpg_independent": 1.423}


def build_incpg(gb_type, material):
    actuator, _ = gearbox_runner.build(gb_type, "RI100", material)
    gb = actuator.inrunnerCompoundPlanetaryGearbox
    gb.setNs(21), gb.setNpBig(54), gb.setNpSmall(30), gb.setNr(105)
    gb.setModuleBig(0.6), gb.setModuleSmall(0.6), gb.setNumPlanet(3)
    actuator.updateFacewidth()
    actuator.getMassKG_3DP()
    return actuator


def incpg_whole_volumes_m3(a):
    """The whole casing and sun volumes, from the mass model run with one density for everything."""
    gb = a.inrunnerCompoundPlanetaryGearbox
    densities = gb.densityGears, gb.densityStructure
    gb.densityStructure = gb.densityGears
    try:
        a.getMassKG_3DP()
        return a.gearbox_casing_mass / gb.densityGears, a.sun_mass / gb.densityGears
    finally:
        gb.densityGears, gb.densityStructure = densities
        a.getMassKG_3DP()


@pytest.mark.parametrize("gb_type", INCPG_METAL)
def test_incpg_metal_ring_and_sun_split(gb_type):
    a = build_incpg(gb_type, "metal")
    gb = a.inrunnerCompoundPlanetaryGearbox
    assert (gb.densityGears, gb.densityStructure) == (7850, 2700)
    pcd = gb.Nr * gb.moduleSmall
    ring = math.pi / 4 * ((pcd + gb.moduleSmall + 2 * a.ringRadialWidthMM) ** 2 - pcd ** 2) * (gb.fwRingMM + a.standard_clearance_1_5mm) * 1e-9
    casing, sun = incpg_whole_volumes_m3(a)
    assert 0 < ring < casing
    assert a.ring_gear_mass == pytest.approx(ring * 7850, rel=1e-9)
    assert a.gearbox_housing_mass == pytest.approx((casing - ring) * 2700, rel=1e-9)
    assert a.gearbox_casing_mass == pytest.approx(a.ring_gear_mass + a.gearbox_housing_mass, rel=1e-12)
    steel = a.sun_steel_mass / 7850
    assert 0 < steel < sun
    assert a.sun_hub_mass == pytest.approx((sun - steel) * 2700, rel=1e-9)


@pytest.mark.parametrize("gb_type", INCPG_METAL)
def test_incpg_3dp_is_unchanged(gb_type):
    a = build_incpg(gb_type, "3dp")
    gb = a.inrunnerCompoundPlanetaryGearbox
    assert gb.densityGears == gb.densityStructure
    pcd = gb.Nr * gb.moduleSmall
    ring = math.pi / 4 * ((pcd + gb.moduleSmall + 2 * a.ringRadialWidthMM) ** 2 - pcd ** 2) * (gb.fwRingMM + a.standard_clearance_1_5mm) * 1e-9
    assert a.ring_gear_mass == pytest.approx(ring * gb.densityGears, rel=1e-12)
    assert a.gearbox_housing_mass > 0 and a.sun_hub_mass > 0


@pytest.mark.parametrize("gb_type", INCPG_METAL)
def test_incpg_metal_optimum_gets_lighter(gb_type):
    """The re-recorded metal golden designs (same gear set): dependent 1,776 -> 1,320 g, independent 1,848 -> 1,423 g."""
    assert build_incpg(gb_type, "metal").getMassKG_3DP() == pytest.approx(INCPG_METAL[gb_type], abs=0.001)


# ---- ICPG ----------------------------------------------------------------------------------------
# Already split by name (density_steel / density_alum). The ring's teeth piece reaches the stator bore; only
# pitch -> min(pitch + 2 x ringRadialWidthMM, bore) over the teeth length is steel. The sun's base flange (the
# rotor-coupler hub, which also seats the bottom-casing bearing) is aluminium; teeth and support bulge steel.
# Golden metal design (RO100, 10:1): Ns, Np big, Np small, Nr, module, planets; the split keeps the optimum.
def build_icpg(material):
    actuator, _ = gearbox_runner.build("icpg", "RO100", material)
    gb = actuator.internalcompoundPlanetaryGearbox
    gb.setNs(18), gb.setNpBig(49), gb.setNpSmall(29), gb.setNr(96)
    gb.setModuleBig(0.6), gb.setModuleSmall(0.6), gb.setNumPlanet(3)
    actuator.updateFacewidth()
    actuator.getMassKG_3DP()
    return actuator


def icpg_ring_steel_volume_m3(a):
    pcd = a.Nr * a.module_s
    od = min(pcd + 2 * a.ringRadialWidthMM, a.stator_ID)
    teeth_length = (a.fw_r + 2 * a.standard_clearance_1_5mm
                    - (a.fw_s_used - a.rotor_bottom_thickness - a.stator_height - a.ring_gear_thickness_mounting_casing))
    return math.pi / 4 * (od ** 2 - pcd ** 2) * teeth_length * 1e-9


def icpg_whole_volumes_m3(a):
    gb = a.internalcompoundPlanetaryGearbox
    densities = gb.densityGears, gb.densityStructure
    gb.densityStructure = gb.densityGears
    try:
        a.getMassKG_3DP()
        return a.ring_gear_mass_kg / gb.densityGears, a.sun_gear_mass_kg / gb.densityGears
    finally:
        gb.densityGears, gb.densityStructure = densities
        a.getMassKG_3DP()


def test_icpg_metal_ring_and_sun_split():
    a = build_icpg("metal")
    gb = a.internalcompoundPlanetaryGearbox
    assert (gb.densityGears, gb.densityStructure) == (7850, 2700)
    ring, (ring_whole, sun_whole) = icpg_ring_steel_volume_m3(a), icpg_whole_volumes_m3(a)
    assert 0 < ring < ring_whole
    assert a.ring_steel_mass_kg == pytest.approx(ring * 7850, rel=1e-9)
    assert a.ring_housing_mass_kg == pytest.approx((ring_whole - ring) * 2700, rel=1e-9)
    assert a.ring_gear_mass_kg == pytest.approx(a.ring_steel_mass_kg + a.ring_housing_mass_kg, rel=1e-12)
    sun_steel = a.sun_steel_mass_kg / 7850
    assert 0 < sun_steel < sun_whole
    assert a.sun_hub_mass_kg == pytest.approx((sun_whole - sun_steel) * 2700, rel=1e-9)


def test_icpg_3dp_is_unchanged():
    a = build_icpg("3dp")
    gb = a.internalcompoundPlanetaryGearbox
    assert gb.densityGears == gb.densityStructure
    assert a.ring_steel_mass_kg == pytest.approx(icpg_ring_steel_volume_m3(a) * gb.densityGears, rel=1e-12)
    assert a.ring_housing_mass_kg > 0 and a.sun_hub_mass_kg > 0


def test_icpg_metal_optimum_gets_lighter():
    """The re-recorded metal golden design (same gear set): 2,714 -> 2,125 g."""
    assert build_icpg("metal").getMassKG_3DP() == pytest.approx(2.125, abs=0.001)


# ---- Sun hubs: INSSPG and INWPG ------------------------------------------------------------------
# The rotor-coupler hub (and the INSSPG bottom part / the INWPG magnet carrier) is aluminium, the rest of the
# sun steel. The two parts add up to the whole sun volume; in 3D-printed mode the sun is unchanged.
def _sun_whole_volume_m3(a, gb):
    densities = gb.densityGears, gb.densityStructure
    gb.densityStructure = gb.densityGears
    try:
        a.getMassKG_3DP()
        return a.sun_mass / gb.densityGears
    finally:
        gb.densityGears, gb.densityStructure = densities
        a.getMassKG_3DP()


SUN_HUB_CASES = [("insspg_type_1", build_insspg, "planetaryGearbox"), ("insspg_type_2", build_insspg, "planetaryGearbox"),
                 ("inwpg_dependent", build_inwpg, "inrunnerWolfromPlanetaryGearbox"),
                 ("inwpg_independent", build_inwpg, "inrunnerWolfromPlanetaryGearbox")]


@pytest.mark.parametrize("gb_type, build, gearbox", SUN_HUB_CASES, ids=[c[0] for c in SUN_HUB_CASES])
def test_metal_sun_is_steel_and_its_hub_aluminium(gb_type, build, gearbox):
    a = build(gb_type, "metal")
    gb = getattr(a, gearbox)
    whole = _sun_whole_volume_m3(a, gb)
    steel, hub = a.sun_steel_mass / 7850, a.sun_hub_mass / 2700
    assert 0 < steel < whole and hub > 0
    assert steel + hub == pytest.approx(whole, rel=1e-9)
    hub_disc = math.pi / 4 * a.sun_hub_dia ** 2 * a.sun_coupler_hub_thickness * 1e-9 if gb_type.startswith("insspg") else 0
    assert hub > hub_disc * 0.99      # at least the hub disc is aluminium


@pytest.mark.parametrize("gb_type, build, gearbox", SUN_HUB_CASES, ids=[c[0] for c in SUN_HUB_CASES])
def test_3dp_sun_is_unchanged(gb_type, build, gearbox):
    a = build(gb_type, "3dp")
    gb = getattr(a, gearbox)
    assert a.sun_mass == pytest.approx(_sun_whole_volume_m3(a, gb) * gb.densityGears, rel=1e-12)
    assert a.sun_mass == pytest.approx(a.sun_steel_mass + a.sun_hub_mass, rel=1e-12)
