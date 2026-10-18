import json
import os

# --------------------------------------------------------
# Import classes from your newly created INSSPG file
# --------------------------------------------------------
from ActuatorandGearbox_INSSPG import singleStagePlanetaryGearbox
from ActuatorandGearbox_INSSPG import singleStagePlanetaryActuator
from ActuatorandGearbox_INSSPG import optimizationSingleStageActuator
from CommonComponents import load_motor

#--------------------------------------------------------
# Importing Config data
#--------------------------------------------------------
current_dir = os.path.dirname(__file__)

# Support for looking in either the root or a config_files folder
motor_config_path = os.path.join(current_dir, "insspg_motor_config.json")
if not os.path.exists(motor_config_path):
    motor_config_path = os.path.join(current_dir, "config_files", "insspg_motor_config.json")

sspg_params_path = os.path.join(current_dir, "insspg_params.json")
if not os.path.exists(sspg_params_path):
    sspg_params_path = os.path.join(current_dir, "config_files", "insspg_params.json")

# Load the JSON files
with open(motor_config_path, "r") as motor_file:
    motor_config = json.load(motor_file)

with open(sspg_params_path, "r") as sspg_params_file:
    sspg_params = json.load(sspg_params_file)

#---------------------------------------------------
# Transferring relevant data to individual variables
#---------------------------------------------------
material_properties = motor_config["Material_properties"]

Gear_standard_parameters = motor_config["Gear_standard_parameters"]
Lewis_params             = motor_config["Lewis_params"]
MIT_params               = motor_config["MIT_params"]
cost_gains               = motor_config["Cost_gain_parameters"]

Steel    = material_properties["Steel"]
Aluminum = material_properties["Aluminum"]
PLA      = material_properties["PLA"]

sspg_design_params_base  = sspg_params["sspg_design_parameters"]
sspg_design_params_3dp   = sspg_params["sspg_3DP_design_parameters"]
sspg_optimization_params = sspg_params["sspg_optimization_parameters"]

# Merge design params safely so Actuator has access to everything
sspg_design_params = {**sspg_design_params_base, **sspg_design_params_3dp}

#--------------------------------------------------------
# Run Execution Function
#--------------------------------------------------------
def run(motor_name, gear_ratio, gearbox_type="insspg_type_1"):
    motor = load_motor(motor_name, motor_type="frameless_inrunner")
    maxGearboxDiameter = motor.getStatorODMM() - 5.5 - (sspg_design_params["standard_clearance_1_5mm"])*2 - (sspg_design_params["loose_clearance_3DP"])/2
    planetaryGearbox = singleStagePlanetaryGearbox(
        design_params             = sspg_design_params,
        gear_standard_parameters  = Gear_standard_parameters,
        maxGearAllowableStressMPa = PLA["maxAllowableStressMPa"],
        densityGears              = PLA["density"],
        densityStructure          = PLA["density"]
    )
    actuator = singleStagePlanetaryActuator(
        design_params            = sspg_design_params,
        motor                    = motor,
        motor_driver_params      = None,
        planetaryGearbox         = planetaryGearbox,
        FOS                      = MIT_params["FOS"],
        serviceFactor            = MIT_params["serviceFactor"],
        maxGearboxDiameter       = maxGearboxDiameter,
        stressAnalysisMethodName = "MIT",
        insspg_type              = gearbox_type
    )
    optimizer = optimizationSingleStageActuator(
        design_params             = sspg_design_params,
        gear_standard_paramaeters = Gear_standard_parameters,
        K_Mass                    = cost_gains["K_Mass"],
        K_Eff                     = cost_gains["K_Eff"],
        K_Width                   = cost_gains["K_Width"],
        MODULE_MIN                = sspg_optimization_params["MODULE_MIN"],
        MODULE_MAX                = sspg_optimization_params["MODULE_MAX"],
        NUM_PLANET_MIN            = sspg_optimization_params["NUM_PLANET_MIN"],
        NUM_PLANET_MAX            = sspg_optimization_params["NUM_PLANET_MAX"],
        NUM_TEETH_SUN_MIN         = sspg_optimization_params["NUM_TEETH_SUN_MIN"],
        NUM_TEETH_PLANET_MIN      = sspg_optimization_params["NUM_TEETH_PLANET_MIN"],
        GEAR_RATIO_MIN            = sspg_optimization_params["GEAR_RATIO_MIN"],
        GEAR_RATIO_MAX            = sspg_optimization_params["GEAR_RATIO_MAX"],
        GEAR_RATIO_STEP           = sspg_optimization_params["GEAR_RATIO_STEP"]
    )
    return optimizer.optimizeActuator(
        Actuator         = actuator,
        UsePSCasVariable = 0,
        log              = 0,
        csv              = 1,
        printOptParams   = 1,
        gearRatioReq     = gear_ratio
    )

#=============================================================
# Execution Block (If run directly)
#=============================================================
if __name__ == "__main__":
    print("--- Starting INSSPG Optimization for RI100 ---")

    # Defaults to type 1 if you run this file directly instead of actOpt.py
    totalTime_RI100, _ = run("RI100", 0, "insspg_type_1")

    print(f"Optimization Completed : RI100 INSSPG : Time taken: {totalTime_RI100:.2f} sec")
