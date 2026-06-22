import sys

GEARBOX_DISPATCH = {
    "sspg": "Opt_singleStagePlanetaryGBOptimization",
    "dspg": "Opt_doubleStagePlanetaryGBOptimization",
    "cpg": "Opt_compoundPlanetaryGBOptimization",
    "icpg": "Opt_internalcompoundPlanetryGBOptimization",
    "wpg": "Opt_wolfromPlanetaryGBOptimization",
}

def main(motor, gearbox_type, gear_ratio=0):
    if gearbox_type not in GEARBOX_DISPATCH:
        raise ValueError(f"Unknown gearbox type: {gearbox_type}")

    module_name = GEARBOX_DISPATCH[gearbox_type]
    module = __import__(module_name)

    print(f"Running optimization:")
    print(f"  Motor       : {motor}")
    print(f"  Gearbox     : {gearbox_type}")
    print(f"  Gear Ratio  : {gear_ratio}")

    total_time, opt_parameters = module.run(motor, gear_ratio)
    print("Time taken:", total_time, "sec")
    if opt_parameters is None:
        print("No feasible solution found.")
        return
    else:
        print("Optimization Completed.")
    if(gearbox_type=="sspg"):
        print("-------------------------------")
        print("Optimal Parameters:")
        print("Number of teeth: Sun(Ns):", opt_parameters[2], ", Planet(Np):", opt_parameters[3], ", Ring(Nr):", opt_parameters[4],
              ", Module(m):", opt_parameters[5], ", NumPlanet(n_p):", opt_parameters[1])
        print("---")
        print("Gear Ratio(GR):", opt_parameters[0],": 1")
        print("-------------------------------")
    elif(gearbox_type=="cpg"):
        print("-------------------------------")
        print("Optimal Parameters:")
        print("Number of teeth: Sun1(Ns1):", opt_parameters[2], ", Planet1(Np1):", opt_parameters[3], ", Planet2(Np2):", opt_parameters[4], ", Ring(Nr):", opt_parameters[5],
              ", Module(m):", opt_parameters[6], ", NumPlanet(n_p):", opt_parameters[1])
        print("---")
        print("Gear Ratio(GR):", opt_parameters[0],": 1")
        print("-------------------------------")
    elif(gearbox_type=="icpg"):
        print("-------------------------------")
        print("Optimal Parameters:")
        print("Number of teeth: Sun1(Ns1):", opt_parameters[2], ", Planet1(Np1):", opt_parameters[3], ", Planet2(Np2):", opt_parameters[4], ", Ring(Nr):", opt_parameters[5],
              ", Module(m):", opt_parameters[6], ", NumPlanet(n_p):", opt_parameters[1])
        print("---")
        print("Gear Ratio(GR):", opt_parameters[0],": 1")
# --- NEW MASS BREAKDOWN BLOCK ---
        if len(opt_parameters) > 10:
            print("---")
            print("Mass Breakdown (kg):")
            print("  Sun Gear      :", round(opt_parameters[10], 4))
            print("  Planets       :", round(opt_parameters[11], 4))
            print("  Ring Gear     :", round(opt_parameters[12], 4))
            print("  Main Carrier  :", round(opt_parameters[13], 4))
            print("  Sec. Carrier  :", round(opt_parameters[14], 4))
            print("  Motor Casing  :", round(opt_parameters[15], 4))
            print("total_sum_except_motor_and_baering :" ,round(opt_parameters[16],4))
            print("  Bearings      :", round(opt_parameters[9], 4))
            print("---")
            print("Total Gearbox   :", round(opt_parameters[8], 3), "kg")
        print("-------------------------------")
    elif(gearbox_type=="wpg"):
        print("-------------------------------")
        print("Optimal Parameters:")
        print("Number of teeth: Sun1(Ns1):", opt_parameters[2], ", Planet1(Np1):", opt_parameters[3], ", Ring1(R1):", opt_parameters[4], ", Planet2(Np2):", opt_parameters[5], ", Ring2(Nr2):", opt_parameters[6],
              ", Module1(m1):", opt_parameters[7], ", Module2(m2):", opt_parameters[8], ", NumPlanet(n_p):", opt_parameters[1])
        print("---")
        print("Gear Ratio(GR):", opt_parameters[0],": 1")
        print("-------------------------------")
    elif(gearbox_type=="dspg"):
        print("-------------------------------")
        print("Optimal Parameters:")
        print("Number of teeth: Sun1(Ns1):", opt_parameters[3], ", Planet1(Np1):", opt_parameters[4], ", Ring1(R1):", opt_parameters[5], "Sun2(Ns2):", opt_parameters[6], ", Planet2(Np2):", opt_parameters[7], ", Ring2(Nr2):", opt_parameters[8],
              ", Module1(m1):", opt_parameters[9], ", Module2(m2):", opt_parameters[10], ", NumPlanet1(n_p1):", opt_parameters[1], "NumPlanet2(n_p2):", opt_parameters[2])
        print("---")
        print("Gear Ratio(GR):", opt_parameters[0],": 1")
        print("-------------------------------")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage:")
        print("  python actOpt.py <motor> <gearbox_type> <gear_ratio>")
        sys.exit(1)

    motor = sys.argv[1]
    gearbox_type = sys.argv[2]
    gear_ratio = float(sys.argv[3])

    main(motor, gearbox_type, gear_ratio)
