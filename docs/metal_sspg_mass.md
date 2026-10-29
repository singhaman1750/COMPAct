# Metal SSPG: why the mass is too high, and what would fix it

Analysis from 2026-10-29. Nothing in the code or config was changed for it. The numbers come from
`tools/metal_analysis/sspg_mass_whatif.py`, which rebuilds one optimised design and re-weighs it
with changed values (see [Reproduce](#reproduce)).

## Status

- **Change #1 done for SSPG (2026-10-30):** only the ring (ring pitch circle to `ring_OD`,
  `fw_r + clearance_planet` long) is weighed as steel; the rest of the gearbox casing (output-bearing
  holder, case-mounting ring, fillet) is aluminium. 3dp results are bit-identical; the CAD is
  unchanged.
  - MN8014 6:1 metal: 1,357 → **1,067 g** (same gear set).
  - U8_Lite 6.5:1 metal: 1,224 → **979 g**; the optimiser now picks module 0.5, 25/56/137
    (ratio 6.48) instead of module 0.6, 23/52/127 (the metal golden baseline was re-recorded).
  - With the ring steel, a thinner ring wall (#9) now saves about 20 g.
- **CPG done too (2026-10-30):** the same split (steel ring of the mass model's 5 mm thickness);
  U8_Lite 10:1 metal 1,032 → 802 g with a new gear set.
- The other changes (#2–#8) are still open, and #1 is still open for the other gearbox types.
- The tables below are the analysis **before** change #1. `tools/metal_analysis/sspg_mass_whatif.py`
  now starts from the code with #1 in it.

## Summary

Metal mode (`--material metal`: steel gears, aluminium structure) reuses the 3D-printed SSPG design,
so metal masses come out too high. For MN8014 at 6:1, the metal optimum (1,357 g) is **heavier than
the 3D-printed one** (778 g). For comparison, a commercial metal actuator of the U8 class (T-motor
AK80-6, U8-size motor, 6:1) weighs about 485 g (from memory, not checked against the datasheet).

Two causes carry most of the extra mass:

1. **The whole gearbox casing is weighed as steel.** The casing (ring gear + output-bearing holder +
   case-mounting ring + fillet) is one printed part, and the mass code weighs all of it at gear
   density. A metal actuator would use a steel ring in an aluminium housing. This is already
   follow-up task 1 under "Material modes" in [ISSUES.md](../ISSUES.md).
2. **The planet width is set by two printed-style planet bearings, not by the steel.** The planet
   must hold two 3.5 mm bearings plus a 1 mm gap (8 mm). Steel needs only 1.7 mm (U8_Lite) or
   3.6 mm (MN8014).

The other 3D-printing values (wall thicknesses, clearances, plate thicknesses) add more. This is
follow-up task 2 under "Material modes" in ISSUES.md.

## Mass breakdown of the metal optimum

| Part | U8_Lite, 6.5:1 | MN8014, 6:1 |
|---|---|---|
| Design | Ns 23 / Np 52 / Nr 127, module 0.6, 3 planets | Ns 26 / Np 52 / Nr 130, module 0.5, 3 planets |
| **Total** | **1,224 g** | **1,357 g** |
| Motor | 238 g | 392 g |
| **Gearbox casing (steel)** | **455 g** (ring 95 g + rest 360 g) | **524 g** (ring 82 g + rest 442 g) |
| Motor case (aluminium) | 157 g | 168 g |
| Planets (3×) | 129 g | 85 g |
| Output bearing | 81 g | 50 g |
| Carrier | 73 g | 51 g |
| Sun | 49 g | 47 g |
| Secondary carrier, retainer, small bearings | 43 g | 40 g |
| Planet width: actual / steel needs | 8.0 / 1.7 mm | 8.0 / 3.6 mm |
| Ring gear OD / motor OD | 86.2 / 87.1 mm | 75.0 / 87.8 mm |

For MN8014 the ring gear is much smaller than the motor case, so the code fills the space between
them with a solid ring ("case mounting" + "fillet"), all weighed as steel.

## Candidate changes

Savings are for each change alone, on the designs above. They overlap, so they don't add up exactly.

| # | Change | U8_Lite | MN8014 | Confidence it is realistic | Why |
|---|---|---|---|---|---|
| 1 | Casing as aluminium, only the ring gear as steel (mass code) | −236 g | −290 g | **High** | Metal actuators use a steel ring in an aluminium housing; the geometry is unchanged, only the material. |
| 2 | One planet bearing instead of two (planet ≈ stress width, ≥ 3.5 mm) | −168 g | −161 g | **High** on direction, **medium** on value | The value depends on the bearing chosen; very narrow planets raise alignment concerns. |
| 3 | `clearance_motor_and_case_min` 5 → 2 mm | −91 g | −92 g | **Medium** | Machined parts sit closer; the limit depends on wiring and cooling around the motor. |
| 4 | `sec_carrier_thickness` 5 → 3, `sun_coupler_hub_thickness` 4 → 3, `bearing_retainer_thickness` 2 → 1.5 | −76 g | −110 g | **Medium** | Aluminium is about 3× stronger and stiffer than PLA; engineering judgement, no stress check. |
| 5 | `Motor_case_thickness` 2.5 → 1.5, `base_plate_thickness` 4 → 2.5, `case_mounting_surface_height` 4 → 3 | −75 g | −67 g | **Medium** | Common machined-aluminium sizes; the base plate carries the motor, so be careful below 2.5 mm. |
| 6 | `clearance_planet`, `standard_clearance_1_5mm`, `clearance_sun_coupler_sec_carrier` 1.5 → 0.5 mm | −61 g | −70 g | **Medium–low** | `standard_clearance_1_5mm` is used in many places, not all of them print gaps; it would need splitting by role first. |
| 7 | `bearing_mount_wall_bolt_dia_multiple` 2 → 1.5 | −47 g | −36 g | **Low–medium** | Threads in aluminium allow thinner walls than plastic with inserts; the output load needs checking. |
| 8 | `planet_shaft_dia` 8 → 4 mm | −10 g | −9 g | **Low** | Small effect; the pin size should follow the bearing choice in #2. |
| 9 | Ring wall (`ringRadialWidthMM`) 5 → 3 mm | +4 g | +4 g | **High** that it doesn't help alone | With the ring smaller than the motor, the material just moves into the case-mounting ring. It only helps after #1. |
| — | `tight_clearance_3DP` 0.4, `loose_clearance_3DP` 0.8 | 0 g | 0 g | **High** they should differ for metal | CAD fits only; no mass effect. |

**Combined:**

| | U8_Lite, 6.5:1 | MN8014, 6:1 |
|---|---|---|
| Now | 1,224 g, 65.0 mm wide | 1,357 g, 67.5 mm wide |
| #1 + #2 | 847 g, 60.5 mm | 950 g, 63.1 mm |
| Everything | 672 g, 51.5 mm | 766 g, 54.1 mm |

## Would the Onshape CAD break?

Predictions from how the variables are used; the model was not opened (no Onshape API calls).
Each can be checked in the browser by typing the value into the SSPG document's variables.

| # | CAD changes? | Risk | Why |
|---|---|---|---|
| 1 | No (mass code only) | **None** | But the CAD still draws a one-piece ring + casing, not a steel ring in an aluminium housing. |
| 2 | Yes | **High** | The planet is drawn for two 3.5 mm bearing pockets, and the gap between them is drawn in the CAD, not sent from the code. A ~3.6 mm planet would make the pockets overlap. Needs a one-bearing planet in the CAD. |
| 3 | Yes | **Low–medium** | The CAD already handles values ≥ 5 (the gap grows when the ring is wider). Below 5 is untested: the chamfer, grip pattern and wire slot could reach the motor space. |
| 4 | Yes | **Medium–high** | Bolt heads are sunk into these plates (M5 head 5 mm, M3 head 3 mm); in 3 mm plates the counterbores cut through or leave zero thickness. |
| 5 | Yes | **High** (case wall), **medium** (others) | The grip pattern is cut 2 mm deep (`pattern_depth`), so a 1.5 mm wall gets holes. `case_mounting_bolt_depth` (4.5) is deeper than a 3 mm mounting surface. |
| 6 | Yes | **Medium–high** | Small clearances make faces touch or coincide, a common cause of Onshape boolean failures; one value drives many features. |
| 7 | Yes | **High** | The output bolt sits mid-wall, 3 mm from the bearing seat with a 6 mm wall; its M4 nut pocket (7 mm across flats) reaches 3.5 mm, cutting 0.5 mm into the seat. With 8 mm it clears by 0.5 mm. |
| 8 | Yes | **High** | The planet pin is an M5 bolt and can't pass through a 4 mm shaft; the shaft must also match the planet bearings' bore (8 mm). |
| 9 | Yes | **Low** | Only the ring OD changes, inside a case sized by the motor. |

## Suggested way forward

1. Do #1 in the mass code (no CAD risk); it changes metal results only, so the metal golden
   baselines are re-recorded in the same commit.
2. Try #3 by hand in the Onshape browser to see whether the CAD survives a 2 mm gap.
3. Plan the rest as a **metal SSPG variant**: a metal design block in `sspg_params.json` chosen in
   metal mode, plus CAD work for a one-bearing planet, smaller or shallower fasteners, a shallower
   grip pattern, and possibly a separate ring part.

## Caveats

- One gear set per motor. With other values the optimiser may choose a different design, so real
  savings differ somewhat.
- The suggested values are engineering judgement, not stress or tolerance calculations.
- The 3dp results and the Onshape interface are not affected by any of this.

## Reproduce

```bash
python tools/metal_analysis/sspg_mass_whatif.py U8_Lite 6.5
python tools/metal_analysis/sspg_mass_whatif.py MN8014 6
```

The script runs the SSPG optimiser for the motor and ratio (metal and 3dp), prints the metal
mass breakdown, then rebuilds the same gear set with each change and prints the new mass. It runs
in a temporary CAD folder and changes no files. Since change #1 is in the code, the script's base
already has the steel ring and aluminium housing (it also prints the mass the same gear set had
with the whole casing steel); the numbers in the tables above were made before, with #1 estimated
by re-weighing the non-ring part of the casing.
