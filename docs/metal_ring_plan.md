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
| WPG | U8_Lite 20:1 | 1,748 → 1,238 g (new gear set 56/48/36/152/140; the old set would be 1,167 g but costs more: ratio 19.91, wider gears) |
| INWPG dependent | RI100 20:1 | 2,410 → 1,718 g (same gear set) |
| INWPG independent | RI100 20:1 | 2,517 → 1,854 g (same gear set) |
| IDSPG | RO100 20:1 | 3,003 → 2,429 g (same gear sets; rings 2,543 g, plus the stage-1 sun hub as aluminium) |
| INDSPG | RI100 20:1 | 2,032 → 1,445 g (same gear sets; rings and the stage-1 sun hub) |
| ISSPG compact | RO100 6.5:1 | 2,117 → 1,939 g (same gear set) |
| ISSPG inside | RO100 6.5:1 | 2,192 → 2,025 g (same gear set) |

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

### WPG (`ActuatorAndGearbox.py`, `wolfromPlanetaryActuator.getMassKG_3DP`) — done
- **Ring 1 (fixed) in `gearbox_casing_mass`:** steel = the mass model's `ring_gear1` piece (pitch
  `Nr1 × module1` to `ring_gear1_OD = bearing_ID + 4 × 1.5`, `ring1FwMM` long); bearing holder, spacer
  wall and case mounting are aluminium. `spacer_wall_for_ring2_*` renamed `spacer_wall_for_ring1_*` (it is
  built on ring 1's OD; mass model only, not in the CAD).
- **Ring 2 (output) `small_ring_mass`:** the annulus (pitch to `+ 2 × module2 + 2 × small_ring_case_thickness`)
  is split by height: `small_ring_gear` (`ring2FwMM`) is steel, `small_ring_carrier_wall`
  (`carrier_thickness + carrier_bearing_step_width + clearance_planet`) aluminium; the end wall (inner carrier
  bearing seat) and the output-bearing sleeve are aluminium.
- Stored: `ring_gear1_mass`, `gearbox_housing_mass`, `small_ring_gear_mass`, `small_ring_housing_mass`. Not
  printed: WPG copies `print_mass_of_parts_3DP` into its results file, and new rows would change the 3dp results.
- **Open notes (not changed here):**
  - Ring 1's mass-model OD is `bearing_ID + 6` (81 mm on the golden design); the CAD (`ring_OD_b`) and the
    motor-case sizing use pitch + 2 × `ring_radial_thickness` (84 mm). For a large Np1 − Np2 the ring-1 wall
    could reach zero or go negative (not checked).
  - End-wall height in the mass model is inner bearing width + step (8.5 mm); the CAD has
    `small_ring_output_wall_thickness` = 5. The annulus and the end wall may overlap axially.
  - Unused: `ring1_ID`, `ringFwUsedMM`, `small_ring_gear_casing_thickness`, `Ring1OuterRadiusMM`, `Ring2OuterRadiusMM`.
  - The search weighs each design with `gear_casing_big_ring_to_bearing_dist` left from the last best
    design: ISSUES bug 19 (also IDSPG, INDSPG, INWPG).

### DSPG (`ActuatorAndGearbox.py`, `getMassKG_3DP_stg1` L8621, `_stg2` L8913)
- **Exactly the SSPG pattern, per stage:** `gearbox_casing_mass = (ring + bearing holder + case mounting
  + fillet) × density_gears` (L8794, L9064); ring = pitch to `pitch + 2 × ring_radial_thickness`,
  length `ringFwMM + clearance_planet` (L8749-8783, L9013-9053).
- **Steel:** the existing `ring_volume` of each stage (no thick-ring decision needed).

### ISSPG compact / inside (`ActuatorAndGearbox_ISSPG_compact.py` / `_inside.py`, `getMassKG_3DP`) — done
- `ring_gear_volume` runs from the pitch circle to the stator bore. Steel = pitch to min(pitch + 2 × module +
  2 × `ring_stator_case_thickness`, bore), `ringFwUsedMM` long — the ring the search already allows in
  `maxRingGearOD()` (no separate ring-wall key in ISSPG); the rest of the ring, the bearing holder, the
  ring-stator tube and the ring hub are aluminium.
- New `ring_gear_steel_mass` / `ring_housing_mass`, printed under `ring_mass` (log mode only).
- The sun (with its rotor-coupler hub) stays steel: sun-hub follow-up.

### ICPG (`ActuatorandGearbox_ICPG.py`, `getMassKG_3DP` L1050)
- **Already split by name:** `density_steel` / `density_alum` (= gear / structure density);
  `ring_gear_mass = vol_ring_net × density_steel` (L1261) with `vol_ring_net` = teeth (pitch to
  **`stator_ID`**) + mounting flange + bearing support + middle section + 6 bolt bosses (L1187-1215).
- **Steel:** the teeth annulus pitch + 2 × wall over `fw_ring_teeth_m`; the rest of `vol_ring_net` aluminium.

### IDSPG (`ActuatorandGearbox_IDSPG.py`, `getMassKG_3DP_stg1` / `_stg2`) — done
- **Stage 1:** `ring_gear_volume` runs from the pitch circle to the stator bore. Steel = pitch to pitch +
  2 × `ring1RadialWidthMM` (the minimum wall the stage-1 search keeps: ring PCD ≤ `Stator_ID` − 2 × it), same
  length; the rest out to the bore, the bearing steps, the top support and the pattern bulge are aluminium.
- **Stage 2:** the existing `ring_gear_volume` (pitch + 2 × `ring_radial_thickness`) is steel, as DSPG; casing
  support, bearing step and bearing support are aluminium.
- New `ring_gear_steel_mass_stg1/2` and `ring_housing_mass_stg1/2`, printed under `ring_gear_mass_stg1/2`.
- **Stage-1 sun:** the sun gear and its shaft pieces (shaft, carrier-bearing step, bottom bearing support)
  stay steel; the hub disc that couples the sun to the rotor (Ø `rotor_mount_hole_PCD` + hole + 6,
  `sun_coupler_hub_thickness1` thick, minus its share of the central bolt hole) is aluminium. New
  `sun_steel_mass_stg1` / `sun_hub_mass_stg1`. The stage-2 sun (inside `carrier_mass_stg1`) stays steel.
- **Open:** ISSUES bug 20 (stage-2 bearing step has a negative volume).

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

### INDSPG (`ActuatorandGearbox_INDSPG.py`, `getMassKG_3DP_stg1` / `_stg2`) — done
- **Stage 1:** `ring_gear_volume` runs from the pitch circle to the rotor bore (`rotor_ID − 2 × loose_clearance_3DP`).
  Steel = pitch to min(pitch + 2 × `ring_radial_thickness`, that bore), `ringFwUsedMM` long — the stage-1 search
  only keeps ring PCD ≤ `rotor_ID` − 6, so the clip can bind; the rest of the housing is aluminium.
- **Stage 2:** the existing `ring_gear_volume` (pitch + 2 × `ring_radial_thickness`, `fw_r2`) is steel, as DSPG.
- **Stage-1 sun:** gear and shaft steel, the rotor-coupler hub (Ø `sun_hub_dia1` × `sun_coupler_hub_thickness1`)
  aluminium, as IDSPG. The stage-2 sun (inside the stage-1 carrier) stays steel.
- Stored, not printed (the parts printout goes into the results file).
- **Open:** ISSUES bug 21 (stage-1 negative volumes, unused stage-2 volumes, possible overlap).

### INWPG dependent / independent (`ActuatorAndGearbox_INWPG_*.py`, `getMassKG_3DP`) — done
- **Ring 1 in `gearbox_casing_mass`:** the existing `ring_volume` runs from the pitch circle to
  `gearbox_casing_top_OD` (ring + casing wall). Steel = the ring itself, pitch to the code's
  `ring_OD = pitch + 2 × module + 2 × ringRadialWidthMMBig`, `ring1FwMM` long (`ring_gear1_volume`); the casing
  wall around it, bearing holder, case mounting, plate and casing top (/ bottom, dependent) are aluminium.
- **Ring 2 `small_ring_mass`:** as WPG; `small_ring_gear` (`ring2FwMM`) steel, carrier wall, end wall and
  output-bearing sleeve aluminium. Ring wall `ringRadialWidthMMSmall` (4).
- Stored, not printed (the parts printout goes into the results file).

## Order

1. **DSPG** (pure SSPG pattern, biggest framed saving) → 2. **WPG** (two rings, framed) →
3. **INSSPG type 1 / 2** (existing ring volume, three branches) → 4. **INCPG dependent / independent** →
5. **INWPG dependent / independent** → 6. **ISSPG compact / inside** → 7. **ICPG** → 8. **IDSPG** →
9. **INDSPG**. Types with the existing ring volume come first; the thick-ring types need decision 1.

## Follow-up: sun hubs (all types)

Every type weighs its whole sun at gear density, including the hub that couples it to the motor rotor
(SSPG, CPG, WPG, DSPG, INCPG, INWPG, ISSPG, INSSPG; ICPG as `density_steel`). IDSPG and INDSPG stage 1 now
weigh that hub as aluminium (the Ø84 × 4 mm hub was 174 g of its 224 g sun on the golden design). The
other types keep the all-steel sun until the same split is applied to them, one rule for all.

## After all types

- Update `docs/metal_sspg_mass.md` / ISSUES "Material modes" follow-up 1 (done for all types).
- Re-run the actuator-map metal sweep (all motors, metal only, ~1 h) and release map v1.1 (metal map
  without the casing overestimate; the 3dp map is unchanged).
- Follow-up 2 of "Material modes" (separate metal thicknesses / clearances) stays open.
