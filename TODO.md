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

## README rewrite

Audited `README.md` against the actual current code (`actOpt.py`'s `GEARBOX_DISPATCH`, every `Opt_*.py` motor branch, `CADs/` folder contents). Findings, in order of severity:

**Stale/incomplete content:**
- **"Supported Hardware" tables only cover ~half the framework.** Motors table lists 6 (`U8, U10, U12, MN8014, VT8020, MAD_M6C12`) but the code supports 10 — missing `RO60, RO80, RO100, RI100`. Gearbox Topologies table lists 4 (`sspg, cpg, wpg, dspg`) but `actOpt.py` dispatches 11 — missing `icpg, insspg_type_1, insspg_type_2, incpg_dependent, incpg_independent, isspg_inside, isspg_compact`. These tables look like they predate the whole R-motor/inrunner-gearbox line of work.
- **Step 4 (Run Optimization) documents the 7 newer gearbox types as 5 separate repetitive "Syntax + Example" blocks** instead of one table — same info as the Supported Hardware tables should have, just duplicated inconsistently in prose instead.
- **ISSPG's motor list is wrong** — README says `<motor>`: RO80, RO100, but `Opt_ISSPG_inside.py`/`Opt_ISSPG_compact.py` also support `RO60` (confirmed via `motor_name == "RO60"` branches in both files).
- **`insspg_type_1`/`insspg_type_2` labels need a domain check.** README calls them "Independent"/"Dependent" respectively, but nothing found in `Opt_INSSPG.py`/`ActuatorandGearbox_INSSPG.py` confirms that mapping in those terms — the code just branches on a `"fw_s_used"` face-width formula, described as "TYPE 1 MATH" vs "TYPE 2 MATH". **Needs your confirmation** before the rewrite states it either way.
- **Step 5/6 CAD-output paths only cover SSPG/CPG/DSPG/WPG** (`CADs/<TYPE>/<type>_equations.txt`); the other 7 gearbox types write elsewhere (`CADs/ICPG/icpg_equations.txt`, `CADs/INSSPG/insspg_equations.txt`, `CADs/INCPG/incpg_equations.txt`, `CADs/ISSPG/isspg_equations_onshape.txt`, `CADs/DSPG/Equation_Files/<motor>/...`) and aren't documented at all.
- **No "Project Structure" section** — nothing in the README maps the repo's file layout (`actOpt.py`, `Opt_*.py`, `ActuatorAndGearbox_*.py`, `CommonComponents.py`, `config_files/`, `CADs/`, `results/`) for a new reader.

**Presentation/formatting issues:**
- Onshape links are inconsistently formatted — some gearbox types show only a clickable `👉 **[Open X in Onshape](url)**` link, others additionally repeat the same URL in a raw, unlabeled code block right below it (ISSPG/INCPG/INSSPG do this, SSPG/CPG/WPG/DSPG don't).
- A dead HTML comment block (lines ~332-340, "iv. Set the Equations File") is left in the raw source — should be deleted or resolved, not commented out.
- The `[COPY PASTE THE LINK IF HYPERLINK DOESN'T OPEN]` note appears exactly once (above the SSPG link only) even though the same problem would apply to every link.
- Mass Analysis Google Sheets link (Step 5) uses a bare, unlabeled code fence, inconsistent with the `👉 **[Open X](...)**` link style used everywhere else.

**Separately — not a README issue, a real bug found during this audit:** `ActuatorAndGearbox_ISSPG_inside.py` and `ActuatorAndGearbox_ISSPG_compact.py` both write their Onshape equations file to the exact same path, `CADs/ISSPG/isspg_equations_onshape.txt` — running one gearbox type after the other silently overwrites the first result. Worth its own fix, independent of this README task (flag if you want it added to `ISSUES.md` or fixed directly).

**Plan:**
1. **Resolve the `insspg_type_1`/`insspg_type_2` → Independent/Dependent question** with you before writing anything — *~5 min*
2. **Rebuild "Supported Hardware" as the single source of truth**: one motor table (10 rows) and one gearbox-topology table (11 rows), each gearbox row noting which motors it accepts — *~20 min*
3. **Collapse Step 4's 5 repetitive Syntax/Example blocks** into one syntax block + one combined compatibility table (reusing table from step 2) + 2-3 representative examples instead of one per type — *~20-30 min*
4. **Fix the ISSPG motor list** (add RO60) and **document all 7 CAD-output paths** missing from Step 5/6 — *~15 min*
5. **Add a short "Project Structure" section** (file/folder map, one line each) — *~15-20 min*
6. **Clean up formatting inconsistencies**: normalize Onshape link presentation (pick one style, apply everywhere), delete the dead HTML comment block, fix the Mass Analysis link style — *~15-20 min*
7. **Review pass together** — read the rewritten README end-to-end against the live repo one more time before committing — *~15 min*

**Estimated total (working together, interactively):** ~1.5 to 2 hours.
