# TODO

## Testing

No formal test suite exists yet (no pytest, no `test_*.py` files). Minimal plan for periodic testing, in order of effort:

1. **Shell smoke test** — re-run the 11 known-good `(motor, gearbox_type)` combinations through `actOpt.py` and check none crash:
   - `U8 sspg`, `U8 cpg`, `U8 dspg`, `U8 wpg`, `RO100 icpg`, `RI100 insspg_type_1`, `RI100 insspg_type_2`, `RI100 incpg_dependent`, `RI100 incpg_independent`, `RO100 isspg_inside`, `RO100 isspg_compact` (all with ratio `6.5`)

2. **`test_actopt.py` (pytest)** — formalize (1) as a parametrized pytest file: run all 11 combos via `subprocess`, assert exit code 0 and `opt_parameters is not None`.

3. **Golden-output regression test** — extend (2) to assert the *exact* expected numbers (teeth counts, module, gear ratio) for each combo, not just "didn't crash." This is the one that would catch silent wrong-value bugs (e.g. the ICPG `maxContinuousCurrent`-not-passed issue found during the motor-class investigation) that still exit cleanly.

4. **CI hook** — add a `.github/workflows/test.yml` to run whichever of the above on every push/PR, so it happens automatically instead of manually.

Suggested starting point: combine (2) + (3) into one `test_actopt.py` (~40-50 lines).

## Root folder restructure — split into `gearboxes/` and `optimizers/`

Root currently holds 7 `ActuatorAndGearbox*.py` model files + 10 `Opt_*.py` driver files (17 files) alongside `actOpt.py`, `CommonComponents.py`, config/results folders, etc. Goal: only `actOpt.py`-type entry files stay at root; models move to `gearboxes/`, drivers move to `optimizers/`.

**Open decision (settle first, ~10-15 min):** whether to split `ActuatorAndGearbox.py` (currently bundles SSPG/CPG/WPG/DSPG, 11k lines) into 4 per-type files *before* this move, so `gearboxes/` ends up with 10 uniform one-type-per-file modules instead of 7 files + 1 oversized one. Doing it first avoids touching that file's imports twice.

**Steps:**
1. Decide final layout, folder names, and whether the `ActuatorAndGearbox.py` split (above) happens first — *~10-15 min*
2. Create `gearboxes/` and `optimizers/`, `git mv` all 17 (or 20, if split first) files into place, add `__init__.py` to each — *~15 min*
3. Fix the `config_files/` relative-path logic in all 10 `Opt_*.py` files — each currently does `os.path.join(os.path.dirname(__file__), "config_files/...")`, which breaks once the file is one directory deeper (`config_files/` stays at repo root) — *~20-30 min*
4. Update every `from ActuatorAndGearbox_X import Y` line in the 10 `Opt_*.py` files to the package-qualified path (`from gearboxes.ActuatorAndGearbox_X import Y`) — *~20-30 min*
5. Update `actOpt.py`: `GEARBOX_DISPATCH` values need the `optimizers.` prefix, and the dynamic-import mechanism (`__import__(module_name)`) needs to switch to `importlib.import_module(module_name)`, since bare `__import__` on a dotted path returns the top-level package, not the submodule — *~15-20 min*
6. Update `run_all.sh` to the new paths — *~5 min*
7. Verify: syntax check all touched files, grep sweep for any remaining un-qualified `Opt_*`/`ActuatorAndGearbox_*` imports, live-run all 11 gearbox-type combos through `actOpt.py` and diff against last known-good output, run `run_all.sh` — *~30-45 min (mostly wait time on the slower combos, e.g. DSPG)*
8. Commit — *~5 min*

**Estimated total (working together, interactively):** ~2 to 2.5 hours, likely spread across more than one sitting.
