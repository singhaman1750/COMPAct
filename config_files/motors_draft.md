# Motor data — working draft

Collected values for the planned `config_files/motors.json`. **No code reads this file.** Once a
motor's values are complete and confirmed, they move into `motors.json`.

## Decided conventions

- **Gear sizing torque:** peak torque. **Stress-check speed:** no-load speed. Both are a shared
  setting so they can be switched to rated torque / rated speed.
- **Torque source, in order of preference:** measured test torque at max current → manufacturer
  Kt × peak current → Kv-based estimate (9.55 / KV × current, marked as an estimate).
  When the test current differs from the datasheet peak current by more than 1 %, the peak
  torque is the measured Kt (test torque ÷ test current) × peak current, marked as an estimate.
  If the test table has several propellers, use the **highest measured torque** among the 100 % rows
  whose columns pass the checks (power = voltage × current; efficiency = thrust ÷ power; speed below
  KV × voltage) — this is the manufacturer's stated max torque when given (decided 2026-10-17).
  Scale to the peak current only if no valid test reached the peak current (within 1 %).
- **No-load speed:** datasheet value if given; otherwise KV × operating voltage, marked as an
  estimate.
- **Wire slot:** measured size, with `loose_clearance_3DP` (0.8 mm) built into the stored values
  as +0.4 mm on the radius. The slot length is the centre-to-centre length and is stored as
  measured. The distance from centre is a position and gets no clearance.
- **Hole diameter:** stored as the screw size (M4 → 4).

- **System (decided 2026-10-17):** 48 V supply (12S); moteus driver, 120 A. Check that the driver's
  maximum input covers a fully charged 12S pack (50.4 V).
- **KV choice (decided 2026-10-17):** one KV variant per motor model — the variant rated for 12S
  (48 V) with the highest peak torque whose peak current is within 120 A. Variants rated only up to
  6S can't run on 48 V.
  Ruled out by voltage: MN5006 (both KVs, 4–6S), MN6007 II KV320 (6S), MN7005 KV230 (6S),
  M6C12 KV280/KV400 (6S), M6C06 V3 KV320 (6S), U12 II KV60 (22–25S, i.e. 81–100 V).
- **Only the chosen variant per model goes into `motors.json`**; the others stay in this draft as
  reference data (decided 2026-10-17).
- **No-load speed:** KV × 48 V (the system voltage) for every framed motor, marked as an estimate;
  frameless motors use their datasheet no-load speed at 48 V (decided 2026-10-17).
- **Mass:** with cables.

## Chosen for `motors.json`

Framed (24): U8 Lite, U8 Lite L, U8 II, U8 II Lite, U8 II PRO, MN8012, MN8014, MN8017,
U10 Plus KV80, U10 II, MN5008 KV170, MN6007 II KV160, MN7005 KV115, MN1005 V2 KV90,
M6C06 EEE V3 KV160, M6C12 EEE KV170, M6C10 EEE KV150, M6C08 EEE KV180, M6C06 EEE KV140,
1005 EEE KV90, 7005 EEE KV115, 8118 EEE KV100, 5008 EEE KV170, 5010 EEE KV200 (24 framed).
Ruled out by voltage: MAD 5005 EEE (all KVs, 4–6S).
Frameless (5): RI100, RI80, RO100, RO80, RO60.
Vector Technics: pending (wire slots, torque decision).

## Framed outrunner motors

### U8 Lite (T-Motor) — the code's `U8`, pending confirmation

| Field | Value | Source |
|---|---|---|
| KV | 100 | datasheet |
| Operating voltage | 48 V (12S) | datasheet test voltage — pending convention |
| Peak current | 29.3 A | datasheet (180 s) |
| Peak torque | 2.73 Nm | measured test, 100 % throttle, 29.3 A, 48 V, G28×9.2 prop |
| No-load speed | ≈ 4800 rpm | estimate: KV × 48 V |
| Mass | 238 g | datasheet, incl. cable |
| Diameter × height | 87.1 × 27.05 mm | datasheet |
| Internal resistance | 170 ± 5 mΩ | datasheet |
| Stator mount | 4 × M4 @ PCD 36 mm | measured/drawing (user, 2026-10-16) |
| Rotor mount (primary) | 4 × M4 @ PCD 23 mm | measured/drawing (user, 2026-10-16) |
| Rotor mount (alternative) | 4 × M3 @ PCD 20 mm | measured/drawing (user, 2026-10-16) |
| Wire slot: distance from centre | 32 mm | measured (user, 2026-10-16) |
| Wire slot: length | 5.5 mm | measured (user, 2026-10-16) |
| Wire slot: radius | 2.9 mm | measured 2.5 mm + 0.4 mm (loose_clearance_3DP) |

Code's current `MotorU8_framed` differs: 24 V, 24 A, 750 W, 240 g, 86.8 × 26.5 mm, stator mount
PCD 32, wire slot 38 / 10 / 2.5.

### Other framed motors — specs collected, not yet complete

Missing for all of these unless noted: mounting patterns (T-Motor), wire slot, confirmation of
which ones to include.

**T-Motor U series** (store pages, 2026-10-16) — KV / voltage / mass / Ø × H / peak current /
measured torque @ current @ voltage:
- U8 Lite L: 110 / 12S / 282 g / 87.1 × 28.05 / 45.8 A / 3.87 Nm @ 45.8 A @ 47 V
- U8 II: 85 / 12S / 277 g / 87.1 × 29.1 / 19.1 A / 1.80 Nm @ 16.5 A @ 48 V
  → **peak torque 2.08 Nm** (estimate: measured Kt 1.80 / 16.5 = 0.109 Nm/A × 19.1 A peak)
- U8 II Lite: 100 / 12S / 253 g / 87.3 × 26.05 / 31 A / 2.81 Nm @ 31.1 A @ 47 V
- U8 II PRO: 100 / 12S / 287 g / 87.3 × 29.55 / 31 A / test table identical to U8 II Lite — not trusted
  → **peak torque 2.96 Nm** (estimate: Kv-based Kt 9.55 / 100 = 0.0955 Nm/A × 31 A peak)

  **Mounting and wire slot for all five U8 versions** (U8 Lite, U8 Lite L, U8 II, U8 II Lite,
  U8 II PRO) are the same as U8 Lite (user, 2026-10-16): stator mount 4 × M4 @ PCD 36;
  rotor mount 4 × M4 @ PCD 23 (alternative 4 × M3 @ PCD 20); wire slot 32 mm from centre,
  length 5.5 mm, radius 2.9 mm (2.5 + 0.4). Note: U8 II Lite and U8 II PRO have a 12 mm shaft,
  the others 15 mm — the shaft size isn't used by the code.
- U10 II: 100 / 12S / 415 g / 98.6 × 33.1 / 32.4 A / 3.59 Nm @ 32.4 A @ 48 V
  Mounting (from the T-Motor drawing, dimensioned): stator mount 4 × M5 @ PCD 40; rotor mount
  4 × M4 @ PCD 23 (primary), alternative 4 × M3 @ PCD 20.
  Wire slot (**measured from the drawing, approximate** — slot not dimensioned; scale 2.85 px/mm from
  the Ø98.6 outline): ≈ 45 mm from centre (± 1), length ≈ 9 mm centre-to-centre (± 1.5; ≈ 13.5 end
  to end), radius ≈ 2.25 mm (± 0.5) → stored 2.65 mm (+ 0.4). Replace with a calliper measurement
  if one becomes available.
- U12 II: 60 / 22–25S / 803 g / 106.8 × 47.6 / 41 A / 7.4 Nm @ 40.4 A @ 99.7 V
  → **peak torque 7.51 Nm** (estimate: measured Kt 7.40 / 40.4 = 0.1832 Nm/A × 41 A peak)
  Mounting (from the T-Motor drawing, dimensioned): stator mount 4 × M5 @ PCD 40; rotor mount
  4 × M4 @ PCD 23 (primary), alternative 4 × M3 @ PCD 20. Body Ø106.8 × 47.6 ✓.
  Wire slot (user, 2026-10-17): 50 mm from centre, length 7 mm (given as "width"; taken as the
  centre-to-centre length, since a 4 mm radius already makes the slot 8 mm wide — to confirm),
  radius 4.4 mm (measured 4 + 0.4). The drawing shows a cable-exit block on the rim (12.8 mm dim.).

**T-Motor U10 Plus** (test reports U.000014–16) — 88.6 × 40 mm, 500 g excl. cables, 36N40P,
15 mm shaft; torque from the test table where received:
Mounting for all three variants (user, 2026-10-16): stator mount 4 × M4 @ PCD 32; rotor mount
4 × M4 @ PCD 23 (primary), alternative 4 × M3 @ PCD 21 (first given as M4 @ 21 / M3 @ 23; the user
confirmed they were swapped). Matches the code's current `U10` (stator 4 × 4 @ 32, rotor 4 × 4 @ 23).
Wire slot (user, 2026-10-16): 37 mm from centre, length 10 mm, radius 5.4 mm (measured 5 + 0.4).
Code's current `U10` slot: 38 / 10 / 2.5.
- KV80: 6–14S, 33 A, 1500 W, 95 mΩ, 514 g incl. cables
  Test (100 % throttle, 56 V): 4.102 N·m @ 31.4 A, 3604 rpm, 1758.4 W, 11 550 g
  → **peak torque 4.31 Nm** (estimate: measured Kt 4.102 / 31.4 = 0.1306 Nm/A × 33 A peak);
  no-load ≈ 3840 rpm at 48 V (estimate: KV × 48 V; test was at 56 V)
- KV100: 6–12S, 36 A, 1700 W, 60 mΩ, 508 g incl. cables — matches the code's `U10`
  Test (100 % throttle, 48 V): 3.636 N·m @ 36.5 A, 1751.86 W, 9960 g (speed column reads
  11 814 rpm, which is impossible for KV100 at 48 V — likely a typo; not used)
  → **peak torque 3.59 Nm** (estimate: measured Kt 3.636 / 36.5 = 0.0996 Nm/A × 36 A peak);
  no-load ≈ 4800 rpm (estimate: KV × 48 V)
- KV170: 6–12S, 60 A, 2000 W, 21 mΩ, 511 g incl. cables
  Test A (100 % throttle, 24 V, other propeller): 3.342 N·m @ 58.9 A, 3307 rpm, 1413.6 W, 9517 g — all columns
  consistent (82 % motor efficiency). **Used.**
  → **peak torque 3.40 Nm** (estimate: measured Kt 3.342 / 58.9 = 0.0567 Nm/A × 60 A peak);
  no-load ≈ 8160 rpm at 48 V (estimate: KV × 48 V; test was at 24 V)
  Test B (100 % throttle, 24 V): 3.536 N·m @ 63.66 A, 1527.84 W, 9456 g; speed column reads
  9098 rpm, impossible — kept as a cross-check only (scales to 3.33 Nm, within 2 % of test A)

**T-Motor MN series** (store pages) — KV / voltage / mass / Ø × H / peak current / measured
torque @ current @ voltage:
- MN5006 KV300: 4–6S / 108 g / 55.6 × 30 / 20 A / 0.50 Nm @ 15.4 A @ 23.2 V (below peak)
  → **peak torque 0.65 Nm** (estimate: measured Kt 0.50 / 15.41 = 0.0324 Nm/A × 20 A peak)
- MN5006 KV450: 4–6S / 106 g / 55.6 × 30 / 26 A / 0.55 Nm @ 24.8 A @ 15.0 V
  → **peak torque 0.58 Nm** (estimate: measured Kt 0.55 / 24.82 = 0.0222 Nm/A × 26 A peak)

  **Mounting and wire slot for both MN5006 variants** (KV300, KV450; same Ø55.6 × 30 body):
  stator mount 4 × M3 @ PCD 25 (user, 2026-10-17); rotor mount 4 × M3 @ PCD 18 (primary),
  alternative 4 × M3 @ PCD 12 (user; drawing shows 8-M3 on Ø12 / Ø18).
  Wire slot (user, 2026-10-17): 14.5 mm from centre, length 6 mm, radius 2.9 mm (given 2.5 + 0.4).
  (Drawing estimate was 14.3 / 5.4 / 1.95.)

- MN5008 KV170: 6–12S / 128 g / 55.6 × 32 / 15 A / 0.87 Nm @ 14.6 A @ 46.9 V
  → **peak torque 0.89 Nm** (estimate: measured Kt 0.87 / 14.63 = 0.0595 Nm/A × 15 A peak)
  Mounting and wire slot: same as MN5006 (user, 2026-10-17) — stator mount 4 × M3 @ PCD 25;
  rotor mount 4 × M3 @ PCD 18 (primary), alternative 4 × M3 @ PCD 12; wire slot 14.5 mm from centre,
  length 6 mm, radius 2.9 mm.
- MN6007 II KV160: 12S / 159 g / 67.2 × 26.1 / 23.7 A / 1.49 Nm @ 23.8 A @ 47.3 V
- MN6007 II KV320: 6S / 161 g / 67.2 × 26.1 / 44.2 A / 1.37 Nm @ 44.2 A @ 23.6 V

  **Mounting and wire slot for both MN6007 II variants** (KV160, KV320; same Ø67.2 × 26.1 body),
  from the T-Motor drawing (confirmed by user, 2026-10-17): stator mount 4 × M4 @ PCD 32; rotor
  mount 4 × M3 @ PCD 18 (primary), alternatives 4 × M3 @ PCD 12 and 4 × M3 @ PCD 20 (drawn as 12-M3).
  Wire slot (measured from the drawing, scale 3.55 px/mm; confirmed by user): 24.6 mm from centre,
  length 6.3 mm centre-to-centre (10.1 end to end), radius 2.3 mm (measured 1.9 + 0.4).

- MN7005 KV115: 6–12S / 188 g / 79 × 21 / 15 A / 1.32 Nm @ 14.1 A @ 48 V
  → **peak torque 1.41 Nm** (estimate: measured Kt 1.32 / 14.07 = 0.0938 Nm/A × 15 A peak)
- MN7005 KV230: 6S / 188 g / 79 × 21 / 28 A / 1.28 Nm @ 29.2 A @ 24 V
  → **peak torque 1.23 Nm** (estimate: measured Kt 1.28 / 29.15 = 0.0439 Nm/A × 28 A peak)

  **Mounting and wire slot for both MN7005 variants** (KV115, KV230; same Ø79 × 21.8 body),
  user-approved 2026-10-17: stator mount 4 × M4 @ PCD 32 (drawing); rotor mount 4 × M4 @ PCD 23
  (primary), alternative 4 × M3 @ PCD 20 (drawing: Ø4 holes on Ø23, Ø3 holes on Ø20).
  Wire slot (**estimate** — not on the drawing; from a perspective photo and the other MN motors):
  ≈ 28 mm from centre (± 4), length ≈ 6 mm centre-to-centre (± 2), radius 2.9 mm (estimated 2.5 + 0.4).
  Replace with a calliper measurement if possible.

- MN8012 KV100: 12S / 351 g / 87.8 × 29 / 40 A / 4.06 Nm @ 40.0 A @ 46.8 V
- MN8014 KV100: 12S / 392 g / 87.8 × 31.5 / 52 A / 4.79 Nm @ 51.9 A @ 46.7 V — matches the code's `MN8014`
- MN8017 KV120: 12S / 453 g / 87.8 × 34.5 / 68.6 A / 5.80 Nm @ 68.6 A @ 46.4 V

  **Mounting and wire slot for the MN80 series** (MN8012, MN8014, MN8017), user 2026-10-16:
  mounting is the same as the U8 series — stator mount 4 × M4 @ PCD 36; rotor mount
  4 × M4 @ PCD 23 (alternative 4 × M3 @ PCD 20). Wire slot 38 mm from centre, length 10 mm,
  radius 4.4 mm (measured 4 + 0.4). The code's current `MN8014` slot (40 / 10 / 2.5) differs.
  The other MN models (MN5006, MN5008, MN6007 II, MN7005, MN1005 V2) have no mounting or slot
  data yet.

- MN1005 V2 KV90: 12S / 282 g / 107 × 23 / 32 A / 3.40 Nm @ 30.8 A @ 47.3 V
  → **peak torque 3.54 Nm** (estimate: measured Kt 3.40 / 30.76 = 0.1105 Nm/A × 32 A peak)
  Mounting (from the T-Motor drawing, dimensioned; user-approved 2026-10-17): stator mount
  4 × M4 @ PCD 32; rotor mount 4 × M4 @ PCD 23 (primary), alternative 4 × M3 @ PCD 20.
  Body Ø107 × 23 ✓ (Ø38 centre boss, Ø50 / Ø78.4 steps — not mounting patterns).
  Wire slot (**measured from the drawing, low confidence** — faint lines, 2.25 px/mm): ≈ 36 mm from
  centre (± 2), length ≈ 8 mm centre-to-centre (± 3), radius 2.4 mm (measured ≈ 2 + 0.4, ± 0.7).
  Leads are enamelled wire, so a small slot is plausible. Replace with a measurement if possible.

**Vector Technics** (product pages) — KV / voltage / mass / Ø × L / max continuous current /
stated Kt / motor mount / prop mount. Stated Kt is 17–38 % above the Kv-based value; no test
tables:
- 4006 SL: 380 / 6S / 67 g / 44.6 × 20 / 9 A / 0.033 / 4×M3 @ 25 / 4×M3 @ 12
- 6008 SL: 340 / 6S / 170 g / 68.8 × 24.3 / 35 A / 0.033 / 4×M3 @ 30 / 12×M3 @ 12, 18, 20
- 8008 SL: 90 / 12S / 210 g / 88.4 × 26 / 20 A / 0.139 / 4×M3 @ 30 / 8×M3 @ 20, 23
- 8015 SL: 100 / 12S / 420 g / 88.4 × 34 / 40 A / 0.1245 / 4×M4 @ 36 / 4×M3 @ 20 + 4×M4 @ 23
- 10005 SL: 90 / 12S / 277 g / 107 × 23 / 12.69 A / 0.1468 / 4×M4 @ 23 / 4×M4 @ 32
- 8020 PRO 120 KV: 120 / 12S / 566 g / 88.4 × 50.3 / 54 A / 0.108 / 4×M4 @ 40 / 4×M3 @ 20 + 4×M4 @ 23
  — does **not** match the code's `VT8020` (KV100, 713 g, 89.4 × 45.5)

**MAD Components EEE** (product pages) — electrical data and torque are only in images/test
sheets, not yet received:
- **M6C12 EEE — complete, all four KV variants** (product page images, read 2026-10-17: spec tables,
  drawing, test tables). Shared: body Ø72 × 27 mm (the 33.4 mm on the page = 27 body + 6.4 shaft;
  the code's 27 mm is correct), 14 pole pairs, 6 mm shaft, 60 mm 16 AWG leads.
  Stator mount 4 × M4 @ PCD 32 (primary, as in the code), alternative 4 × M3 @ PCD 25.
  Rotor mount 4 × M3 @ PCD 18 (primary, confirmed by user 2026-10-17; the code used PCD 22),
  alternatives 4 × M3 @ PCD 12 and @ PCD 22.
  Wire slot (user choice: at the point where the wires emerge; from the drawing, 3.65 px/mm): the three
  leads emerge ≈ 14 mm from centre and run radially across the stator face to the rim as a ≈ 7 mm
  bundle → slot 16 mm from centre, length 4 mm, radius 3.9 mm (3.5 + 0.4). The CAD slot can't model
  the full radial channel. Code's current `MAD_M6C12` slot: 26 / 10 / 2.5.
  Masses are taken as with cable (as for M6C06 V3). Max currents are 10–30 s limits (MAD notes).
  - KV150: 12S; 36.2 A; **peak torque 2.64 Nm measured** (24×7.2 prop, 47.6 V, 35.14 A, 4982 rpm; =
    stated max torque; the highest-current test, HAVOC 22×7.0 at 36.18 A, gave 2.52 Nm); Kt 0.0751
    (+18 % vs Kv-based); no-load ≈ 7200 rpm (KV × 48); 1725 W; 90 mΩ; 0.67 A @ 20 V; 257 g.
    Matches the code's `MAD_M6C12` (257 g, 36.2 A, 1725 W); code torque 2.31 Nm (Kv-based) → 2.64.
  - KV170: 12S; 51.5 A; **peak torque 3.03 Nm measured** (24×7.2, 47.75 V, 51.53 A, 5309 rpm); Kt 0.0588
    (+5 %); no-load ≈ 8160 rpm (KV × 48); 2460 W; 77 mΩ; 0.89 A @ 20 V; 255 g.
  - KV280: 6S; 58.4 A; **peak torque 2.11 Nm measured** (24×7.2, 23.36 V, 58.44 A, 4566 rpm); Kt 0.0362
    (+6 %); no-load ≈ 6720 rpm (KV × 24); 1365 W; 31 mΩ; 1.53 A @ 20 V; 256 g.
  - KV400: 6S; 75.7 A; **peak torque 1.71 Nm measured** (20×6.0, 23.33 V, 75.74 A, 7082 rpm); Kt 0.0226
    (−5 %); no-load ≈ 9600 rpm (KV × 24); 1766 W; 17 mΩ; 2.5 A @ 20 V; 268 g.
- **M6C10 EEE — complete, chosen KV150** (product page images read by helper agents 2026-10-17; test rows re-checked: V×I and T×ω within 0.1 %). Body Ø72 × 25 mm (31.4 incl. shaft).
  Stator mount 4 × M4 @ PCD 32 (alt. 4 × M3 @ PCD 25); rotor mount 4 × M3 @ PCD 18 (alt. 12, 22).
  Wire slot (from drawing, approx.): radial bundle 7.3 mm wide emerging ≈ 10–14 mm → 16 / 4 / 4.05.
  - **KV150 (chosen, user 2026-10-17)**: 12S; 36.3 A; **peak torque 2.377 Nm measured** (24×7.2, 47.76 V,
    36.26 A, 4801 rpm; = stated 2.38); Kt 0.0656; no-load ≈ 7200 rpm (KV × 48); 1732 W; 120 mΩ; 209 g.
  - KV200: 12S; 2.302 Nm @ 46.97 A; 201 g. KV250: 8–12S; 2.398 Nm @ 62.65 A; 213 g (rule pick by 0.9 %,
    not chosen: 1.7× the current, 12 000 rpm). KV300: 6S (ruled out).
- **M6C08 EEE — complete, chosen KV180** (product page images read by helper agents 2026-10-17; test rows re-checked: V×I and T×ω within 0.1 %). Body Ø72 × 23 mm (29.4 incl. shaft).
  Stator mount 4 × M4 @ PCD 32 (alt. 4 × M3 @ PCD 25); rotor mount 4 × M3 @ PCD 18 (alt. 12, 22).
  Wire slot (from drawing, approx.): outlet block centre 11.8 mm, leads emerge 13.5 mm, bundle 7.0 mm
  → 15.5 / 4 / 3.9.
  - **KV180 (chosen)**: 12S; 34 A; **peak torque 1.992 Nm measured** (HAVOC 22×7.0, 43.65 V — supply sagged —
    34.02 A, 4996 rpm; = stated 1.99); Kt 0.0586; no-load ≈ 8640 rpm (KV × 48); 1485 W; 119 mΩ; 180 g.
  - KV130: 12S; 1.653 Nm @ 19.92 A; 188 g. KV260 (6–8S), KV320 (6S): ruled out.
- **M6C06 EEE (non-V3) — complete, chosen KV140** (product page images read by helper agents 2026-10-17; test rows re-checked: V×I and T×ω within 0.1 %). Body Ø72 × 21 mm (27.4 incl. shaft).
  Stator mount 4 × M4 @ PCD 32 (alt. 4 × M3 @ PCD 25); rotor mount 4 × M3 @ PCD 18 (alt. 12, 22).
  Wire slot (from drawing, approx.): radial bundle 6.9 mm wide emerging ≈ 12.6 mm → 14.6 / 4 / 3.85.
  - **KV140 (chosen)**: 12S; 21 A; **peak torque 1.487 Nm measured** (24×7.2, 48.07 V, 21.01 A, 3853 rpm;
    = stated 1.49); Kt 0.0708; no-load ≈ 6720 rpm (KV × 48); 1010 W; 301 mΩ; 163 g.
  - KV220 (8S), KV320 (6S): ruled out.
- **M6C06 EEE V3 — complete** (product page images: specs, drawing, test tables; user 2026-10-17).
  Shared: Ø72.1 × 22.4 mm, 14 pole pairs, 4 mm shaft, 60 mm 16 AWG leads. Stator mount 4 × M4 @ PCD 32;
  rotor mount 4 × M3 @ PCD 18 (primary), alternatives 4 × M3 @ PCD 12 and @ PCD 20.
  Wire slot (**estimate from the drawing**, low–medium confidence — radial cable-exit block on the rim
  at 3 o'clock, opening ≈ 7.5 mm, inner edge ≈ 26–27 mm, rim 36.05 mm; following the U12 II values):
  32 mm from centre, length 7 mm, radius 4.15 mm (3.75 + 0.4).
  - KV160: 12S; max current 22.43 A; **peak torque 1.483 Nm measured** (100 % throttle, 22×6.6 prop,
    47.92 V, 22.43 A, 5443 rpm; all columns consistent); Kt 0.0661 (+11 % vs Kv-based); no-load
    ≈ 7680 rpm (estimate: KV × 48 V); max power 1075 W; 163 mΩ; no-load current 0.5 A @ 30 V;
    mass 157 g (with cable).
  - KV320: 6S; max current 43.15 A; **peak torque 1.414 Nm measured** (100 % throttle, 22×6.6 prop,
    23.52 V, 43.15 A, 5230 rpm; all columns consistent); Kt 0.0328 (+10 % vs Kv-based); no-load
    ≈ 7680 rpm (estimate: KV × 24 V); max power 1014 W; 40 mΩ; no-load current 1.0 A @ 20 V;
    mass 160 g (with cable).
  Note: MAD's max current is a 10–30 s short-term limit (MAD note), shorter than T-Motor's 180 s rating.
- **1005 EEE — complete, KV90** (product page images read by helper agents 2026-10-17; test rows re-checked: V×I and T×ω within 0.1 %). Body Ø107 × 22.5 mm. Stator mount 4 × M4 @ PCD 32;
  rotor mount 4 × M4 @ PCD 23 (alt. 4 × M3 @ PCD 20). Wire slot (from drawing): oval slot along the
  circumference at 6 o'clock, 10.1 × 5.8 mm, centre 34.0 mm → 34 / 4.3 / 3.3.
  KV90: 12S; 34 A; **peak torque 3.92 Nm measured** (CB2 PRO 32×11, 47.92 V, 34.13 A, 3021 rpm; = stated 3.9);
  Kt 0.1149; no-load ≈ 4320 rpm (KV × 48); 1636 W; 144 mΩ; 279 g.
- **7005 EEE — complete, KV115** (product page images read by helper agents 2026-10-17; test rows re-checked: V×I and T×ω within 0.1 %). Body Ø79 × 21.8 mm. Stator mount 4 × M4 @ PCD 32;
  rotor mount 4 × M4 @ PCD 23 (alt. 4 × M3 @ PCD 20). Wire slot (from drawing): oval slot along the
  circumference, 9.2 × 4.0 mm, centre 28.8 mm → 28.8 / 5.2 / 2.4.
  KV115: 12S; 21.2 A; **peak torque 1.842 Nm measured** (FLUXER PRO 24×7.2, 47.92 V, 21.2 A, 4235 rpm;
  = stated 1.8); Kt 0.0869; no-load ≈ 5520 rpm (KV × 48); 1016 W; 191 mΩ; 196 g (the page's
  "standard 186 g / extended 196 g" is really KV230 / KV115). KV230: 6S, ruled out.
- **8118 EEE V1.0 — complete, KV100** (product page images read by helper agents 2026-10-17; test rows re-checked: V×I and T×ω within 0.1 %). Body Ø88.6 × 41 mm. Stator mount 4 × M4 @ PCD 32
  (alt. 4 × M3 @ PCD 50 and @ PCD 30); rotor mount 4 × M4 @ PCD 23. Wire slot (from drawing): boss
  centred 36.5 mm, 10.1 mm lead ribbon running radially → 36.5 / 4 / 5.45.
  KV100: 12S; 62 A; **peak torque 5.108 Nm measured** (FLUXER PRO 30×10, 47.78 V, 62.0 A, 4193 rpm;
  = stated 5.1); Kt 0.0824; no-load ≈ 4800 rpm (KV × 48); 2962 W; 61 mΩ; **520 g** (spec image; the page
  text says 620 g — user chose 520 g, 2026-10-17).
- **5008 EEE V2.0 — complete, KV170** (product page images read by helper agents 2026-10-17; test rows re-checked: V×I and T×ω within 0.1 %). Body Ø56 × 25.9 mm (30.7 incl. shaft). Stator mount
  4 × M3 @ PCD 30 (alt. 4 × M3 @ PCD 25); rotor mount 2 × M3 @ PCD 18 (alt. 2 × M3 @ PCD 12).
  Wire slot (from drawing): sleeve centre 16.9 mm, 7.6 mm wide → 16.9 / 4 / 4.2.
  KV170: 12S; 20.6 A; **peak torque 1.088 Nm measured** (HAVOC 18×5.7, 47.60 V, 20.63 A, 6304 rpm; no
  stated max torque); Kt 0.0527; no-load ≈ 8160 rpm (KV × 48); 981 W; 195 mΩ; 130 g.
  KV240 (6–8S), KV300, KV340, KV400 (6S): ruled out.
- 5005 EEE: KV 280/350/440, all 4–6S (confirmed from the test sheets) — **ruled out by voltage**.
  88 / 90 / 92 g; highest measured torques 0.607 / 0.581 / 0.530 Nm (6S). Reference only.
- **5010 EEE V2.0 — complete, KV200** (product page images read by helper agents 2026-10-17; test rows re-checked: V×I and T×ω within 0.1 %). Body Ø56, ≈ 21 mm body (32.7 incl. shaft and prop
  adapter). Stator mount 4 × M3 @ PCD 30 (alt. 4 × M3 @ PCD 25); rotor mount 2 × M3 @ PCD 18
  (alt. 2 × M3 @ PCD 12). Wire slot (from drawing): sleeve centre 16.8 mm, 7.6 mm wide → 16.8 / 4 / 4.2.
  KV200: 6–12S; 22.3 A; **peak torque 1.086 Nm measured** (24×7.2 at 6S, 23.54 V, 22.31 A; = stated 1.09;
  best 12S row 1.021 Nm @ 21.62 A — user chose 1.086, 2026-10-17); no-load ≈ 9600 rpm (KV × 48);
  1029 W; 106 mΩ; 162.9 g. KV240, KV310, KV370: 6S, ruled out; KV110: no data on the page.

**Unidentified code entries:** `VT8020` (KV100, 48 V, 40 A, 1900 W, 713 g, 89.4 × 45.5, motor
mount PCD 51, output 6 × Ø3 @ PCD 71.5) and `U12` (KV120, 48 V, 95 A, 4560 W, 778 g,
106.8 × 47.6). `U15` is not used by any script.

## Frameless motors (datasheets received 2026-10-16)

| Motor | Type | KV | No-load @ 48 V | Rated speed | Kt (Nm/A) | Rated torque | Peak torque | Rated / peak current | Mass |
|---|---|---|---|---|---|---|---|---|---|
| RI100 | inrunner | 105 | 4368 rpm | 2825 rpm | 0.129 | 1.76 Nm | 4.95 Nm | 13.6 / 38.6 A | 500 g |
| RI80 | inrunner | 75 | 2960 rpm | 2430 rpm | 0.155 | 1.45 Nm | 4.10 Nm | 9.4 / 27.6 A | 411 g |
| RO100 | outrunner | 55 | 2550 rpm | 2000 rpm | 0.2 | 4.0 Nm | 12 Nm | 20 / 62 A | 710 g |
| RO80 | outrunner | 105 | 5040 rpm | 3600 rpm | 0.087 | 1.3 Nm | 4.0 Nm | 15 / 50 A | 352 g |
| RO60 | outrunner | 115 | 5520 rpm | 4200 rpm | 0.094 | 0.8 Nm | 2.4 Nm | 8.5 / 40 A | 248 g |

Open: ISSPG uses 525 g (RO100) and 265 g (RO80) instead of 710 / 352 g; RO100 rotor height
(33.45 or 33.2 mm), rotor hole (4 or 5 mm) and stator–rotor offset (2.75 or 3 mm). RO60's
datasheet peak torque (2.4 Nm) is below Kt × peak current (3.76 Nm); the datasheet value is used.
