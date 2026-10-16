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
  If the test table has several propellers, use the highest-current 100 % row whose columns pass
  the checks (power = voltage × current; efficiency = thrust ÷ power; speed below KV × voltage).
- **No-load speed:** datasheet value if given; otherwise KV × operating voltage, marked as an
  estimate.
- **Wire slot:** measured size, with `loose_clearance_3DP` (0.8 mm) built into the stored values
  as +0.4 mm on the radius. The slot length is the centre-to-centre length and is stored as
  measured. The distance from centre is a position and gets no clearance.
- **Hole diameter:** stored as the screw size (M4 → 4).

Open conventions: operating voltage (manufacturer test voltage vs nominal), mass with or without
cables, which pattern to use when several are listed.

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
  no-load ≈ 4480 rpm (estimate: KV × 56 V)
- KV100: 6–12S, 36 A, 1700 W, 60 mΩ, 508 g incl. cables — matches the code's `U10`
  Test (100 % throttle, 48 V): 3.636 N·m @ 36.5 A, 1751.86 W, 9960 g (speed column reads
  11 814 rpm, which is impossible for KV100 at 48 V — likely a typo; not used)
  → **peak torque 3.59 Nm** (estimate: measured Kt 3.636 / 36.5 = 0.0996 Nm/A × 36 A peak);
  no-load ≈ 4800 rpm (estimate: KV × 48 V)
- KV170: 6–12S, 60 A, 2000 W, 21 mΩ, 511 g incl. cables
  Test A (100 % throttle, 24 V, other propeller): 3.342 N·m @ 58.9 A, 3307 rpm, 1413.6 W, 9517 g — all columns
  consistent (82 % motor efficiency). **Used.**
  → **peak torque 3.40 Nm** (estimate: measured Kt 3.342 / 58.9 = 0.0567 Nm/A × 60 A peak);
  no-load ≈ 4080 rpm (estimate: KV × 24 V)
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
- M6C12 EEE V3: KV 150/170/280/400, 72 × 33.4, motor mount D25 M3×4 + D32 M4×4, prop D12/18/22 M3×4
  — the code's `MAD_M6C12` has height 27 mm (matches M6C06 EEE, 72 × 27.4)
- M6C10 EEE: KV 150/200/250/300, 72 × 31.4, same mounts as M6C12
- M6C08 EEE: KV 130/180/260/320, 72 × 29.4, same mounts
- M6C06 EEE: KV 140/220/320, 72 × 27.4, same mounts
- M6C06 EEE V3: KV 160/320, 72.1 × 22.4, motor mount D32 M4×4, prop D12/18/20 M3×4
- 1005 EEE: KV90, 12S, 279 g, 107 × 22.5, motor D32 M4×4, prop D20 M3×4 + D23 M4×4
- 7005 EEE: KV115 (12S) / KV230 (6S), 186 g (196 g extended), 79 × 21.8, motor D32 M4×4, prop D20 M3×4 + D23 M4×4
- 8118 EEE V1.0: KV100, 620 g, 88.6 × 41, motor D30 + D50 M3×4 and D32 M4×4, prop D23 M4×4
- 5008 EEE V2.0: KV 170–400, 6/8/12S, 124–138 g, 56 × 30.7, motor D25 + D30 M3×4, prop D12/18 M3×2
- 5005 EEE: KV 280/350/440, 4–6S, 88–92 g, 56 × 27.7, same mounts as 5008
- 5010 EEE V2.0: KV 110–370, 6/8/12S, 162 g, 56 × 32.7, same mounts as 5008

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
