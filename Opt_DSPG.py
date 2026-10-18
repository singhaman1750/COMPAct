from ActuatorAndGearbox import doubleStagePlanetaryGearbox
from ActuatorAndGearbox import doubleStagePlanetaryActuator
from ActuatorAndGearbox import optimizationDoubleStagePlanetaryActuator
from CommonComponents import load_motor, max_gearbox_dia_mult_factor
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
material_properties = config_data["Material_properties"]

Gear_standard_parameters = config_data["Gear_standard_parameters"]
Lewis_params             = config_data["Lewis_params"]
MIT_params               = config_data["MIT_params"]

Steel    = material_properties["Steel"]
Aluminum = material_properties["Aluminum"]
PLA      = material_properties["PLA"]

dspg_design_params       = dspg_params["dspg_design_parameters_3DP"]
dspg_optimization_params = dspg_params["dspg_optimization_parameters"]

motor_driver_data = config_data["Motor_drivers"]

#--------------------------------------------------------
# Motors Drivers
#--------------------------------------------------------
Motor_Driver_Moteus_params    = motor_driver_data["Moteus"]
Motor_Driver_OdrivePro_params = motor_driver_data["OdrivePro"]

# Optimization
opt_param = config_data["Cost_gain_parameters"]

K_Mass = opt_param["K_Mass"]
K_Eff  = opt_param["K_Eff"]
K_Width  = opt_param["K_Width"]

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

#=============================================================
# run: optimise the DSPG actuator for any framed motor in motors.json
#=============================================================
def run(motor_name, gear_ratio):
    motor = load_motor(motor_name, motor_type="framed_outrunner")
    maxGearboxDiameter = motor.motorDiaMM * max_gearbox_dia_mult_factor(motor, dspg_optimization_params) - 2*dspg_design_params["ring_radial_thickness"]
    doubleStagePlanetaryGearboxInstance = doubleStagePlanetaryGearbox(design_parameters         = dspg_design_params,
                                                                      gear_standard_parameters  = Gear_standard_parameters,
                                                                      densityGears              = PLA["density"],
                                                                      densityStructure          = PLA["density"],
                                                                      maxGearAllowableStressMPa = PLA["maxAllowableStressMPa"])
    actuator = doubleStagePlanetaryActuator(design_parameters           = dspg_design_params,
                                            motor                       = motor,
                                            motor_driver_params         = Motor_Driver_OdrivePro_params,
                                            doubleStagePlanetaryGearbox = doubleStagePlanetaryGearboxInstance,
                                            FOS                         = MIT_params["FOS"],
                                            serviceFactor               = MIT_params["serviceFactor"],
                                            maxGearboxDiameter          = maxGearboxDiameter,
                                            stressAnalysisMethodName    = "MIT")
    optimizer = optimizationDoubleStagePlanetaryActuator(design_parameters        = dspg_design_params,
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
                                                         GEAR_RATIO_STEP          = GEAR_RATIO_STEP       )
    return optimizer.optimizeActuator(actuator,
                                      UsePSCasVariable = 0,
                                      log              = 0,
                                      csv              = 1,
                                      printOptParams   = 1,
                                      gearRatioReq     = gear_ratio)
