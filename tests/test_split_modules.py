"""WPG, INCPG, INWPG and ICPG use two modules, as CPG does (test_cpg_modules.py): the sun, the big planet
and (Wolfrom) the big ring mesh with the big one (module_b), the small planet and the ring it meshes with
use the small one (module_s). The CAD file still has a single "module" (the big one), so the Onshape
interface is unchanged (ISSUES.md bug 18).

Today the optimiser only finds equal modules (the geometric constraint is an exact float comparison), so
these tests take each type's first golden design and set a smaller small module by hand.
"""
import re
from pathlib import Path

import pytest

import gearbox_runner
from CommonComponents import bearings_discrete
from variable_helpers import GEARBOXES, golden_design

REPO = Path(__file__).resolve().parents[1]

COMPOUND = ["incpg_dependent", "incpg_independent", "icpg"]          # one ring, on the small side
WOLFROM = ["wpg", "inwpg_dependent", "inwpg_independent"]           # a big ring and a small ring
SOURCES = {                                                         # file, and the class to check in it
    "wpg": ("ActuatorAndGearbox.py", "class wolfromPlanetaryActuator"),
    "incpg_dependent": ("ActuatorAndGearbox_INCPG_dependent.py", None),
    "incpg_independent": ("ActuatorAndGearbox_INCPG_independent.py", None),
    "inwpg_dependent": ("ActuatorAndGearbox_INWPG_dependent.py", None),
    "inwpg_independent": ("ActuatorAndGearbox_INWPG_independent.py", None),
    "icpg": ("ActuatorandGearbox_ICPG.py", None),
}


def build(monkeypatch, tmp_path, gb):
    """The type's first golden design with the small module set 0.1 below the big one."""
    spec = GEARBOXES[gb]
    _, motor, material, gears, _ = golden_design(spec.golden()[0])
    gears = list(gears)
    i_b = 4 if gb in COMPOUND else 5                                # index of module_b in the setter's tuple
    m_b = gears[i_b]
    m_s = round(m_b - 0.1, 1)
    gears[i_b + 1] = m_s
    monkeypatch.setenv("COMPACT_CAD_DIR", str(tmp_path))
    a, _ = gearbox_runner.build(spec.gb_type, motor, material)
    spec.set_gears(getattr(a, spec.gearbox_attr), gears)
    a.setVariables()
    return a, m_b, m_s


@pytest.mark.parametrize("gb", COMPOUND + WOLFROM)
def test_small_side_follows_the_small_module(monkeypatch, tmp_path, gb):
    a, m_b, m_s = build(monkeypatch, tmp_path, gb)
    assert (a.module_b, a.module_s) == (m_b, m_s)
    assert a.dp_p_s == pytest.approx(a.Np_s * m_s)
    if gb in COMPOUND:
        assert a.dp_r == pytest.approx(a.Nr * m_s)
    else:
        assert a.dp_r_s == pytest.approx(a.Nr_s * m_s)


@pytest.mark.parametrize("gb", COMPOUND + WOLFROM)
def test_big_side_follows_the_big_module(monkeypatch, tmp_path, gb):
    a, m_b, _ = build(monkeypatch, tmp_path, gb)
    assert a.dp_s == pytest.approx(a.Ns * m_b)
    assert a.dp_p_b == pytest.approx(a.Np_b * m_b)
    assert (a.h_a, a.h_b, a.h_f) == pytest.approx((m_b, 1.25 * m_b, 1.25 * m_b))
    if gb in WOLFROM:
        assert a.dp_r_b == pytest.approx(a.Nr_b * m_b)


@pytest.mark.parametrize("gb, attr, wall", [("wpg", "bearing_ID", "small_ring_case_thickness"),
                                            ("inwpg_dependent", "output_bearing_ID", "small_ring_radial_width"),
                                            ("inwpg_independent", "output_bearing_ID", "small_ring_radial_width")])
def test_wolfrom_output_bearing_is_sized_on_the_small_ring(monkeypatch, tmp_path, gb, attr, wall):
    a, _, m_s = build(monkeypatch, tmp_path, gb)
    required = m_s * a.Nr_s + 2 * m_s + 2 * getattr(a, wall)
    assert getattr(a, attr) == bearings_discrete(required).getBearingIDMM()


def test_wpg_bearing_mount_uses_the_small_ring_tooth_depth(monkeypatch, tmp_path):
    a, _, m_s = build(monkeypatch, tmp_path, "wpg")
    assert a.h_b_s == pytest.approx(1.25 * m_s)


@pytest.mark.parametrize("gb", COMPOUND + WOLFROM)
def test_cad_file_keeps_one_module_variable(monkeypatch, tmp_path, gb):
    a, m_b, _ = build(monkeypatch, tmp_path, gb)
    a.genEquationFile_editCADdirectly()
    spec = GEARBOXES[gb]
    files = [tmp_path / spec.cad_folder / f"{spec.cad_file}_onshape.txt"]
    if spec.has_plain:
        files.append(tmp_path / spec.cad_folder / f"{spec.cad_file}.txt")
    for f in files:
        assert re.findall(r'^"(module[^"]*)"\s*=\s*(\S+)', f.read_text(), re.M) == [("module", str(m_b))], f.name


@pytest.mark.parametrize("gb", COMPOUND + WOLFROM)
def test_no_plain_module_attribute_left(gb):
    """`self.module` without a suffix would be ambiguous again; the class uses module_b / module_s."""
    name, cls = SOURCES[gb]
    src = (REPO / name).read_text(encoding="utf-8")
    if cls:
        start = src.index(cls)
        src = src[start:src.index("\nclass ", start + 1)]
    code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
    assert not re.search(r"self\.module(?![_A-Za-z0-9])", code)
