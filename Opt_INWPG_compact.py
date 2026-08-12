import sys
import numpy as np
from ActuatorAndGearbox_INWPG_compact import motor
from ActuatorAndGearbox_INWPG_compact import material
from ActuatorAndGearbox_INWPG_compact import inrunnerWolfromPlanetaryGearbox
from ActuatorAndGearbox_INWPG_compact import inrunnerWolfromPlanetaryActuator
from ActuatorAndGearbox_INWPG_compact import optimizationInrunnerWolfromPlanetaryActuator
import os
import json

#--------------------------------------------------------
# Importing motor data
#--------------------------------------------------------
# Get the current directory
current_dir = os.path.dirname(__file__)

# Build the file path
config_path = os.path.join(current_dir, "config_files/config.json")
inwpg_params_path = os.path.join(current_dir, "config_files/inwpg_params_compact.json")
inwpg_motor_config_path = os.path.join(current_dir, "config_files/insspg_motor_config.json")

# Load the JSON file
with open(config_path, "r") as config_file:
    config_data = json.load(config_file)

with open(inwpg_params_path, "r") as inwpg_params_file:
    inwpg_params = json.load(inwpg_params_file)

with open(inwpg_motor_config_path, "r") as inwpg_motor_config_file:
    inwpg_motor_config = json.load(inwpg_motor_config_file)

#---------------------------------------------------
# Transferring relevant data to individual variables
#---------------------------------------------------
motor_data          = inwpg_motor_config["Motors"]
material_properties = config_data["Material_properties"]

Gear_standard_parameters = config_data["Gear_standard_parameters"]
Lewis_params             = config_data["Lewis_params"]
MIT_params               = config_data["MIT_params"]

Steel    = material_properties["Steel"]
Aluminum = material_properties["Aluminum"]
PLA      = material_properties["PLA"]

inwpg_design_params       = inwpg_params["inwpg_3DP_design_parameters"]
inwpg_optimization_params = inwpg_params["inwpg_optimization_parameters"]

motor_driver_data = config_data["Motor_drivers"]

#--------------------------------------------------------
# Motors Drivers
#--------------------------------------------------------
Motor_Driver_Moteus_params    = motor_driver_data["Moteus"]
Motor_Driver_OdrivePro_params = motor_driver_data["OdrivePro"]

#--------------------------------------------------------
# Motors
#--------------------------------------------------------

#Motor RI100
MotorRI100_Kv                   = motor_data["RI100"]["Kv"]                   # rpm/V
MotorRI100_maxContinuousCurrent = motor_data["RI100"]["maxContinuousCurrent"] # A

MotorRI100_maxTorque                  = MotorRI100_maxContinuousCurrent / (MotorRI100_Kv * 2 * np.pi / 60)
MotorRI100_power                      = motor_data["RI100"]["power"]                 # W 

MotorRI100_ratedVoltage               = motor_data["RI100"]["ratedVoltage"]   
MotorRI100_maxMotorAngVelRPM          = MotorRI100_Kv * MotorRI100_ratedVoltage # RPM 
MotorRI100_mass                       = motor_data["RI100"]["massKG"]                  # kg 

MotorRI100_rotor_OD                  = motor_data["RI100"]["Rotor_OD"]
MotorRI100_stator_ID                 = motor_data["RI100"]["Stator_ID"]
MotorRI100_rotor_height              = motor_data["RI100"]["Rotor_height"]
MotorRI100_rotor_ID                  = motor_data["RI100"]["Rotor_ID"]
MotorRI100_stator_height             = motor_data["RI100"]["stator_height"]
MotorRI100_stator_OD                 = motor_data["RI100"]["Stator_OD"]
MotorRI100_stator_hole_dia           = motor_data["RI100"]["stator_mounting_holes_dia"]
MotorRI100_stator_wire_top_height    = motor_data["RI100"]["stator_upper_step_height"]
MotorRI100_stator_mid_height         = motor_data["RI100"]["stator_mid_height"]
MotorRI100_stator_wire_bottom_height = motor_data["RI100"]["stator_bottom_step_height_"]
MotorRI100_stator_wire_OD            = motor_data["RI100"]["stator_side_step_OD"]
MotorRI100_stator_hole_num           = motor_data["RI100"]["stator_hole_num"]
MotorRI100_stator_wire_ID            = motor_data["RI100"]["stator_side_step_ID"]

# Motor-RI100
MotorRI100  = motor(rotor_OD                   = MotorRI100_rotor_OD,
                  stator_ID                    = MotorRI100_stator_ID,
                  rotor_height                 = MotorRI100_rotor_height,
                  rotor_ID                     = MotorRI100_rotor_ID,
                  stator_height                = MotorRI100_stator_height,
                  stator_OD                    = MotorRI100_stator_OD,
                  stator_hole_dia              = MotorRI100_stator_hole_dia,
                  stator_wire_top_height       = MotorRI100_stator_wire_top_height,
                  stator_mid_height            = MotorRI100_stator_mid_height,
                  stator_wire_bottom_height    = MotorRI100_stator_wire_bottom_height,
                  stator_wire_OD               = MotorRI100_stator_wire_OD,          
                  stator_hole_num              = MotorRI100_stator_hole_num,     
                  stator_wire_ID               = MotorRI100_stator_wire_ID,      
                  maxMotorAngVelRPM            = MotorRI100_maxMotorAngVelRPM,
                  maxMotorTorque               = MotorRI100_maxTorque,
                  maxMotorPower                = MotorRI100_power,
                  motorMass                    = MotorRI100_mass,
                  motorName                    = "RI100")

#-------------------------------------------------------
# Gearbox 
#-------------------------------------------------------
inrunnerWolfromPlanetaryGearboxInstance = inrunnerWolfromPlanetaryGearbox(design_parameters         = inwpg_design_params,
                                                                            gear_standard_parameters  = Gear_standard_parameters,
                                                                            densityGears              = PLA["density"],
                                                                            densityStructure          = PLA["density"],
                                                                            maxGearAllowableStressMPa = PLA["maxAllowableStressMPa"],
                                                                            densityAluminum           = Aluminum["density"])

#-----------------------------------------------------
# Actuator
#-----------------------------------------------------
maxGBDia_multFactor           = inwpg_optimization_params["MAX_GB_DIA_MULT_FACTOR"] # 1

maxGearboxDiameter_RI100      = maxGBDia_multFactor * MotorRI100.motorDiaMM       

# RI100-Actuator
Actuator_RI100 = inrunnerWolfromPlanetaryActuator(design_parameters        = inwpg_design_params,
                                                   motor                    = MotorRI100,  
                                                   motor_driver_params      = Motor_Driver_OdrivePro_params,
                                                   inrunnerWolfromPlanetaryGearbox = inrunnerWolfromPlanetaryGearboxInstance, 
                                                   FOS                      = MIT_params["FOS"], 
                                                   serviceFactor            = MIT_params["serviceFactor"], 
                                                   maxGearboxDiameter       = maxGearboxDiameter_RI100,
                                                   stressAnalysisMethodName = "MIT")

#-----------------------------------------------------
# Optimization
#-----------------------------------------------------
opt_param = config_data["Cost_gain_parameters"]

K_Mass = opt_param["K_Mass"]
K_Eff  = opt_param["K_Eff"]
K_Width  = opt_param["K_Width"]

GEAR_RATIO_MIN  = inwpg_optimization_params["GEAR_RATIO_MIN"]  # 4
GEAR_RATIO_MAX  = inwpg_optimization_params["GEAR_RATIO_MAX"]  # 45
GEAR_RATIO_STEP = inwpg_optimization_params["GEAR_RATIO_STEP"] # 1

MODULE_BIG_MIN             = inwpg_optimization_params["MODULE_BIG_MIN"]             # 0.5
MODULE_BIG_MAX             = inwpg_optimization_params["MODULE_BIG_MAX"]             # 1.2
MODULE_SMALL_MIN           = inwpg_optimization_params["MODULE_SMALL_MIN"]           # 0.5
MODULE_SMALL_MAX           = inwpg_optimization_params["MODULE_SMALL_MAX"]           # 1.2
NUM_PLANET_MIN             = inwpg_optimization_params["NUM_PLANET_MIN"]             # 3  
NUM_PLANET_MAX             = inwpg_optimization_params["NUM_PLANET_MAX"]             # 5  
NUM_TEETH_SUN_MIN          = inwpg_optimization_params["NUM_TEETH_SUN_MIN"]          # 20 
NUM_TEETH_PLANET_BIG_MIN   = inwpg_optimization_params["NUM_TEETH_PLANET_BIG_MIN"]   # 20 
NUM_TEETH_PLANET_SMALL_MIN = inwpg_optimization_params["NUM_TEETH_PLANET_SMALL_MIN"] # 20 

Optimizer_RI100     = optimizationInrunnerWolfromPlanetaryActuator(design_parameters          = inwpg_design_params         ,
                                                        gear_standard_parameters   = Gear_standard_parameters  ,
                                                        K_Mass                     = K_Mass                    ,
                                                        K_Eff                      = K_Eff                     ,
                                                        K_Width                    = K_Width                   ,
                                                        MODULE_BIG_MIN             = MODULE_BIG_MIN            ,
                                                        MODULE_BIG_MAX             = MODULE_BIG_MAX            ,
                                                        MODULE_SMALL_MIN           = MODULE_SMALL_MIN          ,
                                                        MODULE_SMALL_MAX           = MODULE_SMALL_MAX          ,
                                                        NUM_PLANET_MIN             = NUM_PLANET_MIN            ,
                                                        NUM_PLANET_MAX             = NUM_PLANET_MAX            ,
                                                        NUM_TEETH_SUN_MIN          = NUM_TEETH_SUN_MIN         ,
                                                        NUM_TEETH_PLANET_BIG_MIN   = NUM_TEETH_PLANET_BIG_MIN  ,
                                                        NUM_TEETH_PLANET_SMALL_MIN = NUM_TEETH_PLANET_SMALL_MIN,
                                                        GEAR_RATIO_MIN             = GEAR_RATIO_MIN            ,
                                                        GEAR_RATIO_MAX             = GEAR_RATIO_MAX            ,
                                                        GEAR_RATIO_STEP            = GEAR_RATIO_STEP           )

#=============================================================
# run function to select the gearbox_type
#=============================================================
def run(motor_name, gear_ratio):
    if motor_name == "RI100":
        return Optimizer_RI100.optimizeActuator(
            Actuator_RI100,
            UsePSCasVariable=0,
            log=0,
            csv=1,
            printOptParams=1,
            gearRatioReq=gear_ratio
        )

    else:
        raise ValueError(f"Unsupported motor: {motor_name}")

#-------------------------------------------------
# Optimize
#-------------------------------------------------
# totalTime_RI100 = Optimizer_RI100.optimizeActuator(Actuator_RI100, UsePSCasVariable = 0, log=0, csv=1, printOptParams=1, gearRatioReq = 0)
# print("Optimization Completed : CPG RI100 : Total Time:", totalTime_RI100)
