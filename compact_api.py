"""COMPAct for other projects (co-design): the actuator map inside an optimisation loop, and the real
gearbox design at the end. This is the only module another project needs to import.

    from compact_api import ActuatorMap, final_design, nearest_design
    amap = ActuatorMap()                                    # the latest released map (maps/v2)
    a = amap.actuator("U8_Lite", 9.3, "3dp")                # in the loop: milliseconds, SI units
    a.gb_type, a.mass, a.width, a.dia, a.peak_torque, a.no_load_speed, a.reflected_inertia
    d = final_design("U8_Lite", 9.3, "3dp", gb_type=a.gb_type, cad_dir="out/hip")   # at the end
    d["gb_type"], d["ratio"], d["gears"], d["face_widths_mm"], d["mass_kg"], d["cad_files"]

ActuatorMap is tools/actuator_map/map.py's, with the released map as its default folder; see that
file (or tools/actuator_map/README.md) for actuator(), select(), ranking() and the flags.
final_design() runs the normal optimiser once (0.1 s to about 75 s), as the map's sweep did, and
writes the CAD equation files. nearest_design() is an instant lookup of the nearest swept design.
Guide: docs/codesign_integration.md.
"""
import csv
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
if str(REPO) not in sys.path:  # last, so the importing project's own modules (e.g. a `tools`) come first
    sys.path.append(str(REPO))

from tools.actuator_map.map import Actuator, Candidate  # noqa: E402,F401  (re-exported)
from tools.actuator_map.map import ActuatorMap as _ActuatorMap  # noqa: E402
from tools.actuator_map.table import GEAR_COLUMNS, load_gains, load_motors, make_row  # noqa: E402

MAPS_DIR = REPO / "tools" / "actuator_map" / "maps"
FACE_WIDTH = re.compile(r"(^|_)fw_")
# make_row's columns that only mean something inside a sweep table (ranking against other types)
TABLE_ONLY = ("ratio_requested", "best_by_real_width", "best_by_compact_cost", "near_best_real_width",
              "near_best_compact", "no_full_torque_design")


def released_maps():
    """The released map folders (maps/v1, maps/v2, ...), oldest first."""
    found = [p for p in MAPS_DIR.glob("v*") if p.name[1:].isdigit() and (p / "fits.json").is_file()]
    return sorted(found, key=lambda p: int(p.name[1:]))


def default_map_dir():
    maps = released_maps()
    if not maps:
        raise FileNotFoundError(f"no released map in {MAPS_DIR}")
    return maps[-1]


class ActuatorMap(_ActuatorMap):
    """tools/actuator_map/map.py's ActuatorMap; `path` defaults to the latest released map."""

    def __init__(self, path=None):
        self.path = Path(path) if path is not None else default_map_dir()
        super().__init__(self.path)


def final_design(motor, ratio, material="3dp", gb_type=None, cad_dir=None, amap=None):
    """The real design for (motor, ratio, material, gb_type): one run of the normal optimiser.

    gb_type: the type the map chose (Actuator.gb_type); if None, the map's best type at `ratio`
             (`amap`, default the latest released map)
    cad_dir: if given, the CAD equation files are written there, as <cad_dir>/<FAMILY>/...

    Returns a dict: the map table's columns for this design (gb_type, the real ratio, mass_kg,
    width_*_m, dia_*_m, efficiency, torque_carried_fraction, output torques and speeds, inertias,
    compact_cost, real_width_score, torque_capped, cad_issues, commit), plus
        gears           teeth counts, modules and planet counts by name (table.py's GEAR_COLUMNS)
        face_widths_mm  every face-width CAD variable (fw_*)
        cad_vars        every CAD variable, as in the Onshape equations file
        opt_parameters  the optimiser's own parameter list
        cad_files       the files written to cad_dir ([] without cad_dir)
        seconds         run time
    Raises ValueError when the optimiser finds no design.
    """
    from tools.actuator_map.case import run_case
    from tools.actuator_map.sweep import git_commit

    if gb_type is None:
        gb_type = (amap or ActuatorMap()).actuator(motor, ratio, material).gb_type
    if cad_dir is not None:
        cad_dir = Path(cad_dir).resolve()  # run_case works in a temporary folder
    case = run_case(gb_type, motor, ratio, material, cad_out=cad_dir)
    if not case["feasible"]:
        why = case["error"] or "no design passes the checks"
        raise ValueError(f"{motor} {material} {gb_type} at ratio {ratio:g}: {why}")
    case["commit"] = git_commit()
    design = make_row(case, load_motors()[motor], load_gains())
    for col in TABLE_ONLY:
        design.pop(col)
    gears = {col: design.pop(col) for col in GEAR_COLUMNS}
    design.update({
        "gears": {col: x for col, x in gears.items() if x is not None},
        "face_widths_mm": {k: v for k, v in case["cad_vars"].items() if FACE_WIDTH.search(k)},
        "cad_vars": case["cad_vars"],
        "opt_parameters": case["opt_parameters"],
        "cad_files": sorted(str(p) for p in Path(cad_dir).rglob("*") if p.is_file()) if cad_dir else [],
        "seconds": case["seconds"],
    })
    return design


def _value(text):
    if text == "":
        return None
    if text in ("True", "False"):
        return text == "True"
    for kind in (int, float):
        try:
            return kind(text)
        except ValueError:
            pass
    return text


def nearest_design(motor, ratio, material="3dp", gb_type=None, map_dir=None):
    """The swept design nearest to `ratio` (by real ratio) in a released map's table: instant, but
    only the swept ratios, and without face widths or CAD files (use final_design for those).

    gb_type: only this type; if None, only the designs that were best at their swept ratio.
    Returns the table row as a dict, with the teeth counts etc. also under "gears".
    """
    path = Path(map_dir) if map_dir is not None else default_map_dir()
    with open(path / f"table_{material}.csv", newline="", encoding="utf-8") as f:
        rows = [{k: _value(v) for k, v in r.items()} for r in csv.DictReader(f) if r["motor"] == motor]
    rows = [r for r in rows if (r["gb_type"] == gb_type if gb_type else r["best_by_real_width"])]
    if not rows:
        raise ValueError(f"{motor} {material} {gb_type or 'best'}: no design in {path.name}")
    row = min(rows, key=lambda r: (abs(r["ratio"] - ratio), r["ratio"]))
    row["gears"] = {col: row[col] for col in GEAR_COLUMNS if row[col] is not None}
    return row
