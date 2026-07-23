import sys
import numpy as np
from ActuatorandGearbox_ICPG import motor
from ActuatorandGearbox_ICPG import material
from ActuatorandGearbox_ICPG import internalcompoundPlanetaryGearbox
from ActuatorandGearbox_ICPG import internalcompoundPlanetaryActuator
from ActuatorandGearbox_ICPG import optimizationInternalCompoundPlanetaryActuator
import os
import json

#--------------------------------------------------------
# Importing motor data
#--------------------------------------------------------
# Get the current directory
current_dir = os.path.dirname(__file__)

# Build the file path
config_path = os.path.join(current_dir, "config_files/motor_config.json")
cpg_params_path = os.path.join(current_dir, "config_files/icpg_params.json")

# Load the JSON file
with open(config_path, "r") as motor_config_file:
    config_data = json.load(motor_config_file)

with open(cpg_params_path, "r") as icpg_params_file:
    cpg_params = json.load(icpg_params_file)

#---------------------------------------------------
# Transferring relevant data to individual variables
#---------------------------------------------------
motor_data          = config_data["Motors"]
material_properties = config_data["Material_properties"]

Gear_standard_parameters = config_data["Gear_standard_parameters"]
Lewis_params             = config_data["Lewis_params"]
MIT_params               = config_data["MIT_params"]

Steel    = material_properties["Steel"]
Aluminum = material_properties["Aluminum"]
PLA      = material_properties["PLA"]

cpg_design_params       = cpg_params["cpg_3DP_design_parameters"]
cpg_optimization_params = cpg_params["cpg_optimization_parameters"]

#motor_driver_data = config_data["Motor_drivers"]

#--------------------------------------------------------
# Motors Drivers
#--------------------------------------------------------
#Motor_Driver_Moteus_params    = motor_driver_data["Moteus"]
#Motor_Driver_OdrivePro_params = motor_driver_data["OdrivePro"]

#--------------------------------------------------------
# Motors
#--------------------------------------------------------

# =====================================================
# Motor RO100
# =====================================================

MotorRO100_Kv                   = motor_data["MotorRO100"]["Kv"]
MotorRO100_maxContinuousCurrent = motor_data["MotorRO100"]["maxContinuousCurrent"]

MotorRO100_maxTorque = (
    MotorRO100_maxContinuousCurrent
    /
    (MotorRO100_Kv * 2 * np.pi / 60)
)

MotorRO100_power                = motor_data["MotorRO100"]["power"]
MotorRO100_ratedVoltage         = motor_data["MotorRO100"]["ratedVoltage"]

MotorRO100_maxMotorAngVelRPM    = (
    MotorRO100_Kv
    * MotorRO100_ratedVoltage
)

MotorRO100_massKG              = motor_data["MotorRO100"]["massKG"]

MotorRO100_statorODMM          = motor_data["MotorRO100"]["statorODMM"]
MotorRO100_statorIDMM          = motor_data["MotorRO100"]["statorIDMM"]
MotorRO100_statorHeightMM      = motor_data["MotorRO100"]["statorHeightMM"]

MotorRO100_rotorODMM           = motor_data["MotorRO100"]["rotorODMM"]
MotorRO100_rotorIDMM           = motor_data["MotorRO100"]["rotorIDMM"]
MotorRO100_rotorHeightMM       = motor_data["MotorRO100"]["rotorHeightMM"]

MotorRO100_statorMountingHolesPCDMM = motor_data["MotorRO100"]["statorMountingHolesPCDMM"]

MotorRO100_rotorBottomIDMM         = motor_data["MotorRO100"]["rotorBottomIDMM"]
MotorRO100_rotorBottomThicknessMM  = motor_data["MotorRO100"]["rotorBottomThicknessMM"]

MotorRO100_rotorCSKHeadUpperDiaMM  = motor_data["MotorRO100"]["rotorCSKHeadUpperDiaMM"]

MotorRO100_rotorMountHolePCDMM     = motor_data["MotorRO100"]["rotorMountHolePCDMM"]
MotorRO100_rotorMountHoleDiaMM     = motor_data["MotorRO100"]["rotorMountHoleDiaMM"]

MotorRO100_motor_height                   = motor_data["MotorRO100"]["motor_height"]
MotorRO100_motor_stator_extrusion_dia        = motor_data["MotorRO100"]["motor_stator_extrusion_dia"]
MotorRO100_motor_stator_extrusion_depth      = motor_data["MotorRO100"]["motor_stator_extrusion_depth"]
MotorRO100_stator_top_rotor_top_offset      = motor_data["MotorRO100"]["stator_top_rotor_top_offset"]
# =====================================================
# Motor RO80
# =====================================================

MotorRO80_Kv                   = motor_data["MotorRO80"]["Kv"]
MotorRO80_maxContinuousCurrent = motor_data["MotorRO80"]["maxContinuousCurrent"]

MotorRO80_maxTorque = (
    MotorRO80_maxContinuousCurrent
    /
    (MotorRO80_Kv * 2 * np.pi / 60)
)

MotorRO80_power                = motor_data["MotorRO80"]["power"]
MotorRO80_ratedVoltage         = motor_data["MotorRO80"]["ratedVoltage"]

MotorRO80_maxMotorAngVelRPM    = (
    MotorRO80_Kv
    * MotorRO80_ratedVoltage
)

MotorRO80_massKG              = motor_data["MotorRO80"]["massKG"]

MotorRO80_statorODMM          = motor_data["MotorRO80"]["statorODMM"]
MotorRO80_statorIDMM          = motor_data["MotorRO80"]["statorIDMM"]
MotorRO80_statorHeightMM      = motor_data["MotorRO80"]["statorHeightMM"]

MotorRO80_rotorODMM           = motor_data["MotorRO80"]["rotorODMM"]
MotorRO80_rotorIDMM           = motor_data["MotorRO80"]["rotorIDMM"]
MotorRO80_rotorHeightMM       = motor_data["MotorRO80"]["rotorHeightMM"]

MotorRO80_statorMountingHolesPCDMM = motor_data["MotorRO80"]["statorMountingHolesPCDMM"]

MotorRO80_rotorBottomIDMM         = motor_data["MotorRO80"]["rotorBottomIDMM"]
MotorRO80_rotorBottomThicknessMM  = motor_data["MotorRO80"]["rotorBottomThicknessMM"]

MotorRO80_rotorCSKHeadUpperDiaMM  = motor_data["MotorRO80"]["rotorCSKHeadUpperDiaMM"]

MotorRO80_rotorMountHolePCDMM     = motor_data["MotorRO80"]["rotorMountHolePCDMM"]
MotorRO80_rotorMountHoleDiaMM     = motor_data["MotorRO80"]["rotorMountHoleDiaMM"]

MotorRO80_motor_height                   = motor_data["MotorRO80"]["motor_height"]
MotorRO80_motor_stator_extrusion_dia        = motor_data["MotorRO80"]["motor_stator_extrusion_dia"]
MotorRO80_motor_stator_extrusion_depth      = motor_data["MotorRO80"]["motor_stator_extrusion_depth"]
MotorRO80_stator_top_rotor_top_offset      = motor_data["MotorRO80"]["stator_top_rotor_top_offset"]

# =====================================================
# Motor - RO100
# =====================================================


MotorRO100 = motor(
    maxMotorAngVelRPM        = MotorRO100_maxMotorAngVelRPM,
    maxMotorTorque           = MotorRO100_maxTorque,
    maxMotorPower            = MotorRO100_power,

    motorMass                = MotorRO100_massKG,

    stator_OD                = MotorRO100_statorODMM,
    stator_ID                = MotorRO100_statorIDMM,
    stator_height            = MotorRO100_statorHeightMM,

    stator_hole_PCD          = MotorRO100_statorMountingHolesPCDMM,

    motor_OD                 = MotorRO100_rotorODMM,
    rotor_ID                 = MotorRO100_rotorIDMM,
    rotor_height             = MotorRO100_rotorHeightMM,

    motor_rotor_base_ID      = MotorRO100_rotorBottomIDMM,
    motor_rotor_base_thickness = MotorRO100_rotorBottomThicknessMM,

    rotorCSKHeadUpperDiaMM   = MotorRO100_rotorCSKHeadUpperDiaMM,

    motor_rotor_hole_PCD     = MotorRO100_rotorMountHolePCDMM,
    motor_rotor_hole_dia     = MotorRO100_rotorMountHoleDiaMM,

    motor_stator_extrusion_dia   =  MotorRO100_motor_stator_extrusion_dia ,
    motor_stator_extrusion_depth =  MotorRO100_motor_stator_extrusion_depth , 
    stator_top_rotor_top_offset  =  MotorRO100_stator_top_rotor_top_offset ,

    motor_height                    = MotorRO100_motor_height,

    motorName                = "RO100"
)


# =====================================================
# Motor - RO80
# =====================================================

MotorRO80 = motor(
    maxMotorAngVelRPM        = MotorRO80_maxMotorAngVelRPM,
    maxMotorTorque           = MotorRO80_maxTorque,
    maxMotorPower            = MotorRO80_power,

    motorMass                = MotorRO80_massKG,

    stator_OD                = MotorRO80_statorODMM,
    stator_ID                = MotorRO80_statorIDMM,
    stator_height            = MotorRO80_statorHeightMM,

    stator_hole_PCD          = MotorRO80_statorMountingHolesPCDMM,

    motor_OD                 = MotorRO80_rotorODMM,
    rotor_ID                 = MotorRO80_rotorIDMM,
    rotor_height             = MotorRO80_rotorHeightMM,

    motor_rotor_base_ID      = MotorRO80_rotorBottomIDMM,
    motor_rotor_base_thickness = MotorRO80_rotorBottomThicknessMM,

    rotorCSKHeadUpperDiaMM   = MotorRO80_rotorCSKHeadUpperDiaMM,

    motor_rotor_hole_PCD     = MotorRO80_rotorMountHolePCDMM,
    motor_rotor_hole_dia     = MotorRO80_rotorMountHoleDiaMM,

    motor_stator_extrusion_dia   =  MotorRO80_motor_stator_extrusion_dia ,
    motor_stator_extrusion_depth =  MotorRO80_motor_stator_extrusion_depth ,  
    stator_top_rotor_top_offset  =  MotorRO80_stator_top_rotor_top_offset ,

    motor_height                    = MotorRO80_motor_height,

    motorName                = "RO80"
)
#-------------------------------------------------------
# Gearbox 
#-------------------------------------------------------
internalcompoundPlanetaryGearboxInstance = internalcompoundPlanetaryGearbox(design_parameters         = cpg_design_params,
                                                            gear_standard_parameters  = Gear_standard_parameters,
                                                            densityGears              = PLA["density"],
                                                            densityStructure          = PLA["density"],
                                                            maxGearAllowableStressMPa = PLA["maxAllowableStressMPa"])

#-----------------------------------------------------
# Actuator
#-----------------------------------------------------

maxGBDia_multFactor = cpg_optimization_params["MAX_GB_DIA_MULT_FACTOR"]

# Internal Gearbox Packaging Limits
maxGearboxDiameter_RO80  = (
    maxGBDia_multFactor
    * MotorRO80.getStatorIDMM()
)

maxGearboxDiameter_RO100 = (
    maxGBDia_multFactor
    * MotorRO100.getStatorIDMM()
)


#-----------------------------------------------------
# RO80 Actuator
#-----------------------------------------------------

Actuator_RO80 = internalcompoundPlanetaryActuator(
    design_parameters        = cpg_design_params,
    motor                    = MotorRO80,
    #motor_driver_params      = Motor_Driver_OdrivePro_params,
    internalcompoundPlanetaryGearbox=internalcompoundPlanetaryGearboxInstance,
    FOS                      = MIT_params["FOS"],
    serviceFactor            = MIT_params["serviceFactor"],

    maxGearboxDiameter       = maxGearboxDiameter_RO80,

    stressAnalysisMethodName = "MIT"
)


#-----------------------------------------------------
# RO100 Actuator
#-----------------------------------------------------

Actuator_RO100 = internalcompoundPlanetaryActuator(
    design_parameters        = cpg_design_params,
    motor                    = MotorRO100,
    #motor_driver_params      = Motor_Driver_OdrivePro_params,
     internalcompoundPlanetaryGearbox=internalcompoundPlanetaryGearboxInstance,

    FOS                      = MIT_params["FOS"],
    serviceFactor            = MIT_params["serviceFactor"],

    maxGearboxDiameter       = maxGearboxDiameter_RO100,

    stressAnalysisMethodName = "MIT"
)

#-----------------------------------------------------
# Optimization
#-----------------------------------------------------
opt_param = config_data["Cost_gain_parameters"]

K_Mass = opt_param["K_Mass"]
K_Eff  = opt_param["K_Eff"]
K_Width = opt_param["K_Width"]

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

#-----------------------------------------------------
# RO80 Optimizer
#-----------------------------------------------------

Optimizer_RO80 = optimizationInternalCompoundPlanetaryActuator(
    design_parameters          = cpg_design_params,
    gear_standard_parameters   = Gear_standard_parameters,

    K_Mass                     = K_Mass,
    K_Eff                      = K_Eff,
    K_Width                    = K_Width,

    MODULE_BIG_MIN             = MODULE_BIG_MIN,
    MODULE_BIG_MAX             = MODULE_BIG_MAX,

    MODULE_SMALL_MIN           = MODULE_SMALL_MIN,
    MODULE_SMALL_MAX           = MODULE_SMALL_MAX,

    NUM_PLANET_MIN             = NUM_PLANET_MIN,
    NUM_PLANET_MAX             = NUM_PLANET_MAX,

    NUM_TEETH_SUN_MIN          = NUM_TEETH_SUN_MIN,
    NUM_TEETH_PLANET_BIG_MIN   = NUM_TEETH_PLANET_BIG_MIN,
    NUM_TEETH_PLANET_SMALL_MIN = NUM_TEETH_PLANET_SMALL_MIN,

    GEAR_RATIO_MIN             = GEAR_RATIO_MIN,
    GEAR_RATIO_MAX             = GEAR_RATIO_MAX,
    GEAR_RATIO_STEP            = GEAR_RATIO_STEP
)


#-----------------------------------------------------
# RO100 Optimizer
#-----------------------------------------------------

Optimizer_RO100 = optimizationInternalCompoundPlanetaryActuator(
    design_parameters          = cpg_design_params,
    gear_standard_parameters   = Gear_standard_parameters,

    K_Mass                     = K_Mass,
    K_Eff                      = K_Eff,
    K_Width                    = K_Width,

    MODULE_BIG_MIN             = MODULE_BIG_MIN,
    MODULE_BIG_MAX             = MODULE_BIG_MAX,

    MODULE_SMALL_MIN           = MODULE_SMALL_MIN,
    MODULE_SMALL_MAX           = MODULE_SMALL_MAX,

    NUM_PLANET_MIN             = NUM_PLANET_MIN,
    NUM_PLANET_MAX             = NUM_PLANET_MAX,

    NUM_TEETH_SUN_MIN          = NUM_TEETH_SUN_MIN,
    NUM_TEETH_PLANET_BIG_MIN   = NUM_TEETH_PLANET_BIG_MIN,
    NUM_TEETH_PLANET_SMALL_MIN = NUM_TEETH_PLANET_SMALL_MIN,

    GEAR_RATIO_MIN             = GEAR_RATIO_MIN,
    GEAR_RATIO_MAX             = GEAR_RATIO_MAX,
    GEAR_RATIO_STEP            = GEAR_RATIO_STEP
)

#=============================================================
# run function to select the motor
#=============================================================
def run(motor_name, gear_ratio):

    if motor_name == "RO80":
        return Optimizer_RO80.optimizeActuator(
            Actuator_RO80,
            UsePSCasVariable = 0,
            log              = 0,
            csv              = 1,
            printOptParams   = 1,
            gearRatioReq     = gear_ratio
        )

    elif motor_name == "RO100":
        return Optimizer_RO100.optimizeActuator(
            Actuator_RO100,
            UsePSCasVariable = 0,
            log              = 0,
            csv              = 1,
            printOptParams   = 1,
            gearRatioReq     = gear_ratio
        )

    else:
        raise ValueError(
            f"Unsupported motor: {motor_name}. "
            f"Supported motors are: RO80, RO100"
        )

#-------------------------------------------------
# Optimize
#-------------------------------------------------
# totalTime_U8 = Optimizer_U8.optimizeActuator(Actuator_U8, UsePSCasVariable = 0, log=0, csv=1, printOptParams=1, gearRatioReq = 0)
# print("Optimization Completed : CPG U8 : Total Time:", totalTime_U8)

# totalTime_U10 = Optimizer_U10.optimizeActuator(Actuator_U10, UsePSCasVariable = 0, log=0, csv=1, printOptParams=1, gearRatioReq = 0)
# print("Optimization Completed : CPG U10 : Total Time:", totalTime_U10)

# totalTime_MN8014 = Optimizer_MN8014.optimizeActuator(Actuator_MN8014, UsePSCasVariable = 0, log=0, csv=1, printOptParams=1, gearRatioReq = 0)
# print("Optimization Completed : CPG MN8014 : Total Time:", totalTime_MN8014)

# totalTime_VT8020 = Optimizer_VT8020.optimizeActuator(Actuator_VT8020, UsePSCasVariable = 0, log=0, csv=1, printOptParams=1, gearRatioReq = 0)
# print("Optimization Completed : CPG VT8020 : Total Time:", totalTime_VT8020)

# totalTime_U12 = Optimizer_U12.optimizeActuator(Actuator_U12, UsePSCasVariable = 0, log=0, csv=1, printOptParams=1, gearRatioReq = 0)
# print("Optimization Completed : CPG U12 : Total Time:", totalTime_U12)

# totalTime_MAD_M6C12 = Optimizer_MAD_M6C12.optimizeActuator(Actuator_MAD_M6C12, UsePSCasVariable = 0, log=0, csv=1, printOptParams=1, gearRatioReq = 0)
# print("Optimization Completed : CPG  MAD_M6C12 : Time Taken:", totalTime_MAD_M6C12)