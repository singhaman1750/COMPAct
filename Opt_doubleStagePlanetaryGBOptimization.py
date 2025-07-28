import sys
import numpy as np
from ActuatorAndGearbox import motor
from ActuatorAndGearbox import material
from ActuatorAndGearbox import doubleStagePlanetaryGearbox
from ActuatorAndGearbox import doubleStagePlanetaryActuator
from ActuatorAndGearbox import optimizationDoubleStagePlanetaryActuator
import sys
import os
import json

#--------------------------------------------------------
# Importing Config data
#--------------------------------------------------------
# Get the current directory
current_dir = os.path.dirname(__file__)

# Build the file path
config_path      = os.path.join(current_dir, "config_files/config.json")
dspg_params_path = os.path.join(current_dir, "config_files/dspg_params.json")

# Load the JSON file
with open(config_path, "r") as config_file:
    config_data = json.load(config_file)

with open(dspg_params_path, "r") as dspg_params_file:
    dspg_params = json.load(dspg_params_file)

#---------------------------------------------------
# Transferring relevant data to individual variables
#---------------------------------------------------
motor_data          = config_data["Motors"]
material_properties = config_data["Material_properties"]

Gear_standard_parameters = config_data["Gear_standard_parameters"]
Lewis_params             = config_data["Lewis_params"]

Steel    = material_properties["Steel"]
Aluminum = material_properties["Aluminum"]

dspg_design_params       = dspg_params["dspg_design_parameters_3DP"]
dspg_optimization_params = dspg_params["dspg_optimization_parameters"]

#--------------------------------------------------------
# Motors
#--------------------------------------------------------
# T motor U8
MotorU8_maxTorque         = motor_data["MotorU8_framed"]["maxTorque"]            # Nm
MotorU8_power             = motor_data["MotorU8_framed"]["power"]                # W 
MotorU8_maxMotorAngVelRPM = (MotorU8_power * 60) / (MotorU8_maxTorque * 2*np.pi) # RPM 
MotorU8_mass              = motor_data["MotorU8_framed"]["mass"]                 # kg 
MotorU8_dia               = motor_data["MotorU8_framed"]["dia"]                  # mm 
MotorU8_length            = motor_data["MotorU8_framed"]["length"]               # mm

# U10 Motor
MotorU10_maxTorque         = motor_data["MotorU10_framed"]["maxTorque"]             # Nm
MotorU10_power             = motor_data["MotorU10_framed"]["power"]                 # W
MotorU10_maxMotorAngVelRPM = (MotorU10_power * 60) / (MotorU10_maxTorque * 2*np.pi) # RPM
MotorU10_mass              = motor_data["MotorU10_framed"]["mass"]                  # Kg 
MotorU10_dia               = motor_data["MotorU10_framed"]["dia"]                   # mm
MotorU10_length            = motor_data["MotorU10_framed"]["length"]                # mm

# MN8014 Motor
MotorMN8014_maxTorque         = motor_data["MotorMN8014_framed"]["maxTorque"]                # Nm
MotorMN8014_power             = motor_data["MotorMN8014_framed"]["power"]                    # W
MotorMN8014_maxMotorAngVelRPM = (MotorMN8014_power * 60) / (MotorMN8014_maxTorque * 2*np.pi) # RPM
MotorMN8014_mass              = motor_data["MotorMN8014_framed"]["mass"]                     # Kg 
MotorMN8014_dia               = motor_data["MotorMN8014_framed"]["dia"]                      # mm
MotorMN8014_length            = motor_data["MotorMN8014_framed"]["length"]                   # mm

# VT8020 Motor
Motor8020_maxTorque         = motor_data["Motor8020_framed"]["maxTorque"]              # Nm
Motor8020_power             = motor_data["Motor8020_framed"]["power"]                  # W
Motor8020_maxMotorAngVelRPM = (Motor8020_power * 60) / (Motor8020_maxTorque * 2*np.pi) # RPM
Motor8020_mass              = motor_data["Motor8020_framed"]["mass"]                   # Kg 
Motor8020_dia               = motor_data["Motor8020_framed"]["dia"]                    # mm
Motor8020_length            = motor_data["Motor8020_framed"]["length"]                 # mm

# U12 Motor
MotorU12_maxTorque         = motor_data["MotorU12_framed"]["maxTorque"]             # Nm
MotorU12_power             = motor_data["MotorU12_framed"]["power"]                 # W 
MotorU12_maxMotorAngVelRPM = (MotorU12_power * 60) / (MotorU12_maxTorque * 2*np.pi) # RPM 
MotorU12_mass              = motor_data["MotorU12_framed"]["mass"]                  # kg 
MotorU12_dia               = motor_data["MotorU12_framed"]["dia"]                   # mm 
MotorU12_length            = motor_data["MotorU12_framed"]["length"]                # mm

# Motor-U8
MotorU8 = motor(maxMotorAngVelRPM = MotorU8_maxMotorAngVelRPM, 
                 maxMotorTorque    = MotorU8_maxTorque       ,
                 maxMotorPower     = MotorU8_power           ,
                 motorMass         = MotorU8_mass            ,
                 motorDia          = MotorU8_dia             ,
                 motorLength       = MotorU8_length          ,
                 motorName         = "U8")

# Motor-U10
MotorU10  = motor(maxMotorAngVelRPM   = MotorU10_maxMotorAngVelRPM, # RPM 
                  maxMotorTorque      = MotorU10_maxTorque        , # Nm 
                  maxMotorPower       = MotorU10_power            , # W 
                  motorMass           = MotorU10_mass             , # kg 
                  motorDia            = MotorU10_dia              , # mm 
                  motorLength         = MotorU10_length           ,      
                  motorName           = "U10") 

# Motor-MN8014
MotorMN8014 = motor(maxMotorAngVelRPM = MotorMN8014_maxMotorAngVelRPM, # RPM 
                    maxMotorTorque      = MotorMN8014_maxTorque      , # Nm 
                    maxMotorPower       = MotorMN8014_power          , # W 
                    motorMass           = MotorMN8014_mass           , # kg 
                    motorDia            = MotorMN8014_dia            , # mm 
                    motorLength         = MotorMN8014_length         ,     
                    motorName           = "MN8014") 

# Motor-VT8020
Motor8020 = motor(maxMotorAngVelRPM = Motor8020_maxMotorAngVelRPM , # RPM 
                  maxMotorTorque    = Motor8020_maxTorque         , # Nm 
                  maxMotorPower     = Motor8020_power             , # W 
                  motorMass         = Motor8020_mass              , # kg 
                  motorDia          = Motor8020_dia               , # mm 
                  motorLength       = Motor8020_length            ,     
                  motorName         = "VT8020")

# Motor-U12
MotorU12 = motor(maxMotorAngVelRPM = MotorU12_maxMotorAngVelRPM, 
                 maxMotorTorque    = MotorU12_maxTorque        , 
                 maxMotorPower     = MotorU12_power            ,
                 motorMass         = MotorU12_mass             , 
                 motorDia          = MotorU12_dia              , 
                 motorLength       = MotorU12_length           ,
                 motorName         = "U12")

#--------------------------------------------------------
# Gearbox
#--------------------------------------------------------
doubleStagePlanetaryGearboxInstance = doubleStagePlanetaryGearbox(design_parameters         = dspg_design_params,
                                                                  gear_standard_parameters  = Gear_standard_parameters,
                                                                  densityGear               = Steel["density"],
                                                                  densityCarrier            = Aluminum["density"],
                                                                  maxGearAllowableStressMPa = Steel["maxAllowableStressMPa"])
                                                                  
#----------------------------------------
# Actuator
#----------------------------------------
maxGearboxDiameter_U8     = MotorU8.motorDiaMM     - 2*dspg_design_params["Ring2RadialWidthMM"]
maxGearboxDiameter_U10    = MotorU10.motorDiaMM    - 2*dspg_design_params["Ring2RadialWidthMM"]
maxGearboxDiameter_MN8014 = MotorMN8014.motorDiaMM - 2*dspg_design_params["Ring2RadialWidthMM"]
maxGearboxDiameter_VT8020 = Motor8020.motorDiaMM   - 2*dspg_design_params["Ring2RadialWidthMM"]
maxGearboxDiameter_U12    = MotorU12.motorDiaMM    - 2*dspg_design_params["Ring2RadialWidthMM"] 

# U8-Actuator
Actuator_U8 = doubleStagePlanetaryActuator(design_parameters           = dspg_design_params,
                                           motor                       = MotorU8,  
                                           doubleStagePlanetaryGearbox = doubleStagePlanetaryGearboxInstance, 
                                           FOS                         = Lewis_params["FOS"], 
                                           serviceFactor               = Lewis_params["serviceFactor"], 
                                           maxGearboxDiameter          = maxGearboxDiameter_U8,
                                           stressAnalysisMethodName    = "Lewis")

# U10-Actuator
Actuator_U10 = doubleStagePlanetaryActuator(design_parameters           = dspg_design_params,
                                            motor                       = MotorU10,  
                                            doubleStagePlanetaryGearbox = doubleStagePlanetaryGearboxInstance, 
                                            FOS                         = Lewis_params["FOS"], 
                                            serviceFactor               = Lewis_params["serviceFactor"], 
                                            maxGearboxDiameter          = maxGearboxDiameter_U10,
                                            stressAnalysisMethodName    = "Lewis")

# MN8014-Actuator
Actuator_MN8014 = doubleStagePlanetaryActuator(design_parameters           = dspg_design_params,
                                               motor                       = MotorMN8014,  
                                               doubleStagePlanetaryGearbox = doubleStagePlanetaryGearboxInstance, 
                                               FOS                         = Lewis_params["FOS"], 
                                               serviceFactor               = Lewis_params["serviceFactor"], 
                                               maxGearboxDiameter          = maxGearboxDiameter_MN8014,
                                               stressAnalysisMethodName    = "Lewis")

Actuator_VT8020 = doubleStagePlanetaryActuator(design_parameters           = dspg_design_params,
                                               motor                       = Motor8020,
                                               doubleStagePlanetaryGearbox = doubleStagePlanetaryGearboxInstance,
                                               FOS                         = Lewis_params["FOS"],
                                               serviceFactor               = Lewis_params["serviceFactor"],
                                               maxGearboxDiameter          = maxGearboxDiameter_VT8020,
                                               stressAnalysisMethodName    = "Lewis")

Actuator_U12 = doubleStagePlanetaryActuator(design_parameters           = dspg_design_params,
                                            motor                       = MotorU12,
                                            doubleStagePlanetaryGearbox = doubleStagePlanetaryGearboxInstance,
                                            FOS                         = Lewis_params["FOS"],
                                            serviceFactor               = Lewis_params["serviceFactor"],
                                            maxGearboxDiameter          = maxGearboxDiameter_U12,
                                            stressAnalysisMethodName    = "Lewis")

# Optimization
opt_param = config_data["Cost_gain_parameters"]

K_Mass = opt_param["K_Mass"]
K_Eff  = opt_param["K_Eff"]

GEAR_RATIO_MIN  = dspg_optimization_params["GEAR_RATIO_MIN"]        # 4   
GEAR_RATIO_MAX  = dspg_optimization_params["GEAR_RATIO_MAX"]        # 45  
GEAR_RATIO_STEP = dspg_optimization_params["GEAR_RATIO_STEP"]       # 1  

MODULE_STAGE1_MIN     = dspg_optimization_params["MODULE_STAGE1_MIN"]     # 0.5 
MODULE_STAGE1_MAX     = dspg_optimization_params["MODULE_STAGE1_MAX"]     # 0.8 
MODULE_STAGE2_MIN     = dspg_optimization_params["MODULE_STAGE2_MIN"]     # 0.9 
MODULE_STAGE2_MAX     = dspg_optimization_params["MODULE_STAGE2_MAX"]     # 1.2 
NUM_PLANET_STAGE1_MIN = dspg_optimization_params["NUM_PLANET_STAGE1_MIN"] # 3   
NUM_PLANET_STAGE1_MAX = dspg_optimization_params["NUM_PLANET_STAGE1_MAX"] # 5   
NUM_PLANET_STAGE2_MIN = dspg_optimization_params["NUM_PLANET_STAGE2_MIN"] # 3   
NUM_PLANET_STAGE2_MAX = dspg_optimization_params["NUM_PLANET_STAGE2_MAX"] # 5   
NUM_TEETH_SUN_MIN     = dspg_optimization_params["NUM_TEETH_SUN_MIN"]     # 20  
NUM_TEETH_PLANET_MIN  = dspg_optimization_params["NUM_TEETH_PLANET_MIN"]  # 20   

Optimizer_U8     = optimizationDoubleStagePlanetaryActuator(design_parameters        = dspg_design_params,
                                                            gear_standard_parameters = Gear_standard_parameters,
                                                            K_Mass                   = K_Mass                ,
                                                            K_Eff                    = K_Eff                 ,
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
                                                            GEAR_RATIO_STEP          = GEAR_RATIO_STEP       )

Optimizer_U10    = optimizationDoubleStagePlanetaryActuator(design_parameters        = dspg_design_params,
                                                            gear_standard_parameters = Gear_standard_parameters,
                                                            K_Mass                   = K_Mass                ,
                                                            K_Eff                    = K_Eff                 ,
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
                                                            GEAR_RATIO_STEP          = GEAR_RATIO_STEP       )

Optimizer_MN8014 = optimizationDoubleStagePlanetaryActuator(design_parameters        = dspg_design_params,
                                                            gear_standard_parameters = Gear_standard_parameters,
                                                            K_Mass                   = K_Mass                ,
                                                            K_Eff                    = K_Eff                 ,
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
                                                            GEAR_RATIO_STEP          = GEAR_RATIO_STEP       )

Optimizer_VT8020 = optimizationDoubleStagePlanetaryActuator(design_parameters        = dspg_design_params,
                                                            gear_standard_parameters = Gear_standard_parameters,
                                                            K_Mass                   = K_Mass                ,
                                                            K_Eff                    = K_Eff                 ,
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
                                                            GEAR_RATIO_STEP          = GEAR_RATIO_STEP       )

Optimizer_U12 = optimizationDoubleStagePlanetaryActuator(design_parameters        = dspg_design_params,
                                                         gear_standard_parameters = Gear_standard_parameters,
                                                         K_Mass                   = K_Mass                ,
                                                         K_Eff                    = K_Eff                 ,
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
                                                         GEAR_RATIO_STEP          = GEAR_RATIO_STEP       )

#-----------------------
# Optimization: U8
#-----------------------
totalTime_U8 = Optimizer_U8.optimizeActuator(Actuator_U8, UsePSCasVariable = 0, log=0, csv=1)

# Convert to hours, minutes, and seconds
hours_U8, remainder_U8 = divmod(totalTime_U8, 3600)
minutes_U8, seconds_U8 = divmod(remainder_U8, 60)

# Print
print("Optimization Completed : DSPG U8")
print(f"Time taken: {hours_U8} hours, {minutes_U8} minutes, and {seconds_U8} seconds")

# #-----------------------
# # Optimization: U10
# #-----------------------
# totalTime_U10 = Optimizer_U10.optimizeActuator(Actuator_U10, UsePSCasVariable = 1, log=0, csv=1)

# # Convert to hours, minutes, and seconds
# hours_U10, remainder_U10 = divmod(totalTime_U10, 3600)
# minutes_U10, seconds_U10 = divmod(remainder_U10, 60)

# # Print
# print("Optimization Completed : DSPG U10")
# print(f"Time taken: {hours_U10} hours, {minutes_U10} minutes, and {seconds_U10} seconds")

# #-----------------------
# # Optimization: MN8014
# #-----------------------
# totalTime_MN8014 = Optimizer_MN8014.optimizeActuator(Actuator_MN8014, UsePSCasVariable = 1, log=0, csv=1)

# # Convert to hours, minutes, and seconds
# hours_MN8014, remainder_MN8014 = divmod(totalTime_MN8014, 3600)
# minutes_MN8014, seconds_MN8014 = divmod(remainder_MN8014, 60)

# # Print
# print("Optimization Completed : DSPG MN8014")
# print(f"Time taken: {hours_MN8014} hours, {minutes_MN8014} minutes, and {seconds_MN8014} seconds")

# #-----------------------
# # Optimization: VT8020
# #-----------------------
# totalTime_VT8020 = Optimizer_VT8020.optimizeActuator(Actuator_VT8020, UsePSCasVariable = 1, log=0, csv=1)

# # Convert to hours, minutes, and seconds
# hours_VT8020, remainder_VT8020 = divmod(totalTime_VT8020, 3600)
# minutes_VT8020, seconds_VT8020 = divmod(remainder_VT8020, 60)

# # Print
# print("Optimization Completed : DSPG VT8020")
# print(f"Time taken: {hours_VT8020} hours, {minutes_VT8020} minutes, and {seconds_VT8020} seconds")

# # --------------------
# # Optimization: U12
# # --------------------
# totalTime_U12 = Optimizer_U12.optimizeActuator(Actuator_U12, UsePSCasVariable = 1, log=0, csv=1)
 
# # Convert to hours, minutes, and seconds
# hours_U12, remainder_U12 = divmod(totalTime_U12, 3600)
# minutes_U12, seconds_U12 = divmod(remainder_U12, 60)

# # Print
# print("Optimization Completed : DSPG U12")
# print(f"Time taken: {hours_U12} hours, {minutes_U12} minutes, and {seconds_U12} seconds")