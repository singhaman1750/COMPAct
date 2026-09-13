import math
import os
import sys
import time
import json
import numpy as np
from ActuatorandGearbox_INDSPG import material
from ActuatorandGearbox_INDSPG import inrunnerdoubleStagePlanetaryGearbox
from ActuatorandGearbox_INDSPG import inrunnerdoubleStageActuator
from ActuatorandGearbox_INDSPG import optimizationDoubleStageActuator

#----------motor variables from common components----------#
from CommonComponents import motor_frameless_inrunner as Motor



#--------------------------------------------------------
# Importing Config data
#--------------------------------------------------------
current_dir = os.path.dirname(__file__)

# Build the file path
config_path      = os.path.join(current_dir, "config_files/indspg_motor_config.json")
indspg_params_path = os.path.join(current_dir, "config_files/indspg_params.json")

# Load the JSON file
with open(config_path, "r") as config_file:
    config_data = json.load(config_file)

with open(indspg_params_path, "r") as indspg_params_file:
    indspg_params = json.load(indspg_params_file)

#---------------------------------------------------
# Transferring relevant data to individual variables
#---------------------------------------------------
motor_data          = config_data["Motors"]
material_properties = config_data["Material_properties"]

Gear_standard_parameters = config_data["Gear_standard_parameters"]
Lewis_params             = config_data["Lewis_params"]
MIT_params               = config_data["MIT_params"]

Steel    = material_properties["Steel"]
Aluminum = material_properties["Aluminum"]
pla     = material_properties["PLA"]

indspg_design_params       = indspg_params["indspg_design_parameters_3DP"]
indspg_optimization_params = indspg_params["indspg_optimization_parameters"]


#motor_driver_data = config_data["Motor_drivers"]

#--------------------------------------------------------
# Motors Drivers
#--------------------------------------------------------
#Motor_Driver_Moteus_params    = motor_driver_data["Moteus"]
#Motor_Driver_OdrivePro_params = motor_driver_data["OdrivePro"]


#--------------------------------------------------------
# Motors
#--------------------------------------------------------
# RI100

Motor_RI100_rotor_OD                     = motor_data["MotorRI100"]["rotor_OD"]
Motor_RI100_stator_ID                    = motor_data["MotorRI100"]["stator_ID"]
Motor_RI100_rotor_height                 = motor_data["MotorRI100"]["rotor_height"]
Motor_RI100_rotor_ID                     = motor_data["MotorRI100"]["rotor_ID"]
Motor_RI100_stator_height                = motor_data["MotorRI100"]["stator_height"]
Motor_RI100_stator_OD                    = motor_data["MotorRI100"]["stator_OD"]
Motor_RI100_stator_hole_dia              = motor_data["MotorRI100"]["stator_hole_dia"]
Motor_RI100_stator_wire_top_height       = motor_data["MotorRI100"]["stator_wire_top_height"]
Motor_RI100_stator_mid_height            = motor_data["MotorRI100"]["stator_mid_height"]
Motor_RI100_stator_wire_bottom_height    = motor_data["MotorRI100"]["stator_wire_bottom_height"]
Motor_RI100_stator_wire_OD              = motor_data["MotorRI100"]["stator_wire_OD"]
Motor_RI100_stator_wire_ID              = motor_data["MotorRI100"]["stator_wire_ID"]
Motor_RI100_maxMotorAngVelRPM           = motor_data["MotorRI100"]["maxMotorAngVelRPM"]
Motor_RI100_maxMotorTorque              = motor_data["MotorRI100"]["maxMotorTorque"]
Motor_RI100_maxMotorPower               = motor_data["MotorRI100"]["maxMotorPower"]
Motor_RI100_motorMass                   = motor_data["MotorRI100"]["motorMass"]

# RI_80

Motor_RI80_rotor_OD                     = motor_data["MotorRI80"]["rotor_OD"]
Motor_RI80_stator_ID                    = motor_data["MotorRI80"]["stator_ID"]
Motor_RI80_rotor_height                 = motor_data["MotorRI80"]["rotor_height"]
Motor_RI80_rotor_ID                     = motor_data["MotorRI80"]["rotor_ID"]
Motor_RI80_stator_height                = motor_data["MotorRI80"]["stator_height"]
Motor_RI80_stator_OD                    = motor_data["MotorRI80"]["stator_OD"]
Motor_RI80_stator_hole_dia              = motor_data["MotorRI80"]["stator_hole_dia"]
Motor_RI80_stator_wire_top_height       = motor_data["MotorRI80"]["stator_wire_top_height"]
Motor_RI80_stator_mid_height            = motor_data["MotorRI80"]["stator_mid_height"]
Motor_RI80_stator_wire_bottom_height    = motor_data["MotorRI80"]["stator_wire_bottom_height"]
Motor_RI80_stator_wire_OD              = motor_data["MotorRI80"]["stator_wire_OD"]
Motor_RI80_stator_wire_ID              = motor_data["MotorRI80"]["stator_wire_ID"]
Motor_RI80_maxMotorAngVelRPM           = motor_data["MotorRI80"]["maxMotorAngVelRPM"]
Motor_RI80_maxMotorTorque              = motor_data["MotorRI80"]["maxMotorTorque"]
Motor_RI80_maxMotorPower               = motor_data["MotorRI80"]["maxMotorPower"]
Motor_RI80_motorMass                   = motor_data["MotorRI80"]["motorMass"]


#MOTOR RI100

MotorRI100 = Motor( rotor_OD                     = Motor_RI100_rotor_OD,
                    stator_ID                    = Motor_RI100_stator_ID,
                    rotor_height                 = Motor_RI100_rotor_height,
                    rotor_ID                     = Motor_RI100_rotor_ID,
                    stator_height                = Motor_RI100_stator_height,
                    stator_OD                    = Motor_RI100_stator_OD,
                    stator_hole_dia              = Motor_RI100_stator_hole_dia,
                    stator_wire_top_height       = Motor_RI100_stator_wire_top_height,
                    stator_mid_height            = Motor_RI100_stator_mid_height,
                    stator_wire_bottom_height    = Motor_RI100_stator_wire_bottom_height,
                    stator_wire_OD              = Motor_RI100_stator_wire_OD,
                    stator_wire_ID              = Motor_RI100_stator_wire_ID,
                    maxMotorAngVelRPM           = Motor_RI100_maxMotorAngVelRPM,
                    maxMotorTorque              = Motor_RI100_maxMotorTorque,
                    maxMotorPower               = Motor_RI100_maxMotorPower,
                    motorMass                   = Motor_RI100_motorMass
                )

#MOTOR RI80

MotorRI80 = Motor( rotor_OD                     = Motor_RI80_rotor_OD,
                    stator_ID                    = Motor_RI80_stator_ID, 
                    rotor_height                 = Motor_RI80_rotor_height,
                    rotor_ID                     = Motor_RI80_rotor_ID,
                    stator_height                = Motor_RI80_stator_height,
                    stator_OD                    = Motor_RI80_stator_OD,
                    stator_hole_dia              = Motor_RI80_stator_hole_dia,
                    stator_wire_top_height       = Motor_RI80_stator_wire_top_height,
                    stator_mid_height            = Motor_RI80_stator_mid_height,
                    stator_wire_bottom_height    = Motor_RI80_stator_wire_bottom_height,
                    stator_wire_OD              = Motor_RI80_stator_wire_OD,
                    stator_wire_ID              = Motor_RI80_stator_wire_ID,
                    maxMotorAngVelRPM           = Motor_RI80_maxMotorAngVelRPM,
                    maxMotorTorque              = Motor_RI80_maxMotorTorque,
                    maxMotorPower               = Motor_RI80_maxMotorPower,
                    motorMass                   = Motor_RI80_motorMass
                )   


#------------------------------------------------------
# Gearbox 
#--------------------------------------------------------
inrunnerdoubleStagePlanetaryGearboxInstance = inrunnerdoubleStagePlanetaryGearbox(design_parameters         = indspg_design_params,
                                                                  gear_standard_parameters  = Gear_standard_parameters,
                                                                  densityGears              = Aluminum["density"],
                                                                  densityStructure          = pla["density"],
                                                                  maxGearAllowableStressMPa = pla["maxAllowableStressMPa"])
                                                                  
#-----------------------------------------------------
# Actuator
#-----------------------------------------------------

maxGBDia_multFactor = indspg_optimization_params["MAX_GB_DIA_MULT_FACTOR"]


maxGearboxDiameter_RI100 = (
    maxGBDia_multFactor
    * ( MotorRI100.getStator_wire_OD() - indspg_design_params["ring2RadialWidthMM"]*2 )
)

# --- NEW: Define Stage 1 specific limit ---
maxGearboxDiameter_Stg1_RI100 = (MotorRI100.getRotorIDMM() - indspg_design_params["standard_clearance_1_5mm"]*4)

maxGearboxDiameter_RI80 = (
    maxGBDia_multFactor
    * ( MotorRI80.getStator_wire_OD() - indspg_design_params["ring2RadialWidthMM"]*2 )
)

# --- NEW: Define Stage 1 specific limit ---
maxGearboxDiameter_Stg1_RI80 = (MotorRI80.getRotorIDMM() - indspg_design_params["standard_clearance_1_5mm"]*5)



#-----------------------------------------------------
# RI 100 & RI 80 Actuator Instances
#-----------------------------------------------------


Actuator_RI100 = inrunnerdoubleStageActuator(
    design_parameters        = indspg_design_params,
    motor                    = MotorRI100,
    inrunnerdoubleStagePlanetaryGearbox=inrunnerdoubleStagePlanetaryGearboxInstance,

    FOS                      = MIT_params["FOS"],
    serviceFactor            = MIT_params["serviceFactor"],

    maxGearboxDiameter       = maxGearboxDiameter_RI100,
    maxGearboxDiameter_Stg1  = maxGearboxDiameter_Stg1_RI100,
    stressAnalysisMethodName = "MIT"
)

Actuator_RI80 = inrunnerdoubleStageActuator(
    design_parameters        = indspg_design_params,
    motor                    = MotorRI80,
    inrunnerdoubleStagePlanetaryGearbox=inrunnerdoubleStagePlanetaryGearboxInstance,

    FOS                      = MIT_params["FOS"],
    serviceFactor            = MIT_params["serviceFactor"],

    maxGearboxDiameter       = maxGearboxDiameter_RI80,
    maxGearboxDiameter_Stg1  = maxGearboxDiameter_Stg1_RI80,
    stressAnalysisMethodName = "MIT"
)


# Optimization
opt_param = config_data["Cost_gain_parameters"]

K_Mass = opt_param["K_Mass"]
K_Eff  = opt_param["K_Eff"]
K_Width  = opt_param["K_Width"]

GEAR_RATIO_MIN  = indspg_optimization_params["GEAR_RATIO_MIN"]        # 4   
GEAR_RATIO_MAX  = indspg_optimization_params["GEAR_RATIO_MAX"]        # 45  
GEAR_RATIO_STEP = indspg_optimization_params["GEAR_RATIO_STEP"]       # 1  

MODULE_STAGE1_MIN     = indspg_optimization_params["MODULE_STAGE1_MIN"]     # 0.5 
MODULE_STAGE1_MAX     = indspg_optimization_params["MODULE_STAGE1_MAX"]     # 0.8 
MODULE_STAGE2_MIN     = indspg_optimization_params["MODULE_STAGE2_MIN"]     # 0.9 
MODULE_STAGE2_MAX     = indspg_optimization_params["MODULE_STAGE2_MAX"]     # 1.2 
NUM_PLANET_STAGE1_MIN = indspg_optimization_params["NUM_PLANET_STAGE1_MIN"] # 3   
NUM_PLANET_STAGE1_MAX = indspg_optimization_params["NUM_PLANET_STAGE1_MAX"] # 5   
NUM_PLANET_STAGE2_MIN = indspg_optimization_params["NUM_PLANET_STAGE2_MIN"] # 3   
NUM_PLANET_STAGE2_MAX = indspg_optimization_params["NUM_PLANET_STAGE2_MAX"] # 5   
NUM_TEETH_SUN_MIN     = indspg_optimization_params["NUM_TEETH_SUN_MIN"]     # 20  
NUM_TEETH_PLANET_MIN  = indspg_optimization_params["NUM_TEETH_PLANET_MIN"]  # 20   

Optimizer_RI100     = optimizationDoubleStageActuator(design_parameters        = indspg_design_params,
                                                            gear_standard_parameters = Gear_standard_parameters,
                                                            K_Mass                   = K_Mass                ,
                                                            K_Eff                    = K_Eff                 ,
                                                            K_Width                  = K_Width               ,
                                                            MODULE_STAGE1_MIN        = MODULE_STAGE1_MIN     ,
                                                            MODULE_STAGE1_MAX        = MODULE_STAGE1_MAX     ,
                                                            MODULE_STAGE2_MIN        = MODULE_STAGE2_MIN     ,
                                                            MODULE_STAGE2_MAX        = MODULE_STAGE2_MAX     ,
                                                            NUM_PLANET_STAGE1_MIN    = NUM_PLANET_STAGE1_MIN ,
                                                            NUM_PLANET_STAGE1_MAX    = NUM_PLANET_STAGE1_MAX ,
                                                            NUM_PLANET_STAGE2_MIN    = NUM_PLANET_STAGE2_MIN ,
                                                            NUM_PLANET_STAGE2_MAX    = NUM_PLANET_STAGE2_MAX ,
                                                            NUM_TEETH_SUN_MIN        = NUM_TEETH_SUN_MIN     ,
                                                            NUM_TEETH_PLANET_MIN     = NUM_TEETH_PLANET_MIN  ,
                                                            GEAR_RATIO_MIN           = GEAR_RATIO_MIN        ,
                                                            GEAR_RATIO_MAX           = GEAR_RATIO_MAX        ,
                                                            GEAR_RATIO_STEP          = GEAR_RATIO_STEP       
                                                        )

Optimizer_RI80    = optimizationDoubleStageActuator(design_parameters        = indspg_design_params,
                                                            gear_standard_parameters = Gear_standard_parameters,
                                                            K_Mass                   = K_Mass                ,
                                                            K_Eff                    = K_Eff                 ,
                                                            K_Width                  = K_Width               ,
                                                            MODULE_STAGE1_MIN        = MODULE_STAGE1_MIN     ,
                                                            MODULE_STAGE1_MAX        = MODULE_STAGE1_MAX     ,
                                                            MODULE_STAGE2_MIN        = MODULE_STAGE2_MIN     ,
                                                            MODULE_STAGE2_MAX        = MODULE_STAGE2_MAX     ,
                                                            NUM_PLANET_STAGE1_MIN    = NUM_PLANET_STAGE1_MIN ,
                                                            NUM_PLANET_STAGE1_MAX    = NUM_PLANET_STAGE1_MAX ,
                                                            NUM_PLANET_STAGE2_MIN    = NUM_PLANET_STAGE2_MIN ,
                                                            NUM_PLANET_STAGE2_MAX    = NUM_PLANET_STAGE2_MAX ,
                                                            NUM_TEETH_SUN_MIN        = NUM_TEETH_SUN_MIN     ,
                                                            NUM_TEETH_PLANET_MIN     = NUM_TEETH_PLANET_MIN  ,
                                                            GEAR_RATIO_MIN           = GEAR_RATIO_MIN        ,
                                                            GEAR_RATIO_MAX           = GEAR_RATIO_MAX        ,
                                                            GEAR_RATIO_STEP          = GEAR_RATIO_STEP       
                                                        )



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


# #-----------------------
# # Optimization: RI100
# #-----------------------
# totalTime_RO100 = Optimizer_RO100.optimizeActuator(Actuator_RO100, UsePSCasVariable = 0, log=0, csv=1, printOptParams=1, gearRatioReq=0)

# # Convert to hours, minutes, and seconds
# hours_RO100, remainder_RO100 = divmod(totalTime_RO100, 3600)
# minutes_RO100, seconds_RO100 = divmod(remainder_RO100, 60)

# #Print
# print("Optimization Completed : DSPG RO100")
# print(f"Time taken: {hours_RO100} hours, {minutes_RO100} minutes, and {seconds_RO100} seconds")

# #-----------------------
# # Optimization: RO80
# #-----------------------
# totalTime_RO80 = Optimizer_RO80.optimizeActuator(Actuator_RO80, UsePSCasVariable = 0, log=0, csv=1, printOptParams=1, gearRatioReq=0)

# # Convert to hours, minutes, and seconds
# hours_RO80, remainder_RO80 = divmod(totalTime_RO80, 3600)
# minutes_RO80, seconds_RO80 = divmod(remainder_RO80, 60)

# # Print
# print("Optimization Completed : DSPG RO80")
# print(f"Time taken: {hours_RO80} hours, {minutes_RO80} minutes, and {seconds_RO80} seconds")