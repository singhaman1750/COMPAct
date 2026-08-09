import math
import os
import sys
import time
import json
import numpy as np
from ActuatorandGearbox_IDSPG import material
from ActuatorandGearbox_IDSPG import doubleStagePlanetaryGearbox
from ActuatorandGearbox_IDSPG import doubleStagePlanetaryActuator
from ActuatorandGearbox_IDSPG import optimizationDoubleStagePlanetaryActuator

#----------motor variables from common components----------#
from CommonComponents import motor_frameless_outrunner as Motor



#--------------------------------------------------------
# Importing Config data
#--------------------------------------------------------
current_dir = os.path.dirname(__file__)

# Build the file path
config_path      = os.path.join(current_dir, "config_files/idspg_motor_config.json")
idspg_params_path = os.path.join(current_dir, "config_files/idspg_params.json")

# Load the JSON file
with open(config_path, "r") as config_file:
    config_data = json.load(config_file)

with open(idspg_params_path, "r") as idspg_params_file:
    idspg_params = json.load(idspg_params_file)

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

idspg_design_params       = idspg_params["idspg_design_parameters_3DP"]
idspg_optimization_params = idspg_params["idspg_optimization_parameters"]
MotorRO100 = Motor()

motor_driver_data = config_data["Motor_drivers"]

#--------------------------------------------------------
# Motors Drivers
#--------------------------------------------------------
Motor_Driver_Moteus_params    = motor_driver_data["Moteus"]
Motor_Driver_OdrivePro_params = motor_driver_data["OdrivePro"]


#--------------------------------------------------------
# Motors
#--------------------------------------------------------

#--------------------------------------------------------
# Gearbox 
#--------------------------------------------------------
doubleStagePlanetaryGearboxInstance = doubleStagePlanetaryGearbox(design_parameters   = idspg_design_params,
                                                                  gear_standard_parameters  = Gear_standard_parameters,
                                                                  densityGears              = PLA["density"],
                                                                  densityStructure          = PLA["density"],
                                                                  maxGearAllowableStressMPa = PLA["maxAllowableStressMPa"])
                                                                  
#-----------------------------------------------------
# Actuator
#-----------------------------------------------------

maxGBDia_multFactor = idspg_optimization_params["MAX_GB_DIA_MULT_FACTOR"]

# # Internal Gearbox Packaging Limits
# maxGearboxDiameter_RI80  = (
#     maxGBDia_multFactor
#     * Motor.getStatorODMM()
# )
# # --- NEW: Define Stage 1 specific limit ---
# maxGearboxDiameter_Stg1_RI80 = Motor.getRotorIDMM() - idspg_design_params["standard_clearance_1_5mm"]*2


maxGearboxDiameter_RO100 = (
    maxGBDia_multFactor
    * ( MotorRO100.getMotorODMM() )
)


# --- NEW: Define Stage 1 specific limit ---
maxGearboxDiameter_Stg1_RO100 = (MotorRO100.getStatorIDMM() - idspg_design_params["ring1RadialWidthMM"]*2) 



#-----------------------------------------------------
# RI80 Actuator
#-----------------------------------------------------

# Actuator_RI80 = inrunnerdoubleStageActuator(
#     design_parameters        = indspg_design_params,
#     motor                    = MotorRI80,
#     inrunnerdoubleStagePlanetaryGearbox=inrunnerdoubleStagePlanetaryGearboxInstance,
#     FOS                      = MIT_params["FOS"],
#     serviceFactor            = MIT_params["serviceFactor"],

#     maxGearboxDiameter       = maxGearboxDiameter_RI80,
#     maxGearboxDiameter_Stg1  = maxGearboxDiameter_Stg1_RI80,

#     stressAnalysisMethodName = "MIT"
# )


#-----------------------------------------------------
# RI100 Actuator
#-----------------------------------------------------

Actuator_RO100 = doubleStagePlanetaryActuator(
    design_parameters        = idspg_design_params,
    motor                    = MotorRO100,
    motor_driver_params      = Motor_Driver_OdrivePro_params,
    doubleStagePlanetaryGearbox=doubleStagePlanetaryGearboxInstance,

    FOS                      = MIT_params["FOS"],
    serviceFactor            = MIT_params["serviceFactor"],

    maxGearboxDiameter       = maxGearboxDiameter_RO100,
    maxGearboxDiameter_Stg1  = maxGearboxDiameter_Stg1_RO100,
    stressAnalysisMethodName = "MIT"
)



# Optimization
opt_param = config_data["Cost_gain_parameters"]

K_Mass = opt_param["K_Mass"]
K_Eff  = opt_param["K_Eff"]
K_Width  = opt_param["K_Width"]

GEAR_RATIO_MIN  = idspg_optimization_params["GEAR_RATIO_MIN"]        # 4   
GEAR_RATIO_MAX  = idspg_optimization_params["GEAR_RATIO_MAX"]        # 45  
GEAR_RATIO_STEP = idspg_optimization_params["GEAR_RATIO_STEP"]       # 1  

MODULE_STAGE1_MIN     = idspg_optimization_params["MODULE_STAGE1_MIN"]     # 0.5 
MODULE_STAGE1_MAX     = idspg_optimization_params["MODULE_STAGE1_MAX"]     # 0.8 
MODULE_STAGE2_MIN     = idspg_optimization_params["MODULE_STAGE2_MIN"]     # 0.9 
MODULE_STAGE2_MAX     = idspg_optimization_params["MODULE_STAGE2_MAX"]     # 1.2 
NUM_PLANET_STAGE1_MIN = idspg_optimization_params["NUM_PLANET_STAGE1_MIN"] # 3   
NUM_PLANET_STAGE1_MAX = idspg_optimization_params["NUM_PLANET_STAGE1_MAX"] # 5   
NUM_PLANET_STAGE2_MIN = idspg_optimization_params["NUM_PLANET_STAGE2_MIN"] # 3   
NUM_PLANET_STAGE2_MAX = idspg_optimization_params["NUM_PLANET_STAGE2_MAX"] # 5   
NUM_TEETH_SUN_MIN     = idspg_optimization_params["NUM_TEETH_SUN_MIN"]     # 20  
NUM_TEETH_PLANET_MIN  = idspg_optimization_params["NUM_TEETH_PLANET_MIN"]  # 20   

Optimizer_RO100     = optimizationDoubleStagePlanetaryActuator(design_parameters        = idspg_design_params,
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

# Optimizer_RI80    = optimizationDoubleStageActuator(design_parameters        = indspg_design_params,
#                                                             gear_standard_parameters = Gear_standard_parameters,
#                                                             K_Mass                   = K_Mass                ,
#                                                             K_Eff                    = K_Eff                 ,
#                                                             K_Width                  = K_Width               ,
#                                                             MODULE_STAGE1_MIN        = MODULE_STAGE1_MIN     ,
#                                                             MODULE_STAGE1_MAX        = MODULE_STAGE1_MAX     ,
#                                                             MODULE_STAGE2_MIN        = MODULE_STAGE2_MIN     ,
#                                                             MODULE_STAGE2_MAX        = MODULE_STAGE2_MAX     ,
#                                                             NUM_PLANET_STAGE1_MIN    = NUM_PLANET_STAGE1_MIN ,
#                                                             NUM_PLANET_STAGE1_MAX    = NUM_PLANET_STAGE1_MAX ,
#                                                             NUM_PLANET_STAGE2_MIN    = NUM_PLANET_STAGE2_MIN ,
#                                                             NUM_PLANET_STAGE2_MAX    = NUM_PLANET_STAGE2_MAX ,
#                                                             NUM_TEETH_SUN_MIN        = NUM_TEETH_SUN_MIN     ,
#                                                             NUM_TEETH_PLANET_MIN     = NUM_TEETH_PLANET_MIN  ,
#                                                             GEAR_RATIO_MIN           = GEAR_RATIO_MIN        ,
#                                                             GEAR_RATIO_MAX           = GEAR_RATIO_MAX        ,
#                                                             GEAR_RATIO_STEP          = GEAR_RATIO_STEP       )




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

    # elif motor_name == "RI80":
    #     return Optimizer_RI80.optimizeActuator(
    #         Actuator_RI80,
    #         UsePSCasVariable=0,
    #         log=0,
    #         csv=1,
    #         printOptParams=1,
    #         gearRatioReq=gear_ratio
    #     )

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