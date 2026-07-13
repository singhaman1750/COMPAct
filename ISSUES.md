# Known Issues / Findings — `bearings_discrete` and `nuts_and_bolts_dimensions`

Notes from an audit of the `bearings_discrete` and `nuts_and_bolts_dimensions` classes,
duplicated across:

- `ActuatorAndGearbox.py` (OLD — shared by SSPG/CPG/DSPG/WPG)
- `ActuatorandGearbox_ICPG.py`
- `ActuatorandGearbox_INSSPG.py`
- `ISSPG_inside_gen_eq.py`
- `ISSPG_compact_gen_eq.py`
- `InrunnerCPG_dependent_gen_eq.py`
- `InrunnerCPG_independent_gen_eq.py`

## 1. `bearings_discrete` — OD table vs ID table content differ

`bearings_discrete` supports two lookup modes: by inner diameter (`idRequiredMM`, the
default) and by outer diameter (`odRequiredMM`, opt-in). These two modes drew from
**two different bearing catalogues**, not one shared table:

- **28 rows are common** to both tables.
- **Rows only in the OD-table** (not available to an ID-based lookup):
  `[44.45, 53.975, 6.35, 0.031]`, `[50, 62, 6, 0.036]`
- **Rows only in the ID-table** (not available to an OD-based lookup):
  `[28, 52, 12, 0.096]`, `[32, 58, 13, 0.122]`

Practical effect: a request that could resolve to one of these non-overlapping rows
gets a **different physical bearing** depending on whether you look up by ID or by OD
— e.g. a bearing needing `OD ≈ 53mm` only exists in the OD-table, and a bearing needing
`ID ≈ 28mm` with a wide 12mm section only exists in the ID-table.

**Status:** documented, not merged into one catalogue. Unifying the two tables into a
single combined catalogue is a bigger, more consequential change (it would alter which
physical bearing gets selected for some inputs) and was intentionally left as a
separate decision rather than folded in silently.

## 2. Both tables were unsorted — now fixed

The bearing lookup in both branches is a **linear scan** that assumes the table is
sorted ascending by the column it searches on. Neither table actually was:

- **ID-table**: `[76.2, 88.9, 6.35, 0.07]` (ID = 76.2mm) was placed *before*
  `[75, 95, 10, 0.149]` (ID = 75mm) — i.e. a larger-ID row appeared before a
  smaller-ID row. For a request of `idRequiredMM = 75`, the scan would stop at the
  76.2mm row and never reach the exact 75mm match later in the list.
- **OD-table**: `[44.45, 53.975, 6.35, 0.031]` (OD = 53.975mm) was placed *before*
  `[40, 52, 7, 0.031]` (OD = 52mm) — same class of bug on the OD axis.

Both were present identically in all 7 files (the ID-table bug in
`ISSPG_inside_gen_eq.py`, `InrunnerCPG_dependent_gen_eq.py`,
`InrunnerCPG_independent_gen_eq.py`, and `ISSPG_compact_gen_eq.py`'s missing-rows
predecessor; the OD-table bug in all four dual-mode files plus the three files it was
later ported into).

**Status:** fixed. Both tables are now sorted ascending by their respective lookup
column (ID for the ID-table, OD for the OD-table) in all 7 files, and the linear scans
now behave correctly. `bearings_discrete` is fully converged — identical constructor
signature, table content, sort order, and bounds-checking — across all 7 files.

## 3. `nuts_and_bolts_dimensions` — two remaining differences

Unlike `bearings_discrete`, this class was already mostly consistent. Two real
(non-cosmetic) differences remain open:

### 3a. `ActuatorandGearbox_INSSPG.py` silently falls back instead of raising

| Situation | OLD / ICPG / ISSPG_inside / ISSPG_compact / INCPG_dependent / INCPG_independent | INSSPG |
|---|---|---|
| Unknown socket-head bolt diameter | `raise ValueError(f"Socket head bolt M{diameter} not found.")` | `return [diameter*1.5, diameter]  # Safe fallback` |
| Unknown CSK bolt diameter | `raise ValueError(f"CSK bolt M{diameter} not found.")` | `return [diameter*2, diameter*0.5]  # Safe fallback` |
| Unknown nut diameter | `raise ValueError(f"No nut data found for bolt diameter M{diameter}")` | `return [diameter*1.5, diameter*0.8]  # Safe fallback` |

INSSPG is the only one of the 7 files that never raises here — an unlisted bolt/nut
size silently returns an estimated dimension instead of erroring out.

### 3b. Attribute name split: `nut_thickness` vs `nut_depth`

| Files using `self.nut_thickness` | Files using `self.nut_depth` |
|---|---|
| OLD, ICPG, INSSPG | ISSPG_inside, ISSPG_compact, INCPG_dependent, INCPG_independent |

Same computed value, different attribute name. Code reading `.nut_thickness` off an
ISSPG/INCPG instance (or `.nut_depth` off an OLD/ICPG/INSSPG instance) would raise
`AttributeError`.

**Status:** open — not yet fixed. Everything else in this class (bolt-head dimension
table, nut dimension table) is identical across all 7 files.
