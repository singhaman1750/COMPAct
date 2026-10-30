# Metal mode: steel ring, aluminium housing, for every gearbox type (plan)

Plan made on 2026-10-30 on the branch `metal-ring-steel-all` (from dev `0dad829`). **Planning only**:
nothing in the code changes until each step is approved. SSPG (PR #107) and CPG (PR #109) are done;
this plan covers the 13 other types.

## The rule (the same as SSPG and CPG)

In metal mode only the **ring** is steel; everything else in the gearbox casing is aluminium.

- **Steel ring:** an annulus from the ring's **pitch circle** (`Nr × module` of the gear it meshes
  with) to **pitch circle + 2 × ring wall**, over the **ring length the mass model uses**.
- **The rest** of every volume that is now weighed at gear density as part of the casing (bearing
  holders, mounting structures, fillets, spacer walls, hubs, the part of a thick "ring" volume beyond
  the ring wall) becomes structure density (aluminium in metal mode).
- **3D-printed results stay bit-identical**: when gear and structure density are equal (3dp), the
  code keeps the original expression (the same-density branch used for SSPG / CPG).
- **The CAD is untouched** (mass only). The results CSV format doesn't change.
- **Golden check:** only that type's metal golden case may change (lighter, possibly a different gear
  set); it is re-recorded in the same commit with old → new values. Every other case must stay
  unchanged.
- **Tests:** the steel-ring and housing volumes re-derived independently, 3dp unchanged, the new metal
  optimum.

### One implementation pattern for all types

The geometry doesn't change, only the material of part of it. So in each mass function:

```python
steel_ring_volume = pi/4 * ((ring_PCD + 2*ring_wall)**2 - ring_PCD**2) * ring_length   # per ring
if density_gears == density_structure:          # 3D printed: the original expression, bit-identical
    casing_mass = (all the casing volumes) * density_gears
else:
    casing_mass = steel_ring_volume * density_gears + (all the casing volumes - steel_ring_volume) * density_structure
```

The total volume stays exactly the mass model's; only the steel share changes. The steel ring must
lie inside the mass model's ring volume (checked by a test).

## Done so far

| Type | Metal golden design | Before → after |
|---|---|---|
| SSPG | U8_Lite 6.5:1 | 1,224 → 979 g (new gear set) |
| CPG | U8_Lite 10:1 | 1,032 → 802 g (new gear set) |
| DSPG | U8_Lite 20:1 | 1,743 → 1,241 g (same gear sets) |
| INSSPG type 1 | RI100 6.5:1 | 1,861 → 1,524 g (same gear set) |
| INSSPG type 2 | RI100 6.5:1 | 1,616 → 1,304 g (same gear set; ring housing still the older formula, ISSUES bug 4) |

## Overview of the 13 remaining types

Numbers are for each type's golden metal design (the case that will be re-recorded). "At gear density"
is the casing / ring mass now weighed as steel; the **saving is a rough estimate** (steel ring taken as
pitch circle + 2 × 5 mm over the ring face width + 1.5 mm; the rest at aluminium), refined per type.

| Type | Golden metal case | Total now | Casing / ring masses now at gear density | Rings | Steel ring (rough) | Saving (rough) | Effort |
|---|---|---|---|---|---|---|---|
| WPG | U8_Lite 20:1 | 1,748 g | `gearbox_casing_mass` 596 + `small_ring_mass` 353 | 2 | ~107 g | **~550 g (32 %)** | ~1 h |
| DSPG | U8_Lite 20:1 | 1,743 g | `gearbox_casing_mass_stg1` 554 + `_stg2` 356 | 2 (one per stage) | ~145 g | **~500 g (29 %)** | ~1 h |
| ISSPG compact | RO100 6.5:1 | 2,117 g | `ring_mass` 340 | 1 | ~101 g | ~160 g (7 %) | ~45 min |
| ISSPG inside | RO100 6.5:1 | 2,192 g | `ring_mass` 315 | 1 | ~101 g | ~140 g (6 %) | ~20 min |
| ICPG | RO100 10:1 | 2,714 g | `ring_gear_mass_kg` 690 | 1 | ~112 g | ~380 g (14 %) | ~45 min |
| IDSPG | RO100 20:1 | 3,003 g | `ring_gear_mass_stg1` 559 + `_stg2` 364 | 2 | ~197 g | ~480 g (16 %) | ~1 h |
| INSSPG type 1 | RI100 6.5:1 | 1,861 g | `ring_mass` 580 (3 branches) | 1 | ~99 g | ~320 g (17 %) | ~45 min |
| INSSPG type 2 | RI100 6.5:1 | 1,616 g | `ring_mass` 533 (3 branches) | 1 | ~86 g | ~290 g (18 %) | ~20 min |
| INCPG dependent | RI100 10:1 | 1,776 g | `gearbox_casing_mass` 661 | 1 | ~54 g | ~400 g (22 %) | ~45 min |
| INCPG independent | RI100 10:1 | 1,848 g | `gearbox_casing_mass` 604 | 1 | ~54 g | ~360 g (20 %) | ~20 min |
| INDSPG | RI100 20:1 | 1,988 g | `ring_gear_mass_stg1` 389 + `_stg2` 576 | 2 | ~142 g | ~540 g (27 %) | ~1 h |
| INWPG dependent | RI100 20:1 | 2,410 g | `gearbox_casing_mass` 888 + `small_ring_mass` 309 | 2 | ~162 g | **~680 g (28 %)** | ~1 h |
| INWPG independent | RI100 20:1 | 2,517 g | `gearbox_casing_mass` 790 + `small_ring_mass` 314 | 2 | ~119 g | **~650 g (26 %)** | ~20 min |
| **Total** | | | | | | | **~9 h** |

Parts already weighed as aluminium are not touched: motor cases (`density_structure`) and the
inrunner rotor hubs / couplers (`densityAluminum`, `densityRotor`).

## Decisions needed

1. **Thick "ring" volumes.** In many types the mass model's ring volume is **thicker than a ring wall**:
   it runs to the stator bore (ISSPG, ICPG, IDSPG stage 1), the rotor bore (INDSPG stage 1), the output
   bearing's bore + 6 mm (WPG big ring), the casing OD (INWPG big ring) or the bearing-holder / mounting OD
   (INCPG). Proposal (your definition): **steel only from the pitch circle to pitch circle + 2 × ring
   wall**, the rest of that volume aluminium (a steel ring insert in an aluminium housing).
   Alternative: the whole toothed volume steel (less saving, less realistic).
2. **Which ring wall** for types whose mass model has no explicit ring wall: proposal, the type's own
   config value (`ring_radial_thickness` / `ringRadialWidthMM*` / `small_ring_case_thickness` /
   `small_ring_radial_width` / `big_ring_radial_thickness`); where a type has none, 5 mm as a new
   config key (to agree per type).
3. **Ring length:** the length the mass model already uses for the ring (e.g. `ringFwUsedMM` =
   face width + clearance), per type.
4. **Wolfrom output ring** (WPG, INWPG ×2): its volume also holds bearing seats and the output-bearing
   structure; only its toothed annulus becomes steel.
5. **PR grouping:** decided: one PR per type (as SSPG / CPG).

## Per type

### WPG (`ActuatorAndGearbox.py`, `wolfromPlanetaryActuator.getMassKG_3DP`, from L6251)
- **At gear density:** `gearbox_casing_mass` (L6476-6480) = bearing-holding structure + spacer wall for
  ring 2 + case-mounting structure + **ring gear 1**; `small_ring_mass` (L6533) = small-ring annulus +
  small-ring bearing structure + output-bearing structure.
- **Rings:** big ring 1: pitch `Nr1 × module1`, mass-model OD `bearing_ID + 1.5 × 4` (thick), length
  `ring1FwMM`. Small (output) ring 2: pitch `Nr2 × module2`, OD `+ 2 × module2 + 2 × small_ring_case_thickness`,
  length `ring2FwMM + carrier + step + clearance`.
- **Steel:** ring 1 annulus (pitch + 2 × wall, wall = decision 2) × `ring1FwMM`; ring 2 annulus × `ring2FwMM`.
- **Note:** the CAD / mass mismatches found in the classification plan (motor-case gap, bearing-mount
  ring term) are not touched here.

### DSPG (`ActuatorAndGearbox.py`, `getMassKG_3DP_stg1` L8621, `_stg2` L8913)
- **Exactly the SSPG pattern, per stage:** `gearbox_casing_mass = (ring + bearing holder + case mounting
  + fillet) × density_gears` (L8794, L9064); ring = pitch to `pitch + 2 × ring_radial_thickness`,
  length `ringFwMM + clearance_planet` (L8749-8783, L9013-9053).
- **Steel:** the existing `ring_volume` of each stage (no thick-ring decision needed).

### ISSPG compact / inside (`ActuatorAndGearbox_ISSPG_compact.py` / `_inside.py`, `getMassKG_3DP`)
- **At gear density:** `ring_mass = (ring_gear + bearing-holding structure + ring-stator structure + ring hub) × density_gears` (compact L1492).
- **Ring:** pitch `Nr × module` to **`stator_ID`** (thick), length `ringFwMM + clearance_planet` (L1462-1485).
- **Steel:** pitch + 2 × wall (decision 1, 2) × that length; the rest aluminium. Inside: the same code
  at its own lines.

### ICPG (`ActuatorandGearbox_ICPG.py`, `getMassKG_3DP` L1050)
- **Already split by name:** `density_steel` / `density_alum` (= gear / structure density);
  `ring_gear_mass = vol_ring_net × density_steel` (L1261) with `vol_ring_net` = teeth (pitch to
  **`stator_ID`**) + mounting flange + bearing support + middle section + 6 bolt bosses (L1187-1215).
- **Steel:** the teeth annulus pitch + 2 × wall over `fw_ring_teeth_m`; the rest of `vol_ring_net` aluminium.

### IDSPG (`ActuatorandGearbox_IDSPG.py`, `_stg1` L1655, `_stg2` L1930)
- **Stage 1:** `ring_gear_mass = (ring_gear_volume (pitch to Stator_ID) + bearing steps + top support +
  pattern bulges) × density_gears` (L1758-1769).
- **Stage 2:** `ring_gear_mass = (ring_gear_volume (pitch + 2 × ring_radial_thickness) + casing support
  + bearing step + bearing support) × density_gears` (L2026-2044).
- **Steel:** stage 1 pitch + 2 × wall (decision 1, 2); stage 2 the existing `ring_gear_volume`.

### INSSPG type 1 / type 2 (`ActuatorandGearbox_INSSPG.py`, `_getMassKG_3DP_type1` L1218, `_type2` L982)
- **At gear density:** `ring_mass = ring_vol_net × density_gears`, in **three branches** per type (bearing
  vs ring size, L1160 / 1173 / 1183 and L1391 / 1403); `ring_vol_net` = ring gear (pitch to
  `pitch + 2 × ring_radial_thickness`, length `ringFwMM`) + top mount + bearing step + bottom part +
  bearing support.
- **Steel:** the existing `ring_gear_volume` in every branch.
- **Note:** ISSUES bugs 4 / 10 live in these functions; not touched.

### INCPG dependent / independent (`ActuatorAndGearbox_INCPG_*.py`, `getMassKG_3DP`)
- **At gear density:** `gearbox_casing_mass = (ring + bearing holder + case mounting + mounting plate
  − chamfer + casing bottom) × density_gears` (dependent L1942-1943).
- **Ring:** pitch `Nr × module2` to **`ring_OD_used`** = the bearing-holder or mounting OD (thick,
  L1910-1914), length `fw_r + 1.5`.
- **Steel:** pitch + 2 × wall (`ring_radial_thickness`, already in the code: `ring_OD = Nr·module2 +
  module2 + 2 × ring_radial_thickness`), the rest aluminium.

### INDSPG (`ActuatorandGearbox_INDSPG.py`, `_stg1` L1535, `_stg2` L1829)
- **Stage 1:** `ring_gear_mass = (ring_gear_volume (pitch to rotor_ID − 2 × loose clearance) + top
  support + casing support + 3 bearing supports + step above rotor) × density_gears` (L1660-1669).
- **Stage 2:** `ring_gear_mass = (ring_gear_volume (pitch + 2 × ring_radial_thickness, length fw_r2) +
  casing support + bearing step + bearing support + casing step) × density_gears` (L1922-1961).
- **Steel:** stage 1 pitch + 2 × wall (decision 1, 2); stage 2 the existing `ring_gear_volume`.

### INWPG dependent / independent (`ActuatorAndGearbox_INWPG_*.py`, `getMassKG_3DP`)
- **At gear density:** `gearbox_casing_mass = (ring (pitch to **gearbox_casing_top_OD**) + bearing holder
  + case mounting + plate + casing top + casing bottom) × density_gears` (dependent L2477-2488);
  `small_ring_mass` (L2493-2510) as WPG.
- **Steel:** big ring pitch + 2 × wall (`big_ring_radial_thickness`, + `2 × module` as the code's
  `ring_OD`) × `ring1FwMM`; small ring annulus (`small_ring_radial_width`) × `ring2FwMM`.

## Order

1. **DSPG** (pure SSPG pattern, biggest framed saving) → 2. **WPG** (two rings, framed) →
3. **INSSPG type 1 / 2** (existing ring volume, three branches) → 4. **INCPG dependent / independent** →
5. **INWPG dependent / independent** → 6. **ISSPG compact / inside** → 7. **ICPG** → 8. **IDSPG** →
9. **INDSPG**. Types with the existing ring volume come first; the thick-ring types need decision 1.

## After all types

- Update `docs/metal_sspg_mass.md` / ISSUES "Material modes" follow-up 1 (done for all types).
- Re-run the actuator-map metal sweep (all motors, metal only, ~1 h) and release map v1.1 (metal map
  without the casing overestimate; the 3dp map is unchanged).
- Follow-up 2 of "Material modes" (separate metal thicknesses / clearances) stays open.
