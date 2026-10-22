"""
Runs one optimisation case in a fresh process and writes the outcome as JSON.
Called by golden.py; not meant to be run by hand.

Args: gb_type motor gear_ratio cad_group out_json [material]
"""

import json
import re
import sys
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np  # noqa: E402

import gearbox_runner  # noqa: E402


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
    material = sys.argv[6] if len(sys.argv) > 6 else "3dp"
    gear_ratio = float(gear_ratio)
    cad_dir = REPO_ROOT / "CADs" / cad_group

    result = {"gb_type": gb_type, "motor": motor, "gear_ratio": gear_ratio, "error": None}
    if material != "3dp":
        result["material"] = material
    before = snapshot(cad_dir)
    real_stdout = sys.stdout
    try:
        _total_time, opt_parameters = gearbox_runner.run(gb_type, motor, gear_ratio, material)
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
    # golden.py runs each case in an empty working directory, so everything
    # under ./results was written by this run.
    results_dir = Path.cwd() / "results"
    result["results_files"] = {
        p.relative_to(results_dir).as_posix(): drop_timing_lines(
            p.read_text(encoding="utf-8", errors="replace")
        )
        for p in sorted(results_dir.rglob("*"))
        if p.is_file()
    } if results_dir.exists() else {}
    Path(out_json).write_text(json.dumps(result), encoding="utf-8")


_TIMING = re.compile(r"running time|time taken", re.IGNORECASE)


def drop_timing_lines(text):
    """Remove run-time measurements, which differ on every run."""
    kept, skip_next = [], False
    for line in text.splitlines():
        if skip_next:
            skip_next = False
            if re.fullmatch(r"\s*[\d.eE+-]+\s*", line):
                continue
        if _TIMING.search(line):
            # 'Running Time (sec)' on its own line is followed by the number
            skip_next = not re.search(r"\d", line)
            continue
        kept.append(line)
    return "\n".join(kept) + "\n"


if __name__ == "__main__":
    main()
