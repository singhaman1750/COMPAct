"""Shared helpers for the variable-category tests: which gearboxes have a spec, how to set one of
their gear sets, and how to write and read their CAD equation files in a temporary folder.

To add a gearbox: write config_files/variables/<gb>_variables.json and add an entry to GEARBOXES.
"""
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tests" / "golden"))

import gearbox_runner  # noqa: E402
from golden import BASELINE_DIR  # noqa: E402
from tools.variables.render import load  # noqa: E402

CONFIG = REPO / "config_files"


@dataclass
class Gearbox:
    gb_type: str
    cad_folder: str                       # CADs/<cad_folder>/<file>.txt and <file>_onshape.txt
    cad_file: str
    gearbox_attr: str                     # the actuator's gearbox object
    counts: dict                          # expected CAD variables per category
    code_only: int                        # expected number of code-only values
    set_gears: Callable                   # (gearbox, gear set) -> None
    from_opt: Callable                    # golden opt_parameters -> gear set
    extra: list = field(default_factory=list)   # (motor, gear set) reaching other rule branches
    branches: Callable = None             # actuator -> {rule: which branch}
    params_name: str = None               # the config file, when it is not <gb_type>_params.json
    config_file: str = "config.json"      # gear standard / MIT factors (the motor config of the frameless types)

    @property
    def params_file(self):
        return self.params_name or f"{self.gb_type}_params.json"

    def golden(self):
        return sorted(p.stem for p in BASELINE_DIR.glob(f"{self.gb_type}__*.json"))


def _set_sspg(gb, g):
    Ns, Np, Nr, module, n = g
    gb.setNs(Ns), gb.setNp(Np), gb.setNr(Nr), gb.setModule(module), gb.setNumPlanet(n)


def _set_cpg(gb, g):
    Ns, Np_b, Np_s, Nr, m_b, m_s, n = g
    gb.setNs(Ns), gb.setNpBig(Np_b), gb.setNpSmall(Np_s), gb.setNr(Nr)
    gb.setModuleBig(m_b), gb.setModuleSmall(m_s), gb.setNumPlanet(n)


def _set_wpg(gb, g):
    Ns, Np_b, Np_s, Nr_b, Nr_s, m_b, m_s, n = g
    gb.setNs(Ns), gb.setNpBig(Np_b), gb.setNpSmall(Np_s), gb.setNrBig(Nr_b), gb.setNrSmall(Nr_s)
    gb.setModuleBig(m_b), gb.setModuleSmall(m_s), gb.setNumPlanet(n)


def _set_dspg(gb, g):
    Ns1, Np1, Nr1, m1, n1, Ns2, Np2, Nr2, m2, n2 = g
    for stage, (Ns, Np, Nr, module, n) in ((gb.Stage1, (Ns1, Np1, Nr1, m1, n1)), (gb.Stage2, (Ns2, Np2, Nr2, m2, n2))):
        stage.setNs(Ns), stage.setNp(Np), stage.setNr(Nr), stage.setModule(module), stage.setNumPlanet(n)


def _branches_single(a):
    return {"ring wider than motor": a.ring_OD >= a.motor_OD,
            "bearing wider than ring": a.bearing_OD + a.output_mounting_hole_dia * 4 > a.Nr * a.module + 2 * a.h_b}


def _branches_cpg(a):
    return {"big planets wider than motor": (a.Ns + a.Np_b * 2) * a.module_b >= a.motor_OD,
            "bearing wider than ring": a.bearing_OD + a.output_mounting_hole_dia * 4 > a.Nr * a.module_s + 2 * a.h_b_s,
            "ring grown to the bearing": not a.Nr * a.module_s + 5 * 2 > a.bearing_OD}


def _branches_incpg_dependent(a):
    return {"rotor top bearing: the sun, not the motor minimum, sets the bore":
            a.module * a.Ns + 2 * a.standard_clearance_1_5mm > a.min_rotor_top_bearing_ID}


def _branches_insspg(a):
    return {"sun support: capped at 21 mm":
            a.carrier_PCD - (a.planet_shaft_dia + a.planet_shaft_step_offset * 2) - a.standard_clearance_1_5mm * 3 > 21}


def _branches_wpg(a):
    # bearing_mount_thickness has a second case, but the bearing is chosen with a bore of at least
    # module * Nr_s + 2 * module + 2 * small_ring_case_thickness, so the first case always applies
    return {"sun hub: motor holes wider than the sun tip":
            a.motor_output_hole_PCD + a.motor_output_hole_CSK_OD + a.standard_clearance_1_5mm * 2 > a.module * a.Ns + 2 * a.module}


def _branches_dspg(a):
    return {"stage 1: ring wider than motor": a.ring_OD1 >= a.motor_OD,
            "stage 1: bearing wider than ring": a.bearing1_OD + a.output_mounting_hole_dia1 * 4 > a.Nr1 * a.module1 + 2 * a.h_b1,
            "stage 2: bearing wider than ring": a.bearing2_OD + a.output_mounting_hole_dia2 * 4 > a.Nr2 * a.module2 + 2 * a.h_b2,
            "stage 1-2 mounting: extra width needed": a.stg1_stg2_mounting_extra_width > 0}


GEARBOXES = {
    "sspg": Gearbox(
        "sspg", "SSPG", "sspg_equations", "planetaryGearbox",
        counts={"input": 18, "optimisation": 4, "fixed": 43, "dependent": 48}, code_only=28,
        set_gears=_set_sspg,
        from_opt=lambda p: (p[2], p[3], p[4], p[5], p[1]),           # [gr, n, Ns, Np, Nr, module]
        extra=[("U8_Lite", (20, 40, 100, 1.2, 3)), ("MAD_M6C12_KV170", (18, 30, 78, 0.5, 3)),
               ("VT8020_PRO", (30, 60, 150, 1.0, 4))],
        branches=_branches_single),
    "cpg": Gearbox(
        "cpg", "CPG", "cpg_equations", "compoundPlanetaryGearbox",
        counts={"input": 18, "optimisation": 5, "fixed": 42, "dependent": 54}, code_only=31,
        set_gears=_set_cpg,
        from_opt=lambda p: (p[2], p[3], p[4], p[5], p[6], p[7], p[1]),   # [gr, n, Ns, Np_b, Np_s, Nr, m_b, m_s]
        extra=[("MAD_M6C12_KV170", (18, 70, 30, 118, 1.0, 1.0, 3)), ("U8_Lite", (30, 30, 30, 90, 0.5, 0.5, 3)),
               ("VT8020_PRO", (24, 40, 26, 90, 1.2, 1.2, 3)),
               ("U10_Plus_KV80", (18, 24, 60, 102, 1.0, 1.0, 3))],   # made up: ring wider than bearing + bolts
        branches=_branches_cpg),
    "incpg_dependent": Gearbox(
        "incpg_dependent", "INCPG", "incpg_dependent_equations", "inrunnerCompoundPlanetaryGearbox",
        counts={"input": 21, "optimisation": 5, "fixed": 54, "dependent": 54}, code_only=22,
        set_gears=_set_cpg,
        from_opt=lambda p: (p[2], p[3], p[4], p[5], p[6], p[7], p[1]),   # [gr, n, Ns, Np_b, Np_s, Nr, m_b, m_s]
        extra=[], branches=_branches_incpg_dependent),
    "incpg_independent": Gearbox(
        "incpg_independent", "INCPG", "incpg_independent_equations", "inrunnerCompoundPlanetaryGearbox",
        counts={"input": 21, "optimisation": 5, "fixed": 57, "dependent": 55}, code_only=21,
        set_gears=_set_cpg,
        from_opt=lambda p: (p[2], p[3], p[4], p[5], p[6], p[7], p[1]),   # [gr, n, Ns, Np_b, Np_s, Nr, m_b, m_s]
        extra=[]),
    "insspg_type_1": Gearbox(
        "insspg_type_1", "INSSPG", "insspg_type_1_equations", "planetaryGearbox",
        counts={"input": 12, "optimisation": 4, "fixed": 56, "dependent": 35}, code_only=60,
        set_gears=_set_sspg,
        from_opt=lambda p: (p[2], p[3], p[4], p[5], p[1]),           # [gr, n, Ns, Np, Nr, module, ...]
        extra=[("RI100", (18, 28, 74, 0.5, 4))],                    # small carrier: the sun support is not capped
        branches=_branches_insspg,
        params_name="insspg_params.json", config_file="insspg_motor_config.json"),
    "insspg_type_2": Gearbox(
        "insspg_type_2", "INSSPG", "insspg_type_2_equations", "planetaryGearbox",
        counts={"input": 12, "optimisation": 4, "fixed": 56, "dependent": 35}, code_only=60,
        set_gears=_set_sspg,
        from_opt=lambda p: (p[2], p[3], p[4], p[5], p[1]),
        extra=[("RI100", (18, 28, 74, 0.5, 4))],                    # small carrier: the sun support is not capped
        branches=_branches_insspg,
        params_name="insspg_params.json", config_file="insspg_motor_config.json"),
    "wpg": Gearbox(
        "wpg", "WPG", "wpg_equations", "wolfromPlanetaryGearbox",
        counts={"input": 18, "optimisation": 5, "fixed": 52, "dependent": 68}, code_only=35,
        set_gears=_set_wpg,
        # [gr, n, Ns, Np_b, Nr_b, Np_s, Nr_s, module_b, module_s]
        from_opt=lambda p: (p[2], p[3], p[5], p[4], p[6], p[7], p[8], p[1]),
        extra=[],
        branches=_branches_wpg),
    "dspg": Gearbox(
        "dspg", "DSPG", "dspg_equations", "doubleStagePlanetaryGearbox",
        counts={"input": 36, "optimisation": 15, "fixed": 90, "dependent": 114}, code_only=33,
        set_gears=_set_dspg,
        # [gr, n1, n2, Ns1, Np1, Nr1, Ns2, Np2, Nr2, module1, module2]
        from_opt=lambda p: (p[3], p[4], p[5], p[9], p[1], p[6], p[7], p[8], p[10], p[2]),
        extra=[("U8_Lite", (18, 60, 138, 1.0, 3, 36, 30, 96, 0.5, 3)),    # small stage-2 ring: no extra mounting width
               ("U8_Lite", (18, 60, 138, 1.0, 3, 18, 60, 138, 1.0, 3))],   # both rings wider than their bearings
        branches=_branches_dspg),
}
# only gearboxes whose spec exists are tested
SPECS = {gb: load(gb) for gb in GEARBOXES if (CONFIG / "variables" / f"{gb}_variables.json").is_file()}


def equation_lines(text):
    return re.findall(r'^"(.+?)"\s*=\s*([-\d.eE+]+)', text, re.M)


def write_design(monkeypatch, folder, gb, motor, material, gears):
    """Build the actuator for this gear set and write its two equation files to `folder`; return the
    actuator, the optimiser and the two files' (name, value) lines."""
    spec = GEARBOXES[gb]
    monkeypatch.setenv("COMPACT_CAD_DIR", str(folder))
    actuator, optimizer = gearbox_runner.build(spec.gb_type, motor, material)
    spec.set_gears(getattr(actuator, spec.gearbox_attr), gears)
    actuator.updateFacewidth()
    actuator.genEquationFile_editCADdirectly()
    base = Path(folder) / spec.cad_folder
    stage_files = load(gb).get("plain_files")      # a gearbox with one plain file per stage (DSPG)
    if stage_files:
        plain = [(prefix + n, v) for prefix, f in stage_files.items() for n, v in equation_lines((base / f).read_text())]
    else:
        plain = equation_lines((base / f"{spec.cad_file}.txt").read_text())
    onshape = equation_lines((base / f"{spec.cad_file}_onshape.txt").read_text())
    return actuator, optimizer, plain, onshape


def golden_design(name):
    """(gearbox, motor, material, gear set, the baseline's Onshape file text) of a golden case."""
    b = json.loads((BASELINE_DIR / f"{name}.json").read_text(encoding="utf-8"))
    gb = b["gb_type"]
    (text,) = [t for p, t in b["cad_files"].items() if p.endswith(f"{GEARBOXES[gb].cad_file}_onshape.txt")]
    return gb, b["motor"], b.get("material", "3dp"), GEARBOXES[gb].from_opt(b["opt_parameters"]), text


def downstream_of(gb, *names):
    """Every variable that depends on any of `names`, directly or through others (plus `names`)."""
    spec = SPECS[gb]
    found, grew = set(names), True
    while grew:
        grew = False
        for e in spec["cad_variables"] + spec["code_only"]:
            if e["name"] not in found and set(e.get("depends_on", [])) & found:
                found.add(e["name"])
                grew = True
    return found
