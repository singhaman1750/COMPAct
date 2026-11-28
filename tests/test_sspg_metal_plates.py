"""SSPG metal plates (ISSUES.md, "Metal: realistic values", M3): secondary carrier 5 -> 3 mm
(aluminium) and sun hub 4 -> 3 mm (steel, part of the sun); the output bearing retainer stays 2 mm.
3D-printed mode keeps 5 / 4 / 2 mm (the golden baselines check that bit for bit).
"""
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import gearbox_runner  # noqa: E402

# The SSPG metal golden design (U8_Lite, 6.5:1): Ns, Np, Nr, module, planets.
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


@pytest.mark.parametrize("material, sec_carrier, sun_hub, retainer", [("3dp", 5, 4, 2), ("metal", 3, 3, 2)])
def test_plate_thicknesses_per_material(material, sec_carrier, sun_hub, retainer):
    a = build(material)
    assert (a.sec_carrier_thickness, a.sun_coupler_hub_thickness, a.bearing_retainer_thickness) \
        == (sec_carrier, sun_hub, retainer)
    # the housing step: secondary carrier + clearance_planet + sun hub - mounting surface
    assert a.case_dist == pytest.approx(sec_carrier + a.clearance_planet + sun_hub - a.case_mounting_surface_height)
    # the sun runs through the secondary carrier
    assert a.fw_s_used == pytest.approx(a.fw_p + a.clearance_planet + sec_carrier + a.standard_clearance_1_5mm)


def test_metal_actuator_is_narrower_by_the_plates():
    # before M3 (5 mm carrier, 4 mm hub): 62.05 mm, 850 g; M4's 2.5 mm base plate takes 1.5 mm more
    a = build("metal")
    assert a.case_dist == pytest.approx(3.5)
    assert a.actuator_width == pytest.approx(62.05 - (5 - 3) - (4 - 3) - 1.5)
    assert a.getMassKG_3DP() * 1000 == pytest.approx(766.2, abs=1)
