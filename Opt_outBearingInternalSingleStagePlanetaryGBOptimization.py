import sys
import numpy as np
from ISSPG_compact_gen_eq import internalsingleStagePlanetaryGearbox
from ISSPG_compact_gen_eq import motor
from ISSPG_compact_gen_eq import internalsingleStagePlanetaryActuator
from ISSPG_compact_gen_eq import optimizationInternalSingleStageActuator
import json
import os

#--------------------------------------------------------
# Importing Config data
#--------------------------------------------------------
# Get the current directory
current_dir = os.path.dirname(__file__)

# Build the file path
config_path      = os.path.join(current_dir, "config_files/config.json")
isspg_params_path = os.path.join(current_dir, "config_files/isspg_params.json")

# Load the JSON file
with open(config_path, "r") as config_file:
    config_data = json.load(config_file)

with open(isspg_params_path, "r") as isspg_params_file:
    isspg_params = json.load(isspg_params_file)

#---------------------------------------------------
# Transferring relevant data to individual variables
#---------------------------------------------------
material_properties = config_data["Material_properties"]

Gear_standard_parameters = config_data["Gear_standard_parameters"]
Lewis_params             = config_data["Lewis_params"]
MIT_params               = config_data["MIT_params"]

Steel    = material_properties["Steel"]
Aluminum = material_properties["Aluminum"]
PLA      = material_properties["PLA"]

isspg_design_params       = isspg_params["isspg_3DP_design_parameters"]
isspg_optimization_params = isspg_params["isspg_optimization_parameters"]

motor_driver_data = config_data["Motor_drivers"]

#--------------------------------------------------------
# Motors Drivers
#--------------------------------------------------------
Motor_Driver_Moteus_params    = motor_driver_data["Moteus"]
Motor_Driver_OdrivePro_params = motor_driver_data["OdrivePro"]

#--------------------------------------------------------
# Motors
#--------------------------------------------------------
MotorRO100 = motor(
                  motor_OD                     = 113.5,
                  stator_ID                    = 74,
                  motor_rotor_base_thickness   = 3.2,
                  motor_rotor_base_ID          = 60,
                  rotor_height                 = 33.2,
                  rotor_ID                     = 101.8,
                  motor_stator_extrusion_depth = 2,
                  motor_stator_extrusion_dia   = 88,
                  stator_height                = 31.5,
                  stator_OD                    = 100,
                  stator_top_rotor_top_offset  = 3,
                  stator_hole_dia              = 3,
                  stator_hole_PCD              = 82.5,
                  motor_rotor_hole_num         = 6,
                  motor_rotor_hole_dia         = 5,
                  motor_rotor_hole_PCD         = 74,
                  motor_height                 = 36.2,
                  maxMotorAngVelRPM            = 2550,  # RPM
                  maxMotorTorque               = 4,     # Nm
                  maxMotorPower                = 4 * 2550 * 2*np.pi/60,  # W
                  motorMass                    = 0.525, # KG
                  motorName                    = "RO100")

MotorRO80 = motor(
                 motor_OD                     = 92.6,
                 stator_ID                    = 55,
                 motor_rotor_base_thickness   = 2.6,
                 motor_rotor_base_ID          = 51,
                 rotor_height                 = 21.6,
                 rotor_ID                     = 82.6,
                 motor_stator_extrusion_depth = 1.5,
                 motor_stator_extrusion_dia   = 68,
                 stator_height                = 22,
                 stator_OD                    = 81,
                 stator_top_rotor_top_offset  = 4.8,
                 stator_hole_dia              = 3,
                 stator_hole_PCD              = 63,
                 motor_rotor_hole_num         = 6,
                 motor_rotor_hole_dia         = 4,
                 motor_rotor_hole_PCD         = 62,
                 motor_height                 = 26.4,
                 maxMotorAngVelRPM            = 5040,  # RPM
                 maxMotorTorque               = 1.3,   # Nm
                 maxMotorPower                = 1.3 * 5040 * 2*np.pi/60,  # W
                 motorMass                    = 0.265, # KG
                 motorName                    = "RO80")

MotorRO60 = motor(
                 motor_OD                     = 73.8,
                 stator_ID                    = 32,
                 motor_rotor_base_thickness   = 2,
                 motor_rotor_base_ID          = 37,
                 rotor_height                 = 19,
                 rotor_ID                     = 63.1,
                 motor_stator_extrusion_depth = 1.8,
                 motor_stator_extrusion_dia   = 47.6,
                 stator_height                = 19.5,
                 stator_OD                    = 61.5,
                 stator_top_rotor_top_offset  = 4,
                 stator_hole_dia              = 3,
                 stator_hole_PCD              = 40,
                 motor_rotor_hole_num         = 6,
                 motor_rotor_hole_dia         = 3,
                 motor_rotor_hole_PCD         = 46,
                 motor_height                 = 23,
                 maxMotorAngVelRPM            = 5520,  # RPM
                 maxMotorTorque               = 0.8,   # Nm
                 maxMotorPower                = 0.8 * 5520 * 2*np.pi/60,  # W
                 motorMass                    = 0.248, # KG
                 motorName                    = "RO60")

#--------------------------------------------------------
# Gearboxes  
#--------------------------------------------------------
PlanetaryGearbox = internalsingleStagePlanetaryGearbox(design_params             = isspg_design_params,
                                                       gear_standard_parameters  = Gear_standard_parameters,
                                                       maxGearAllowableStressMPa = PLA["maxAllowableStressMPa"], # MPa
                                                       densityGears              = PLA["density"], # kg/m^3
                                                       densityStructure          = PLA["density"]) # kg/m^3

#--------------------------------------------------------
# Actuators
#--------------------------------------------------------

# RO100-Actuator
Actuator_RO100    = internalsingleStagePlanetaryActuator(design_params           = isspg_design_params,
                                                        motor                    = MotorRO100,
                                                        motor_driver_params      = Motor_Driver_OdrivePro_params,
                                                        planetaryGearbox         = PlanetaryGearbox,
                                                        FOS                      = 1.2,
                                                        serviceFactor            = 1.5,
                                                        stressAnalysisMethodName = "MIT") # Lewis or AGMA

# RO80-Actuator
Actuator_RO80    = internalsingleStagePlanetaryActuator(design_params            = isspg_design_params,
                                                        motor                    = MotorRO80,
                                                        motor_driver_params      = Motor_Driver_OdrivePro_params,
                                                        planetaryGearbox         = PlanetaryGearbox,
                                                        FOS                      = 1.2,
                                                        serviceFactor            = 1.5,
                                                        stressAnalysisMethodName = "MIT") # Lewis or AGMA

# RO60-Actuator
Actuator_RO60    = internalsingleStagePlanetaryActuator(design_params            = isspg_design_params,
                                                        motor                    = MotorRO60,
                                                        motor_driver_params      = Motor_Driver_OdrivePro_params,
                                                        planetaryGearbox         = PlanetaryGearbox,
                                                        FOS                      = 1.2,
                                                        serviceFactor            = 1.5,
                                                        stressAnalysisMethodName = "MIT") # Lewis or AGMA

#--------------------------------------------------------
# Optimization
#--------------------------------------------------------
cost_gains = config_data["Cost_gain_parameters"]

K_Mass = cost_gains["K_Mass"]
K_Eff  = cost_gains["K_Eff"]
K_Width = cost_gains["K_Width"]

GEAR_RATIO_MIN       = isspg_optimization_params["GEAR_RATIO_MIN"]       # 4   
GEAR_RATIO_MAX       = isspg_optimization_params["GEAR_RATIO_MAX"]       # 15 
GEAR_RATIO_STEP      = isspg_optimization_params["GEAR_RATIO_STEP"]      # 1  

MODULE_MIN           = isspg_optimization_params["MODULE_MIN"]           # 0.5 
MODULE_MAX           = isspg_optimization_params["MODULE_MAX"]           # 1.2 
NUM_PLANET_MIN       = isspg_optimization_params["NUM_PLANET_MIN"]       # 3   
NUM_PLANET_MAX       = isspg_optimization_params["NUM_PLANET_MAX"]       # 7   
NUM_TEETH_SUN_MIN    = isspg_optimization_params["NUM_TEETH_SUN_MIN"]    # 20  
NUM_TEETH_PLANET_MIN = isspg_optimization_params["NUM_TEETH_PLANET_MIN"] # 20

Optimizer_RO100   = optimizationInternalSingleStageActuator(design_params     = isspg_design_params  ,
                                                    gear_standard_paramaeters = Gear_standard_parameters,
                                                    K_Mass                    = K_Mass              ,
                                                    K_Eff                     = K_Eff               ,
                                                    K_Width                   = K_Width             ,
                                                    MODULE_MIN                = MODULE_MIN          ,
                                                    MODULE_MAX                = MODULE_MAX          ,
                                                    NUM_PLANET_MIN            = NUM_PLANET_MIN      ,
                                                    NUM_PLANET_MAX            = NUM_PLANET_MAX      ,
                                                    NUM_TEETH_SUN_MIN         = NUM_TEETH_SUN_MIN   ,
                                                    NUM_TEETH_PLANET_MIN      = NUM_TEETH_PLANET_MIN,
                                                    GEAR_RATIO_MIN            = GEAR_RATIO_MIN      ,
                                                    GEAR_RATIO_MAX            = GEAR_RATIO_MAX      ,
                                                    GEAR_RATIO_STEP           = GEAR_RATIO_STEP     )

Optimizer_RO80    = optimizationInternalSingleStageActuator(design_params     = isspg_design_params  ,
                                                    gear_standard_paramaeters = Gear_standard_parameters,
                                                    K_Mass                    = K_Mass              ,
                                                    K_Eff                     = K_Eff               ,
                                                    K_Width                   = K_Width             ,
                                                    MODULE_MIN                = MODULE_MIN          ,
                                                    MODULE_MAX                = MODULE_MAX          ,
                                                    NUM_PLANET_MIN            = NUM_PLANET_MIN      ,
                                                    NUM_PLANET_MAX            = NUM_PLANET_MAX      ,
                                                    NUM_TEETH_SUN_MIN         = NUM_TEETH_SUN_MIN   ,
                                                    NUM_TEETH_PLANET_MIN      = NUM_TEETH_PLANET_MIN,
                                                    GEAR_RATIO_MIN            = GEAR_RATIO_MIN      ,
                                                    GEAR_RATIO_MAX            = GEAR_RATIO_MAX      ,
                                                    GEAR_RATIO_STEP           = GEAR_RATIO_STEP     )

Optimizer_RO60    = optimizationInternalSingleStageActuator(design_params     = isspg_design_params  ,
                                                    gear_standard_paramaeters = Gear_standard_parameters,
                                                    K_Mass                    = K_Mass              ,
                                                    K_Eff                     = K_Eff               ,
                                                    K_Width                   = K_Width             ,
                                                    MODULE_MIN                = MODULE_MIN          ,
                                                    MODULE_MAX                = MODULE_MAX          ,
                                                    NUM_PLANET_MIN            = NUM_PLANET_MIN      ,
                                                    NUM_PLANET_MAX            = NUM_PLANET_MAX      ,
                                                    NUM_TEETH_SUN_MIN         = NUM_TEETH_SUN_MIN   ,
                                                    NUM_TEETH_PLANET_MIN      = NUM_TEETH_PLANET_MIN,
                                                    GEAR_RATIO_MIN            = GEAR_RATIO_MIN      ,
                                                    GEAR_RATIO_MAX            = GEAR_RATIO_MAX      ,
                                                    GEAR_RATIO_STEP           = GEAR_RATIO_STEP     )

#=============================================================
# run function to select the gearbox_type
#=============================================================
def run(motor_name, gear_ratio):

    if motor_name == "RO100":
        return Optimizer_RO100.optimizeActuator(
            Actuator_RO100,
            UsePSCasVariable=0,
            log=0,
            csv=1,
            printOptParams=1,
            gearRatioReq=gear_ratio
        )

    elif motor_name == "RO80":
        return Optimizer_RO80.optimizeActuator(
            Actuator_RO80,
            UsePSCasVariable=0,
            log=0,
            csv=1,
            printOptParams=1,
            gearRatioReq=gear_ratio
        )

    elif motor_name == "RO60":
        return Optimizer_RO60.optimizeActuator(
            Actuator_RO60,
            UsePSCasVariable=0,
            log=0,
            csv=1,
            printOptParams=1,
            gearRatioReq=gear_ratio
        )    

    else:
        raise ValueError(f"Unsupported motor: {motor_name}")
