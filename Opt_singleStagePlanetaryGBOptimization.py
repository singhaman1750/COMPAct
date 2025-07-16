import sys
import numpy as np
from ActuatorAndGearbox import singleStagePlanetaryGearbox
from ActuatorAndGearbox import motor
from ActuatorAndGearbox import singleStagePlanetaryActuator
from ActuatorAndGearbox import optimizationSingleStageActuator
import json
import os

#--------------------------------------------------------
# Importing Config data
#--------------------------------------------------------
# Get the current directory
current_dir = os.path.dirname(__file__)

# Build the file path
config_path      = os.path.join(current_dir, "config_files/config.json")
sspg_params_path = os.path.join(current_dir, "config_files/sspg_params.json")

# Load the JSON file
with open(config_path, "r") as config_file:
    config_data = json.load(config_file)

with open(sspg_params_path, "r") as sspg_params_file:
    sspg_params = json.load(sspg_params_file)

#---------------------------------------------------
# Transferring relevant data to individual variables
#---------------------------------------------------
motor_data          = config_data["Motors"]
material_properties = config_data["Material_properties"]

Gear_standard_parameters = config_data["Gear_standard_parameters"]
Lewis_params             = config_data["Lewis_params"]
MIT_params               = config_data["MIT_params"]

Steel               = material_properties["Steel"]
Aluminum            = material_properties["Aluminum"]
PLA                 = material_properties["PLA"]

sspg_design_params       = sspg_params["sspg_3DP_design_parameters"]
sspg_optimization_params = sspg_params["sspg_optimization_parameters"]

#--------------------------------------------------------
# Motors
#--------------------------------------------------------
# T motor U8
MotorU8_maxTorque         = motor_data["MotorU8_framed"]["maxTorque"]             # Nm
MotorU8_power             = motor_data["MotorU8_framed"]["power"]                 # W 
MotorU8_maxMotorAngVelRPM = (MotorU8_power * 60) / (MotorU8_maxTorque * 2*np.pi) # RPM 
MotorU8_mass              = motor_data["MotorU8_framed"]["mass"]                  # kg 
MotorU8_dia               = motor_data["MotorU8_framed"]["dia"]                   # mm 
MotorU8_length            = motor_data["MotorU8_framed"]["length"]                # mm

# U10 Motor
MotorU10_maxTorque                  = motor_data["MotorU10_framed"]["maxTorque"]              # Nm
MotorU10_power                      = motor_data["MotorU10_framed"]["power"]                  # W
MotorU10_maxMotorAngVelRPM          = (MotorU10_power * 60) / (MotorU10_maxTorque * 2*np.pi)  # RPM
MotorU10_mass                       = motor_data["MotorU10_framed"]["mass"]                   # Kg 
MotorU10_dia                        = motor_data["MotorU10_framed"]["dia"]                    # mm
MotorU10_length                     = motor_data["MotorU10_framed"]["length"]                 # mm
MotorU10_motor_mount_hole_PCD       = motor_data["MotorU10_framed"]["motor_mount_hole_PCD"]
MotorU10_motor_mount_hole_dia       = motor_data["MotorU10_framed"]["motor_mount_hole_dia"]
MotorU10_motor_mount_hole_num       = motor_data["MotorU10_framed"]["motor_mount_hole_num"]
MotorU10_motor_output_hole_PCD      = motor_data["MotorU10_framed"]["motor_output_hole_PCD"]
MotorU10_motor_output_hole_dia      = motor_data["MotorU10_framed"]["motor_output_hole_dia"]
MotorU10_motor_output_hole_num      = motor_data["MotorU10_framed"]["motor_output_hole_num"]
MotorU10_wire_slot_dist_from_center = motor_data["MotorU10_framed"]["wire_slot_dist_from_center"]
MotorU10_wire_slot_length           = motor_data["MotorU10_framed"]["wire_slot_length"]
MotorU10_wire_slot_radius           = motor_data["MotorU10_framed"]["wire_slot_radius"]

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

# T motor U12
MotorU12_maxTorque         = motor_data["MotorU12_framed"]["maxTorque"]             # Nm
MotorU12_power             = motor_data["MotorU12_framed"]["power"]                 # W 
MotorU12_maxMotorAngVelRPM = (MotorU12_power * 60) / (MotorU12_maxTorque * 2*np.pi) # RPM 
MotorU12_mass              = motor_data["MotorU12_framed"]["mass"]                  # kg 
MotorU12_dia               = motor_data["MotorU12_framed"]["dia"]                   # mm 
MotorU12_length            = motor_data["MotorU12_framed"]["length"]                # mm

# MaxonIR
MotorMaxonIR_maxTorque         = motor_data["MotorMaxonIR_framed"]["maxTorque"]             # Nm
MotorMaxonIR_power             = motor_data["MotorMaxonIR_framed"]["power"]                 # W 
MotorMaxonIR_maxMotorAngVelRPM = (MotorMaxonIR_power * 60) / (MotorMaxonIR_maxTorque * 2*np.pi) # RPM 
MotorMaxonIR_mass              = motor_data["MotorMaxonIR_framed"]["mass"]                  # kg 
MotorMaxonIR_dia               = motor_data["MotorMaxonIR_framed"]["dia"]                   # mm 
MotorMaxonIR_length            = motor_data["MotorMaxonIR_framed"]["length"]                # mm

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
                    maxMotorTorque    = MotorMN8014_maxTorque      , # Nm 
                    maxMotorPower     = MotorMN8014_power          , # W 
                    motorMass         = MotorMN8014_mass           , # kg 
                    motorDia          = MotorMN8014_dia            , # mm 
                    motorLength       = MotorMN8014_length         ,     
                    motorName         = "MN8014") 

# Motor-VT8020
Motor8020 = motor(maxMotorAngVelRPM = Motor8020_maxMotorAngVelRPM, # RPM 
                  maxMotorTorque    = Motor8020_maxTorque        , # Nm 
                  maxMotorPower     = Motor8020_power            , # W 
                  motorMass         = Motor8020_mass             , # kg 
                  motorDia          = Motor8020_dia              , # mm 
                  motorLength       = Motor8020_length           ,     
                  motorName         = "VT8020")

# Motor-U12
MotorU12 = motor(maxMotorAngVelRPM = MotorU12_maxMotorAngVelRPM,
                 maxMotorTorque    = MotorU12_maxTorque        ,
                 maxMotorPower     = MotorU12_power            ,
                 motorMass         = MotorU12_mass             , 
                 motorDia          = MotorU12_dia              ,
                 motorLength       = MotorU12_length           ,
                 motorName         = "U12")

MotorMaxonIR = motor(maxMotorAngVelRPM = MotorMaxonIR_maxMotorAngVelRPM,
                 maxMotorTorque        = MotorMaxonIR_maxTorque,
                 maxMotorPower         = MotorMaxonIR_power,
                 motorMass             = MotorMaxonIR_mass, 
                 motorDia              = MotorMaxonIR_dia,
                 motorLength           = MotorMaxonIR_length,
                 motorName             = "MaxonIR")

#--------------------------------------------------------
# Gearboxes 
#--------------------------------------------------------
PlanetaryGearbox = singleStagePlanetaryGearbox(design_params             = sspg_design_params,
                                               gear_standard_parameters  = Gear_standard_parameters,
                                               maxGearAllowableStressMPa = PLA["maxAllowableStressMPa"], # MPa
                                               densityGears              = PLA["density"],    # kg/m^3
                                               densityCarrier            = Aluminum["density"], # kg/m^3
                                               densityStructure          = Aluminum["density"]) # kg/m^3

#--------------------------------------------------------
# Actuators
#--------------------------------------------------------
maxGearboxDiameter_U8      = MotorU8.motorDiaMM - 2*sspg_design_params["ringRadialWidthMM"] 
maxGearboxDiameter_U10     = MotorU10.motorDiaMM - 2*sspg_design_params["ringRadialWidthMM"] 
maxGearboxDiameter_MN8014  = MotorMN8014.motorDiaMM - 2*sspg_design_params["ringRadialWidthMM"] 
maxGearboxDiameter_VT8020  = Motor8020.motorDiaMM - 2*sspg_design_params["ringRadialWidthMM"]
maxGearboxDiameter_U12     = MotorU12.motorDiaMM - 2*sspg_design_params["ringRadialWidthMM"] 

# U8-Actuator
Actuator_U8    = singleStagePlanetaryActuator(design_params            = sspg_design_params,
                                               motor                    = MotorU8,
                                               planetaryGearbox         = PlanetaryGearbox,
                                               FOS                      = MIT_params["FOS"],
                                               serviceFactor            = MIT_params["serviceFactor"],
                                               maxGearboxDiameter       = maxGearboxDiameter_U8, # mm 
                                               stressAnalysisMethodName = "MIT") # Lewis or AGMA

# U10-Actuator
Actuator_U10    = singleStagePlanetaryActuator(design_params            = sspg_design_params,
                                               motor                    = MotorU10,
                                               planetaryGearbox         = PlanetaryGearbox,
                                               FOS                      = MIT_params["FOS"],
                                               serviceFactor            = MIT_params["serviceFactor"],
                                               maxGearboxDiameter       = maxGearboxDiameter_U10, # mm 
                                               stressAnalysisMethodName = "MIT") # Lewis or AGMA

# MN8014-Actuator
Actuator_MN8014 = singleStagePlanetaryActuator(design_params            = sspg_design_params,
                                               motor                    = MotorMN8014, 
                                               planetaryGearbox         = PlanetaryGearbox, 
                                               FOS                      = MIT_params["FOS"], 
                                               serviceFactor            = MIT_params["serviceFactor"], 
                                               maxGearboxDiameter       = maxGearboxDiameter_MN8014, # mm 
                                               stressAnalysisMethodName = "MIT") # Lewis or AGMA

# VT8020-Actuator
Actuator_VT8020 = singleStagePlanetaryActuator(design_params            = sspg_design_params,
                                               motor                    = Motor8020, 
                                               planetaryGearbox         = PlanetaryGearbox, 
                                               FOS                      = MIT_params["FOS"], 
                                               serviceFactor            = MIT_params["serviceFactor"], 
                                               maxGearboxDiameter       = maxGearboxDiameter_VT8020, # mm 
                                               stressAnalysisMethodName = "MIT") # Lewis or AGMA

# U12-Actuator
Actuator_U12 = singleStagePlanetaryActuator(design_params            = sspg_design_params,
                                            motor                    = MotorU12, 
                                            planetaryGearbox         = PlanetaryGearbox, 
                                            FOS                      = MIT_params["FOS"], 
                                            serviceFactor            = MIT_params["serviceFactor"], 
                                            maxGearboxDiameter       = maxGearboxDiameter_U12, # mm 
                                            stressAnalysisMethodName = "MIT") # Lewis or AGMA

#--------------------------------------------------------
# Optimization
#--------------------------------------------------------
cost_gains = config_data["Cost_gain_parameters"]

K_Mass = 1 # cost_gains["K_Mass"]
K_Eff  = 0 # cost_gains["K_Eff"]

GEAR_RATIO_MIN       = sspg_optimization_params["GEAR_RATIO_MIN"]       # 4   
GEAR_RATIO_MAX       = sspg_optimization_params["GEAR_RATIO_MAX"]       # 15 
GEAR_RATIO_STEP      = sspg_optimization_params["GEAR_RATIO_STEP"]      # 1  
MODULE_MIN           = sspg_optimization_params["MODULE_MIN"]           # 0.5 
MODULE_MAX           = sspg_optimization_params["MODULE_MAX"]           # 1.2 
NUM_PLANET_MIN       = sspg_optimization_params["NUM_PLANET_MIN"]       # 3   
NUM_PLANET_MAX       = sspg_optimization_params["NUM_PLANET_MAX"]       # 7   
NUM_TEETH_SUN_MIN    = sspg_optimization_params["NUM_TEETH_SUN_MIN"]    # 20  
NUM_TEETH_PLANET_MIN = sspg_optimization_params["NUM_TEETH_PLANET_MIN"] # 20

Optimizer_U8     = optimizationSingleStageActuator(design_params        = sspg_design_params  ,
                                                   gear_standard_paramaeters = Gear_standard_parameters,
                                                   K_Mass               = K_Mass              ,
                                                   K_Eff                = K_Eff               ,
                                                   MODULE_MIN           = MODULE_MIN          ,
                                                   MODULE_MAX           = MODULE_MAX          ,
                                                   NUM_PLANET_MIN       = NUM_PLANET_MIN      ,
                                                   NUM_PLANET_MAX       = NUM_PLANET_MAX      ,
                                                   NUM_TEETH_SUN_MIN    = NUM_TEETH_SUN_MIN   ,
                                                   NUM_TEETH_PLANET_MIN = NUM_TEETH_PLANET_MIN,
                                                   GEAR_RATIO_MIN       = GEAR_RATIO_MIN      ,
                                                   GEAR_RATIO_MAX       = GEAR_RATIO_MAX      ,
                                                   GEAR_RATIO_STEP      = GEAR_RATIO_STEP     )

Optimizer_U10    = optimizationSingleStageActuator(design_params        = sspg_design_params  ,
                                                   gear_standard_paramaeters = Gear_standard_parameters,
                                                   K_Mass               = K_Mass              ,
                                                   K_Eff                = K_Eff               ,
                                                   MODULE_MIN           = MODULE_MIN          ,
                                                   MODULE_MAX           = MODULE_MAX          ,
                                                   NUM_PLANET_MIN       = NUM_PLANET_MIN      ,
                                                   NUM_PLANET_MAX       = NUM_PLANET_MAX      ,
                                                   NUM_TEETH_SUN_MIN    = NUM_TEETH_SUN_MIN   ,
                                                   NUM_TEETH_PLANET_MIN = NUM_TEETH_PLANET_MIN,
                                                   GEAR_RATIO_MIN       = GEAR_RATIO_MIN      ,
                                                   GEAR_RATIO_MAX       = GEAR_RATIO_MAX      ,
                                                   GEAR_RATIO_STEP      = GEAR_RATIO_STEP     )

Optimizer_MN8014 = optimizationSingleStageActuator(design_params        = sspg_design_params  ,
                                                   gear_standard_paramaeters = Gear_standard_parameters,
                                                   K_Mass               = K_Mass              ,
                                                   K_Eff                = K_Eff               ,
                                                   MODULE_MIN           = MODULE_MIN          ,
                                                   MODULE_MAX           = MODULE_MAX          ,
                                                   NUM_PLANET_MIN       = NUM_PLANET_MIN      ,
                                                   NUM_PLANET_MAX       = NUM_PLANET_MAX      ,
                                                   NUM_TEETH_SUN_MIN    = NUM_TEETH_SUN_MIN   ,
                                                   NUM_TEETH_PLANET_MIN = NUM_TEETH_PLANET_MIN,
                                                   GEAR_RATIO_MIN       = GEAR_RATIO_MIN      ,
                                                   GEAR_RATIO_MAX       = GEAR_RATIO_MAX      ,
                                                   GEAR_RATIO_STEP      = GEAR_RATIO_STEP     )

Optimizer_VT8020 = optimizationSingleStageActuator(design_params        = sspg_design_params  ,
                                                   gear_standard_paramaeters = Gear_standard_parameters,
                                                   K_Mass               = K_Mass              ,
                                                   K_Eff                = K_Eff               ,
                                                   MODULE_MIN           = MODULE_MIN          ,
                                                   MODULE_MAX           = MODULE_MAX          ,
                                                   NUM_PLANET_MIN       = NUM_PLANET_MIN      ,
                                                   NUM_PLANET_MAX       = NUM_PLANET_MAX      ,
                                                   NUM_TEETH_SUN_MIN    = NUM_TEETH_SUN_MIN   ,
                                                   NUM_TEETH_PLANET_MIN = NUM_TEETH_PLANET_MIN,
                                                   GEAR_RATIO_MIN       = GEAR_RATIO_MIN      ,
                                                   GEAR_RATIO_MAX       = GEAR_RATIO_MAX      ,
                                                   GEAR_RATIO_STEP      = GEAR_RATIO_STEP     )

Optimizer_U12 = optimizationSingleStageActuator(design_params        = sspg_design_params  ,
                                                gear_standard_paramaeters = Gear_standard_parameters,
                                                K_Mass               = K_Mass              ,
                                                K_Eff                = K_Eff               ,
                                                MODULE_MIN           = MODULE_MIN          ,
                                                MODULE_MAX           = MODULE_MAX          ,
                                                NUM_PLANET_MIN       = NUM_PLANET_MIN      ,
                                                NUM_PLANET_MAX       = NUM_PLANET_MAX      ,
                                                NUM_TEETH_SUN_MIN    = NUM_TEETH_SUN_MIN   ,
                                                NUM_TEETH_PLANET_MIN = NUM_TEETH_PLANET_MIN,
                                                GEAR_RATIO_MIN       = GEAR_RATIO_MIN      ,
                                                GEAR_RATIO_MAX       = GEAR_RATIO_MAX      ,
                                                GEAR_RATIO_STEP      = GEAR_RATIO_STEP     )

# U8
totalTime_U8 = Optimizer_U8.optimizeActuator(Actuator_U8, UsePSCasVariable = 0, log=0, csv=1)
print("Optimization Completed : U8 SSPG : Time taken:", totalTime_U8, " sec")
# 
# U10
# totalTime_U10 = Optimizer_U10.optimizeActuator(Actuator_U10, UsePSCasVariable = 0, log=0, csv=1)
# print("Optimization Completed : U10 SSPG : Time taken:", totalTime_U10, " sec")
# 
# MN8014
# totalTime_MN8014 = Optimizer_MN8014.optimizeActuator(Actuator_MN8014, UsePSCasVariable = 1, log=0, csv=1)
# print("Optimization Completed : MN8014 SSPG : Time taken:", totalTime_MN8014, " sec")

# VT8020
# totalTime_VT8020 = Optimizer_VT8020.optimizeActuator(Actuator_VT8020, UsePSCasVariable = 1, log=0, csv=1)
# print("Optimization Completed : VT8020 SSPG : Time taken:", totalTime_VT8020, " sec")

# U12
# totalTime_U12 = Optimizer_U12.optimizeActuator(Actuator_U12, UsePSCasVariable = 1, log=0, csv=1)
# print("Optimization Completed : U12 SSPG : Time taken:", totalTime_U12, " sec")

# MaxonIR
# totalTime_MaxonIR = Optimizer_MaxonIR.optimizeActuator(Actuator_MaxonIR, UsePSCasVariable = 1, log=0, csv=1)
# print("Optimization Completed : MaxonIR SSPG : Time taken:", totalTime_MaxonIR, " sec")

