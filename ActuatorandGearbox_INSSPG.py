import numpy as np
import os
import sys
import time
import math

from CommonComponents import material, bearings_discrete, nuts_and_bolts_dimensions, motor_frameless_inrunner_mahi as motor

class singleStagePlanetaryGearbox:
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
                 densityGears              = 7850.0,
                 densityStructure          = 2710.0
                 ):
        
        self.Ns        = Ns
        self.Np        = Np
        self.Nr        = Nr
        self.numPlanet = numPlanet
        self.module    = module

        self.maxGearAllowableStressMPa = maxGearAllowableStressMPa
        self.maxGearAllowableStressPa  = maxGearAllowableStressMPa * 10**6
        self.densityGears              = densityGears
        self.densityStructure          = densityStructure
        self.bhnSun                    = 270 
        self.bhnPlanet                 = 270 
        self.bhnRing                   = 270 
        self.enduranceStressSunMPa     = 2.75*self.bhnSun - 69    
        self.enduranceStressPlanetMPa  = 2.75*self.bhnPlanet - 69 
        self.enduranceStressRingMPa    = 2.75*self.bhnRing - 69   
        self.youngsModulusSun          = 2.05 * 10**5 
        self.youngsModulusPlanet       = 2.05 * 10**5 
        self.youngsModulusRing         = 2.05 * 10**5 
        self.equivYoungsModulusSP      = (2.0 * self.youngsModulusSun * self.youngsModulusPlanet) / (self.youngsModulusSun + self.youngsModulusPlanet)
        self.equivYoungsModulusPR      = (2.0 * self.youngsModulusPlanet * self.youngsModulusRing) / (self.youngsModulusPlanet + self.youngsModulusRing)

        self.fwSunMM    = fwSunMM
        self.fwRingMM   = fwRingMM
        self.fwPlanetMM = fwPlanetMM

        self.fwSunM     = fwSunMM / 1000.0
        self.fwRingM    = fwRingMM / 1000.0
        self.fwPlanetM  = fwPlanetMM / 1000.0

        self.mu            = gear_standard_parameters["coefficientOfFriction"] 
        self.pressureAngle = gear_standard_parameters["pressureAngleDEG"]      

        self.ringRadialWidthMM   = design_params.get("ringRadialWidthMM", 4.0)          
        self.ringRadialWidthM    = self.ringRadialWidthMM / 1000.0 
        self.planetMinDistanceMM = design_params.get("planetMinDistanceMM", 5.0)        
        
        self.sCarrierExtrusionDiaMM       =  design_params.get("sCarrierExtrusionDiaMM", 8.0)       
        self.sCarrierExtrusionClearanceMM =  design_params.get("sCarrierExtrusionClearanceMM", 1.0) 
    
    def geometricConstraint(self):
        return (self.Ns + 2*self.Np == self.Nr) 
    
    def meshingConstraint(self):
        return ((self.Ns + self.Nr) % self.numPlanet == 0)

    def noPlanetInterferenceConstraint_old(self):
        return 2*(self.Ns + self.Np)*self.module*np.sin(np.pi/self.numPlanet) >= 2*self.module*self.Np + self.planetMinDistanceMM

    def noPlanetInterferenceConstraint(self):
        Rs                        = (self.module) * self.Ns / 2
        Rp                        = (self.module) * self.Np / 2 
        numPlanet                 = self.numPlanet
        sCarrierExtrusionRadiusMM = self.sCarrierExtrusionDiaMM * 0.5
        return 2 * (Rs + Rp) * np.sin(np.pi/(2*numPlanet)) - Rp - sCarrierExtrusionRadiusMM >= self.sCarrierExtrusionClearanceMM * 2

    def gearRatio(self):
        return (self.Nr + self.Ns) / self.Ns

    def inverse_involute(self,inv_alpha):
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

    def quadratic_min(self, a, b, k=0.01):
        return (a + b - np.sqrt((a - b)**2 + k**2)) / 2
    
    def getPressureAngleRad(self):
        return self.pressureAngle * np.pi / 180  

    def getWorkingPressureAngle(self):
        module = self.module  
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr
        xs     = 0.0 
        xp     = 0.0 
        xr     = 0.0 
        
        alpha = self.getPressureAngleRad()

        inv_alpha_w_sunPlanet = 2*np.tan(alpha)*((xs + xp)/(Ns + Np)) + self.involute(alpha)
        alpha_w_sunPlanet = self.inverse_involute(inv_alpha_w_sunPlanet)

        inv_alpha_w_planetRing = 2*np.tan(alpha)*((xr-xp)/(Nr - Np)) + self.involute(alpha)
        alpha_w_planetRing = self.inverse_involute(inv_alpha_w_planetRing)

        return alpha_w_sunPlanet, alpha_w_planetRing

    def getCenterDistModificationCoeff(self):
        module = self.module  
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr
        xs     = 0.0 
        xp     = 0.0 
        xr     = 0.0 
        
        alpha = self.getPressureAngleRad()  
        alpha_w_sunPlanet, alpha_w_planetRing = self.getWorkingPressureAngle()

        y_sunPlanet  = ((Ns + Np) / 2) * ((np.cos(alpha) / np.cos(alpha_w_sunPlanet)) - 1)
        y_planetRing = ((Nr - Np) / 2) * ((np.cos(alpha) / np.cos(alpha_w_planetRing)) - 1)

        return y_sunPlanet, y_planetRing

    def getCenterDistance(self):
        module = self.module  
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr
        xs     = 0.0 
        xp     = 0.0 
        xr     = 0.0 

        y_sunPlanet, y_planetRing = self.getCenterDistModificationCoeff()

        centerDist_sunPlanet = ((Ns + Np)/2  + y_sunPlanet)* module
        centerDist_planetRing = ((Nr - Np)/2  + y_planetRing)* module

        return centerDist_sunPlanet, centerDist_planetRing

    def getBaseDia(self):
        module = self.module  
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr
        xs     = 0.0 
        xp     = 0.0 
        xr     = 0.0 

        alpha = self.getPressureAngleRad() 

        D_sun    = module * Ns 
        D_planet = module * Np 
        D_ring   = module * Nr 

        D_b_sun    = D_sun * np.cos(alpha)
        D_b_planet = D_planet * np.cos(alpha)
        D_b_ring   = D_ring * np.cos(alpha)

        return D_b_sun, D_b_planet, D_b_ring

    def getTipCircleDia(self):
        module = self.module  
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr
        xs     = 0.0 
        xp     = 0.0 
        xr     = 0.0 

        alpha     = self.getPressureAngleRad() 
        D_sun     = module * Ns 
        D_planet  = module * Np 
        D_ring    = module * Nr 

        y_sunPlanet, y_planetRing = self.getCenterDistModificationCoeff()

        D_a_sun    = D_sun     + 2 * module * (1 + y_sunPlanet - xp)
        D_a_planet = D_planet + 2 * module * (1 + self.quadratic_min((y_sunPlanet - xs), xp))  
        D_a_ring   = D_ring    - 2 * module * (1 - xr)
        
        return D_a_sun, D_a_planet, D_a_ring

    def getTipPressureAngle(self):
        module = self.module  
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr
        xs     = 0.0 
        xp     = 0.0 
        xr     = 0.0 

        alpha = self.getPressureAngleRad() 
        D_b_sun, D_b_planet, D_b_ring = self.getBaseDia() 
        D_a_sun, D_a_planet, D_a_ring = self.getTipCircleDia() 

        alpha_a_sun    = np.arccos(D_b_sun / D_a_sun)
        alpha_a_planet = np.arccos(D_b_planet/D_a_planet)
        alpha_a_ring   = np.arccos(D_b_ring / D_a_ring)

        return alpha_a_sun, alpha_a_planet, alpha_a_ring

    def getErrorTipCircleDia_planet(self):
        module = self.module  
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr
        xs     = 0.0 
        xp     = 0.0 
        xr     = 0.0 

        y_sunPlanet, _ = self.getCenterDistModificationCoeff()
        _, D_a_planet_1, _ = self.getTipCircleDia()
        D_a_planet_2 = module * Np + 2*module*(1 + np.minimum((y_sunPlanet - xs),xp)) 

        return np.abs(D_a_planet_1 - D_a_planet_2)
    
    def contactRatio_sunPlanet(self):
        module = self.module  
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr
        xs     = 0.0 
        xp     = 0.0 
        xr     = 0.0 

        alpha_w_sunPlanet, _ = self.getWorkingPressureAngle()
        alpha_a_sun, alpha_a_planet, _ = self.getTipPressureAngle()

        Approach_CR_sunPlanet = (Np / (2 * np.pi)) * (np.tan(alpha_a_planet) - np.tan(alpha_w_sunPlanet)) 
        Recess_CR_sunPlanet   = (Ns / (2 * np.pi)) * (np.tan(alpha_a_sun) - np.tan(alpha_w_sunPlanet))    

        CR_sunPlanet = Approach_CR_sunPlanet + Recess_CR_sunPlanet
        return Approach_CR_sunPlanet, Recess_CR_sunPlanet, CR_sunPlanet

    def contactRatio_planetRing(self):
        module = self.module  
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr
        xs     = 0.0 
        xp     = 0.0 
        xr     = 0.0 

        _, alpha_w_planetRing = self.getWorkingPressureAngle()
        _, alpha_a_planet, alpha_a_ring = self.getTipPressureAngle()

        Approach_CR_planetRing = -(Nr / (2 * np.pi)) * (np.tan(alpha_a_ring) - np.tan(alpha_w_planetRing)) 
        Recess_CR_planetRing   =  Np / (2 * np.pi) * (np.tan(alpha_a_planet) - np.tan(alpha_w_planetRing)) 
        
        CR_planetRing = Approach_CR_planetRing + Recess_CR_planetRing
        return Approach_CR_planetRing, Recess_CR_planetRing, CR_planetRing

    def getEfficiency(self):
        module = self.module  
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr
        xs     = 0.0 
        xp     = 0.0 
        xr     = 0.0 

        eps_sunPlanetA, eps_sunPlanetR, _ = self.contactRatio_sunPlanet()
        eps_planetRingA, eps_planetRingR, _ = self.contactRatio_planetRing()
        
        epsilon_sunPlanet = eps_sunPlanetA**2 + eps_sunPlanetR**2 - eps_sunPlanetA - eps_sunPlanetR + 1 
        epsilon_planetRing = eps_planetRingA**2 + eps_planetRingR**2 - eps_planetRingA - eps_planetRingR + 1 
        
        eff_SP = 1 - self.mu * np.pi * ((1 / Np) + (1 / Ns)) * epsilon_sunPlanet
        eff_PR = 1 - self.mu * np.pi * ((1 / Np) - (1 / Nr)) * epsilon_planetRing

        Eff = (1 + eff_SP * eff_PR * (Nr / Ns)) / (1 + (Nr / Ns))
        return Eff

    def getPCRadiusSunMM(self):    return (self.Ns * self.module / 2)
    def getPCRadiusPlanetMM(self): return (self.Np * self.module / 2)
    def getPCRadiusRingMM(self):   return (self.Nr * self.module / 2)
    def getOuterRadiusRingMM(self):return ((self.Nr * self.module / 2) + self.ringRadialWidthMM)
    def getCarrierRadiusMM(self):  return (((self.Ns + self.Np + self.Np/2)/2)*self.module)
    
    def getPCRadiusSunM(self):     return ((self.Ns * self.module / 2)/1000.0)
    def getPCRadiusPlanetM(self):  return ((self.Np * self.module / 2)/1000.0)
    def getPCRadiusRingM(self):    return ((self.Nr * self.module / 2)/1000.0)
    def getOuterRadiusRingM(self): return (((self.Nr * self.module / 2)/1000.0) + self.ringRadialWidthM)
    def getCarrierRadiusM(self):   return (((self.Ns + self.Np + self.Np/2)/2)*self.module/1000.0)

    def setfwSunMM(self, fwSunMM):
        self.fwSunMM = fwSunMM
        self.fwSunM = fwSunMM / 1000.0

    def setfwPlanetMM(self, fwPlanetMM):
        self.fwPlanetMM = fwPlanetMM
        self.fwPlanetM = fwPlanetMM / 1000.0

    def setfwRingMM(self, fwRingMM):
        self.fwRingMM = fwRingMM
        self.fwRingM = fwRingMM / 1000.0

    def setNs(self, Ns): self.Ns = Ns
    def setNp(self, Np): self.Np = Np
    def setNr(self, Nr): self.Nr = Nr
    def setModule(self, module): self.module = module
    def setNumPlanet(self, numPlanet): self.numPlanet = numPlanet


#=========================================================================
# Actuator classes
#=========================================================================
#-------------------------------------------------------------------------
# Single Stage Actuator class (INSSPG)
#-------------------------------------------------------------------------
class singleStagePlanetaryActuator:
    def __init__(self, 
                 design_params,
                 motor_driver_params      = None,
                 motor                    = None, 
                 planetaryGearbox         = singleStagePlanetaryGearbox,
                 FOS                      = 2.0,
                 serviceFactor            = 2.0,
                 maxGearboxDiameter       = 140.0,
                 stressAnalysisMethodName = "Lewis",
                 insspg_type              = "insspg_type_1"):   
        
        self.insspg_type = insspg_type                          
        
        self.motor              = motor
        self.planetaryGearbox   = planetaryGearbox
        self.FOS                = FOS
        self.serviceFactor      = serviceFactor
        self.maxGearboxDiameter = maxGearboxDiameter 
        self.stressAnalysisMethodName = stressAnalysisMethodName

        #============================================
        # Motor Parameters
        #============================================
        self.motorLengthMM           = self.motor.getLengthMM()
        self.motorDiaMM              = self.motor.getDiaMM()
        self.motorMassKG             = self.motor.getMassKG()
        self.MaxMotorTorque          = self.motor.maxMotorTorque         
        self.MaxMotorAngVelRPM       = self.motor.maxMotorAngVelRPM      
        self.MaxMotorAngVelRadPerSec = self.motor.maxMotorAngVelRadPerSec 

        self.design_params       = design_params
        self.motor_driver_params = motor_driver_params
        self.ringRadialWidthMM   = self.design_params.get("ringRadialWidthMM", self.planetaryGearbox.ringRadialWidthMM)

        # --- Pre-Cache Static Bolt Dimensions (Speed Optimization) ---
        planet_pin_bolt = nuts_and_bolts_dimensions(bolt_dia=self.design_params.get("planet_pin_bolt_dia", 5), bolt_type="socket_head")
        self.planet_pin_socket_head_dia  = planet_pin_bolt.bolt_head_dia
        self.planet_pin_bolt_wrench_size = planet_pin_bolt.nut_width_across_flats

        sun_central_bolt = nuts_and_bolts_dimensions(bolt_dia=self.design_params.get("sun_central_bolt_dia", 5), bolt_type="socket_head")
        self.sun_central_bolt_socket_head_dia = sun_central_bolt.bolt_head_dia

        carrier_trap_hole = nuts_and_bolts_dimensions(bolt_dia=self.design_params.get("carrier_trapezoidal_support_hole_dia", 3), bolt_type="socket_head")
        self.carrier_trapezoidal_support_hole_socket_head_dia = carrier_trap_hole.bolt_head_dia
        self.carrier_trapezoidal_support_hole_wrench_size     = carrier_trap_hole.nut_width_across_flats
        
        case_mounting_hole_bolt = nuts_and_bolts_dimensions(bolt_dia=self.design_params.get("case_mounting_hole_dia", 4), bolt_type="socket_head")
        self.case_mounting_hole_allen_socket_dia = case_mounting_hole_bolt.bolt_head_dia
        self.case_mounting_wrench_size           = case_mounting_hole_bolt.nut_width_across_flats

        output_mounting_hole_bolt = nuts_and_bolts_dimensions(bolt_dia=self.design_params.get("output_mounting_hole_dia", 5), bolt_type="socket_head")
        self.output_mounting_nut_thickness   = output_mounting_hole_bolt.nut_thickness         
        self.output_mounting_nut_wrench_size = output_mounting_hole_bolt.nut_width_across_flats

        #---------------- Setting all design variables ---------------
        self.setVariables()
    
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
        self.Ns         = self.planetaryGearbox.Ns
        self.Np         = self.planetaryGearbox.Np
        self.Nr         = self.Ns + 2 * self.Np
        self.module     = self.planetaryGearbox.module
        self.num_planet = self.planetaryGearbox.numPlanet

        #------------------------------------------------------
        # Independent Constant variables
        #------------------------------------------------------
        self.pressure_angle     = self.planetaryGearbox.getPressureAngleRad()
        self.pressure_angle_deg = self.planetaryGearbox.getPressureAngleRad() * 180 / np.pi
        
        # --- Clearances & Tolerances ---
        self.clearance_planet                   = self.design_params.get("clearance_planet", 1.5)
        self.standard_clearance_1_5mm           = self.design_params.get("standard_clearance_1_5mm", 1.5)
        self.standard_fillet_1_5mm              = self.design_params.get("standard_fillet_1_5mm", 1.5)
        self.standard_bearing_insertion_chamfer = self.design_params.get("standard_bearing_insertion_chamfer", 0.5)
        self.tight_clearance_3DP                = self.design_params.get("tight_clearance_3DP", 0.4)
        self.loose_clearance_3DP                = self.design_params.get("loose_clearance_3DP", 0.8)
        self.Rotor_tight_clearance              = self.design_params.get("Rotor_tight_clearance", 0.04)

        # --- Dynamic Bearing Lookup ---
        self.bearingIDClearanceMM = self.design_params.get("bearingIDClearanceMM", 10)
        IdrequiredMM              = (self.module * (self.Ns + self.Np)) + self.planet_pin_socket_head_dia + (self.loose_clearance_3DP * 2)
        Bearings                  = bearings_discrete(IdrequiredMM)
        
        self.bearing_ID           = Bearings.getBearingIDMM()
        self.bearing_OD           = Bearings.getBearingODMM()
        self.bearing_height       = Bearings.getBearingWidthMM()
        self.bearing_mass         = Bearings.getBearingMassKG()

        # --- Inrunner Motor: Rotor & Stator ---
        self.motor_OD      = self.motorDiaMM
        self.motor_height  = self.motorLengthMM
        self.Rotor_ID      = self.design_params.get("Rotor_ID", 45)
        self.Rotor_OD      = self.design_params.get("Rotor_OD", 55.6)
        self.Rotor_height  = self.design_params.get("Rotor_height", 15)
        self.Stator_ID     = self.design_params.get("Stator_ID", 57)
        self.Stator_OD     = self.design_params.get("Stator_OD", 104)
        self.stator_height = self.design_params.get("stator_height", 24.5)
        
        self.rotor_mount_hole_dia            = self.design_params.get("rotor_mount_hole_dia", 4)
        self.rotor_mount_hole_CSK_OD         = self.design_params.get("rotor_mount_hole_CSK_OD", 8)
        self.rotor_mount_hole_CSK_head_hight = self.design_params.get("rotor_mount_hole_CSK_head_hight", 2)

        # --- Type 1 Rotor Support Bearings ---
        self.rotor_support_bearing_ID           = self.design_params.get("rotor_support_bearing_ID", 30)
        self.rotor_support_bearing_OD           = self.design_params.get("rotor_support_bearing_OD", 42)
        self.rotor_support_bearing_height       = self.design_params.get("rotor_support_bearing_height", 7)
        self.rotor_upper_support_bearing_ID     = self.design_params.get("rotor_upper_support_bearing_ID", 40)
        self.rotor_upper_support_bearing_OD     = self.design_params.get("rotor_upper_support_bearing_OD", 50)
        self.rotor_upper_support_bearing_height = self.design_params.get("rotor_upper_support_bearing_height", 6)

        # --- Type 2 Sun Bearings ---
        self.sun_bottom_casing_bearing_OD     = self.design_params.get("sun_bottom_casing_bearing_OD", 24)
        self.sun_bottom_casing_bearing_ID     = self.design_params.get("sun_bottom_casing_bearing_ID", 15)
        self.sun_bottom_casing_bearing_height = self.design_params.get("sun_bottom_casing_bearing_height", 5)
        self.sun_sec_carrier_bearing_ID       = self.design_params.get("sun_sec_carrier_bearing_ID", 25)
        self.sun_sec_carrier_bearing_OD       = self.design_params.get("sun_sec_carrier_bearing_OD", 32)
        self.sun_sec_carrier_bearing_height   = self.design_params.get("sun_sec_carrier_bearing_height", 4)

        # --- Stator Casings ---
        self.stator_casing_thickness                 = self.design_params.get("stator_casing_thickness", 3.5)
        self.stator_bottom_step_height_              = self.design_params.get("stator_bottom_step_height_", 4.5)
        self.stator_upper_step_height                = self.design_params.get("stator_upper_step_height", 7)
        self.stator_side_step_OD                     = self.design_params.get("stator_side_step_OD", 101)
        self.stator_mounting_holes_dia               = self.design_params.get("stator_mounting_holes_dia", 3)
        self.stator_hole_bolt_socket_head_dia        = self.design_params.get("stator_hole_bolt_socket_head_dia", 5.5)
        self.stator_bearing_support_casing_thickness = self.design_params.get("stator_bearing_support_casing_thickness", 2.5)

        self.stator_casing_hole_dia                  = self.design_params.get("stator_casing_hole_dia", 4)
        self.stator_casing_hole_socket_head_dia      = self.design_params.get("stator_casing_hole_socket_head_dia", 7.25)

        # --- Case Mounting & Output Dimensions ---
        self.case_mounting_hole_dia              = self.design_params.get("case_mounting_hole_dia", 4)
        self.case_mounting_wrench_thickness      = self.design_params.get("case_mounting_wrench_thickness", 3)
        self.case_mounting_hole_allen_socket_dia = self.design_params.get("case_mounting_hole_allen_socket_dia", 5.5)
        self.case_mounting_bolt_depth            = self.design_params.get("case_mounting_bolt_depth", 4.5)
        self.case_mounting_wrench_size           = self.design_params.get("case_mounting_wrench_size", 7)

        self.rotor_output_hole_PCD           = self.design_params.get("rotor_output_hole_PCD", 29)
        self.Rotor_output_hole_num           = self.design_params.get("Rotor_output_hole_num", 4)
        self.output_mounting_nut_thickness   = self.design_params.get("output_mounting_nut_thickness", 3.8)
        self.output_mounting_nut_wrench_size = self.design_params.get("output_mounting_nut_wrench_size", 7.8)
        self.output_mounting_hole_dia        = self.design_params.get("output_mounting_hole_dia", 5)

        # --- Base Gearbox Components ---
        self.sec_carrier_thickness             = self.design_params.get("sec_carrier_thickness", 5)
        self.sun_coupler_hub_thickness         = self.design_params.get("sun_coupler_hub_thickness", 4)
        self.clearance_sun_coupler_sec_carrier = self.design_params.get("clearance_sun_coupler_sec_carrier", 1.5)
        
        # --- Planet Parameters ---
        self.planet_bore              = self.design_params.get("planet_bore", 10)
        self.planet_pin_bolt_dia      = self.design_params.get("planet_pin_bolt_dia", 5)
        self.planet_pin_socket_head_dia= self.design_params.get("planet_pin_socket_head_dia", 8.5)
        self.planet_shaft_dia         = self.design_params.get("planet_shaft_dia", 8)
        self.planet_pin_bolt_wrench_size = self.design_params.get("planet_pin_bolt_wrench_size", 8)
        self.planet_shaft_step_offset = self.design_params.get("planet_shaft_step_offset", 1)
        self.planet_bearing_OD        = self.design_params.get("planet_bearing_OD", 12)
        self.planet_bearing_width     = self.design_params.get("planet_bearing_width", 3.5)
        self.bearing_retainer_thickness = self.design_params.get("bearing_retainer_thickness", 2)

        # --- Carrier Trapezoidal Dimensions ---
        self.carrier_trapezoidal_support_sun_offset                 = self.design_params.get("carrier_trapezoidal_support_sun_offset", 5)
        self.carrier_trapezoidal_support_hole_PCD_offset_bearing_ID = self.design_params.get("carrier_trapezoidal_support_hole_PCD_offset_bearing_ID", 4)
        self.carrier_trapezoidal_support_hole_dia                   = self.design_params.get("carrier_trapezoidal_support_hole_dia", 3)
        self.carrier_trapezoidal_support_hole_socket_head_dia       = self.design_params.get("carrier_trapezoidal_support_hole_socket_head_dia", 5.5)
        self.carrier_trapezoidal_support_hole_wrench_size           = self.design_params.get("carrier_trapezoidal_support_hole_wrench_size", 5.5)
        self.carrier_bearing_step_width                             = self.design_params.get("carrier_bearing_step_width", 1.5)

        # --- Sun & Main Bearings ---
        self.sun_hub_dia              = self.design_params.get("sun_hub_dia", 37)
        self.sun_central_bolt_dia     = self.design_params.get("sun_central_bolt_dia", 5)
        self.sun_central_bolt_socket_head_dia = self.design_params.get("sun_central_bolt_socket_head_dia", 8.5)
        self.sun_shaft_bearing_ID     = self.design_params.get("sun_shaft_bearing_ID", 8)
        self.sun_shaft_bearing_OD     = self.design_params.get("sun_shaft_bearing_OD", 16)
        self.sun_shaft_bearing_width  = self.design_params.get("sun_shaft_bearing_width", 5)

        ##-------bearing mount thickness ------ ##
        self.bearing_mount_thickness = self.design_params.get("bearing_mount_thickness",2)

        #------------------------------------------------------
        # Dependent gear variables
        #------------------------------------------------------
        self.h_a          = 1 * self.module
        self.h_b          = 1.25 * self.module
        self.h_f          = 1.25 * self.module
        self.clr_tip_root = self.h_f - self.h_a

        self.dp_s      = self.module * self.Ns
        self.db_s      = self.dp_s * np.cos(self.pressure_angle)
        self.fw_s_calc = self.planetaryGearbox.fwSunMM
        self.alpha_s   = (np.sqrt(self.dp_s**2 - self.db_s**2) / self.db_s) * 180 / np.pi - self.pressure_angle_deg 
        self.beta_s    = (360 / (4 * self.Ns) - self.alpha_s) * 2

        self.dp_p    = self.module * self.Np
        self.db_p    = self.dp_p * np.cos(self.pressure_angle)
        self.fw_p    = self.planetaryGearbox.fwPlanetMM
        self.alpha_p = (np.sqrt(self.dp_p**2 - self.db_p**2) / self.db_p) * 180 / np.pi - self.pressure_angle_deg 
        self.beta_p  = (360 / (4 * self.Np) - self.alpha_p) * 2

        self.dp_r    = self.module * self.Nr
        self.db_r    = self.dp_r * np.cos(self.pressure_angle)
        self.fw_r    = self.planetaryGearbox.fwRingMM
        self.alpha_r = (np.sqrt(self.dp_r**2 - self.db_r**2) / self.db_r) * 180 / np.pi - self.pressure_angle_deg 
        self.beta_r  = (360 / (4 * self.Nr) + self.alpha_r) * 2

        # ------------------------------------------------------------------------------------
        # EXPLICIT USER CONSTRAINTS (Mathematically Locked)
        # ------------------------------------------------------------------------------------
        self.carrier_PCD = self.module * (self.Ns + self.Np)

        # --- NEW SUN SUPPORT OD ---
        calculated_sun_support = self.carrier_PCD - (self.planet_shaft_dia + self.planet_shaft_step_offset * 2) - self.standard_clearance_1_5mm * 3
        self.sun_support_OD = min(calculated_sun_support, 21)
        # --------------------------
        
        if self.insspg_type == "insspg_type_2":
                # --- TYPE 2 MATH ---
                self.fw_s_used = (self.Rotor_height 
                                - 2 
                                - self.sun_coupler_hub_thickness 
                                + self.loose_clearance_3DP 
                                + self.sec_carrier_thickness 
                                + self.fw_p 
                                + self.standard_clearance_1_5mm)
        else:
                # --- TYPE 1 MATH (Original) ---
                self.fw_s_used = (self.standard_clearance_1_5mm 
                                + self.stator_height 
                                - self.Rotor_height 
                                - self.stator_bottom_step_height_  
                                + self.stator_bearing_support_casing_thickness 
                                + self.loose_clearance_3DP*2 
                                + self.sec_carrier_thickness 
                                + self.standard_clearance_1_5mm 
                                + self.clearance_planet 
                                + self.fw_p 
                                - self.sun_coupler_hub_thickness 
                                - self.standard_clearance_1_5mm)
                # ------------------------------------------------------------------------------------

        # Speed Optimization Caching
        self.bearing_mass_base = bearings_discrete(self.bearing_ID).getBearingMassKG()

    def _equation_lines(self):
        # EXACT MATCH TO USER'S CSV LIST ORDER
        return [
            f'"Ns"= {self.Ns}\n',
            f'"Np"= {self.Np}\n',
            f'"Nr"= {self.Nr}\n',
            f'"module"= {self.module}\n',
            f'"num_planet"= {self.num_planet}\n',
            f'"pressure_angle"= {self.pressure_angle_deg}\n',
            f'"h_a"= {self.h_a}\n',
            f'"h_b"= {self.h_b}\n',
            f'"clr_tip_root"= {self.clr_tip_root}\n',
            f'"h_f"= {self.h_f}\n',
            f'"motor_OD"= {self.motor_OD}\n',
            f'"planet_bore"= {self.planet_bore}\n',
            f'"motor_height"= {self.motor_height}\n',
            f'"bearing_ID"= {self.bearing_ID}\n',
            f'"bearing_OD"= {self.bearing_OD}\n',
            f'"bearing_height"= {self.bearing_height}\n',
            f'"clearance_planet"= {self.clearance_planet}\n',
            f'"sec_carrier_thickness"= {self.sec_carrier_thickness}\n',
            f'"sun_coupler_hub_thickness"= {self.sun_coupler_hub_thickness}\n',
            f'"clearance_sun_coupler_sec_carrier"= {self.clearance_sun_coupler_sec_carrier}\n',
            f'"case_mounting_hole_dia"= {self.case_mounting_hole_dia}\n',
            f'"case_mounting_wrench_thickness"= {self.case_mounting_wrench_thickness}\n',
            f'"case_mounting_hole_allen_socket_dia"= {self.case_mounting_hole_allen_socket_dia}\n',
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
            f'"bearing_mount_thickness"= {self.bearing_mount_thickness}\n',
            f'"carrier_PCD"= {self.carrier_PCD}\n',
            f'"rotor_output_hole_PCD"= {self.rotor_output_hole_PCD}\n',
            f'"Rotor_output_hole_num"= {self.Rotor_output_hole_num}\n',
            f'"output_mounting_nut_thickness"= {self.output_mounting_nut_thickness}\n',
            f'"output_mounting_nut_wrench_size"= {self.output_mounting_nut_wrench_size}\n',
            f'"output_mounting_hole_dia"= {self.output_mounting_hole_dia}\n',
            f'"case_mounting_bolt_depth"= {self.case_mounting_bolt_depth}\n',
            f'"case_mounting_wrench_size"= {self.case_mounting_wrench_size}\n',
            f'"planet_pin_bolt_dia"= {self.planet_pin_bolt_dia}\n',
            f'"planet_pin_socket_head_dia"= {self.planet_pin_socket_head_dia}\n',
            f'"planet_shaft_dia"= {self.planet_shaft_dia}\n',
            f'"planet_pin_bolt_wrench_size"= {self.planet_pin_bolt_wrench_size}\n',
            f'"planet_shaft_step_offset"= {self.planet_shaft_step_offset}\n',
            f'"planet_bearing_OD"= {self.planet_bearing_OD}\n',
            f'"planet_bearing_width"= {self.planet_bearing_width}\n',
            f'"carrier_trapezoidal_support_sun_offset"= {self.carrier_trapezoidal_support_sun_offset}\n',
            f'"carrier_trapezoidal_support_hole_PCD_offset_bearing_ID"= {self.carrier_trapezoidal_support_hole_PCD_offset_bearing_ID}\n',
            f'"carrier_trapezoidal_support_hole_dia"= {self.carrier_trapezoidal_support_hole_dia}\n',
            f'"carrier_trapezoidal_support_hole_socket_head_dia"= {self.carrier_trapezoidal_support_hole_socket_head_dia}\n',
            f'"carrier_trapezoidal_support_hole_wrench_size"= {self.carrier_trapezoidal_support_hole_wrench_size}\n',
            f'"carrier_bearing_step_width"= {self.carrier_bearing_step_width}\n',
            f'"standard_clearance_1_5mm"= {self.standard_clearance_1_5mm}\n',
            f'"standard_fillet_1_5mm"= {self.standard_fillet_1_5mm}\n',
            f'"sun_shaft_bearing_OD"= {self.sun_shaft_bearing_OD}\n',
            f'"sun_shaft_bearing_width"= {self.sun_shaft_bearing_width}\n',
            f'"sun_shaft_bearing_ID"= {self.sun_shaft_bearing_ID}\n',
            f'"standard_bearing_insertion_chamfer"= {self.standard_bearing_insertion_chamfer}\n',
            f'"sun_hub_dia"= {self.sun_hub_dia}\n',
            f'"sun_central_bolt_dia"= {self.sun_central_bolt_dia}\n',
            f'"sun_central_bolt_socket_head_dia"= {self.sun_central_bolt_socket_head_dia}\n',
            f'"bearing_retainer_thickness"= {self.bearing_retainer_thickness}\n',
            f'"tight_clearance_3DP"= {self.tight_clearance_3DP}\n',
            f'"loose_clearance_3DP"= {self.loose_clearance_3DP}\n',
            f'"Stator_ID"= {self.Stator_ID}\n',
            f'"Stator_OD"= {self.Stator_OD}\n',
            f'"stator_height"= {self.stator_height}\n',
            f'"stator_casing_thickness"= {self.stator_casing_thickness}\n',
            f'"stator_bottom_step_height_"= {self.stator_bottom_step_height_}\n',
            f'"stator_upper_step_height"= {self.stator_upper_step_height}\n',
            f'"stator_side_step_OD"= {self.stator_side_step_OD}\n',
            f'"stator_mounting_holes_dia"= {self.stator_mounting_holes_dia}\n',
            f'"stator_hole_bolt_socket_head_dia"= {self.stator_hole_bolt_socket_head_dia}\n',
            f'"Rotor_height"= {self.Rotor_height}\n',
            f'"Rotor_OD"= {self.Rotor_OD}\n',
            f'"Rotor_ID"= {self.Rotor_ID}\n',
            f'"rotor_mount_hole_dia"= {self.rotor_mount_hole_dia}\n',
            f'"rotor_mount_hole_CSK_OD"= {self.rotor_mount_hole_CSK_OD}\n',
            f'"rotor_mount_hole_CSK_head_hight"= {self.rotor_mount_hole_CSK_head_hight}\n',
            f'"rotor_support_bearing_ID"= {self.rotor_support_bearing_ID}\n',
            f'"rotor_support_bearing_OD"= {self.rotor_support_bearing_OD}\n',
            f'"rotor_support_bearing_height"= {self.rotor_support_bearing_height}\n',
            f'"rotor_upper_support_bearing_ID"= {self.rotor_upper_support_bearing_ID}\n',
            f'"rotor_upper_support_bearing_OD"= {self.rotor_upper_support_bearing_OD}\n',
            f'"rotor_upper_support_bearing_height"= {self.rotor_upper_support_bearing_height}\n',
            f'"Rotor_tight_clearance"= {self.Rotor_tight_clearance}\n',
            f'"stator_bearing_support_casing_thickness"= {self.stator_bearing_support_casing_thickness}\n',
            f'"fw_s_used"= {self.fw_s_used}\n',
            f'"ringRadialWidthMM"= {self.ringRadialWidthMM}\n',
            f'"sun_support_OD"= {self.sun_support_OD}\n',
            f'"stator_casing_hole_dia"= {self.stator_casing_hole_dia}\n',
            f'"stator_casing_hole_socket_head_dia"= {self.stator_casing_hole_socket_head_dia}\n',
            f'"sun_bottom_casing_bearing_OD"= {self.sun_bottom_casing_bearing_OD}\n',
            f'"sun_bottom_casing_bearing_ID"= {self.sun_bottom_casing_bearing_ID}\n',
            f'"sun_bottom_casing_bearing_height"= {self.sun_bottom_casing_bearing_height}\n',
            f'"sun_sec_carrier_bearing_ID"= {self.sun_sec_carrier_bearing_ID}\n',
            f'"sun_sec_carrier_bearing_OD"= {self.sun_sec_carrier_bearing_OD}\n',
            f'"sun_sec_carrier_bearing_height"= {self.sun_sec_carrier_bearing_height}\n'
        ]

    def genEquationFile(self, motor_name="NO_MOTOR", gearRatioLL = 0.0, gearRatioUL = 0.0):
        self.setVariables()
        lines = self._equation_lines()
        
        # Matches Screenshot Structure: CADs/SSPG/Equation_Files/{motor_name}/
        path_sw = os.path.join(os.path.dirname(__file__), 'CADs', 'INSSPG',f'insspg_equations_{gearRatioLL}_{gearRatioUL}.txt')
        os.makedirs(os.path.dirname(path_sw), exist_ok=True)
        with open(path_sw, 'w') as eqFile: eqFile.writelines(lines)

        path_os = os.path.join(os.path.dirname(__file__), 'CADs', 'INSSPG',f'insspg_equations_{gearRatioLL}_{gearRatioUL}_onshape.txt')
        with open(path_os, 'w') as eqFile: eqFile.writelines(lines)

    def genEquationFile_editCADdirectly(self):
        self.setVariables()
        lines = self._equation_lines()

        path_sw = os.path.join(os.path.dirname(__file__), 'CADs', 'INSSPG', 'insspg_equations.txt')
        os.makedirs(os.path.dirname(path_sw), exist_ok=True)
        with open(path_sw, 'w') as eqFile: eqFile.writelines(lines)

        path_os = os.path.join(os.path.dirname(__file__), 'CADs', 'INSSPG', 'insspg_equations_onshape.txt')
        with open(path_os, 'w') as eqFile: eqFile.writelines(lines)

    #--------------------------------------------
    # Combined Minimalist Print Functions
    #--------------------------------------------
    def printParametersLess(self):
        vars = [self.module, self.Ns, self.Np, self.Nr, self.num_planet]
        print("\n--- SSPG Overview ---")
        print("[m, Ns, Np, Nr, numPl]:", vars)
        print("Gear ratio = ", round(self.planetaryGearbox.gearRatio(), 3))
        print("Efficiency = ", round(self.planetaryGearbox.getEfficiency(), 4))
        print("Mass (gearbox, kg) = ", round(getattr(self, 'gearbox_mass_kg', 0), 3), " kg")
        print("---------------------------------------------------")

    def printVolumeAndMassParameters(self):
        print("--- Mass Breakdown (g) ---")
        print("Motor mass:               ", round(1000 * self.motorMassKG, 2))
        print("Motor_case_mass:          ", round(1000 * getattr(self, 'Motor_case_mass', 0), 2))
        print("gearbox_casing_mass:      ", round(1000 * getattr(self, 'gearbox_casing_mass', 0), 2))
        print("carrier_mass:             ", round(1000 * getattr(self, 'carrier_mass', 0), 2))
        print("sun_mass:                 ", round(1000 * getattr(self, 'sun_mass', 0), 2))
        print("sec_carrier_mass:         ", round(1000 * getattr(self, 'sec_carrier_mass', 0), 2))
        print("planet_mass:              ", round(1000 * getattr(self, 'planet_mass', 0), 2))
        print("planet_bearing_mass:      ", round(1000 * getattr(self, 'planet_bearing_combined_mass', 0), 2))
        print("sun_shaft_bearing_mass:   ", round(1000 * getattr(self, 'sun_shaft_bearing_mass', 0), 2))
        print("bearing_mass:             ", round(1000 * getattr(self, 'bearing_mass', 0), 2))
        print("bearing_retainer_mass:    ", round(1000 * getattr(self, 'bearing_retainer_mass', 0), 2))
        print("---------------------------------------------------")

    #--------------------------------------------
    # Gear tooth stress analysis (Untouched Logic)
    #--------------------------------------------
    def getToothForces(self, constraintCheck=True):
        if constraintCheck:
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
        numPlanet = self.planetaryGearbox.numPlanet

        Ft = (self.serviceFactor*self.motor.getMaxMotorTorque())/( numPlanet * Rs_Mt)
        return Ft

    def lewisStressAnalysisMinFacewidth(self):
        if not self.planetaryGearbox.geometricConstraint(): return
        if not self.planetaryGearbox.meshingConstraint(): return
        if not self.planetaryGearbox.noPlanetInterferenceConstraint(): return
        
        Rs_Mt = self.planetaryGearbox.getPCRadiusSunM()
        Rp_Mt = self.planetaryGearbox.getPCRadiusPlanetM()
        
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
        P = np.pi*module*0.001 
        
        bMin_sun     = (self.FOS * Ft / (self.planetaryGearbox.maxGearAllowableStressPa * ySun    * Kv_sun    * P)) 
        bMin_planet1 = (self.FOS * Ft / (self.planetaryGearbox.maxGearAllowableStressPa * yPlanet * Kv_sun    * P))
        bMin_planet2 = (self.FOS * Ft / (self.planetaryGearbox.maxGearAllowableStressPa * yPlanet * Kv_planet * P))
        bMin_ring    = (self.FOS * Ft / (self.planetaryGearbox.maxGearAllowableStressPa * yRing   * Kv_ring   * P))

        bMin_planet = max(bMin_planet1, bMin_planet2)
        bMin_ring = max(bMin_ring, bMin_planet)
        bMin_planet = bMin_ring

        self.planetaryGearbox.setfwSunMM    ( bMin_sun    * 1000)
        self.planetaryGearbox.setfwPlanetMM ( bMin_planet * 1000)
        self.planetaryGearbox.setfwRingMM   ( bMin_ring   * 1000)

    def mitStressAnalysisMinFacewidth(self):
        if not self.planetaryGearbox.geometricConstraint(): return
        if not self.planetaryGearbox.meshingConstraint(): return
        if not self.planetaryGearbox.noPlanetInterferenceConstraint(): return
        
        Ns = self.planetaryGearbox.Ns
        module = self.planetaryGearbox.module
        Ft = self.getToothForces(False)
        
        _,_,CR = self.planetaryGearbox.contactRatio_sunPlanet()
        qe = 1 / CR
        qk = (7.65734266e-08 * Ns**4 - 2.19500130e-05 * Ns**3 + 2.33893357e-03 * Ns**2 - 1.13320908e-01 * Ns + 4.44727778)
        
        bMin_sun_mit    = (self.FOS * Ft * qe * qk / (self.planetaryGearbox.maxGearAllowableStressPa * module * 0.001)) 
        bMin_planet_mit = (self.FOS * Ft * qe * qk / (self.planetaryGearbox.maxGearAllowableStressPa * module * 0.001))
        bMin_ring_mit   = (self.FOS * Ft * qe * qk / (self.planetaryGearbox.maxGearAllowableStressPa * module * 0.001))

        if (bMin_planet_mit * 1000 < (self.planet_bearing_width*2 + self.standard_clearance_1_5mm * 2 / 3)) : 
            bMin_planet_mit = (self.planet_bearing_width*2 + self.standard_clearance_1_5mm * 2 / 3) / 1000
            bMin_ring_mit = bMin_planet_mit 

        bMin_sun_mitMM    = bMin_sun_mit    * 1000
        bMin_planet_mitMM = bMin_planet_mit * 1000
        bMin_ring_mitMM   = bMin_ring_mit   * 1000

        self.planetaryGearbox.setfwSunMM    ( bMin_sun_mit    * 1000)
        self.planetaryGearbox.setfwPlanetMM ( bMin_planet_mit * 1000)
        self.planetaryGearbox.setfwRingMM   ( bMin_ring_mit   * 1000)

        return bMin_sun_mitMM, bMin_planet_mitMM, bMin_ring_mitMM

    def AGMAStressAnalysisMinFacewidth(self):
        if not self.planetaryGearbox.geometricConstraint(): return
        if not self.planetaryGearbox.meshingConstraint(): return
        if not self.planetaryGearbox.noPlanetInterferenceConstraint_old(): return
        
        Rs_Mt = self.planetaryGearbox.getPCRadiusSunM()
        Rp_Mt = self.planetaryGearbox.getPCRadiusPlanetM()

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

        Wt = self.getToothForces(False) 

        Y_planet   = (0.154 - 0.912 / Np) * np.pi
        Y_sun      = (0.154 - 0.912 / Ns) * np.pi
        Y_ring     = (0.154 - 0.912 / Nr) * np.pi

        H = 0.331 - (0.436 * np.pi * pressureAngle / 180)
        L = 0.324 - (0.492 * np.pi * pressureAngle / 180)
        M = 0.261 + (0.545 * np.pi * pressureAngle / 180) 
        
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

        Yj_planet = Y_planet/Kf_planet
        Yj_sun = Y_sun/Kf_sun
        Yj_ring = Y_ring/Kf_ring 

        Qv = 7      
        B_planet =  0.25*(12-Qv)**(2/3)
        A_planet = 50 + 56*(1-B_planet)
        Kv_planet = ((A_planet+np.sqrt(200*max(V_rp, V_sp)))/A_planet)**B_planet

        B_sun =  0.25*(12-Qv)**(2/3)
        A_sun = 50 + 56*(1-B_sun)
        Kv_sun = ((A_sun+np.sqrt(200*V_sp))/A_sun)**B_sun

        B_ring =  0.25*(12-Qv)**(2/3)
        A_ring = 50 + 56*(1-B_ring)
        Kv_ring = ((A_ring+np.sqrt(200*V_rp))/A_ring)**B_planet

        Ks = Kh = Kb = 1
        
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

     # --- ROUTER FUNCTION ---

    def getMassKG_3DP(self):
        if self.insspg_type == "insspg_type_2":
            return self._getMassKG_3DP_type2()
        else:
            return self._getMassKG_3DP_type1()

    # --- YOUR NEW MASS MATH ---
    def _getMassKG_3DP_type2(self):
        self.setVariables()
        module    = self.planetaryGearbox.module
        Ns        = self.planetaryGearbox.Ns
        Np        = self.planetaryGearbox.Np
        Nr        = self.planetaryGearbox.Nr
        numPlanet = self.planetaryGearbox.numPlanet

        density_3DP_material = self.planetaryGearbox.densityGears

        sunFwM    = self.planetaryGearbox.fwSunMM * 0.001
        planetFwM = self.planetaryGearbox.fwPlanetMM * 0.001
        ringFwM   = self.planetaryGearbox.fwRingMM * 0.001

        sunFwMM    = self.planetaryGearbox.fwSunMM 
        planetFwMM = self.planetaryGearbox.fwPlanetMM
        ringFwMM   = self.planetaryGearbox.fwRingMM

        DiaSunMM    = Ns * module
        DiaPlanetMM = Np * module
        DiaRingMM   = Nr * module

        RadiusSunMM    = DiaSunMM    * 0.5
        RadiusPlanetMM = DiaPlanetMM * 0.5
        RadiusRingMM   = DiaRingMM   * 0.5
        
        standard_clearance_1_5mm     = self.standard_clearance_1_5mm   
        clearance_planet             = self.clearance_planet            
        output_mounting_hole_dia     = self.output_mounting_hole_dia    
        sec_carrier_thickness        = self.sec_carrier_thickness       
        sun_coupler_hub_thickness    = self.sun_coupler_hub_thickness   
        sun_shaft_bearing_OD         = self.sun_shaft_bearing_OD        
        carrier_bearing_step_width   = self.carrier_bearing_step_width  
        planet_shaft_dia             = self.planet_shaft_dia            
        sun_shaft_bearing_ID         = self.sun_shaft_bearing_ID        
        sun_shaft_bearing_width      = self.sun_shaft_bearing_width     
        planet_bore                  = self.planet_bore                 
        bearing_retainer_thickness   = self.bearing_retainer_thickness  


        ring_radial_thickness = self.ringRadialWidthMM
        ring_OD  = Nr * module + ring_radial_thickness*2
        motor_OD = self.motorDiaMM


        motor_height      = self.motorLengthMM

        ring_ID      = Nr * module
        ringFwUsedMM = ringFwMM + clearance_planet

        # Pull the dynamically calculated bearing sizes from self (MATCHING YOUR SCREENSHOT)
        bearing_ID     = self.bearing_ID 
        bearing_OD     = self.bearing_OD 
        bearing_height = self.bearing_height    
        bearing_mass   = self.bearing_mass

        carrier_OD     = bearing_ID
        carrier_ID     = sun_shaft_bearing_OD - standard_clearance_1_5mm * 2
        carrier_height = bearing_height + carrier_bearing_step_width

        carrier_shaft_OD = planet_shaft_dia
        carrier_shaft_height = planetFwMM + clearance_planet * 2
        carrier_shaft_num = numPlanet * 2

        carrier_volume = (np.pi * (((carrier_OD*0.5)**2) - ((carrier_ID)*0.5)**2) * carrier_height
                         + np.pi * ((carrier_shaft_OD*0.5)**2) * carrier_shaft_height * carrier_shaft_num) * 1e-9

        carrier_mass = carrier_volume * density_3DP_material

        ##------sun_gear_mass_calculation--------##

        sun_hub_dia = self.sun_hub_dia
        sun_shaft_dia    = sun_shaft_bearing_ID
        sun_shaft_height = sun_shaft_bearing_width + 2 * standard_clearance_1_5mm
        sun_supportOD = self.sun_support_OD
        fw_s_used = self.fw_s_used

        sun_hub_volume   = np.pi * ((sun_hub_dia*0.5) ** 2) * sun_coupler_hub_thickness * 1e-9
        sun_gear_volume  = np.pi * ((DiaSunMM * 0.5) ** 2) * fw_s_used * 1e-9
        sun_shaft_volume = np.pi * ((sun_shaft_dia*0.5) ** 2) * sun_shaft_height * 1e-9
        sun_uper_support_volume = np .pi * (self.Rotor_height-2-sun_coupler_hub_thickness)*((self.sun_sec_carrier_bearing_ID/2+standard_clearance_1_5mm/3)**2 - (DiaSunMM*0.5)**2 )*1e-9
        sun_bottom_part_volume = np.pi * (self.sun_bottom_casing_bearing_height+standard_clearance_1_5mm)*((self.sun_bottom_casing_bearing_ID/2)**2 -(self.sun_central_bolt_socket_head_dia/2)**2)*1e-9 + np.pi*(self.stator_bottom_step_height_ - (self.sun_bottom_casing_bearing_height - (self.stator_casing_thickness - self.standard_clearance_1_5mm)) + 2)*((self.sun_bottom_casing_bearing_ID/2+standard_clearance_1_5mm)**2 -(self.sun_central_bolt_socket_head_dia/2)**2)*1e-9

        
        sun_volume       = sun_hub_volume + sun_gear_volume + sun_shaft_volume + sun_uper_support_volume + sun_bottom_part_volume
        sun_mass         = sun_volume * density_3DP_material

        ##--------planet_gear_volume------------##

        planet_volume = (np.pi * ((DiaPlanetMM*0.5)**2 - (planet_bore*0.5)**2) * planetFwMM) * 1e-9
        planet_mass   = planet_volume * density_3DP_material
        
        ##--------sec_carrier_volume-----------##

        sec_carrier_OD = bearing_ID
        sec_carrier_ID = (DiaSunMM + DiaPlanetMM) - planet_shaft_dia - 2 * standard_clearance_1_5mm
        sec_carrier_bearing_support_volume = np.pi * self.sun_sec_carrier_bearing_height * ((self.sun_sec_carrier_bearing_OD/2+standard_clearance_1_5mm*2.5)**2 - (self.sun_sec_carrier_bearing_OD/2)**2)*1e-9 + np.pi * standard_clearance_1_5mm * ((self.sun_sec_carrier_bearing_OD/2+standard_clearance_1_5mm*2.5)**2 - (self.sun_sec_carrier_bearing_OD/2-standard_clearance_1_5mm)**2)*1e-9


        sec_carrier_volume = (np.pi * ((sec_carrier_OD*0.5)**2 - (sec_carrier_ID*0.5)**2) * sec_carrier_thickness) * 1e-9 + sec_carrier_bearing_support_volume
        sec_carrier_mass   = sec_carrier_volume * density_3DP_material
        
        ##------sun and planet bearing mass ---------##

        sun_shaft_bearing_mass       = 4 * 0.001 + 0.0066 + 0.0079 # mass of both rotor support bearing added
        planet_bearing_mass          = 1 * 0.001 
        planet_bearing_num           = numPlanet * 2
        planet_bearing_combined_mass = planet_bearing_mass * planet_bearing_num

        ## -------- motor_casing_mass----------##
        
        #upper_casing_cy_1_ID = self.rotor_upper_support_bearing_ID
        #upper_casing_cy_1_OD = self.Stator_ID + 1
        #upper_casing_cy_1_height = self.rotor_upper_support_bearing_height + self.standard_clearance_1_5mm
        #upper_casing_cy_1_VOL = np.pi * upper_casing_cy_1_height * ((upper_casing_cy_1_OD/2)**2 - (upper_casing_cy_1_ID/2)**2 ) * 1e-9

        #upper_casing_cy_2_ID = upper_casing_cy_1_OD
        #upper_casing_cy_2_OD = self.Stator_OD + self.stator_casing_thickness*2
        #upper_casing_cy_2_height = self.stator_bearing_support_casing_thickness-standard_clearance_1_5mm/2
        #upper_casing_cy_2_VOL = np.pi * upper_casing_cy_2_height * ((upper_casing_cy_2_OD/2)**2 - (upper_casing_cy_2_ID/2)**2) * 1e-9

        #upper_casing_cy_3_ID = self.stator_side_step_OD + self.tight_clearance_3DP*2
        #upper_casing_cy_3_OD = upper_casing_cy_2_OD
        #upper_casing_cy_3_height = self.stator_upper_step_height + self.loose_clearance_3DP
        #upper_casing_cy_3_VOL = np.pi * upper_casing_cy_3_height * ((upper_casing_cy_3_OD/2)**2 - (upper_casing_cy_3_ID/2)**2) * 1e-9 

        #uper_casing_VOL = upper_casing_cy_2_VOL + upper_casing_cy_3_VOL

        middle_casing_VOL = np.pi * (self.stator_height-self.stator_upper_step_height+standard_clearance_1_5mm*2.5) * ((self.Stator_OD/2+self.stator_casing_thickness)**2 - (self.Stator_OD/2)**2) * 1e-9
        
        bottom_casing_plate_VOL = np.pi * (self.stator_casing_thickness) * ((self.Stator_OD/2+self.stator_casing_thickness)**2) * 1e-9 + np.pi * (standard_clearance_1_5mm) * ((self.Stator_OD/2+self.stator_casing_thickness)**2 - (self.Stator_OD/2+self.stator_casing_thickness-2.5)**2)* 1e-9
        #bottom_casing_step_height_VOL = np.pi * (self.stator_bottom_step_height_-self.standard_clearance_1_5mm) * ((50/2)**2) * 1e-9 + np.pi * (standard_clearance_1_5mm) * ((self.rotor_support_bearing_ID/2+standard_clearance_1_5mm*2)**2)*1e-9
        bottom_casing_bearing_support_VOL = np.pi * (self.sun_bottom_casing_bearing_height - (self.stator_casing_thickness - self.standard_clearance_1_5mm))* ((self.sun_bottom_casing_bearing_OD/2+standard_clearance_1_5mm*2)**2) * 1e-9
        bottom_casing_hole_VOL = np.pi * (self.sun_bottom_casing_bearing_height - (self.stator_casing_thickness - self.standard_clearance_1_5mm)+self.stator_casing_thickness)*((self.sun_bottom_casing_bearing_OD/2)**2)*1e-9

        bottom_casing_vol = bottom_casing_plate_VOL+bottom_casing_bearing_support_VOL - bottom_casing_hole_VOL + 4*np.pi*2*((9/2)**2-(5.5/2)**2)*1e-9

        Motor_case_vol = middle_casing_VOL+bottom_casing_vol
        Motor_case_mass = Motor_case_vol * density_3DP_material

        ##---------carrier_vol--------##
        # Radii
        r_carrier_outer     = (self.bearing_ID / 2) / 1000
        r_carrier_trapezoid = ((self.bearing_ID
                                - (self.Ns * self.module + 2 * self.carrier_trapezoidal_support_sun_offset))
                               / 4) / 1000
        
        fw_carrier = self.fw_p / 1000

        # Volume sub-components
        vol_carrier_disk      = math.pi * (self.bearing_height / 1000) * r_carrier_outer     ** 2
        vol_carrier_trapezoid = math.pi * fw_carrier * r_carrier_trapezoid ** 2

        vol_carrier_net = vol_carrier_disk + 3 * vol_carrier_trapezoid   # 3 trapezoidal arms
        carrier_mass = vol_carrier_net * density_3DP_material

        ##---------ring_gear_mass--------##

        # --------------------------------------------------------
        # --- CONDITIONAL RING GEAR MASS ---
        # --------------------------------------------------------
        # Condition: (Bearing OD - Clearance*2) > (Nr * module + Loose Clearance)
        left_side  = bearing_OD - (self.standard_clearance_1_5mm * 2)
        right_side = (self.Nr * self.module) + self.loose_clearance_3DP

        if left_side > right_side:
            # TRUE: Bearing side is larger
            top_mount_vol = np.pi * (bearing_height+self.loose_clearance_3DP+standard_clearance_1_5mm) * ((bearing_OD/2+self.case_mounting_wrench_size+standard_clearance_1_5mm)**2 - (bearing_OD/2)**2)* 1e-9
            bearing_step_volume = np.pi * (carrier_bearing_step_width + self.loose_clearance_3DP) * ((bearing_OD/2)**2 - (ring_ID/2+self.loose_clearance_3DP/2)**2 )* 1e-9
            ring_gear_volume = np.pi * ( ringFwMM )*((ring_OD/2)**2 - (ring_ID/2)**2)* 1e-9
            ring_bearing_support_below_volume = np.pi * standard_clearance_1_5mm * ((bearing_OD/2+self.case_mounting_wrench_size+standard_clearance_1_5mm)**2-(ring_OD/2)**2)*1e-9
            ring_bottom_part_volume = (np.pi * (self.stator_casing_thickness)*((self.Stator_OD/2+self.stator_casing_thickness)**2-(ring_OD/2)**2)*1e-9 + np.pi * (self.stator_upper_step_height)*((self.Stator_OD/2+self.stator_casing_thickness)**2-(self.stator_side_step_OD/2)**2)* 1e-9 
                                       +  np.pi*(self.sec_carrier_thickness - (self.stator_height - self.stator_bottom_step_height_ - self.Rotor_height) + self.clearance_planet)*((self.Stator_OD/2+self.stator_casing_thickness)**2-(self.Stator_OD/2+self.stator_casing_thickness-standard_clearance_1_5mm-self.case_mounting_hole_allen_socket_dia)**2)*1e-9
                                       -  np.pi*(standard_clearance_1_5mm*2)*((self.Stator_OD/2+self.stator_casing_thickness)**2-(self.stator_side_step_OD/2)**2)*1e-9)
            
            ring_vol_net = top_mount_vol + bearing_step_volume + ring_gear_volume + ring_bottom_part_volume + ring_bearing_support_below_volume
            ring_mass = ring_vol_net * density_3DP_material

        else:
            # FALSE: Gear side is larger
            top_mount_vol = np.pi * (bearing_height+self.loose_clearance_3DP+standard_clearance_1_5mm) * ((bearing_OD/2+self.case_mounting_wrench_size+standard_clearance_1_5mm)**2 - (bearing_OD/2)**2)* 1e-9
            bearing_step_volume = np.pi * (carrier_bearing_step_width + self.loose_clearance_3DP) * ((bearing_OD/2)**2 - (bearing_OD/2-standard_clearance_1_5mm)**2 )* 1e-9
            ring_gear_volume = np.pi * ( ringFwMM )*((ring_OD/2)**2 - (ring_ID/2)**2)* 1e-9
            ring_bearing_support_below_volume = np.pi * standard_clearance_1_5mm * ((bearing_OD/2+self.case_mounting_wrench_size+standard_clearance_1_5mm)**2-(ring_OD/2)**2)*1e-9
            ring_bottom_part_volume = (np.pi * (self.stator_casing_thickness)*((self.Stator_OD/2+self.stator_casing_thickness)**2-(ring_OD/2)**2)*1e-9 + np.pi * (self.stator_upper_step_height)*((self.Stator_OD/2+self.stator_casing_thickness)**2-(self.stator_side_step_OD/2)**2)* 1e-9 
                                       +  np.pi*(self.sec_carrier_thickness - (self.stator_height - self.stator_bottom_step_height_ - self.Rotor_height) + self.clearance_planet)*((self.Stator_OD/2+self.stator_casing_thickness)**2-(self.Stator_OD/2+self.stator_casing_thickness-standard_clearance_1_5mm-self.case_mounting_hole_allen_socket_dia)**2)*1e-9
                                       -  np.pi*(standard_clearance_1_5mm*2)*((self.Stator_OD/2+self.stator_casing_thickness)**2-(self.stator_side_step_OD/2)**2)*1e-9)
            
            ring_vol_net = top_mount_vol + bearing_step_volume + ring_gear_volume + ring_bottom_part_volume + ring_bearing_support_below_volume
            ring_mass = ring_vol_net * density_3DP_material

        # --------------------------------------------------------
        
        top_mount_vol = np.pi * (bearing_height) * ((bearing_OD/2+self.case_mounting_wrench_size+standard_clearance_1_5mm)**2 - (bearing_OD/2)**2)* 1e-9
        bearing_step_volume = np.pi * (carrier_bearing_step_width + standard_clearance_1_5mm/2) * ((ring_OD/2)**2 - (bearing_OD/2-standard_clearance_1_5mm)**2 )* 1e-9
        ring_gear_volume = np.pi * ( ringFwMM )*((ring_OD/2)**2 - (ring_ID/2)**2)* 1e-9
        ring_bottom_part_volume = np.pi * (self.stator_casing_thickness)*((self.Stator_OD/2+self.stator_casing_thickness)**2-(ring_OD/2)**2)*1e-9 + np.pi * (sec_carrier_thickness+clearance_planet+self.loose_clearance_3DP)*((self.Stator_OD/2+self.stator_casing_thickness)**2-(self.Stator_OD/2-self.stator_mounting_holes_dia/2-self.stator_casing_thickness-standard_clearance_1_5mm/2)**2)* 1e-9
        
        ring_vol_net = top_mount_vol + bearing_step_volume + ring_gear_volume + ring_bottom_part_volume
        ring_mass = ring_vol_net * density_3DP_material

        ##-------bearing-retainer-mass---------##

        bearing_retainer_volume = np.pi * bearing_retainer_thickness * ((bearing_OD/2+self.case_mounting_wrench_size+standard_clearance_1_5mm)**2 - (bearing_OD/2-standard_clearance_1_5mm)**2)*1e-9
        bearing_retainer_mass = bearing_retainer_volume * density_3DP_material

        ##--------all_parts_mass--------##

        self.Motor_case_mass              = Motor_case_mass
        self.carrier_mass                 = carrier_mass
        self.sun_mass                     = sun_mass
        self.sec_carrier_mass             = sec_carrier_mass
        self.planet_mass                  = planet_mass
        self.planet_bearing_combined_mass = planet_bearing_combined_mass
        self.sun_shaft_bearing_mass       = sun_shaft_bearing_mass
        self.bearing_mass                 = bearing_mass+planet_bearing_combined_mass+sun_shaft_bearing_mass
        self.ring_mass                    = ring_mass
        self.bearing_retainer_mass        = bearing_retainer_mass

        gearbox_mass = self.Motor_case_mass + self.carrier_mass + self.sun_mass + (self.planet_mass * self.num_planet) + self.ring_mass + self.sec_carrier_mass + self.bearing_retainer_mass +0.01
        self.gearbox_mass = gearbox_mass
        Actuator_mass = (self.motorMassKG 
                         + self.Motor_case_mass  
                         + self.carrier_mass 
                         + self.sun_mass 
                         + self.sec_carrier_mass 
                         + self.planet_mass * numPlanet 
                         + self.bearing_mass 
                         + self.ring_mass
                         + self.bearing_retainer_mass
                         )

        return Actuator_mass

    def _getMassKG_3DP_type1(self):
        self.setVariables() 
        module    = self.planetaryGearbox.module
        Ns        = self.planetaryGearbox.Ns
        Np        = self.planetaryGearbox.Np
        Nr        = self.planetaryGearbox.Nr
        numPlanet = self.planetaryGearbox.numPlanet

        density_3DP_material = self.planetaryGearbox.densityGears

        sunFwM    = self.planetaryGearbox.fwSunMM * 0.001
        planetFwM = self.planetaryGearbox.fwPlanetMM * 0.001
        ringFwM   = self.planetaryGearbox.fwRingMM * 0.001

        sunFwMM    = self.planetaryGearbox.fwSunMM 
        planetFwMM = self.planetaryGearbox.fwPlanetMM
        ringFwMM   = self.planetaryGearbox.fwRingMM

        DiaSunMM    = Ns * module
        DiaPlanetMM = Np * module
        DiaRingMM   = Nr * module

        RadiusSunMM    = DiaSunMM    * 0.5
        RadiusPlanetMM = DiaPlanetMM * 0.5
        RadiusRingMM   = DiaRingMM   * 0.5
        

        standard_clearance_1_5mm     = self.standard_clearance_1_5mm   
        clearance_planet             = self.clearance_planet            
        output_mounting_hole_dia     = self.output_mounting_hole_dia    
        sec_carrier_thickness        = self.sec_carrier_thickness       
        sun_coupler_hub_thickness    = self.sun_coupler_hub_thickness   
        sun_shaft_bearing_OD         = self.sun_shaft_bearing_OD        
        carrier_bearing_step_width   = self.carrier_bearing_step_width  
        planet_shaft_dia             = self.planet_shaft_dia            
        sun_shaft_bearing_ID         = self.sun_shaft_bearing_ID        
        sun_shaft_bearing_width      = self.sun_shaft_bearing_width     
        planet_bore                  = self.planet_bore                 
        bearing_retainer_thickness   = self.bearing_retainer_thickness  


        ring_radial_thickness = self.ringRadialWidthMM
        ring_OD  = Nr * module + ring_radial_thickness*2
        motor_OD = self.motorDiaMM


        motor_height      = self.motorLengthMM

        ring_ID      = Nr * module
        ringFwUsedMM = ringFwMM + clearance_planet

        # Pull the dynamically calculated bearing sizes from self (MATCHING YOUR SCREENSHOT)
        bearing_ID     = self.bearing_ID 
        bearing_OD     = self.bearing_OD 
        bearing_height = self.bearing_height    
        bearing_mass   = self.bearing_mass

        carrier_OD     = bearing_ID
        carrier_ID     = sun_shaft_bearing_OD - standard_clearance_1_5mm * 2
        carrier_height = bearing_height + carrier_bearing_step_width

        carrier_shaft_OD = planet_shaft_dia
        carrier_shaft_height = planetFwMM + clearance_planet * 2
        carrier_shaft_num = numPlanet * 2

        carrier_volume = (np.pi * (((carrier_OD*0.5)**2) - ((carrier_ID)*0.5)**2) * carrier_height
                        + np.pi * ((carrier_shaft_OD*0.5)**2) * carrier_shaft_height * carrier_shaft_num) * 1e-9

        carrier_mass = carrier_volume * density_3DP_material

        ##------sun_gear_mass_calculation--------##

        sun_hub_dia = self.sun_hub_dia
        sun_shaft_dia    = sun_shaft_bearing_ID
        sun_shaft_height = sun_shaft_bearing_width + 2 * standard_clearance_1_5mm
        sun_supportOD = self.sun_support_OD
        fw_s_used = self.fw_s_used

        sun_hub_volume   = np.pi * ((sun_hub_dia*0.5) ** 2) * sun_coupler_hub_thickness * 1e-9
        sun_gear_volume  = np.pi * ((DiaSunMM * 0.5) ** 2) * fw_s_used * 1e-9
        sun_shaft_volume = np.pi * ((sun_shaft_dia*0.5) ** 2) * sun_shaft_height * 1e-9
        sun_uper_support_volume = np .pi * (fw_s_used-self.fw_p-clearance_planet-sec_carrier_thickness/2)*((sun_supportOD/2)**2 - (DiaSunMM*0.5)**2 )*1e-9
        sun_bottom_part_volume = np.pi*(self.Rotor_height+self.stator_bottom_step_height_)*((14/2)** - (self.sun_central_bolt_socket_head_dia/2)**2)*1e-9 + np.pi * (standard_clearance_1_5mm*4)*((14/2+standard_clearance_1_5mm)**2-(14/2)**2)*1e-9
        
        sun_volume       = sun_hub_volume + sun_gear_volume + sun_shaft_volume + sun_uper_support_volume + sun_bottom_part_volume
        sun_mass         = sun_volume * density_3DP_material

        ##--------planet_gear_volume------------##

        planet_volume = (np.pi * ((DiaPlanetMM*0.5)**2 - (planet_bore*0.5)**2) * planetFwMM) * 1e-9
        planet_mass   = planet_volume * density_3DP_material
        
        ##--------sec_carrier_volume-----------##

        sec_carrier_OD = bearing_ID
        sec_carrier_ID = (DiaSunMM + DiaPlanetMM) - planet_shaft_dia - 2 * standard_clearance_1_5mm

        sec_carrier_volume = (np.pi * ((sec_carrier_OD*0.5)**2 - (sec_carrier_ID*0.5)**2) * sec_carrier_thickness) * 1e-9
        sec_carrier_mass   = sec_carrier_volume * density_3DP_material
        
        ##------sun and planet bearing mass ---------##

        sun_shaft_bearing_mass       = 4 * 0.001 + 0.022 + 0.026 # mass of both rotor support bearing added
        planet_bearing_mass          = 1 * 0.001 
        planet_bearing_num           = numPlanet * 2
        planet_bearing_combined_mass = planet_bearing_mass * planet_bearing_num

        ## -------- motor_casing_mass----------##
        
        upper_casing_cy_1_ID = self.rotor_upper_support_bearing_ID
        upper_casing_cy_1_OD = self.Stator_ID + 1
        upper_casing_cy_1_height = self.rotor_upper_support_bearing_height + self.standard_clearance_1_5mm
        upper_casing_cy_1_VOL = np.pi * upper_casing_cy_1_height * ((upper_casing_cy_1_OD/2)**2 - (upper_casing_cy_1_ID/2)**2 ) * 1e-9

        upper_casing_cy_2_ID = upper_casing_cy_1_OD
        upper_casing_cy_2_OD = self.Stator_OD + self.stator_casing_thickness*2
        upper_casing_cy_2_height = self.stator_bearing_support_casing_thickness-standard_clearance_1_5mm/2
        upper_casing_cy_2_VOL = np.pi * upper_casing_cy_2_height * ((upper_casing_cy_2_OD/2)**2 - (upper_casing_cy_2_ID/2)**2) * 1e-9

        upper_casing_cy_3_ID = self.stator_side_step_OD + self.tight_clearance_3DP*2
        upper_casing_cy_3_OD = upper_casing_cy_2_OD
        upper_casing_cy_3_height = self.stator_upper_step_height + self.loose_clearance_3DP
        upper_casing_cy_3_VOL = np.pi * upper_casing_cy_3_height * ((upper_casing_cy_3_OD/2)**2 - (upper_casing_cy_3_ID/2)**2) * 1e-9

        uper_casing_VOL = upper_casing_cy_1_VOL + upper_casing_cy_2_VOL + upper_casing_cy_3_VOL

        middle_casing_VOL = np.pi * (self.stator_height-self.stator_upper_step_height+standard_clearance_1_5mm) * ((self.Stator_OD/2+self.stator_casing_thickness)**2 - (self.Stator_OD/2)**2) * 1e-9
        
        bottom_casing_plate_VOL = np.pi * (self.stator_casing_thickness) * ((self.Stator_OD/2+self.stator_casing_thickness)**2) * 1e-9 + np.pi * (standard_clearance_1_5mm) * ((self.Stator_OD/2+self.stator_casing_thickness)**2 - (self.Stator_OD/2+self.stator_casing_thickness-2.5)**2)* 1e-9
        bottom_casing_step_height_VOL = np.pi * (self.stator_bottom_step_height_-self.standard_clearance_1_5mm) * ((50/2)**2) * 1e-9 + np.pi * (standard_clearance_1_5mm) * ((self.rotor_support_bearing_ID/2+standard_clearance_1_5mm*2)**2)*1e-9
        bottom_casing_bearing_support_VOL = np.pi * (self.rotor_support_bearing_height)* ((self.rotor_support_bearing_ID/2)**2) * 1e-9
        bottom_casing_hole_VOL = np.pi * (self.rotor_support_bearing_height+self.stator_bottom_step_height_+self.stator_casing_thickness)*((self.rotor_support_bearing_ID/2-standard_clearance_1_5mm*2)**2)*1e-9

        bottom_casing_vol = bottom_casing_plate_VOL+bottom_casing_step_height_VOL+bottom_casing_bearing_support_VOL - bottom_casing_hole_VOL

        Motor_case_vol = uper_casing_VOL + middle_casing_VOL+bottom_casing_vol
        Motor_case_mass = Motor_case_vol * density_3DP_material

        ##---------carrier_vol--------##
        # Radii
        r_carrier_outer     = (self.bearing_ID / 2) / 1000
        r_carrier_trapezoid = ((self.bearing_ID
                                - (self.Ns * self.module + 2 * self.carrier_trapezoidal_support_sun_offset))
                               / 4) / 1000
        
        fw_carrier = self.fw_p / 1000

        # Volume sub-components
        vol_carrier_disk      = math.pi * (self.bearing_height / 1000) * r_carrier_outer     ** 2
        vol_carrier_trapezoid = math.pi * fw_carrier * r_carrier_trapezoid ** 2

        vol_carrier_net = vol_carrier_disk + 3 * vol_carrier_trapezoid   # 3 trapezoidal arms
        carrier_mass = vol_carrier_net * density_3DP_material

        ##---------ring_gear_mass--------##

        # --------------------------------------------------------
        # --- CONDITIONAL RING GEAR MASS ---
        # --------------------------------------------------------
        # Condition: (Bearing OD - Clearance*2) > (Nr * module + Loose Clearance)
        left_side  = bearing_OD - (self.standard_clearance_1_5mm * 2)
        right_side = (self.Nr * self.module) + self.loose_clearance_3DP

        if left_side > right_side:
            # TRUE: Bearing side is larger
            top_mount_vol = np.pi * (bearing_height+self.loose_clearance_3DP+standard_clearance_1_5mm) * ((bearing_OD/2+self.case_mounting_wrench_size+standard_clearance_1_5mm)**2 - (bearing_OD/2)**2)* 1e-9
            bearing_step_volume = np.pi * (carrier_bearing_step_width + self.loose_clearance_3DP) * ((bearing_OD/2)**2 - (ring_ID/2+self.loose_clearance_3DP/2)**2 )* 1e-9
            ring_gear_volume = np.pi * ( ringFwMM )*((ring_OD/2)**2 - (ring_ID/2)**2)* 1e-9
            ring_bearing_support_below_volume = np.pi * standard_clearance_1_5mm * ((bearing_OD/2+self.case_mounting_wrench_size+standard_clearance_1_5mm)**2-(ring_OD/2)**2)*1e-9
            ring_bottom_part_volume = np.pi * (self.stator_casing_thickness)*((self.Stator_OD/2+self.stator_casing_thickness)**2-(ring_OD/2)**2)*1e-9 + np.pi * (sec_carrier_thickness+clearance_planet+self.loose_clearance_3DP)*((self.Stator_OD/2+self.stator_casing_thickness)**2-(self.Stator_OD/2-self.stator_mounting_holes_dia/2-self.stator_casing_thickness-standard_clearance_1_5mm/2)**2)* 1e-9
        
            ring_vol_net = top_mount_vol + bearing_step_volume + ring_gear_volume + ring_bottom_part_volume + ring_bearing_support_below_volume
            ring_mass = ring_vol_net * density_3DP_material


        else:
            # FALSE: Gear side is larger
            top_mount_vol = np.pi * (bearing_height+self.loose_clearance_3DP+standard_clearance_1_5mm) * ((bearing_OD/2+self.case_mounting_wrench_size+standard_clearance_1_5mm)**2 - (bearing_OD/2)**2)* 1e-9
            bearing_step_volume = np.pi * (carrier_bearing_step_width + self.loose_clearance_3DP) * ((bearing_OD/2)**2 - (bearing_OD/2-standard_clearance_1_5mm)**2 )* 1e-9
            ring_gear_volume = np.pi * ( ringFwMM )*((ring_OD/2)**2 - (ring_ID/2)**2)* 1e-9
            ring_bearing_support_below_volume = np.pi * standard_clearance_1_5mm * ((bearing_OD/2+self.case_mounting_wrench_size+standard_clearance_1_5mm)**2-(ring_OD/2)**2)*1e-9
            ring_bottom_part_volume = np.pi * (self.stator_casing_thickness)*((self.Stator_OD/2+self.stator_casing_thickness)**2-(ring_OD/2)**2)*1e-9 + np.pi * (sec_carrier_thickness+clearance_planet+self.loose_clearance_3DP)*((self.Stator_OD/2+self.stator_casing_thickness)**2-(self.Stator_OD/2-self.stator_mounting_holes_dia/2-self.stator_casing_thickness-standard_clearance_1_5mm/2)**2)* 1e-9
            
            ring_vol_net = top_mount_vol + bearing_step_volume + ring_gear_volume + ring_bottom_part_volume + ring_bearing_support_below_volume
            ring_mass = ring_vol_net * density_3DP_material

        # --------------------------------------------------------

        ##---------ring_gear_mass_old--------##
        
        #top_mount_vol = np.pi * (bearing_height) * ((bearing_OD/2+self.case_mounting_wrench_size+standard_clearance_1_5mm)**2 - (bearing_OD/2)**2)* 1e-9
        #bearing_step_volume = np.pi * (carrier_bearing_step_width + standard_clearance_1_5mm/2) * ((ring_OD/2)**2 - (bearing_OD/2-standard_clearance_1_5mm)**2 )* 1e-9
        #ring_gear_volume = np.pi * ( ringFwMM )*((ring_OD/2)**2 - (ring_ID/2)**2)* 1e-9
        #ring_bottom_part_volume = np.pi * (self.stator_casing_thickness)*((self.Stator_OD/2+self.stator_casing_thickness)**2-(ring_OD/2)**2)*1e-9 + np.pi * (sec_carrier_thickness+clearance_planet+self.loose_clearance_3DP)*((self.Stator_OD/2+self.stator_casing_thickness)**2-(self.Stator_OD/2-self.stator_mounting_holes_dia/2-self.stator_casing_thickness-standard_clearance_1_5mm/2)**2)* 1e-9
        
        #ring_vol_net = top_mount_vol + bearing_step_volume + ring_gear_volume + ring_bottom_part_volume
        #ring_mass = ring_vol_net * density_3DP_material

        ##-------bearing-retainer-mass---------##

        bearing_retainer_volume = np.pi * bearing_retainer_thickness * ((bearing_OD/2+self.case_mounting_wrench_size+standard_clearance_1_5mm)**2 - (bearing_OD/2-standard_clearance_1_5mm)**2)*1e-9
        bearing_retainer_mass = bearing_retainer_volume * density_3DP_material

        ##--------all_parts_mass--------##

        self.Motor_case_mass              = Motor_case_mass
        self.carrier_mass                 = carrier_mass
        self.sun_mass                     = sun_mass
        self.sec_carrier_mass             = sec_carrier_mass
        self.planet_mass                  = planet_mass
        self.planet_bearing_combined_mass = planet_bearing_combined_mass
        self.sun_shaft_bearing_mass       = sun_shaft_bearing_mass
        self.bearing_mass                 = bearing_mass+planet_bearing_combined_mass+sun_shaft_bearing_mass
        self.ring_mass                    = ring_mass
        self.bearing_retainer_mass        = bearing_retainer_mass

        gearbox_mass = self.Motor_case_mass + self.carrier_mass + self.sun_mass + (self.planet_mass * self.num_planet) + self.ring_mass + self.sec_carrier_mass + self.bearing_retainer_mass +0.02
        self.gearbox_mass = gearbox_mass
        Actuator_mass = (self.motorMassKG 
                         + self.Motor_case_mass  
                         + self.carrier_mass 
                         + self.sun_mass 
                         + self.sec_carrier_mass 
                         + self.planet_mass * numPlanet 
                         + self.bearing_mass 
                         + self.ring_mass
                         + self.bearing_retainer_mass
                         )

        return Actuator_mass
    
    def check_type2_geometry(self):
            """Returns True if the geometry is valid, False if it fails the condition."""
            # Refresh variables to get the current gear dimensions for this loop
            self.setVariables() 
            
            # --- CONSTRAINT 1: Carrier must fit inside Stator ID ---
            required_diameter = (self.planet_shaft_dia + 
                                (self.planet_shaft_step_offset * 2) + 
                                self.carrier_PCD + 
                                (self.standard_clearance_1_5mm * 2))
            condition_1_passes = (required_diameter <= self.motor.Stator_ID)
            
            # --- CONSTRAINT 2: Sun gear must fit inside the secondary carrier bearing ---
            sun_gear_dia = self.Ns * self.module
            max_allowable_sun_dia = self.sun_sec_carrier_bearing_ID - self.loose_clearance_3DP
            condition_2_passes = (sun_gear_dia <= max_allowable_sun_dia)
            
            # --- FINAL CHECK ---
            # The geometry is only valid if BOTH conditions are true
            if condition_1_passes and condition_2_passes:
                return True
            else:
                return False


#========================================================================
# Class: Actuator Optimization
#========================================================================
class optimizationSingleStageActuator:
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
                 NUM_TEETH_PLANET_MIN = 20,
                 GEAR_RATIO_MIN       = 5,
                 GEAR_RATIO_MAX       = 12,
                 GEAR_RATIO_STEP      = 1):
        
        self.K_Mass               = K_Mass
        self.K_Eff                = K_Eff
        self.K_Width              = K_Width
        self.MODULE_MIN           = MODULE_MIN
        self.MODULE_MAX           = MODULE_MAX
        self.NUM_PLANET_MIN       = NUM_PLANET_MIN
        self.NUM_PLANET_MAX       = NUM_PLANET_MAX
        self.NUM_TEETH_SUN_MIN    = NUM_TEETH_SUN_MIN
        self.NUM_TEETH_PLANET_MIN = NUM_TEETH_PLANET_MIN
        self.GEAR_RATIO_MIN       = GEAR_RATIO_MIN
        self.GEAR_RATIO_MAX       = GEAR_RATIO_MAX
        self.GEAR_RATIO_STEP      = GEAR_RATIO_STEP

        self.Cost                         = 100000
        self.totalGearboxesWithRequiredGR = 0
        self.totalFeasibleGearboxes       = 0
        self.cntrBeforeCons               = 0
        self.iter                         = 0
        self.gearRatioIter                = self.GEAR_RATIO_MIN
        self.design_params                = design_params
        self.gear_standard_parameters     = gear_standard_paramaeters
        self.gearRatioReq                 = 0.0
        self.UsePSCasVariable             = 0 

    def printOptimizationParameters(self, Actuator=singleStagePlanetaryActuator, log=1, csv=0):
        if log:
            print("--------------------Motor Parameters--------------------")
            print("maxMotorAngVelRPM:       ", Actuator.motor.maxMotorAngVelRPM)
            print("maxMotorAngVelRadPerSec: ", Actuator.motor.maxMotorAngVelRadPerSec)
            print("maxMotorTorque:          ", Actuator.motor.maxMotorTorque)
            print("maxMotorPower:           ", Actuator.motor.maxMotorPower)
            print("motorMass:               ", Actuator.motor.massKG)
            print("motorDia:                ", Actuator.motor.motorDiaMM)
            print("motorLength:             ", Actuator.motor.motorLengthMM)
            print("\n--------------Planetary Gearbox Parameters--------------")
            print("maxGearAllowableStressMPa: ", Actuator.planetaryGearbox.maxGearAllowableStressMPa)
            print("\n-----------Gear strength and size parameters------------")
            print("FOS:                     ", Actuator.FOS)
            print("serviceFactor:           ", Actuator.serviceFactor)
            print("stressAnalysisMethodName:", Actuator.stressAnalysisMethodName)
            print("maxGearBoxDia:           ", Actuator.maxGearboxDiameter)
            print("\n-----------------Optimization Parameters-----------------")
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
            print("maxMotorAngVelRPM,maxMotorAngVelRadPerSec,maxMotorTorque,maxMotorPower,motorMass,motorDia,motorLength")
            print(f"{Actuator.motor.maxMotorAngVelRPM},{Actuator.motor.maxMotorAngVelRadPerSec},{Actuator.motor.maxMotorTorque},{Actuator.motor.maxMotorPower},{Actuator.motor.massKG},{Actuator.motor.motorDiaMM},{Actuator.motor.motorLengthMM}")
            print("\nGear strength and size parameters:")
            print("FOS,serviceFactor,stressAnalysisMethodName,maxGearBoxDia,maxGearAllowableStressMPa")
            print(f"{Actuator.FOS},{Actuator.serviceFactor},{Actuator.stressAnalysisMethodName},{Actuator.maxGearboxDiameter},{Actuator.planetaryGearbox.maxGearAllowableStressMPa}")
            print("\nOptimization Parameters:")            
            print("K_mass, K_Eff, K_Width, MODULE_MIN, MODULE_MAX, NUM_PLANET_MIN, NUM_PLANET_MAX, NUM_TEETH_SUN_MIN, NUM_TEETH_PLANET_MIN, GEAR_RATIO_MIN, GEAR_RATIO_MAX, GEAR_RATIO_STEP")
            print(f"{self.K_Mass},{self.K_Eff},{self.K_Width},{self.MODULE_MIN},{self.MODULE_MAX},{self.NUM_PLANET_MIN},{self.NUM_PLANET_MAX},{self.NUM_TEETH_SUN_MIN},{self.NUM_TEETH_PLANET_MIN},{self.GEAR_RATIO_MIN},{self.GEAR_RATIO_MAX},{self.GEAR_RATIO_STEP}")

    def printOptimizationResults(self, Actuator=singleStagePlanetaryActuator, log=1, csv=0):
        Actuator.setVariables()
        if log:
            print("Iteration: ", self.iter)
            Actuator.printParametersLess()
            Actuator.printVolumeAndMassParameters()
            eff = round(Actuator.planetaryGearbox.getEfficiency(), 3)
            if self.UsePSCasVariable == 1: 
                eff  = round(self.sspgOpt.getEfficiency(Var=False), 3)
                print("Efficiency with PSC", eff)
            print("\nCost:", self.Cost)
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
            mass       = round(Actuator.getMassKG_3DP(), 3)
            eff        = round(Actuator.planetaryGearbox.getEfficiency(), 3)
            
            if self.UsePSCasVariable == 1: 
                eff  = round(self.sspgOpt.getEfficiency(Var=False), 3)
            
            peakTorque = round(Actuator.motor.getMaxMotorTorque()*Actuator.planetaryGearbox.gearRatio(), 3)
            Cost       = self.cost(Actuator = Actuator) 
            Torque_Density = peakTorque / mass
            Outer_Bearing_mass = getattr(Actuator, 'bearing_mass', 0)
            Actuator_width = getattr(Actuator, 'actuator_width', 0)
            print(f"{iter},{gearRatio},{module},{Ns},{Np},{Nr},{numPlanet},{fwSunMM},{fwPlanetMM},{fwRingMM},{mass},{eff},{peakTorque},{Cost},{Torque_Density},{Outer_Bearing_mass},{Actuator_width}")

    def optimizeActuator(self, Actuator=singleStagePlanetaryActuator, UsePSCasVariable=0, log=0, csv=1, gearRatioReq=0, printOptParams=1):
        self.UsePSCasVariable = UsePSCasVariable
        totalTime = 0
        opt_parameters = None 
        self.gearRatioReq = gearRatioReq
        if UsePSCasVariable == 0:
            totalTime, opt_parameters = self.optimizeActuatorWithoutPSC(Actuator=Actuator, log=log, csv=csv, printOptParams=printOptParams)
        elif UsePSCasVariable == 1:
            totalTime = self.optimizeActuatorWithPSC(Actuator=Actuator, log=log, csv=csv, printOptParams=printOptParams)
        else:
            print("ERROR: \"UsePSCasVariable\" can be either 0 or 1")
        
        return totalTime, opt_parameters

    def optimizeActuatorWithoutPSC(self, Actuator=singleStagePlanetaryActuator, log=1, csv=0, printOptParams=1): 
        startTime = time.time()
        opt_parameters = None 
        if csv and log:
            log, csv = 0, 1
        elif not csv and not log:
            log, csv = 0, 1

        # Generates routing matching user's VS Code screenshot: "results/results_BruteForce_{motor_name}/"
        output_dir = os.path.join(os.path.dirname(__file__), 'results', f'results_BruteForce_{Actuator.motor.motorName}')
        os.makedirs(output_dir, exist_ok=True)
        
        if csv:
            main_fileName = os.path.join(output_dir, f"SSPG_BRUTEFORCE_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}_{Actuator.insspg_type}.csv")
            param_fileName = os.path.join(output_dir, f"SSPG_BRUTEFORCE_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}_{Actuator.insspg_type}_Motor_Params.csv")
        elif log:
            main_fileName = os.path.join(output_dir, f"SSPG_BRUTEFORCE_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}_{Actuator.insspg_type}_LOG.txt")
            param_fileName = None
            
        # Writes the Motor_Params CSV
        if csv and printOptParams:
            with open(param_fileName, "w") as param_file:
                sys.stdout = param_file
                self.printOptimizationParameters(Actuator, log, csv)
            sys.stdout = sys.__stdout__

        with open(main_fileName, "w") as file1:
            sys.stdout = file1
            if log and printOptParams:
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
            elif csv:
                print("iter, gearRatio, module, Ns, Np, Nr, numPlanet, fwSunMM, fwPlanetMM, fwRingMM, mass, eff, peakTorque, Cost, Torque_Density, Outer_Bearing_mass, Actuator_width")

            while self.gearRatioIter <= self.GEAR_RATIO_MAX:
                opt_done = 0
                self.iter = 0
                self.Cost = 100000
                MinCost = self.Cost
                Actuator.planetaryGearbox.setModule(self.MODULE_MIN)
                while Actuator.planetaryGearbox.module <= self.MODULE_MAX:
                    Actuator.planetaryGearbox.setNs(self.NUM_TEETH_SUN_MIN) 
                    while 2*Actuator.planetaryGearbox.getPCRadiusSunMM() <= Actuator.maxGearboxDiameter:
                        Actuator.planetaryGearbox.setNp(self.NUM_TEETH_PLANET_MIN) 
                        while 2*Actuator.planetaryGearbox.getPCRadiusPlanetMM() <= Actuator.maxGearboxDiameter/2:
                            Actuator.planetaryGearbox.setNr(2*Actuator.planetaryGearbox.Np + Actuator.planetaryGearbox.Ns) 
                            if 2*Actuator.planetaryGearbox.getPCRadiusRingMM() <= Actuator.maxGearboxDiameter:
                                Actuator.planetaryGearbox.setNumPlanet(self.NUM_PLANET_MIN) 
                                while Actuator.planetaryGearbox.numPlanet <= self.NUM_PLANET_MAX:
                                    self.cntrBeforeCons += 1
 
                                    # 1. Base constraints all gearboxes must pass
                                    passes_base = (Actuator.planetaryGearbox.geometricConstraint() and 
                                                   Actuator.planetaryGearbox.meshingConstraint() and 
                                                   Actuator.planetaryGearbox.noPlanetInterferenceConstraint())
                                        
                                    # 2. Type 2 specific geometry constraint
                                    passes_type2 = True
                                    if Actuator.insspg_type == "insspg_type_2":
                                        passes_type2 = Actuator.check_type2_geometry()

                                    # 3. Proceed only if both are true
                                    if passes_base and passes_type2:
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
                                                
                                                total_mass = Actuator.getMassKG_3DP()
                                                motor_mass = Actuator.motor.getMassKG()

                                                opt_parameters = [
                                                    Actuator.planetaryGearbox.gearRatio(),        # [0] GR
                                                    Actuator.planetaryGearbox.numPlanet,          # [1] n_p
                                                    Actuator.planetaryGearbox.Ns,                 # [2] Ns
                                                    Actuator.planetaryGearbox.Np,                 # [3] Np
                                                    Actuator.planetaryGearbox.Nr,                 # [4] Nr
                                                    Actuator.planetaryGearbox.module,             # [5] m
                                                    total_mass,                                   # [6] Total Actuator mass
                                                    getattr(Actuator, 'bearing_mass', 0),         # [7] Bearings
                                                    getattr(Actuator, 'sun_mass', 0),             # [8] Sun Gear
                                                    getattr(Actuator, 'planet_mass', 0),          # [9] Planets
                                                    getattr(Actuator, 'ring_mass', 0),            # [10] Ring Gear (or ring_mass)
                                                    getattr(Actuator, 'carrier_mass', 0),         # [11] Main Carrier
                                                    getattr(Actuator, 'sec_carrier_mass', 0),     # [12] Sec Carrier
                                                    getattr(Actuator, 'Motor_case_mass', 0),      # [13] Motor Casing
                                                    getattr(Actuator, 'gearbox_mass', 0),         # [14] Total except motor and bearing
                                                    getattr(Actuator, 'bearing_retainer_mass', 0) # [15] NEW: Bearing Retainer Mass
                                                ]
                                                  
                                                opt_planetaryGearbox = singleStagePlanetaryGearbox(design_params             = self.design_params,
                                                                                                   gear_standard_parameters  = self.gear_standard_parameters,
                                                                                                   Ns                        = Actuator.planetaryGearbox.Ns,
                                                                                                   Np                        = Actuator.planetaryGearbox.Np,
                                                                                                   Nr                        = Actuator.planetaryGearbox.Nr, 
                                                                                                   module                    = Actuator.planetaryGearbox.module,     
                                                                                                   numPlanet                 = Actuator.planetaryGearbox.numPlanet,
                                                                                                   fwSunMM                   = Actuator.planetaryGearbox.fwSunMM,    
                                                                                                   fwPlanetMM                = Actuator.planetaryGearbox.fwPlanetMM, 
                                                                                                   fwRingMM                  = Actuator.planetaryGearbox.fwRingMM,   
                                                                                                   maxGearAllowableStressMPa = Actuator.planetaryGearbox.maxGearAllowableStressMPa, 
                                                                                                   densityGears              = Actuator.planetaryGearbox.densityGears,      
                                                                                                   densityStructure          = Actuator.planetaryGearbox.densityStructure) 

                                                opt_actuator = singleStagePlanetaryActuator(design_params            = self.design_params,
                                                                                            motor                    = Actuator.motor, 
                                                                                            motor_driver_params      = Actuator.motor_driver_params,
                                                                                            planetaryGearbox         = opt_planetaryGearbox, 
                                                                                            FOS                      = Actuator.FOS, 
                                                                                            serviceFactor            = Actuator.serviceFactor, 
                                                                                            maxGearboxDiameter       = Actuator.maxGearboxDiameter, 
                                                                                            stressAnalysisMethodName = Actuator.stressAnalysisMethodName,
                                                                                            insspg_type              = Actuator.insspg_type) # <--- THE Link used only for actuator type
                                                opt_actuator.updateFacewidth()
                                                opt_actuator.getMassKG_3DP()

                                    Actuator.planetaryGearbox.setNumPlanet(Actuator.planetaryGearbox.numPlanet + 1)
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

            endTime = time.time()
            totalTime = endTime - startTime
            if(printOptParams):
                print("\nRunning Time (sec): ", totalTime) 

        sys.stdout = sys.__stdout__
        return totalTime, opt_parameters

    def optimizeActuatorWithPSC(self, Actuator=singleStagePlanetaryActuator, log=1, csv=0, printOptParams=1):
            startTime = time.time()
            opt_parameters = []
            if csv and log:
                log, csv = 0, 1
            elif not csv and not log:
                log, csv = 0, 1

            # Generates routing matching user's VS Code screenshot: "results/results_BiLevel_{motor_name}/"
            output_dir = os.path.join(os.path.dirname(__file__), 'results', f'results_BiLevel_{Actuator.motor.motorName}')
            os.makedirs(output_dir, exist_ok=True)
            
            if csv:
                main_fileName = os.path.join(output_dir, f"SSPG_BILEVEL_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}.csv")
                param_fileName = os.path.join(output_dir, f"SSPG_BILEVEL_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}_Motor_Params.csv")
            elif log:
                main_fileName = os.path.join(output_dir, f"SSPG_BILEVEL_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}_LOG.txt")
                param_fileName = None
                
            # Writes the Motor_Params CSV
            if csv and printOptParams:
                with open(param_fileName, "w") as param_file:
                    sys.stdout = param_file
                    self.printOptimizationParameters(Actuator, log, csv)
                sys.stdout = sys.__stdout__

            with open(main_fileName, "w") as file1:
                sys.stdout = file1
                if log and printOptParams:
                    self.printOptimizationParameters(Actuator, log, csv)
                    print(" ")

                if log:
                    print("\n*****************************************************************")
                    print("FOR MINIMUM GEAR RATIO ", self.gearRatioIter)
                    print("*****************************************************************")
                elif csv:
                    print("\niter, gearRatio, module, Ns, Np, Nr, numPlanet, fwSunMM, fwPlanetMM, fwRingMM, PSCs, PSCp, PSCr, CD_SP, CD_PR, mass, eff, peakTorque, Cost, Torque_Density")
                
                while self.gearRatioIter <= self.GEAR_RATIO_MAX:
                    opt_done  = 0
                    self.iter = 0
                    self.Cost = 100000
                    MinCost   = self.Cost
                    Actuator.planetaryGearbox.setModule(self.MODULE_MIN)
                    while Actuator.planetaryGearbox.module <= self.MODULE_MAX:
                        Actuator.planetaryGearbox.setNs(self.NUM_TEETH_SUN_MIN) 
                        while 2*Actuator.planetaryGearbox.getPCRadiusSunMM() <= Actuator.maxGearboxDiameter:
                            Actuator.planetaryGearbox.setNp(self.NUM_TEETH_PLANET_MIN) 
                            while 2*Actuator.planetaryGearbox.getPCRadiusPlanetMM() <= Actuator.maxGearboxDiameter/2:
                                Actuator.planetaryGearbox.setNr(2*Actuator.planetaryGearbox.Np + Actuator.planetaryGearbox.Ns) 
                                if 2*Actuator.planetaryGearbox.getPCRadiusRingMM() <= Actuator.maxGearboxDiameter:
                                    Actuator.planetaryGearbox.setNumPlanet(self.NUM_PLANET_MIN) 
                                    while Actuator.planetaryGearbox.numPlanet <= self.NUM_PLANET_MAX:
                                        self.cntrBeforeCons += 1
                                        
                                        # 1. Base constraints all gearboxes must pass
                                        passes_base = (Actuator.planetaryGearbox.geometricConstraint() and 
                                                       Actuator.planetaryGearbox.meshingConstraint() and 
                                                       Actuator.planetaryGearbox.noPlanetInterferenceConstraint())
                                            
                                        # 2. Type 2 specific geometry constraint
                                        passes_type2 = True
                                        if Actuator.insspg_type == "insspg_type_2":
                                            passes_type2 = Actuator.check_type2_geometry()

                                        # 3. Proceed only if both are true
                                        if passes_base and passes_type2:
                                            self.totalFeasibleGearboxes += 1
                                            
                                            if (Actuator.planetaryGearbox.gearRatio() >= self.gearRatioIter):
                                                self.totalGearboxesWithRequiredGR += 1
                                                Actuator.updateFacewidth()

                                                effActuator = Actuator.planetaryGearbox.getEfficiency()
                                                massActuator = Actuator.getMassKG_3DP()

                                                self.Cost = (self.K_Mass * massActuator) + (self.K_Eff * effActuator)
                                                
                                                if self.Cost <= MinCost:
                                                    MinCost    = self.Cost
                                                    self.iter += 1
                                                    opt_done   = 1
                                                    Actuator.genEquationFile()
                                                    opt_parameters = [Actuator.planetaryGearbox.gearRatio(),
                                                                      Actuator.planetaryGearbox.numPlanet,
                                                                      Actuator.planetaryGearbox.Ns,
                                                                      Actuator.planetaryGearbox.Np,
                                                                      Actuator.planetaryGearbox.Nr,
                                                                      Actuator.planetaryGearbox.module]
                                                    
                                                    opt_planetaryGearbox = singleStagePlanetaryGearbox(design_params             = self.design_params,
                                                                                                       gear_standard_parameters  = self.gear_standard_parameters,
                                                                                                       Ns                        = Actuator.planetaryGearbox.Ns,
                                                                                                       Np                        = Actuator.planetaryGearbox.Np,
                                                                                                       Nr                        = Actuator.planetaryGearbox.Nr, 
                                                                                                       module                    = Actuator.planetaryGearbox.module,     
                                                                                                       numPlanet                 = Actuator.planetaryGearbox.numPlanet,
                                                                                                       fwSunMM                   = Actuator.planetaryGearbox.fwSunMM,    
                                                                                                       fwPlanetMM                = Actuator.planetaryGearbox.fwPlanetMM, 
                                                                                                       fwRingMM                  = Actuator.planetaryGearbox.fwRingMM,   
                                                                                                       maxGearAllowableStressMPa = Actuator.planetaryGearbox.maxGearAllowableStressMPa, 
                                                                                                       densityGears              = Actuator.planetaryGearbox.densityGears,      
                                                                                                       densityStructure          = Actuator.planetaryGearbox.densityStructure) 

                                                    opt_actuator = singleStagePlanetaryActuator(design_params            = self.design_params,
                                                                                                motor                    = Actuator.motor, 
                                                                                                planetaryGearbox         = opt_planetaryGearbox, 
                                                                                                FOS                      = Actuator.FOS, 
                                                                                                serviceFactor            = Actuator.serviceFactor, 
                                                                                                maxGearboxDiameter       = Actuator.maxGearboxDiameter,  
                                                                                                stressAnalysisMethodName = "Lewis",
                                                                                                insspg_type              = Actuator.insspg_type) 
                                                    opt_actuator.updateFacewidth()
                                                    opt_actuator.getMassKG_3DP()

                                        Actuator.planetaryGearbox.setNumPlanet(Actuator.planetaryGearbox.numPlanet + 1)
                                Actuator.planetaryGearbox.setNp(Actuator.planetaryGearbox.Np + 1)
                        Actuator.planetaryGearbox.setNs(Actuator.planetaryGearbox.Ns + 1)
                    Actuator.planetaryGearbox.setModule(Actuator.planetaryGearbox.module + 0.100)
                if (opt_done == 1):
                    try:
                        self.sspgOpt = optimal_continuous_PSC_sspg(GEAR_RATIO_MIN = opt_parameters[0],
                                                                   numPlanet = opt_parameters[1],
                                                                   Ns = opt_parameters[2],
                                                                   Np = opt_parameters[3],
                                                                   Nr = opt_parameters[4],
                                                                   M  = opt_parameters[5] * 10) 
                        _, calc_centerDistForManufacturing = self.sspgOpt.solve()
                        self.sspgOpt.solve(optimizeForManufacturing  = True, 
                                           centerDistForManufacturing = calc_centerDistForManufacturing)
                    except NameError:
                        pass
                    self.printOptimizationResults(opt_actuator, log, csv)
                self.gearRatioIter += self.GEAR_RATIO_STEP

                if log:
                    print("Number of iterations: ", self.cntrBeforeCons)
                    print("Total Feasible Gearboxes:", self.totalFeasibleGearboxes)
                    print("Total Gearboxes with required Gear Ratio:", self.totalGearboxesWithRequiredGR)
                    print("*****************************************************************")

            endTime = time.time()
            totalTime = endTime - startTime
            print("\nRunning Time (sec): ", totalTime) 

            sys.stdout = sys.__stdout__
            return totalTime

    def cost(self, Actuator=singleStagePlanetaryActuator):
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