"""
Fast design search for the two-stage gearboxes (DSPG, IDSPG, INDSPG).

The original search nested the stage-2 loops inside the stage-1 loops and ran every
check on every (stage 1, stage 2) pair: about 228 million pairs for DSPG with a U8,
of which only ~15 000 have the requested gear ratio. Every check, however, looks at
one stage only (teeth, module, planets and fixed clearances), so here:

1. each stage's designs are listed once, in the order the old loops visited them,
   with whether they pass that stage's checks (`stage_designs`);
2. for a ratio bin, only the passing pairs whose ratio r1 * r2 is in the bin are
   produced, in the old visiting order (`pairs_in_ratio_bin`).

The optimisers then evaluate exactly the pairs the old search evaluated, in the same
order, so they choose the same design (ties included) and write the same files.
"""

import numpy as np


class StageDesigns:
    """One stage's designs for one module: every design the old loops reached
    (`tried`), and the ones passing the stage's checks (`passing`, `ratios`)."""

    def __init__(self, module, tried):
        self.module  = module
        self.tried   = len(tried)
        self.passing = [design for design, ok in tried if ok]
        # (Nr + Ns) / Ns, as singleStagePlanetaryGearbox.gearRatio() computes it
        self.ratios  = np.array([(Nr + Ns) / Ns for Ns, Np, Nr, numPlanet in self.passing], dtype=float)


def stage_designs(stage, module_min, module_max, sun_teeth_min, planet_teeth_min,
                  planets_min, planets_max, max_diameter, checks):
    """List a stage's designs per module, visiting them exactly as the original loops did:
    module from module_min in 0.1 steps (rounded to 0.1); Ns while the sun's pitch diameter
    fits max_diameter; Np while the planet's fits max_diameter / 2; Nr = Ns + 2 Np, kept if
    the ring's pitch diameter fits; numPlanet from planets_min to planets_max.
    `checks()` tells whether the design currently set on `stage` passes that stage's checks.
    Returns a list of StageDesigns, one per module, in module order. Leaves `stage` set to
    whatever it was last given (the optimisers set every value before evaluating a pair)."""
    per_module = []
    stage.setModule(module_min)
    while stage.module <= module_max:
        tried = []
        stage.setNs(sun_teeth_min)
        while 2*stage.getPCRadiusSunMM() <= max_diameter:
            stage.setNp(planet_teeth_min)
            while 2*stage.getPCRadiusPlanetMM() <= max_diameter/2:
                stage.setNr(2*stage.Np + stage.Ns)
                if 2*stage.getPCRadiusRingMM() <= max_diameter:
                    stage.setNumPlanet(planets_min)
                    while stage.numPlanet <= planets_max:
                        tried.append(((stage.Ns, stage.Np, stage.Nr, stage.numPlanet), checks()))
                        stage.setNumPlanet(stage.numPlanet + 1)
                stage.setNp(stage.Np + 1)
            stage.setNs(stage.Ns + 1)
        per_module.append(StageDesigns(stage.module, tried))
        stage.setModule(stage.module + 0.100)
        stage.setModule(round(stage.module, 1))
    return per_module


def pair_counts(stage1_designs, stage2_designs):
    """(pairs the original search looped over, pairs passing both stages' checks) — the
    original optimisers' cntrIterBeforeCons and totalFeasibleGearboxes, per ratio bin."""
    tried    = sum(d1.tried for d1 in stage1_designs) * sum(d2.tried for d2 in stage2_designs)
    feasible = sum(len(d1.passing) for d1 in stage1_designs) * sum(len(d2.passing) for d2 in stage2_designs)
    return tried, feasible


def pairs_in_ratio_bin(stage1_designs, stage2_designs, ratio_low, ratio_high):
    """Yield (module1, stage-1 design, module2, stage-2 design) for every pair passing both
    stages' checks whose ratio r1 * r2 satisfies ratio_low <= r1 * r2 <= ratio_high,
    in the original loops' order (module1, module2, stage-1 design, stage-2 design).
    A design is (Ns, Np, Nr, numPlanet)."""
    for d1 in stage1_designs:
        for d2 in stage2_designs:
            if not d2.passing:
                continue
            for design1 in d1.passing:
                Ns1, Np1, Nr1, numPlanet1 = design1
                product = ((Nr1 + Ns1) / Ns1) * d2.ratios
                for index in np.nonzero((product >= ratio_low) & (product <= ratio_high))[0]:
                    yield d1.module, design1, d2.module, d2.passing[index]


def set_stage(stage, module, design):
    """Put a design (Ns, Np, Nr, numPlanet) and module on a singleStagePlanetaryGearbox."""
    Ns, Np, Nr, numPlanet = design
    stage.setModule(module)
    stage.setNs(Ns)
    stage.setNp(Np)
    stage.setNr(Nr)
    stage.setNumPlanet(numPlanet)
