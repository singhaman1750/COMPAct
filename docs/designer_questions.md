# Questions for the designers

Numbers and choices in the code whose meaning the code doesn't explain. They are kept as they are until a
designer answers; the code has a `TODO` comment pointing here. When a question is answered, write the
answer below it, then move the number to the config (or fix it) and mark the question **Answered**.

## Q1. INSSPG type 1: the `1.5 × standard_clearance_1_5mm` in the sun length

`ActuatorandGearbox_INSSPG.py`, `setVariables`, type-1 branch:

```python
self.fw_s_used = (- self.sun_coupler_hub_thickness
                  + self.standard_clearance_1_5mm
                  + self.standard_clearance_1_5mm*1.5   # <- this term (2.25 mm)
                  + self.rotor_support_bearing_height
                  + self.standard_clearance_1_5mm
                  + self.sec_carrier_thickness
                  + self.clearance_planet
                  + self.fw_p)
```

- What does the 2.25 mm step stand for, for example a gap, a shoulder or a chamfer?
- Should it scale with `standard_clearance_1_5mm`, or is it a fixed length?

**Status:** open.

## Q2. INSSPG type 2: the `- 2` mm in the sun length

`ActuatorandGearbox_INSSPG.py`, `setVariables`, type-2 branch:

```python
self.fw_s_used = (self.Rotor_height
                - 2                                      # <- this term
                - self.sun_coupler_hub_thickness
                + self.loose_clearance_3DP
                + self.sec_carrier_thickness
                + self.fw_p
                + self.standard_clearance_1_5mm)
```

- What is the 2 mm taken off the rotor height, for example the part of the rotor the sun doesn't reach, or a step?
- Is it the same for every inrunner motor, or does it depend on the rotor?

**Status:** open.

## Q3. INDSPG: the stage-1 output bearing is a fixed inch thin bearing

`config_files/indspg_params.json`: `a1_bearing_ID` 38.1, `a1_bearing_OD` 47.625, `a1_bearing_height`
4.763 mm, `a1_bearing_massKg` 0.0227 (1½″ × 1⅞″ × 3/16″). It is the same for every design, while the mass code
sizes the stage-1 carrier with a catalogue bearing (ISSUES bug 22).

- Was this thin-section bearing chosen on purpose, for example to save height inside the stator?
- Should it stay fixed for every design, or be picked per design from the bearing table, with this bearing added to the table?
- The stage-1 sun's bottom bearing on RI100 is also an inch thin-section bearing from the config
  (`a1_sun_bottom_casing_bearing_*`: 44.45 × 53.975 × 4.763 mm, 1¾″ × 2⅛″ × 3/16″), while RI80 takes the
  catalogue bearing for its rotor's bore (`a1_sun_bottom_casing_bearing_source` in `indspg_params.json`).
  Was it chosen for the same reason?

**Status:** open.

## Q4. ISSPG compact and INSSPG: bearings picked one size too big (ISSUES bug 5)

Three places know the largest bearing their space can hold, but `bearings_discrete(odRequiredMM=...)` returns
the smallest bearing whose OD is at least that value, so each gets a bearing 0.5–3.5 mm larger than its space:

| Gearbox / motor | Bearing | Max OD | Picked today | Largest that fits |
|---|---|---|---|---|
| ISSPG compact RO100 | sun-2 (`motor_rotor_base_ID`) | 60 | 50×62×6 | 45×58×7 |
| ISSPG compact RO80 | sun-2 | 51 | 40×52×7 | 40×50×6 |
| INSSPG RI100 | rotor support (`Rotor_ID - 4`) | 41 | 30×42×7 | 25×37×7 |
| INSSPG RI100 | rotor upper support (`Stator_ID - 1.5 × 5`) | 49.5 | 40×50×6 | 35×47×7 |
| INSSPG RI80 | rotor support | 36.5 | 25×37×7 | 20×32×7 |
| INSSPG RI80 | rotor upper support | 43.5 | 35×47×7 | 30×42×7 |

- In the Onshape models, does the picked bearing really overlap its space, or is the limit a different dimension?
- Were the `- 4` and `- 1.5 × 5` clearances meant to absorb the larger bearing?
- If the bearing must fit: is the largest bearing that fits the right choice (it changes the CAD sizes and masses)?

To be gone through together with the designers, not fixed alone.

**Status:** open.

## Q5. ICPG: the motor-height floor on the sun length

`ActuatorandGearbox_ICPG.py`, `setVariables`: when the output bearing doesn't fit inside the stator bore with
`stator_bearing_clearance_multiple` (2) × 1.5 mm around it, the sun length `fw_s_used` is at least the motor height,
so the bearing sits past the motor:

```python
fw_s_used_floor = self.motor_height
floor_applies   = (self.stator_ID - self.bearing_OD) / 2 < self.standard_clearance_1_5mm * self.stator_bearing_clearance_multiple
```

The floor was first `stator_height + rotor_bottom_thickness` (commit `1075730`, 2026-06-15) and changed to
`motor_height` a week later (`2c1fc51`). In every design checked the output bearing is wider than the stator
bore (RO100: bore 74 mm, bearings 72–110 mm OD), so the condition always holds and the rule is in effect
"the sun is at least the motor height".

- Which axial position should the floor be: the motor height or the stator height plus the rotor bottom?
- Is 3 mm of radial room the right test for "the bearing fits inside the stator"?

**Status:** open.
