"""A design's mass must not depend on which design was set up before it (ISSUES bug 19).

The optimiser weighs each candidate after `updateFacewidth()`; `setVariables()` used to run only when a
new best design was found, so the mass model read derived values (face widths, bearings, distances) left
over from that design. Each case below sets up design Y fully, then switches to design X the way the
search does, and compares X's mass with X weighed on a freshly built actuator.
"""
import contextlib
import io
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import gearbox_runner  # noqa: E402

WOLFROM = ("Ns", "NpBig", "NrBig", "NpSmall", "NrSmall", "ModuleBig", "ModuleSmall", "NumPlanet")
DOUBLE = ("Ns", "Np", "Nr", "Module", "NumPlanet")

# type, motor, design X, design Y (golden designs of the type: Wolfrom as WOLFROM, double stage per stage as DOUBLE)
CASES = [
    ("wpg", "U8_Lite", (63, 35, 133, 28, 126, 0.5, 0.5, 7), (56, 48, 152, 36, 140, 0.5, 0.5, 4)),
    ("inwpg_dependent", "RI100", (18, 36, 90, 21, 75, 0.8, 0.8, 3), (54, 30, 114, 24, 108, 0.6, 0.6, 6)),
    ("inwpg_independent", "RI100", (33, 33, 99, 24, 90, 0.6, 0.6, 3), (54, 30, 114, 24, 108, 0.6, 0.6, 6)),
    ("idspg", "RO100", ((33, 29, 91, 0.7, 4), (19, 31, 81, 1.4, 4)), ((30, 45, 120, 0.5, 3), (41, 41, 123, 0.8, 4))),
    ("indspg", "RI100", ((26, 25, 76, 0.5, 3), (19, 29, 77, 1.2, 4)), ((19, 26, 71, 0.5, 3), (27, 30, 87, 0.6, 3))),
]


def set_design(actuator, gb_type, design):
    gb = getattr(actuator, gearbox_runner.GEARBOXES[gb_type].gearbox_arg)
    if hasattr(gb, "Stage1"):
        for stage, values in zip((gb.Stage1, gb.Stage2), design):
            for name, value in zip(DOUBLE, values):
                getattr(stage, "set" + name)(value)
    else:
        for name, value in zip(WOLFROM, design):
            getattr(gb, "set" + name)(value)


def mass_after(actuator, gb_type, design, refresh):
    set_design(actuator, gb_type, design)
    actuator.updateFacewidth()
    if refresh:
        actuator.setVariables()
    with contextlib.redirect_stdout(io.StringIO()):
        return actuator.getMassKG_3DP()


@pytest.mark.parametrize("material", ["3dp", "metal"])
@pytest.mark.parametrize("gb_type, motor, x, y", CASES, ids=[c[0] for c in CASES])
def test_mass_does_not_depend_on_the_previous_design(gb_type, motor, x, y, material):
    fresh, _ = gearbox_runner.build(gb_type, motor, material)
    expected = mass_after(fresh, gb_type, x, refresh=True)

    searched, _ = gearbox_runner.build(gb_type, motor, material)
    mass_after(searched, gb_type, y, refresh=True)                       # Y was the last best design
    assert mass_after(searched, gb_type, x, refresh=False) == pytest.approx(expected, rel=1e-12)
