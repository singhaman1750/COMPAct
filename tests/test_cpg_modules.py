"""CPG uses two modules: the sun and the big planet mesh with the big one (module_b), the small
planet and the ring with the small one (module_s). The CAD file still has a single "module"
(the big one), so the Onshape interface is unchanged (ISSUES.md bug 18).

Today the optimiser only finds equal modules (the geometric constraint is an exact float
comparison), so these tests set unequal modules by hand.
"""
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import gearbox_runner  # noqa: E402

M_BIG, M_SMALL = 0.6, 0.5


@pytest.fixture()
def actuator(monkeypatch, tmp_path):
    monkeypatch.setenv("COMPACT_CAD_DIR", str(tmp_path))
    a, _ = gearbox_runner.build("cpg", "U8_Lite", "3dp")
    gb = a.compoundPlanetaryGearbox
    gb.setNs(21), gb.setNpBig(54), gb.setNpSmall(30), gb.setNr(105), gb.setNumPlanet(3)
    gb.setModuleBig(M_BIG), gb.setModuleSmall(M_SMALL)
    a.setVariables()
    return a


def test_ring_side_follows_the_small_module(actuator):
    a = actuator
    assert (a.module_b, a.module_s) == (M_BIG, M_SMALL)
    assert a.dp_r == pytest.approx(a.Nr * M_SMALL)
    assert a.dp_p_s == pytest.approx(a.Np_s * M_SMALL)
    assert a.h_b_s == pytest.approx(1.25 * M_SMALL)
    assert a.ring_OD == pytest.approx(a.Nr * M_SMALL + 2 * a.ring_radial_thickness)
    ring_tips = a.Nr * M_SMALL + 2 * a.h_b_s
    if a.bearing_OD + a.output_mounting_hole_dia * 4 > ring_tips:
        assert a.bearing_mount_thickness == a.output_mounting_hole_dia * 2
    else:
        assert a.bearing_mount_thickness == pytest.approx(
            (ring_tips - (a.bearing_OD + a.output_mounting_hole_dia * 4)) / 2
            + a.output_mounting_hole_dia * 2 + a.standard_clearance_1_5mm)


def test_big_side_follows_the_big_module(actuator):
    a = actuator
    assert a.dp_s == pytest.approx(a.Ns * M_BIG)
    assert a.dp_p_b == pytest.approx(a.Np_b * M_BIG)
    assert a.carrier_PCD == pytest.approx((a.Ns + a.Np_b) * M_BIG)
    assert (a.h_a, a.h_b, a.h_f) == pytest.approx((M_BIG, 1.25 * M_BIG, 1.25 * M_BIG))


def test_cad_file_keeps_one_module_variable(actuator, tmp_path):
    actuator.genEquationFile_editCADdirectly()
    for name in ("cpg_equations.txt", "cpg_equations_onshape.txt"):
        text = (tmp_path / "CPG" / name).read_text()
        assert re.findall(r'^"(module[^"]*)"\s*=\s*(\S+)', text, re.M) == [("module", str(M_BIG))]


def test_no_plain_module_attribute_left_in_cpg():
    """`self.module` without a suffix would be ambiguous again; the class uses module_b / module_s."""
    src = (REPO / "ActuatorAndGearbox.py").read_text(encoding="utf-8")
    body = src[src.index("class compoundPlanetaryActuator"):src.index("class wolfromPlanetaryActuator")]
    assert not re.search(r"self\.module(?![_A-Za-z0-9])", body)
