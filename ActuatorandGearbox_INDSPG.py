import math
import os
import sys
import time
import numpy as np

# Import the base gearbox geometry class from single-stage planetry gearbox file
from ActuatorAndGearbox import singleStagePlanetaryGearbox

from CommonComponents import material, bearings_discrete, nuts_and_bolts_dimensions, motor_frameless_inrunner as motor

class bearings_continuous:
    def __init__(self, idRequiredMM):
        # Bearing dataset entered according to e1102 in 
        # [idMM, odMM, widthMM, massKG] format pg no b10-12
        self.data_bearings = [[25, 37, 7, 0.021],
                              [28, 52, 12, 0.096],
                              [30, 42, 7, 0.024],
                              [32, 58, 13, 0.122],
                              [35, 47, 7, 0.027],
                              [40, 52, 7, 0.031],
                              [45, 58, 7, 0.038],
                              [50, 65, 7, 0.050],
                              [55, 72, 9, 0.081],
                              [60, 78, 10, 0.103],
                              [65, 85, 10, 0.128],
                              [70, 90, 10, 0.134],
                              [75, 95, 10, 0.149],
                              [80, 100, 10, 0.151],
                              [85, 110, 13, 0.263],
                              [90, 115, 13, 0.276],
                              [95, 120, 13, 0.297],
                              [100, 125, 13, 0.31],
                              [105, 130, 13, 0.324],
                              [110, 140, 16, 0.497],
                              [120, 150, 16, 0.537],
                              [130, 165, 18, 0.758],
                              [140, 170, 18, 0.832],
                              [150, 190, 20, 1.15],
                              [160, 200, 20, 1.23]]
        self.idRequiredMM = idRequiredMM
        self.indexBearing = 0

        # while (self.data_bearings[self.indexBearing][0] < self.idRequiredMM):
        #     self.indexBearing +=1
        # # Extract columns
        # data_bearings = np.array(self.data_bearings)
        # self.d = data_bearings[:, 0].reshape(-1, 1)  # Inner diameters
        # self.D = data_bearings[:, 1]  # Outer diameters
        # self.B = data_bearings[:, 2]  # Widths
        # self.L = data_bearings[:, 3]  # Load ratings

        # # Create linear regression models
        # self.lr_D = LinearRegression().fit(self.d, self.D)
        # self.lr_B = LinearRegression().fit(self.d, self.B)
        # self.lr_L = LinearRegression().fit(self.d, self.L)

    def getBearingIDMM(self):
        return self.idRequiredMM
        return self.data_bearings[self.indexBearing][0]
    
    def getBearingODMM(self):
        a_OD = 1.180682635961756 
        b_OD = 8.566071759021273
        Bearing_OD = a_OD * self.idRequiredMM + b_OD
        return Bearing_OD
        return self.data_bearings[self.indexBearing][1]
    
    def getBearingWidthMM(self):
        a_widths  = 0.09293718515472396
        b_widths  = 4.617962372776808

        Bearing_Width = a_widths * self.idRequiredMM + b_widths
        return Bearing_Width
        return self.data_bearings[self.indexBearing][2]
    
    def getBearingMassKG(self):
        a_weights = 8.4777526725202e-05
        b_weights = -0.006890846402773096
        c_weights = 0.18849936113412308

        Bearing_Weight = a_weights * self.idRequiredMM * self.idRequiredMM + b_weights * self.idRequiredMM + c_weights
        return Bearing_Weight
        return self.data_bearings[self.indexBearing][3]
    
# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  INTERNAL DOUBLE STAGE PLANETARY GEARBOX                                 ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class inrunnerdoubleStagePlanetaryGearbox:
    def __init__(self,
                 design_parameters,
                 gear_standard_parameters,
                 Ns1 = 20, Np1 = 40, Nr1 = 100, 
                 Ns2 = 20, Np2 = 40, Nr2 = 100, 
                 numPlanet1 = 2,   numPlanet2 = 2, 
                 module1    = 0.8, module2    = 0.8, 
                 densityGears = 7850.0,
                 densityStructure = 2710.0,
                 fwSun1MM = 5.0, fwRing1MM = 5.0, fwPlanet1MM = 5.0,
                 fwSun2MM = 5.0, fwRing2MM = 5.0, fwPlanet2MM = 5.0,
                 maxGearAllowableStressMPa = 400) :
        
        #------------------------------------------------------------------
        # Converting the available DSPG data to stg-1 and stg-2 SSPG data 
        #------------------------------------------------------------------
        dspg_stg1_parameters = {
            "sCarrierExtrusionDiaMM"       : design_parameters["sCarrierExtrusionDiaMM_Stg1"],
            "sCarrierExtrusionClearanceMM" : design_parameters["sCarrierExtrusionClearanceMM_Stg1"],
            "ringRadialWidthMM"            : design_parameters["ring_radial_thickness"], 
            "planetMinDistanceMM"          : design_parameters["planetMinDistanceMM"]
        }

        dspg_stg2_parameters = {
            "sCarrierExtrusionDiaMM"       : design_parameters["sCarrierExtrusionDiaMM_Stg2"],
            "sCarrierExtrusionClearanceMM" : design_parameters["sCarrierExtrusionClearanceMM_Stg2"],
            "ringRadialWidthMM"            : design_parameters["ring_radial_thickness"], 
            "planetMinDistanceMM"          : design_parameters["planetMinDistanceMM"]
        }

        self.densityGears     = densityGears
        self.densityStructure = densityStructure
        self.fwSun1MM          = fwSun1MM
        self.fwSun2MM          = fwSun2MM
        self.fwRing1MM         = fwRing1MM
        self.fwRing2MM         = fwRing2MM
        self.fwPlanet1MM       = fwPlanet1MM
        self.fwPlanet2MM       = fwPlanet2MM

        # Using single Layer Planetary Gearbox for the first and second layer
        # Stage-1
        self.Stage1 = singleStagePlanetaryGearbox(design_params             = dspg_stg1_parameters,
                                                  gear_standard_parameters  = gear_standard_parameters,
                                                  Ns                        = Ns1, 
                                                  Np                        = Np1, 
                                                  Nr                        = Nr1, 
                                                  module                    = module1, 
                                                  numPlanet                 = numPlanet1,
                                                  fwSunMM                   = fwSun1MM, 
                                                  fwPlanetMM                = fwPlanet1MM,
                                                  fwRingMM                  = fwRing1MM,  
                                                  maxGearAllowableStressMPa = maxGearAllowableStressMPa, 
                                                  densityGears              = self.densityGears,
                                                  densityStructure          = self.densityStructure)
                
        # Stage-2
        self.Stage2 = singleStagePlanetaryGearbox(design_params             = dspg_stg2_parameters,
                                                  gear_standard_parameters  = gear_standard_parameters,
                                                  Ns                        = Ns2, 
                                                  Np                        = Np2, 
                                                  Nr                        = Nr2, 
                                                  module                    = module2, 
                                                  numPlanet                 = numPlanet2,
                                                  fwSunMM                   = fwSun2MM, 
                                                  fwPlanetMM                = fwPlanet2MM,
                                                  fwRingMM                  = fwRing2MM,  
                                                  maxGearAllowableStressMPa = maxGearAllowableStressMPa, 
                                                  densityGears              = self.densityGears,
                                                  densityStructure          = self.densityStructure)
        
        self.maxGearAllowableStressMPa = maxGearAllowableStressMPa

        # secondary carrier parameters
        self.sCarrierExtrusionDiaMM_Stg1       = design_parameters["sCarrierExtrusionDiaMM_Stg1"]       # 12
        self.sCarrierExtrusionClearanceMM_Stg1 = design_parameters["sCarrierExtrusionClearanceMM_Stg1"] # 2
        self.sCarrierExtrusionDiaMM_Stg2       = design_parameters["sCarrierExtrusionDiaMM_Stg2"]       # 12
        self.sCarrierExtrusionClearanceMM_Stg2 = design_parameters["sCarrierExtrusionClearanceMM_Stg2"] # 2        
        
    def getEfficiency(self):
        return self.Stage1.getEfficiency() * self.Stage2.getEfficiency()
    
    def getMassKG(self):
        totalMass = self.Stage1.getMassKG() + self.Stage2.getMassKG()
        return totalMass

    def printParameters(self):
        print("----------------------First Layer---------------------------")
        self.Stage1.printParameters()
        print("----------------------Second Layer--------------------------")
        self.Stage2.printParameters()

    def printParametersLess(self):
        print ("[module1, Ns1, Np1, Nr1, numPlanet1]:", [self.Stage1.module, self.Stage1.Ns, self.Stage1.Np, self.Stage1.Nr, self.Stage1.numPlanet])
        print ("[module2, Ns2, Np2, Nr2, numPlanet2]:", [self.Stage2.module, self.Stage2.Ns, self.Stage2.Np, self.Stage2.Nr, self.Stage2.numPlanet])
        print(" ")
        print ("[fwSun1MM, fwPlanet1MM, fwRing1MM]:",round(self.Stage1.fwSunMM,3), round(self.Stage1.fwPlanetMM,3), round(self.Stage1.fwRingMM,3))
        print ("[fwSun2MM, fwPlanet2MM, fwRing2MM]:",round(self.Stage2.fwSunMM,3), round(self.Stage2.fwPlanetMM,3), round(self.Stage2.fwRingMM,3))
        print(" ")
        # print ("Gear Ratio: ", self.gearRatio())
        print("Gear ratio (Stage1, Stage 2 , Total)= ", [self.Stage1.gearRatio(), self.Stage2.gearRatio(),self.gearRatio()])

        print ("Efficiency: ", self.getEfficiency())
        print(" ")
        print ("Mass (Gearbox, kg):",round(self.getMassKG(),3), " kg")
        print ("Mass (Gearbox1, kg):",round(self.Stage1.getMassKG(),3), " kg")
        print ("Mass (Gearbox2, kg):",round(self.Stage2.getMassKG(),3), " kg")

    def gearRatio(self):
        return self.Stage1.gearRatio() * self.Stage2.gearRatio()
    
    def efficiency(self):
        return self.Stage1.getEfficiency() * self.Stage2.getEfficiency()
    
    #----------------------------
    # Constraints
    #----------------------------
    def geometricConstraint(self):
        return (self.Stage1.geometricConstraint() and self.Stage2.geometricConstraint())

    def meshingConstraint(self):
        return (self.Stage1.meshingConstraint() and self.Stage2.meshingConstraint())

    def noPlanetInterferenceConstraint(self):
        return (self.noPlanetInterferenceConstraintStg1() and self.noPlanetInterferenceConstraintStg2())

    def noPlanetInterferenceConstraintStg1(self):
        Ns1        = self.Stage1.Ns
        Np1        = self.Stage1.Np
        Nr1        = self.Stage1.Nr
        module1    = self.Stage1.module
        numPlanet1 = self.Stage1.numPlanet

        Rs1                         = module1 * Ns1 / 2
        Rp1                         = module1 * Np1 / 2
        sCarrierExtrusionRadiusMM_Stg1  = self.sCarrierExtrusionDiaMM_Stg1 * 0.5
        return 2 * (Rs1  + Rp1) * np.sin(np.pi/(2*numPlanet1)) - Rp1 - sCarrierExtrusionRadiusMM_Stg1 >= self.sCarrierExtrusionClearanceMM_Stg1 

    def noPlanetInterferenceConstraintStg2(self):
        Ns2        = self.Stage2.Ns
        Np2        = self.Stage2.Np
        Nr2        = self.Stage2.Nr
        module2    = self.Stage2.module
        numPlanet2 = self.Stage2.numPlanet

        Rs2                         = module2 * Ns2 / 2
        Rp2                         = module2 * Np2 / 2
        sCarrierExtrusionRadiusMM_Stg2  = self.sCarrierExtrusionDiaMM_Stg2 * 0.5
        return 2 * (Rs2  + Rp2) * np.sin(np.pi/(2*numPlanet2)) - Rp2 - sCarrierExtrusionRadiusMM_Stg2 >= self.sCarrierExtrusionClearanceMM_Stg2

#-------------------------------------------------------------------------
# Inrunner Double Stage Actuator class
#-------------------------------------------------------------------------
class inrunnerdoubleStageActuator:
    def __init__(self, 
                 design_parameters,
                 motor_driver_params=None,
                 motor = motor, 
                 inrunnerdoubleStagePlanetaryGearbox = inrunnerdoubleStagePlanetaryGearbox, 
                 FOS=2.0, 
                 serviceFactor=2.0, 
                 maxGearboxDiameter=140.0,
                 maxGearboxDiameter_Stg1=32.0,
                 stressAnalysisMethodName = "Lewis"):
      
        self.motor = motor
        self.inrunnerdoubleStagePlanetaryGearbox = inrunnerdoubleStagePlanetaryGearbox
        self.FOS = FOS
        self.serviceFactor = serviceFactor
        self.maxGearboxDiameter = maxGearboxDiameter # TODO: convert it to 
                                                     # outer diameter of 
                                                     # the motor
        self.maxGearboxDiameter_Stg1 = maxGearboxDiameter_Stg1    # Stage 1 specific limit

        self.stressAnalysisMethodName = stressAnalysisMethodName
        
        #========================================
        # Motor Specifications
        #========================================
        self.motorLengthMM           = self.motor.getLengthMM()
        self.motorDiaMM              = self.motor.getDiaMM()
        self.motorMassKG             = self.motor.getMassKG()
        self.MaxMotorTorque          = self.motor.maxMotorTorque          # U12_maxTorque          # Nm
        self.MaxMotorAngVelRPM       = self.motor.maxMotorAngVelRPM       # U12_maxAngVelRPM       # RPM
        self.MaxMotorAngVelRadPerSec = self.motor.maxMotorAngVelRadPerSec # U12_maxAngVelRadPerSec # radians/sec

        #------------------------------------------------------------------------
        # Variables required from stage-1 to calculate some dimensions in stage-2
        #------------------------------------------------------------------------
        self.Bearing_ID_stg1_MM        : float | None = None                                                              #TODO: check for bearing selection once all done
        self.Bearing_OD_stg1_MM        : float | None = None
        self.Bearing_thickness_stg1_MM : float | None = None
        self.Bearing_mass_stg1_KG      : float | None = None

        self.bearing_mounting_thickness_stg1 : float | None = None

        self.design_params       = design_parameters
        self.motor_driver_params = motor_driver_params

        # ===== Set the Design Variables =====
        self.setVariables()

        self.motor_case_width   = 0
        self.gearbox_width_Stg1 = 0
        self.gearbox_width_Stg2 = 0
        self.actuator_width     = 0

    def cost(self):
        mass = self.getMassKG_3DP()
        eff = self.inrunnerdoubleStagePlanetaryGearbox.getEfficiency()
        width = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.fwPlanetMM + self.inrunnerdoubleStagePlanetaryGearbox.Stage2.fwPlanetMM
        cost = mass - 2 * eff + 0.2 * width 
        return cost 

    def setVariables_stg1(self):
        ## --------------------------------------------------------------------
        ## Stage 1 - Input Parameters & Constants
        ## --------------------------------------------------------------------
        
        # Input gear parameters from the parent object
        self.Ns1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.Ns
        self.Np1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.Np
        self.num_planet1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.numPlanet
        self.module1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.module

        self.fw_s1_calc = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.fwSunMM
        self.fw_r1      = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.fwRingMM
        
        # Shared constants and design parameters
        self.pressure_angle = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.getPressureAngleRad() * 180 / np.pi

        self.clearance_planet                           = self.design_params["clearance_planet"] # 1.5
        self.tight_clearance_3DP                        = self.design_params["tight_clearance_3DP"]        
        self.loose_clearance_3DP                        = self.design_params["loose_clearance_3DP"]
        self.standard_clearance_1_5mm                   = self.design_params["standard_clearance_1_5mm"] # 1.5
        self.standard_fillet_1_5mm                      = self.design_params["standard_fillet_1_5mm"] # 1.5
        self.standard_bearing_insertion_chamfer         = self.design_params["standard_bearing_insertion_chamfer"] # 0.5
        self.ring_radial_thickness                      = self.design_params["ring_radial_thickness"] # 5
        self.sec_carrier_thickness1                     = self.design_params["sec_carrier_thickness1"] # 5
        self.sun_coupler_hub_thickness1                 = self.design_params["sun_coupler_hub_thickness1"] # 4
        self.clearance_sun_coupler_sec_carrier          = self.design_params["clearance_sun_coupler_sec_carrier"] # 1.5
        self.stator_casing_thickness                    = self.design_params["stator_casing_thickness"] # 2.5                          
        self.clearance_case_mount_holes_shell_thickness = self.design_params["clearance_case_mount_holes_shell_thickness"] # 1
        self.output_mounting_hole_dia1                  = self.design_params["output_mounting_hole_dia1"] # 4
        self.case_mounting_hole_dia                     = self.design_params["case_mounting_hole_dia"] # 3
        self.case_mounting_bolt_depth                   = self.design_params["case_mounting_bolt_depth"] # 4.5
        self.case_mounting_surface_height               = self.design_params["case_mounting_surface_height"] # 4
        self.carrier_bearing_step_width                 = self.design_params["carrier_bearing_step_width"] # 1.5
        self.planet_shaft_step_offset                   = self.design_params["planet_shaft_step_offset"] # 1
        self.bearing_retainer_thickness1                = self.design_params["bearing_retainer_thickness1"] # 2

        self.bearingIDClearanceMM                       = self.design_params["bearingIDClearanceMM"]


        ## --------------------------------------------------------------------
        ## New varibales added to dspg existing one for inrunner type                          #TODO: change the name
        ## --------------------------------------------------------------------
        self.a2_bearing_retainer_hole_dia = self.design_params["a2_bearing_retainer_hole_dia"]
        self.a2_bearing_retainer_hole_num = self.design_params["a2_bearing_retainer_hole_num"]
        self.a2_bearing_retainer_nut_wrench_size = self.design_params["a2_bearing_retainer_nut_wrench_size"]
        self.a2_bearing_retainer_wrench_height = self.design_params["a2_bearing_retainer_wrench_height"]
        self.bearing_retainer_thickness = self.design_params["bearing_retainer_thickness"]

        self.a1_sun_bottom_casing_bearing_ID = self.design_params["a1_sun_bottom_casing_bearing_ID"]
        self.a1_sun_bottom_casing_bearing_OD = self.design_params["a1_sun_bottom_casing_bearing_OD"]
        self.a1_sun_bottom_casing_bearing_height = self.design_params["a1_sun_bottom_casing_bearing_height"]
        self.a1_sun_bottom_casing_bearing_massKg = self.design_params["a1_sun_bottom_casing_bearing_massKg"]



        #----------FIXING THE FW_P STAGE 1 TO 9 MM ------------#                  

        self.fw_p_1_fix = self.design_params["fw_p_1_fix"]                    #TODO: check if it is required to be fixed or not

        #------------------------------------------------------#


        ## --------------------------------------------------------------------
        ## Motor, Driver, and Base Plate Dimensions
        ## --------------------------------------------------------------------
        # self.motor_OD                   = self.motorDiaMM    # 88.6                     #TODO: remove them later
        # self.motor_height               = self.motorLengthMM # 43
        # self.motor_mount_hole_PCD       = self.motor.motor_mount_hole_PCD # 32
        # self.motor_mount_hole_dia       = self.motor.motor_mount_hole_dia # 4
        # self.motor_mount_hole_num       = self.motor.motor_mount_hole_num # 4
        # self.motor_output_hole_PCD      = self.motor.motor_output_hole_PCD # 23
        # self.motor_output_hole_dia      = self.motor.motor_output_hole_dia # 4
        # self.motor_output_hole_num      = self.motor.motor_output_hole_num # 4
        # self.wire_slot_dist_from_center = self.motor.wire_slot_dist_from_center # 30
        # self.wire_slot_length           = self.motor.wire_slot_length # 10
        # self.wire_slot_radius           = self.motor.wire_slot_radius # 4

        
        self.rotor_OD      = self.motor.rotor_OD
        self.stator_ID     = self.motor.stator_ID
        self.rotor_height  = self.motor.rotor_height
        self.rotor_ID      = self.motor.rotor_ID
        self.stator_height = self.motor.stator_height
        self.stator_OD     = self.motor.stator_OD
        self.motorDiaMM    = self.stator_OD

        self.stator_hole_dia           = self.motor.stator_hole_dia
        self.stator_wire_top_height    = self.motor.stator_wire_top_height
        self.stator_wire_bottom_height = self.motor.stator_wire_bottom_height
        self.stator_wire_ID            = self.motor.stator_wire_ID
        self.stator_wire_OD            = self.motor.stator_wire_OD
        #self.stator_mid_height         = self.motor.stator_mid_height
        self.stator_hole_num           = self.motor.stator_hole_num

        self.stator_casing_hole_dia  = self.design_params["stator_casing_hole_dia"]
        self.stator_casing_hole_allen_socket_head_dia = self.design_params["stator_casing_hole_allen_socket_head_dia"]
        self.stator_mounting_holes_head_socket_dia = self.design_params["stator_mounitng_holes_head_socket_dia"]

        self.rotor_mount_hole_PCD = self.design_params["rotor_mount_hole_PCD"]
        self.rotor_mount_hole_dia = self.design_params["rotor_mount_hole_dia"]
        self.rotor_mount_hole_num = self.design_params["rotor_mount_hole_num"]
        self.rotor_csk_head_upper_dia = self.design_params["Rotor_csk_head_upper_dia"]
        self.rotor_csk_head_height = self.design_params["Rotor_csk_head_height"]

        #motor_output_hole_bolt = nuts_and_bolts_dimensions(bolt_dia = self.motor_output_hole_dia, bolt_type="CSK")

        #self.motor_output_hole_CSK_OD          = motor_output_hole_bolt.bolt_head_dia
        #self.motor_output_hole_CSK_head_height = motor_output_hole_bolt.bolt_head_height

        #self.central_hole_offset_from_motor_mount_PCD = self.design_params["central_hole_offset_from_motor_mount_PCD"] # 5
        
        self.stator_casing_thickness = self.design_params["stator_casing_thickness"] # 3.5
        #self.air_flow_hole_offset = self.design_params["air_flow_hole_offset"] # 3

        # === Driver ===
        # self.driver_upper_holes_dist_from_center = self.motor_driver_params["driver_upper_holes_dist_from_center"] # 23
        # self.driver_lower_holes_dist_from_center = self.motor_driver_params["driver_lower_holes_dist_from_center"] # 15
        # self.driver_side_holes_dist_from_center  = self.motor_driver_params["driver_side_holes_dist_from_center"]  # 20
        # self.driver_mount_holes_dia              = self.motor_driver_params["driver_mount_holes_dia"]              # 2.5
        # self.driver_mount_inserts_OD             = self.motor_driver_params["driver_mount_inserts_OD"]             # 3.5
        # self.driver_mount_thickness              = self.motor_driver_params["driver_mount_thickness"]              # 1.5
        # self.driver_mount_height                 = self.motor_driver_params["driver_mount_height"]                 # 4

        ## --------------------------------------------------------------------
        ## Stage 1 - Core Gear Geometry Calculations
        ## --------------------------------------------------------------------
        self.Nr1 = self.Ns1 + 2 * self.Np1
        self.h_a1 = 1 * self.module1
        self.h_f1 = 1.25 * self.module1
        self.h_b1 = 1.25 * self.module1
        self.fw_p1 = self.fw_r1
        self.clr_tip_root1 = self.h_f1 - self.h_a1
        
        # Sun gear dimensions
        self.dp_s1 = self.module1 * self.Ns1
        self.db_s1 = self.dp_s1 * np.cos(np.deg2rad(self.pressure_angle))
        self.alpha_s1 = np.sqrt(self.dp_s1 ** 2 - self.db_s1 ** 2) / self.db_s1 * 180 / np.pi - self.pressure_angle
        self.beta_s1 = (360 / (4 * self.Ns1) - self.alpha_s1) * 2

        # Planet gear dimensions
        self.dp_p1 = self.module1 * self.Np1
        self.db_p1 = self.dp_p1 * np.cos(np.deg2rad(self.pressure_angle))
        self.alpha_p1 = np.sqrt(self.dp_p1 ** 2 - self.db_p1 ** 2) / self.db_p1 * 180 / np.pi - self.pressure_angle
        self.beta_p1 = (360 / (4 * self.Np1) - self.alpha_p1) * 2
        
        # Ring gear dimensions
        self.dp_r1 = self.module1 * self.Nr1
        self.db_r1 = self.dp_r1 * np.cos(np.deg2rad(self.pressure_angle))
        self.alpha_r1 = np.sqrt(self.dp_r1 ** 2 - self.db_r1 ** 2) / self.db_r1 * 180 / np.pi - self.pressure_angle
        self.beta_r1 = (360 / (4 * self.Nr1) + self.alpha_r1) * 2

        ## --------------------------------------------------------------------
        ## Stage 1 - Component and Casing Calculations
        ## --------------------------------------------------------------------
        
        # Bearing calculations
        # req_bearing1_ID = self.module1 * (self.Ns1 + self.Np1) + self.bearingIDClearanceMM   #TODO: check for bearing selection once all done , THIS IS FIX VALUE
        # Bearing1 = bearings_discrete(req_bearing1_ID)
        # self.bearing1_ID = Bearing1.getBearingIDMM()
        # self.bearing1_OD = Bearing1.getBearingODMM()
        # self.bearing1_height = Bearing1.getBearingWidthMM()

        self.bearing1_ID = 38.1                                                                #TODO: if possible extract it from bearing selection once all done , THIS IS FIX VALUE
        self.bearing1_OD = 47.625
        self.bearing1_height = 4.763


        #case_mounting_bolt = nuts_and_bolts_dimensions(bolt_dia = self.case_mounting_hole_dia, bolt_type="socket_head")
        
        #self.case_mounting_hole_allen_socket_dia = case_mounting_bolt.bolt_head_dia
        #self.case_mounting_wrench_size           = case_mounting_bolt.nut_width_across_flats # 5.5
        #self.case_mounting_nut_thickness         = case_mounting_bolt.nut_thickness # 2.4

        # Housing and case calculations
        #self.ring_OD1 = self.Nr1 * self.module1 + self.ring_radial_thickness * 2
        #self.clearance_motor_and_case = (5 if self.ring_OD1 < self.motor_OD else (self.ring_OD1 - self.motor_OD) / 2 + 5)
        #self.motor_case_OD_base = self.motor_OD + self.clearance_motor_and_case * 2 + self.Motor_case_thickness * 2
        #self.Motor_case_ID = self.motor_OD + self.clearance_motor_and_case * 2
        #self.case_mounting_hole_shift = self.case_mounting_hole_dia / 2 - 0.5
        #self.case_mounting_PCD = self.motor_case_OD_base + self.case_mounting_hole_shift * 2
        #self.Motor_case_OD_max = self.case_mounting_PCD + self.case_mounting_hole_allen_socket_dia + self.clearance_case_mount_holes_shell_thickness * 2

        # Mounting thickness and PCD
        #self.bearing_mount_thickness1 = (self.output_mounting_hole_dia1 * 2 if (self.bearing1_OD + self.output_mounting_hole_dia1 * 4) > (self.Nr1 * self.module1 + 2 * self.h_b1) else ((self.Nr1 * self.module1 + 2 * self.h_b1 - (self.bearing1_OD + self.output_mounting_hole_dia1 * 4)) / 2) + self.output_mounting_hole_dia1 * 2 + self.standard_clearance_1_5mm)
        #self.output_mounting_PCD1 = self.bearing1_OD + self.bearing_mount_thickness1
        
        # Carrier and final assembly dimensions
        self.carrier_PCD1 = (self.Np1 + self.Ns1) * self.module1
        self.fw_s1_used = self.fw_p_1_fix + self.clearance_planet + self.sec_carrier_thickness1 + self.standard_clearance_1_5mm
        #self.case_dist1 = self.sec_carrier_thickness1 + self.clearance_planet + self.sun_coupler_hub_thickness1 - self.case_mounting_surface_height
        self.sun_hub_dia1 = self.rotor_ID - 2 * (self.standard_clearance_1_5mm + 2)

        ## --------------------------------------------------------------------
        ## Stage 1 - Fastener and Detailed Feature Dimensions
        ## --------------------------------------------------------------------
        self.output_mounting_nut_depth1                              = self.design_params["output_mounting_nut_depth1"] # 3
        self.ring_to_chamfer_clearance1                              = self.design_params["ring_to_chamfer_clearance1"] # 2
        self.Motor_case_OD_base_to_chamfer                           = self.design_params["Motor_case_OD_base_to_chamfer"] # 5
        self.pattern_offset_from_motor_case_OD_base                  = self.design_params["pattern_offset_from_motor_case_OD_base"] # 3
        self.pattern_bulge_dia                                       = self.design_params["pattern_bulge_dia"] # 3
        self.pattern_num_bulge                                       = self.design_params["pattern_num_bulge"] # 18
        self.pattern_depth                                           = self.design_params["pattern_depth"] # 2
        self.case_mounting_nut_clearance                             = self.design_params["case_mounting_nut_clearance"] # 2
        self.planet_shaft_dia1                                       = self.design_params["planet_shaft_dia1"] # 8
        self.carrier_trapezoidal_support_sun_offset1                 = self.design_params["carrier_trapezoidal_support_sun_offset1"] # 5
        self.carrier_trapezoidal_support_hole_PCD_offset_bearing_ID1 = self.design_params["carrier_trapezoidal_support_hole_PCD_offset_bearing_ID1"] # 4
        self.sun_shaft_bearing_OD1                                   = self.design_params["sun_shaft_bearing_OD1"] # 16
        self.sun_shaft_bearing_width1                                = self.design_params["sun_shaft_bearing_width1"] # 4
        self.planet_bearing_OD1                                      = self.design_params["planet_bearing_OD1"] # 12
        self.planet_bearing_width1                                   = self.design_params["planet_bearing_width1"] # 3
        self.planet_bore1                                            = self.design_params["planet_bore1"] # 10
        self.sun_shaft_bearing_ID1                                   = self.design_params["sun_shaft_bearing_ID1"] # 8
        self.planet_pin_bolt_dia1                                    = self.design_params["planet_pin_bolt_dia1"] # 5
        self.carrier_trapezoidal_support_hole_dia1                   = self.design_params["carrier_trapezoidal_support_hole_dia1"] # 3
        self.sun_central_bolt_dia1                                   = self.design_params["sun_central_bolt_dia1"] # 5

        #output_mounting_bolt1 =  nuts_and_bolts_dimensions(bolt_dia = self.output_mounting_hole_dia1, bolt_type="socket_head")

        #self.output_mounting_nut_wrench_size1 = output_mounting_bolt1.nut_width_across_flats # 7
        #self.output_mounting_nut_thickness1   = output_mounting_bolt1.nut_thickness # 3.2 

        planet_pin_bolt1 = nuts_and_bolts_dimensions(bolt_dia = self.planet_pin_bolt_dia1, bolt_type="socket_head")

        self.planet_pin_socket_head_dia1  = planet_pin_bolt1.bolt_head_dia    # 8.5
        self.planet_pin_bolt_wrench_size1 = planet_pin_bolt1.nut_width_across_flats # 8
        
        carrier_trapezoidal_support_hole_bolt1 = nuts_and_bolts_dimensions(bolt_dia = self.carrier_trapezoidal_support_hole_dia1, bolt_type="socket_head")

        self.carrier_trapezoidal_support_hole_socket_head_dia1 = carrier_trapezoidal_support_hole_bolt1.bolt_head_dia    # 5.5
        self.carrier_trapezoidal_support_hole_wrench_size1     = carrier_trapezoidal_support_hole_bolt1.nut_width_across_flats # 5.5

        sun_central_bolt1 = nuts_and_bolts_dimensions(bolt_dia = self.sun_central_bolt_dia1, bolt_type="socket_head")

        self.sun_central_bolt_socket_head_dia1 = sun_central_bolt1.bolt_head_dia # 8.5

        
        # Stg1:
        # "fw_r"+"clearance_planet" + "bearing_height"+"clearance_planet" + "case_dist" + "bearing_retainer_thickness"
        self.gearbox_width_Stg1 = (  self.fw_r1
                                   + self.clearance_planet
                                   + self.carrier_bearing_step_width
                                   + self.sun_coupler_hub_thickness1
                                   + 2
                                   + self.bearing1_height*1.5
                                   + self.standard_clearance_1_5mm )
        # Motor:
        # "motor_height" + "case_mounting_surface_height" + "standard_clearance_1_5mm" + "base_plate_thickness" 
        # self.motor_case_width = (  self.motor_height
        #                          + self.case_mounting_surface_height
        #                          + self.standard_clearance_1_5mm
        #                          + self.stator_casing_thickness)

    def setVariables_stg2(self):
        ## --------------------------------------------------------------------
        ## Stage 2 - Input Parameters & Constants
        ## --------------------------------------------------------------------

        # Input gear parameters from the parent object
        self.Ns2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.Ns
        self.Np2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.Np
        self.module2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.module
        self.num_planet2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.numPlanet


        self.fw_s2_calc = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.fwSunMM
        self.fw_r2      = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.fwRingMM

        # Shared constants and design parameters
        self.clearance_planet                                        = self.design_params["clearance_planet"] # 1.5
        self.clearance_case_mount_holes_shell_thickness2             = self.design_params["clearance_case_mount_holes_shell_thickness2"] # 1
        self.clearance_sun_coupler_sec_carrier                       = self.design_params["clearance_sun_coupler_sec_carrier"] # 1.5
        self.standard_clearance_1_5mm                                = self.design_params["standard_clearance_1_5mm"] # 1.5
        self.standard_fillet_1_5mm                                   = self.design_params["standard_fillet_1_5mm"] # 1.5
        self.ring_radial_thickness                                   = self.design_params["ring_radial_thickness"] # 5
        self.sec_carrier_thickness2                                  = self.design_params["sec_carrier_thickness2"] # 5
        self.ring_to_chamfer_clearance2                              = self.design_params["ring_to_chamfer_clearance2"] # 2
        self.planet_shaft_dia2                                       = self.design_params["planet_shaft_dia2"] # 8
        self.planet_shaft_step_offset2                               = self.design_params["planet_shaft_step_offset2"] # 1
        self.carrier_trapezoidal_support_sun_offset2                 = self.design_params["carrier_trapezoidal_support_sun_offset2"] # 5
        self.carrier_trapezoidal_support_hole_PCD_offset_bearing_ID2 = self.design_params["carrier_trapezoidal_support_hole_PCD_offset_bearing_ID2"] # 4
        self.carrier_bearing_step_width2                             = self.design_params["carrier_bearing_step_width2"] # 1.5
        self.sun_shaft_bearing_OD2                                   = self.design_params["sun_shaft_bearing_OD2"] # 16
        self.sun_shaft_bearing_width2                                = self.design_params["sun_shaft_bearing_width2"] # 4
        self.planet_bearing_OD2                                      = self.design_params["planet_bearing_OD2"] # 12
        self.planet_bearing_width2                                   = self.design_params["planet_bearing_width2"] # 3
        self.planet_bore2                                            = self.design_params["planet_bore2"] # 10
        self.sun_shaft_bearing_ID2                                   = self.design_params["sun_shaft_bearing_ID2"] # 8
        self.bearing_retainer_thickness2                             = self.design_params["bearing_retainer_thickness2"] # 2
        self.output_mounting_nut_wrench_size2                        = self.design_params["a2_output_mounting_nut_wrench_size"] # 6

        self.output_mounting_hole_dia2             = self.design_params["output_mounting_hole_dia2"] # 4
        self.planet_pin_bolt_dia2                  = self.design_params["planet_pin_bolt_dia2"] # 5
        self.carrier_trapezoidal_support_hole_dia2 = self.design_params["carrier_trapezoidal_support_hole_dia2"] # 3
        self.sun_central_bolt_dia2                 = self.design_params["sun_central_bolt_dia2"] # 5
        self.stg1_stg2_mounting_hole_dia           = self.design_params["stg1_stg2_mounting_hole_dia"] # 4
        self.stg1_stg2_mounting_pattern_width      = self.design_params["stg1_stg2_mounting_pattern_width"] # 12
        self.output_mounting_nut_depth2            = self.design_params["output_mounting_nut_depth2"] # 3


        ## --------------------------------------------------------------------
        ## New varibales added to dspg existing one for inrunner type                          #TODO: change the name and seperate stgae 1 and 2 variables
        ## --------------------------------------------------------------------
        self.a2_bearing_retainer_hole_dia = self.design_params["a2_bearing_retainer_hole_dia"]
        self.a2_bearing_retainer_hole_num = self.design_params["a2_bearing_retainer_hole_num"]
        self.a2_bearing_retainer_nut_wrench_size = self.design_params["a2_bearing_retainer_nut_wrench_size"]
        self.a2_bearing_retainer_wrench_height = self.design_params["a2_bearing_retainer_wrench_height"]
        self.bearing_retainer_thickness = self.design_params["bearing_retainer_thickness"]

        self.a1_sun_bottom_casing_bearing_ID = self.design_params["a1_sun_bottom_casing_bearing_ID"]
        self.a1_sun_bottom_casing_bearing_OD = self.design_params["a1_sun_bottom_casing_bearing_OD"]
        self.a1_sun_bottom_casing_bearing_height = self.design_params["a1_sun_bottom_casing_bearing_height"]
        self.a1_sun_bottom_casing_bearing_massKg = self.design_params["a1_sun_bottom_casing_bearing_massKg"]

        self.stator_mounting_hole_wrench_dia = self.design_params["stator_mounting_hole_wrench_dia"]
        self.stator_mounting_hole_wrench_thickness = self.design_params["stator_mounting_hole_wrench_thickness"]


        
        ## --------------------------------------------------------------------
        ## Stage 2 - Core Gear Geometry Calculations
        ## --------------------------------------------------------------------
        self.Nr2 = self.Ns2 + 2 * self.Np2
        self.fw_p2 = self.fw_r2
        self.h_a2 = 1 * self.module2
        self.h_f2 = 1.25 * self.module2
        self.h_b2 = 1.25 * self.module2
        self.clr_tip_root2 = self.h_f2 - self.h_a2

        # Pitch circle diameters
        self.dp_p2 = self.module2 * self.Np2
        self.dp_r2 = self.module2 * self.Nr2
        self.dp_s2 = self.module2 * self.Ns2
        self.carrier_PCD2 = (self.Np2 + self.Ns2) * self.module2

        # Base circle diameters (correcting to use radians for trig functions)
        self.db_s2 = self.dp_s2 * np.cos(np.deg2rad(self.pressure_angle))
        self.db_p2 = self.dp_p2 * np.cos(np.deg2rad(self.pressure_angle))
        self.db_r2 = self.dp_r2 * np.cos(np.deg2rad(self.pressure_angle))

        # Alpha and Beta angles
        self.alpha_s2 = np.sqrt(self.dp_s2**2 - self.db_s2**2) / self.db_s2 * 180 / np.pi - self.pressure_angle
        self.alpha_p2 = np.sqrt(self.dp_p2**2 - self.db_p2**2) / self.db_p2 * 180 / np.pi - self.pressure_angle
        self.alpha_r2 = np.sqrt(self.dp_r2**2 - self.db_r2**2) / self.db_r2 * 180 / np.pi - self.pressure_angle
        self.beta_s2 = (360 / (4 * self.Ns2) - self.alpha_s2) * 2
        self.beta_p2 = (360 / (4 * self.Np2) - self.alpha_p2) * 2
        self.beta_r2 = (360 / (4 * self.Nr2) + self.alpha_r2) * 2
        
        ## --------------------------------------------------------------------
        ## Stage 2 - Component & Fastener Lookups
        ## --------------------------------------------------------------------

        # Planet pin bolt dimensions
        planet_bolt2 = nuts_and_bolts_dimensions(bolt_dia=self.planet_pin_bolt_dia2, bolt_type="socket_head")
        self.planet_pin_socket_head_dia2 = planet_bolt2.bolt_head_dia
        self.planet_pin_bolt_wrench_size2 = planet_bolt2.nut_width_across_flats

        # Stage 2 Bearing lookup
        req_bearing2_ID = self.module2 * (self.Ns2 + self.Np2) + self.planet_pin_socket_head_dia2    #TODO: check if too tight tolerance
        Bearing2 = bearings_discrete(req_bearing2_ID)
        self.bearing2_ID = Bearing2.getBearingIDMM()
        self.bearing2_OD = Bearing2.getBearingODMM()
        self.bearing2_height = Bearing2.getBearingWidthMM()

        # Output mounting hole/nut dimensions
        #output_mounting_hole2 = nuts_and_bolts_dimensions(bolt_dia=self.output_mounting_hole_dia2)
        #self.output_mounting_nut_wrench_size2 = output_mounting_hole2.nut_width_across_flats
        #self.output_mounting_nut_thickness2 = output_mounting_hole2.nut_thickness

        
        # Carrier support hole dimensions
        carrier_trapezoidal_support_hole2 = nuts_and_bolts_dimensions(bolt_dia=self.carrier_trapezoidal_support_hole_dia2, bolt_type="socket_head")
        self.carrier_trapezoidal_support_hole_socket_head_dia2 = carrier_trapezoidal_support_hole2.bolt_head_dia
        self.carrier_trapezoidal_support_hole_wrench_size2 = carrier_trapezoidal_support_hole2.nut_width_across_flats
        
        # Sun gear central bolt dimensions
        sun_central_bolt2 = nuts_and_bolts_dimensions(bolt_dia=self.sun_central_bolt_dia2)
        self.sun_central_bolt_socket_head_dia2 = sun_central_bolt2.bolt_head_dia

        # Stage 1-2 interface mounting hole dimensions
        stg1_stg2_mounting_hole = nuts_and_bolts_dimensions(bolt_dia=self.stg1_stg2_mounting_hole_dia)
        self.stg1_stg2_allen_socket_head_dia = stg1_stg2_mounting_hole.bolt_head_dia

        ## --------------------------------------------------------------------
        ## Stage 2 - Final Assembly & Interface Calculations
        ## --------------------------------------------------------------------
        
        self.ring_OD2 = self.Nr2 * self.module2 + self.ring_radial_thickness * 2
        self.fw_s2_used = self.fw_p2 + self.clearance_planet + self.sec_carrier_thickness2 + self.standard_clearance_1_5mm + self.loose_clearance_3DP
        #self.bearing_mount_thickness2 = (self.output_mounting_hole_dia2 * 2) if ((self.bearing2_OD + self.output_mounting_hole_dia2 * 4) > (self.Nr2 * self.module2 + 2 * self.h_b2)) else (((self.Nr2 * self.module2 + 2 * self.h_b2 - (self.bearing2_OD + self.output_mounting_hole_dia2 * 4)) / 2) + self.output_mounting_hole_dia2 * 2 + self.standard_clearance_1_5mm)
        #self.output_mounting_PCD2 = self.bearing2_OD + self.bearing_mount_thickness2
        #self.case_dist2 = self.sec_carrier_thickness2 + self.clearance_planet + self.standard_clearance_1_5mm - self.bearing_retainer_thickness2
        
        # Interface variables
        # Note: This final definition for stg1_stg2_mounting_extra_width is used, as it appears last.
        # It depends on variables from Stage 1 (self.bearing1_OD, self.bearing_mounting_thickness_stg1).
        #self.stg1_stg2_mounting_extra_width = (0) if ((self.Nr2 * self.module2 + self.ring_radial_thickness * 2 + self.stg1_stg2_allen_socket_head_dia) / 2 + self.standard_clearance_1_5mm * 2 + self.stg1_stg2_allen_socket_head_dia / 2 - (self.bearing1_OD + self.bearing_mounting_thickness_stg1 * 2) / 2) < 0 else ((self.Nr2 * self.module2 + self.ring_radial_thickness * 2 + self.stg1_stg2_allen_socket_head_dia) / 2 + self.standard_clearance_1_5mm * 2 + self.stg1_stg2_allen_socket_head_dia / 2 - (self.bearing1_OD + self.bearing_mounting_thickness_stg1 * 2) / 2)

        self.gearbox_width_Stg2 = (  self.fw_s2_used                         #TODO: why fw_r2 is used here instead of fw_p2 although same or can use fw_s2_used
                                   + self.clearance_planet
                                   + self.carrier_bearing_step_width2
                                   + self.bearing2_height
                                   + self.bearing_retainer_thickness2)

    def setVariables(self):
        self.setVariables_stg1()
        self.setVariables_stg2()

        self.actuator_width = self.gearbox_width_Stg1 + self.gearbox_width_Stg2

    # ══════════════════════════════════════════════════════════════════════
    # CAD equation file generation
    # ══════════════════════════════════════════════════════════════════════
    def _equation_lines(self):
                  
        return [
        f'"a1_Ns" = {self.Ns1}\n',
        f'"a1_Np" = {self.Np1}\n',
        f'"a1_Nr" = {self.Nr1}\n',
        f'"a1_num_planet" = {self.num_planet1}\n',
        f'"a1_module" = {self.module1}\n',
        # f'"a1_pressure angle" = {self.pressure_angle}\n',
        f'"a1_pressure_angle" = {self.pressure_angle}\n',
        # f'"a1_motor_mount_hole_PCD" = {self.motor_mount_hole_PCD}\n',
        # f'"a1_motor_mount_hole_dia" = {self.motor_mount_hole_dia}\n',
        # f'"a1_motor_mount_hole_num" = {self.motor_mount_hole_num}\n',
        # f'"a1_motor_output_hole_PCD" = {self.motor_output_hole_PCD}\n',
        # f'"a1_motor_output_hole_dia" = {self.motor_output_hole_dia}\n',
        # f'"a1_motor_output_hole_num" = {self.motor_output_hole_num}\n',
        # f'"a1_motor_OD" = {self.motor_OD}\n',
        # f'"a1_motor_height" = {self.motor_height}\n',
        # f'"a1_wire_slot_dist_from_center" = {self.wire_slot_dist_from_center}\n',
        # f'"a1_wire_slot_length" = {self.wire_slot_length}\n',
        # f'"a1_wire_slot_radius" = {self.wire_slot_radius}\n',
        f'"a1_h_a" = {self.h_a1}\n',
        f'"a1_h_b" = {self.h_b1}\n',
        f'"a1_h_f" = {self.h_f1}\n',
        f'"a1_clr_tip_root" = {self.clr_tip_root1}\n',
        f'"a1_dp_s" = {self.dp_s1}\n',
        f'"a1_db_s" = {self.db_s1}\n',
        f'"a1_fw_s_calc" = {self.fw_s1_calc}\n',
        f'"a1_alpha_s" = {self.alpha_s1}\n',
        f'"a1_beta_s" = {self.beta_s1}\n',
        f'"a1_dp_p" = {self.dp_p1}\n',
        f'"a1_db_p" = {self.db_p1}\n',
        f'"a1_fw_p" = {self.fw_p_1_fix}\n',
        f'"a1_alpha_p" = {self.alpha_p1}\n',
        f'"a1_beta_p" = {self.beta_p1}\n',
        f'"a1_dp_r" = {self.dp_r1}\n',
        f'"a1_db_r" = {self.db_r1}\n',
        f'"a1_fw_r" = {self.fw_r1}\n',
        f'"a1_alpha_r" = {self.alpha_r1}\n',
        f'"a1_beta_r" = {self.beta_r1}\n',
        f'"a1_bearing_ID" = {self.bearing1_ID}\n',
        f'"a1_bearing_OD" = {self.bearing1_OD}\n',
        f'"a1_bearing_height" = {self.bearing1_height}\n',
        f'"a1_clearance_planet" = {self.clearance_planet}\n',
        # f'"a1_case_dist" = {self.case_dist1}\n',
        # f'"a1_Motor_case_OD_max" = {self.Motor_case_OD_max}\n',
        # f'"a1_case_mounting_PCD" = {self.case_mounting_PCD}\n',
        # f'"a1_bearing_mount_thickness" = {self.bearing_mount_thickness1}\n',
        f'"a1_case_mounting_hole_dia" = {self.case_mounting_hole_dia}\n',
        # f'"a1_output_mounting_PCD" = {self.output_mounting_PCD1}\n',
        f'"a1_output_mounting_hole_dia" = {self.output_mounting_hole_dia1}\n',
        f'"a1_clearance_case_mount_holes_shell_thickness" = {self.clearance_case_mount_holes_shell_thickness}\n',
        # f'"a1_motor_case_OD_base" = {self.motor_case_OD_base}\n',
        f'"a1_sec_carrier_thickness" = {self.sec_carrier_thickness1}\n',
        f'"a1_sun_coupler_hub_thickness" = {self.sun_coupler_hub_thickness1}\n',
        f'"a1_clearance_sun_coupler_sec_carrier" = {self.clearance_sun_coupler_sec_carrier}\n',
        # f'"a1_clearance_motor_and_case" = {self.clearance_motor_and_case}\n',
        # f'"a1_Motor_case_thickness" = {self.Motor_case_thickness}\n',
        # f'"a1_Motor_case_ID" = {self.Motor_case_ID}\n',
        # f'"a1_case_mounting_hole_shift" = {self.case_mounting_hole_shift}\n',
        # f'"a1_output_mounting_nut_wrench_size" = {self.output_mounting_nut_wrench_size1}\n',
        # f'"a1_output_mounting_nut_thickness" = {self.output_mounting_nut_thickness1}\n',
        # f'"a1_case_mounting_hole_allen_socket_dia" = {self.case_mounting_hole_allen_socket_dia}\n',
        f'"a1_output_mounting_nut_depth" = {self.output_mounting_nut_depth1}\n',
        f'"a1_case_mounting_bolt_depth" = {self.case_mounting_bolt_depth}\n',
        f'"a1_ring_radial_thickness" = {self.ring_radial_thickness}\n',
        # f'"a1_ring_OD" = {self.ring_OD1}\n',
        f'"a1_ring_to_chamfer_clearance" = {self.ring_to_chamfer_clearance1}\n',
        f'"a1_Motor_case_OD_base_to_chamfer" = {self.Motor_case_OD_base_to_chamfer}\n',
        f'"a1_pattern_offset_from_motor_case_OD_base" = {self.pattern_offset_from_motor_case_OD_base}\n',
        f'"a1_pattern_bulge_dia" = {self.pattern_bulge_dia}\n',
        f'"a1_pattern_num_bulge" = {self.pattern_num_bulge}\n',
        f'"a1_pattern_depth" = {self.pattern_depth}\n',
        # f'"a1_case_mounting_wrench_size" = {self.case_mounting_wrench_size}\n',
        f'"a1_case_mounting_nut_clearance" = {self.case_mounting_nut_clearance}\n',
        # f'"a1_base_plate_thickness" = {self.base_plate_thickness}\n',
        # f'"a1_case_mounting_nut_thickness" = {self.case_mounting_nut_thickness}\n',
        f'"a1_case_mounting_surface_height" = {self.case_mounting_surface_height}\n',
        # f'"a1_central_hole_offset_from_motor_mount_PCD" = {self.central_hole_offset_from_motor_mount_PCD}\n',
        # f'"a1_driver_upper_holes_dist_from_center" = {self.driver_upper_holes_dist_from_center}\n',
        # f'"a1_driver_lower_holes_dist_from_center" = {self.driver_lower_holes_dist_from_center}\n',
        # f'"a1_driver_side_holes_dist_from_center" = {self.driver_side_holes_dist_from_center}\n',
        # f'"a1_driver_mount_holes_dia" = {self.driver_mount_holes_dia}\n',
        # f'"a1_driver_mount_inserts_OD" = {self.driver_mount_inserts_OD}\n',
        # f'"a1_driver_mount_thickness" = {self.driver_mount_thickness}\n',
        # f'"a1_driver_mount_height" = {self.driver_mount_height}\n',
        # f'"a1_air_flow_hole_offset" = {self.air_flow_hole_offset}\n',
        f'"a1_planet_pin_bolt_dia" = {self.planet_pin_bolt_dia1}\n',
        f'"a1_planet_pin_socket_head_dia" = {self.planet_pin_socket_head_dia1}\n',
        f'"a1_carrier_PCD" = {self.carrier_PCD1}\n',
        f'"a1_planet_shaft_dia" = {self.planet_shaft_dia1}\n',
        f'"a1_planet_shaft_step_offset" = {self.planet_shaft_step_offset}\n',
        f'"a1_carrier_trapezoidal_support_sun_offset" = {self.carrier_trapezoidal_support_sun_offset1}\n',
        f'"a1_carrier_trapezoidal_support_hole_PCD_offset_bearing_ID" = {self.carrier_trapezoidal_support_hole_PCD_offset_bearing_ID1}\n',
        f'"a1_carrier_trapezoidal_support_hole_dia" = {self.carrier_trapezoidal_support_hole_dia1}\n',
        f'"a1_carrier_trapezoidal_support_hole_socket_head_dia" = {self.carrier_trapezoidal_support_hole_socket_head_dia1}\n',
        f'"a1_carrier_bearing_step_width" = {self.carrier_bearing_step_width}\n',
        f'"a1_standard_clearance_1_5mm" = {self.standard_clearance_1_5mm}\n',
        f'"a1_standard_fillet_1_5mm" = {self.standard_fillet_1_5mm}\n',
        f'"a1_sun_shaft_bearing_OD" = {self.sun_shaft_bearing_OD1}\n',
        f'"a1_sun_shaft_bearing_width" = {self.sun_shaft_bearing_width1}\n',
        f'"a1_standard_bearing_insertion_chamfer" = {self.standard_bearing_insertion_chamfer}\n',
        f'"a1_carrier_trapezoidal_support_hole_wrench_size" = {self.carrier_trapezoidal_support_hole_wrench_size1}\n',
        f'"a1_planet_pin_bolt_wrench_size" = {self.planet_pin_bolt_wrench_size1}\n',
        f'"a1_planet_bearing_OD" = {self.planet_bearing_OD1}\n',
        f'"a1_planet_bearing_width" = {self.planet_bearing_width1}\n',
        f'"a1_planet_bore" = {self.planet_bore1}\n',
        f'"a1_sun_shaft_bearing_ID" = {self.sun_shaft_bearing_ID1}\n',
        f'"a1_sun_hub_dia" = {self.sun_hub_dia1}\n',
        f'"a1_sun_central_bolt_dia" = {self.sun_central_bolt_dia1}\n',
        f'"a1_sun_central_bolt_socket_head_dia" = {self.sun_central_bolt_socket_head_dia1}\n',
        f'"a1_fw_s_used" = {self.fw_s1_used}\n',
        # f'"a1_motor_output_hole_CSK_OD" = {self.motor_output_hole_CSK_OD}\n',
        # f'"a1_motor_output_hole_CSK_head_height" = {self.motor_output_hole_CSK_head_height}\n',
        f'"a1_bearing_retainer_thickness" = {self.bearing_retainer_thickness1}\n',
        f'"a1_stg1_stg2_mounting_pattern_width" = {self.stg1_stg2_mounting_pattern_width}\n',
        f'"a1_stg1_stg2_allen_socket_head_dia" = {self.stg1_stg2_allen_socket_head_dia}\n',
        f'"a1_stg1_stg2_mounting_hole_dia" = {self.stg1_stg2_mounting_hole_dia}\n',
        f'"a1_Ns2" = {self.Ns2}\n',
        f'"a1_Np2" = {self.Np2}\n',
        f'"a1_Nr2" = {self.Nr2}\n',
        f'"a1_module2" = {self.module2}\n',
        # f'"a1_stg1_stg2_mounting_extra_width" = {self.stg1_stg2_mounting_extra_width}\n',
        f'"a1_dp_s2" = {self.dp_s2}\n',
        f'"a1_db_s2" = {self.db_s2}\n',
        f'"a1_fw_s_calc2" = {self.fw_s2_calc}\n',
        f'"a1_alpha_s2" = {self.alpha_s2}\n',
        f'"a1_beta_s2" = {self.beta_s2}\n',
        f'"a1_fw_s_used2" = {self.fw_s2_used}\n',
        f'"a1_fw_p2" = {self.fw_p2}\n',
        f'"a1_tight_clearance_3DP" = {self.tight_clearance_3DP}\n',
        f'"a1_loose_clearance_3DP" = {self.loose_clearance_3DP}\n' 



        f'"a2_Ns" = {self.Ns2}\n',
        f'"a2_Np" = {self.Np2}\n',
        f'"a2_Nr" = {self.Nr2}\n',
        f'"a2_module" = {self.module2}\n',
        f'"a2_pressure_angle" = {self.pressure_angle}\n',
        f'"a2_h_a" = {self.h_a2}\n',
        f'"a2_h_f" = {self.h_f2}\n',
        f'"a2_clr_tip_root" = {self.clr_tip_root2}\n',
        f'"a2_dp_r" = {self.dp_r2}\n',
        f'"a2_db_r" = {self.db_r2}\n',
        f'"a2_fw_r" = {self.fw_r2}\n',
        f'"a2_alpha_r" = {self.alpha_r2}\n',
        f'"a2_beta_r" = {self.beta_r2}\n',
        f'"a2_bearing_ID" = {self.bearing2_ID}\n',
        f'"a2_bearing_OD" = {self.bearing2_OD}\n',
        f'"a2_bearing_height" = {self.bearing2_height}\n',
        f'"a2_clearance_planet" = {self.clearance_planet}\n',
        # f'"a2_case_dist" = {self.case_dist2}\n',
        # f'"a2_Motor_case_OD_max" = {self.Motor_case_OD_max}\n',
        # f'"a2_case_mounting_PCD" = {self.case_mounting_PCD}\n',
        # f'"a2_bearing_mount_thickness" = {self.bearing_mount_thickness2}\n',
        f'"a2_case_mounting_hole_dia" = {self.case_mounting_hole_dia}\n',
        # f'"a2_output_mounting_PCD" = {self.output_mounting_PCD2}\n',
        f'"a2_output_mounting_hole_dia" = {self.output_mounting_hole_dia2}\n',
        f'"a2_clearance_case_mount_holes_shell_thickness" = {self.clearance_case_mount_holes_shell_thickness}\n',
        # f'"a2_motor_case_OD_base" = {self.motor_case_OD_base}\n',
        f'"a2_sec_carrier_thickness" = {self.sec_carrier_thickness2}\n',
        f'"a2_sun_coupler_hub_thickness" = {getattr(self, "sun_coupler_hub_thickness1", "N/A")}\n', # Note: Using stg1 value
        f'"a2_clearance_sun_coupler_sec_carrier" = {self.clearance_sun_coupler_sec_carrier}\n',
        # f'"a2_clearance_motor_and_case" = {self.clearance_motor_and_case}\n',
        # f'"a2_motor_OD" = {self.motor_OD}\n',
        # f'"a2_Motor_case_thickness" = {self.Motor_case_thickness}\n',
        # f'"a2_Motor_case_ID" = {self.Motor_case_ID}\n',
        # f'"a2_case_mounting_hole_shift" = {self.case_mounting_hole_shift}\n',
        f'"a2_output_mounting_nut_wrench_size" = {self.output_mounting_nut_wrench_size2}\n',
        # f'"a2_output_mounting_nut_thickness" = {self.output_mounting_nut_thickness2}\n',
        # f'"a2_case_mounting_hole_allen_socket_dia" = {self.case_mounting_hole_allen_socket_dia}\n',
        f'"a2_output_mounting_nut_depth" = {self.output_mounting_nut_depth2}\n',
        f'"a2_case_mounting_bolt_depth" = {self.case_mounting_bolt_depth}\n',
        f'"a2_ring_radial_thickness" = {self.ring_radial_thickness}\n',
        f'"a2_ring_OD" = {self.ring_OD2}\n',
        f'"a2_ring_to_chamfer_clearance" = {self.ring_to_chamfer_clearance2}\n',
        f'"a2_Motor_case_OD_base_to_chamfer" = {self.Motor_case_OD_base_to_chamfer}\n',
        f'"a2_pattern_offset_from_motor_case_OD_base" = {self.pattern_offset_from_motor_case_OD_base}\n',
        f'"a2_pattern_bulge_dia" = {self.pattern_bulge_dia}\n',
        f'"a2_pattern_num_bulge" = {self.pattern_num_bulge}\n',
        f'"a2_pattern_depth" = {self.pattern_depth}\n',
        # f'"a2_motor_height" = {self.motor_height}\n',
        # f'"a2_case_mounting_wrench_size" = {self.case_mounting_wrench_size}\n',
        f'"a2_case_mounting_nut_clearance" = {self.case_mounting_nut_clearance}\n',
        # f'"a2_base_plate_thickness" = {self.base_plate_thickness}\n',
        # f'"a2_case_mounting_nut_thickness" = {self.case_mounting_nut_thickness}\n',
        f'"a2_case_mounting_surface_height" = {self.case_mounting_surface_height}\n',
        # f'"a2_motor_mount_hole_PCD" = {self.motor_mount_hole_PCD}\n',
        # f'"a2_motor_mount_hole_dia" = {self.motor_mount_hole_dia}\n',
        # f'"a2_motor_mount_hole_num" = {self.motor_mount_hole_num}\n',
        # f'"a2_central_hole_offset_from_motor_mount_PCD" = {self.central_hole_offset_from_motor_mount_PCD}\n',
        # f'"a2_wire_slot_dist_from_center" = {self.wire_slot_dist_from_center}\n',
        # f'"a2_wire_slot_length" = {self.wire_slot_length}\n',
        # f'"a2_wire_slot_radius" = {self.wire_slot_radius}\n',
        # f'"a2_driver_upper_holes_dist_from_center" = {self.driver_upper_holes_dist_from_center}\n',
        # f'"a2_driver_lower_holes_dist_from_center" = {self.driver_lower_holes_dist_from_center}\n',
        # f'"a2_driver_side_holes_dist_from_center" = {self.driver_side_holes_dist_from_center}\n',
        # f'"a2_driver_mount_holes_dia" = {self.driver_mount_holes_dia}\n',
        # f'"a2_driver_mount_inserts_OD" = {self.driver_mount_inserts_OD}\n',
        # f'"a2_driver_mount_thickness" = {self.driver_mount_thickness}\n',
        # f'"a2_driver_mount_height" = {self.driver_mount_height}\n',
        # f'"a2_air_flow_hole_offset" = {self.air_flow_hole_offset}\n',
        f'"a2_num_planet" = {self.num_planet2}\n',
        f'"a2_planet_pin_bolt_dia" = {self.planet_pin_bolt_dia2}\n',
        f'"a2_planet_pin_socket_head_dia" = {self.planet_pin_socket_head_dia2}\n',
        f'"a2_carrier_PCD" = {self.carrier_PCD2}\n',
        f'"a2_planet_shaft_dia" = {self.planet_shaft_dia2}\n',
        f'"a2_fw_p" = {self.fw_p2}\n',
        f'"a2_planet_shaft_step_offset" = {self.planet_shaft_step_offset2}\n',
        f'"a2_carrier_trapezoidal_support_sun_offset" = {self.carrier_trapezoidal_support_sun_offset2}\n',
        f'"a2_carrier_trapezoidal_support_hole_PCD_offset_bearing_ID" = {self.carrier_trapezoidal_support_hole_PCD_offset_bearing_ID2}\n',
        f'"a2_carrier_trapezoidal_support_hole_dia" = {self.carrier_trapezoidal_support_hole_dia2}\n',
        f'"a2_carrier_trapezoidal_support_hole_socket_head_dia" = {self.carrier_trapezoidal_support_hole_socket_head_dia2}\n',
        f'"a2_carrier_bearing_step_width" = {self.carrier_bearing_step_width2}\n',
        f'"a2_standard_clearance_1_5mm" = {self.standard_clearance_1_5mm}\n',
        f'"a2_standard_fillet_1_5mm" = {self.standard_fillet_1_5mm}\n',
        f'"a2_sun_shaft_bearing_OD" = {self.sun_shaft_bearing_OD2}\n',
        f'"a2_sun_shaft_bearing_width" = {self.sun_shaft_bearing_width2}\n',
        f'"a2_standard_bearing_insertion_chamfer" = {self.standard_bearing_insertion_chamfer}\n',
        f'"a2_carrier_trapezoidal_support_hole_wrench_size" = {self.carrier_trapezoidal_support_hole_wrench_size2}\n',
        f'"a2_planet_pin_bolt_wrench_size" = {self.planet_pin_bolt_wrench_size2}\n',
        # f'"a2_pressure angle" = {self.pressure_angle}\n', 
        # f'"a2_motor_output_hole_PCD" = {self.motor_output_hole_PCD}\n',
        # f'"a2_motor_output_hole_dia" = {self.motor_output_hole_dia}\n',
        # f'"a2_motor_output_hole_num" = {self.motor_output_hole_num}\n',
        f'"a2_h_b" = {self.h_b2}\n',
        f'"a2_dp_s" = {self.dp_s2}\n',
        f'"a2_db_s" = {self.db_s2}\n',
        f'"a2_fw_s_calc" = {self.fw_s2_calc}\n',
        f'"a2_alpha_s" = {self.alpha_s2}\n',
        f'"a2_beta_s" = {self.beta_s2}\n',
        f'"a2_dp_p" = {self.dp_p2}\n',
        f'"a2_db_p" = {self.db_p2}\n',
        f'"a2_alpha_p" = {self.alpha_p2}\n',
        f'"a2_beta_p" = {self.beta_p2}\n',
        f'"a2_planet_bearing_OD" = {self.planet_bearing_OD2}\n',
        f'"a2_planet_bearing_width" = {self.planet_bearing_width2}\n',
        f'"a2_planet_bore" = {self.planet_bore2}\n',
        f'"a2_sun_shaft_bearing_ID" = {self.sun_shaft_bearing_ID2}\n',
        f'"a2_sun_hub_dia" = {self.sun_hub_dia1}\n', 
        f'"a2_sun_central_bolt_dia" = {self.sun_central_bolt_dia2}\n',
        f'"a2_sun_central_bolt_socket_head_dia" = {self.sun_central_bolt_socket_head_dia2}\n',
        f'"a2_fw_s_used" = {self.fw_s2_used}\n',
        # f'"a2_motor_output_hole_CSK_OD" = {self.motor_output_hole_CSK_OD}\n',
        # f'"a2_motor_output_hole_CSK_head_height" = {self.motor_output_hole_CSK_head_height}\n',
        f'"a2_bearing_retainer_thickness" = {self.bearing_retainer_thickness2}\n',
        f'"a2_Ns1" = {self.Ns1}\n',
        f'"a2_Np1" = {self.Np1}\n',
        f'"a2_Nr1" = {self.Nr1}\n',
        f'"a2_module1" = {self.module1}\n',
        f'"a2_bearing1_ID" = {self.bearing1_ID}\n',
        f'"a2_bearing1_OD" = {self.bearing1_OD}\n',
        f'"a2_bearing1_height1" = {self.bearing1_height}\n',
        # f'"a2_bearing_mount_thickness1" = {self.bearing_mount_thickness1}\n',
        # f'"a2_output_mounting_PCD1" = {self.output_mounting_PCD1}\n',
        f'"a2_num_planet1" = {self.num_planet1}\n',
        f'"a2_stg1_stg2_mounting_pattern_width" = {self.stg1_stg2_mounting_pattern_width}\n',
        f'"a2_stg1_stg2_allen_socket_head_dia" = {self.stg1_stg2_allen_socket_head_dia}\n',
        f'"a2_stg1_stg2_mounting_hole_dia" = {self.stg1_stg2_mounting_hole_dia}\n',
        # f'"a2_stg1_stg2_mounting_extra_width" = {self.stg1_stg2_mounting_extra_width}\n',
        f'"a2_tight_clearance_3DP" = {self.tight_clearance_3DP}\n',
        f'"a2_loose_clearance_3DP" = {self.loose_clearance_3DP}\n' 

#---------new_variables_added--------

        f'"Stator_wire_OD" = {self.stator_wire_OD}\n',
        f'"Stator_wire_ID" = {self.stator_wire_ID}\n',
        f'"stator_bottom_step_height_" = {self.stator_wire_bottom_height}\n',
        f'"stator_upper_step_height" = {self.stator_wire_top_height}\n',
        f'"stator_casing_hole_dia" = {self.stator_casing_hole_dia}\n',
        f'"stator_casing_thickness" = {self.stator_casing_thickness}\n',
        f'"stator_casing_hole_allen_socket_head_dia" = {self.stator_casing_hole_allen_socket_head_dia}\n',
        f'"stator_mounting_hole_num" = {self.stator_hole_num}\n',
        f'"stator_mounting_holes_dia" = {self.stator_hole_dia}\n',
        f'"stator_mounitng_holes_head_socket_dia" = {self.stator_mounting_holes_head_socket_dia}\n',
        f'"Stator_ID" = {self.stator_ID}\n',
        f'"Stator_OD" = {self.stator_OD}\n',
        f'"Stator_height" = {self.stator_height}\n',
        f'"Rotor_ID" = {self.rotor_ID}\n',
        f'"Rotor_OD" = {self.rotor_OD}\n',
        f'"Rotor_height" = {self.rotor_height}\n',
        f'"a2_bearing_retainer_hole_dia" = {self.a2_bearing_retainer_hole_dia}\n',
        f'"a2_bearing_retainer_hole_num" = {self.a2_bearing_retainer_hole_num}\n',
        f'"a2_bearing_retainer_nut_wrench_size" = {self.a2_bearing_retainer_nut_wrench_size}\n',
        f'"a2_bearing_retainer_wrench_height" = {self.a2_bearing_retainer_wrench_height}\n',
        f'"bearing_retainer_thickness" = {self.bearing_retainer_thickness}\n',
        f'"a1_sun_bottom_casing_bearing_ID" = {self.a1_sun_bottom_casing_bearing_ID}\n',
        f'"a1_sun_bottom_casing_bearing_OD" = {self.a1_sun_bottom_casing_bearing_OD}\n',
        f'"a1_sun_bottom_casing_bearing_height" = {self.a1_sun_bottom_casing_bearing_height}\n',
        f'"rotor_mount_hole_PCD" = {self.rotor_mount_hole_PCD}\n',
        f'"rotor_mount_hole_dia" = {self.rotor_mount_hole_dia}\n',
        f'"rotor_mount_hole_num" = {self.rotor_mount_hole_num}\n',
        f'"Rotor_csk_head_upper_dia" = {self.rotor_csk_head_upper_dia}\n',
        f'"Rotor_csk_head_height" = {self.rotor_csk_head_height}\n',
        f'"stator_mounting_hole_wrench_dia" = {self.stator_mounting_hole_wrench_dia}\n',
        f'"stator_mounting_hole_wrench_thickness" = {self.stator_mounting_hole_wrench_thickness}\n'
    ]

    def genEquationFile(self, motor_name="NO_MOTOR", gearRatioLL=0.0, gearRatioUL=0.0):
            self.setVariables()
            lines = self._equation_lines()
            path_sw = os.path.join(os.path.dirname(__file__), 'CADs', 'INDSPG', 'Equation_Files',
                                   motor_name, f'indspg_equations_{gearRatioLL}_{gearRatioUL}.txt')
            os.makedirs(os.path.dirname(path_sw), exist_ok=True)
            with open(path_sw, 'w') as f:
                f.writelines(lines)
            path_os = os.path.join(os.path.dirname(__file__), 'CADs', 'INDSPG', 'Equation_Files',
                                   motor_name, f'indspg_equations_{gearRatioLL}_{gearRatioUL}_onshape.txt')
            with open(path_os, 'w') as f:
                f.writelines(lines)
    
    def genEquationFile_editCADdirectly(self):
        self.setVariables()
        lines = self._equation_lines()
        path_sw = os.path.join(os.path.dirname(__file__), 'CADs', 'INDSPG', 'indspg_equations.txt')
        os.makedirs(os.path.dirname(path_sw), exist_ok=True)
        with open(path_sw, 'w') as f:
            f.writelines(lines)
        path_os = os.path.join(os.path.dirname(__file__), 'CADs', 'INDSPG', 'indspg_equations_onshape.txt')
        with open(path_os, 'w') as f:
            f.writelines(lines)


    #--------------------------------
    # Update Facewidths
    #--------------------------------
    def getToothForces(self, constraintCheck=True):
        if constraintCheck:
            # Check if the constraints are satisfied
            if not self.inrunnerdoubleStagePlanetaryGearbox.Stage1.geometricConstraint():
                print("Geometric constraint not satisfied in Layer 1")
                return
            if not self.inrunnerdoubleStagePlanetaryGearbox.Stage1.meshingConstraint():
                print("Meshing constraint not satisfied in Layer 1")
                return
            if not self.inrunnerdoubleStagePlanetaryGearbox.Stage1.noPlanetInterferenceConstraint():
                print("No planet interference constraint not satisfied in Layer 1")
                return
            if not self.inrunnerdoubleStagePlanetaryGearbox.Stage2.geometricConstraint():
                print("Geometric constraint not satisfied in Layer 2")
                return
            if not self.inrunnerdoubleStagePlanetaryGearbox.Stage2.meshingConstraint():
                print("Meshing constraint not satisfied in Layer 2")
                return
            if not self.inrunnerdoubleStagePlanetaryGearbox.Stage2.noPlanetInterferenceConstraint():
                print("No planet interference constraint not satisfied in Layer 2")
                return
        
        Ns1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.Ns
        Np1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.Np
        Nr1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.Nr
        module1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.module
        numPlanet1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.numPlanet

        Ns2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.Ns
        Np2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.Np
        Nr2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.Nr
        module2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.module
        numPlanet2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.numPlanet

        Rs1_Mt = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.getPCRadiusSunM()
        Rp1_Mt = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.getPCRadiusPlanetM()
        Rr1_Mt = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.getPCRadiusRingM()

        Rs2_Mt = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.getPCRadiusSunM()
        Rp2_Mt = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.getPCRadiusPlanetM()
        Rr2_Mt = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.getPCRadiusRingM()

        GR1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.gearRatio()
        GR2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.gearRatio()
        GR = GR1*GR2

        wSun1     = self.motor.getMaxMotorAngVelRadPerSec()
        wCarrier1 = wSun1 / GR1
        wPlanet1  = ( -Ns1 / (Nr1- Ns1) ) * wSun1
        
        wSun2     = wCarrier1
        wCarrier2 = wSun2 / GR2
        wPlanet2  = (- Ns2 / (Nr2 - Ns2)) * wSun2

        Ft1 = (self.serviceFactor*self.motor.getMaxMotorTorque())/(numPlanet1 * Rs1_Mt)
        Ft2 = (self.serviceFactor*self.motor.getMaxMotorTorque()*GR1)/(numPlanet2*Rs2_Mt)

        Ft = [Ft1, Ft2]
        return Ft

    def lewisStressAnalysisMinFacewidth(self):
        # Check if the constraints are satisfied
        if not self.inrunnerdoubleStagePlanetaryGearbox.Stage1.geometricConstraint():
            print("Geometric constraint not satisfied in Layer 1")
            return
        if not self.inrunnerdoubleStagePlanetaryGearbox.Stage1.meshingConstraint():
            print("Meshing constraint not satisfied in Layer 1")
            return
        if not self.inrunnerdoubleStagePlanetaryGearbox.noPlanetInterferenceConstraint():
            print("No planet interference constraint not satisfied")
            return
        if not self.inrunnerdoubleStagePlanetaryGearbox.Stage2.geometricConstraint():
            print("Geometric constraint not satisfied in Layer 2")
            return
        if not self.inrunnerdoubleStagePlanetaryGearbox.Stage2.meshingConstraint():
            print("Meshing constraint not satisfied in Layer 2")
            return
        # if not self.inrunnerdoubleStagePlanetaryGearbox.Stage2.noPlanetInterferenceConstraint():
        #     print("No planet interference constraint not satisfied in Layer 2")
        #     return
        
        Ns1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.Ns
        Np1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.Np
        Nr1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.Nr
        module1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.module
        numPlanet1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.numPlanet

        Ns2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.Ns
        Np2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.Np
        Nr2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.Nr
        module2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.module
        numPlanet2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.numPlanet

        Rs1_Mt = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.getPCRadiusSunM()
        Rp1_Mt = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.getPCRadiusPlanetM()
        Rr1_Mt = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.getPCRadiusRingM()

        Rs2_Mt = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.getPCRadiusSunM()
        Rp2_Mt = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.getPCRadiusPlanetM()
        Rr2_Mt = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.getPCRadiusRingM()

        GR1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.gearRatio()
        GR2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.gearRatio()
        GR = GR1*GR2

        wSun1     = self.motor.getMaxMotorAngVelRadPerSec()
        wCarrier1 = wSun1 / GR1
        wPlanet1  = ( -Ns1 / (Nr1- Ns1) ) * wSun1
        
        wSun2     = wCarrier1
        wCarrier2 = wSun2 / GR2
        wPlanet2  = (- Ns2 / (Nr2 - Ns2)) * wSun2

        Ft = self.getToothForces(False)

        Ft1 = Ft[0]
        Ft2 = Ft[1]

        ySun1    = 0.154 - 0.912 / Ns1
        yPlanet1 = 0.154 - 0.912 / Np1
        yRing1   = 0.154 - 0.912 / Nr1

        ySun2    = 0.154 - 0.912 / Ns2
        yPlanet2 = 0.154 - 0.912 / Np2
        yRing2   = 0.154 - 0.912 / Nr2

        V_sp1 = (Rs1_Mt *wSun1)
        V_rp1 = (wCarrier1 * (Rs1_Mt + Rp1_Mt) + wPlanet1 * (Rp1_Mt))
        
        V_sp2 = (Rs2_Mt*wSun2)
        V_rp2 = (wCarrier2*(Rs2_Mt + Rp2_Mt) + wPlanet2*(Rp2_Mt))
        
        if V_sp1 <= 7.5:
            Kv_sun1 = 3/(3+V_sp1)
        elif V_sp1 > 7.5 and V_sp1 <= 12.5:
            Kv_sun1 = 4.5/(4.5 + V_sp1)
        else:
            Kv_sun1 = 4.5/(4.5 + V_sp1)

        if V_rp1 <= 7.5:
            Kv_planet1 = 3/(3+V_rp1)
        elif V_rp1 > 7.5 and V_rp1 <= 12.5:
            Kv_planet1 = 4.5/(4.5 + V_rp1)

        if V_sp2 <= 7.5:
            Kv_sun2 = 3/(3+V_sp2)
        elif V_sp2 > 7.5 and V_sp2 <= 12.5:
            Kv_sun2 = 4.5/(4.5 + V_sp2)
        else:
            Kv_sun2 = 4.5/(4.5 + V_sp2)

        if V_rp2 <= 7.5:
            Kv_planet2 = 3/(3+V_rp2)
        elif V_rp2 > 7.5 and V_rp2 <= 12.5:
            Kv_planet2 = 4.5/(4.5 + V_rp2)

        Kv_ring1 = Kv_planet1
        Kv_ring2 = Kv_planet2

        P1 = np.pi*self.inrunnerdoubleStagePlanetaryGearbox.Stage1.module*0.001 # m
        P2 = np.pi*self.inrunnerdoubleStagePlanetaryGearbox.Stage2.module*0.001 # m

        bMin_sun1      = (self.FOS * Ft1 / (self.inrunnerdoubleStagePlanetaryGearbox.Stage1.maxGearAllowableStressPa * ySun1 * Kv_sun1 * P1)) # m
        bMin_planet1_1 = (self.FOS * Ft1 / (self.inrunnerdoubleStagePlanetaryGearbox.Stage1.maxGearAllowableStressPa * yPlanet1 * Kv_sun1 * P1))
        bMin_planet1_2 = (self.FOS * Ft1 / (self.inrunnerdoubleStagePlanetaryGearbox.Stage1.maxGearAllowableStressPa * yPlanet1 * Kv_planet1 * P1))
        bMin_ring1     = (self.FOS * Ft1 / (self.inrunnerdoubleStagePlanetaryGearbox.Stage1.maxGearAllowableStressPa * yRing1 * Kv_ring1 * P1)) 
  
        bMin_sun2      = (self.FOS * Ft2 / (self.inrunnerdoubleStagePlanetaryGearbox.Stage2.maxGearAllowableStressPa * ySun2 * Kv_sun2 * P2)) # m
        bMin_planet2_1 = (self.FOS * Ft2 / (self.inrunnerdoubleStagePlanetaryGearbox.Stage2.maxGearAllowableStressPa * yPlanet2 * Kv_sun2 * P2))
        bMin_planet2_2 = (self.FOS * Ft2 / (self.inrunnerdoubleStagePlanetaryGearbox.Stage2.maxGearAllowableStressPa * yPlanet2 * Kv_planet2 * P2))
        bMin_ring2     = (self.FOS * Ft2 / (self.inrunnerdoubleStagePlanetaryGearbox.Stage2.maxGearAllowableStressPa * yRing2 * Kv_ring2 * P2))

        if bMin_planet1_1 > bMin_planet1_2:
            bMin_planet1 = bMin_planet1_1
        else:
            bMin_planet1 = bMin_planet1_2

        if bMin_planet2_1 > bMin_planet2_2:
            bMin_planet2 = bMin_planet2_1
        else:
            bMin_planet2 = bMin_planet2_2

        if bMin_ring1 < bMin_planet1:
            bMin_ring1 = bMin_planet1
        else:
            bMin_planet1 = bMin_ring1

        if bMin_ring2 < bMin_planet2:
            bMin_ring2 = bMin_planet2
        else:
            bMin_planet2 = bMin_ring2

        self.inrunnerdoubleStagePlanetaryGearbox.Stage1.setfwSunMM(bMin_sun1*1000)
        self.inrunnerdoubleStagePlanetaryGearbox.Stage1.setfwPlanetMM(bMin_planet1*1000)
        self.inrunnerdoubleStagePlanetaryGearbox.Stage1.setfwRingMM(bMin_ring1*1000)
        self.inrunnerdoubleStagePlanetaryGearbox.Stage2.setfwSunMM(bMin_sun2*1000)
        self.inrunnerdoubleStagePlanetaryGearbox.Stage2.setfwPlanetMM(bMin_planet2*1000)
        self.inrunnerdoubleStagePlanetaryGearbox.Stage2.setfwRingMM(bMin_ring2*1000)

    def AGMAStressAnalysisMinFacewidth(self):
        # Check if the constraints are satisfied
        if not self.inrunnerdoubleStagePlanetaryGearbox.Stage1.geometricConstraint():
            print("Geometric constraint not satisfied in Layer 1")
            return
        if not self.inrunnerdoubleStagePlanetaryGearbox.Stage1.meshingConstraint():
            print("Meshing constraint not satisfied in Layer 1")
            return
        if not self.inrunnerdoubleStagePlanetaryGearbox.Stage1.noPlanetInterferenceConstraint():
            print("No planet interference constraint not satisfied in Layer 1")
            return
        if not self.inrunnerdoubleStagePlanetaryGearbox.Stage2.geometricConstraint():
            print("Geometric constraint not satisfied in Layer 2")
            return
        if not self.inrunnerdoubleStagePlanetaryGearbox.Stage2.meshingConstraint():
            print("Meshing constraint not satisfied in Layer 2")
            return
        if not self.inrunnerdoubleStagePlanetaryGearbox.Stage2.noPlanetInterferenceConstraint():
            print("No planet interference constraint not satisfied in Layer 2")
            return
        
        Ns1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.Ns
        Np1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.Np
        Nr1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.Nr
        module1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.module
        numPlanet1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.numPlanet

        Ns2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.Ns
        Np2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.Np
        Nr2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.Nr
        module2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.module
        numPlanet2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.numPlanet

        Rs1_Mt = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.getPCRadiusSunM()
        Rp1_Mt = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.getPCRadiusPlanetM()
        Rr1_Mt = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.getPCRadiusRingM()

        Rs2_Mt = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.getPCRadiusSunM()
        Rp2_Mt = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.getPCRadiusPlanetM()
        Rr2_Mt = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.getPCRadiusRingM()

        GR1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.gearRatio()
        GR2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.gearRatio()
        GR = GR1*GR2

        wSun1     = self.motor.getMaxMotorAngVelRadPerSec()
        wCarrier1 = wSun1 / GR1
        wPlanet1  = ( -Ns1 / (Nr1- Ns1) ) * wSun1
        
        wSun2     = wCarrier1
        wCarrier2 = wSun2 / GR2
        wPlanet2  = (- Ns2 / (Nr2 - Ns2)) * wSun2

        Wt = self.getToothForces(False)
        Wt1 = Wt[0]
        Wt2 = Wt[1]

        pressureAngle1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.pressureAngle
        pressureAngle2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.pressureAngle

        V_sp1 = abs(Rs1_Mt *wSun1)
        V_rp1 = abs(wCarrier1 * (Rs1_Mt + Rp1_Mt) + wPlanet1 * (Rp1_Mt))
        
        V_sp2 = abs(Rs2_Mt*wSun2)
        V_rp2 = abs(wCarrier2*(Rs2_Mt + Rp2_Mt) + wPlanet2*(Rp2_Mt))
        
        # T Krishna Rao - Design of Machine Elements - II pg.191
        # Modified Lewis Form Factor Y = pi*y for pressure angle = 20
        # Stage 1
        Y_planet1   = (0.154 - 0.912 / Np1) * np.pi
        Y_sun1   = (0.154 - 0.912 / Ns1) * np.pi
        Y_ring1   = (0.154 - 0.912 / Nr1) * np.pi
        # stage 2
        Y_planet2   = (0.154 - 0.912 / Np2) * np.pi
        Y_sun2   = (0.154 - 0.912 / Ns2) * np.pi
        Y_ring2   = (0.154 - 0.912 / Nr2) * np.pi

        # AGMA 908-B89 pg.16
        # Kf Fatigue stress concentration factor (Mitchiner and Mabie formula) 
        # t -> tooth thickness, r -> fillet radius and l -> tooth height
        # Stage 1
        H1 = 0.331 - (0.436 * np.pi * pressureAngle1 / 180)
        L1 = 0.324 - (0.492 * np.pi * pressureAngle1 / 180)
        M1 = 0.261 + (0.545 * np.pi * pressureAngle1 / 180)  

        t_planet1 = (13.5 * Y_planet1)**(1/2) * module1
        r_planet1 = 0.3 * module1
        l_planet1 = 2.25 * module1
        Kf_planet1 = H1 + (t_planet1 / r_planet1)**(L1) * (t_planet1 / l_planet1)**(M1)

        t_sun1 = (13.5 * Y_sun1)**(1/2) * module1
        r_sun1 = 0.3 * module1
        l_sun1 = 2.25 * module1
        Kf_sun1 = H1 + (t_sun1 / r_sun1)**(L1) * (t_sun1 / l_sun1)**(M1)

        t_ring1 = (13.5 * Y_ring1)**(1/2) * module1
        r_ring1 = 0.3 * module1
        l_ring1 = 2.25 * module1
        Kf_ring1 = H1 + (t_ring1 / r_ring1)**(L1) * (t_ring1 / l_ring1)**(M1)
        # Stage 2
        H2 = 0.331 - (0.436 * np.pi * pressureAngle2 / 180)
        L2 = 0.324 - (0.492 * np.pi * pressureAngle2 / 180)
        M2 = 0.261 + (0.545 * np.pi * pressureAngle2 / 180) 

        t_planet2 = (13.5 * Y_planet2)**(1/2) * module2
        r_planet2 = 0.3 * module2
        l_planet2 = 2.25 * module2
        Kf_planet2 = H2 + (t_planet2 / r_planet2)**(L2) * (t_planet2 / l_planet2)**(M2)

        t_sun2 = (13.5 * Y_sun2)**(1/2) * module2
        r_sun2 = 0.3 * module2
        l_sun2 = 2.25 * module2
        Kf_sun2 = H2 + (t_sun2 / r_sun2)**(L2) * (t_sun2 / l_sun2)**(M2)

        t_ring2 = (13.5 * Y_ring2)**(1/2) * module2
        r_ring2 = 0.3 * module2
        l_ring2 = 2.25 * module2
        Kf_ring2 = H2 + (t_ring2 / r_ring2)**(L2) * (t_ring2 / l_ring2)**(M2)

        # Shigley's Mechanical Engineering Design 9th Edition pg.752
        # Yj Geometry factor
        # Stage 1
        Yj_planet1 = Y_planet1/Kf_planet1
        Yj_sun1 = Y_sun1/Kf_sun1
        Yj_ring1 = Y_ring1/Kf_ring1 
        # Stage 2
        Yj_planet2 = Y_planet2/Kf_planet2
        Yj_sun2 = Y_sun2/Kf_sun2
        Yj_ring2 = Y_ring2/Kf_ring2 

        # Kv Dynamic factor
        # Shigley's Mechanical Engineering Design 9th Edition pg.756
        # Stage 1
        Qv1 = 7      # Quality numbers 3 to 7 will include most commercial-quality gears.
        B_planet1 =  0.25*(12-Qv1)**(2/3)
        A_planet1 = 50 + 56*(1-B_planet1)
        Kv_planet1 = ((A_planet1+np.sqrt(200*max(V_rp1, V_sp1)))/A_planet1)**B_planet1

        B_sun1 =  0.25*(12-Qv1)**(2/3)
        A_sun1 = 50 + 56*(1-B_sun1)
        Kv_sun1 = ((A_sun1+np.sqrt(200*V_sp1))/A_sun1)**B_sun1

        B_ring1 =  0.25*(12-Qv1)**(2/3)
        A_ring1 = 50 + 56*(1-B_ring1)
        Kv_ring1 = ((A_ring1+np.sqrt(200*V_rp1))/A_ring1)**B_ring1
        # Stage 2
        Qv2 = 7
        B_planet2 =  0.25*(12-Qv2)**(2/3)
        A_planet2 = 50 + 56*(1-B_planet2)
        Kv_planet2 = ((A_planet2+np.sqrt(200*max(V_rp2, V_sp2)))/A_planet2)**B_planet2

        B_sun2 =  0.25*(12-Qv2)**(2/3)
        A_sun2 = 50 + 56*(1-B_sun2)
        Kv_sun2 = ((A_sun2+np.sqrt(200*V_sp2))/A_sun2)**B_sun2

        B_ring2 =  0.25*(12-Qv2)**(2/3)
        A_ring2 = 50 + 56*(1-B_ring2)
        Kv_ring2 = ((A_ring2+np.sqrt(200*V_rp2))/A_ring2)**B_ring2

        # Shigley's Mechanical Engineering Design 9th Edition pg.764
        # Ks Size factor (can be omitted if enough information is not available)
        # Stage 1 = Stage 2
        Ks = 1

        # NPTEL Fatigue Consideration in Design lecture-7 pg.10 Table-7.4 (https://archive.nptel.ac.in/courses/112/106/112106137/)
        # Kh Load-distribution factor (0-50mm, less rigid mountings, less accurate gears)
        # Stage 1 = Stage 2
        Kh = 1.3

        # Shigley's Mechanical Engineering Design 9th Edition pg.764
        # Kb Rim-thickness factor (the gears have a uniform thickness)
        # Stage 1 = Stage 2
        Kb = 1

        # Stage 1
        bMin_planet1 = (self.FOS * Wt1 * Kv_planet1 * Ks * Kh * Kb)/(module1 * Yj_planet1 * self.inrunnerdoubleStagePlanetaryGearbox.Stage1.maxGearAllowableStressPa * 0.001)
        bMin_sun1 = (self.FOS * Wt1 * Kv_sun1 * Ks * Kh * Kb) / (module1 * Yj_sun1 * self.inrunnerdoubleStagePlanetaryGearbox.Stage1.maxGearAllowableStressPa * 0.001)
        bMin_ring1 = (self.FOS * Wt1 * Kv_ring1 * Ks * Kh * Kb) / (module1 * Yj_ring1 * self.inrunnerdoubleStagePlanetaryGearbox.Stage1.maxGearAllowableStressPa * 0.001)
        # Stage 2
        bMin_planet2 = (self.FOS * Wt2 * Kv_planet2 * Ks * Kh * Kb)/(module2 * Yj_planet2 * self.inrunnerdoubleStagePlanetaryGearbox.Stage2.maxGearAllowableStressPa * 0.001)
        bMin_sun2 = (self.FOS * Wt2 * Kv_sun2 * Ks * Kh * Kb) / (module2 * Yj_sun2 * self.inrunnerdoubleStagePlanetaryGearbox.Stage2.maxGearAllowableStressPa * 0.001)
        bMin_ring2 = (self.FOS * Wt2 * Kv_ring2 * Ks * Kh * Kb) / (module2 * Yj_ring2 * self.inrunnerdoubleStagePlanetaryGearbox.Stage2.maxGearAllowableStressPa * 0.001)

        if bMin_ring1 < bMin_planet1:
            bMin_ring1 = bMin_planet1
        else:
            bMin_planet1 = bMin_ring1

        if bMin_ring2 < bMin_planet2:
            bMin_ring2 = bMin_planet2
        else:
            bMin_planet2 = bMin_ring2

        self.inrunnerdoubleStagePlanetaryGearbox.Stage1.setfwSunMM(bMin_sun1*1000)
        self.inrunnerdoubleStagePlanetaryGearbox.Stage1.setfwPlanetMM(bMin_planet1*1000)
        self.inrunnerdoubleStagePlanetaryGearbox.Stage1.setfwRingMM(bMin_ring1*1000)
        self.inrunnerdoubleStagePlanetaryGearbox.Stage2.setfwSunMM(bMin_sun2*1000)
        self.inrunnerdoubleStagePlanetaryGearbox.Stage2.setfwPlanetMM(bMin_planet2*1000)
        self.inrunnerdoubleStagePlanetaryGearbox.Stage2.setfwRingMM(bMin_ring2*1000)

    def mitStressAnalysisMinFacewidth(self):
        # Check if the constraints are satisfied
        if not self.inrunnerdoubleStagePlanetaryGearbox.Stage1.geometricConstraint():
            print("Geometric constraint not satisfied in Layer 1")
            return
        if not self.inrunnerdoubleStagePlanetaryGearbox.Stage1.meshingConstraint():
            print("Meshing constraint not satisfied in Layer 1")
            return
        if not self.inrunnerdoubleStagePlanetaryGearbox.noPlanetInterferenceConstraint():
            print("No planet interference constraint not satisfied")
            return
        if not self.inrunnerdoubleStagePlanetaryGearbox.Stage2.geometricConstraint():
            print("Geometric constraint not satisfied in Layer 2")
            return
        if not self.inrunnerdoubleStagePlanetaryGearbox.Stage2.meshingConstraint():
            print("Meshing constraint not satisfied in Layer 2")
            return
        # if not self.inrunnerdoubleStagePlanetaryGearbox.Stage2.noPlanetInterferenceConstraint():
        #     print("No planet interference constraint not satisfied in Layer 2")
        #     return
        
        Ns1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.Ns
        Np1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.Np
        Nr1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.Nr
        module1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.module
        numPlanet1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.numPlanet

        Ns2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.Ns
        Np2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.Np
        Nr2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.Nr
        module2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.module
        numPlanet2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.numPlanet

        Rs1_Mt = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.getPCRadiusSunM()
        Rp1_Mt = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.getPCRadiusPlanetM()
        Rr1_Mt = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.getPCRadiusRingM()

        Rs2_Mt = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.getPCRadiusSunM()
        Rp2_Mt = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.getPCRadiusPlanetM()
        Rr2_Mt = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.getPCRadiusRingM()

        GR1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.gearRatio()
        GR2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.gearRatio()
        GR = GR1*GR2

        wSun1     = self.motor.getMaxMotorAngVelRadPerSec()
        wCarrier1 = wSun1 / GR1
        wPlanet1  = ( -Ns1 / (Nr1- Ns1) ) * wSun1
        
        wSun2     = wCarrier1
        wCarrier2 = wSun2 / GR2
        wPlanet2  = (- Ns2 / (Nr2 - Ns2)) * wSun2

        Ft = self.getToothForces(False)

        Ft1 = Ft[0]
        Ft2 = Ft[1]

        _,_,CR1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.contactRatio_sunPlanet()
        qe1 = 1 / CR1
        # qk = 1.85 + 0.35 * (np.log(Ns) / np.log(100)) 
        qk1 = (7.65734266e-08 * Ns1**4
            - 2.19500130e-05 * Ns1**3
            + 2.33893357e-03 * Ns1**2
            - 1.13320908e-01 * Ns1
            + 4.44727778)
        bMin_sun_mit1    = (self.FOS * Ft1 * qe1 * qk1 / (self.inrunnerdoubleStagePlanetaryGearbox.Stage1.maxGearAllowableStressPa * module1 * 0.001)) # m
        bMin_planet_mit1 = (self.FOS * Ft1 * qe1 * qk1 / (self.inrunnerdoubleStagePlanetaryGearbox.Stage1.maxGearAllowableStressPa * module1 * 0.001))
        bMin_ring_mit1   = (self.FOS * Ft1 * qe1 * qk1 / (self.inrunnerdoubleStagePlanetaryGearbox.Stage1.maxGearAllowableStressPa * module1 * 0.001))


        _,_,CR2 = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.contactRatio_sunPlanet()
        qe2 = 1 / CR2
        # qk = 1.85 + 0.35 * (np.log(Ns) / np.log(100)) 
        qk2 = (7.65734266e-08 * Ns2**4
            - 2.19500130e-05 * Ns2**3
            + 2.33893357e-03 * Ns2**2
            - 1.13320908e-01 * Ns2
            + 4.44727778)
        bMin_sun_mit2    = (self.FOS * Ft2 * qe2 * qk2 / (self.inrunnerdoubleStagePlanetaryGearbox.Stage2.maxGearAllowableStressPa * module2 * 0.001)) # m
        bMin_planet_mit2 = (self.FOS * Ft2 * qe2 * qk2 / (self.inrunnerdoubleStagePlanetaryGearbox.Stage2.maxGearAllowableStressPa * module2 * 0.001))
        bMin_ring_mit2   = (self.FOS * Ft2 * qe2 * qk2 / (self.inrunnerdoubleStagePlanetaryGearbox.Stage2.maxGearAllowableStressPa * module2 * 0.001))

        #------------- Contraint in planet to accomodate its bearings------------------------------------------
        if (bMin_planet_mit1 * 1000 < (self.planet_bearing_width1*2 + self.standard_clearance_1_5mm * 2 / 3)) : 
            bMin_planet_mit1 = (self.planet_bearing_width1*2 + self.standard_clearance_1_5mm * 2 / 3) / 1000
            bMin_ring_mit1 = bMin_planet_mit1 # FT on both are same

        if (bMin_planet_mit2 * 1000 < (self.planet_bearing_width2*2 + self.standard_clearance_1_5mm * 2 / 3)) : 
            bMin_planet_mit2 = (self.planet_bearing_width2*2 + self.standard_clearance_1_5mm * 2 / 3) / 1000
            bMin_ring_mit2 = bMin_planet_mit2 # FT on both are same



        self.inrunnerdoubleStagePlanetaryGearbox.Stage1.setfwSunMM      (bMin_sun_mit1*1000)
        self.inrunnerdoubleStagePlanetaryGearbox.Stage1.setfwPlanetMM   (bMin_planet_mit1*1000)
        self.inrunnerdoubleStagePlanetaryGearbox.Stage1.setfwRingMM     (bMin_ring_mit1*1000)
        self.inrunnerdoubleStagePlanetaryGearbox.Stage2.setfwSunMM      (bMin_sun_mit2*1000)
        self.inrunnerdoubleStagePlanetaryGearbox.Stage2.setfwPlanetMM   (bMin_planet_mit2*1000)
        self.inrunnerdoubleStagePlanetaryGearbox.Stage2.setfwRingMM     (bMin_ring_mit2*1000)

        bMin_sun_mit1MM    = bMin_sun_mit1    * 1000
        bMin_planet_mit1MM = bMin_planet_mit1 * 1000
        bMin_ring_mit1MM   = bMin_ring_mit1   * 1000

        bMin_sun_mit2MM    = bMin_sun_mit2    * 1000
        bMin_planet_mit2MM = bMin_planet_mit2 * 1000
        bMin_ring_mit2MM   = bMin_ring_mit2   * 1000

        return bMin_sun_mit1MM, bMin_planet_mit1MM, bMin_ring_mit1MM, bMin_sun_mit2MM, bMin_planet_mit2MM, bMin_ring_mit2MM

    def updateFacewidth(self):
        if self.stressAnalysisMethodName == "Lewis":
            self.lewisStressAnalysisMinFacewidth()
        elif self.stressAnalysisMethodName == "AGMA":
            self.AGMAStressAnalysisMinFacewidth()
        elif self.stressAnalysisMethodName == "MIT":
            self.mitStressAnalysisMinFacewidth()

    def getMassKG_3DP_stg1(self):
        module    = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.module
        Ns        = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.Ns
        Np        = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.Np
        Nr        = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.Nr
        numPlanet = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.numPlanet
        module2    = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.module
        Ns2        = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.Ns
        # Np        = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.Np
        Nr2         = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.Nr
        # numPlanet = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.numPlanet

        #------------------------------------
        # density of materials
        #------------------------------------
        density_3DP_material = self.inrunnerdoubleStagePlanetaryGearbox.densityGears

        #------------------------------------
        # Face Width
        #------------------------------------
        sunFwMM     = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.fwSunMM
        planetFwMM  = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.fwPlanetMM
        ringFwMM    = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.fwRingMM
        # sun2FwMM     = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.fwSunMM
        planet2FwMM  = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.fwPlanetMM
        # ring2FwMM    = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.fwRingMM

        sunFwM    = sunFwMM    * 0.001
        planetFwM = planetFwMM * 0.001
        ringFwM   = ringFwMM   * 0.001

        #------------------------------------
        # Diameter and Radius
        #------------------------------------
        DiaSunMM    = Ns * module
        DiaPlanetMM = Np * module
        DiaRingMM   = Nr * module

        Dia2SunMM    = Ns2 * module2
        # Dia2PlanetMM = Np2 * module2
        # Dia2RingMM   = Nr2 * module2

        RadiusSunMM    = DiaSunMM    * 0.5
        RadiusPlanetMM = DiaPlanetMM * 0.5
        RadiusRingMM   = DiaRingMM   * 0.5
        
        #------------------------------------
        # Bearing Selection
        #------------------------------------
        IdrequiredMM      = module * (Ns + Np) + self.bearingIDClearanceMM
        Bearings          = bearings_discrete(IdrequiredMM)
        InnerDiaBearingMM = Bearings.getBearingIDMM()
        OuterDiaBearingMM = Bearings.getBearingODMM()
        WidthBearingMM    = Bearings.getBearingWidthMM()
        BearingMassKG     = Bearings.getBearingMassKG()

        self.Bearing_ID_stg1_MM        = 38.1 # Bearings.getBearingIDMM()
        self.Bearing_OD_stg1_MM        = 47.625 # Bearings.getBearingODMM()
        self.Bearing_thickness_stg1_MM = 4.763 # Bearings.getBearingWidthMM()
        self.Bearing_mass_stg1_KG      = 0.0227 # Bearings.getBearingMassKG()

        #======================================
        # Mass Calculation
        #======================================
        #--------------------------------------
        # Independent variables
        #--------------------------------------
        # To be written in Gearbox(dspg) JSON files
        case_mounting_surface_height    = self.case_mounting_surface_height
        standard_clearance_1_5mm        = self.standard_clearance_1_5mm    
        stator_casing_thickness         = self.stator_casing_thickness        
        #Motor_case_thickness            = self.Motor_case_thickness        
        clearance_planet                = self.clearance_planet            
        output_mounting_hole_dia        = self.output_mounting_hole_dia1    
        sec_carrier_thickness           = self.sec_carrier_thickness1       
        sun_coupler_hub_thickness       = self.sun_coupler_hub_thickness1   
        sun_shaft_bearing_OD            = self.sun_shaft_bearing_OD1        
        carrier_bearing_step_width      = self.carrier_bearing_step_width  
        planet_shaft_dia                = self.planet_shaft_dia1            
        sun_shaft_bearing_ID            = self.sun_shaft_bearing_ID1        
        sun_shaft_bearing_width         = self.sun_shaft_bearing_width1     
        planet_bore                     = self.planet_bore1                 
        bearing_retainer_thickness      = self.bearing_retainer_thickness1  
        stg1_stg2_allen_socket_head_dia = self.stg1_stg2_allen_socket_head_dia

        #--------------------------------------
        # Dependent variables
        #--------------------------------------
        h_b = 1.25 * module

        #--------------------------------------
        # Mass: dspg_motor_casing
        #--------------------------------------
        middle_casing_VOL = np.pi * (self.stator_height-self.stator_wire_top_height+standard_clearance_1_5mm*2.5) * ((self.stator_OD/2+self.stator_casing_thickness)**2 - (self.stator_OD/2)**2) * 1e-9
                
        bottom_casing_plate_VOL = np.pi * (self.stator_casing_thickness) * ((self.stator_OD/2+self.stator_casing_thickness)**2) * 1e-9 + np.pi * (standard_clearance_1_5mm) * ((self.stator_OD/2+self.stator_casing_thickness)**2 - (self.stator_OD/2+self.stator_casing_thickness-2.5)**2)* 1e-9
        #bottom_casing_step_height_VOL = np.pi * (self.stator_bottom_step_height_-self.standard_clearance_1_5mm) * ((50/2)**2) * 1e-9 + np.pi * (standard_clearance_1_5mm) * ((self.rotor_support_bearing_ID/2+standard_clearance_1_5mm*2)**2)*1e-9
        bottom_casing_bearing_support_VOL = np.pi * (self.a1_sun_bottom_casing_bearing_height - (self.stator_casing_thickness - self.standard_clearance_1_5mm))* ((self.a1_sun_bottom_casing_bearing_OD/2+standard_clearance_1_5mm*2)**2) * 1e-9
        bottom_casing_hole_VOL = np.pi * (self.a1_sun_bottom_casing_bearing_height - (self.stator_casing_thickness - self.standard_clearance_1_5mm)+self.stator_casing_thickness)*((self.a1_sun_bottom_casing_bearing_OD/2)**2)*1e-9

        bottom_casing_vol = bottom_casing_plate_VOL+bottom_casing_bearing_support_VOL - bottom_casing_hole_VOL + 4*np.pi*2*((9/2)**2-(5.5/2)**2)*1e-9

        Motor_case_vol = middle_casing_VOL+bottom_casing_vol
        Motor_case_mass = Motor_case_vol * density_3DP_material


        #--------------------------------------
        # Mass: ring_gear
        #--------------------------------------
        ring_ID        = Nr * module
        ringFwUsedMM   = ringFwMM 

        bearing_ID     = InnerDiaBearingMM 
        bearing_OD     = OuterDiaBearingMM 
        bearing_height = WidthBearingMM    
        bearing_mass   = BearingMassKG      

        step_above_rotor = (ringFwUsedMM - self.rotor_height - self.loose_clearance_3DP 
                    - self.stator_wire_bottom_height - self.stator_casing_thickness 
                    + self.a1_sun_bottom_casing_bearing_height/2 + 2 
                    + self.sun_coupler_hub_thickness1 + self.standard_clearance_1_5mm 
                    + self.sec_carrier_thickness1 + self.clearance_planet)

        ring_gear_volume = ((np.pi * (((self.rotor_ID-self.loose_clearance_3DP*2)*0.5)**2 - ((ring_ID*0.5)**2)) * ringFwUsedMM) )* 1e-9
        top_support_vol = ((np.pi * (((self.stator_OD+self.stator_casing_thickness*2)*0.5)**2 - ((self.stator_wire_ID)*0.5)**2)) * stator_casing_thickness) * 1e-9
        casing_support_vol = ((np.pi * (((self.stator_OD+self.stator_casing_thickness*2)*0.5)**2 - (((self.stator_wire_OD+self.tight_clearance_3DP))*0.5)**2)) * (self.stator_wire_top_height+self.loose_clearance_3DP)) * 1e-9
        bearing_support_vol1 = (np.pi * (self.bearing1_height+self.loose_clearance_3DP+self.standard_clearance_1_5mm*2) * ((self.stator_wire_ID*0.5)**2 - ((self.bearing1_OD*0.5)**2))) * 1e-9
        bearing_support_vol2 = (np.pi * (self.loose_clearance_3DP+self.standard_clearance_1_5mm*2) * ((self.bearing1_OD*0.5)**2 - (((self.bearing1_ID-self.standard_clearance_1_5mm*3)*0.5)**2))) * 1e-9
        bearing_support_vol3 = (np.pi * (self.standard_clearance_1_5mm*2) * (((self.bearing1_ID-self.standard_clearance_1_5mm*3)*0.5)**2 - (((ring_ID+self.loose_clearance_3DP+self.standard_clearance_1_5mm*4)*0.5)**2))) * 1e-9
        step_above_rotor_vol = (np.pi * (step_above_rotor) * ((self.stator_wire_ID*0.5)**2 - ((ring_ID*0.5)**2))) * 1e-9

        ring_gear_mass = (ring_gear_volume + top_support_vol + casing_support_vol + bearing_support_vol1 + bearing_support_vol2 + bearing_support_vol3 + step_above_rotor_vol) * density_3DP_material
        


        #----------------------------------
        # Mass: dspg_carrier
        #----------------------------------
        carrier_OD     = bearing_ID
        carrier_ID     = sun_shaft_bearing_OD - standard_clearance_1_5mm * 2
        carrier_height = bearing_height + carrier_bearing_step_width

        carrier_shaft_OD = planet_shaft_dia
        carrier_shaft_height = planetFwMM + clearance_planet * 2
        carrier_shaft_num = numPlanet * 2

        #---------------------------------- new one

        r_carrier_outer     = (bearing_ID / 2) / 1000
        r_carrier_trapezoid = ((bearing_ID
                                - (self.Ns1 * self.module1 + 2 * self.carrier_trapezoidal_support_sun_offset1))
                               / 4) / 1000
        
        fw_carrier = self.fw_p1 / 1000

        # Volume sub-components
        vol_carrier_disk      = math.pi * (bearing_height / 1000) * r_carrier_outer     ** 2
        vol_carrier_trapezoid = math.pi * fw_carrier * r_carrier_trapezoid ** 2

        vol_carrier_net = vol_carrier_disk + 3 * vol_carrier_trapezoid   # 3 trapezoidal arms


        #----------------------------------

        carrier_volume = vol_carrier_net 

        sun2_shaft_dia    = sun_shaft_bearing_ID
        sun2_shaft_height = sun_shaft_bearing_width + 2 * standard_clearance_1_5mm

        fw_s2_used        = planet2FwMM + clearance_planet + sec_carrier_thickness + standard_clearance_1_5mm + self.loose_clearance_3DP

        sun2_gear_volume  = np.pi * ((Dia2SunMM * 0.5) ** 2-(self.sun_central_bolt_dia2*0.5)**2) * fw_s2_used * 1e-9
        sun2_shaft_volume = np.pi * ((sun2_shaft_dia*0.5) ** 2) * sun2_shaft_height * 1e-9

        sun2_volume       = sun2_gear_volume + sun2_shaft_volume
        sun2_mass         = sun2_volume * density_3DP_material

        carrier_mass = carrier_volume * density_3DP_material

        carrier_stg1_mass = sun2_mass + carrier_mass

        #----------------------------------
        # Mass: dspg_sun
        #----------------------------------
        sun_hub_dia = self.sun_hub_dia1

        sun_shaft_dia    = sun_shaft_bearing_ID
        sun_shaft_height = sun_shaft_bearing_width + 2 * standard_clearance_1_5mm

        fw_s_used        = planetFwMM + clearance_planet + sec_carrier_thickness + standard_clearance_1_5mm

        sun_hub_volume   = np.pi * ((sun_hub_dia*0.5) ** 2) * sun_coupler_hub_thickness * 1e-9
        sun_gear_volume  = np.pi * ((DiaSunMM * 0.5) ** 2) * fw_s_used * 1e-9
        sun_shaft_volume = np.pi * ((sun_shaft_dia*0.5) ** 2) * sun_shaft_height * 1e-9

        sun_volume       = sun_hub_volume + sun_gear_volume + sun_shaft_volume
        sun_mass         = sun_volume * density_3DP_material

        #--------------------------------------
        # Mass: dspg_planet
        #--------------------------------------
        planet_volume = (np.pi * ((DiaPlanetMM*0.5)**2 - (planet_bore*0.5)**2) * planetFwMM) * 1e-9
        planet_mass   = planet_volume * density_3DP_material

        #--------------------------------------
        # Mass: dspg_sec_carrier
        #--------------------------------------
        sec_carrier_OD = bearing_ID
        sec_carrier_ID = (DiaSunMM + DiaPlanetMM) - planet_shaft_dia - 2 * standard_clearance_1_5mm

        sec_carrier_volume = (np.pi * ((sec_carrier_OD*0.5)**2 - (sec_carrier_ID*0.5)**2) * sec_carrier_thickness) * 1e-9
        sec_carrier_mass   = sec_carrier_volume * density_3DP_material

        #--------------------------------------
        # Mass: dspg_sun_shaft_bearing
        #--------------------------------------
        sun_shaft_bearing_mass       = 4 * 0.001 # kg

        #--------------------------------------
        # Mass: dspg_planet_bearing
        #--------------------------------------
        planet_bearing_mass          = 1 * 0.001 # kg
        planet_bearing_num           = numPlanet * 2
        planet_bearing_combined_mass = planet_bearing_mass * planet_bearing_num

        #--------------------------------------
        # Mass: dspg_planet_bearing
        #--------------------------------------
        bearing_mass = BearingMassKG # kg

        #--------------------------------------
        # Mass: dspg_bearing_retainer
        #--------------------------------------
        #bearing_retainer_OD        = bearing_holding_structure_OD
        #bearing_retainer_ID        = bearing_OD - standard_clearance_1_5mm * 2


        #bearing_retainer_volume = (np.pi * ((bearing_retainer_OD*0.5)**2 - (bearing_retainer_ID*0.5)**2) * bearing_retainer_thickness) * 1e-9

        #bearing_retainer_mass   = bearing_retainer_volume * density_3DP_material

        self.Motor_case_mass_stg1              = Motor_case_mass
        self.ring_gear_mass_stg1               = ring_gear_mass
        #self.gearbox_casing_mass_stg1          = gearbox_casing_mass
        self.carrier_mass_stg1                 = carrier_stg1_mass
        self.sun_mass_stg1                     = sun_mass
        self.sec_carrier_mass_stg1             = sec_carrier_mass
        self.planet_mass_stg1                  = planet_mass
        self.planet_bearing_combined_mass_stg1 = planet_bearing_combined_mass
        self.sun_shaft_bearing_mass_stg1       = sun_shaft_bearing_mass
        self.bearing_mass_stg1                 = bearing_mass
       # self.bearing_retainer_mass_stg1        = bearing_retainer_mass

        #----------------------------------------
        # Total Actuator Mass
        #----------------------------------------
        Actuator_mass = (self.motorMassKG 
                        + self.Motor_case_mass_stg1 
                        + self.ring_gear_mass_stg1
                        #+ self.gearbox_casing_mass_stg1 
                        + self.carrier_mass_stg1 
                        + self.sun_mass_stg1 
                        + self.sec_carrier_mass_stg1 
                        + self.planet_mass_stg1 * numPlanet 
                        + self.planet_bearing_combined_mass_stg1 
                        + self.sun_shaft_bearing_mass_stg1 
                        + self.bearing_mass_stg1 
                        #+ self.bearing_retainer_mass_stg1
        )
        
        return Actuator_mass

    def getMassKG_3DP_stg2(self):
        module1    = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.module
        Ns1        = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.Ns
        Np1        = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.Np
        Nr1        = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.Nr
        numPlanet1 = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.numPlanet
        module     = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.module
        Ns         = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.Ns
        Np         = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.Np
        Nr         = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.Nr
        numPlanet  = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.numPlanet

        #------------------------------------
        # density of materials
        #------------------------------------
        density_3DP_material = self.inrunnerdoubleStagePlanetaryGearbox.densityGears

        #------------------------------------
        # Face Width
        #------------------------------------
        sun1FwMM     = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.fwSunMM
        planet1FwMM  = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.fwPlanetMM
        ring1FwMM    = self.inrunnerdoubleStagePlanetaryGearbox.Stage1.fwRingMM
        
        sunFwMM     = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.fwSunMM
        planetFwMM  = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.fwPlanetMM
        ringFwMM    = self.inrunnerdoubleStagePlanetaryGearbox.Stage2.fwRingMM

        sunFwM    = sunFwMM    * 0.001
        planetFwM = planetFwMM * 0.001
        ringFwM   = ringFwMM   * 0.001

        #------------------------------------
        # Diameter and Radius
        #------------------------------------
        Dia1SunMM    = Ns1 * module1
        Dia1PlanetMM = Np1 * module1
        Dia1RingMM   = Nr1 * module1

        DiaSunMM    = Ns * module
        DiaPlanetMM = Np * module
        DiaRingMM   = Nr * module

        RadiusSunMM    = DiaSunMM    * 0.5
        RadiusPlanetMM = DiaPlanetMM * 0.5
        RadiusRingMM   = DiaRingMM   * 0.5

        #------------------------------------
        # Bearing Selection
        #------------------------------------
        IdrequiredMM      = module * (Ns + Np) + self.bearingIDClearanceMM
        Bearings          = bearings_discrete(IdrequiredMM)
        InnerDiaBearingMM = Bearings.getBearingIDMM()
        OuterDiaBearingMM = Bearings.getBearingODMM()
        WidthBearingMM    = Bearings.getBearingWidthMM()
        BearingMassKG     = Bearings.getBearingMassKG()   

        #======================================
        # Mass Calculation
        #======================================
        #--------------------------------------
        # Independent variables
        #--------------------------------------
        # To be written in Gearbox(dspg) JSON files
        case_mounting_surface_height    = self.case_mounting_surface_height
        standard_clearance_1_5mm        = self.standard_clearance_1_5mm    
        #base_plate_thickness            = self.base_plate_thickness        
        #Motor_case_thickness            = self.Motor_case_thickness        
        clearance_planet                = self.clearance_planet            
        #output_mounting_hole_dia        = self.output_mounting_hole_dia2    
        sec_carrier_thickness           = self.sec_carrier_thickness2       
        sun_shaft_bearing_OD            = self.sun_shaft_bearing_OD2        
        carrier_bearing_step_width      = self.carrier_bearing_step_width  
        planet_shaft_dia                = self.planet_shaft_dia2            
        #sun_shaft_bearing_ID            = self.sun_shaft_bearing_ID2        
        #sun_shaft_bearing_width         = self.sun_shaft_bearing_width2     
        planet_bore                     = self.planet_bore2                 
        #bearing_retainer_thickness      = self.bearing_retainer_thickness2  
        #stg1_stg2_allen_socket_head_dia = self.stg1_stg2_allen_socket_head_dia
        

        #--------------------------------------
        # Dependent variables
        #--------------------------------------
        h_b = 1.25 * module

        #--------------------------------------
        # Mass: ring_gear
        #--------------------------------------

        ring_radial_thickness = self.ring_radial_thickness
        ring_ID               = Nr * module
        ring_OD               = Nr * module + ring_radial_thickness*2
        ringFwUsedMM          = ringFwMM + clearance_planet

        bearing_ID     = InnerDiaBearingMM 
        bearing_OD     = OuterDiaBearingMM 
        bearing_height = WidthBearingMM    
        bearing_mass   = BearingMassKG      

        ring_gear_volume = (np.pi * (((ring_OD*0.5)**2) - ((ring_ID*0.5)**2)) * ringFwUsedMM) * 1e-9
        ring_gear_mass   = ring_gear_volume * density_3DP_material

        #----------------------------------
        # Mass: dspg_carrier
        #----------------------------------
        carrier_OD     = bearing_ID
        carrier_ID     = sun_shaft_bearing_OD - standard_clearance_1_5mm * 2
        carrier_height = bearing_height + carrier_bearing_step_width

        carrier_shaft_OD = planet_shaft_dia
        carrier_shaft_height = planetFwMM + clearance_planet * 2
        carrier_shaft_num = numPlanet * 2

        carrier_volume = (np.pi * (((carrier_OD*0.5)**2) - ((carrier_ID)*0.5)**2) * carrier_height
                        + np.pi * ((carrier_shaft_OD*0.5)**2) * carrier_shaft_height * carrier_shaft_num) * 1e-9

        carrier_mass = carrier_volume * density_3DP_material

        #--------------------------------------
        # Mass: dspg_planet
        #--------------------------------------
        planet_volume = (np.pi * ((DiaPlanetMM*0.5)**2 - (planet_bore*0.5)**2) * planetFwMM) * 1e-9
        planet_mass   = planet_volume * density_3DP_material

        #--------------------------------------
        # Mass: dspg_sec_carrier
        #--------------------------------------
        sec_carrier_OD = bearing_ID
        sec_carrier_ID = (DiaSunMM + DiaPlanetMM) - planet_shaft_dia - 2 * standard_clearance_1_5mm

        sec_carrier_volume = (np.pi * ((sec_carrier_OD*0.5)**2 - (sec_carrier_ID*0.5)**2) * sec_carrier_thickness) * 1e-9
        sec_carrier_mass = sec_carrier_volume * density_3DP_material

        #--------------------------------------
        # Mass: dspg_sun_shaft_bearing
        #--------------------------------------
        sun_shaft_bearing_mass = 4 * 0.001 # kg

        #--------------------------------------
        # Mass: dspg_planet_bearing
        #--------------------------------------
        planet_bearing_mass          = 1 * 0.001 # kg
        planet_bearing_num           = numPlanet * 2
        planet_bearing_combined_mass = planet_bearing_mass * planet_bearing_num


        #--------------------------------------
        # Mass: dspg_bearing
        #--------------------------------------
        bearing_mass = BearingMassKG # kg

        #--------------------------------------
        # Mass: dspg_bearing_retainer
        #--------------------------------------
       # bearing_retainer_OD = bearing_holding_structure_OD
      #  bearing_retainer_ID = bearing_OD - standard_clearance_1_5mm * 2

      #  bearing_retainer_volume = (np.pi * ((bearing_retainer_OD * 0.5)**2 - (bearing_retainer_ID * 0.5)**2) * bearing_retainer_thickness) * 1e-9

      #  bearing_retainer_mass   = bearing_retainer_volume * density_3DP_material

       # self.gearbox_casing_mass_stg2          = gearbox_casing_mass
        self.ring_gear_mass_stg2                 = ring_gear_mass
        self.carrier_mass_stg2                 = carrier_mass
        self.sec_carrier_mass_stg2             = sec_carrier_mass
        self.planet_mass_stg2                  = planet_mass
        self.planet_bearing_combined_mass_stg2 = planet_bearing_combined_mass
        self.sun_shaft_bearing_mass_stg2       = sun_shaft_bearing_mass
        self.bearing_mass_stg2                 = bearing_mass
        #self.bearing_retainer_mass_stg2        = bearing_retainer_mass

        #----------------------------------------
        # Total Actuator Mass
        #----------------------------------------
        Actuator_mass = (self.ring_gear_mass_stg2
                       + self.carrier_mass_stg2 
                       + self.sec_carrier_mass_stg2 
                       + self.planet_mass_stg2 * numPlanet 
                       + self.planet_bearing_combined_mass_stg2 
                       + self.sun_shaft_bearing_mass_stg2 
                       + self.bearing_mass_stg2 
                      # + self.bearing_retainer_mass_stg2)
        )
        
        return Actuator_mass
        
    def getMassKG_3DP(self):
        totalMass = self.getMassKG_3DP_stg1() + self.getMassKG_3DP_stg2()
        #self.print_mass_of_parts_3DP()
        return totalMass

    def print_mass_of_parts_3DP(self):
        print("motorMassKG :", 1000 * self.motorMassKG )
        print("Motor_case_mass_stg1 :", 1000 * self.Motor_case_mass_stg1 )
        print("gearbox_casing_mass_stg1 :", 1000 * self.gearbox_casing_mass_stg1 )
        print("carrier_mass_stg1 :", 1000 * self.carrier_mass_stg1 )
        print("sun_mass_stg1 :", 1000 * self.sun_mass_stg1 )
        print("sec_carrier_mass_stg1 :", 1000 * self.sec_carrier_mass_stg1 )
        print("planet_mass_stg1 :", 1000 * self.planet_mass_stg1)
        print("planet_bearing_combined_mass_stg1 :", 1000 * self.planet_bearing_combined_mass_stg1 )
        print("sun_shaft_bearing_mass_stg1 :", 1000 * self.sun_shaft_bearing_mass_stg1 )
        print("bearing_mass_stg1 :", 1000 * self.bearing_mass_stg1 )
        print("bearing_retainer_mass_stg1 :", 1000 * self.bearing_retainer_mass_stg1)
        print("gearbox_casing_mass_stg2 :", 1000 * self.gearbox_casing_mass_stg2 )
        print("carrier_mass_stg2 :", 1000 * self.carrier_mass_stg2 )
        print("sec_carrier_mass_stg2 :", 1000 * self.sec_carrier_mass_stg2 )
        print("planet_mass_stg2 :", 1000 * self.planet_mass_stg2)
        print("planet_bearing_combined_mass_stg2 :", 1000 * self.planet_bearing_combined_mass_stg2 )
        print("sun_shaft_bearing_mass_stg2 :", 1000 * self.sun_shaft_bearing_mass_stg2 )
        print("bearing_mass_stg2 :", 1000 * self.bearing_mass_stg2 )
        print("bearing_retainer_mass_stg2 :", 1000 * self.bearing_retainer_mass_stg2)


#========================================================================
# Actuator Optimization
#========================================================================

#------------------------------------------------------------
# Class: Optimization of Double Stage Planetary Actuator
#------------------------------------------------------------
class optimizationDoubleStageActuator:
    def __init__(self,
                 design_parameters,
                 gear_standard_parameters,
                 K_Mass                = 1.0,
                 K_Eff                 = -2.0,
                 K_Width               = 0.2,
                 MODULE_STAGE1_MIN     = 0.5,
                 MODULE_STAGE1_MAX     = 1.2,
                 MODULE_STAGE2_MIN     = 0.5,
                 MODULE_STAGE2_MAX     = 1.2,
                 NUM_PLANET_STAGE1_MIN = 3,
                 NUM_PLANET_STAGE1_MAX = 5,
                 NUM_PLANET_STAGE2_MIN = 3,
                 NUM_PLANET_STAGE2_MAX = 5,
                 NUM_TEETH_SUN_MIN     = 20,
                 NUM_TEETH_PLANET_MIN  = 20,
                 GEAR_RATIO_MIN        = 5,
                 GEAR_RATIO_MAX        = 40,
                 GEAR_RATIO_STEP       = 5):
        self.K_Mass                = K_Mass               
        self.K_Eff                 = K_Eff                
        self.K_Width               = K_Width                
        self.MODULE_STAGE1_MIN     = MODULE_STAGE1_MIN    
        self.MODULE_STAGE1_MAX     = MODULE_STAGE1_MAX    
        self.MODULE_STAGE2_MIN     = MODULE_STAGE2_MIN    
        self.MODULE_STAGE2_MAX     = MODULE_STAGE2_MAX    
        self.NUM_PLANET_STAGE1_MIN = NUM_PLANET_STAGE1_MIN
        self.NUM_PLANET_STAGE1_MAX = NUM_PLANET_STAGE1_MAX
        self.NUM_PLANET_STAGE2_MIN = NUM_PLANET_STAGE2_MIN
        self.NUM_PLANET_STAGE2_MAX = NUM_PLANET_STAGE2_MAX
        self.NUM_TEETH_SUN_MIN     = NUM_TEETH_SUN_MIN    
        self.NUM_TEETH_PLANET_MIN  = NUM_TEETH_PLANET_MIN 
        self.GEAR_RATIO_MIN        = GEAR_RATIO_MIN       
        self.GEAR_RATIO_MAX        = GEAR_RATIO_MAX       
        self.GEAR_RATIO_STEP       = GEAR_RATIO_STEP  

        self.Cost                    = 100000
        self.totalGearboxesWithReqGR = 0
        self.totalFeasibleGearboxes  = 0
        self.cntrIterBeforeCons      = 0
        self.iter                    = 0
        self.gearRatioIter           = self.GEAR_RATIO_MIN 
        self.UsePSCasVariable        = 1 # Default   

        self.gear_standard_parameters = gear_standard_parameters
        self.design_parameters        = design_parameters

        self.gearRatioReq            = 0

    def optimizeActuator(self, Actuator=inrunnerdoubleStageActuator, UsePSCasVariable=0, log=1, csv=0, gearRatioReq = 0, printOptParams = 1):
        self.UsePSCasVariable = UsePSCasVariable
        totalTime = 0
        self.gearRatioReq = gearRatioReq
        opt_parameters = None
        if UsePSCasVariable == 0:
            totalTime, opt_parameters = self.optimizeActuatorWithoutPSC(Actuator=Actuator, log=log, csv=csv, printOptParams=printOptParams)
        elif UsePSCasVariable == 1:
            totalTime, opt_parameters = self.optimizeActuatorWithPSC(Actuator=Actuator, log=log, csv=csv, printOptParams=printOptParams)
        else:
            totalTime = 0
            print("ERROR: \"UsePSCasVariable\" can be either 0 or 1")

        return totalTime, opt_parameters
    
    def optimizeActuatorWithoutPSC(self, Actuator=inrunnerdoubleStageActuator, log=1, csv=0, printOptParams = 1):
        startTime = time.time()
        opt_parameters = None
        if csv and log:
            print("WARNING: Both csv and Log cannot be true")
            print("WARNING: Please set either csv or log to be 0 in \"Optimizer.optimizeActuator(Actuator)\" function")
            print(" ")
            print("ACTION:Making log to be false and csv to be true")
            log = 0
            csv = 1
        elif not csv and not log:
            print("WARNING: Both csv and Log cannot be false")
            print("WARNING: Please set either csv or log to be 1 in \"Optimizer.optimizeActuator(Actuator)\" function")
            print(" ")
            print("ACTION:Making log to be False and csv to be true")
            log = 0
            csv = 1
        
        if csv:
            fileName = f"./results/results_BruteForce_{Actuator.motor.motorName}/INDSPG_BRUTEFORCE_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}.csv"
        elif log:
            fileName = f"./results/results_BruteForce_{Actuator.motor.motorName}/INDSPG_BRUTEFORCE_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}_LOG.txt"
        
        with open(fileName, "w") as DSPGLogFile:
            sys.stdout = DSPGLogFile
            if(printOptParams):
                self.printOptimizationParameters(Actuator, log, csv)
                print(" ")
            
            if self.gearRatioReq != 0:
                self.GEAR_RATIO_MIN = self.gearRatioReq - self.GEAR_RATIO_STEP/2
                self.GEAR_RATIO_MAX = self.gearRatioReq + (self.GEAR_RATIO_STEP/2 - 1e-6)

            self.gearRatioIter = self.GEAR_RATIO_MIN
            if log:
                print("*****************************************************************")
                print("FOR MINIMUM GEAR RATIO ", self.gearRatioIter)
                print("*****************************************************************")
                print(" ")
            elif csv:
                # Printing the optimization iterations below
                # print("iter, gearRatio, module1, module2, Ns1, Np1, Nr1, numPlanet1, Ns2, Np2, Nr2, numPlanet2, fwSun1MM, fwPlanet1MM, fwRing1MM, fwSun2MM, fwPlanet2MM, fwRing2MM, Opt_PSC_sun1,  Opt_PSC_planet1, Opt_PSC_ring1, Opt_PSC_sun2, Opt_PSC_planet2, Opt_PSC_ring2, Opt_CD_SP1, Opt_CD_PR1, Opt_CD_SP2, Opt_CD_PR2, mass, eff, peakTorque, Cost, Torque_Density")
                print("iter, gearRatio, module1, module2, Ns1, Np1, Nr1, numPlanet1, Ns2, Np2, Nr2, numPlanet2, fwSun1MM, fwPlanet1MM, fwRing1MM, fwSun2MM, fwPlanet2MM, fwRing2MM, mass, eff, peakTorque, Cost, Torque_Density, Outer_Bearing_mass_stg1, Outer_Bearing_mass_stg2, Actuator_width")

            while self.gearRatioIter <= self.GEAR_RATIO_MAX:
                opt_done  = 0
                self.iter = 0
                self.Cost = 100000
                MinCost   = self.Cost

                Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.setModule(self.MODULE_STAGE1_MIN)
                while Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.module <= self.MODULE_STAGE1_MAX:
                    Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.setModule(self.MODULE_STAGE2_MIN)
                    while Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.module <= self.MODULE_STAGE2_MAX:
                        # Setting Ns
                        Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.setNs(self.NUM_TEETH_SUN_MIN)
                        while 2*Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.getPCRadiusSunMM() <= Actuator.maxGearboxDiameter_Stg1:  # specific stage 1 Max diameter
                            # Setting Np
                            Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.setNp(self.NUM_TEETH_PLANET_MIN)
                            while 2*Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.getPCRadiusPlanetMM() <= Actuator.maxGearboxDiameter_Stg1*0.5: # specific stage 1 Max diameter
                                # Setting Nr
                                Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.setNr(2*Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.Np + 
                                                                                Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.Ns)
                                if 2*Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.getPCRadiusRingMM() <= Actuator.maxGearboxDiameter_Stg1: # specific stage 1 Max diameter
                                # while 2*Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.getPCRadiusRingMM() <= maxGearBoxDia:
                                    # Setting number of Planet
                                    Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.setNumPlanet(self.NUM_PLANET_STAGE1_MIN)
                                    while Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.numPlanet <= self.NUM_PLANET_STAGE1_MAX:
                                        # # Setting Nr
                                        Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.setNs(self.NUM_TEETH_SUN_MIN)
                                        while 2*Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.getPCRadiusSunMM() <= Actuator.maxGearboxDiameter:
                                            # Setting Np
                                            Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.setNp(self.NUM_TEETH_PLANET_MIN)
                                            while 2*Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.getPCRadiusPlanetMM() <= Actuator.maxGearboxDiameter*0.5:
                                                # Setting Ns
                                                Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.setNr(2*Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.Np + 
                                                                                                Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.Ns)
                                                if 2*Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.getPCRadiusRingMM() <= Actuator.maxGearboxDiameter:
                                                # while 2*Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.getPCRadiusRingMM() <= maxGearBoxDia:
                                                    # Setting number of Planet
                                                    Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.setNumPlanet(self.NUM_PLANET_STAGE2_MIN)
                                                    while Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.numPlanet <= self.NUM_PLANET_STAGE2_MAX:
                                                        self.cntrIterBeforeCons += 1
                                                        #print("Before Constraints", cntrIterBeforeCons)
                                                        if (Actuator.inrunnerdoubleStagePlanetaryGearbox.geometricConstraint() and 
                                                            Actuator.inrunnerdoubleStagePlanetaryGearbox.meshingConstraint() #and 
                                                            #Actuator.inrunnerdoubleStagePlanetaryGearbox.noPlanetInterferenceConstraint()        #TODO:  CHANGE IT BACK TO ORIGINAL
                                                            ):
                                                            self.totalFeasibleGearboxes += 1
                                                            # Fiter for the Gear Ratio
                                                            if (Actuator.inrunnerdoubleStagePlanetaryGearbox.gearRatio() >= self.gearRatioIter and 
                                                                Actuator.inrunnerdoubleStagePlanetaryGearbox.gearRatio() <= (self.gearRatioIter + 1)):

                                                                self.totalGearboxesWithReqGR += 1

                                                                Actuator.updateFacewidth()
                                                                # effActuator = Actuator.inrunnerdoubleStagePlanetaryGearbox.getEfficiency()
                                                                # massActuator = Actuator.getMassKG_3DP()
                                                                
                                                                self.Cost = self.cost(Actuator=Actuator)

                                                                if self.Cost < MinCost:
                                                                    MinCost = self.Cost
                                                                    self.iter +=1
                                                                    # Actuator.genEquationFile()
                                                                    if (self.gearRatioReq == 0):
                                                                        Actuator.genEquationFile(motor_name=Actuator.motor.motorName, gearRatioLL=round(self.gearRatioIter, 1), gearRatioUL = (round(self.gearRatioIter + self.GEAR_RATIO_STEP,1)))
                                                                    else:
                                                                        Actuator.genEquationFile_editCADdirectly()

                                                                    opt_done = 1
                                                                    opt_parameters = [Actuator.inrunnerdoubleStagePlanetaryGearbox.gearRatio(),
                                                                                      Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.numPlanet,
                                                                                      Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.numPlanet,
                                                                                      Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.Ns,
                                                                                      Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.Np,
                                                                                      Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.Nr,
                                                                                      Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.Ns,
                                                                                      Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.Np,
                                                                                      Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.Nr,
                                                                                      Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.module, 
                                                                                      Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.module]
                                                                    opt_planetaryGearbox = inrunnerdoubleStagePlanetaryGearbox(design_parameters         = self.design_parameters,
                                                                                                                       gear_standard_parameters  = self.gear_standard_parameters,
                                                                                                                       Ns1                       = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.Ns,
                                                                                                                       Np1                       = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.Np,
                                                                                                                       Nr1                       = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.Nr,
                                                                                                                       Ns2                       = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.Ns,
                                                                                                                       Np2                       = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.Np,
                                                                                                                       Nr2                       = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.Nr,  
                                                                                                                       numPlanet1                = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.numPlanet,
                                                                                                                       numPlanet2                = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.numPlanet,
                                                                                                                       module1                   = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.module, # mm
                                                                                                                       module2                   = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.module, # mm
                                                                                                                       densityGears              = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.densityGears,
                                                                                                                       densityStructure          = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.densityStructure, 
                                                                                                                       fwSun1MM                  = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.fwSunMM, # mm
                                                                                                                       fwPlanet1MM               = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.fwPlanetMM, # mm
                                                                                                                       fwRing1MM                 = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.fwRingMM, # mm
                                                                                                                       fwSun2MM                  = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.fwSunMM, # mm
                                                                                                                       fwPlanet2MM               = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.fwPlanetMM, # mm
                                                                                                                       fwRing2MM                 = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.fwRingMM, # mm
                                                                                                                       maxGearAllowableStressMPa = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.maxGearAllowableStressMPa) # MPa
                                                                    opt_actuator = inrunnerdoubleStageActuator(design_parameters           = self.design_parameters,
                                                                                                                motor                       = Actuator.motor, 
                                                                                                                motor_driver_params         = Actuator.motor_driver_params,
                                                                                                                inrunnerdoubleStagePlanetaryGearbox = opt_planetaryGearbox, 
                                                                                                                FOS                         = Actuator.FOS, 
                                                                                                                serviceFactor               = Actuator.serviceFactor, 
                                                                                                                maxGearboxDiameter          = Actuator.maxGearboxDiameter, # mm 
                                                                                                                stressAnalysisMethodName    = "MIT") # Lewis or AGMA or MIT
                                                                    opt_actuator.updateFacewidth()
                                                                    opt_actuator.getMassKG_3DP()
                                                                    # self.printOptimizationResults(Actuator, log, csv)
                                                        Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.setNumPlanet(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.numPlanet + 1)
                                                    # Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.setNr(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.Ns + 1)
                                                Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.setNp(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.Np + 1)
                                            Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.setNs(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.Ns + 1)
                                        Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.setNumPlanet(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.numPlanet + 1)
                                    # Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.setNr(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.Nr + 1)
                                Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.setNp(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.Np + 1)
                            Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.setNs(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.Ns + 1)
                        Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.setModule(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.module + 0.100)
                        Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.setModule(round(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.module,1))
                    Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.setModule(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.module + 0.100)
                    Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.setModule(round(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.module,1))
                if (opt_done == 1):
                        self.printOptimizationResults(opt_actuator, log, csv)
                self.gearRatioIter += self.GEAR_RATIO_STEP
                
                if log:
                    print("Number of iterations: ", self.cntrIterBeforeCons)
                    print("Total Feasible Gearboxes:", self.totalFeasibleGearboxes)
                    print("Total Gearboxes with requires Gear Ratio:", self.totalGearboxesWithReqGR)
                    print("*****************************************************************")
                    print("----------------------------END----------------------------------")
                    print(" ")
            # Print the time in the file 
            endTime = time.time()
            totalTime = endTime - startTime
            if(printOptParams):
                print("\n")
                print("Running Time (sec)")
                print(totalTime) 

        sys.stdout = sys.__stdout__

        return totalTime, opt_parameters

    def optimizeActuatorWithPSC(self, Actuator=inrunnerdoubleStageActuator, log=1, csv=0):
        startTime = time.time()
        opt_parameters = None
        if csv and log:
            print("WARNING: Both csv and Log cannot be true")
            print("WARNING: Please set either csv or log to be 0 in \"Optimizer.optimizeActuator(Actuator)\" function")
            print(" ")
            print("ACTION:Making log to be false and csv to be true")
            log = 0
            csv = 1
        elif not csv and not log:
            print("WARNING: Both csv and Log cannot be false")
            print("WARNING: Please set either csv or log to be 1 in \"Optimizer.optimizeActuator(Actuator)\" function")
            print(" ")
            print("ACTION:Making log to be False and csv to be true")
            log = 0
            csv = 1
        
        if csv:
            fileName = f"./results/results_bilevel_{Actuator.motor.motorName}/INDSPG_BILEVEL_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}.csv"
        elif log:
            fileName = f"./results/results_bilevel_{Actuator.motor.motorName}/INDSPG_BILEVEL_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}_LOG.txt"
        
        with open(fileName, "w") as dspgLogFile:
            sys.stdout = dspgLogFile
            self.printOptimizationParameters(Actuator, log, csv)

            if log:
                print(" ")
                print("*****************************************************************")
                print("FOR MINIMUM GEAR RATIO ", self.gearRatioIter)
                print("*****************************************************************")
                print(" ")
            elif csv:
                # Printing the optimization iterations below
                print(" ")
                print("iter, gearRatio, module1, module2, Ns1, Np1, Nr1, numPlanet1, Ns2, Np2, Nr2, numPlanet2, fwSun1MM, fwPlanet1MM, fwRing1MM, fwSun2MM, fwPlanet2MM, fwRing2MM, PSCs1, PSCp1, PSCr1, PSCs2, PSCp2, PSCr2, CD_SP1, CD_PR1, CD_SP2, CD_PR2, mass, eff, peakTorque, Cost, Torque_Density")

            while self.gearRatioIter <= self.GEAR_RATIO_MAX:
                opt_done  = 0
                self.iter = 0
                self.Cost = 100000
                MinCost = self.Cost

                Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.setModule(self.MODULE_STAGE1_MIN)
                while Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.module <= self.MODULE_STAGE1_MAX:
                    Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.setModule(self.MODULE_STAGE2_MIN)
                    while Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.module <= self.MODULE_STAGE2_MAX:
                        # Setting Ns
                        Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.setNs(self.NUM_TEETH_SUN_MIN)
                        while 2*Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.getPCRadiusSunMM() <= Actuator.maxGearboxDiameter:
                            # Setting Np
                            Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.setNp(self.NUM_TEETH_PLANET_MIN)
                            while 2*Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.getPCRadiusPlanetMM() <= Actuator.maxGearboxDiameter/2:
                                # Setting Nr
                                Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.setNr(2*Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.Np + 
                                                                                Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.Ns)
                                if 2*Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.getPCRadiusRingMM() <= Actuator.maxGearboxDiameter:
                                # while 2*Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.getPCRadiusRingMM() <= maxGearBoxDia:
                                    # Setting number of Planet
                                    Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.setNumPlanet(self.NUM_PLANET_STAGE1_MIN)
                                    while Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.numPlanet <= self.NUM_PLANET_STAGE1_MAX:
                                        # # Setting Nr
                                        Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.setNs(self.NUM_TEETH_SUN_MIN)
                                        while 2*Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.getPCRadiusSunMM() <= Actuator.maxGearboxDiameter:
                                            # Setting Np
                                            Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.setNp(self.NUM_TEETH_PLANET_MIN)
                                            while 2*Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.getPCRadiusPlanetMM() <= Actuator.maxGearboxDiameter/2:
                                                # Setting Ns
                                                Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.setNr(2*Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.Np + 
                                                                                                Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.Ns)
                                                if 2*Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.getPCRadiusRingMM() <= Actuator.maxGearboxDiameter:
                                                # while 2*Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.getPCRadiusRingMM() <= maxGearBoxDia:
                                                    # Setting number of Planet
                                                    Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.setNumPlanet(self.NUM_PLANET_STAGE2_MIN)
                                                    while Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.numPlanet <= self.NUM_PLANET_STAGE2_MAX:
                                                        self.cntrIterBeforeCons += 1
                                                        #print("Before Constraints", cntrIterBeforeCons)
                                                        if (Actuator.inrunnerdoubleStagePlanetaryGearbox.geometricConstraint() and 
                                                            Actuator.inrunnerdoubleStagePlanetaryGearbox.meshingConstraint() and 
                                                            Actuator.inrunnerdoubleStagePlanetaryGearbox.noPlanetInterferenceConstraint()):
                                                            self.totalFeasibleGearboxes += 1
                                                            # Fiter for the Gear Ratio
                                                            if (Actuator.inrunnerdoubleStagePlanetaryGearbox.gearRatio() >= self.gearRatioIter and 
                                                                Actuator.inrunnerdoubleStagePlanetaryGearbox.gearRatio() <= (self.gearRatioIter + self.GEAR_RATIO_STEP)):

                                                                self.totalGearboxesWithReqGR += 1

                                                                Actuator.updateFacewidth()
                                                                effActuator = Actuator.inrunnerdoubleStagePlanetaryGearbox.getEfficiency()
                                                                # massActuator = Actuator.getMassStructureKG()
                                                                massActuator = Actuator.getMassKG_3DP()
                                                                self.Cost = (self.K_Mass * massActuator) + (self.K_Eff * effActuator)

                                                                if self.Cost < MinCost:
                                                                    MinCost = self.Cost
                                                                    self.iter +=1
                                                                    opt_done = 1
                                                                    Actuator.genEquationFile()
                                                                    opt_parameters = [Actuator.inrunnerdoubleStagePlanetaryGearbox.gearRatio(),
                                                                                      Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.numPlanet,
                                                                                      Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.numPlanet,
                                                                                      Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.Ns,
                                                                                      Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.Np,
                                                                                      Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.Nr,
                                                                                      Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.Ns,
                                                                                      Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.Np,
                                                                                      Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.Nr,
                                                                                      Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.module, 
                                                                                      Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.module]
                                                                    opt_planetaryGearbox = inrunnerdoubleStagePlanetaryGearbox(design_parameters         = self.design_parameters,
                                                                                                                       gear_standard_parameters  = self.gear_standard_parameters,
                                                                                                                       Ns1                       = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.Ns,
                                                                                                                       Np1                       = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.Np,
                                                                                                                       Nr1                       = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.Nr,
                                                                                                                       Ns2                       = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.Ns,
                                                                                                                       Np2                       = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.Np,
                                                                                                                       Nr2                       = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.Nr,  
                                                                                                                       numPlanet1                = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.numPlanet,
                                                                                                                       numPlanet2                = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.numPlanet,
                                                                                                                       module1                   = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.module, # mm
                                                                                                                       module2                   = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.module, # mm
                                                                                                                       densityGears              = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.densityGears,
                                                                                                                       densityStructure          = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.densityStructure, 
                                                                                                                       fwSun1MM                  = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.fwSunMM, # mm
                                                                                                                       fwPlanet1MM               = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.fwPlanetMM, # mm
                                                                                                                       fwRing1MM                 = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.fwRingMM, # mm
                                                                                                                       fwSun2MM                  = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.fwSunMM, # mm
                                                                                                                       fwPlanet2MM               = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.fwPlanetMM, # mm
                                                                                                                       fwRing2MM                 = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.fwRingMM, # mm
                                                                                                                       maxGearAllowableStressMPa = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.maxGearAllowableStressMPa) # MPa
                                                                    opt_actuator = inrunnerdoubleStageActuator(design_parameters           = self.design_parameters,
                                                                                                                motor                       = Actuator.motor, 
                                                                                                                inrunnerdoubleStagePlanetaryGearbox = opt_planetaryGearbox, 
                                                                                                                FOS                         = Actuator.FOS, 
                                                                                                                serviceFactor               = Actuator.serviceFactor, 
                                                                                                                maxGearboxDiameter          = Actuator.maxGearboxDiameter, # mm 
                                                                                                                stressAnalysisMethodName    = "Lewis") # Lewis or AGMA
                                                                    # self.printOptimizationResults(Actuator, log, csv)
                                                        Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.setNumPlanet(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.numPlanet + 1)
                                                    # Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.setNr(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.Ns + 1)
                                                Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.setNp(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.Np + 1)
                                            Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.setNs(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.Ns + 1)
                                        Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.setNumPlanet(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.numPlanet + 1)
                                    # Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.setNr(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.Nr + 1)
                                Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.setNp(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.Np + 1)
                            Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.setNs(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.Ns + 1)
                        Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.setModule(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.module + 0.100)
                        Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.setModule(round(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.module,1))
                    Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.setModule(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.module + 0.100)
                    Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.setModule(round(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.module,1))
                if (opt_done == 1):
                        self.dspgOpt = optimal_continuous_PSC_dspg(GEAR_RATIO_MIN = opt_parameters[0], 
                                                                   numPlanetStg1  = opt_parameters[1], 
                                                                   numPlanetStg2  = opt_parameters[2],
                                                                   Ns1_init       = opt_parameters[3],
                                                                   Np1_init       = opt_parameters[4],
                                                                   Nr1_init       = opt_parameters[5],
                                                                   Ns2_init       = opt_parameters[6],
                                                                   Np2_init       = opt_parameters[7],
                                                                   Nr2_init       = opt_parameters[8],
                                                                   M1_init        = opt_parameters[9] * 10,
                                                                   M2_init        = opt_parameters[10] * 10)
                                                
                        _, calc_centerDistForManufacturing_stg1, calc_centerDistForManufacturing_stg2 = self.dspgOpt.solve()
                        self.dspgOpt.solve(optimizeForManufacturing        = True,
                                           centerDistForManufacturing_stg1 = calc_centerDistForManufacturing_stg1,
                                           centerDistForManufacturing_stg2 = calc_centerDistForManufacturing_stg2)
                        self.printOptimizationResults(opt_actuator, log, csv)
                self.gearRatioIter += self.GEAR_RATIO_STEP
                
                if log:
                    print("Number of iterations: ", self.cntrIterBeforeCons)
                    print("Total Feasible Gearboxes:", self.totalFeasibleGearboxes)
                    print("Total Gearboxes with requires Gear Ratio:", self.totalGearboxesWithReqGR)
                    print("*****************************************************************")
                    print("----------------------------END----------------------------------")
                    print(" ")
            # Print the time in the file 
            endTime = time.time()
            totalTime = endTime - startTime
            print("\n")
            print("Running Time (sec)")
            print(totalTime) 

        sys.stdout = sys.__stdout__

        return totalTime, opt_parameters

    def printOptimizationParameters(self, Actuator=inrunnerdoubleStageActuator, log=1, csv=0):
        # Motor Parameters
        maxMotorAngVelRPM       = Actuator.motor.maxMotorAngVelRPM
        maxMotorAngVelRadPerSec = Actuator.motor.maxMotorAngVelRadPerSec
        maxMotorTorque          = Actuator.motor.maxMotorTorque
        maxMotorPower           = Actuator.motor.maxMotorPower
        motorMass               = Actuator.motor.massKG
        motorDia                = Actuator.motor.motorDiaMM
        motorLength             = Actuator.motor.motorLengthMM
        
        # Planetary Gearbox Parameters
        maxGearAllowableStressMPa = Actuator.inrunnerdoubleStagePlanetaryGearbox.maxGearAllowableStressMPa
        
        # Gear strength parameters
        FOS                      = Actuator.FOS
        serviceFactor            = Actuator.serviceFactor
        maxGearBoxDia            = Actuator.maxGearboxDiameter
        stressAnalysisMethodName = Actuator.stressAnalysisMethodName
        
        if log:
           # Printing the parameters below
            print("--------------------Motor Parameters--------------------")
            print("maxMotorAngVelRPM:       ", maxMotorAngVelRPM)
            print("maxMotorAngVelRadPerSec: ", maxMotorAngVelRadPerSec)
            print("maxMotorTorque:          ", maxMotorTorque)
            print("maxMotorPower:           ", maxMotorPower)
            print("motorMass:               ", motorMass)
            print("motorDia:                ", motorDia)
            print("motorLength:             ", motorLength)
            print(" ")
            print("--------------Planetary Gearbox Parameters--------------")
            print("maxGearAllowableStressMPa: ", maxGearAllowableStressMPa)
            print(" ")
            print("-----------Gear strength and size parameters------------")
            print("FOS:                      ", FOS)
            print("serviceFactor:            ", serviceFactor)
            print("stressAnalysisMethodName: ", stressAnalysisMethodName)
            print("maxGearBoxDia:            ", maxGearBoxDia)
            print(" ")
            print("-----------------Optimization Parameters-----------------")
            print("K_Mass:                   ", self.K_Mass)
            print("K_Eff:                    ", self.K_Eff)
            print("MODULE_STAGE1_MIN:        ", self.MODULE_STAGE1_MIN)
            print("MODULE_STAGE1_MAX:        ", self.MODULE_STAGE1_MAX)
            print("MODULE_STAGE2_MIN:        ", self.MODULE_STAGE2_MIN)
            print("MODULE_STAGE2_MAX:        ", self.MODULE_STAGE2_MAX)
            print("NUM_PLANET_STAGE1_MIN:    ", self.NUM_PLANET_STAGE1_MIN)
            print("NUM_PLANET_STAGE1_MAX:    ", self.NUM_PLANET_STAGE1_MAX)
            print("NUM_PLANET_STAGE2_MIN:    ", self.NUM_PLANET_STAGE2_MIN)
            print("NUM_PLANET_STAGE2_MAX:    ", self.NUM_PLANET_STAGE2_MAX)
            print("NUM_TEETH_SUN_MIN:        ", self.NUM_TEETH_SUN_MIN)
            print("NUM_TEETH_PLANET_MIN:     ", self.NUM_TEETH_PLANET_MIN)
            print("GEAR_RATIO_MIN:           ", self.GEAR_RATIO_MIN)
            print("GEAR_RATIO_MAX:           ", self.GEAR_RATIO_MAX)
            print("GEAR_RATIO_STEP:          ", self.GEAR_RATIO_STEP)

        elif csv:
            print("Motor Parameters:")
            print("maxMotorAngVelRPM,","maxMotorAngVelRadPerSec,","maxMotorTorque,","maxMotorPower,","motorMass,","motorDia,", "motorLength")
            print(maxMotorAngVelRPM,",", maxMotorAngVelRadPerSec,",", maxMotorTorque,",",maxMotorPower,",",motorMass,",",motorDia,",", motorLength)
            print(" ")
            print("Gear strength and size parameters:")
            print("FOS,", "serviceFactor,", "stressAnalysisMethodName,", "maxGearBoxDia,","maxGearAllowableStressMPa")
            print(FOS,",", serviceFactor,",", stressAnalysisMethodName,",", maxGearBoxDia,",",maxGearAllowableStressMPa)
            print(" ")
            print("Optimization Parameters:")            
            print("K_mass, K_Eff, MODULE_STAGE1_MIN, MODULE_STAGE1_MAX, MODULE_STAGE2_MIN, MODULE_STAGE2_MAX, NUM_PLANET_STAGE1_MIN, NUM_PLANET_STAGE1_MAX, NUM_PLANET_STAGE2_MIN, NUM_PLANET_STAGE2_MAX, NUM_TEETH_SUN_MIN, NUM_TEETH_PLANET_MIN, GEAR_RATIO_MIN, GEAR_RATIO_MAX, GEAR_RATIO_STEP")
            print(self.K_Mass,",", self.K_Eff,",", self.MODULE_STAGE1_MIN,",", self.MODULE_STAGE1_MAX,",", self.MODULE_STAGE2_MIN,",", self.MODULE_STAGE2_MAX,",", self.NUM_PLANET_STAGE1_MIN,",", self.NUM_PLANET_STAGE1_MAX,",", self.NUM_PLANET_STAGE2_MIN,",", self.NUM_PLANET_STAGE2_MAX,",", self.NUM_TEETH_SUN_MIN,",", self.NUM_TEETH_PLANET_MIN,",", self.GEAR_RATIO_MIN,",", self.GEAR_RATIO_MAX,",", self.GEAR_RATIO_STEP)

    def printOptimizationResults(self, Actuator=inrunnerdoubleStageActuator, log=1, csv=0):
        Actuator.setVariables()
        if log:
            # Printing the parameters below
            print("Iteration: ", self.iter)
            Actuator.printParametersLess()
            Actuator.printVolumeAndMassParameters()
            print(" ")
            print("Cost:", self.Cost)
            print("*****************************************************************")
        elif csv:
            iter        = self.iter
            gearRatio   = Actuator.inrunnerdoubleStagePlanetaryGearbox.gearRatio()
            module1     = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.module
            Ns1         = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.Ns
            Np1         = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.Np
            Nr1         = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.Nr
            numPlanet1  = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.numPlanet
            module2     = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.module
            Ns2         = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.Ns
            Np2         = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.Np
            Nr2         = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.Nr
            numPlanet2  = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.numPlanet
            fwSun1MM    = round(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.fwSunMM    , 3)
            fwPlanet1MM = round(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.fwPlanetMM , 3)
            fwRing1MM   = round(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.fwRingMM   , 3)
            fwSun2MM    = round(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.fwSunMM    , 3)
            fwPlanet2MM = round(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.fwPlanetMM , 3)
            fwRing2MM   = round(Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.fwRingMM   , 3)
            if self.UsePSCasVariable == 1 :
                Opt_PSC_ring1 = self.dspgOpt.model.PSCr1.value
                Opt_PSC_planet1 = self.dspgOpt.model.PSCp1.value
                Opt_PSC_sun1 = self.dspgOpt.model.PSCs1.value
                Opt_PSC_ring2 = self.dspgOpt.model.PSCr2.value
                Opt_PSC_planet2 = self.dspgOpt.model.PSCp2.value
                Opt_PSC_sun2 = self.dspgOpt.model.PSCs2.value
                Opt_CD_SP1, Opt_CD_PR1, Opt_CD_SP2, Opt_CD_PR2 = self.dspgOpt.getCenterDistance(Var=False)
            else :
                Opt_PSC_ring1 = 0
                Opt_PSC_planet1 = 0
                Opt_PSC_sun1 = 0
                Opt_PSC_ring2 = 0
                Opt_PSC_planet2 = 0
                Opt_PSC_sun2 = 0
                Opt_CD_SP1 = ((Ns1 + Np1)/2)* module1
                Opt_CD_PR1 = ((Nr1 - Np1)/2)* module1
                Opt_CD_SP2 = ((Ns2 + Np2)/2)* module2
                Opt_CD_PR2 = ((Nr2 - Np2)/2)* module2

            # mass        = round(Actuator.getMassStructureKG(), 3)
            mass        = round(Actuator.getMassKG_3DP(), 3)
            eff         = round(Actuator.inrunnerdoubleStagePlanetaryGearbox.getEfficiency(), 3)
            if (self.UsePSCasVariable == 1):
                eff = self.dspgOpt.getEfficiency(Var = False)
            
            peakTorque  = round(Actuator.motor.getMaxMotorTorque()*Actuator.inrunnerdoubleStagePlanetaryGearbox.gearRatio(), 3)
            Cost        = self.cost(Actuator=Actuator)
            Torque_Density =  peakTorque/mass
            Outer_Bearing_mass_stg1 = Actuator.bearing_mass_stg1
            Outer_Bearing_mass_stg2 = Actuator.bearing_mass_stg2
            Actuator_width = Actuator.actuator_width
            print(iter,",", gearRatio,",", module1,",", module2,",", Ns1,",", Np1,",", Nr1,",", numPlanet1,",", Ns2,",", Np2,",", Nr2,",", numPlanet2,",", fwSun1MM,",", fwPlanet1MM,",", fwRing1MM,",", fwSun2MM,",", fwPlanet2MM,",", fwRing2MM,"," , mass, ",", eff, ",", peakTorque, ",", Cost,",", Torque_Density,",", Outer_Bearing_mass_stg1,",", Outer_Bearing_mass_stg2,",",Actuator_width)

    def cost(self, Actuator=inrunnerdoubleStageActuator):
        K_gearRatio = 0
        if self.gearRatioReq != 0:
            K_gearRatio = 1
        
        gearRatio_err = np.sqrt((Actuator.inrunnerdoubleStagePlanetaryGearbox.gearRatio() - self.gearRatioReq)**2)

        mass = Actuator.getMassKG_3DP()
        eff = Actuator.inrunnerdoubleStagePlanetaryGearbox.getEfficiency()
        width = Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage1.fwPlanetMM + Actuator.inrunnerdoubleStagePlanetaryGearbox.Stage2.fwPlanetMM
        cost = (self.K_Mass    * mass 
                + self.K_Eff   * eff 
                + self.K_Width * width 
                + K_gearRatio  * gearRatio_err)
        return cost