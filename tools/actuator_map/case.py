"""Run one actuator-map case: a normal COMPAct optimisation for (gearbox type, motor, gear ratio,
material), then read the best design.

Nothing in the optimiser changes. The run happens in a fresh temporary folder (COMPACT_CAD_DIR and
the working directory point there), exactly as `actOpt.py --gb_type ... --motor ... --gr ...` would
run it. The optimiser's printOptimizationResults is wrapped to keep a reference to the best
actuator it prints; the CAD variables are read from the Onshape equations file the optimiser itself
wrote. As a guard, the kept actuator rewrites that file into a second folder and the two must be
byte-identical (`same_cad_file`).
"""
import contextlib
import io
import os
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "Onshape_extension"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import gearbox_runner  # noqa: E402
from set_values import gearbox_family  # noqa: E402

from tools.actuator_map.geometry import geometry  # noqa: E402

CAD_DIR_ENV = "COMPACT_CAD_DIR"


def parse_cad_vars(text):
    """name -> number from an Onshape equations file ('"name"= value' lines)."""
    return {k: float(v) for k, v in re.findall(r'^"(.+?)"\s*=\s*([-\d.eE+]+)', text, re.M)}


def _num(x):
    """numpy scalars -> plain Python numbers, for JSON."""
    if isinstance(x, (list, tuple)):
        return [_num(i) for i in x]
    try:
        return x.item()
    except AttributeError:
        return x


def run_case(gb_type, motor, ratio, material="3dp"):
    """Optimise one case and return a JSON-ready dict. Infeasible cases and optimiser errors are
    returned too (feasible False, with `error` set when the optimiser raised)."""
    started = time.time()
    result = {"gb_type": gb_type, "motor": motor, "ratio_requested": ratio, "material": material,
              "feasible": False, "error": None}
    tmp = Path(tempfile.mkdtemp(prefix="actuator_map_"))
    old_cwd, old_cad_dir = os.getcwd(), os.environ.get(CAD_DIR_ENV)
    os.environ[CAD_DIR_ENV] = str(tmp / "CADs")
    os.chdir(tmp)
    try:
        actuator, optimizer = gearbox_runner.build(gb_type, motor, material)
        best = {}
        print_results = optimizer.printOptimizationResults

        def keep_best(Actuator, *args, **kwargs):
            best["actuator"] = Actuator
            return print_results(Actuator, *args, **kwargs)

        optimizer.printOptimizationResults = keep_best
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                _, params = optimizer.optimizeActuator(actuator, UsePSCasVariable=0, log=0, csv=1,
                                                       printOptParams=1, gearRatioReq=ratio)
        except Exception as e:  # e.g. bug 13: INDSPG raises when no design exists
            result["error"] = f"{type(e).__name__}: {e}"
            return result
        if not params or "actuator" not in best:
            return result

        best_actuator = best["actuator"]
        eq_name = f"{gb_type}_equations_onshape.txt"
        written = (tmp / "CADs" / gearbox_family(gb_type) / eq_name).read_bytes()
        os.environ[CAD_DIR_ENV] = str(tmp / "CADs_check")
        with contextlib.redirect_stdout(io.StringIO()):
            best_actuator.genEquationFile_editCADdirectly()
        rewritten = (tmp / "CADs_check" / gearbox_family(gb_type) / eq_name).read_bytes()
        cad_vars = parse_cad_vars(written.decode("utf-8"))

        try:
            geo = geometry(gb_type, cad_vars, getattr(best_actuator, "actuator_width", None))
        except Exception as e:  # a CAD variable the formulas don't know: keep the case, flag it
            geo = {"geometry_notes": [f"geometry failed: {type(e).__name__}: {e}"]}
        gearbox = getattr(best_actuator, gearbox_runner.GEARBOXES[gb_type].gearbox_arg)
        with contextlib.redirect_stdout(io.StringIO()):
            code_width = getattr(best_actuator, "actuator_width", None)
            result.update({
                "feasible": True,
                "gear_ratio": _num(gearbox.gearRatio()),
                "cost": _num(optimizer.cost(Actuator=best_actuator)),
                "mass_kg": _num(best_actuator.getMassKG_3DP()),
                "efficiency": _num(gearbox.getEfficiency()),
                # share of the motor's peak torque the gears carry (< 1 only when the face width
                # was capped: ISSPG, ICPG, INWPG with 3D-printed gears)
                "torque_carried_fraction": _num(getattr(best_actuator, "torque_carried_fraction", 1.0)),
                **{k: _num(v) for k, v in geo.items()},
                "code_actuator_width_mm": _num(code_width),
                "opt_parameters": _num(list(params)),
                "same_cad_file": written == rewritten,
                "cad_vars": cad_vars,
            })
        return result
    finally:
        os.chdir(old_cwd)
        if old_cad_dir is None:
            os.environ.pop(CAD_DIR_ENV, None)
        else:
            os.environ[CAD_DIR_ENV] = old_cad_dir
        shutil.rmtree(tmp, ignore_errors=True)
        result["seconds"] = round(time.time() - started, 2)
