import re
import os
import math
import numpy as np
import sys
import time

from CommonComponents import bearings_discrete, nuts_and_bolts_dimensions, motor_driver, motor_frameless_outrunner as motor

class internalsingleStagePlanetaryGearbox:
    def __init__(self, 
                 design_params,
                 gear_standard_parameters,
                 Ns                        = 20,
                 Np                        = 40,
                 Nr                        = 100,
                 module                    = 0.5,
                 numPlanet                 = 3,
                 fwSunMM                   = 5.0,
                 fwPlanetMM                = 5.0,
                 fwRingMM                  = 5.0,
                 maxGearAllowableStressMPa = 400,
                 densityGears              = 1246,
                 densityStructure          = 1246,
                 ):
        
        self.Ns        = Ns
        self.Np        = Np
        self.Nr        = Nr
        self.numPlanet = numPlanet
        self.module    = module

        self.maxGearAllowableStressMPa = maxGearAllowableStressMPa # MPa
        self.maxGearAllowableStressPa  = maxGearAllowableStressMPa * 10**6 # Pa
        self.densityGears              = densityGears
        self.densityStructure          = densityStructure
        self.bhnSun                    = 270 # Brinell Hardness Number for sun gear
        self.bhnPlanet                 = 270 # Brinell Hardness Number for planet gear
        self.bhnRing                   = 270 # Brinell Hardness Number for ring gear
        self.enduranceStressSunMPa     = 2.75*self.bhnSun - 69    # MPa
        self.enduranceStressPlanetMPa  = 2.75*self.bhnPlanet - 69 # MPa
        self.enduranceStressRingMPa    = 2.75*self.bhnRing - 69   # MPa
        self.youngsModulusSun          = 2.05 * 10**5 # MPa 
        self.youngsModulusPlanet       = 2.05 * 10**5 # MPa 
        self.youngsModulusRing         = 2.05 * 10**5 # MPa 
        self.equivYoungsModulusSP      = (2.0 * self.youngsModulusSun * self.youngsModulusPlanet) / (self.youngsModulusSun + self.youngsModulusPlanet)
        self.equivYoungsModulusPR      = (2.0 * self.youngsModulusPlanet * self.youngsModulusRing) / (self.youngsModulusPlanet + self.youngsModulusRing)

        # Face width of sun gear, planet gear, and ring gear in mm
        self.fwSunMM    = fwSunMM
        self.fwRingMM   = fwRingMM
        self.fwPlanetMM = fwPlanetMM

        # Face width of sun gear, planet gear, and ring gear in m
        self.fwSunM     = fwSunMM / 1000.0
        self.fwRingM    = fwRingMM / 1000.0
        self.fwPlanetM  = fwPlanetMM / 1000.0

        # Coefficient of friction and Pressure Angles
        self.mu            = gear_standard_parameters["coefficientOfFriction"] # 0.3 # Coefficient of friction
        self.pressureAngle = gear_standard_parameters["pressureAngleDEG"]      # 20  # deg

        self.planetMinDistanceMM = design_params["planetMinDistanceMM"]        # mm
        
        self.sCarrierExtrusionDiaMM       =  design_params["sCarrierExtrusionDiaMM"]       # 8.0 # mm
        self.sCarrierExtrusionClearanceMM =  design_params["sCarrierExtrusionClearanceMM"] # 1.0 # mm
    
    #------------------------------------
    # Constraints
    #------------------------------------
    def geometricConstraint(self):
        return (self.Ns + 2*self.Np == self.Nr) 
    
    def meshingConstraint(self):
        return ((self.Ns + self.Nr) % self.numPlanet == 0)

    def noPlanetInterferenceConstraint_old(self):
        return 2*(self.Ns + self.Np)*self.module*np.sin(np.pi/self.numPlanet) >= 2*self.module*self.Np + self.planetMinDistanceMM

    # New incorporates the extrusion diameter
    def noPlanetInterferenceConstraint(self):
        Rs                        = (self.module) * self.Ns / 2
        Rp                        = (self.module) * self.Np / 2 
        numPlanet                 = self.numPlanet
        sCarrierExtrusionRadiusMM = self.sCarrierExtrusionDiaMM * 0.5
        return 2 * (Rs + Rp) * np.sin(np.pi/(2*numPlanet)) - Rp - sCarrierExtrusionRadiusMM >= self.sCarrierExtrusionClearanceMM * 2

    #------------------------------------
    # Gear ratio
    #------------------------------------
    def gearRatio(self):
        return (self.Nr + self.Ns) / self.Ns

    #-------------------------------------------------------------------------
    # Uitility Functions
    #-------------------------------------------------------------------------
    def inverse_involute(self,inv_alpha):
        # This is an approximation of the inverse involute function
        alpha  = ((3*inv_alpha)**(1/3) - 
                  (2*inv_alpha)/5 + 
                  (9/175)*(3)**(2/3)*inv_alpha**(5/3) - 
                  (2/175)*(3)**(1/3)*(inv_alpha)**(7/3) - 
                  (144/67375)*(inv_alpha)**(3) + 
                  (3258/3128125)*(3)**(2/3)*(inv_alpha)**(11/3) - 
                  (49711/153278125)*(3)**(1/3)*(inv_alpha)**(13/3))
        return alpha

    def involute(self,alpha):
        return (np.tan(alpha) - alpha)

    # Define the differentiable quadratic approximation of the min function
    def quadratic_min(self, a, b, k=0.01):
        return (a + b - np.sqrt((a - b)**2 + k**2)) / 2
    
    #-------------------------------------------------------------------------
    # Gear Tooth profile parameters
    #-------------------------------------------------------------------------
    def getPressureAngleRad(self):
        return self.pressureAngle * np.pi / 180  # Pressure angle in radians

    def getWorkingPressureAngle(self):
        module = self.module  # Module of the gear
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr
        xs     = 0.0 # self.PSCs
        xp     = 0.0 # self.PSCp
        xr     = 0.0 # self.PSCr
        
        #---------------------------------
        # Pressure Angle
        #---------------------------------
        alpha = self.getPressureAngleRad()

        #---------------------------------
        # Working pressure angle
        #---------------------------------
        # Sun-Planet
        inv_alpha_w_sunPlanet = 2*np.tan(alpha)*((xs + xp)/(Ns + Np)) + self.involute(alpha)
        alpha_w_sunPlanet = self.inverse_involute(inv_alpha_w_sunPlanet)

        # Planet-Ring
        inv_alpha_w_planetRing = 2*np.tan(alpha)*((xr-xp)/(Nr - Np)) + self.involute(alpha)
        alpha_w_planetRing = self.inverse_involute(inv_alpha_w_planetRing)

        return alpha_w_sunPlanet, alpha_w_planetRing

    def getCenterDistModificationCoeff(self):
        module = self.module  # Module of the gear
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr
        xs     = 0.0 # self.PSCs
        xp     = 0.0 # self.PSCp
        xr     = 0.0 # self.PSCr
        
        #------------------------------
        # Pressure Angle
        #------------------------------
        alpha = self.getPressureAngleRad()  # Pressure angle in radians

        #------------------------------
        # Working pressure angle
        #------------------------------
        alpha_w_sunPlanet, alpha_w_planetRing = self.getWorkingPressureAngle()

        #------------------------------
        # Centre distance modification coefficient
        #------------------------------
        y_sunPlanet  = ((Ns + Np) / 2) * ((np.cos(alpha) / np.cos(alpha_w_sunPlanet)) - 1)
        y_planetRing = ((Nr - Np) / 2) * ((np.cos(alpha) / np.cos(alpha_w_planetRing)) - 1)

        return y_sunPlanet, y_planetRing

    def getCenterDistance(self):
        module = self.module  # Module of the gear
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr
        xs     = 0.0 # self.PSCs
        xp     = 0.0 # self.PSCp
        xr     = 0.0 # self.PSCr

        #-------------------------------
        # Centre distance modification coefficient
        #-------------------------------
        y_sunPlanet, y_planetRing = self.getCenterDistModificationCoeff()

        #-------------------------------
        # Centre distance
        #-------------------------------
        centerDist_sunPlanet = ((Ns + Np)/2  + y_sunPlanet)* module
        centerDist_planetRing = ((Nr - Np)/2  + y_planetRing)* module

        return centerDist_sunPlanet, centerDist_planetRing

    def getBaseDia(self):
        module = self.module  # Module of the gear
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr
        xs     = 0.0 # self.PSCs
        xp     = 0.0 # self.PSCp
        xr     = 0.0 # self.PSCr

        # Pressure Angle
        alpha = self.getPressureAngleRad() # Rad

        # Reference Diameter
        D_sun    = module * Ns # Sun's reference diameter
        D_planet = module * Np # Planet's reference diameter
        D_ring   = module * Nr # Ring's reference diameter

        # Base Diameter
        D_b_sun    = D_sun * np.cos(alpha)
        D_b_planet = D_planet * np.cos(alpha)
        D_b_ring   = D_ring * np.cos(alpha)

        return D_b_sun, D_b_planet, D_b_ring

    def getTipCircleDia(self):
        module = self.module  # Module of the gear
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr
        xs     = 0.0 # self.PSCs
        xp     = 0.0 # self.PSCp
        xr     = 0.0 # self.PSCr

        #----------------------------
        # Pressure Angle
        #----------------------------
        alpha = self.getPressureAngleRad() # Rad

        #----------------------------
        # Reference Diameter
        #----------------------------
        D_sun    = module * Ns # Sun's reference diameter
        D_planet = module * Np # Planet's reference diameter
        D_ring   = module * Nr # Ring's reference diameter

        #----------------------------
        # Center Distance Modification Coefficient
        #----------------------------
        y_sunPlanet, y_planetRing = self.getCenterDistModificationCoeff()

        #----------------------------
        # Tip circle diameter
        #----------------------------
        # Sun
        D_a_sun = D_sun + 2 * module * (1 + y_sunPlanet - xp)

        # Planet
        D_a_planet = D_planet + 2 * module * (1 + self.quadratic_min((y_sunPlanet - xs), xp))  
        # D_a_planet = D_planet + 2 * module * (1 + self.quadratic_min((y_planetRing - xs),xp)) 
        # D_a_planet = D_planet + 2 * module * (1 + xp) 
        
        # Ring
        D_a_ring = D_ring - 2 * module * (1 - xr)
        
        return D_a_sun, D_a_planet, D_a_ring

    def getTipPressureAngle(self):
        module = self.module  # Module of the gear
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr
        xs     = 0.0 # self.PSCs
        xp     = 0.0 # self.PSCp
        xr     = 0.0 # self.PSCr

        alpha = self.getPressureAngleRad() # Pressure Angle (Rad)
        D_b_sun, D_b_planet, D_b_ring = self.getBaseDia() # Base Diameter
        D_a_sun, D_a_planet, D_a_ring = self.getTipCircleDia() # Tip Circle Diameter

        #----------------------------
        # Tip Pressure angle
        #----------------------------
        alpha_a_sun    = np.arccos(D_b_sun / D_a_sun)
        alpha_a_planet = np.arccos(D_b_planet/D_a_planet)
        alpha_a_ring   = np.arccos(D_b_ring / D_a_ring)

        return alpha_a_sun, alpha_a_planet, alpha_a_ring

    def getErrorTipCircleDia_planet(self):
        module = self.module  # Module of the gear
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr
        xs     = 0.0 # self.PSCs
        xp     = 0.0 # self.PSCp
        xr     = 0.0 # self.PSCr

        # Centre distance modification coefficient
        y_sunPlanet, _ = self.getCenterDistModificationCoeff()

        # Tip Circle Diameter
        _, D_a_planet_1, _ = self.getTipCircleDia()
        D_a_planet_2 = module * Np + 2*module*(1 + np.minimum((y_sunPlanet - xs),xp)) # TODO: How will we implement min function 

        return np.abs(D_a_planet_1 - D_a_planet_2)
    
    #-------------------------------------------------------------------------
    # Contact Ratio
    #-------------------------------------------------------------------------
    def contactRatio_sunPlanet(self):
        module = self.module  # Module of the gear
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr
        xs     = 0.0 # self.PSCs
        xp     = 0.0 # self.PSCp
        xr     = 0.0 # self.PSCr

        # Working pressure angle
        alpha_w_sunPlanet, _ = self.getWorkingPressureAngle()

        # Tip pressure angle
        alpha_a_sun, alpha_a_planet, _ = self.getTipPressureAngle()

        # Contact ratio
        Approach_CR_sunPlanet = (Np / (2 * np.pi)) * (np.tan(alpha_a_planet) - np.tan(alpha_w_sunPlanet)) # Approach contact ratio
        Recess_CR_sunPlanet   = (Ns / (2 * np.pi)) * (np.tan(alpha_a_sun) - np.tan(alpha_w_sunPlanet))    # Recess contact ratio

        # write the final formula
        CR_sunPlanet = Approach_CR_sunPlanet + Recess_CR_sunPlanet

        #----------------------------------
        # Contact Ratio Alternater Formula
        #----------------------------------
        #  Ra_sun    = D_a_sun / 2
        #  Rb_sun    = D_b_sun / 2
        #  Ra_planet = D_a_planet / 2
        #  Rb_planet = D_b_planet / 2
        #  Pb        = np.pi * module * cos(alpha)
        #
        #  CR2       = (sqrt(Ra_sun**2 - Rb_sun**2) + sqrt(Ra_planet**2 - Rb_planet**2) - centerDist_sunPlanet * sin(alpha)) / Pb

        return Approach_CR_sunPlanet, Recess_CR_sunPlanet, CR_sunPlanet

    def contactRatio_planetRing(self):
        module = self.module  # Module of the gear
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr
        xs     = 0.0 # self.PSCs
        xp     = 0.0 # self.PSCp
        xr     = 0.0 # self.PSCr

        # Working pressure angle
        _, alpha_w_planetRing = self.getWorkingPressureAngle()

        # Tip pressure angle
        _, alpha_a_planet, alpha_a_ring = self.getTipPressureAngle()

        # Contact ratio
        Approach_CR_planetRing = -(Nr / (2 * np.pi)) * (np.tan(alpha_a_ring) - np.tan(alpha_w_planetRing)) # Approach contact ratio
        Recess_CR_planetRing   =   Np / (2 * np.pi) * (np.tan(alpha_a_planet) - np.tan(alpha_w_planetRing)) # Recess contact ratio
        
        # Contact Ratio
        CR_planetRing = Approach_CR_planetRing + Recess_CR_planetRing

        #-------------------------------------
        # Contact Ratio - Alternate Formula
        #-------------------------------------
        # Ra_ring   = D_a_ring / 2
        # Rb_ring   = D_b_ring / 2
        # Ra_planet = D_a_planet / 2
        # Rb_planet = D_b_planet / 2
        # Pb        = np.pi * module * cos(alpha)

        # Contact Ratio
        # CR2 = (sqrt(Ra_ring**2 - Rb_ring**2) + sqrt(Ra_planet**2 - Rb_planet**2) - centerDist_planetRing * sin(alpha)) / Pb
        # CR = (-sqrt(Ra_ring**2 - Rb_ring**2) + sqrt(Ra_planet**2 - Rb_planet**2) + centerDist_planetRing * sin(alpha)) / Pb

        return Approach_CR_planetRing, Recess_CR_planetRing, CR_planetRing

    #-------------------------------------------------------------------------
    # Gearbox Efficiency
    #-------------------------------------------------------------------------
    def getEfficiency(self):
        module = self.module  # Module of the gear
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr
        xs     = 0.0 # self.PSCs
        xp     = 0.0 # self.PSCp
        xr     = 0.0 # self.PSCr

        # Contact ratio
        eps_sunPlanetA, eps_sunPlanetR, _ = self.contactRatio_sunPlanet()
        eps_planetRingA, eps_planetRingR, _ = self.contactRatio_planetRing()
        
        # Contact-Ratio-Factor
        epsilon_sunPlanet = eps_sunPlanetA**2 + eps_sunPlanetR**2 - eps_sunPlanetA - eps_sunPlanetR + 1 
        epsilon_planetRing = eps_planetRingA**2 + eps_planetRingR**2 - eps_planetRingA - eps_planetRingR + 1 
        
        # Efficiency
        eff_SP = 1 - self.mu * np.pi * ((1 / Np) + (1 / Ns)) * epsilon_sunPlanet
        eff_PR = 1 - self.mu * np.pi * ((1 / Np) - (1 / Nr)) * epsilon_planetRing

        Eff = (1 + eff_SP * eff_PR * (Nr / Ns)) / (1 + (Nr / Ns))
        return Eff

    #---------------------------------------------
    # Pitch circle radius of sun gear, planet gear, and ring gear in mm
    #---------------------------------------------
    def getPCRadiusSunMM(self):
        return (self.Ns * self.module / 2)
    
    def getPCRadiusPlanetMM(self):
        return (self.Np * self.module / 2)
    
    def getPCRadiusRingMM(self):
        return (self.Nr * self.module / 2)
    
    #def getOuterRadiusRingMM(self):
       # return ((self.Nr * self.module / 2) + self.ringRadialWidthMM)
    
    def getCarrierRadiusMM(self):
        return (((self.Ns + self.Np + self.Np/2)/2)*self.module)
    
    #---------------------------------------------
    # Pitch circle radius of sun gear, planet gear, and ring gear in m
    #---------------------------------------------
    def getPCRadiusSunM(self):
        return ((self.Ns * self.module / 2)/1000.0)

    def getPCRadiusPlanetM(self):
        return ((self.Np * self.module / 2)/1000.0)
    
    def getPCRadiusRingM(self):
        return ((self.Nr * self.module / 2)/1000.0)
    
    #def getOuterRadiusRingM(self):
        #return (((self.Nr * self.module / 2)/1000.0) + self.ringRadialWidthM)

    def getCarrierRadiusM(self):
        return (((self.Ns + self.Np + self.Np/2)/2)*self.module/1000.0)

    #---------------------------------------------
    # Set the face width of the sun gear, planet gear, and ring gear in mm
    #---------------------------------------------
    def setfwSunMM(self, fwSunMM):
        self.fwSunMM = fwSunMM
        self.fwSunM = fwSunMM / 1000.0

    def setfwPlanetMM(self, fwPlanetMM):
        self.fwPlanetMM = fwPlanetMM
        self.fwPlanetM = fwPlanetMM / 1000.0

    def setfwRingMM(self, fwRingMM):
        self.fwRingMM = fwRingMM
        self.fwRingM = fwRingMM / 1000.0

    def setNs(self, Ns):
        self.Ns = Ns
    
    def setNp(self, Np):
        self.Np = Np
    
    def setNr(self, Nr):
        self.Nr = Nr
    
    def setModule(self, module):
        self.module = module
    
    def setNumPlanet(self, numPlanet):
        self.numPlanet = numPlanet

class internalsingleStagePlanetaryActuator:
    def __init__(self, 
                 design_params,
                 motor_driver_params,
                 motor                    = motor,
                 planetaryGearbox         = internalsingleStagePlanetaryGearbox,
                 FOS                      = 1.2,
                 serviceFactor            = 1.5,
                 stressAnalysisMethodName = "MIT"):
        
        self.motor              = motor
        self.planetaryGearbox   = planetaryGearbox
        self.FOS                = FOS
        self.serviceFactor      = serviceFactor
        maxGearboxDiameter      = self.motor.getStatorIDMM() 
        self.maxGearboxDiameter = maxGearboxDiameter # TODO: convert it to 
                                                     # outer diameter of 
                                                     # the motor
        self.stressAnalysisMethodName = stressAnalysisMethodName

        #============================================
        # Motor Parameters
        #============================================
        self.motorHeightMM           = self.motor.getMotorHeightMM()
        self.motorODMM               = self.motor.getMotorODMM()
        self.motorMassKG             = self.motor.getMassKG()
        self.MaxMotorTorque          = self.motor.getMaxMotorTorque()          # Nm
        self.MaxMotorAngVelRPM       = self.motor.getMaxMotorAngVelRPM()       # RPM
        self.MaxMotorAngVelRadPerSec = self.motor.getMaxMotorAngVelRadPerSec() # radians/sec

        #============================================
        # Actuator Design Parameters
        #============================================
        #--------------------------------------------
        # Design Parameters
        #--------------------------------------------
        self.design_params = design_params
        self.motor_driver_params  = motor_driver_params

        #--------------------------------------------
        # Independent parameters
        #--------------------------------------------
        #self.ringRadialWidthMM = self.planetaryGearbox.ringRadialWidthMM

        #---------------- Setting all design variables ---------------
        self.setVariables()
    
    #---------------------------------------------
    # Generate Equation file for 3DP Actuators
    #---------------------------------------------

    def cost(self):
        mass = self.getMassKG_3DP()
        eff = self.planetaryGearbox.getEfficiency()
        width = self.planetaryGearbox.fwPlanetMM
        cost = mass - 2 * eff + 0.2 * width
        return cost

    def setVariables(self):
        #------------------------------------------------------
        # Optimization Variables
        #------------------------------------------------------
        # --- Inputs from other classes ---
        self.Ns         = self.planetaryGearbox.Ns
        self.Np         = self.planetaryGearbox.Np
        self.Nr         = self.Ns + 2 * self.Np
        self.module     = self.planetaryGearbox.module
        self.num_planet = self.planetaryGearbox.numPlanet

        #------------------------------------------------------
        # Indepent Constant variables
        #------------------------------------------------------
        # --- Gear Profile parameters ---
        self.pressure_angle     = self.planetaryGearbox.getPressureAngleRad()
        self.pressure_angle_deg = self.planetaryGearbox.getPressureAngleRad() * 180 / np.pi

        # --- variable used in gearbox class not used here ---
        # self.ringRadialWidthMM            = 5.0
        # self.planetMinDistanceMM          = 5.0
        # self.sCarrierExtrusionDiaMM       = 8.0
        # self.sCarrierExtrusionClearanceMM = 1.0
        
        # --- Clearances -----------------
        self.clearance_planet                           = self.design_params["clearance_planet"]                           # 1.5
        self.clearance_case_mount_holes_shell_thickness = self.design_params["clearance_case_mount_holes_shell_thickness"] # 1
        self.standard_clearance_1_5mm                   = self.design_params["standard_clearance_1_5mm"]                   # 1.5
        self.standard_clearance_2_mm                    = self.design_params["standard_clearance_2_mm"]
       # self.case_mounting_nut_clearance                = self.design_params["case_mounting_nut_clearance"]                # 2
        self.standard_fillet_1_5mm                      = self.design_params["standard_fillet_1_5mm"]                      # 1.5
        self.standard_fillet_3_mm                       = self.design_params["standard_fillet_3_mm"]
        self.standard_bearing_insertion_chamfer         = self.design_params["standard_bearing_insertion_chamfer"]         # 0.5
        self.bearingIDClearanceMM                       = self.design_params["bearingIDClearanceMM"]
        self.tight_clearance_3DP                        = self.design_params["tight_clearance_3DP"]        
        self.loose_clearance_3DP                        = self.design_params["loose_clearance_3DP"]
        self.bearing_step_width                         = self.design_params["bearing_step_width"] # 2

        # --- Sun coupler, sun gear & sun gear dimensions ---
        self.sun1_bearing_ID           = self.design_params["sun1_bearing_ID"]           # 8
        self.sun1_bearing_OD           = self.design_params["sun1_bearing_OD"]           # 16
        self.sun1_bearing_width        = self.design_params["sun1_bearing_width"]        # 5
        self.sun_central_bolt_dia      = self.design_params["sun_central_bolt_dia"]      # 5

        # --- casing Motor and gearbox casing dimensions ---
        self.case_mounting_surface_height             = self.design_params["case_mounting_surface_height"] # 4
        self.case_mounting_hole_dia                   = self.design_params["case_mounting_hole_dia"] # 3
        self.motor_case_thickness                     = self.design_params["motor_case_thickness"] # 2.5
       #self.air_flow_hole_offset                     = self.design_params["air_flow_hole_offset"] # 3
        self.central_hole_offset_from_motor_mount_PCD = self.design_params["central_hole_offset_from_motor_mount_PCD"] # 5
        self.output_mount_hole_dia                    = self.design_params["output_mount_hole_dia"] # 4
        self.motor_case_OD_base_to_chamfer            = self.design_params["motor_case_OD_base_to_chamfer"] # 5
        self.pattern_offset_from_motor_case_OD_base   = self.design_params["pattern_offset_from_motor_case_OD_base"] # 3 
        self.pattern_bulge_dia                        = self.design_params["pattern_bulge_dia"] # 3
        self.pattern_num_bulge                        = self.design_params["pattern_num_bulge"] # 18
        self.pattern_depth                            = self.design_params["pattern_depth"] # 2
        self.clearance_motor_and_case                 = self.design_params["clearance_motor_and_case"]
        self.case_mounting_hole_shift                 = self.case_mounting_hole_dia / 2 
        self.ring_hub_to_case_hole_num                = self.design_params["ring_hub_to_case_hole_num"]
        self.ring_hub_to_case_hole_dia                = self.design_params["ring_hub_to_case_hole_dia"]
        self.wire_slot_radius                         = self.design_params["wire_slot_radius"]
        self.wire_slot_length                         = self.design_params["wire_slot_length"]
        self.actuactor_mount_hole_dia                 = self.design_params["actuactor_mount_hole_dia"]

        case_mounting_hole_bolt = nuts_and_bolts_dimensions(bolt_dia=self.case_mounting_hole_dia, bolt_type="socket_head")

        self.case_mounting_hole_allen_socket_dia = case_mounting_hole_bolt.bolt_head_dia
        self.case_mounting_wrench_size       = case_mounting_hole_bolt.nut_width_across_flats
        self.case_mounting_nut_depth     = case_mounting_hole_bolt.nut_thickness

        output_mount_hole_bolt = nuts_and_bolts_dimensions(bolt_dia=self.output_mount_hole_dia, bolt_type="socket_head")

        self.output_mount_nut_wrench_size       = output_mount_hole_bolt.nut_width_across_flats
        self.output_mount_hole_nut_depth        = output_mount_hole_bolt.nut_thickness

        ring_hub_to_case_hole_bolt = nuts_and_bolts_dimensions(bolt_dia=self.ring_hub_to_case_hole_dia, bolt_type="socket_head")

        self.ring_hub_to_case_hole_nut_wrench_size       = ring_hub_to_case_hole_bolt.nut_width_across_flats
        self.ring_hub_to_case_hole_nut_depth             = ring_hub_to_case_hole_bolt.nut_thickness

        actuactor_mount_hole_bolt = nuts_and_bolts_dimensions(bolt_dia=self.actuactor_mount_hole_dia, bolt_type="socket_head")

        self.actuactor_mount_nut_wrench_size       = actuactor_mount_hole_bolt.nut_width_across_flats
        self.actuactor_mount_nut_depth             = actuactor_mount_hole_bolt.nut_thickness

        # --- Planet Gear dimensions ---
        self.planet_pin_bolt_dia      = self.design_params["planet_pin_bolt_dia"] # 5 
        #self.planet_shaft_dia         = self.design_params["planet_shaft_dia"] # 8  
        self.planet_shaft_step_offset = self.design_params["planet_shaft_step_offset"] # 1  
        self.planet_bearing_OD        = self.design_params["planet_bearing_OD"] # 12 
        self.planet_bearing_width     = self.design_params["planet_bearing_width"] # 3.5
        self.planet_bearing_ID        = self.design_params["planet_bearing_ID"] # 4

        # --- carrier dimensions ---
        self.carrier_trapezoidal_support_sun_offset                        = self.design_params["carrier_trapezoidal_support_sun_offset"] # 5
        self.carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID = self.design_params["carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID"] # 4
        self.carrier_trapezoidal_support_hole_dia                          = self.design_params["carrier_trapezoidal_support_hole_dia"] # 3

        carrier_trapezoidal_support_hole = nuts_and_bolts_dimensions(bolt_dia=self.carrier_trapezoidal_support_hole_dia, bolt_type="socket_head")

        self.carrier_trapezoidal_support_hole_socket_head_dia = carrier_trapezoidal_support_hole.bolt_head_dia
        self.carrier_trapezoidal_support_hole_wrench_size     = carrier_trapezoidal_support_hole.nut_width_across_flats
        self.carrier_trapezoidal_support_nut_depth            = carrier_trapezoidal_support_hole.nut_thickness 

        planet_pin_bolt = nuts_and_bolts_dimensions(bolt_dia=self.planet_pin_bolt_dia , bolt_type="socket_head")
        
        self.planet_pin_socket_head_dia = planet_pin_bolt.bolt_head_dia
        self.planet_pin_nut_wrench_size = planet_pin_bolt.nut_width_across_flats 
        self.planet_pin_nut_depth       = planet_pin_bolt.nut_thickness

        self.carrier_top_to_mid_hole_dia = self.design_params["carrier_top_to_mid_hole_dia"]

        carrier_top_to_mid_hole_bolt = nuts_and_bolts_dimensions(bolt_dia=self.carrier_top_to_mid_hole_dia , bolt_type="socket_head")
        
        self.carrier_top_to_mid_bolt_socket_dia  = carrier_top_to_mid_hole_bolt.bolt_head_dia
        self.carrier_top_to_mid_nut_wrench_size = carrier_top_to_mid_hole_bolt.nut_width_across_flats 
        self.carrier_top_to_mid_nut_depth        = carrier_top_to_mid_hole_bolt.nut_thickness

        # --- Driver Dimensions ---
        self.driver_upper_holes_dist_from_center = self.motor_driver_params["driver_upper_holes_dist_from_center"]
        self.driver_lower_holes_dist_from_center = self.motor_driver_params["driver_lower_holes_dist_from_center"]
        self.driver_side_holes_dist_from_center  = self.motor_driver_params["driver_side_holes_dist_from_center"]
        self.driver_mount_holes_dia              = self.motor_driver_params["driver_mount_holes_dia"]
        self.driver_mount_inserts_OD             = self.motor_driver_params["driver_mount_inserts_OD"]
        self.driver_mount_thickness              = self.motor_driver_params["driver_mount_thickness"]
        self.driver_mount_height                 = self.motor_driver_params["driver_mount_height"]
        self.motor_mount_driver_hole_dia                      = self.design_params["motor_mount_driver_hole_dia"] 
        self.motor_mount_driver_hole_num                      = self.design_params["motor_mount_driver_hole_num"]

        motor_mount_driver_bolt = nuts_and_bolts_dimensions(bolt_dia=self.motor_mount_driver_hole_dia , bolt_type="socket_head")
        
        self.motor_mount_driver_nut_wrench_size = motor_mount_driver_bolt.nut_width_across_flats 
        self.motor_mount_driver_nut_depth       = motor_mount_driver_bolt.nut_thickness         
        
        # --- Magnet Mount ---
        self.magnet_mount_hole_dia        = self.design_params["magnet_mount_hole_dia"]
        self.magnet_thickness             = self.design_params["magnet_thickness"]
        self.magnet_dia                   = self.design_params["magnet_dia"]
        self.magnet_mount_thickness       = self.design_params["magnet_mount_thickness"]
        self.magnet_pattern_bulge_dia    = self.design_params["magnet_pattern_bulge_dia"]
        self.magnet_pattern_bulge_number = self.design_params["magnet_pattern_bulge_number"]
        self.magnet_mount_height         = self.design_params["magnet_mount_height"]

        # --- Motor --- 
        self.motor_OD                     = self.motorODMM
        self.motor_height                 = self.motorHeightMM
        self.stator_ID                    = self.motor.getStatorIDMM()
        self.motor_rotor_base_thickness   = self.motor.getRotorBottomThicknessMM()
        self.motor_rotor_base_ID          = self.motor.getRotorBottomIDMM()
        self.rotor_height                 = self.motor.getRotorHeightMM()
        self.rotor_ID                     = self.motor.getRotorIDMM()
        self.motor_stator_extrusion_depth = self.motor.getMotorStatorExtrusionDepth()
        self.motor_stator_extrusion_dia   = self.motor.getMotorStatorExtrusionDia()
        self.stator_height                = self.motor.getStatorHeightMM()
        self.stator_OD                    = self.motor.getStatorODMM()
        self.stator_top_rotor_top_offset  = self.motor.getStatorTopRotorTopOffset()
        self.stator_hole_dia              = self.motor.getStatorHoleDia()
        self.stator_hole_PCD              = self.motor.getStatorMountingHolePCD()
        self.motor_rotor_hole_num         = self.motor.getMotorRotorHoleNum()
        self.motor_rotor_hole_dia         = self.motor.getRotorMountHoleDiaMM()
        self.motor_rotor_hole_PCD         = self.motor.getRotorMountHolePCDMM()
        self.rotorCSKHeadUpperDiaMM       = self.motor.getRotorCSKHeadUpperDiaMM()
        self.rotorCSKHeadHeightMM         = self.motor.getRotorCSKHeadHeightMM()

        #------------------------------------------------------
        # Dependent variables
        #------------------------------------------------------
        # --- Gear Profile parameters ---
        self.h_a          = 1 * self.module
        self.h_b          = 1.25 * self.module
        self.h_f          = 1.25 * self.module
        self.clr_tip_root = self.h_f - self.h_a

        # --- Planet Gear Geometry ---
        self.dp_s      = self.module * self.Ns
        self.db_s      = self.dp_s * np.cos(self.pressure_angle)
        self.fw_s_calc = self.planetaryGearbox.fwSunMM
        self.alpha_s   = (np.sqrt(self.dp_s**2 - self.db_s**2) / self.db_s) * 180 / np.pi - self.pressure_angle * 180 / np.pi 
        self.beta_s    = (360 / (4 * self.Ns) - self.alpha_s) * 2

        self.dp_p    = self.module * self.Np
        self.db_p    = self.dp_p * np.cos(self.pressure_angle)
        self.fw_p    = self.planetaryGearbox.fwPlanetMM
        self.alpha_p = (np.sqrt(self.dp_p**2 - self.db_p**2) / self.db_p) * 180 / np.pi - self.pressure_angle * 180 / np.pi 
        self.beta_p  = (360 / (4 * self.Np) - self.alpha_p) * 2

        # --- 
        
        # ---

        self.dp_r    = self.module * self.Nr
        self.db_r    = self.dp_r * np.cos(self.pressure_angle)
        self.fw_r    = self.planetaryGearbox.fwRingMM
        self.alpha_r = (np.sqrt(self.dp_r**2 - self.db_r**2) / self.db_r) * 180 / np.pi - self.pressure_angle * 180 / np.pi 
        self.beta_r  = (360 / (4 * self.Nr) + self.alpha_r) * 2      

        # --- Bearing Dimensions ---

        # --- Output Bearing Dimensions ---
        OutputBearingIdrequiredMM  =  self.tight_clearance_3DP + (self.carrier_top_to_mid_nut_wrench_size * 0.5) + self.sun1_bearing_OD + 20#clearnace
        outputbearing              = bearings_discrete(OutputBearingIdrequiredMM)
        self.output_bearing_ID     = outputbearing.getBearingIDMM()
        self.output_bearing_OD     = outputbearing.getBearingODMM()
        self.output_bearing_width  = outputbearing.getBearingWidthMM()

        # --- sun2 Bearing Dimensions ---
        Sun2BearingIDrequiredMM  = self.Ns*self.module + self.standard_clearance_1_5mm  #self.motor_rotor_base_ID
        sun2bearing              = bearings_discrete(Sun2BearingIDrequiredMM)
        self.sun2_bearing_ID     = sun2bearing.getBearingIDMM()
        self.sun2_bearing_OD     = sun2bearing.getBearingODMM()
        self.sun2_bearing_width  = sun2bearing.getBearingWidthMM()
        
        # --- Sun coupler & sun gear dimensions ---
        sun_hub_bolt = nuts_and_bolts_dimensions(bolt_dia=self.motor_rotor_hole_dia , bolt_type="socket_head")
        
        self.sun_hub_nut_wrench_size    = sun_hub_bolt.nut_width_across_flats 
        self.sun_hub_nut_depth          = sun_hub_bolt.nut_thickness

        sun_hub_dia_min = self.motor_rotor_hole_PCD + self.sun_hub_nut_wrench_size + self.standard_clearance_1_5mm * 4
        
        sun_central_bolt = nuts_and_bolts_dimensions(bolt_dia = self.sun_central_bolt_dia, bolt_type="socket_head")
        self.sun_central_bolt_socket_head_dia   = sun_central_bolt.bolt_head_dia
        self.sun_central_nut_wrench_size        = sun_central_bolt.nut_width_across_flats 
        self.sun_central_nut_depth              = sun_central_bolt.nut_thickness

        #--- Input Bearing Dimension ---
        InputBearingIDrequiredMM  = sun_hub_dia_min #self.motor_rotor_base_ID
        inputbearing              = bearings_discrete(InputBearingIDrequiredMM)
        self.input_bearing_ID     = inputbearing.getBearingIDMM()
        self.input_bearing_OD     = inputbearing.getBearingODMM()
        self.input_bearing_width  = inputbearing.getBearingWidthMM()

        self.sun_hub_dia = self.input_bearing_ID 

        # --- Secondary Carrier dimensions ---
        self.sec_carrier_thickness = self.design_params["sec_carrier_thickness"]

        #Sun hub thickness
        self.sun_coupler_hub_thickness =  self.input_bearing_width + self.bearing_step_width
        
        #self.fw_s_used = self.sec_carrier_thickness + self.clearance_planet + self.fw_p
        self.fw_s_used = (self.sun2_bearing_width + self.bearing_step_width  
                          + self.sec_carrier_thickness + self.clearance_planet + self.fw_p 
                          - (self.sun_coupler_hub_thickness - 2*self.standard_clearance_1_5mm) + self.bearing_step_width/2 )
        #--- Carrier Top Dimension ---
        self.carrier_thickness_top = self.output_bearing_width + self.bearing_step_width + self.standard_clearance_1_5mm 
        
        #--- Carrier Thickness Mid ---
        self.carrier_thickness_mid = 6

        # --- Carrier Thickness ---
        self.carrier_thickness = self.carrier_thickness_mid + self.carrier_thickness_top

        # --- Ring Gear and hub dimension ---

        self.ring_hub_thickness = (self.fw_s_used + self.clearance_planet
                                    + self.carrier_thickness - (self.motor_case_thickness-self.bearing_step_width)
                                    - self.motor_height
                                    )
        if self.ring_hub_thickness < 3:
            self.ring_hub_thickness    = 3
            self.carrier_thickness     = ( self.motor_height
                                         + self.ring_hub_thickness
                                         + self.motor_case_thickness
                                         - self.bearing_step_width
                                         - self.fw_s_used
                                         - self.clearance_planet)                        
            self.carrier_thickness_mid = self.carrier_thickness - self.carrier_thickness_top

        self.ring_stator_case_thickness      = self.design_params["ring_stator_case_thickness"]
        self.ring_hub_offset_stator_hole_PCD = self.design_params["ring_hub_offset_stator_hole_PCD"]
        self.stator_ring_hub_hole_num        = self.design_params["stator_ring_hub_hole_num"]
   

        # --- Motor Casing ---
        self.motor_case_height = ( self.motor_height
                                    + self.ring_hub_thickness
                                    + self.sun_coupler_hub_thickness
                                    + self.bearing_step_width 
                                    )     
    
        #------------------------------------------
        self.actuator_width = (  self.motor_case_thickness
                               + self.motor_case_thickness
                               + self.motor_case_height
                               )
    
    def genEquationFile_editCADdirectly(self):
        self.setVariables()
        file_path = os.path.join(os.path.dirname(__file__), 'CADs', 'ISSPG', 'isspg_equations_onshape.txt')
        with open(file_path, 'w') as eqFile:
            eqFile.writelines([
                f'"Ns"= {self.Ns}\n',
                f'"Np"= {self.Np}\n',
                f'"Nr"= {self.Nr}\n',
                f'"module"= {self.module}\n',
                f'"num_planet"= {self.num_planet}\n',

                f'"pressure_angle_deg"= {self.pressure_angle_deg}\n',

                f'"clearance_planet"= {self.clearance_planet}\n',
                f'"clearance_case_mount_holes_shell_thickness"= {self.clearance_case_mount_holes_shell_thickness}\n',
                f'"standard_clearance_1_5mm"= {self.standard_clearance_1_5mm}\n',
                f'"standard_clearance_2_mm"= {self.standard_clearance_2_mm}\n',
                f'"standard_fillet_1_5mm"= {self.standard_fillet_1_5mm}\n',
                f'"standard_fillet_3_mm"= {self.standard_fillet_3_mm}\n',
                f'"standard_bearing_insertion_chamfer"= {self.standard_bearing_insertion_chamfer}\n',
                f'"bearingIDClearanceMM"= {self.bearingIDClearanceMM}\n',
                f'"tight_clearance_3DP"= {self.tight_clearance_3DP}\n',
                f'"loose_clearance_3DP"= {self.loose_clearance_3DP}\n',
                f'"bearing_step_width"= {self.bearing_step_width}\n',

                f'"sun1_bearing_ID"= {self.sun1_bearing_ID}\n',
                f'"sun1_bearing_OD"= {self.sun1_bearing_OD}\n',
                f'"sun_coupler_hub_thickness"= {self.sun_coupler_hub_thickness}\n',
                f'"sun1_bearing_width"= {self.sun1_bearing_width}\n',
                f'"sun_central_bolt_dia"= {self.sun_central_bolt_dia}\n',

                f'"case_mounting_surface_height"= {self.case_mounting_surface_height}\n',
                f'"case_mounting_hole_dia"= {self.case_mounting_hole_dia}\n',
                f'"motor_case_thickness"= {self.motor_case_thickness}\n',
                f'"output_mount_hole_dia"= {self.output_mount_hole_dia}\n',
                f'"motor_case_OD_base_to_chamfer"= {self.motor_case_OD_base_to_chamfer}\n',
                f'"pattern_offset_from_motor_case_OD_base"= {self.pattern_offset_from_motor_case_OD_base}\n',
                f'"pattern_bulge_dia"= {self.pattern_bulge_dia}\n',
                f'"pattern_num_bulge"= {self.pattern_num_bulge}\n',
                f'"pattern_depth"= {self.pattern_depth}\n',
                f'"clearance_motor_and_case"= {self.clearance_motor_and_case}\n',
                f'"case_mounting_hole_shift"= {self.case_mounting_hole_shift}\n',
                f'"ring_hub_to_case_hole_num"= {self.ring_hub_to_case_hole_num}\n',
                f'"ring_hub_to_case_hole_dia"= {self.ring_hub_to_case_hole_dia}\n',

                f'"case_mounting_hole_allen_socket_dia"= {self.case_mounting_hole_allen_socket_dia}\n',
                f'"case_mounting_wrench_size"= {self.case_mounting_wrench_size}\n',
                f'"case_mounting_nut_depth"= {self.case_mounting_nut_depth}\n',

                f'"output_mount_nut_wrench_size"= {self.output_mount_nut_wrench_size}\n',
                f'"output_mount_hole_nut_depth"= {self.output_mount_hole_nut_depth}\n',

                f'"ring_hub_to_case_hole_nut_wrench_size"= {self.ring_hub_to_case_hole_nut_wrench_size}\n',
                f'"ring_hub_to_case_hole_nut_depth"= {self.ring_hub_to_case_hole_nut_depth}\n',

                f'"planet_pin_bolt_dia"= {self.planet_pin_bolt_dia}\n',
                f'"planet_shaft_step_offset"= {self.planet_shaft_step_offset}\n',
                f'"planet_bearing_OD"= {self.planet_bearing_OD}\n',
                f'"planet_bearing_width"= {self.planet_bearing_width}\n',
                f'"planet_bearing_ID"= {self.planet_bearing_ID}\n',

                f'"carrier_trapezoidal_support_sun_offset"= {self.carrier_trapezoidal_support_sun_offset}\n',
                f'"carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID"= {self.carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID}\n',
                f'"carrier_trapezoidal_support_hole_dia"= {self.carrier_trapezoidal_support_hole_dia}\n',
                f'"carrier_trapezoidal_support_hole_socket_head_dia"= {self.carrier_trapezoidal_support_hole_socket_head_dia}\n',
                f'"carrier_trapezoidal_support_hole_wrench_size"= {self.carrier_trapezoidal_support_hole_wrench_size}\n',
                f'"carrier_trapezoidal_support_nut_depth"= {self.carrier_trapezoidal_support_nut_depth}\n',

                f'"planet_pin_socket_head_dia"= {self.planet_pin_socket_head_dia}\n',
                f'"planet_pin_nut_wrench_size"= {self.planet_pin_nut_wrench_size}\n',
                f'"planet_pin_nut_depth"= {self.planet_pin_nut_depth}\n',

                f'"driver_upper_holes_dist_from_center"= {self.driver_upper_holes_dist_from_center}\n',
                f'"driver_lower_holes_dist_from_center"= {self.driver_lower_holes_dist_from_center}\n',
                f'"driver_side_holes_dist_from_center"= {self.driver_side_holes_dist_from_center}\n',
                f'"driver_mount_holes_dia"= {self.driver_mount_holes_dia}\n',
                f'"driver_mount_inserts_OD"= {self.driver_mount_inserts_OD}\n',
                f'"driver_mount_thickness"= {self.driver_mount_thickness}\n',
                f'"driver_mount_height"= {self.driver_mount_height}\n',
                f'"motor_mount_driver_hole_dia"= {self.motor_mount_driver_hole_dia}\n',
                f'"central_hole_offset_from_motor_mount_PCD"= {self.central_hole_offset_from_motor_mount_PCD}\n',
                f'"motor_mount_driver_hole_num"= {self.motor_mount_driver_hole_num}\n',
                f'"motor_mount_driver_nut_wrench_size"= {self.motor_mount_driver_nut_wrench_size}\n',
                f'"motor_mount_driver_nut_depth"= {self.motor_mount_driver_nut_depth}\n',

                f'"magnet_mount_hole_dia"= {self.magnet_mount_hole_dia}\n',
                f'"magnet_thickness"= {self.magnet_thickness}\n',
                f'"magnet_dia"= {self.magnet_dia}\n',
                f'"magnet_mount_thickness"= {self.magnet_mount_thickness}\n',
                f'"magnet_pattern_bulge_dia"= {self.magnet_pattern_bulge_dia}\n',
                f'"magnet_pattern_bulge_number"= {self.magnet_pattern_bulge_number}\n',
                f'"magnet_mount_height"= {self.magnet_mount_height}\n',

                f'"motor_OD"= {self.motor_OD}\n',
                f'"motor_height"= {self.motor_height}\n',
                f'"stator_ID"= {self.stator_ID}\n',
                f'"motor_rotor_base_thickness"= {self.motor_rotor_base_thickness}\n',
                f'"motor_rotor_base_ID"= {self.motor_rotor_base_ID}\n',
                f'"rotor_height"= {self.rotor_height}\n',
                f'"rotor_ID"= {self.rotor_ID}\n',
                f'"motor_stator_extrusion_depth"= {self.motor_stator_extrusion_depth}\n',
                f'"motor_stator_extrusion_dia"= {self.motor_stator_extrusion_dia}\n',
                f'"stator_height"= {self.stator_height}\n',
                f'"stator_OD"= {self.stator_OD}\n',
                f'"stator_top_rotor_top_offset"= {self.stator_top_rotor_top_offset}\n',
                f'"stator_hole_dia"= {self.stator_hole_dia}\n',
                f'"stator_hole_PCD"= {self.stator_hole_PCD}\n',
                f'"motor_rotor_hole_num"= {self.motor_rotor_hole_num}\n',
                f'"motor_rotor_hole_dia"= {self.motor_rotor_hole_dia}\n',
                f'"motor_rotor_hole_PCD"= {self.motor_rotor_hole_PCD}\n',
                f'"rotorCSKHeadUpperDiaMM"= {self.rotorCSKHeadUpperDiaMM}\n',
                f'"rotorCSKHeadHeightMM"= {self.rotorCSKHeadHeightMM}\n',

                f'"h_a"= {self.h_a}\n',
                f'"h_b"= {self.h_b}\n',
                f'"h_f"= {self.h_f}\n',
                f'"clr_tip_root"= {self.clr_tip_root}\n',

                f'"dp_s"= {self.dp_s}\n',
                f'"db_s"= {self.db_s}\n',
                f'"fw_s_calc"= {self.fw_s_calc}\n',
                f'"alpha_s"= {self.alpha_s}\n',
                f'"beta_s"= {self.beta_s}\n',

                f'"dp_p"= {self.dp_p}\n',
                f'"db_p"= {self.db_p}\n',
                f'"fw_p"= {self.fw_p}\n',
                f'"alpha_p"= {self.alpha_p}\n',
                f'"beta_p"= {self.beta_p}\n',

                f'"dp_r"= {self.dp_r}\n',
                f'"db_r"= {self.db_r}\n',
                f'"fw_r"= {self.fw_r}\n',
                f'"alpha_r"= {self.alpha_r}\n',
                f'"beta_r"= {self.beta_r}\n',

                f'"output_bearing_ID"= {self.output_bearing_ID}\n',
                f'"output_bearing_OD"= {self.output_bearing_OD}\n',
                f'"output_bearing_width"= {self.output_bearing_width}\n',

                f'"sun2_bearing_ID"= {self.sun2_bearing_ID}\n',
                f'"sun2_bearing_OD"= {self.sun2_bearing_OD}\n',
                f'"sun2_bearing_width"= {self.sun2_bearing_width}\n',

                f'"input_bearing_ID"= {self.input_bearing_ID}\n',
                f'"input_bearing_OD"= {self.input_bearing_OD}\n',
                f'"input_bearing_width"= {self.input_bearing_width}\n',

                f'"sec_carrier_thickness"= {self.sec_carrier_thickness}\n',

                f'"sun_hub_nut_wrench_size"= {self.sun_hub_nut_wrench_size}\n',
                f'"sun_hub_nut_depth"= {self.sun_hub_nut_depth}\n',
                f'"sun_hub_dia"= {self.sun_hub_dia}\n',

                f'"sun_central_bolt_socket_head_dia"= {self.sun_central_bolt_socket_head_dia}\n',
                f'"sun_central_nut_wrench_size"= {self.sun_central_nut_wrench_size}\n',
                f'"sun_central_nut_depth"= {self.sun_central_nut_depth}\n',

                f'"fw_s_used"= {self.fw_s_used}\n',

                f'"carrier_thickness_top"= {self.carrier_thickness_top}\n',
                f'"carrier_top_to_mid_hole_dia"= {self.carrier_top_to_mid_hole_dia}\n',
                f'"carrier_top_to_mid_bolt_socket_dia"= {self.carrier_top_to_mid_bolt_socket_dia}\n',
                f'"carrier_top_to_mid_nut_wrench_size"= {self.carrier_top_to_mid_nut_wrench_size}\n',
                f'"carrier_top_to_mid_nut_depth"= {self.carrier_top_to_mid_nut_depth}\n',

                f'"carrier_thickness_mid"= {self.carrier_thickness_mid}\n',
                f'"carrier_thickness"= {self.carrier_thickness}\n',

                f'"ring_hub_thickness"= {self.ring_hub_thickness}\n',
                f'"ring_stator_case_thickness"= {self.ring_stator_case_thickness}\n',
                f'"ring_hub_offset_stator_hole_PCD"= {self.ring_hub_offset_stator_hole_PCD}\n',
                f'"stator_ring_hub_hole_num"= {self.stator_ring_hub_hole_num}\n',

                f'"motor_case_height"= {self.motor_case_height}\n',

                f'"wire_slot_length"= {self.wire_slot_length}\n',
                f'"wire_slot_radius"= {self.wire_slot_radius}\n',

                f'"actuactor_mount_hole_dia"= {self.actuactor_mount_hole_dia}\n',
                f'"actuactor_mount_nut_wrench_size"= {self.actuactor_mount_nut_wrench_size}\n',
                f'"actuactor_mount_nut_depth"= {self.actuactor_mount_nut_depth}\n',               
            ])

    # ═══════════════════════════════════════════════════════════════════
    #  ERRORS
    # ═══════════════════════════════════════════════════════════════════
    def SecCarrierODConstraint(self):
        Ns     = self.planetaryGearbox.Ns
        Np     = self.planetaryGearbox.Np
        module = self.planetaryGearbox.module

        motor_rotor_base_ID = self.motor_rotor_base_ID

        sec_carrier_OD = module*(Ns+Np) + self.planet_pin_socket_head_dia + self.standard_clearance_1_5mm * 2
        max_sec_carrier_OD = motor_rotor_base_ID - 2*self.standard_clearance_1_5mm

        return  max_sec_carrier_OD > sec_carrier_OD
            
    def maxRingGearOD(self):
        self.max_ring_gear_ha = self.stator_ID - (self.ring_stator_case_thickness * 2)
        max_ring_gear_ha=self.max_ring_gear_ha
        Nr     = self.planetaryGearbox.Nr      # ← live value
        module = self.planetaryGearbox.module  # ← live value
        result = max_ring_gear_ha > ((Nr * module) + 2*module)
        return result
 

    #--------------------------------------------
    # Gear tooth stress analysis
    #--------------------------------------------
    def getToothForces(self, constraintCheck=True):
        if constraintCheck:
            # Check if the constraints are satisfied
            if not self.planetaryGearbox.geometricConstraint():
                print("Geometric constraint not satisfied")
                return
            if not self.planetaryGearbox.meshingConstraint():
                print("Meshing constraint not satisfied")
                return
            if not self.planetaryGearbox.noPlanetInterferenceConstraint_old():
                print("No planet interference constraint not satisfied")
                return
        
        Rs_Mt = self.planetaryGearbox.getPCRadiusSunM()
        Rp_Mt = self.planetaryGearbox.getPCRadiusPlanetM()
        Rr_Mt = self.planetaryGearbox.getPCRadiusRingM()

        numPlanet = self.planetaryGearbox.numPlanet
        Ns = self.planetaryGearbox.Ns
        Np = self.planetaryGearbox.Np
        Nr = self.planetaryGearbox.Nr
        module = self.planetaryGearbox.module


        wSun = self.motor.getMaxMotorAngVelRadPerSec()
        wCarrier = wSun/self.planetaryGearbox.gearRatio()
        wPlanet = ( -Ns / (Nr - Ns) ) * wSun

        Ft = (self.serviceFactor*self.motor.getMaxMotorTorque())/( numPlanet * Rs_Mt)
        
        return Ft

    def lewisStressAnalysisMinFacewidth(self):
        # Check if the constraints are satisfied
        if not self.planetaryGearbox.geometricConstraint():
            print("Geometric constraint not satisfied")
            return
        if not self.planetaryGearbox.meshingConstraint():
            print("Meshing constraint not satisfied")
            return
        if not self.planetaryGearbox.noPlanetInterferenceConstraint():
            print("No planet interference constraint old not satisfied")
            return
        
        Rs_Mt = self.planetaryGearbox.getPCRadiusSunM()
        Rp_Mt = self.planetaryGearbox.getPCRadiusPlanetM()
        Rr_Mt = self.planetaryGearbox.getPCRadiusRingM()

        numPlanet = self.planetaryGearbox.numPlanet
        Ns = self.planetaryGearbox.Ns
        Np = self.planetaryGearbox.Np
        Nr = self.planetaryGearbox.Nr
        module = self.planetaryGearbox.module

        wSun = self.motor.getMaxMotorAngVelRadPerSec()
        wCarrier = wSun/self.planetaryGearbox.gearRatio()
        wPlanet = ( -Ns / (Nr - Ns) ) * wSun
        
        Ft = self.getToothForces(False)

        ySun    = 0.154 - 0.912 / Ns
        yPlanet = 0.154 - 0.912 / Np
        yRing   = 0.154 - 0.912 / Nr

        V_sp = ( wSun * Rs_Mt )
        V_rp = ( wCarrier*(Rs_Mt + Rp_Mt) + (wPlanet * Rp_Mt) )
        
        if V_sp <= 7.5:
            Kv_sun = 3/(3+V_sp)
        elif V_sp > 7.5 and V_sp <= 12.5:
            Kv_sun = 4.5/(4.5 + V_sp)

        if V_rp <= 7.5:
            Kv_planet = 3/(3+V_rp)
        elif V_rp > 7.5 and V_rp <= 12.5:
            Kv_planet = 4.5/(4.5 + V_rp)

        Kv_ring = Kv_planet

        P = np.pi*module*0.001 # m
        
        # Lewis static load capacity
        bMin_sun     = (self.FOS * Ft / (self.planetaryGearbox.maxGearAllowableStressPa * ySun    * Kv_sun    * P)) # m
        bMin_planet1 = (self.FOS * Ft / (self.planetaryGearbox.maxGearAllowableStressPa * yPlanet * Kv_sun    * P))
        bMin_planet2 = (self.FOS * Ft / (self.planetaryGearbox.maxGearAllowableStressPa * yPlanet * Kv_planet * P))
        bMin_ring    = (self.FOS * Ft / (self.planetaryGearbox.maxGearAllowableStressPa * yRing   * Kv_ring   * P))

        if bMin_planet1 > bMin_planet2:
            bMin_planet = bMin_planet1
        else:
            bMin_planet = bMin_planet2

        if bMin_ring < bMin_planet:
            bMin_ring = bMin_planet
        else:
            bMin_planet = bMin_ring

        self.planetaryGearbox.setfwSunMM    ( bMin_sun    * 1000)
        self.planetaryGearbox.setfwPlanetMM ( bMin_planet * 1000)
        self.planetaryGearbox.setfwRingMM   ( bMin_ring   * 1000)

    def mitStressAnalysisMinFacewidth(self):
        # Check if the constraints are satisfied
        if not self.planetaryGearbox.geometricConstraint():
            print("Geometric constraint not satisfied")
            return
        if not self.planetaryGearbox.meshingConstraint():
            print("Meshing constraint not satisfied")
            return
        if not self.planetaryGearbox.noPlanetInterferenceConstraint():
            print("No planet interference constraint old not satisfied")
            return
        
        Rs_Mt = self.planetaryGearbox.getPCRadiusSunM()
        Rp_Mt = self.planetaryGearbox.getPCRadiusPlanetM()
        Rr_Mt = self.planetaryGearbox.getPCRadiusRingM()

        numPlanet = self.planetaryGearbox.numPlanet
        Ns = self.planetaryGearbox.Ns
        Np = self.planetaryGearbox.Np
        Nr = self.planetaryGearbox.Nr
        module = self.planetaryGearbox.module

        wSun = self.motor.getMaxMotorAngVelRadPerSec()
        wCarrier = wSun/self.planetaryGearbox.gearRatio()
        wPlanet = ( -Ns / (Nr - Ns) ) * wSun

        # Ft = (self.serviceFactor*self.motor.getMaxMotorTorque())/( numPlanet * Rs_Mt)
        
        Ft = self.getToothForces(False)
        
        # Lewis static load capacity
        _,_,CR = self.planetaryGearbox.contactRatio_sunPlanet()
        qe = 1 / CR
        # qk = 1.85 + 0.35 * (np.log(Ns) / np.log(100)) 
        qk = (7.65734266e-08 * Ns**4
            - 2.19500130e-05 * Ns**3
            + 2.33893357e-03 * Ns**2
            - 1.13320908e-01 * Ns
            + 4.44727778)
        bMin_sun_mit    = (self.FOS * Ft * qe * qk / (self.planetaryGearbox.maxGearAllowableStressPa * module * 0.001)) # m
        bMin_planet_mit = (self.FOS * Ft * qe * qk / (self.planetaryGearbox.maxGearAllowableStressPa * module * 0.001))
        bMin_ring_mit   = (self.FOS * Ft * qe * qk / (self.planetaryGearbox.maxGearAllowableStressPa * module * 0.001))


        #------------- Contraint in planet to accomodate its bearings------------------------------------------
        if (bMin_planet_mit * 1000 < (self.planet_bearing_width*2 + self.standard_clearance_1_5mm * 2 / 3)) : 
            bMin_planet_mit = (self.planet_bearing_width*2 + self.standard_clearance_1_5mm * 2 / 3) / 1000
            bMin_ring_mit = bMin_planet_mit # FT on both are same

        bMin_sun_mitMM    = bMin_sun_mit    * 1000
        bMin_planet_mitMM = bMin_planet_mit * 1000
        bMin_ring_mitMM   = bMin_ring_mit   * 1000

        self.planetaryGearbox.setfwSunMM    ( bMin_sun_mit    * 1000)
        self.planetaryGearbox.setfwPlanetMM ( bMin_planet_mit * 1000)
        self.planetaryGearbox.setfwRingMM   ( bMin_ring_mit   * 1000)

        # bMin_sun_lewisMM, bMin_planet_lewisMM, bMin_ring_lewisMM = self.lewisStressAnalysisMinFacewidth()

        return bMin_sun_mitMM, bMin_planet_mitMM, bMin_ring_mitMM

    def AGMAStressAnalysisMinFacewidth(self):
        # Check if the constraints are satisfied
        if not self.planetaryGearbox.geometricConstraint():
            print("Geometric constraint not satisfied")
            return
        if not self.planetaryGearbox.meshingConstraint():
            print("Meshing constraint not satisfied")
            return
        if not self.planetaryGearbox.noPlanetInterferenceConstraint_old():
            print("No planet interference constraint not satisfied")
            return
        
        Rs_Mt = self.planetaryGearbox.getPCRadiusSunM()
        Rp_Mt = self.planetaryGearbox.getPCRadiusPlanetM()
        Rr_Mt = self.planetaryGearbox.getPCRadiusRingM()

        numPlanet = self.planetaryGearbox.numPlanet
        Ns = self.planetaryGearbox.Ns
        Np = self.planetaryGearbox.Np
        Nr = self.planetaryGearbox.Nr
        module = self.planetaryGearbox.module

        wSun = self.motor.getMaxMotorAngVelRadPerSec()
        wCarrier = wSun/self.planetaryGearbox.gearRatio()
        wPlanet = ( -Ns / (Nr - Ns) ) * wSun

        pressureAngle = self.planetaryGearbox.pressureAngle

        V_sp = abs( wSun * Rs_Mt )
        V_rp = abs( wCarrier*(Rs_Mt + Rp_Mt) + (wPlanet * Rp_Mt) )

        # Tangential forces
        Wt = self.getToothForces(False) # Wt includes Ko (overload/service factor)

        # T Krishna Rao - Design of Machine Elements - II pg.191
        # Modified Lewis Form Factor Y = pi*y for pressure angle = 20
        Y_planet   = (0.154 - 0.912 / Np) * np.pi
        Y_sun   = (0.154 - 0.912 / Ns) * np.pi
        Y_ring   = (0.154 - 0.912 / Nr) * np.pi

        # AGMA 908-B89 pg.16
        # Kf Fatigue stress concentration factor
        H = 0.331 - (0.436 * np.pi * pressureAngle / 180)
        L = 0.324 - (0.492 * np.pi * pressureAngle / 180)
        M = 0.261 + (0.545 * np.pi * pressureAngle / 180) 
        # t -> tooth thickness, r -> fillet radius and l -> tooth height
        t_planet = (13.5 * Y_planet)**(1/2) * module
        r_planet = .3*module
        l_planet = 2.25 * module
        Kf_planet = H + (t_planet / r_planet)**(L) * (t_planet / l_planet)**(M)

        t_sun = (13.5 * Y_sun)**(1/2) * module
        r_sun = .3*module
        l_sun = 2.25 * module
        Kf_sun = H + (t_sun / r_sun)**(L) * (t_sun / l_sun)**(M)

        t_ring = (13.5 * Y_ring)**(1/2) * module
        r_ring = .3*module
        l_ring = 2.25 * module
        Kf_ring = H + (t_ring / r_ring)**(L) * (t_ring / l_ring)**(M)

        # Shigley's Mechanical Engineering Design 9th Edition pg.752
        # Yj Geometry factor
        Yj_planet = Y_planet/Kf_planet
        Yj_sun = Y_sun/Kf_sun
        Yj_ring = Y_ring/Kf_ring 

        # Kv Dynamic factor
        # Shigley's Mechanical Engineering Design 9th Edition pg.756
        Qv = 7      # Quality numbers 3 to 7 will include most commercial-quality gears.
        B_planet =  0.25*(12-Qv)**(2/3)
        A_planet = 50 + 56*(1-B_planet)
        Kv_planet = ((A_planet+np.sqrt(200*max(V_rp, V_sp)))/A_planet)**B_planet

        B_sun =  0.25*(12-Qv)**(2/3)
        A_sun = 50 + 56*(1-B_sun)
        Kv_sun = ((A_sun+np.sqrt(200*V_sp))/A_sun)**B_sun

        B_ring =  0.25*(12-Qv)**(2/3)
        A_ring = 50 + 56*(1-B_ring)
        Kv_ring = ((A_ring+np.sqrt(200*V_rp))/A_ring)**B_planet

        # T Krishna Rao - Design of Machine Elements - II pg.191
        # if V_sp <= 7.5:
        #     Kv_sun = (3+V_sp)/3
        # elif V_sp > 7.5 and V_sp <= 12.5:
        #     Kv_sun = (4.5 + V_sp)/4.5

        # if max(V_rp, V_sp) <= 7.5:
        #     Kv_planet = (3+max(V_rp, V_sp))/3
        # elif max(V_rp, V_sp) > 7.5 and max(V_rp, V_sp) <= 12.5:
        #     Kv_planet = (4.5 + max(V_rp, V_sp))/4.5
        # Kv_ring = Kv_planet

        # Shigley's Mechanical Engineering Design 9th Edition pg.764
        # Ks Size factor (can be omitted if enough information is not available)
        Ks = 1

        # NPTEL Fatigue Consideration in Design lecture-7 pg.10 Table-7.4 (https://archive.nptel.ac.in/courses/112/106/112106137/)
        # Kh Load-distribution factor (0-50mm, less rigid mountings, less accurate gears)
        Kh = 1 #TODO: Check its value

        # Shigley's Mechanical Engineering Design 9th Edition pg.764
        # Kb Rim-thickness factor (the gears have a uniform thickness)
        Kb = 1
        
        # AGMA bending stress equation (Shigley's Mechanical Engineering Design 9th Edition pg.746)  
        bMin_planet = (self.FOS * Wt * Kv_planet * Ks * Kh * Kb) / (module * Yj_planet * self.planetaryGearbox.maxGearAllowableStressPa * 0.001)
        bMin_sun    = (self.FOS * Wt * Kv_sun    * Ks * Kh * Kb) / (module * Yj_sun    * self.planetaryGearbox.maxGearAllowableStressPa * 0.001)
        bMin_ring   = (self.FOS * Wt * Kv_ring   * Ks * Kh * Kb) / (module * Yj_ring   * self.planetaryGearbox.maxGearAllowableStressPa * 0.001)

        if bMin_ring < bMin_planet:
            bMin_ring = bMin_planet
        else:
            bMin_planet = bMin_ring

        self.planetaryGearbox.setfwSunMM    ( bMin_sun    * 1000)
        self.planetaryGearbox.setfwPlanetMM ( bMin_planet * 1000)
        self.planetaryGearbox.setfwRingMM   ( bMin_ring   * 1000)

    def updateFacewidth(self):
        if self.stressAnalysisMethodName == "Lewis":
            self.lewisStressAnalysisMinFacewidth()
        elif self.stressAnalysisMethodName == "AGMA":
            self.AGMAStressAnalysisMinFacewidth()
        elif self.stressAnalysisMethodName == "MIT":
            self.mitStressAnalysisMinFacewidth()

    def getMassKG_3DP(self):
        self.setVariables()
        module    = self.planetaryGearbox.module
        Ns        = self.planetaryGearbox.Ns
        Np        = self.planetaryGearbox.Np
        Nr        = self.planetaryGearbox.Nr
        numPlanet = self.planetaryGearbox.numPlanet

        #------------------------------------
        # density of materials
        #------------------------------------
        # density of both gears and the structural materials is the same in 3D printed gearbox
        density_3DP_material = self.planetaryGearbox.densityGears #kg/m^3

        #------------------------------------
        # Face Width
        #------------------------------------
        sunFwMM     = self.planetaryGearbox.fwSunMM
        planetFwMM  = self.planetaryGearbox.fwPlanetMM
        ringFwMM    = self.planetaryGearbox.fwRingMM

        sunFwM    = sunFwMM    * 0.001
        planetFwM = planetFwMM * 0.001
        ringFwM   = ringFwMM   * 0.001

        fw_s_used = (self.sun2_bearing_width + self.bearing_step_width  
                          + self.sec_carrier_thickness + self.clearance_planet + self.fw_p 
                          - (self.sun_coupler_hub_thickness - 2*self.standard_clearance_1_5mm) + self.bearing_step_width/2 )

        #------------------------------------
        # Diameter and Radius
        #------------------------------------
        DiaSunMM    = Ns * module
        DiaPlanetMM = Np * module
        DiaRingMM   = Nr * module

        RadiusSunMM    = DiaSunMM    * 0.5
        RadiusPlanetMM = DiaPlanetMM * 0.5
        RadiusRingMM   = DiaRingMM   * 0.5

        #======================================
        # Mass Calculation
        #======================================

        #--------------------------------------
        # Dependent variables
        #--------------------------------------
        h_b = 1.25 * module

        #--------------------------------------
        # Mass: sspg_motor_casing
        # in two parts:
        # 1. Casing
        # 2. casing Cap
        #--------------------------------------

        Motor_case_ID     = self.motor_OD + (self.clearance_motor_and_case * 2)
        Motor_case_height = self.motor_case_height
        Motor_case_OD = Motor_case_ID + (self.motor_case_thickness* 2)
        Motor_case_thickness = self.motor_case_thickness
        
        #Motor_case_volume = ( (np.pi * ((Motor_case_OD * 0.5)**2 - ((self.output_bearing_OD*0.5) - self.standard_clearance_2_mm)**2) * self.motor_case_thickness )
        #                    + (np.pi * ((Motor_case_OD * 0.5)**2 - (Motor_case_ID * 0.5)**2) * Motor_case_height) 
        #                   + (np.pi * ((Motor_case_OD * 0.5)**2 - (self.input_bearing_OD*0.5)**2) * (self.input_bearing_width + self.bearing_step_width))
        #                    + (np.pi * ((motor_case_mounting_structure_OD  * 0.5)**2 - (motor_case_mounting_structure_ID * 0.5)**2) * motor_case_mounting_structure_height *6)
        #) * 1e-9

        #----------------
        # casing cap
        #----------------

        #volume of top mounting bracket
        mounting_bracket_thickness= self.actuactor_mount_nut_depth + self.standard_clearance_2_mm + self.standard_clearance_2_mm - self.motor_case_thickness
        mounting_bracket_OD = Motor_case_ID
        mounting_bracket_ID = Motor_case_OD - 2*(self.actuactor_mount_nut_wrench_size + self.standard_clearance_2_mm) 

        mounting_bracket_volume = (np.pi * ((mounting_bracket_OD * 0.5)**2 - (mounting_bracket_ID * 0.5)**2) * mounting_bracket_thickness) * 1e-9

        #volume of top plate of casing
        top_plate_casing_volume = (np.pi * ((Motor_case_OD/2)**2 - ((self.output_bearing_OD*0.5) - self.standard_clearance_2_mm)**2) * Motor_case_thickness) * 1e-9

        #volume of curved surface of casing
        top_curve_casing_height = mounting_bracket_thickness + self.pattern_depth
        top_curve_casing_volume = (np.pi * ((Motor_case_OD * 0.5)**2 - (Motor_case_ID * 0.5)**2) * top_curve_casing_height) * 1e-9  

        casing_cap_volume =  top_curve_casing_volume + top_plate_casing_volume + mounting_bracket_volume 

        #----------------
        # casing 
        #----------------

        #volume of bottom plate of casing
        bottom_plate_ID = ((self.magnet_dia + 2 * self.standard_clearance_2_mm) 
                            + 2 * (self.magnet_pattern_bulge_dia + self.standard_clearance_1_5mm))
        bottom_plate_casing_volume = (np.pi * ((Motor_case_OD/2)**2 - 
                                    (bottom_plate_ID*0.5)**2) 
                                    * Motor_case_thickness) * 1e-9
        
        #volume of curved surface of casing
        bottom_curve_casing_height = Motor_case_height - top_curve_casing_height 
        bottom_curve_casing_volume = (np.pi * ((Motor_case_OD * 0.5)**2 - (Motor_case_ID * 0.5)**2) 
                                    * bottom_curve_casing_height) * 1e-9  
        #input bearing structure
        input_bearing_structure_ID = self.input_bearing_OD
        input_bearing_structure_OD = Motor_case_ID
        input_bearing_structure_width = self.input_bearing_width + self.bearing_step_width
        input_bearing_structure_volume = (np.pi * ((input_bearing_structure_OD  * 0.5)**2 
                                        - (input_bearing_structure_ID * 0.5)**2) * input_bearing_structure_width
                                        ) * 1e-9
        casing_volume = bottom_plate_casing_volume + bottom_curve_casing_volume + input_bearing_structure_volume 

        #motor_mounting_structure
        motor_case_mounting_structure_OD     = self.case_mounting_hole_allen_socket_dia + 2*self.clearance_case_mount_holes_shell_thickness
        motor_case_mounting_structure_ID     = self.case_mounting_hole_dia 
        motor_case_mounting_structure_height = Motor_case_height + 2*Motor_case_thickness
        motor_case_mounting_structure_volume = (np.pi * ((motor_case_mounting_structure_OD  * 0.5)**2 - (motor_case_mounting_structure_ID * 0.5)**2) * motor_case_mounting_structure_height *6) * 1e-9 

        #motor_mounting_pattern depth
        #motor_mounting_pattern_height = self.case_mounting_surface_height + self.pattern_depth
        #motor_mounting_pattern_OD     = Motor_case_ID
        #motor_mounting_pattern_ID     = Motor_case_OD - 2*self.motor_case_OD_base_to_chamfer
        #motor_mounting_pattern_volume = (np.pi * ((motor_mounting_pattern_OD  * 0.5)**2 
        #                                - (motor_mounting_pattern_ID * 0.5)**2) * motor_mounting_pattern_height
        #                                ) * 1e-9

        Motor_case_volume = (casing_volume + motor_case_mounting_structure_volume  + casing_cap_volume #+ motor_mounting_pattern_volume
                                )
        Motor_case_mass   = Motor_case_volume * density_3DP_material

        #--------------------------------------
        # Mass: Ring_gear
        #--------------------------------------
        # Mass of the ring gear includes the mass of:
        # 1. Ring gear
        # 2. ring with stator
        # 3. Ring hub
        # 4. Bearing Structure
        #--------------------------------------
        ring_ID      = Nr * module
        ringFwUsedMM = ringFwMM
        ring_OD      = self.stator_ID

        ring_stator_OD     = self.stator_ID 
        ring_stator_ID     = ring_stator_OD - self.ring_stator_case_thickness*2
        ring_stator_height = self.motor_height - fw_s_used

        ring_hub_OD = self.stator_hole_PCD + self.ring_hub_offset_stator_hole_PCD*2
        ring_hub_ID = ring_stator_ID      
        ring_hub_thickness = self.ring_hub_thickness  

        bearing_holding_structure_OD     = ring_stator_ID
        bearing_holding_structure_ID     = self.output_bearing_OD
        bearing_holding_structure_height = self.bearing_step_width + self.output_bearing_width - (self.motor_case_thickness - self.bearing_step_width)

        ring_gear_volume                 = np.pi * (((ring_OD*0.5)**2) - ((ring_ID)*0.5)**2) * ringFwUsedMM * 1e-9
        bearing_holding_structure_volume = np.pi * (((bearing_holding_structure_OD*0.5)**2) - 
                                                    ((bearing_holding_structure_ID*0.5)**2)) * bearing_holding_structure_height * 1e-9
        ring_stator_structure_volume     = np.pi * (((ring_stator_OD*0.5)**2) - 
                                                    ((ring_stator_ID*0.5)**2)) * ring_stator_height * 1e-9
        ring_hub_volume                  = np.pi * (((ring_hub_OD*0.5)**2) - ((ring_hub_ID)*0.5)**2) * ring_hub_thickness * 1e-9

        ring_mass = (ring_gear_volume + bearing_holding_structure_volume + ring_stator_structure_volume + ring_hub_volume) * density_3DP_material

        #--------------------------------------
        # Mass: sspg_planet
        #--------------------------------------
        planet_bearing_structure_OD = self.planet_bearing_OD
        planet_bearing_structure_thickness = self.planet_bearing_width
        
        planet_gear_volume = (np.pi * ((DiaPlanetMM*0.5)**2) * planetFwMM) * 1e-9
        planet_bearing_strcuture_volume = np.pi * ((planet_bearing_structure_OD*0.5) ** 2) * planet_bearing_structure_thickness * 1e-9

        planet_volume = planet_gear_volume - 2*planet_bearing_strcuture_volume
        planet_mass   = planet_volume * density_3DP_material * numPlanet

        #----------------------------------
        # Mass: sspg_carrier
        #----------------------------------
        # Mass of the sspg_carrier includes the mass of:
        # 1. top carrier
        # 2. mid carrier
        #--------------------------------------
        top_carrier_OD     = self.output_bearing_ID
        top_carrier_ID     = self.sun1_bearing_OD - self.standard_clearance_2_mm * 2
        top_carrier_height = self.carrier_thickness_top
        
        mid_carrier_OD     = module*(Ns+Np) + self.planet_pin_socket_head_dia + self.standard_clearance_1_5mm * 2
        mid_carrier_ID     = self.sun1_bearing_OD
        mid_carrier_height = self.carrier_thickness_mid

        #trapezoidal volume
        trapezoidal_height = self.clearance_planet + planetFwMM + self.clearance_planet
        trapezoidal_volume =  np.pi * ((((mid_carrier_OD*0.5)-((DiaSunMM + 2*self.carrier_trapezoidal_support_sun_offset)*0.5))*0.5)**2) * numPlanet * trapezoidal_height  

        carrier_shaft_OD = self.planet_bearing_ID
        carrier_shaft_height = planetFwMM + self.clearance_planet * 2
        carrier_shaft_num = numPlanet * 2

        carrier_volume = (np.pi * (((top_carrier_OD*0.5)**2) - ((top_carrier_ID)*0.5)**2) * top_carrier_height
                        + np.pi * (((mid_carrier_OD*0.5)**2) - ((mid_carrier_ID)*0.5)**2) * mid_carrier_height
                        #+ trapezoidal_volume
                        + np.pi * ((carrier_shaft_OD*0.5)**2) * carrier_shaft_height * carrier_shaft_num
                        ) * 1e-9

        carrier_mass = carrier_volume * density_3DP_material

        #----------------------------------
        # Mass: sspg_sun
        #----------------------------------
        sun_hub_dia = self.sun_hub_dia
        sun_coupler_hub_thickness = self.sun_coupler_hub_thickness

        sun_shaft_dia    = self.sun1_bearing_ID
        sun_shaft_height = self.sun1_bearing_width + self.bearing_step_width

        magnet_structure_OD = ((self.magnet_dia + 2 * self.standard_clearance_2_mm) 
                            + 2 * (self.magnet_pattern_bulge_dia))
        magnet_structure_ID = self.sun_central_bolt_socket_head_dia
        magnet_structure_thickness = self.bearing_step_width + self.motor_case_thickness + self.driver_mount_thickness * 2

        #sun_hub_bearing_volume
        sun_hub_carrier_OD = self.sun2_bearing_OD + 2*self.standard_clearance_1_5mm*5
        sun_hub_carrier_ID = self.sun2_bearing_ID
        sun_hub_carrier_height = self.sun_coupler_hub_thickness - self.standard_clearance_1_5mm * 2


        sun_hub_volume   = np.pi * ((sun_hub_dia*0.5) ** 2) * sun_coupler_hub_thickness * 1e-9
        sun_gear_volume  = np.pi * ((DiaSunMM * 0.5) ** 2) * fw_s_used * 1e-9
        sun_shaft_volume = np.pi * ((sun_shaft_dia*0.5) ** 2) * sun_shaft_height * 1e-9
        magnet_structure_volume = np.pi * (((magnet_structure_OD*0.5) ** 2)-((magnet_structure_ID*0.5) ** 2)) * magnet_structure_thickness * 1e-9
        central_bolt_volume = (np.pi * ((self.sun_central_bolt_dia*0.5)**2)
                                *(fw_s_used+sun_shaft_height+magnet_structure_thickness+sun_coupler_hub_thickness))* 1e-9
        sun_hub_carrier_volume = (np.pi * (((sun_hub_carrier_OD*0.5)**2) - ((sun_hub_carrier_ID*0.5)**2)) * sun_hub_carrier_height)* 1e-9 

        sun_volume       = sun_hub_volume + sun_gear_volume + sun_shaft_volume + magnet_structure_volume-central_bolt_volume - sun_hub_carrier_volume
        sun_mass         = sun_volume * density_3DP_material

        #--------------------------------------
        # Mass: sspg_sec_carrier
        #--------------------------------------
        sec_carrier_top_OD = mid_carrier_OD
        sec_carrier_top_ID = ((self.Np + self.Ns) * self.module) - (
                             self.planet_pin_nut_wrench_size / 2 + self.standard_clearance_1_5mm
                             ) * 2
        sec_carrier_top_thickness = self.sec_carrier_thickness 

        sec_carrier_bottom_OD = self.sun2_bearing_OD + 2*self.standard_clearance_1_5mm*4 
        sec_carrier_bottom_ID = self.sun2_bearing_OD
        sec_carrier_bottom_thickness = self.sun2_bearing_width + self.bearing_step_width 

        sec_carrier_volume = ((np.pi * ((sec_carrier_top_OD*0.5)**2 - (sec_carrier_top_ID*0.5)**2) * sec_carrier_top_thickness)
                            +(np.pi * ((sec_carrier_bottom_OD*0.5)**2 - (sec_carrier_bottom_ID*0.5)**2) * sec_carrier_bottom_thickness)) * 1e-9
        sec_carrier_mass   = sec_carrier_volume * density_3DP_material

        #--------------------------------------
        # Mass: magnet_mount
        #--------------------------------------
        #magnet_mount_OD = self.magnet_dia + 4*self.standard_clearance_2_mm
        #magnet_mount_thickness = self.magnet_mount_thickness*2

        #magnet_mount_volume = (np.pi * ((magnet_mount_OD*0.5)**2) * magnet_mount_thickness) * 1e-9
        #magnet_mount_mass   = magnet_mount_volume * density_3DP_material

        #--------------------------------------
        # Mass: sspg_sun1_bearing
        #--------------------------------------
        sun1_bearing_mass       = 0.004 # kg

        #--------------------------------------
        # Mass: sspg_planet_bearing
        #--------------------------------------
        planet_bearing_mass          = 1 * 0.001 # kg
        planet_bearing_num           = numPlanet * 2
        planet_bearing_combined_mass = planet_bearing_mass * planet_bearing_num

        #--------------------------------------
        # Mass: sspg_output_bearing
        #--------------------------------------
        OutputBearingIdrequiredMM  = self.output_bearing_ID 
        outputbearing              = bearings_discrete(OutputBearingIdrequiredMM)
        self.output_bearing_mass   = outputbearing.getBearingMassKG()
        output_bearing_mass = self.output_bearing_mass # kg

        #--------------------------------------
        # Mass: sspg_input_bearing
        #--------------------------------------
        InputBearingIdrequiredMM  = self.input_bearing_ID
        inputbearing               = bearings_discrete(InputBearingIdrequiredMM)
        self.input_bearing_mass    = inputbearing.getBearingMassKG()
        input_bearing_mass        = self.input_bearing_mass # kg

        #--------------------------------------
        # Mass: sspg_sun2_bearing
        #--------------------------------------
        Sun2BearingIdrequiredMM  = self.sun2_bearing_ID
        sun2bearing              = bearings_discrete(Sun2BearingIdrequiredMM)
        self.sun2_bearing_mass     = sun2bearing.getBearingMassKG()
        sun2_bearing_mass = self.sun2_bearing_mass # kg

        self.Motor_case_mass              = Motor_case_mass
        self.ring_mass                    = ring_mass
        self.carrier_mass                 = carrier_mass
        self.sun_mass                     = sun_mass
        self.sec_carrier_mass             = sec_carrier_mass
        self.planet_mass                  = planet_mass
        self.planet_bearing_combined_mass = planet_bearing_combined_mass
        self.sun2_bearing_mass            = sun2_bearing_mass
        self.input_bearing_mass           = input_bearing_mass
        self.output_bearing_mass          = output_bearing_mass
        self.sun1_bearing_mass            = sun1_bearing_mass

        #----------------------------------------
        # Total Actuator Mass
        #----------------------------------------
        Actuator_mass = ( self.motorMassKG
                        + self.Motor_case_mass 
                        + self.ring_mass 
                        + self.carrier_mass 
                        + self.sun_mass 
                        + self.sec_carrier_mass 
                        + self.planet_mass 
                        + self.planet_bearing_combined_mass 
                        + self.sun2_bearing_mass 
                        + self.input_bearing_mass 
                        + self.output_bearing_mass
                        + self.sun1_bearing_mass)

        Actuator_mass_without_bearing = (self.Motor_case_mass 
                        + self.ring_mass 
                        + self.carrier_mass 
                        + self.sun_mass 
                        + self.sec_carrier_mass 
                        + self.planet_mass 
                        )
        
        self.Actuator_mass = Actuator_mass
        self.Actuator_mass_without_bearing = Actuator_mass_without_bearing 

        return Actuator_mass
    
    def print_mass_of_parts_3DP(self):
        print("Motor_case_mass: ",              1000 * self.Motor_case_mass)
        print("ring_mass: ",                    1000 * self.ring_mass)
        print("carrier_mass: ",                 1000 * self.carrier_mass)
        print("sun_mass: ",                     1000 * self.sun_mass)
        print("sec_carrier_mass: ",             1000 * self.sec_carrier_mass)
        print("planet_mass: ",                  1000 * self.planet_mass)
        print("planet_bearing_combined_mass: ", 1000 * self.planet_bearing_combined_mass)
        print("sun2_bearing_mass: ",            1000 * self.sun2_bearing_mass)
        print("input_bearing_mass: ",           1000 * self.input_bearing_mass)
        print("output_bearing_mass: ",          1000 * self.output_bearing_mass)
        print("sun1_bearing_mass: ",            1000 * self.sun1_bearing_mass)

        print("Actuator_mass_without_bearing:", 1000 * self.Actuator_mass_without_bearing)
        print("Actuator_mass:",                 1000 * self.Actuator_mass)

        print("---------------------------------------------------")

class optimizationInternalSingleStageActuator:
    def __init__(self,
                 design_params,
                 gear_standard_paramaeters,
                 K_Mass               = 1.0,
                 K_Eff                = -2.0,
                 K_Width              = 0.2,
                 MODULE_MIN           = 0.5,
                 MODULE_MAX           = 1.2,
                 NUM_PLANET_MIN       = 3,
                 NUM_PLANET_MAX       = 7,
                 NUM_TEETH_SUN_MIN    = 20,
                 NUM_TEETH_PLANET_MIN = 26,
                 GEAR_RATIO_MIN       = 5,
                 GEAR_RATIO_MAX       = 12,
                 GEAR_RATIO_STEP      = 1):
        
        self.K_Mass                        = K_Mass
        self.K_Eff                         = K_Eff
        self.K_Width                       = K_Width
        self.MODULE_MIN                    = MODULE_MIN
        self.MODULE_MAX                    = MODULE_MAX
        self.NUM_PLANET_MIN                = NUM_PLANET_MIN
        self.NUM_PLANET_MAX                = NUM_PLANET_MAX
        self.NUM_TEETH_SUN_MIN             = NUM_TEETH_SUN_MIN
        self.NUM_TEETH_PLANET_MIN          = NUM_TEETH_PLANET_MIN
        self.GEAR_RATIO_MIN                = GEAR_RATIO_MIN
        self.GEAR_RATIO_MAX                = GEAR_RATIO_MAX
        self.GEAR_RATIO_STEP               = GEAR_RATIO_STEP

        self.Cost                         = 100000
        self.totalGearboxesWithRequiredGR = 0
        self.totalFeasibleGearboxes       = 0
        self.cntrBeforeCons               = 0
        self.iter                         = 0
        self.gearRatioIter                = self.GEAR_RATIO_MIN
        self.design_params = design_params
        self.gear_standard_parameters = gear_standard_paramaeters

        self.gearRatioReq = 0.0

    def printOptimizationParameters(self, Actuator=internalsingleStagePlanetaryActuator, log=1, csv=0):
        # Motor Parameters
        maxMotorAngVelRPM       = Actuator.motor.maxMotorAngVelRPM
        maxMotorAngVelRadPerSec = Actuator.motor.maxMotorAngVelRadPerSec
        maxMotorTorque          = Actuator.motor.maxMotorTorque
        maxMotorPower           = Actuator.motor.maxMotorPower
        motorMass               = Actuator.motor.massKG
        motorDia                = Actuator.motor.motor_OD
        motorLength             = Actuator.motor.motor_height

        # Planetary Gearbox Parameters
        maxGearAllowableStressMPa = Actuator.planetaryGearbox.maxGearAllowableStressMPa

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
            print("FOS:                     ", FOS)
            print("serviceFactor:           ", serviceFactor)
            print("stressAnalysisMethodName:", stressAnalysisMethodName)
            print("maxGearBoxDia:           ", maxGearBoxDia)
            print(" ")
            print("-----------------Optimization Parameters-----------------")
            print("K_Mass:               ", self.K_Mass)
            print("K_Eff:                ", self.K_Eff)
            print("K_Width:              ", self.K_Width)
            print("MODULE_MIN:           ", self.MODULE_MIN)
            print("MODULE_MAX:           ", self.MODULE_MAX)
            print("NUM_PLANET_MIN:       ", self.NUM_PLANET_MIN)
            print("NUM_PLANET_MAX:       ", self.NUM_PLANET_MAX)
            print("NUM_TEETH_SUN_MIN:    ", self.NUM_TEETH_SUN_MIN)
            print("NUM_TEETH_PLANET_MIN: ", self.NUM_TEETH_PLANET_MIN)
            print("GEAR_RATIO_MIN:       ", self.GEAR_RATIO_MIN)
            print("GEAR_RATIO_MAX:       ", self.GEAR_RATIO_MAX)
            print("GEAR_RATIO_STEP:      ", self.GEAR_RATIO_STEP)
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
            print("K_mass, K_Eff, K_Width, MODULE_MIN, MODULE_MAX, NUM_PLANET_MIN, NUM_PLANET_MAX, NUM_TEETH_SUN_MIN, NUM_TEETH_PLANET_MIN, GEAR_RATIO_MIN, GEAR_RATIO_MAX, GEAR_RATIO_STEP")
            print(self.K_Mass,",", self.K_Eff,",", self.K_Width,",", self.MODULE_MIN,",", self.MODULE_MAX,",", self.NUM_PLANET_MIN,",", self.NUM_PLANET_MAX,",", self.NUM_TEETH_SUN_MIN,",", self.NUM_TEETH_PLANET_MIN,",", self.GEAR_RATIO_MIN,",", self.GEAR_RATIO_MAX,",", self.GEAR_RATIO_STEP)

    def printOptimizationResults(self, Actuator=internalsingleStagePlanetaryActuator, log=1, csv=0):
        Actuator.setVariables()
        if log:
            # Printing the parameters below
            print("Iteration: ", self.iter)
            Actuator.printParametersLess()
            Actuator.printVolumeAndMassParameters()
            if self.UsePSCasVariable == 1 :
                Opt_PSC_ring = self.sspgOpt.model.PSCr.value
                Opt_PSC_planet = self.sspgOpt.model.PSCp.value
                Opt_PSC_sun = self.sspgOpt.model.PSCs.value
            else :
                Opt_PSC_ring   = 0
                Opt_PSC_planet = 0
                Opt_PSC_sun    = 0
            eff = round(Actuator.planetaryGearbox.getEfficiency(), 3)
            if self.UsePSCasVariable == 1 : 
                eff  = round(self.sspgOpt.getEfficiency(Var=False), 3)
                print ("Efficiency with PSC", eff)
                print(f"PSC Values - Ring: {Opt_PSC_ring}, Planet: {Opt_PSC_planet}, Sun: {Opt_PSC_sun}")
            print(" ")
            print("Cost:", self.Cost)
            print("*****************************************************************")
        elif csv:
            iter       = self.iter
            gearRatio  = Actuator.planetaryGearbox.gearRatio()
            module     = Actuator.planetaryGearbox.module
            Ns         = Actuator.planetaryGearbox.Ns 
            Np         = Actuator.planetaryGearbox.Np 
            Nr         = Actuator.planetaryGearbox.Nr 
            numPlanet  = Actuator.planetaryGearbox.numPlanet
            fwSunMM    = round(Actuator.planetaryGearbox.fwSunMM    , 3)
            fwPlanetMM = round(Actuator.planetaryGearbox.fwPlanetMM , 3)
            fwRingMM   = round(Actuator.planetaryGearbox.fwRingMM   , 3)
            if self.UsePSCasVariable == 1 :
                Opt_PSC_ring = self.sspgOpt.model.PSCr.value
                Opt_PSC_planet = self.sspgOpt.model.PSCp.value
                Opt_PSC_sun = self.sspgOpt.model.PSCs.value
                Opt_CD_SP, Opt_CD_PR = self.sspgOpt.getCenterDistance(Var=False)
            else :
                Opt_PSC_ring   = 0
                Opt_PSC_planet = 0
                Opt_PSC_sun    = 0
                # Opt_CD_SP, Opt_CD_PR = self.sspgOpt.getCenterDistance(Var=False)
                Opt_CD_SP = ((Ns + Np) / 2) * module
                Opt_CD_PR = ((Nr - Np) / 2) * module

            # mass     = round(Actuator.getMassStructureKG(), 3)
            # mass       = round(Actuator.getMassKG_3DP(), 3)
            mass       = round(Actuator.getMassKG_3DP(), 3)
            eff        = round(Actuator.planetaryGearbox.getEfficiency(), 3)
            
            # Update it is PSC are non-zero
            if self.UsePSCasVariable == 1 : 
                eff  = round(self.sspgOpt.getEfficiency(Var=False), 3)
            
            peakTorque = round(Actuator.motor.getMaxMotorTorque()*Actuator.planetaryGearbox.gearRatio(), 3)
            Cost       = self.cost(Actuator = Actuator) 
            Torque_Density = peakTorque / mass
            Outer_Bearing_mass = Actuator.output_bearing_mass
            Actuator_width = Actuator.actuator_width
            ## Don't delete the comment -- this is to verify if the Center distance and the PSC (should be all zero) are correct or not
            # print(iter,",", gearRatio,",",module,",", Ns,",", Np,",", Nr,",", numPlanet,",",  fwSunMM,",", fwPlanetMM,",", fwRingMM,",",Opt_PSC_sun,",", Opt_PSC_planet,",", Opt_PSC_ring,",", Opt_CD_SP, ",", Opt_CD_PR,",", mass,",", eff,",", peakTorque,",", Cost, ",", Torque_Density, ",", Outer_Bearing_mass, ",", Actuator_width)
            print(iter,",", gearRatio,",",module,",", Ns,",", Np,",", Nr,",", numPlanet,",",  fwSunMM,",", fwPlanetMM,",", fwRingMM,",", mass,",", eff,",", peakTorque,",", Cost, ",", Torque_Density, ",", Outer_Bearing_mass, ",", Actuator_width)

    def optimizeActuator(self, Actuator=internalsingleStagePlanetaryActuator, UsePSCasVariable = 1, log = 0, csv = 1, gearRatioReq = 0, printOptParams = 1):
        self.UsePSCasVariable = UsePSCasVariable
        totalTime = 0
        opt_parameters = None # [Gear Ratio, numPlanet, Ns, Np, Nr, Module]
        self.gearRatioReq = gearRatioReq
        if UsePSCasVariable == 0:
            totalTime, opt_parameters = self.optimizeActuatorWithoutPSC(Actuator=Actuator, log=log, csv=csv, printOptParams = printOptParams)
        elif UsePSCasVariable == 1:
            totalTime = self.optimizeActuatorWithPSC(Actuator=Actuator, log=log, csv=csv, printOptParams = printOptParams)
        else:
            totalTime = 0
            print("ERROR: \"UsePSCasVariable\" can be either 0 or 1")
        
        return totalTime, opt_parameters

    def optimizeActuatorWithoutPSC(self, Actuator=internalsingleStagePlanetaryActuator, log=1, csv=0, printOptParams = 1): 
        startTime = time.time()
        opt_parameters = None # [Gear Ratio, numPlanet, Ns, Np, Nr, Module]
        if csv and log:
            print("WARNING: Both csv and Log cannot be true")
            print("WARNING: Please set either csv or log to be 0 in \"Optimizer.optimizeActuator(Actuator)\" function")
            print(" ")
            print("ACTION: Making log to be false and csv to be true")
            log = 0
            csv = 1
        elif not csv and not log:
            print("WARNING: Both csv and Log cannot be false")
            print("WARNING: Please set either csv or log to be 1 in \"Optimizer.optimizeActuator(Actuator)\" function")
            print(" ")
            print("ACTION: Making log to be False and csv to be true")
            log = 0
            csv = 1

        if csv:
            fileName = f"./results/results_BruteForce_{Actuator.motor.motorName}/ISSPG_BRUTEFORCE_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}.csv"
        elif log:
            fileName = f"./results/results_BruteForce_{Actuator.motor.motorName}/ISSPG_BRUTEFORCE_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}.txt"
            
        with open(fileName, "w") as file1:
            sys.stdout = file1
            if (printOptParams):
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
                # print("iter, gearRatio, module, Ns, Np, Nr, numPlanet, fwSunMM, fwPlanetMM, fwRingMM, PSCs, PSCp, PSCr, CD_SP, CD_PR, mass, eff, peakTorque, Cost, Torque_Density, Outer_Bearing_mass, Actuator_width")
                print("iter, gearRatio, module, Ns, Np, Nr, numPlanet, fwSunMM, fwPlanetMM, fwRingMM, mass, eff, peakTorque, Cost, Torque_Density, Outer_Bearing_mass, Actuator_width")

            while self.gearRatioIter <= self.GEAR_RATIO_MAX:
                opt_done = 0
                self.iter = 0
                self.Cost = 100000
                MinCost = self.Cost
                Actuator.planetaryGearbox.setModule(self.MODULE_MIN)
                while Actuator.planetaryGearbox.module <= self.MODULE_MAX:
                    Actuator.planetaryGearbox.setNs(self.NUM_TEETH_SUN_MIN) # Setting Ns
                    while 2*Actuator.planetaryGearbox.getPCRadiusSunMM() <= Actuator.maxGearboxDiameter:
                        Actuator.planetaryGearbox.setNp(self.NUM_TEETH_PLANET_MIN) # Setting Np
                        while 2*Actuator.planetaryGearbox.getPCRadiusPlanetMM() <= Actuator.maxGearboxDiameter/2:
                            Actuator.planetaryGearbox.setNr(2*Actuator.planetaryGearbox.Np + Actuator.planetaryGearbox.Ns) # Implicitly setting Nr: Geometric Constraint satisfied
                            if 2*Actuator.planetaryGearbox.getPCRadiusRingMM() <= Actuator.maxGearboxDiameter:
                                Actuator.planetaryGearbox.setNumPlanet(self.NUM_PLANET_MIN) # Setting number of Planet
                                while Actuator.planetaryGearbox.numPlanet <= self.NUM_PLANET_MAX:
                                    self.cntrBeforeCons += 1
                
                                    if (Actuator.planetaryGearbox.geometricConstraint() and 
                                        Actuator.planetaryGearbox.meshingConstraint() and 
                                        Actuator.planetaryGearbox.noPlanetInterferenceConstraint() and
                                        Actuator.maxRingGearOD() and
                                        Actuator.SecCarrierODConstraint()
                                        ):

                                            self.totalFeasibleGearboxes += 1
                                            if ((Actuator.planetaryGearbox.gearRatio() >= self.gearRatioIter) and
                                                (Actuator.planetaryGearbox.gearRatio() <= self.gearRatioIter + self.GEAR_RATIO_STEP)):
                                                self.totalGearboxesWithRequiredGR += 1
                                                Actuator.updateFacewidth()

                                                self.Cost = self.cost(Actuator=Actuator)
                                                
                                                if self.Cost <= MinCost:
                                                    MinCost = self.Cost
                                                    self.iter+=1
                                                    opt_done = 1
                                                    round(self.gearRatioIter, 1)
                                                    
                                                    if (self.gearRatioReq == 0):
                                                        Actuator.genEquationFile(motor_name=Actuator.motor.motorName, gearRatioLL=round(self.gearRatioIter, 1), gearRatioUL = (round(self.gearRatioIter + self.GEAR_RATIO_STEP,1)))
                                                    else:
                                                        Actuator.genEquationFile_editCADdirectly()
                                                    
                                                    opt_parameters = [Actuator.planetaryGearbox.gearRatio(),
                                                                    Actuator.planetaryGearbox.numPlanet,
                                                                    Actuator.planetaryGearbox.Ns,
                                                                    Actuator.planetaryGearbox.Np,
                                                                    Actuator.planetaryGearbox.Nr,
                                                                    Actuator.planetaryGearbox.module]
                                                    
                                                    #if Actuator.planetaryGearbox.module == 0.5 :
                                                    #    print(opt_parameters)

                                                    opt_planetaryGearbox = internalsingleStagePlanetaryGearbox(design_params             = self.design_params,
                                                                                                               gear_standard_parameters  = self.gear_standard_parameters,
                                                                                                               Ns                        = Actuator.planetaryGearbox.Ns,
                                                                                                               Np                        = Actuator.planetaryGearbox.Np,
                                                                                                               Nr                        = Actuator.planetaryGearbox.Nr, 
                                                                                                               module                    = Actuator.planetaryGearbox.module,     # mm
                                                                                                               numPlanet                 = Actuator.planetaryGearbox.numPlanet,
                                                                                                               fwSunMM                   = Actuator.planetaryGearbox.fwSunMM,    # mm
                                                                                                               fwPlanetMM                = Actuator.planetaryGearbox.fwPlanetMM, # mm
                                                                                                               fwRingMM                  = Actuator.planetaryGearbox.fwRingMM,   # mm
                                                                                                               maxGearAllowableStressMPa = Actuator.planetaryGearbox.maxGearAllowableStressMPa, # 400 MPa
                                                                                                               densityGears              = Actuator.planetaryGearbox.densityGears,     # 7850 kg/m^3: Steel
                                                                                                               densityStructure          = Actuator.planetaryGearbox.densityStructure) # 2710 kg/m^3: Aluminum

                                                    opt_actuator = internalsingleStagePlanetaryActuator(design_params            = self.design_params,
                                                                                                        motor                    = Actuator.motor, 
                                                                                                        motor_driver_params      = Actuator.motor_driver_params, 
                                                                                                        planetaryGearbox         = opt_planetaryGearbox, 
                                                                                                        FOS                      = Actuator.FOS, 
                                                                                                        serviceFactor            = Actuator.serviceFactor,  
                                                                                                        stressAnalysisMethodName = "MIT") # Lewis or AGMA
                                                    
                                                    opt_actuator.updateFacewidth()
                                                    opt_actuator.getMassKG_3DP()
                                                    #opt_actuator.print_mass_of_parts_3DP()
                                                    #self.printOptimizationResults(Actuator, log, csv)
                                    Actuator.planetaryGearbox.setNumPlanet(Actuator.planetaryGearbox.numPlanet + 1)
                                #Actuator.planetaryGearbox.setNr(Actuator.planetaryGearbox.Ns + 1)
                            Actuator.planetaryGearbox.setNp(Actuator.planetaryGearbox.Np + 1)
                        Actuator.planetaryGearbox.setNs(Actuator.planetaryGearbox.Ns + 1)
                    Actuator.planetaryGearbox.setModule(Actuator.planetaryGearbox.module + 0.100)
                if (opt_done == 1):
                    self.printOptimizationResults(opt_actuator, log, csv)
                self.gearRatioIter += self.GEAR_RATIO_STEP

                if log:
                    print("Number of iterations: ", self.cntrBeforeCons)
                    print("Total Feasible Gearboxes:", self.totalFeasibleGearboxes)
                    print("Total Gearboxes with required Gear Ratio:", self.totalGearboxesWithRequiredGR)
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

    def optimizeActuatorWithPSC(self, Actuator=internalsingleStagePlanetaryActuator, log=1, csv=0, printOptParams = 1):
            startTime = time.time()
            opt_parameters = []
            if csv and log:
                print("WARNING: Both csv and Log cannot be true")
                print("WARNING: Please set either csv or log to be 0 in \"Optimizer.optimizeActuator(Actuator)\" function")
                print(" ")
                print("ACTION: Making log to be false and csv to be true")
                log = 0
                csv = 1
            elif not csv and not log:
                print("WARNING: Both csv and Log cannot be false")
                print("WARNING: Please set either csv or log to be 1 in \"Optimizer.optimizeActuator(Actuator)\" function")
                print(" ")
                print("ACTION: Making log to be False and csv to be true")
                log = 0
                csv = 1

            if csv:
                fileName = f"./results/results_bilevel_{Actuator.motor.motorName}/SSPG_BILEVEL_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}.csv"
            elif log:
                fileName = f"./results/results_bilevel_{Actuator.motor.motorName}/SSPG_BILEVEL_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}.txt"
            
            with open(fileName, "w") as file1:
                sys.stdout = file1
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
                    print("iter, gearRatio, module, Ns, Np, Nr, numPlanet, fwSunMM, fwPlanetMM, fwRingMM, PSCs, PSCp, PSCr, CD_SP, CD_PR, mass, eff, peakTorque, Cost, Torque_Density")
                
                while self.gearRatioIter <= self.GEAR_RATIO_MAX:
                    opt_done  = 0
                    self.iter = 0
                    self.Cost = 100000
                    MinCost   = self.Cost
                    Actuator.planetaryGearbox.setModule(self.MODULE_MIN)
                    while Actuator.planetaryGearbox.module <= self.MODULE_MAX:
                        Actuator.planetaryGearbox.setNs(self.NUM_TEETH_SUN_MIN) # Setting Ns
                        while 2*Actuator.planetaryGearbox.getPCRadiusSunMM() <= Actuator.maxGearboxDiameter:
                            Actuator.planetaryGearbox.setNp(self.NUM_TEETH_PLANET_MIN) # Setting Np
                            while 2*Actuator.planetaryGearbox.getPCRadiusPlanetMM() <= Actuator.maxGearboxDiameter/2:
                                Actuator.planetaryGearbox.setNr(2*Actuator.planetaryGearbox.Np + Actuator.planetaryGearbox.Ns) # Implicitly setting Nr: Geometric Constraint satisfied
                                if 2*Actuator.planetaryGearbox.getPCRadiusRingMM() <= Actuator.maxGearboxDiameter:
                                    Actuator.planetaryGearbox.setNumPlanet(self.NUM_PLANET_MIN) # Setting number of Planet
                                    while Actuator.planetaryGearbox.numPlanet <= self.NUM_PLANET_MAX:
                                        self.cntrBeforeCons += 1
                                        if (Actuator.planetaryGearbox.geometricConstraint() and 
                                            Actuator.planetaryGearbox.meshingConstraint() and 
                                            Actuator.planetaryGearbox.noPlanetInterferenceConstraint()):

                                            self.totalFeasibleGearboxes += 1
                                            if (Actuator.planetaryGearbox.gearRatio() >= self.gearRatioIter):
                                            # if ((Actuator.planetaryGearbox.gearRatio() >= self.gearRatioIter) and 
                                                # (Actuator.planetaryGearbox.gearRatio() <= self.gearRatioIter + self.GEAR_RATIO_STEP)):
                                                self.totalGearboxesWithRequiredGR += 1
                                                Actuator.updateFacewidth()

                                                effActuator = Actuator.planetaryGearbox.getEfficiency()
                                                # massActuator = Actuator.getMassKG_3DP()
                                                massActuator = Actuator.getMassKG_3DP()

                                                self.Cost = (self.K_Mass * massActuator) + (self.K_Eff * effActuator)
                                                if self.Cost <= MinCost:
                                                    MinCost    = self.Cost
                                                    self.iter += 1
                                                    opt_done   = 1
                                                    Actuator.genEquationFile_editCADdirectly()
                                                    opt_parameters = [Actuator.planetaryGearbox.gearRatio(),
                                                                      Actuator.planetaryGearbox.numPlanet,
                                                                      Actuator.planetaryGearbox.Ns,
                                                                      Actuator.planetaryGearbox.Np,
                                                                      Actuator.planetaryGearbox.Nr,
                                                                      Actuator.planetaryGearbox.module]
                                                    opt_planetaryGearbox = internalsingleStagePlanetaryGearbox(design_params             = self.design_params,
                                                                                                                gear_standard_parameters  = self.gear_standard_parameters,
                                                                                                                Ns                        = Actuator.planetaryGearbox.Ns,
                                                                                                                Np                        = Actuator.planetaryGearbox.Np,
                                                                                                                Nr                        = Actuator.planetaryGearbox.Nr, 
                                                                                                                module                    = Actuator.planetaryGearbox.module,     # mm
                                                                                                                numPlanet                 = Actuator.planetaryGearbox.numPlanet,
                                                                                                                fwSunMM                   = Actuator.planetaryGearbox.fwSunMM,    # mm
                                                                                                                fwPlanetMM                = Actuator.planetaryGearbox.fwPlanetMM, # mm
                                                                                                                fwRingMM                  = Actuator.planetaryGearbox.fwRingMM,   # mm
                                                                                                                maxGearAllowableStressMPa = Actuator.planetaryGearbox.maxGearAllowableStressMPa, # 400 MPa
                                                                                                                densityGears              = Actuator.planetaryGearbox.densityGears,     # 7850 kg/m^3: Steel
                                                                                                                densityStructure          = Actuator.planetaryGearbox.densityStructure) # 2710 kg/m^3: Aluminum

                                                    opt_actuator = internalsingleStagePlanetaryActuator(design_params            = self.design_params,
                                                                                                        motor                    = Actuator.motor, 
                                                                                                        motor_driver_params      = Actuator.motor_driver_params,
                                                                                                        planetaryGearbox         = opt_planetaryGearbox, 
                                                                                                        FOS                      = Actuator.FOS, 
                                                                                                        serviceFactor            = Actuator.serviceFactor, 
                                                                                                        stressAnalysisMethodName = "MIT") # Lewis or AGMA
                                        Actuator.planetaryGearbox.setNumPlanet(Actuator.planetaryGearbox.numPlanet + 1)
                                    #Actuator.planetaryGearbox.setNr(Actuator.planetaryGearbox.Ns + 1)
                                Actuator.planetaryGearbox.setNp(Actuator.planetaryGearbox.Np + 1)
                            Actuator.planetaryGearbox.setNs(Actuator.planetaryGearbox.Ns + 1)
                        Actuator.planetaryGearbox.setModule(Actuator.planetaryGearbox.module + 0.100)
                    if (opt_done == 1):
                        self.sspgOpt = optimal_continuous_PSC_sspg(GEAR_RATIO_MIN = opt_parameters[0],
                                                                   numPlanet = opt_parameters[1],
                                                                   Ns = opt_parameters[2],
                                                                   Np = opt_parameters[3],
                                                                   Nr = opt_parameters[4],
                                                                   M  = opt_parameters[5] * 10) # we are sending the module times 10 value
                        _, calc_centerDistForManufacturing = self.sspgOpt.solve()
                        self.sspgOpt.solve(optimizeForManufacturing   = True, 
                                           centerDistForManufacturing = calc_centerDistForManufacturing)
                        self.printOptimizationResults(opt_actuator, log, csv)
                    self.gearRatioIter += self.GEAR_RATIO_STEP

                    if log:
                        print("Number of iterations: ", self.cntrBeforeCons)
                        print("Total Feasible Gearboxes:", self.totalFeasibleGearboxes)
                        print("Total Gearboxes with required Gear Ratio:", self.totalGearboxesWithRequiredGR)
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
            return totalTime

    def cost(self, Actuator=internalsingleStagePlanetaryActuator):
        K_gearRatio = 0
        if self.gearRatioReq != 0:
            K_gearRatio = 10
        
        gearRatio_err = np.sqrt((Actuator.planetaryGearbox.gearRatio() - self.gearRatioReq)**2)

        mass = Actuator.getMassKG_3DP()
        eff = Actuator.planetaryGearbox.getEfficiency()
        width = Actuator.planetaryGearbox.fwPlanetMM
        cost = (self.K_Mass    * mass 
                + self.K_Eff   * eff 
                + self.K_Width * width 
                + K_gearRatio  * gearRatio_err)
        return cost

# ═══════════════════════════════════════════════════════════════════
#   STEP 1 — Read fixed values from ISSPG_fixed.txt
#   Format per line: "name"= value
# ═══════════════════════════════════════════════════════════════════

