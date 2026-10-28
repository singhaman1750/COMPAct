"""The fast two-stage search (two_stage_search.py) must evaluate exactly the pairs the original
nested loops evaluated, in the same order, with the same counts. The original loops are
reproduced here as a slow reference and run on a small search (narrow diameter and planet
counts) so the comparison takes seconds; the golden check covers the full-size searches."""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import gearbox_runner  # noqa: E402
from two_stage_search import pair_counts, pairs_in_ratio_bin, stage_designs  # noqa: E402

# gearbox type -> (golden motor, gearbox attribute, stage-1 diameter attribute, extra stage-2 checks,
#                  small stage-1 / stage-2 diameters in mm)
TYPES = {
    "dspg":   ("U8_Lite", "doubleStagePlanetaryGearbox", "maxGearboxDiameter", [], (50.0, 50.0)),
    "idspg":  ("RO100", "internaldoubleStagePlanetaryGearbox", "maxGearboxDiameter_Stg1", [], (45.0, 70.0)),
    "indspg": ("RI100", "inrunnerdoubleStagePlanetaryGearbox", "maxGearboxDiameter_Stg1", ["additionalConstraints"],
               (39.0, 60.0)),
}
RATIO_BINS = [(8.0, 9.0), (9.5, 10.5), (12.0, 13.0), (15.0, 16.0), (19.5, 20.5)]


def small_search(gb_type):
    motor, gb_attr, dia1_attr, extra2, (dia1, dia2) = TYPES[gb_type]
    actuator, opt = gearbox_runner.build(gb_type, motor)
    actuator.maxGearboxDiameter = dia2
    setattr(actuator, dia1_attr, dia1)
    opt.NUM_PLANET_STAGE1_MAX = opt.NUM_PLANET_STAGE1_MIN + 1
    opt.NUM_PLANET_STAGE2_MAX = opt.NUM_PLANET_STAGE2_MIN + 1
    return actuator, opt, getattr(actuator, gb_attr), getattr(actuator, dia1_attr), extra2


def reference(actuator, opt, gb, dia1, extra2):
    """The original nested loops, checks on every pair; returns (feasible pairs with their ratio,
    in visiting order, pairs tried, pairs feasible)."""
    s1, s2, dia2 = gb.Stage1, gb.Stage2, actuator.maxGearboxDiameter
    found, tried, feasible = [], 0, 0
    s1.setModule(opt.MODULE_STAGE1_MIN)
    while s1.module <= opt.MODULE_STAGE1_MAX:
        s2.setModule(opt.MODULE_STAGE2_MIN)
        while s2.module <= opt.MODULE_STAGE2_MAX:
            s1.setNs(opt.NUM_TEETH_SUN_MIN)
            while 2*s1.getPCRadiusSunMM() <= dia1:
                s1.setNp(opt.NUM_TEETH_PLANET_MIN)
                while 2*s1.getPCRadiusPlanetMM() <= dia1/2:
                    s1.setNr(2*s1.Np + s1.Ns)
                    if 2*s1.getPCRadiusRingMM() <= dia1:
                        s1.setNumPlanet(opt.NUM_PLANET_STAGE1_MIN)
                        while s1.numPlanet <= opt.NUM_PLANET_STAGE1_MAX:
                            s2.setNs(opt.NUM_TEETH_SUN_MIN)
                            while 2*s2.getPCRadiusSunMM() <= dia2:
                                s2.setNp(opt.NUM_TEETH_PLANET_MIN)
                                while 2*s2.getPCRadiusPlanetMM() <= dia2/2:
                                    s2.setNr(2*s2.Np + s2.Ns)
                                    if 2*s2.getPCRadiusRingMM() <= dia2:
                                        s2.setNumPlanet(opt.NUM_PLANET_STAGE2_MIN)
                                        while s2.numPlanet <= opt.NUM_PLANET_STAGE2_MAX:
                                            tried += 1
                                            if (gb.geometricConstraint() and gb.meshingConstraint()
                                                    and all(getattr(gb, c)() for c in extra2)
                                                    and gb.noPlanetInterferenceConstraint()):
                                                feasible += 1
                                                found.append(((s1.module, (s1.Ns, s1.Np, s1.Nr, s1.numPlanet),
                                                               s2.module, (s2.Ns, s2.Np, s2.Nr, s2.numPlanet)),
                                                              gb.gearRatio()))
                                            s2.setNumPlanet(s2.numPlanet + 1)
                                    s2.setNp(s2.Np + 1)
                                s2.setNs(s2.Ns + 1)
                            s1.setNumPlanet(s1.numPlanet + 1)
                    s1.setNp(s1.Np + 1)
                s1.setNs(s1.Ns + 1)
            s2.setModule(round(s2.module + 0.100, 1))
        s1.setModule(round(s1.module + 0.100, 1))
    return found, tried, feasible


@pytest.mark.parametrize("gb_type", sorted(TYPES))
def test_fast_search_evaluates_the_same_pairs_in_the_same_order(gb_type):
    actuator, opt, gb, dia1, extra2 = small_search(gb_type)
    stage1 = stage_designs(gb.Stage1, opt.MODULE_STAGE1_MIN, opt.MODULE_STAGE1_MAX,
                           opt.NUM_TEETH_SUN_MIN, opt.NUM_TEETH_PLANET_MIN,
                           opt.NUM_PLANET_STAGE1_MIN, opt.NUM_PLANET_STAGE1_MAX, dia1,
                           lambda: (gb.Stage1.geometricConstraint() and gb.Stage1.meshingConstraint()
                                    and gb.noPlanetInterferenceConstraintStg1()))
    stage2 = stage_designs(gb.Stage2, opt.MODULE_STAGE2_MIN, opt.MODULE_STAGE2_MAX,
                           opt.NUM_TEETH_SUN_MIN, opt.NUM_TEETH_PLANET_MIN,
                           opt.NUM_PLANET_STAGE2_MIN, opt.NUM_PLANET_STAGE2_MAX, actuator.maxGearboxDiameter,
                           lambda: (gb.Stage2.geometricConstraint() and gb.Stage2.meshingConstraint()
                                    and all(getattr(gb, c)() for c in extra2)
                                    and gb.noPlanetInterferenceConstraintStg2()))
    feasible_pairs, tried, feasible = reference(actuator, opt, gb, dia1, extra2)
    assert pair_counts(stage1, stage2) == (tried, feasible)
    found = 0
    for low, high in RATIO_BINS:
        # the original test: low <= gb.gearRatio() <= high, on every feasible pair
        expected = [pair for pair, ratio in feasible_pairs if low <= ratio <= high]
        assert list(pairs_in_ratio_bin(stage1, stage2, low, high)) == expected, (low, high)
        found += len(expected)
    assert found > 20, "the small search should still find pairs in the ratio bins"
