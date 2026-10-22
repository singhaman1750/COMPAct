import argparse

import gearbox_runner

# How each gearbox type's result is printed: the teeth/module line as (label, index into
# opt_parameters) pairs, and an optional mass breakdown.
TEETH_LAYOUTS = {
    "single": [("Number of teeth: Sun(Ns):", 2), (", Planet(Np):", 3), (", Ring(Nr):", 4),
               (", Module(m):", 5), (", NumPlanet(n_p):", 1)],
    "compound": [("Number of teeth: Sun1(Ns1):", 2), (", Planet1(Np1):", 3), (", Planet2(Np2):", 4),
                 (", Ring(Nr):", 5), (", Module(m):", 6), (", NumPlanet(n_p):", 1)],
    "wolfrom": [("Number of teeth: Sun1(Ns1):", 2), (", Planet1(Np1):", 3), (", Ring1(R1):", 4),
                (", Planet2(Np2):", 5), (", Ring2(Nr2):", 6), (", Module1(m1):", 7), (", Module2(m2):", 8),
                (", NumPlanet(n_p):", 1)],
    "double": [("Number of teeth: Sun1(Ns1):", 3), (", Planet1(Np1):", 4), (", Ring1(R1):", 5),
               ("Sun2(Ns2):", 6), (", Planet2(Np2):", 7), (", Ring2(Nr2):", 8), (", Module1(m1):", 9),
               (", Module2(m2):", 10), (", NumPlanet1(n_p1):", 1), ("NumPlanet2(n_p2):", 2)],
}
# (label, index) rounded to 4 digits, then the total actuator mass index (3 digits).
MASS_BREAKDOWNS = {
    "icpg": ([("  Sun Gear      :", 10), ("  Planets       :", 11), ("  Ring Gear     :", 12),
              ("  Main Carrier  :", 13), ("  Sec. Carrier  :", 14), ("  Motor Casing  :", 15),
              ("total_sum_except_motor_and_baering :", 16), ("  Bearings      :", 9)], 8),
    "insspg": ([("  Sun Gear      :", 8), ("  Planets       :", 9), ("  Ring Gear     :", 10),
                ("  Main Carrier  :", 11), ("  Sec. Carrier  :", 12), ("  Motor Casing  :", 13),
                ("  Bearing Retainer :", 15), ("total_sum_except_motor_and_baering :", 14),
                ("  Bearings      :", 7)], 6),
}
MASS_BREAKDOWN_OF = {"icpg": "icpg", "insspg_type_1": "insspg", "insspg_type_2": "insspg"}


def print_result(gearbox_type, opt_parameters):
    print("-------------------------------")
    print("Optimal Parameters:")
    teeth = TEETH_LAYOUTS[gearbox_runner.GEARBOXES[gearbox_type].optimizer_kind]
    print(*[item for label, index in teeth for item in (label, opt_parameters[index])])
    print("---")
    print("Gear Ratio(GR):", opt_parameters[0], ": 1")
    breakdown = MASS_BREAKDOWN_OF.get(gearbox_type)
    if breakdown and len(opt_parameters) > 10:
        parts, total_index = MASS_BREAKDOWNS[breakdown]
        print("---")
        print("Mass Breakdown (kg):")
        for label, index in parts:
            print(label, round(opt_parameters[index], 4))
        print("---")
        print("Total Actuator (motor + gearbox):", round(opt_parameters[total_index], 3), "kg")
    print("-------------------------------")


def main(motor, gearbox_type, gear_ratio=0):
    if gearbox_type not in gearbox_runner.GEARBOXES:
        raise ValueError(f"Unknown gearbox type: {gearbox_type}")

    print("Running optimization:")
    print(f"  Motor       : {motor}")
    print(f"  Gearbox     : {gearbox_type}")
    print(f"  Gear Ratio  : {gear_ratio}")

    total_time, opt_parameters = gearbox_runner.run(gearbox_type, motor, gear_ratio)
    print("Time taken:", total_time, "sec")
    if opt_parameters is None:
        print("No feasible solution found.")
        return None
    print("Optimization Completed.")
    print_result(gearbox_type, opt_parameters)
    return opt_parameters


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="actOpt.py",
        description="Run planetary gearbox actuator optimization."
    )
    parser.add_argument("--motor", required=True, help="Motor name from config_files/motors.json, e.g. U8_Lite, RO100, RI100")
    parser.add_argument("--gb_type", required=True, choices=list(gearbox_runner.GEARBOXES),
                        help="Gearbox type")
    parser.add_argument("--gr", required=True, type=float, help="Gear ratio (must be > 2)")
    parser.add_argument("--onshape", action="store_true",
                        help="after a successful run, push the result into this gearbox's Onshape model "
                             "(set up Onshape_extension/onshape_models.json and .env first)")

    args = parser.parse_args()

    opt_parameters = main(args.motor, args.gb_type, args.gr)
    if args.onshape:
        if opt_parameters is None:
            print("Onshape: no design found, Onshape model not updated.")
        else:
            from Onshape_extension.set_values import push_to_onshape
            try:
                push_to_onshape(args.gb_type)
            except Exception as error:  # the optimisation result is already saved
                print(f"Onshape: model not updated: {error}")
