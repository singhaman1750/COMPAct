# Motors

All motors live in [`config_files/motors.json`](../config_files/motors.json). The code reads them with
`CommonComponents.load_motor(name)`, which builds the right motor class and applies the rating rule.
The collected datasheet values, how each number was chosen, and variants that were not chosen are in
[`config_files/motors_draft.md`](../config_files/motors_draft.md) (not read by the code).

## Rating rule

`"rating"` at the top of `motors.json` decides what the gears are sized for:
- `"peak"` (default): `peak_torque_Nm`, stress check at `no_load_speed_rpm`;
- `"rated"`: `rated_torque_Nm` and `rated_speed_rpm`. Datasheet values for the frameless motors;
  mostly estimates for the framed motors (see each `*_basis` and the rules below).

The supply is 48 V (12S) with a moteus driver (120 A), so only motor variants rated for 12S are
included, and every peak current must be at most 120 A.

## Adding a motor

Add an entry under `"motors"`; the name is what users pass to `--motor` (use the full model name,
with `_KV<n>` when the model comes in several KV variants). Copy an existing entry of the same kind:

```json
"U8_Lite": {
    "type": "framed_outrunner",
    "source": "where every value comes from",
    "notes": "estimates, alternatives, anything a reader should know",
    "electrical": {
        "kv_rpm_per_V": 100,
        "peak_torque_Nm": 2.73,
        "peak_torque_basis": "measured",
        "peak_current_A": 29.3,
        "no_load_speed_rpm": 4800,
        "no_load_speed_basis": "estimate: KV x 48 V"
    },
    "mass_kg": 0.238,
    "geometry": { "motorDia": 87.1, "motorLength": 27.05, "...": "..." }
}
```

- `type`: `framed_outrunner`, `frameless_outrunner` or `frameless_inrunner` — this decides which
  gearbox types accept the motor.
- `geometry` must contain **every** argument of the motor class (`motor_framed_outrunner`,
  `motor_frameless_outrunner`, `motor_frameless_inrunner` in `CommonComponents.py`) except the
  performance ones; the classes have no defaults, so nothing is silently guessed.
- Every motor needs `rated_current_A`, `rated_torque_Nm` and `rated_speed_rpm` in `electrical`
  (framed motors with a `*_basis` each), and a `mechanical` block:
  ```json
  "mechanical": {
      "rotor_inertia_kgm2": 0.000117,
      "rotor_inertia_basis": "estimate: 0.26 x mass x (motorDia/2)^2, +-30 %",
      "rotor_inertia_source": "where the value or the rule comes from"
  }
  ```
  The code does not use these yet (they are for the actuator map); the tests require them.
- A new **frameless inrunner** also needs its own value in the settings listed per motor
  (`{ "RI100": …, "RI80": … }`): `min_rotor_top_bearing_ID` in `incpg_dependent_params.json`
  and `inwpg_params_dependent.json`, and the six `rotor_top_bearing_*` / `rotor_bottom_bearing_*`
  sizes in `incpg_independent_params.json` and `inwpg_params_independent.json`. Without them
  those gearbox types stop with a message naming the missing setting.

### Conventions for the values

- **Peak torque**, in order of preference: measured test torque at the peak current; else measured
  Kt × peak current; else the Kv-based estimate `9.55 / KV × current`. Set `peak_torque_basis` to
  `measured`, `estimate` or `datasheet`. With several test propellers, use the highest measured
  torque among the 100 % rows that pass the checks (power = voltage × current, speed below
  KV × voltage).
- **No-load speed:** framed motors KV × 48 V (`estimate`); frameless motors the datasheet value at
  48 V.
- **Mass:** with cables.
- **Rated current:** the maker's **truly continuous** current where published (MAD: the
  "sustainable working zone" limit; T-Motor U: "Maximum Continuous Power" ÷ 48 V); otherwise
  0.31 × peak current (the median continuous/peak ratio of the motors that publish one), as an
  `estimate`. A 180 s rating is a short-term rating and is not used as rated.
- **Rated torque (framed):** Kt × rated current, with Kt = peak torque ÷ peak current.
- **Rated speed (framed):** KV × (48 V − rated current × R), R line-to-line (2 × Rph if the maker
  gives per-phase resistance). Frameless motors use the datasheet rated speed.
- **Rotor inertia:** the maker's value if published (CubeMars frameless); otherwise
  0.26 × mass × (motorDia/2)², calibrated on a measured T-Motor U8 (Lee, Pan, Rouse, IROS 2019),
  about ±30 %. Replace an estimate with a measured value when one is available.
- **Holes:** store the screw size as the diameter (M4 → 4). Use the primary pattern; put
  alternatives in `notes`.
- **Wire slot:** the measured size with **+0.4 mm on the radius** (half of `loose_clearance_3DP`);
  length centre-to-centre as measured; distance from the centre as measured.

### Check it

```bash
python -m pytest tests/test_motors.py
python actOpt.py --motor <new name> --gb_type sspg --gr 6.5
```
`tests/test_motors.py` checks that every entry loads, sets every class argument, has positive values,
a peak current within 120 A, rated values below peak / no-load, a plausible rotor inertia, and
geometry that fits (holes and wire slot inside the
motor, stator/rotor diameters in the right order). Record the source of each value in
`motors_draft.md` as well.
