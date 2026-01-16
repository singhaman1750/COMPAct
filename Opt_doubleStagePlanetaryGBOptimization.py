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

#--------------------------------------------------------
# Motors
#--------------------------------------------------------
# T motor U8
MotorU8_Kv                         = motor_data["MotorU8_framed"]["Kv"]                   # rpm/V
MotorU8_maxContinuousCurrent       = motor_data["MotorU8_framed"]["maxContinuousCurrent"] # A

MotorU8_maxTorque                  = MotorU8_maxContinuousCurrent / (MotorU8_Kv * 2 * np.pi / 60)
MotorU8_power                      = motor_data["MotorU8_framed"]["power"]                 # W 
MotorU8_ratedVoltage               = motor_data["MotorU8_framed"]["ratedVoltage"]   
MotorU8_maxMotorAngVelRPM          = MotorU8_Kv * MotorU8_ratedVoltage # RPM 
MotorU8_mass                       = motor_data["MotorU8_framed"]["mass"]                  # kg 
MotorU8_dia                        = motor_data["MotorU8_framed"]["dia"]                   # mm 
MotorU8_length                     = motor_data["MotorU8_framed"]["length"]                # mm
MotorU8_motor_mount_hole_PCD       = motor_data["MotorU8_framed"]["motor_mount_hole_PCD"]
MotorU8_motor_mount_hole_dia       = motor_data["MotorU8_framed"]["motor_mount_hole_dia"]
MotorU8_motor_mount_hole_num       = motor_data["MotorU8_framed"]["motor_mount_hole_num"]
MotorU8_motor_output_hole_PCD      = motor_data["MotorU8_framed"]["motor_output_hole_PCD"]
MotorU8_motor_output_hole_dia      = motor_data["MotorU8_framed"]["motor_output_hole_dia"]
MotorU8_motor_output_hole_num      = motor_data["MotorU8_framed"]["motor_output_hole_num"]
MotorU8_wire_slot_dist_from_center = motor_data["MotorU8_framed"]["wire_slot_dist_from_center"]
MotorU8_wire_slot_length           = motor_data["MotorU8_framed"]["wire_slot_length"]
MotorU8_wire_slot_radius           = motor_data["MotorU8_framed"]["wire_slot_radius"]

# U10 Motor
MotorU10_Kv                         = motor_data["MotorU10_framed"]["Kv"]                   # rpm/V
MotorU10_maxContinuousCurrent       = motor_data["MotorU10_framed"]["maxContinuousCurrent"] # A

MotorU10_maxTorque                  = MotorU10_maxContinuousCurrent / (MotorU10_Kv * 2 * np.pi / 60)
MotorU10_power                      = motor_data["MotorU10_framed"]["power"]                  # W
MotorU10_ratedVoltage               = motor_data["MotorU10_framed"]["ratedVoltage"]   
MotorU10_maxMotorAngVelRPM          = MotorU10_Kv * MotorU10_ratedVoltage   # RPM
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
MotorMN8014_Kv                         = motor_data["MotorMN8014_framed"]["Kv"]                   # rpm/V
MotorMN8014_maxContinuousCurrent       = motor_data["MotorMN8014_framed"]["maxContinuousCurrent"] # A

MotorMN8014_maxTorque                  = MotorMN8014_maxContinuousCurrent / (MotorMN8014_Kv * 2 * np.pi / 60)
MotorMN8014_power                      = motor_data["MotorMN8014_framed"]["power"]                  # W
MotorMN8014_ratedVoltage               = motor_data["MotorMN8014_framed"]["ratedVoltage"]   
MotorMN8014_maxMotorAngVelRPM          = MotorMN8014_Kv * MotorMN8014_ratedVoltage   # RPM
MotorMN8014_mass                       = motor_data["MotorMN8014_framed"]["mass"]                   # Kg 
MotorMN8014_dia                        = motor_data["MotorMN8014_framed"]["dia"]                    # mm
MotorMN8014_length                     = motor_data["MotorMN8014_framed"]["length"]                 # mm
MotorMN8014_motor_mount_hole_PCD       = motor_data["MotorMN8014_framed"]["motor_mount_hole_PCD"]
MotorMN8014_motor_mount_hole_dia       = motor_data["MotorMN8014_framed"]["motor_mount_hole_dia"]
MotorMN8014_motor_mount_hole_num       = motor_data["MotorMN8014_framed"]["motor_mount_hole_num"]
MotorMN8014_motor_output_hole_PCD      = motor_data["MotorMN8014_framed"]["motor_output_hole_PCD"]
MotorMN8014_motor_output_hole_dia      = motor_data["MotorMN8014_framed"]["motor_output_hole_dia"]
MotorMN8014_motor_output_hole_num      = motor_data["MotorMN8014_framed"]["motor_output_hole_num"]
MotorMN8014_wire_slot_dist_from_center = motor_data["MotorMN8014_framed"]["wire_slot_dist_from_center"]
MotorMN8014_wire_slot_length           = motor_data["MotorMN8014_framed"]["wire_slot_length"]
MotorMN8014_wire_slot_radius           = motor_data["MotorMN8014_framed"]["wire_slot_radius"]

# 8020 Motor
Motor8020_Kv                         = motor_data["Motor8020_framed"]["Kv"]                   # rpm/V
Motor8020_maxContinuousCurrent       = motor_data["Motor8020_framed"]["maxContinuousCurrent"] # A

Motor8020_maxTorque                  = Motor8020_maxContinuousCurrent / (Motor8020_Kv * 2 * np.pi / 60)
Motor8020_power                      = motor_data["Motor8020_framed"]["power"]                  # W
Motor8020_ratedVoltage               = motor_data["Motor8020_framed"]["ratedVoltage"]   
Motor8020_maxMotorAngVelRPM          = Motor8020_Kv * Motor8020_ratedVoltage   # RPM
Motor8020_mass                       = motor_data["Motor8020_framed"]["mass"]                   # Kg 
Motor8020_dia                        = motor_data["Motor8020_framed"]["dia"]                    # mm
Motor8020_length                     = motor_data["Motor8020_framed"]["length"]                 # mm
Motor8020_motor_mount_hole_PCD       = motor_data["Motor8020_framed"]["motor_mount_hole_PCD"]
Motor8020_motor_mount_hole_dia       = motor_data["Motor8020_framed"]["motor_mount_hole_dia"]
Motor8020_motor_mount_hole_num       = motor_data["Motor8020_framed"]["motor_mount_hole_num"]
Motor8020_motor_output_hole_PCD      = motor_data["Motor8020_framed"]["motor_output_hole_PCD"]
Motor8020_motor_output_hole_dia      = motor_data["Motor8020_framed"]["motor_output_hole_dia"]
Motor8020_motor_output_hole_num      = motor_data["Motor8020_framed"]["motor_output_hole_num"]
Motor8020_wire_slot_dist_from_center = motor_data["Motor8020_framed"]["wire_slot_dist_from_center"]
Motor8020_wire_slot_length           = motor_data["Motor8020_framed"]["wire_slot_length"]
Motor8020_wire_slot_radius           = motor_data["Motor8020_framed"]["wire_slot_radius"]

# T motor U12
MotorU12_Kv                         = motor_data["MotorU12_framed"]["Kv"]                   # rpm/V
MotorU12_maxContinuousCurrent       = motor_data["MotorU12_framed"]["maxContinuousCurrent"] # A

MotorU12_maxTorque                  = MotorU12_maxContinuousCurrent / (MotorU12_Kv * 2 * np.pi / 60)
MotorU12_power                      = motor_data["MotorU12_framed"]["power"]                 # W 
MotorU12_ratedVoltage               = motor_data["MotorU12_framed"]["ratedVoltage"]   
MotorU12_maxMotorAngVelRPM          = MotorU12_Kv * MotorU12_ratedVoltage   # RPM
MotorU12_mass                       = motor_data["MotorU12_framed"]["mass"]                  # kg 
MotorU12_dia                        = motor_data["MotorU12_framed"]["dia"]                   # mm 
MotorU12_length                     = motor_data["MotorU12_framed"]["length"]                # mm
MotorU12_motor_mount_hole_PCD       = motor_data["MotorU12_framed"]["motor_mount_hole_PCD"]
MotorU12_motor_mount_hole_dia       = motor_data["MotorU12_framed"]["motor_mount_hole_dia"]
MotorU12_motor_mount_hole_num       = motor_data["MotorU12_framed"]["motor_mount_hole_num"]
MotorU12_motor_output_hole_PCD      = motor_data["MotorU12_framed"]["motor_output_hole_PCD"]
MotorU12_motor_output_hole_dia      = motor_data["MotorU12_framed"]["motor_output_hole_dia"]
MotorU12_motor_output_hole_num      = motor_data["MotorU12_framed"]["motor_output_hole_num"]
MotorU12_wire_slot_dist_from_center = motor_data["MotorU12_framed"]["wire_slot_dist_from_center"]
MotorU12_wire_slot_length           = motor_data["MotorU12_framed"]["wire_slot_length"]
MotorU12_wire_slot_radius           = motor_data["MotorU12_framed"]["wire_slot_radius"]

# T motor MAD_M6C12
MotorMAD_M6C12_Kv                         = motor_data["MotorMAD_M6C12_framed"]["Kv"]                   # rpm/V
MotorMAD_M6C12_maxContinuousCurrent       = motor_data["MotorMAD_M6C12_framed"]["maxContinuousCurrent"] # A

MotorMAD_M6C12_maxTorque                  = MotorMAD_M6C12_maxContinuousCurrent / (MotorMAD_M6C12_Kv * 2 * np.pi / 60)
MotorMAD_M6C12_power                      = motor_data["MotorMAD_M6C12_framed"]["power"]                 # W 
MotorMAD_M6C12_ratedVoltage               = motor_data["MotorMAD_M6C12_framed"]["ratedVoltage"]   
MotorMAD_M6C12_maxMotorAngVelRPM          = MotorMAD_M6C12_Kv * MotorMAD_M6C12_ratedVoltage   # RPM
MotorMAD_M6C12_mass                       = motor_data["MotorMAD_M6C12_framed"]["mass"]                  # kg 
MotorMAD_M6C12_dia                        = motor_data["MotorMAD_M6C12_framed"]["dia"]                   # mm 
MotorMAD_M6C12_length                     = motor_data["MotorMAD_M6C12_framed"]["length"]                # mm
MotorMAD_M6C12_motor_mount_hole_PCD       = motor_data["MotorMAD_M6C12_framed"]["motor_mount_hole_PCD"]
MotorMAD_M6C12_motor_mount_hole_dia       = motor_data["MotorMAD_M6C12_framed"]["motor_mount_hole_dia"]
MotorMAD_M6C12_motor_mount_hole_num       = motor_data["MotorMAD_M6C12_framed"]["motor_mount_hole_num"]
MotorMAD_M6C12_motor_output_hole_PCD      = motor_data["MotorMAD_M6C12_framed"]["motor_output_hole_PCD"]
MotorMAD_M6C12_motor_output_hole_dia      = motor_data["MotorMAD_M6C12_framed"]["motor_output_hole_dia"]
MotorMAD_M6C12_motor_output_hole_num      = motor_data["MotorMAD_M6C12_framed"]["motor_output_hole_num"]
MotorMAD_M6C12_wire_slot_dist_from_center = motor_data["MotorMAD_M6C12_framed"]["wire_slot_dist_from_center"]
MotorMAD_M6C12_wire_slot_length           = motor_data["MotorMAD_M6C12_framed"]["wire_slot_length"]
MotorMAD_M6C12_wire_slot_radius           = motor_data["MotorMAD_M6C12_framed"]["wire_slot_radius"]


# Motor-U8
MotorU8 = motor(maxMotorAngVelRPM = MotorU8_maxMotorAngVelRPM, 
                 maxMotorTorque   = MotorU8_maxTorque,
                 maxMotorPower    = MotorU8_power,
                 motorMass        = MotorU8_mass,
                 motorDia         = MotorU8_dia,
                 motorLength      = MotorU8_length,
                 motor_mount_hole_PCD       = MotorU8_motor_mount_hole_PCD,
                 motor_mount_hole_dia       = MotorU8_motor_mount_hole_dia,
                 motor_mount_hole_num       = MotorU8_motor_mount_hole_num,
                 motor_output_hole_PCD      = MotorU8_motor_output_hole_PCD,
                 motor_output_hole_dia      = MotorU8_motor_output_hole_dia,
                 motor_output_hole_num      = MotorU8_motor_output_hole_num,
                 wire_slot_dist_from_center = MotorU8_wire_slot_dist_from_center,
                 wire_slot_length           = MotorU8_wire_slot_length,
                 wire_slot_radius           = MotorU8_wire_slot_radius,
                 motorName        = "U8")

# Motor-U10
MotorU10  = motor(maxMotorAngVelRPM = MotorU10_maxMotorAngVelRPM, # RPM 
                  maxMotorTorque    = MotorU10_maxTorque,         # Nm 
                  maxMotorPower     = MotorU10_power,             # W 
                  motorMass         = MotorU10_mass,              # kg 
                  motorDia          = MotorU10_dia,               # mm 
                  motorLength       = MotorU10_length,    
                  motor_mount_hole_PCD       = MotorU10_motor_mount_hole_PCD,
                  motor_mount_hole_dia       = MotorU10_motor_mount_hole_dia,
                  motor_mount_hole_num       = MotorU10_motor_mount_hole_num,
                  motor_output_hole_PCD      = MotorU10_motor_output_hole_PCD,
                  motor_output_hole_dia      = MotorU10_motor_output_hole_dia,
                  motor_output_hole_num      = MotorU10_motor_output_hole_num,
                  wire_slot_dist_from_center = MotorU10_wire_slot_dist_from_center,
                  wire_slot_length           = MotorU10_wire_slot_length,
                  wire_slot_radius           = MotorU10_wire_slot_radius, 
                  motorName         = "U10") 

# Motor-MN8014
MotorMN8014 = motor(maxMotorAngVelRPM = MotorMN8014_maxMotorAngVelRPM, #RPM 
                    maxMotorTorque    = MotorMN8014_maxTorque      , # Nm 
                    maxMotorPower     = MotorMN8014_power          , # W 
                    motorMass         = MotorMN8014_mass           , # kg 
                    motorDia          = MotorMN8014_dia            , # mm 
                    motorLength       = MotorMN8014_length         ,     
                    motor_mount_hole_PCD       = MotorMN8014_motor_mount_hole_PCD,
                    motor_mount_hole_dia       = MotorMN8014_motor_mount_hole_dia,
                    motor_mount_hole_num       = MotorMN8014_motor_mount_hole_num,
                    motor_output_hole_PCD      = MotorMN8014_motor_output_hole_PCD,
                    motor_output_hole_dia      = MotorMN8014_motor_output_hole_dia,
                    motor_output_hole_num      = MotorMN8014_motor_output_hole_num,
                    wire_slot_dist_from_center = MotorMN8014_wire_slot_dist_from_center,
                    wire_slot_length           = MotorMN8014_wire_slot_length,
                    wire_slot_radius           = MotorMN8014_wire_slot_radius, 
                    motorName         = "MN8014") 

# Motor-VT8020
Motor8020 = motor(maxMotorAngVelRPM = Motor8020_maxMotorAngVelRPM, # RPM 
                  maxMotorTorque    = Motor8020_maxTorque        , # Nm 
                  maxMotorPower     = Motor8020_power            , # W 
                  motorMass         = Motor8020_mass             , # kg 
                  motorDia          = Motor8020_dia              , # mm 
                  motorLength       = Motor8020_length           ,     
                  motor_mount_hole_PCD       = Motor8020_motor_mount_hole_PCD,
                  motor_mount_hole_dia       = Motor8020_motor_mount_hole_dia,
                  motor_mount_hole_num       = Motor8020_motor_mount_hole_num,
                  motor_output_hole_PCD      = Motor8020_motor_output_hole_PCD,
                  motor_output_hole_dia      = Motor8020_motor_output_hole_dia,
                  motor_output_hole_num      = Motor8020_motor_output_hole_num,
                  wire_slot_dist_from_center = Motor8020_wire_slot_dist_from_center,
                  wire_slot_length           = Motor8020_wire_slot_length,
                  wire_slot_radius           = Motor8020_wire_slot_radius, 
                  motorName         = "VT8020")

# Motor-U12
MotorU12 = motor(maxMotorAngVelRPM = MotorU12_maxMotorAngVelRPM,
                 maxMotorTorque    = MotorU12_maxTorque        ,
                 maxMotorPower     = MotorU12_power            ,
                 motorMass         = MotorU12_mass             , 
                 motorDia          = MotorU12_dia              ,
                 motorLength       = MotorU12_length           ,
                 motor_mount_hole_PCD       = MotorU12_motor_mount_hole_PCD,
                 motor_mount_hole_dia       = MotorU12_motor_mount_hole_dia,
                 motor_mount_hole_num       = MotorU12_motor_mount_hole_num,
                 motor_output_hole_PCD      = MotorU12_motor_output_hole_PCD,
                 motor_output_hole_dia      = MotorU12_motor_output_hole_dia,
                 motor_output_hole_num      = MotorU12_motor_output_hole_num,
                 wire_slot_dist_from_center = MotorU12_wire_slot_dist_from_center,
                 wire_slot_length           = MotorU12_wire_slot_length,
                 wire_slot_radius           = MotorU12_wire_slot_radius, 
                 motorName         = "U12")

# Motor-MAD_M6C12
MotorMAD_M6C12 = motor(maxMotorAngVelRPM          = MotorMAD_M6C12_maxMotorAngVelRPM,
                       maxMotorTorque             = MotorMAD_M6C12_maxTorque        ,
                       maxMotorPower              = MotorMAD_M6C12_power            ,
                       motorMass                  = MotorMAD_M6C12_mass             , 
                       motorDia                   = MotorMAD_M6C12_dia              ,
                       motorLength                = MotorMAD_M6C12_length           ,
                       motor_mount_hole_PCD       = MotorMAD_M6C12_motor_mount_hole_PCD,
                       motor_mount_hole_dia       = MotorMAD_M6C12_motor_mount_hole_dia,
                       motor_mount_hole_num       = MotorMAD_M6C12_motor_mount_hole_num,
                       motor_output_hole_PCD      = MotorMAD_M6C12_motor_output_hole_PCD,
                       motor_output_hole_dia      = MotorMAD_M6C12_motor_output_hole_dia,
                       motor_output_hole_num      = MotorMAD_M6C12_motor_output_hole_num,
                       wire_slot_dist_from_center = MotorMAD_M6C12_wire_slot_dist_from_center,
                       wire_slot_length           = MotorMAD_M6C12_wire_slot_length,
                       wire_slot_radius           = MotorMAD_M6C12_wire_slot_radius, 
                       motorName         = "MAD_M6C12")

#--------------------------------------------------------
# Gearbox 
#--------------------------------------------------------
doubleStagePlanetaryGearboxInstance = doubleStagePlanetaryGearbox(design_parameters         = dspg_design_params,
                                                                  gear_standard_parameters  = Gear_standard_parameters,
                                                                  densityGears              = PLA["density"],
                                                                  densityStructure          = PLA["density"],
                                                                  maxGearAllowableStressMPa = PLA["maxAllowableStressMPa"])
                                                                  
#----------------------------------------
# Actuator
#----------------------------------------
maxGBDia_multFactor           = dspg_optimization_params["MAX_GB_DIA_MULT_FACTOR"] # 1
maxGBDia_multFactor_MAD_M6C12 = dspg_optimization_params["MAX_GB_DIA_MULT_FACTOR_MAD_M6C12"] # 1.25

maxGearboxDiameter_U8        = MotorU8.motorDiaMM        * maxGBDia_multFactor - 2*dspg_design_params["ring_radial_thickness"]
maxGearboxDiameter_U10       = MotorU10.motorDiaMM       * maxGBDia_multFactor - 2*dspg_design_params["ring_radial_thickness"]
maxGearboxDiameter_MN8014    = MotorMN8014.motorDiaMM    * maxGBDia_multFactor - 2*dspg_design_params["ring_radial_thickness"]
maxGearboxDiameter_VT8020    = Motor8020.motorDiaMM      * maxGBDia_multFactor - 2*dspg_design_params["ring_radial_thickness"]
maxGearboxDiameter_U12       = MotorU12.motorDiaMM       * maxGBDia_multFactor - 2*dspg_design_params["ring_radial_thickness"] 
maxGearboxDiameter_MAD_M6C12 = MotorMAD_M6C12.motorDiaMM * maxGBDia_multFactor_MAD_M6C12 - 2*dspg_design_params["ring_radial_thickness"] 

# U8-Actuator
Actuator_U8 = doubleStagePlanetaryActuator(design_parameters           = dspg_design_params,
                                           motor                       = MotorU8,  
                                           motor_driver_params         = Motor_Driver_OdrivePro_params,
                                           doubleStagePlanetaryGearbox = doubleStagePlanetaryGearboxInstance, 
                                           FOS                         = MIT_params["FOS"], 
                                           serviceFactor               = MIT_params["serviceFactor"], 
                                           maxGearboxDiameter          = maxGearboxDiameter_U8,
                                           stressAnalysisMethodName    = "MIT")

# U10-Actuator
Actuator_U10 = doubleStagePlanetaryActuator(design_parameters           = dspg_design_params,
                                            motor                       = MotorU10,  
                                            motor_driver_params         = Motor_Driver_OdrivePro_params,
                                            doubleStagePlanetaryGearbox = doubleStagePlanetaryGearboxInstance, 
                                            FOS                         = MIT_params["FOS"], 
                                            serviceFactor               = MIT_params["serviceFactor"], 
                                            maxGearboxDiameter          = maxGearboxDiameter_U10,
                                            stressAnalysisMethodName    = "MIT")

# MN8014-Actuator
Actuator_MN8014 = doubleStagePlanetaryActuator(design_parameters           = dspg_design_params,
                                               motor                       = MotorMN8014,  
                                               motor_driver_params         = Motor_Driver_OdrivePro_params,
                                               doubleStagePlanetaryGearbox = doubleStagePlanetaryGearboxInstance, 
                                               FOS                         = MIT_params["FOS"], 
                                               serviceFactor               = MIT_params["serviceFactor"], 
                                               maxGearboxDiameter          = maxGearboxDiameter_MN8014,
                                               stressAnalysisMethodName    = "MIT")

Actuator_VT8020 = doubleStagePlanetaryActuator(design_parameters           = dspg_design_params,
                                               motor                       = Motor8020,
                                               motor_driver_params         = Motor_Driver_OdrivePro_params,
                                               doubleStagePlanetaryGearbox = doubleStagePlanetaryGearboxInstance,
                                               FOS                         = MIT_params["FOS"],
                                               serviceFactor               = MIT_params["serviceFactor"],
                                               maxGearboxDiameter          = maxGearboxDiameter_VT8020,
                                               stressAnalysisMethodName    = "MIT")

Actuator_U12 = doubleStagePlanetaryActuator(design_parameters           = dspg_design_params,
                                            motor                       = MotorU12,
                                            motor_driver_params         = Motor_Driver_OdrivePro_params,
                                            doubleStagePlanetaryGearbox = doubleStagePlanetaryGearboxInstance,
                                            FOS                         = MIT_params["FOS"],
                                            serviceFactor               = MIT_params["serviceFactor"],
                                            maxGearboxDiameter          = maxGearboxDiameter_U12,
                                            stressAnalysisMethodName    = "MIT")

Actuator_MAD_M6C12 = doubleStagePlanetaryActuator(design_parameters           = dspg_design_params,
                                                  motor                       = MotorMAD_M6C12,
                                                  motor_driver_params         = Motor_Driver_OdrivePro_params,
                                                  doubleStagePlanetaryGearbox = doubleStagePlanetaryGearboxInstance,
                                                  FOS                         = MIT_params["FOS"],
                                                  serviceFactor               = MIT_params["serviceFactor"],
                                                  maxGearboxDiameter          = maxGearboxDiameter_MAD_M6C12,
                                                  stressAnalysisMethodName    = "MIT")


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

Optimizer_U8     = optimizationDoubleStagePlanetaryActuator(design_parameters        = dspg_design_params,
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

Optimizer_U10    = optimizationDoubleStagePlanetaryActuator(design_parameters        = dspg_design_params,
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

Optimizer_MN8014 = optimizationDoubleStagePlanetaryActuator(design_parameters        = dspg_design_params,
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

Optimizer_VT8020 = optimizationDoubleStagePlanetaryActuator(design_parameters        = dspg_design_params,
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

Optimizer_U12 = optimizationDoubleStagePlanetaryActuator(design_parameters        = dspg_design_params,
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



Optimizer_MAD_M6C12 = optimizationDoubleStagePlanetaryActuator(design_parameters        = dspg_design_params,
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

#-----------------------
# Optimization: U8
#-----------------------
totalTime_U8 = Optimizer_U8.optimizeActuator(Actuator_U8, UsePSCasVariable = 0, log=0, csv=1, printOptParams=1, gearRatioReq=0)

# Convert to hours, minutes, and seconds
hours_U8, remainder_U8 = divmod(totalTime_U8, 3600)
minutes_U8, seconds_U8 = divmod(remainder_U8, 60)

#Print
print("Optimization Completed : DSPG U8")
print(f"Time taken: {hours_U8} hours, {minutes_U8} minutes, and {seconds_U8} seconds")

#-----------------------
# Optimization: U10
#-----------------------
totalTime_U10 = Optimizer_U10.optimizeActuator(Actuator_U10, UsePSCasVariable = 0, log=0, csv=1, printOptParams=1, gearRatioReq=0)

# Convert to hours, minutes, and seconds
hours_U10, remainder_U10 = divmod(totalTime_U10, 3600)
minutes_U10, seconds_U10 = divmod(remainder_U10, 60)

# Print
print("Optimization Completed : DSPG U10")
print(f"Time taken: {hours_U10} hours, {minutes_U10} minutes, and {seconds_U10} seconds")

#-----------------------
# Optimization: MN8014
#-----------------------
totalTime_MN8014 = Optimizer_MN8014.optimizeActuator(Actuator_MN8014, UsePSCasVariable = 0, log=0, csv=1, printOptParams=1, gearRatioReq=0)

# Convert to hours, minutes, and seconds
hours_MN8014, remainder_MN8014 = divmod(totalTime_MN8014, 3600)
minutes_MN8014, seconds_MN8014 = divmod(remainder_MN8014, 60)

# Print
print("Optimization Completed : DSPG MN8014")
print(f"Time taken: {hours_MN8014} hours, {minutes_MN8014} minutes, and {seconds_MN8014} seconds")

#-----------------------
# Optimization: VT8020
#-----------------------
totalTime_VT8020 = Optimizer_VT8020.optimizeActuator(Actuator_VT8020, UsePSCasVariable = 0, log=0, csv=1, printOptParams=1, gearRatioReq=0)

# Convert to hours, minutes, and seconds
hours_VT8020, remainder_VT8020 = divmod(totalTime_VT8020, 3600)
minutes_VT8020, seconds_VT8020 = divmod(remainder_VT8020, 60)

# Print
print("Optimization Completed : DSPG VT8020")
print(f"Time taken: {hours_VT8020} hours, {minutes_VT8020} minutes, and {seconds_VT8020} seconds")

# --------------------
# Optimization: U12
# --------------------
totalTime_U12 = Optimizer_U12.optimizeActuator(Actuator_U12, UsePSCasVariable = 0, log=0, csv=1, printOptParams=1, gearRatioReq=0)
 
# Convert to hours, minutes, and seconds
hours_U12, remainder_U12 = divmod(totalTime_U12, 3600)
minutes_U12, seconds_U12 = divmod(remainder_U12, 60)

# Print
print("Optimization Completed : DSPG U12")
print(f"Time taken: {hours_U12} hours, {minutes_U12} minutes, and {seconds_U12} seconds")

# -------------------------
# Optimization: MAD_M6C12
# -------------------------
totalTime_MAD_M6C12 = Optimizer_MAD_M6C12.optimizeActuator(Actuator_MAD_M6C12, UsePSCasVariable = 0, log=0, csv=1, printOptParams=1, gearRatioReq=0)

# Convert to hours, minutes, and seconds
hours_MAD_M6C12, remainder_MAD_M6C12 = divmod(totalTime_MAD_M6C12, 3600)
minutes_MAD_M6C12, seconds_MAD_M6C12 = divmod(remainder_MAD_M6C12, 60)

# Print
print("Optimization Completed : DSPG MAD_M6C12")
print(f"Time taken: {hours_MAD_M6C12} hours, {minutes_MAD_M6C12} minutes, and {seconds_MAD_M6C12} seconds")