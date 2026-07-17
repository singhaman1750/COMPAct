# Known Issues / Findings

## 1. `bearings_discrete` — OD table vs ID table content differ

**Description:** `bearings_discrete` (in `CommonComponents.py`) supports two lookup
modes — by inner diameter (`idRequiredMM`, the default) and by outer diameter
(`odRequiredMM`, opt-in) — but the two modes draw from **two different bearing
catalogues**, not one shared table. 28 rows are common to both, but:
- Rows only in the OD-table (never reachable via an ID-based lookup):
  `[44.45, 53.975, 6.35, 0.031]`, `[50, 62, 6, 0.036]`
- Rows only in the ID-table (never reachable via an OD-based lookup):
  `[28, 52, 12, 0.096]`, `[32, 58, 13, 0.122]`

Practical effect: the same nominal bearing requirement can resolve to a **different
physical bearing** depending on whether the caller looks it up by ID or by OD.

**Reproduce:**
```python
from CommonComponents import bearings_discrete

b_od = bearings_discrete(idRequiredMM=0, odRequiredMM=62)
print(b_od.getBearingIDMM(), b_od.getBearingODMM(), b_od.getBearingWidthMM(), b_od.getBearingMassKG())
# 50 62 6 0.036

b_id = bearings_discrete(idRequiredMM=50)
print(b_id.getBearingIDMM(), b_id.getBearingODMM(), b_id.getBearingWidthMM(), b_id.getBearingMassKG())
# 50 65 7 0.05
```
Both calls describe a "50mm ID bearing," but the OD-lookup returns a 50×62×6mm bearing
while the ID-lookup returns a 50×65×7mm bearing — verified live, output as shown above.

**Probable fix:** merge the two catalogues into one combined table so both lookup modes
draw from the same rows. This is a bigger, more consequential change than a typical bug
fix — it would alter which physical bearing gets selected for some existing inputs — so
it should be a deliberate decision rather than folded in silently.

**Status:** open — not yet fixed.

## 2. ISSPG "inside" and "compact" variants silently overwrite each other's equations file

**Description:** `ActuatorAndGearbox_ISSPG_inside.py` and `ActuatorAndGearbox_ISSPG_compact.py`
both call `genEquationFile_editCADdirectly()` automatically whenever `optimizeActuator()` finds a
feasible solution, and both write to the exact same path:
`CADs/ISSPG/isspg_equations_onshape.txt`. Running one gearbox type after the other silently
clobbers the first run's output — no error, no warning, and no filename distinction between
`isspg_inside` and `isspg_compact` results.

**Reproduce:**
```bash
python actOpt.py RO100 isspg_inside 6.5
# CADs/ISSPG/isspg_equations_onshape.txt now holds the isspg_inside solution

python actOpt.py RO100 isspg_compact 6.5
# CADs/ISSPG/isspg_equations_onshape.txt has been silently overwritten with the
# isspg_compact solution instead — confirmed via file size/mtime change (4254 -> 4190 bytes)
```

**Probable fix:** give each variant its own output filename, e.g.
`CADs/ISSPG/isspg_inside_equations_onshape.txt` and
`CADs/ISSPG/isspg_compact_equations_onshape.txt` — a one-line change to the `file_path`
construction in each file's `genEquationFile_editCADdirectly()` (currently at
`ActuatorAndGearbox_ISSPG_inside.py:818` and `ActuatorAndGearbox_ISSPG_compact.py:811`).

**Status:** open — not yet fixed.
