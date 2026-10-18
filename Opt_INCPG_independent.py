from ActuatorAndGearbox_INCPG_independent import inrunnerCompoundPlanetaryGearbox
from ActuatorAndGearbox_INCPG_independent import inrunnerCompoundPlanetaryActuator
from ActuatorAndGearbox_INCPG_independent import optimizationInrunnerCompoundPlanetaryActuator
from CommonComponents import load_motor
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


# Load the JSON file
with open(config_path, "r") as config_file:
    config_data = json.load(config_file)

with open(incpg_params_path, "r") as incpg_independent_params_file:
    incpg_params = json.load(incpg_independent_params_file)

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

incpg_design_params       = incpg_params["incpg_3DP_design_parameters"]
incpg_optimization_params = incpg_params["incpg_optimization_parameters"]

motor_driver_data = config_data["Motor_drivers"]

#--------------------------------------------------------
# Motors Drivers
#--------------------------------------------------------
Motor_Driver_Moteus_params    = motor_driver_data["Moteus"]
Motor_Driver_OdrivePro_params = motor_driver_data["OdrivePro"]

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

#=============================================================
# run: optimise the INCPG_independent actuator for any frameless inrunner in motors.json
#=============================================================
def run(motor_name, gear_ratio):
    motor = load_motor(motor_name, motor_type="frameless_inrunner")
    maxGearboxDiameter = incpg_optimization_params["MAX_GB_DIA_MULT_FACTOR"] * motor.motorDiaMM
    inrunnerCompoundPlanetaryGearboxInstance = inrunnerCompoundPlanetaryGearbox(design_parameters         = incpg_design_params,
                                                                                gear_standard_parameters  = Gear_standard_parameters,
                                                                                densityGears              = PLA["density"],
                                                                                densityStructure          = PLA["density"],
                                                                                maxGearAllowableStressMPa = PLA["maxAllowableStressMPa"],
                                                                                densityAluminum           = Aluminum["density"])
    actuator = inrunnerCompoundPlanetaryActuator(design_parameters        = incpg_design_params,
                                                 motor                    = motor,
                                                 motor_driver_params      = Motor_Driver_OdrivePro_params,
                                                 inrunnerCompoundPlanetaryGearbox = inrunnerCompoundPlanetaryGearboxInstance,
                                                 FOS                      = MIT_params["FOS"],
                                                 serviceFactor            = MIT_params["serviceFactor"],
                                                 maxGearboxDiameter       = maxGearboxDiameter,
                                                 stressAnalysisMethodName = "MIT")
    optimizer = optimizationInrunnerCompoundPlanetaryActuator(design_parameters          = incpg_design_params,
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
    return optimizer.optimizeActuator(actuator,
                                      UsePSCasVariable = 0,
                                      log              = 0,
                                      csv              = 1,
                                      printOptParams   = 1,
                                      gearRatioReq     = gear_ratio)
