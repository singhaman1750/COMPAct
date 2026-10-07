import sys
import numpy as np
from ActuatorAndGearbox_INCPG_independent import motor
from ActuatorAndGearbox_INCPG_independent import material
from ActuatorAndGearbox_INCPG_independent import inrunnerCompoundPlanetaryGearbox
from ActuatorAndGearbox_INCPG_independent import inrunnerCompoundPlanetaryActuator
from ActuatorAndGearbox_INCPG_independent import optimizationInrunnerCompoundPlanetaryActuator
import os
import json

#--------------------------------------------------------
# Importing motor data
#--------------------------------------------------------
# Get the current directory
current_dir = os.path.dirname(__file__)

# Build the file path
config_path = os.path.join(current_dir, "config_files/config.json")
incpg_params_path = os.path.join(current_dir, "config_files/incpg_independent_params.json")
incpg_motor_config_path = os.path.join(current_dir, "config_files/insspg_motor_config.json")


# Load the JSON file
with open(config_path, "r") as config_file:
    config_data = json.load(config_file)

with open(incpg_params_path, "r") as incpg_independent_params_file:
    incpg_params = json.load(incpg_independent_params_file)

with open(incpg_motor_config_path, "r") as incpg_motor_config_file:
    inwcg_motor_config = json.load(incpg_motor_config_file)

#---------------------------------------------------
# Transferring relevant data to individual variables
#---------------------------------------------------
motor_data          = inwcg_motor_config["Motors"]
material_properties = config_data["Material_properties"]

Gear_standard_parameters = config_data["Gear_standard_parameters"]
Lewis_params             = config_data["Lewis_params"]
MIT_params               = config_data["MIT_params"]

Steel    = material_properties["Steel"]
Aluminum = material_properties["Aluminum"]
PLA      = material_properties["PLA"]

incpg_design_params       = incpg_params["incpg_3DP_design_parameters"]
incpg_optimization_params = incpg_params["incpg_optimization_parameters"]

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


#Motor RI80
MotorRI80_Kv                   = motor_data["RI80"]["Kv"]                   # rpm/V
MotorRI80_maxContinuousCurrent = motor_data["RI80"]["maxContinuousCurrent"] # A

MotorRI80_maxTorque                  = MotorRI80_maxContinuousCurrent / (MotorRI80_Kv * 2 * np.pi / 60)
MotorRI80_power                      = motor_data["RI80"]["power"]                 # W 

MotorRI80_ratedVoltage               = motor_data["RI80"]["ratedVoltage"]   
MotorRI80_maxMotorAngVelRPM          = MotorRI80_Kv * MotorRI80_ratedVoltage # RPM 
MotorRI80_mass                       = motor_data["RI80"]["massKG"]                  # kg 

MotorRI80_rotor_OD                  = motor_data["RI80"]["Rotor_OD"]
MotorRI80_stator_ID                 = motor_data["RI80"]["Stator_ID"]
MotorRI80_rotor_height              = motor_data["RI80"]["Rotor_height"]
MotorRI80_rotor_ID                  = motor_data["RI80"]["Rotor_ID"]
MotorRI80_stator_height             = motor_data["RI80"]["stator_height"]
MotorRI80_stator_OD                 = motor_data["RI80"]["Stator_OD"]
MotorRI80_stator_hole_dia           = motor_data["RI80"]["stator_mounting_holes_dia"]
MotorRI80_stator_wire_top_height    = motor_data["RI80"]["stator_upper_step_height"]
MotorRI80_stator_mid_height         = motor_data["RI80"]["stator_mid_height"]
MotorRI80_stator_wire_bottom_height = motor_data["RI80"]["stator_bottom_step_height_"]
MotorRI80_stator_wire_OD            = motor_data["RI80"]["stator_side_step_OD"]
MotorRI80_stator_hole_num           = motor_data["RI80"]["stator_hole_num"]
MotorRI80_stator_wire_ID            = motor_data["RI80"]["stator_side_step_ID"]

# Motor-RI80
MotorRI80  = motor(rotor_OD                   = MotorRI80_rotor_OD,
                  stator_ID                    = MotorRI80_stator_ID,
                  rotor_height                 = MotorRI80_rotor_height,
                  rotor_ID                     = MotorRI80_rotor_ID,
                  stator_height                = MotorRI80_stator_height,
                  stator_OD                    = MotorRI80_stator_OD,
                  stator_hole_dia              = MotorRI80_stator_hole_dia,
                  stator_wire_top_height       = MotorRI80_stator_wire_top_height,
                  stator_mid_height            = MotorRI80_stator_mid_height,
                  stator_wire_bottom_height    = MotorRI80_stator_wire_bottom_height,
                  stator_wire_OD               = MotorRI80_stator_wire_OD,          
                  stator_hole_num              = MotorRI80_stator_hole_num,     
                  stator_wire_ID               = MotorRI80_stator_wire_ID,      
                  maxMotorAngVelRPM            = MotorRI80_maxMotorAngVelRPM,
                  maxMotorTorque               = MotorRI80_maxTorque,
                  maxMotorPower                = MotorRI80_power,
                  motorMass                    = MotorRI80_mass,
                  motorName                    = "RI80")

#-------------------------------------------------------
# Gearbox 
#-------------------------------------------------------
inrunnerCompoundPlanetaryGearboxInstance = inrunnerCompoundPlanetaryGearbox(design_parameters         = incpg_design_params,
                                                                            gear_standard_parameters  = Gear_standard_parameters,
                                                                            densityGears              = PLA["density"],
                                                                            densityStructure          = PLA["density"],
                                                                            maxGearAllowableStressMPa = PLA["maxAllowableStressMPa"],
                                                                            densityAluminum           = Aluminum["density"])

#-----------------------------------------------------
# Actuator
#-----------------------------------------------------
maxGBDia_multFactor           = incpg_optimization_params["MAX_GB_DIA_MULT_FACTOR"] # 1

maxGearboxDiameter_RI100         = maxGBDia_multFactor * MotorRI100.motorDiaMM       
maxGearboxDiameter_RI80         = maxGBDia_multFactor * MotorRI80.motorDiaMM

# RI100-Actuator
Actuator_RI100 = inrunnerCompoundPlanetaryActuator(design_parameters        = incpg_design_params,
                                                   motor                    = MotorRI100,  
                                                   motor_driver_params      = Motor_Driver_OdrivePro_params,
                                                   inrunnerCompoundPlanetaryGearbox = inrunnerCompoundPlanetaryGearboxInstance, 
                                                   FOS                      = MIT_params["FOS"], 
                                                   serviceFactor            = MIT_params["serviceFactor"], 
                                                   maxGearboxDiameter       = maxGearboxDiameter_RI100,
                                                   stressAnalysisMethodName = "MIT")

Actuator_RI80 = inrunnerCompoundPlanetaryActuator(design_parameters        = incpg_design_params,
                                                   motor                    = MotorRI80,  
                                                   motor_driver_params      = Motor_Driver_OdrivePro_params,
                                                   inrunnerCompoundPlanetaryGearbox = inrunnerCompoundPlanetaryGearboxInstance, 
                                                   FOS                      = MIT_params["FOS"], 
                                                   serviceFactor            = MIT_params["serviceFactor"], 
                                                   maxGearboxDiameter       = maxGearboxDiameter_RI80,
                                                   stressAnalysisMethodName = "MIT")

#-----------------------------------------------------
# Optimization
#-----------------------------------------------------
opt_param = config_data["Cost_gain_parameters"]

K_Mass = opt_param["K_Mass"]
K_Eff  = opt_param["K_Eff"]
K_Width = opt_param["K_Width"]

GEAR_RATIO_MIN  = incpg_optimization_params["GEAR_RATIO_MIN"]  # 4
GEAR_RATIO_MAX  = incpg_optimization_params["GEAR_RATIO_MAX"]  # 30
GEAR_RATIO_STEP = incpg_optimization_params["GEAR_RATIO_STEP"] # 1

MODULE_BIG_MIN             = incpg_optimization_params["MODULE_MIN"]           # 0.8
MODULE_BIG_MAX             = incpg_optimization_params["MODULE_MAX"]           # 1.2
MODULE_SMALL_MIN           = incpg_optimization_params["MODULE_MIN"]           # 0.8
MODULE_SMALL_MAX           = incpg_optimization_params["MODULE_MAX"]           # 1.2
NUM_PLANET_MIN             = incpg_optimization_params["NUM_PLANET_MIN"]       # 3  
NUM_PLANET_MAX             = incpg_optimization_params["NUM_PLANET_MAX"]       # 5  
NUM_TEETH_SUN_MIN          = incpg_optimization_params["NUM_TEETH_SUN_MIN"]    # 20 
NUM_TEETH_PLANET_BIG_MIN   = incpg_optimization_params["NUM_TEETH_PLANET_MIN"] # 20 
NUM_TEETH_PLANET_SMALL_MIN = incpg_optimization_params["NUM_TEETH_PLANET_MIN"] # 20 

Optimizer_RI100 = optimizationInrunnerCompoundPlanetaryActuator(design_parameters          = incpg_design_params,
                                                                gear_standard_parameters   = Gear_standard_parameters,
                                                                K_Mass                     = K_Mass                     ,
                                                                K_Eff                      = K_Eff                      ,
                                                                K_Width                    = K_Width                    ,
                                                                MODULE_BIG_MIN             = MODULE_BIG_MIN             ,
                                                                MODULE_BIG_MAX             = MODULE_BIG_MAX             ,
                                                                MODULE_SMALL_MIN           = MODULE_SMALL_MIN           ,
                                                                MODULE_SMALL_MAX           = MODULE_SMALL_MAX           ,
                                                                NUM_PLANET_MIN             = NUM_PLANET_MIN             ,
                                                                NUM_PLANET_MAX             = NUM_PLANET_MAX             ,
                                                                NUM_TEETH_SUN_MIN          = NUM_TEETH_SUN_MIN          ,
                                                                NUM_TEETH_PLANET_BIG_MIN   = NUM_TEETH_PLANET_BIG_MIN   ,
                                                                NUM_TEETH_PLANET_SMALL_MIN = NUM_TEETH_PLANET_SMALL_MIN ,
                                                                GEAR_RATIO_MIN             = GEAR_RATIO_MIN             ,
                                                                GEAR_RATIO_MAX             = GEAR_RATIO_MAX             ,
                                                                GEAR_RATIO_STEP            = GEAR_RATIO_STEP            )

Optimizer_RI80 = optimizationInrunnerCompoundPlanetaryActuator(design_parameters          = incpg_design_params,
                                                                gear_standard_parameters   = Gear_standard_parameters,
                                                                K_Mass                     = K_Mass                     ,
                                                                K_Eff                      = K_Eff                      ,
                                                                K_Width                    = K_Width                    ,
                                                                MODULE_BIG_MIN             = MODULE_BIG_MIN             ,
                                                                MODULE_BIG_MAX             = MODULE_BIG_MAX             ,
                                                                MODULE_SMALL_MIN           = MODULE_SMALL_MIN           ,
                                                                MODULE_SMALL_MAX           = MODULE_SMALL_MAX           ,
                                                                NUM_PLANET_MIN             = NUM_PLANET_MIN             ,
                                                                NUM_PLANET_MAX             = NUM_PLANET_MAX             ,
                                                                NUM_TEETH_SUN_MIN          = NUM_TEETH_SUN_MIN          ,
                                                                NUM_TEETH_PLANET_BIG_MIN   = NUM_TEETH_PLANET_BIG_MIN   ,
                                                                NUM_TEETH_PLANET_SMALL_MIN = NUM_TEETH_PLANET_SMALL_MIN ,
                                                                GEAR_RATIO_MIN             = GEAR_RATIO_MIN             ,
                                                                GEAR_RATIO_MAX             = GEAR_RATIO_MAX             ,
                                                                GEAR_RATIO_STEP            = GEAR_RATIO_STEP            )

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
    elif motor_name == "RI80":
        return Optimizer_RI80.optimizeActuator(
            Actuator_RI80,
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
