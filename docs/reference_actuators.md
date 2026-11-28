# Reference: off-the-shelf actuators

**How to use this list.** These are commercial actuators, for comparison only. They are not targets
and not universal constants. COMPAct designs don't have to beat them; if a design comes out better
because the physics allows it, that's fine too. The aim is realistic designs, not better numbers.

Source: the co-design repo's actuator catalogue
(`design_builder/actuator_catalogue/actuator_catalogue.csv`, 2026-11-27), 34 actuators sorted by
peak torque. Copied here on 2026-11-27, not checked by COMPAct.

- All values are on the output side (after the gearbox), except rotor inertia J, which is on the
  motor side (reflected inertia = J × ratio²).
- dia = outer housing diameter; axial width = length along the rotation axis.
- Mass is the whole actuator: motor + gearbox + housing, plus the driver where the maker includes it.
- rated ω missing → the co-design model assumes 0.78 × no-load (the catalogue mean).
- heat k = the co-design rated-point proxy, k = 0.1765 × rated ω / rated τ (W/(N·m)²), copper loss
  ≈ k·τ². For GO-M8010-6 it gives 0.522, against 0.494 measured on the Go2 (arXiv 2611.22231). The
  catalogue has no resistance data. COMPAct's `heat_coefficient` comes from the motor's resistance
  instead (see [codesign_integration.md](codesign_integration.md)), so the two are only roughly
  comparable.
- status:
  - verified = checked against the datasheet;
  - consistent = passes the co-design side's internal checks;
  - incomplete = some values estimated. A1: ratio 9.1 from an old table, rotor J estimated, no rated
    speed. GO-M8010-6: some values estimated.

| id | maker / model | mass kg | dia mm | axial width mm | gear ratio | peak τ N·m | rated τ N·m | rated/peak | no-load ω rad/s | rated ω rad/s | V | rotor J kg·m² | peak τ/mass N·m/kg | heat k W/(N·m)² | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lkmtech-mg4005e-i10-v3 | LKMTECH MG4005E-i10-V3 | 0.183 | 53 | 36.0 | 10 | 2.5 | 1 | 0.40 | 33.5 | 26.7 | 24 | 1.4e-05 | 13.7 | 4.713 | consistent |
| cubemars-ak45-10 | CubeMars AK45-10 | 0.260 | 53 | 43.0 | 10 | 7 | 2.5 | 0.36 | 18.8 | 15.7 | 24 | 1.57e-05 | 26.9 | 1.109 | consistent |
| myactuator-x2-7 | MyActuator X2-7 | 0.250 | 44 | 63.5 | 28.17 | 7 | 2.5 | 0.36 | 18.6 | 14.9 | 24 | 1.7e-05 | 28.0 | 1.050 | consistent |
| lkmtech-mg5010e-i10-v3 | LKMTECH MG5010E-i10-V3 | 0.420 | 68 | 41.5 | 10 | 7 | 4 | 0.57 | 33.5 | 24.6 | 24 | 8.5e-05 | 16.7 | 1.086 | consistent |
| myactuator-x6-8 | MyActuator X6-8 | 0.490 | 79 | 44.5 | 8 | 8 | 4.5 | 0.56 | 40.5 | 32.5 | 48 | 1.06e-05 | 16.3 | 1.273 | consistent |
| cubemars-ak60-6-v1-1 | CubeMars AK60-6 V1.1 | 0.368 | 79 | 39.5 | 6 | 9 | 3 | 0.33 | 58.6 | 44.0 | 24 | 2.43e-05 | 24.5 | 2.588 | consistent |
| cubemars-ak60-6-v3-0-24-v | CubeMars AK60-6 V3.0 @ 24 V | 0.380 | 79 | 43.0 | 6 | 9 | 3 | 0.33 | 33.5 | 24.4 | 24 | 2.43e-05 | 23.7 | 1.436 | verified |
| cubemars-ak60-6-v3-0-48-v | CubeMars AK60-6 V3.0 @ 48 V | 0.380 | 79 | 43.0 | 6 | 9 | 3 | 0.33 | 67.0 | 51.3 | 48 | 2.43e-05 | 23.7 | 3.019 | verified |
| myactuator-x4-10-l | MyActuator X4-10-L | 0.330 | 55 | 55.5 | 12.5 | 10 | 4 | 0.40 | 33.2 | 24.9 | 24 | 2.5e-05 | 30.3 | 1.100 | consistent |
| myactuator-x4-10 | MyActuator X4-10 | 0.330 | 55 | 55.5 | 12.6 | 10 | 4 | 0.40 | 33.2 | 24.9 | 24 | 2.5e-05 | 30.3 | 1.100 | consistent |
| cubemars-ak80-6 | CubeMars AK80-6 | 0.485 | 98 | 38.5 | 6 | 12 | 6 | 0.50 | 83.8 | 63.1 | 48 | 6.07e-05 | 24.7 | 1.858 | consistent |
| cubemars-ake60-8-kv80 | CubeMars AKE60-8 KV80 | 0.260 | 69 | 25.0 | 8 | 12.5 | 5 | 0.40 | 25.1 | 18.8 | 24 | 6.47e-05 | 48.1 | 0.665 | consistent |
| lkmtech-mg6012e-i8-v2 | LKMTECH MG6012E-i8-V2 | 0.430 | 80 | 44.5 | 8 | 16 | 6 | 0.38 | 32.5 | 26.8 | 48 | 9.3e-05 | 37.2 | 0.789 | consistent |
| cubemars-ak80-9-v3-0 | CubeMars AK80-9 V3.0 | 0.490 | 98 | 38.5 | 9 | 22 | 9 | 0.41 | 59.7 | 40.8 | 48 | 1.12e-04 | 44.9 | 0.801 | consistent |
| unitree-go-m8010-6 | Unitree GO-M8010-6 | 0.530 | 96 | 42.3 | 6.33 | 23.7 | 7.9 | 0.33 | 29.9 | 23.4 | 24 | 1.12e-04 | 44.7 | 0.522 | incomplete |
| cubemars-ak80-8 | CubeMars AK80-8 | 0.570 | 98 | 43.9 | 8 | 25 | 10 | 0.40 | 37.7 | 25.4 | 48 | 1.23e-04 | 43.9 | 0.449 | consistent |
| lkmtech-mg5010e-i36-v3 | LKMTECH MG5010E-i36-V3 | 0.460 | 68 | 54.5 | 36 | 25 | 13 | 0.52 | 7.7 | 5.7 | 24 | 8.5e-05 | 54.3 | 0.077 | consistent |
| lkmtech-mg8015e-i9-v3 | LKMTECH MG8015E-i9-V3 | 0.705 | 98 | 46.5 | 9 | 28 | 14 | 0.50 | 22.6 | 18.5 | 48 | 2.57e-04 | 39.7 | 0.234 | consistent |
| cubemars-ak70-9-v3-0 | CubeMars AK70-9 V3.0 | 0.540 | 89 | 49.0 | 9 | 29.2 | 8.5 | 0.29 | 33.5 | 27.2 | 48 | 8.66e-05 | 54.1 | 0.565 | consistent |
| myactuator-x8-32 | MyActuator X8-32 | 0.550 | 96 | 41.2 | 9 | 32 | 8 | 0.25 | 29.0 | 25.6 | 24 | 1.43e-04 | 58.2 | 0.564 | consistent |
| unitree-a1-joint-motor | Unitree A1 joint motor | 0.605 | 92 | 40.0 | 9.1 | 33.5 | 11.16 | 0.33 | 21.0 | — (0.78 × no-load) | 20–40 | 1.15e-04 | 55.4 | 0.260 | incomplete |
| myactuator-x4-36 | MyActuator X4-36 | 0.360 | 55 | 61.0 | 36 | 34 | 10.5 | 0.31 | 11.6 | 8.7 | 24 | 3.0e-05 | 94.4 | 0.146 | consistent |
| lkmtech-mg8016e-i6-v2 | LKMTECH MG8016E-i6-V2 | 0.759 | 99 | 50.5 | 6 | 37 | 12 | 0.32 | 31.4 | 27.0 | 48 | 2.57e-04 | 48.7 | 0.397 | consistent |
| cubemars-ak10-9-v2-0-24-v | CubeMars AK10-9 V2.0 @ 24 V | 0.960 | 98 | 61.7 | 9 | 48 | 18 | 0.38 | 16.8 | 11.4 | 24 | 1.0e-04 | 50.0 | 0.112 | verified |
| cubemars-ak10-9-v2-0-48-v | CubeMars AK10-9 V2.0 @ 48 V | 0.960 | 98 | 61.7 | 9 | 48 | 18 | 0.38 | 33.5 | 23.9 | 48 | 1.0e-04 | 50.0 | 0.234 | verified |
| cubemars-ak10-9-v3-0 | CubeMars AK10-9 V3.0 | 0.940 | 98 | 61.7 | 9 | 53 | 18 | 0.34 | 33.5 | 24.6 | 48 | 1.0e-04 | 56.4 | 0.241 | consistent |
| myactuator-x6-60 | MyActuator X6-60 | 0.820 | 80 | 67.5 | 19.612 | 60 | 20 | 0.33 | 18.4 | 16.0 | 48 | 6.6e-05 | 73.2 | 0.141 | consistent |
| cubemars-ak60-39-v3-0 | CubeMars AK60-39 V3.0 | 0.750 | 79 | 67.0 | 39 | 72 | 24 | 0.33 | 10.3 | 7.3 | 48 | 3.05e-05 | 96.0 | 0.054 | consistent |
| cubemars-akh70-16-v1-0-kv41 | CubeMars AKH70-16 V1.0 KV41 | 0.879 | 90 | 60.5 | 16 | 78 | 26 | 0.33 | 11.0 | 9.4 | 48 | 1.17e-04 | 88.7 | 0.064 | consistent |
| myactuator-x8-120 | MyActuator X8-120 | 1.400 | 96 | 76.0 | 19.612 | 120 | 43 | 0.36 | 16.5 | 13.3 | 48 | 1.5e-04 | 85.7 | 0.055 | consistent |
| lkmtech-mg10015e-i36-v3 | LKMTECH MG10015E-i36-V3 | 2.420 | 120 | 85.2 | 36 | 200 | 108 | 0.54 | 5.8 | 4.7 | 48 | 5.25e-04 | 82.6 | 0.008 | consistent |
| cubemars-akh70-48-v1-0-kv41 | CubeMars AKH70-48 V1.0 KV41 | 1.396 | 90 | 81.5 | 48 | 222 | 74 | 0.33 | 3.7 | 2.9 | 48 | 1.17e-04 | 159.0 | 0.007 | consistent |
| myactuator-x12-320 | MyActuator X12-320 | 2.400 | 124 | 85.0 | 20 | 320 | 85 | 0.27 | 13.1 | 10.5 | 48 | 1.29e-03 | 133.3 | 0.022 | consistent |
| myactuator-x15-450 | MyActuator X15-450 | 3.500 | 166 | 69.0 | 20.25 | 450 | 145 | 0.32 | 11.3 | 10.3 | 72 | 3.16e-03 | 128.6 | 0.012 | consistent |

## Reference points from the co-design work (2026-11-27)

- Baseline robot: Unitree A1 joint motor on all 12 joints (0.605 kg, 33.5 N·m).
- Best design of the October co-design run (score 0.1522, 9.01 kg robot): ab-ad myactuator-x2-7;
  hip and knee cubemars-ake60-8-kv80 (knee behind a 1.37:1 chain stage).
- For comparison, the lightest COMPAct metal actuator with at least the A1's peak torque and
  no-load speed is U8_Lite_L @ 9.2, at 0.85 kg (map v2/v3, mass × 1). Metal masses are known to be
  too high ([metal_sspg_mass.md](metal_sspg_mass.md)).
