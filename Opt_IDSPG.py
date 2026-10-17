import os
import json
from ActuatorandGearbox_IDSPG import internaldoubleStagePlanetaryGearbox
from ActuatorandGearbox_IDSPG import internaldoubleStagePlanetaryActuator
from ActuatorandGearbox_IDSPG import optimizationinternalDoubleStagePlanetaryActuator
from CommonComponents import load_motor

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

#=============================================================
# run: optimise the IDSPG actuator for any frameless outrunner in motors.json
#=============================================================
def run(motor_name, gear_ratio):
    motor = load_motor(motor_name, motor_type="frameless_outrunner")
    maxGBDia_multFactor = idspg_optimization_params["MAX_GB_DIA_MULT_FACTOR"]
    maxGearboxDiameter = (
        maxGBDia_multFactor
        * ( motor.getMotorODMM() + idspg_design_params["standard_clearance_1_5mm"]*2 )      #TODO: this is corrrect and implemen in other also
    )
    # Stage 1 sits inside the stator
    maxGearboxDiameter_Stg1 = (motor.getStatorIDMM() - idspg_design_params["ring1RadialWidthMM"]*2)
    internaldoubleStagePlanetaryGearboxInstance = internaldoubleStagePlanetaryGearbox(design_parameters         = idspg_design_params,
                                                                                      gear_standard_parameters  = Gear_standard_parameters,
                                                                                      densityGears              = PLA["density"],
                                                                                      densityStructure          = PLA["density"],
                                                                                      maxGearAllowableStressMPa = PLA["maxAllowableStressMPa"])
    actuator = internaldoubleStagePlanetaryActuator(design_parameters                   = idspg_design_params,
                                                    motor                               = motor,
                                                    motor_driver_params                 = Motor_Driver_OdrivePro_params,
                                                    internaldoubleStagePlanetaryGearbox = internaldoubleStagePlanetaryGearboxInstance,
                                                    FOS                                 = MIT_params["FOS"],
                                                    serviceFactor                       = MIT_params["serviceFactor"],
                                                    maxGearboxDiameter                  = maxGearboxDiameter,
                                                    maxGearboxDiameter_Stg1             = maxGearboxDiameter_Stg1,
                                                    stressAnalysisMethodName            = "MIT")
    optimizer = optimizationinternalDoubleStagePlanetaryActuator(design_parameters        = idspg_design_params,
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
