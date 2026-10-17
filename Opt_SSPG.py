from ActuatorAndGearbox import singleStagePlanetaryGearbox
from ActuatorAndGearbox import singleStagePlanetaryActuator
from ActuatorAndGearbox import optimizationSingleStageActuator
from CommonComponents import load_motor, max_gearbox_dia_mult_factor
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
material_properties = config_data["Material_properties"]

Gear_standard_parameters = config_data["Gear_standard_parameters"]
Lewis_params             = config_data["Lewis_params"]
MIT_params               = config_data["MIT_params"]

Steel    = material_properties["Steel"]
Aluminum = material_properties["Aluminum"]
PLA      = material_properties["PLA"]

sspg_design_params       = sspg_params["sspg_3DP_design_parameters"]
sspg_optimization_params = sspg_params["sspg_optimization_parameters"]

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

GEAR_RATIO_MIN       = sspg_optimization_params["GEAR_RATIO_MIN"]       # 4   
GEAR_RATIO_MAX       = sspg_optimization_params["GEAR_RATIO_MAX"]       # 15 
GEAR_RATIO_STEP      = sspg_optimization_params["GEAR_RATIO_STEP"]      # 1  

MODULE_MIN           = sspg_optimization_params["MODULE_MIN"]           # 0.5 
MODULE_MAX           = sspg_optimization_params["MODULE_MAX"]           # 1.2 
NUM_PLANET_MIN       = sspg_optimization_params["NUM_PLANET_MIN"]       # 3   
NUM_PLANET_MAX       = sspg_optimization_params["NUM_PLANET_MAX"]       # 7   
NUM_TEETH_SUN_MIN    = sspg_optimization_params["NUM_TEETH_SUN_MIN"]    # 20  
NUM_TEETH_PLANET_MIN = sspg_optimization_params["NUM_TEETH_PLANET_MIN"] # 20

#=============================================================
# run: optimise the SSPG actuator for any framed motor in motors.json
#=============================================================
def run(motor_name, gear_ratio):
    motor = load_motor(motor_name)
    maxGearboxDiameter = (max_gearbox_dia_mult_factor(motor, sspg_optimization_params) * motor.motorDiaMM
                          - 2*sspg_design_params["ringRadialWidthMM"])
    planetaryGearbox = singleStagePlanetaryGearbox(design_params             = sspg_design_params,
                                                   gear_standard_parameters  = Gear_standard_parameters,
                                                   maxGearAllowableStressMPa = PLA["maxAllowableStressMPa"], # MPa
                                                   densityGears              = PLA["density"], # kg/m^3
                                                   densityStructure          = PLA["density"]) # kg/m^3
    actuator = singleStagePlanetaryActuator(design_params            = sspg_design_params,
                                            motor                    = motor,
                                            motor_driver_params      = Motor_Driver_OdrivePro_params,
                                            planetaryGearbox         = planetaryGearbox,
                                            FOS                      = MIT_params["FOS"],
                                            serviceFactor            = MIT_params["serviceFactor"],
                                            maxGearboxDiameter       = maxGearboxDiameter, # mm
                                            stressAnalysisMethodName = "MIT") # Lewis or AGMA
    optimizer = optimizationSingleStageActuator(design_params             = sspg_design_params  ,
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
