import sys
import numpy as np
import json
import os

# --------------------------------------------------------
# Import classes from your newly created INSSPG file
# --------------------------------------------------------
from ActuatorandGearbox_INSSPG import singleStagePlanetaryGearbox
from ActuatorandGearbox_INSSPG import motor
from ActuatorandGearbox_INSSPG import singleStagePlanetaryActuator
from ActuatorandGearbox_INSSPG import optimizationSingleStageActuator

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
motor_data          = motor_config["Motors"]
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
# Motor Initialization: RI100
#--------------------------------------------------------
motor_name = "RI100"
m_data     = motor_data[motor_name]

# Instantiate your new Inrunner Motor
MotorRI100 = motor(
    Kv                              = m_data["Kv"],
    maxContinuousCurrent            = m_data["maxContinuousCurrent"],
    ratedVoltage                    = m_data["ratedVoltage"],
    power                           = m_data["power"],
    massKG                          = m_data["massKG"],
    Stator_ID                       = m_data["Stator_ID"],
    Stator_OD                       = m_data["Stator_OD"],
    stator_height                   = m_data["stator_height"],
    Rotor_height                    = m_data["Rotor_height"],
    Rotor_OD                        = m_data["Rotor_OD"],
    Rotor_ID                        = m_data["Rotor_ID"],
    rotor_mount_hole_dia            = m_data["rotor_mount_hole_dia"],
    rotor_mount_hole_CSK_OD         = m_data["rotor_mount_hole_CSK_OD"],
    rotor_mount_hole_CSK_head_hight = m_data["rotor_mount_hole_CSK_head_hight"],
    motorName                       = motor_name
)

#--------------------------------------------------------
# Gearbox Initialization 
#--------------------------------------------------------
PlanetaryGearbox = singleStagePlanetaryGearbox(
    design_params             = sspg_design_params,
    gear_standard_parameters  = Gear_standard_parameters,
    maxGearAllowableStressMPa = PLA["maxAllowableStressMPa"], 
    densityGears              = PLA["density"], 
    densityStructure          = PLA["density"]
)

#--------------------------------------------------------
# Run Execution Function
#--------------------------------------------------------
def run(m_name, gear_ratio, gearbox_type="insspg_type_1"):
    if m_name == "RI100":
        
        # 1. Original Max Diameter Math (Unchanged)
        maxGearboxDiameter_RI100 = MotorRI100.getStatorODMM() - 5.5 - (sspg_design_params["standard_clearance_1_5mm"])*2 - (sspg_design_params["loose_clearance_3DP"])/2  

        # 2. Initialize Actuator INSIDE the run function to pass the type
        Actuator_RI100 = singleStagePlanetaryActuator(
            design_params            = sspg_design_params,
            motor                    = MotorRI100, 
            motor_driver_params      = None, 
            planetaryGearbox         = PlanetaryGearbox, 
            FOS                      = MIT_params["FOS"], 
            serviceFactor            = MIT_params["serviceFactor"], 
            maxGearboxDiameter       = maxGearboxDiameter_RI100, 
            stressAnalysisMethodName = "MIT",
            insspg_type              = gearbox_type  # <--- PASSES THE TYPE DOWN TO YOUR CLASS
        )

        # 3. Initialize Optimizer INSIDE the run function
        Optimizer_RI100 = optimizationSingleStageActuator(
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

        # 4. Run the Optimization
        return Optimizer_RI100.optimizeActuator(
            Actuator         = Actuator_RI100,
            UsePSCasVariable = 0,
            log              = 0,
            csv              = 1,
            printOptParams   = 1,
            gearRatioReq     = gear_ratio
        )
    else:
        raise ValueError(f"Unsupported motor: {m_name}")

#=============================================================
# Execution Block (If run directly)
#=============================================================
if __name__ == "__main__":
    print(f"--- Starting INSSPG Optimization for {MotorRI100.motorName} ---")
    
    # Defaults to type 1 if you run this file directly instead of actOpt.py
    totalTime_RI100, _ = run("RI100", 0, "insspg_type_1")
    
    print(f"Optimization Completed : RI100 INSSPG : Time taken: {totalTime_RI100:.2f} sec")
