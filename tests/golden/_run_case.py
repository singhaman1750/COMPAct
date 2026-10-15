"""
Runs one optimisation case in a fresh process and writes the outcome as JSON.
Called by golden.py; not meant to be run by hand.

Args: gb_type motor gear_ratio cad_group out_json
"""

import json
import sys
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np  # noqa: E402

import actOpt  # noqa: E402


def to_json_value(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return [to_json_value(v) for v in value.tolist()]
    if isinstance(value, (list, tuple)):
        return [to_json_value(v) for v in value]
    if isinstance(value, dict):
        return {str(k): to_json_value(v) for k, v in value.items()}
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    return repr(value)


def snapshot(cad_dir):
    if not cad_dir.exists():
        return {}
    return {
        p: (p.stat().st_mtime_ns, p.stat().st_size)
        for p in cad_dir.rglob("*.txt")
    }


def main():
    gb_type, motor, gear_ratio, cad_group, out_json = sys.argv[1:6]
    gear_ratio = float(gear_ratio)
    cad_dir = REPO_ROOT / "CADs" / cad_group

    result = {"gb_type": gb_type, "motor": motor, "gear_ratio": gear_ratio, "error": None}
    before = snapshot(cad_dir)
    real_stdout = sys.stdout
    try:
        module = __import__(actOpt.GEARBOX_DISPATCH[gb_type])
        # Same call convention as actOpt.main()
        if gb_type in ["insspg_type_1", "insspg_type_2"]:
            _total_time, opt_parameters = module.run(motor, gear_ratio, gb_type)
        else:
            _total_time, opt_parameters = module.run(motor, gear_ratio)
        result["opt_parameters"] = to_json_value(opt_parameters)
    except Exception as exc:  # record crashes as part of current behaviour
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback_tail"] = traceback.format_exc().strip().splitlines()[-1]
        result["opt_parameters"] = None
    finally:
        # The optimisers redirect sys.stdout to their CSV and may not restore it.
        sys.stdout = real_stdout

    after = snapshot(cad_dir)
    changed = sorted(p for p, stamp in after.items() if before.get(p) != stamp)
    result["cad_files"] = {
        p.relative_to(REPO_ROOT).as_posix(): p.read_text(encoding="utf-8", errors="replace")
        for p in changed
    }
    Path(out_json).write_text(json.dumps(result), encoding="utf-8")


if __name__ == "__main__":
    main()
