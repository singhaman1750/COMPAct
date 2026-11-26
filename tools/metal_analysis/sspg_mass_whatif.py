"""Metal SSPG: mass breakdown of the optimised design and what-if changes to it.

    python tools/metal_analysis/sspg_mass_whatif.py MOTOR RATIO      e.g. U8_Lite 6.5

Runs the SSPG optimiser (metal and 3dp) in a temporary folder, prints the metal mass by part,
then rebuilds the same gear set with each candidate change and prints the new mass. Changes no
files. Change #1 (only the ring steel, the rest of the gearbox casing aluminium) is in the code
since 2026-10-30, so it is part of the base. Background and results: docs/metal_sspg_mass.md.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import gearbox_runner  # noqa: E402
from tools.actuator_map.case import run_case  # noqa: E402

motor, ratio = sys.argv[1], float(sys.argv[2])
r = run_case("sspg", motor, ratio, "metal")
gr, n, Ns, Np, Nr, module = r["opt_parameters"]
print(f"{motor} metal, requested {ratio}: GR {gr:.3f}, Ns {Ns} Np {Np} Nr {Nr} module {module} planets {n}")
r3 = run_case("sspg", motor, ratio, "3dp")
print(f"(3dp optimum: GR {r3['opt_parameters'][0]:.3f}, Ns/Np/Nr {r3['opt_parameters'][2:5]}, "
      f"module {r3['opt_parameters'][5]}, mass {r3['mass_kg']*1000:.0f} g)")


def build(ch=None, ring=None, mat="metal"):
    a, _ = gearbox_runner.build("sspg", motor, mat)
    g = a.planetaryGearbox
    for k, v in (ch or {}).items():
        a.design_params[k] = v
    if ring is not None:
        a.ringRadialWidthMM = ring
    g.setNs(Ns), g.setNp(Np), g.setNr(Nr), g.setModule(module), g.setNumPlanet(n)
    a.setVariables(), a.updateFacewidth(), a.setVariables()
    m = a.getMassKG_3DP()
    return a, m


a, base = build()
g = a.planetaryGearbox
before_1 = base + a.gearbox_housing_mass * (g.densityGears / g.densityStructure - 1)   # whole casing steel
print(f"\nbase mass {base*1000:.0f} g, width {a.actuator_width:.1f} mm "
      f"(this gear set with the whole casing steel, before change #1: {before_1*1000:.0f} g)")
print(f"  motor {a.motorMassKG*1000:.0f}, gearbox casing {a.gearbox_casing_mass*1000:.0f} (steel ring "
      f"{a.ring_mass*1000:.0f} + aluminium housing {a.gearbox_housing_mass*1000:.0f}), motor case "
      f"{a.Motor_case_mass*1000:.0f}, planets {a.planet_mass*n*1000:.0f} ({n}x), output bearing {a.bearing_mass*1000:.0f}, "
      f"carrier {a.carrier_mass*1000:.0f}, sun {a.sun_mass*1000:.0f}, sec carrier {a.sec_carrier_mass*1000:.0f}, "
      f"retainer {a.bearing_retainer_mass*1000:.0f}, small bearings {(a.planet_bearing_combined_mass + a.sun_shaft_bearing_mass)*1000:.0f}")
print(f"  fw_p {g.fwPlanetMM:.2f} (stress width {g.fwSunMM:.2f}, bearing minimum {2*a.planet_bearing_width + a.planet_bearing_gap:.1f}), "
      f"ring_OD {a.ring_OD:.1f} vs motor_OD {a.motor_OD}, motor case OD {a.motor_case_OD_base:.1f}, "
      f"bearing {a.bearing_ID}/{a.bearing_OD}x{a.bearing_height}, mount wall {a.bearing_mount_thickness:.1f}, "
      f"branch {'bearing wider' if a.bearing_mount_thickness == a.output_mounting_hole_dia * 2 else 'ring wider'}")

PB = {"planet_bearing_width": 1.75, "planet_bearing_gap": 0.0}
cases = [
    ("2 one planet bearing (min 3.5 mm)", PB, None),
    ("3 motor-case gap 5->2", {"clearance_motor_and_case_min": 2}, None),
    ("4 sec carrier 5->3, hub 4->3, retainer 2->1.5",
     {"sec_carrier_thickness": 3, "sun_coupler_hub_thickness": 3, "bearing_retainer_thickness": 1.5}, None),
    ("5 walls: case 2.5->1.5, base 4->2.5, mount 4->3",
     {"Motor_case_thickness": 1.5, "base_plate_thickness": 2.5, "case_mounting_surface_height": 3}, None),
    ("6 clearances 1.5->0.5",
     {"clearance_planet": 0.5, "standard_clearance_1_5mm": 0.5, "clearance_sun_coupler_sec_carrier": 0.5}, None),
    ("7 bearing-mount wall 2->1.5 bolt dia", {"bearing_mount_wall_bolt_dia_multiple": 1.5}, None),
    ("8 planet shaft 8->4", {"planet_shaft_dia": 4}, None),
    ("9 ring wall 5->3", {}, 3.0),
]
print()
for name, ch, ring in cases:
    a2, m = build(ch, ring)
    print(f"  {name:48s} {m*1000:6.0f} g ({(m-base)*1000:+5.0f})  fw_p {a2.planetaryGearbox.fwPlanetMM:5.2f}")
ALL = dict(PB, Motor_case_thickness=1.5, base_plate_thickness=2.5, case_mounting_surface_height=3, sec_carrier_thickness=3,
           sun_coupler_hub_thickness=3, bearing_retainer_thickness=1.5, clearance_planet=0.5, standard_clearance_1_5mm=0.5,
           clearance_sun_coupler_sec_carrier=0.5, clearance_motor_and_case_min=2, bearing_mount_wall_bolt_dia_multiple=1.5)
print()
for name, ch in (("2", PB), ("2-8", ALL)):
    a2, m = build(ch)
    print(f"  with {name:6s} {m*1000:6.0f} g ({(m-base)*1000:+5.0f}), width {a2.actuator_width:.1f} mm")
