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

**Status:** open.
