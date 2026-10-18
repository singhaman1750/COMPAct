from ActuatorAndGearbox_ISSPG_compact import internalsingleStagePlanetaryGearbox
from ActuatorAndGearbox_ISSPG_compact import internalsingleStagePlanetaryActuator
from ActuatorAndGearbox_ISSPG_compact import optimizationInternalSingleStageActuator
from CommonComponents import load_motor
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

#=============================================================
# run: optimise the ISSPG (compact) actuator for any frameless outrunner in motors.json
#=============================================================
def run(motor_name, gear_ratio):
    motor = load_motor(motor_name, motor_type="frameless_outrunner")
    planetaryGearbox = internalsingleStagePlanetaryGearbox(design_params             = isspg_design_params,
                                                           gear_standard_parameters  = Gear_standard_parameters,
                                                           maxGearAllowableStressMPa = PLA["maxAllowableStressMPa"], # MPa
                                                           densityGears              = PLA["density"], # kg/m^3
                                                           densityStructure          = PLA["density"]) # kg/m^3
    actuator = internalsingleStagePlanetaryActuator(design_params            = isspg_design_params,
                                                    motor                    = motor,
                                                    motor_driver_params      = Motor_Driver_OdrivePro_params,
                                                    planetaryGearbox         = planetaryGearbox,
                                                    FOS                      = 1.2,
                                                    serviceFactor            = 1.5,
                                                    stressAnalysisMethodName = "MIT") # Lewis or AGMA
    optimizer = optimizationInternalSingleStageActuator(design_params             = isspg_design_params ,
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
    return optimizer.optimizeActuator(actuator,
                                      UsePSCasVariable = 0,
                                      log              = 0,
                                      csv              = 1,
                                      printOptParams   = 1,
                                      gearRatioReq     = gear_ratio)
