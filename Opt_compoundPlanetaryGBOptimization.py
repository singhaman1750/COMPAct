import sys
import numpy as np
from ActuatorAndGearbox import motor
from ActuatorAndGearbox import material
from ActuatorAndGearbox import compoundPlanetaryGearbox
from ActuatorAndGearbox import compoundPlanetaryActuator
from ActuatorAndGearbox import optimizationCompoundPlanetaryActuator
import os
import json

#--------------------------------------------------------
# Importing motor data
#--------------------------------------------------------
# Get the current directory
current_dir = os.path.dirname(__file__)

# Build the file path
config_path = os.path.join(current_dir, "config_files/config.json")
cpg_params_path = os.path.join(current_dir, "config_files/cpg_params.json")

# Load the JSON file
with open(config_path, "r") as config_file:
    config_data = json.load(config_file)

with open(cpg_params_path, "r") as cpg_params_file:
    cpg_params = json.load(cpg_params_file)

#---------------------------------------------------
# Transferring relevant data to individual variables
#---------------------------------------------------
motor_data          = config_data["Motors"]
material_properties = config_data["Material_properties"]

Gear_standard_parameters = config_data["Gear_standard_parameters"]
Lewis_params             = config_data["Lewis_params"]

Steel    = material_properties["Steel"]
Aluminum = material_properties["Aluminum"]

cpg_design_params       = cpg_params["cpg_design_parameters"]
cpg_optimization_params = cpg_params["cpg_optimization_parameters"]

#--------------------------------------------------------
# Motor Data
#--------------------------------------------------------
# T motor U8
MotorU8_maxTorque         = motor_data["MotorU8_framed"]["maxTorque"]             # Nm
MotorU8_power             = motor_data["MotorU8_framed"]["power"]                 # W 
MotorU8_maxMotorAngVelRPM = (MotorU8_power * 60) / (MotorU8_maxTorque * 2*np.pi) # RPM 
MotorU8_mass              = motor_data["MotorU8_framed"]["mass"]                  # kg 
MotorU8_dia               = motor_data["MotorU8_framed"]["dia"]                   # mm 
MotorU8_length            = motor_data["MotorU8_framed"]["length"]                # mm

# U10 Motor
MotorU10_maxTorque         = motor_data["MotorU10_framed"]["maxTorque"]              # Nm
MotorU10_power             = motor_data["MotorU10_framed"]["power"]                  # W
MotorU10_maxMotorAngVelRPM = (MotorU10_power * 60) / (MotorU10_maxTorque * 2*np.pi) # RPM
MotorU10_mass              = motor_data["MotorU10_framed"]["mass"]                   # Kg 
MotorU10_dia               = motor_data["MotorU10_framed"]["dia"]                    # mm
MotorU10_length            = motor_data["MotorU10_framed"]["length"]                 # mm

# MN8014 Motor
MotorMN8014_maxTorque         = motor_data["MotorMN8014_framed"]["maxTorque"]              # Nm
MotorMN8014_power             = motor_data["MotorMN8014_framed"]["power"]                  # W
MotorMN8014_maxMotorAngVelRPM = (MotorMN8014_power * 60) / (MotorMN8014_maxTorque * 2*np.pi) # RPM
MotorMN8014_mass              = motor_data["MotorMN8014_framed"]["mass"]                   # Kg 
MotorMN8014_dia               = motor_data["MotorMN8014_framed"]["dia"]                    # mm
MotorMN8014_length            = motor_data["MotorMN8014_framed"]["length"]                 # mm

# 8020 Motor
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
                 maxMotorTorque   = MotorU8_maxTorque,
                 maxMotorPower    = MotorU8_power,
                 motorMass        = MotorU8_mass,
                 motorDia         = MotorU8_dia,
                 motorLength      = MotorU8_length,
                 motorName        = "U8")

# Motor-U10
MotorU10  = motor(maxMotorAngVelRPM = MotorU10_maxMotorAngVelRPM, # RPM 
                  maxMotorTorque    = MotorU10_maxTorque,         # Nm 
                  maxMotorPower     = MotorU10_power,             # W 
                  motorMass         = MotorU10_mass,              # kg 
                  motorDia          = MotorU10_dia,               # mm 
                  motorLength       = MotorU10_length,     
                  motorName         = "U10") 

# Motor-MN8014
MotorMN8014 = motor(maxMotorAngVelRPM = MotorMN8014_maxMotorAngVelRPM, #RPM 
                    maxMotorTorque      = MotorMN8014_maxTorque      , # Nm 
                    maxMotorPower       = MotorMN8014_power          , # W 
                    motorMass           = MotorMN8014_mass           , # kg 
                    motorDia            = MotorMN8014_dia            , # mm 
                    motorLength         = MotorMN8014_length         ,     
                    motorName           = "MN8014") 

# VT8020 Motor
Motor8020 = motor(maxMotorAngVelRPM = Motor8020_maxMotorAngVelRPM , #RPM 
                  maxMotorTorque    = Motor8020_maxTorque         , # Nm 
                  maxMotorPower     = Motor8020_power             , # W 
                  motorMass         = Motor8020_mass              , # kg 
                  motorDia          = Motor8020_dia               , # mm 
                  motorLength       = Motor8020_length            ,
                  motorName         = "VT8020") 

# U12 Motor
MotorU12 = motor(maxMotorAngVelRPM = MotorU12_maxMotorAngVelRPM, 
                 maxMotorTorque    = MotorU12_maxTorque        , 
                 maxMotorPower     = MotorU12_power            ,
                 motorMass         = MotorU12_mass             , 
                 motorDia          = MotorU12_dia              , 
                 motorLength       = MotorU12_length           ,
                 motorName         = "U12")

#-------------------------------------------------------
# Gearbox
#-------------------------------------------------------
compoundPlanetaryGearboxInstance = compoundPlanetaryGearbox(design_parameters         = cpg_design_params,
                                                            gear_standard_parameters  = Gear_standard_parameters,
                                                            gearMaterialDensity       = Steel["density"],
                                                            carrierMaterialDensity    = Aluminum["density"],
                                                            maxGearAllowableStressMPa = Steel["maxAllowableStressMPa"])

#-----------------------------------------------------
# Actuator
#-----------------------------------------------------
maxGearboxDiameter_U8     = 1.5 * MotorU8.motorDiaMM     # - 2*cpg_design_params["ringRadialWidthMM"]
maxGearboxDiameter_U10    = 1.5 * MotorU10.motorDiaMM    # - 2*cpg_design_params["ringRadialWidthMM"]
maxGearboxDiameter_MN8014 = 1.5 * MotorMN8014.motorDiaMM # - 2*cpg_design_params["ringRadialWidthMM"]
maxGearboxDiameter_VT8020 = 1.5 * Motor8020.motorDiaMM   # - 2*cpg_design_params["ringRadialWidthMM"]
maxGearboxDiameter_U12    = 1.5 * MotorU12.motorDiaMM    # - 2*cpg_design_params["ringRadialWidthMM"] 

# U8-Actuator
Actuator_U8 = compoundPlanetaryActuator(design_parameters        = cpg_design_params,
                                        motor                    = MotorU8,  
                                        compoundPlanetaryGearbox = compoundPlanetaryGearboxInstance, 
                                        FOS                      = Lewis_params["FOS"], 
                                        serviceFactor            = Lewis_params["serviceFactor"], 
                                        maxGearboxDiameter       = maxGearboxDiameter_U8,
                                        stressAnalysisMethodName = "Lewis")

# U10-Actuator
Actuator_U10 = compoundPlanetaryActuator(design_parameters        = cpg_design_params,
                                         motor                    = MotorU10,  
                                         compoundPlanetaryGearbox = compoundPlanetaryGearboxInstance, 
                                         FOS                      = Lewis_params["FOS"], 
                                         serviceFactor            = Lewis_params["serviceFactor"], 
                                         maxGearboxDiameter       = maxGearboxDiameter_U10,
                                         stressAnalysisMethodName = "Lewis")

# MN8014-Actuator
Actuator_MN8014 = compoundPlanetaryActuator(design_parameters        = cpg_design_params,
                                            motor                    = MotorMN8014,  
                                            compoundPlanetaryGearbox = compoundPlanetaryGearboxInstance, 
                                            FOS                      = Lewis_params["FOS"], 
                                            serviceFactor            = Lewis_params["serviceFactor"], 
                                            maxGearboxDiameter       = maxGearboxDiameter_MN8014,
                                            stressAnalysisMethodName = "Lewis")

# VT8020-Actuator
Actuator_VT8020 = compoundPlanetaryActuator(design_parameters        = cpg_design_params,
                                            motor                    = Motor8020,  
                                            compoundPlanetaryGearbox = compoundPlanetaryGearboxInstance, 
                                            FOS                      = Lewis_params["FOS"], 
                                            serviceFactor            = Lewis_params["serviceFactor"], 
                                            maxGearboxDiameter       = maxGearboxDiameter_VT8020,
                                            stressAnalysisMethodName = "Lewis")

# U12-Actuator
Actuator_U12 = compoundPlanetaryActuator(design_parameters        = cpg_design_params,
                                         motor                    = MotorU12,  
                                         compoundPlanetaryGearbox = compoundPlanetaryGearboxInstance, 
                                         FOS                      = Lewis_params["FOS"], 
                                         serviceFactor            = Lewis_params["serviceFactor"], 
                                         maxGearboxDiameter       = maxGearboxDiameter_U12,
                                         stressAnalysisMethodName = "Lewis")

#-----------------------------------------------------
# Optimization
#-----------------------------------------------------
opt_param = config_data["Cost_gain_parameters"]

K_Mass = opt_param["K_Mass"]
K_Eff  = opt_param["K_Eff"]

GEAR_RATIO_MIN  = cpg_optimization_params["GEAR_RATIO_MIN"]  # 4
GEAR_RATIO_MAX  = cpg_optimization_params["GEAR_RATIO_MAX"]  # 30
GEAR_RATIO_STEP = cpg_optimization_params["GEAR_RATIO_STEP"] # 1

MODULE_BIG_MIN             = cpg_optimization_params["MODULE_MIN"]           # 0.8
MODULE_BIG_MAX             = cpg_optimization_params["MODULE_MAX"]           # 1.2
MODULE_SMALL_MIN           = cpg_optimization_params["MODULE_MIN"]           # 0.8
MODULE_SMALL_MAX           = cpg_optimization_params["MODULE_MAX"]           # 1.2
NUM_PLANET_MIN             = cpg_optimization_params["NUM_PLANET_MIN"]       # 3  
NUM_PLANET_MAX             = cpg_optimization_params["NUM_PLANET_MAX"]       # 5  
NUM_TEETH_SUN_MIN          = cpg_optimization_params["NUM_TEETH_SUN_MIN"]    # 20 
NUM_TEETH_PLANET_BIG_MIN   = cpg_optimization_params["NUM_TEETH_PLANET_MIN"] # 20 
NUM_TEETH_PLANET_SMALL_MIN = cpg_optimization_params["NUM_TEETH_PLANET_MIN"] # 20 

Optimizer_U8     = optimizationCompoundPlanetaryActuator(design_parameters          = cpg_design_params,
                                                         gear_standard_parameters   = Gear_standard_parameters,
                                                         K_Mass                     = K_Mass                     ,
                                                         K_Eff                      = K_Eff                      ,
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

Optimizer_U10    = optimizationCompoundPlanetaryActuator(design_parameters          = cpg_design_params,
                                                         gear_standard_parameters   = Gear_standard_parameters,
                                                         K_Mass                     = K_Mass                     ,
                                                         K_Eff                      = K_Eff                      ,
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

Optimizer_MN8014 = optimizationCompoundPlanetaryActuator(design_parameters          = cpg_design_params,
                                                         gear_standard_parameters   = Gear_standard_parameters,
                                                         K_Mass                     = K_Mass                     ,
                                                         K_Eff                      = K_Eff                      ,
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

Optimizer_VT8020 = optimizationCompoundPlanetaryActuator(design_parameters          = cpg_design_params,
                                                         gear_standard_parameters   = Gear_standard_parameters,
                                                         K_Mass                     = K_Mass                     ,
                                                         K_Eff                      = K_Eff                      ,
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

Optimizer_U12 = optimizationCompoundPlanetaryActuator(design_parameters          = cpg_design_params,
                                                      gear_standard_parameters   = Gear_standard_parameters,
                                                      K_Mass                     = K_Mass                     ,
                                                      K_Eff                      = K_Eff                      ,
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

#-------------------------------------------------
# Optimize
#-------------------------------------------------
# totalTime_U8 = Optimizer_U8.optimizeActuator(Actuator_U8, UsePSCasVariable = 1, log=0, csv=1)
# print("Optimization Completed : CPG U8 : Total Time:", totalTime_U8)

totalTime_U10 = Optimizer_U10.optimizeActuator(Actuator_U10, UsePSCasVariable = 0, log=0, csv=1)
print("Optimization Completed : CPG U10 : Total Time:", totalTime_U10)

# totalTime_MN8014 = Optimizer_MN8014.optimizeActuator(Actuator_MN8014, UsePSCasVariable = 1, log=0, csv=1)
# print("Optimization Completed : CPG MN8014 : Total Time:", totalTime_MN8014)

# totalTime_VT8020 = Optimizer_VT8020.optimizeActuator(Actuator_VT8020, UsePSCasVariable = 1, log=0, csv=1)
# print("Optimization Completed : CPG VT8020 : Total Time:", totalTime_VT8020)

# totalTime_U12 = Optimizer_U12.optimizeActuator(Actuator_U12, UsePSCasVariable = 1, log=0, csv=1)
# print("Optimization Completed : CPG U12 : Total Time:", totalTime_U12)
