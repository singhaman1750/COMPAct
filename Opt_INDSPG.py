import os
import json
from ActuatorandGearbox_INDSPG import inrunnerdoubleStagePlanetaryGearbox
from ActuatorandGearbox_INDSPG import inrunnerdoubleStageActuator
from ActuatorandGearbox_INDSPG import optimizationDoubleStageActuator
from CommonComponents import load_motor

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

#=============================================================
# run: optimise the INDSPG actuator for any frameless inrunner in motors.json
#=============================================================
def run(motor_name, gear_ratio):
    motor = load_motor(motor_name, motor_type="frameless_inrunner")
    maxGBDia_multFactor = indspg_optimization_params["MAX_GB_DIA_MULT_FACTOR"]
    maxGearboxDiameter = (
        maxGBDia_multFactor
        * ( motor.getStator_wire_OD() - indspg_design_params["ring2RadialWidthMM"]*2 )
    )
    # Stage 1 sits inside the rotor
    maxGearboxDiameter_Stg1 = (motor.getRotorIDMM() - indspg_design_params["standard_clearance_1_5mm"]*4)
    inrunnerdoubleStagePlanetaryGearboxInstance = inrunnerdoubleStagePlanetaryGearbox(design_parameters         = indspg_design_params,
                                                                                      gear_standard_parameters  = Gear_standard_parameters,
                                                                                      densityGears              = pla["density"],
                                                                                      densityStructure          = pla["density"],
                                                                                      densityRotor              = Aluminum["density"],
                                                                                      maxGearAllowableStressMPa = pla["maxAllowableStressMPa"])
    actuator = inrunnerdoubleStageActuator(design_parameters                   = indspg_design_params,
                                           motor                               = motor,
                                           inrunnerdoubleStagePlanetaryGearbox = inrunnerdoubleStagePlanetaryGearboxInstance,
                                           FOS                                 = MIT_params["FOS"],
                                           serviceFactor                       = MIT_params["serviceFactor"],
                                           maxGearboxDiameter                  = maxGearboxDiameter,
                                           maxGearboxDiameter_Stg1             = maxGearboxDiameter_Stg1,
                                           stressAnalysisMethodName            = "MIT")
    optimizer = optimizationDoubleStageActuator(design_parameters        = indspg_design_params,
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
