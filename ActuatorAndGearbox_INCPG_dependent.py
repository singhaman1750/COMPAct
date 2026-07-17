import re
import os
import math
import numpy as np
import sys
import time

from CommonComponents import material, bearings_discrete, nuts_and_bolts_dimensions, motor_driver, motor_frameless_inrunner_suyash as motor

class inrunnerCompoundPlanetaryGearbox:
    def __init__(self,
                 design_parameters,
                 gear_standard_parameters,
                 Ns                        = 20,
                 NpBig                     = 20,
                 NpSmall                   = 20,
                 Nr                        = 60,
                 numPlanet                 =  2,
                 moduleBig                 = 0.8,
                 moduleSmall               = 0.8,
                 fwSunMM                   = 5.0,
                 fwPlanetBigMM             = 5.0,
                 fwPlanetSmallMM           = 5.0,
                 fwRingMM                  = 5.0,
                 densityGears              = 7850.0,
                 densityStructure          = 2710.0,
                 maxGearAllowableStressMPa = 400.0,
                 densityAluminum           = 2170):
        
        self.Ns                        = Ns
        self.NpBig                     = NpBig
        self.NpSmall                   = NpSmall
        self.Nr                        = Nr
        self.numPlanet                 = numPlanet
        self.moduleBig                 = moduleBig
        self.moduleSmall               = moduleSmall
        self.densityGears              = densityGears
        self.densityStructure          = densityStructure
        self.densityAluminum           = densityAluminum
        self.fwSunMM                   = fwSunMM
        self.fwPlanetBigMM             = fwPlanetBigMM
        self.fwPlanetSmallMM           = fwPlanetSmallMM
        self.fwRingMM                  = fwRingMM
        self.maxGearAllowableStressMPa = maxGearAllowableStressMPa # MPa
        self.maxGearAllowableStressPa  = maxGearAllowableStressMPa * 10**6 # Pa

        # Carrier Parameters for the No planet Interference constraint
        self.mu               = gear_standard_parameters["coefficientOfFriction"] # 0.3
        self.pressureAngleDEG = gear_standard_parameters["pressureAngleDEG"]      # 20  # deg

        # self.carrierWidthMM    = design_parameters["carrierWidthMM"]    # carrierWidthMM
        self.ringRadialWidthMM = design_parameters["ringRadialWidthMM"] # ringRadialWidth

        self.planetMinDistanceMM          = design_parameters["planetMinDistanceMM"]          # 5.0 # mm
        self.sCarrierExtrusionDiaMM       = design_parameters["sCarrierExtrusionDiaMM"]       # 8.0 # mm
        self.sCarrierExtrusionClearanceMM = design_parameters["sCarrierExtrusionClearanceMM"] # 1.0 # mm

    def geometricConstraint(self):
        return ((self.Ns + self.NpBig) * self.moduleBig == (self.Nr - self.NpSmall) * self.moduleSmall)
        
    def meshingConstraint(self):
        # TODO: This is a conservative approach. Later make it more general
        return ((self.Ns % self.numPlanet == 0) and (self.Nr % self.numPlanet == 0))
    
    def noPlanetInterferenceConstraint_old(self):
        return 2*(self.Ns + self.NpBig)*self.moduleBig*np.sin(np.pi/self.numPlanet) >= 2*self.moduleBig*self.NpBig + self.planetMinDistanceMM

    def noPlanetInterferenceConstraint(self):
        module1   = self.moduleBig  # Module of the gear
        module2   = self.moduleSmall  # Module of the gear
        Ns        = self.Ns
        Np1       = self.NpBig
        Np2       = self.NpSmall
        Nr        = self.Nr
        numPlanet = self.numPlanet
        
        Rs                        = (Ns)  * (module1) / 2
        Rp1                       = (Np1) * (module1) / 2
        sCarrierExtrusionRadiusMM = self.sCarrierExtrusionDiaMM * 0.5
        return 2 * (Rs + Rp1) * np.sin(np.pi/(2 * numPlanet)) - Rp1 - sCarrierExtrusionRadiusMM >= self.sCarrierExtrusionClearanceMM
    
    def getMassKG(self):
        # Volume of the Sun gear
        fwSunM            = (self.fwSunMM / 1000.0)
        fwPlanetBigM      = (self.fwPlanetBigMM / 1000.0)
        fwPlanetSmallM    = (self.fwPlanetSmallMM / 1000.0)
        fwRingM           = (self.fwRingMM / 1000.0)
        carrierWidthM     = (self.carrierWidthMM / 1000.0)
        sunVolume         = np.pi * fwSunM * (self.getPCRadiusSunM()**2)
        planetBigVolume   = np.pi * fwPlanetBigM * (self.getPCRadiusPlanetBigM()**2)
        planetSmallVolume = np.pi * fwPlanetSmallM * (self.getPCRadiusPlanetSmallM()**2)
        ringVolume        = np.pi * fwRingM * (self.getOuterRadiusRingM()**2 - self.getPCRadiusRingM()**2)
        carrierVolume     = 2 * np.pi * carrierWidthM * (self.getCarrierRadiusM()**2)
        
        # Total mass of the compound planetary gearbox
        combinedGearVolume = sunVolume + (self.numPlanet * planetBigVolume) + planetSmallVolume + ringVolume
        TotalMassKG        = (combinedGearVolume * self.densityGears + carrierVolume * self.densityStructure)
        return TotalMassKG
    
    def gearRatio(self):
        # Radii of the sun, planet, and ring gears
        Rs = self.Ns * self.moduleBig
        RpBig = self.NpBig * self.moduleBig
        RpSmall = self.NpSmall * self.moduleSmall
        Rr = self.Nr * self.moduleSmall

        GR = ((Rs + RpBig) * (RpSmall + RpBig)) / (Rs * RpSmall)
        return GR

    #------------------------------
    # Utility Functions
    #------------------------------
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
        return self.pressureAngleDEG * np.pi / 180  # Pressure angle in radians
 
    def getWorkingPressureAngle(self):
        module1 = self.moduleBig  # Module of the gear
        module2 = self.moduleSmall  # Module of the gear
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr      = self.Nr
        xs      = 0
        xp1     = 0
        xp2     = 0
        xr      = 0
        
        #---------------------------------
        # Pressure Angle
        #---------------------------------
        alpha = self.getPressureAngleRad()

        #---------------------------------
        # Working pressure angle
        #---------------------------------
        # Sun-Planet
        inv_alpha_w_sunPlanet = 2*np.tan(alpha)*((xs + xp1)/(Ns + Np1)) + self.involute(alpha)
        alpha_w_sunPlanet = self.inverse_involute(inv_alpha_w_sunPlanet)

        # Planet-Ring
        inv_alpha_w_planetRing = 2*np.tan(alpha)*((xr-xp2)/(Nr - Np2)) + self.involute(alpha)
        alpha_w_planetRing = self.inverse_involute(inv_alpha_w_planetRing)

        return alpha_w_sunPlanet, alpha_w_planetRing

    def getCenterDistModificationCoeff(self):
        module1 = self.moduleBig  # Module of the gear
        module2 = self.moduleSmall  # Module of the gear
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr      = self.Nr

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
        y_sunPlanet  = ((Ns + Np1) / 2) * ((np.cos(alpha) / np.cos(alpha_w_sunPlanet)) - 1)
        y_planetRing = ((Nr - Np2) / 2) * ((np.cos(alpha) / np.cos(alpha_w_planetRing)) - 1)

        return y_sunPlanet, y_planetRing

    def getCenterDistance(self):
        module1 = self.moduleBig  # Module of the gear
        module2 = self.moduleSmall  # Module of the gear
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr      = self.Nr
    
        #-------------------------------
        # Centre distance modification coefficient
        #-------------------------------
        y_sunPlanet, y_planetRing = self.getCenterDistModificationCoeff()

        #-------------------------------
        # Centre distance
        #-------------------------------
        centerDist_sunPlanet = ((Ns + Np1)/2  + y_sunPlanet)* module1
        centerDist_planetRing = ((Nr - Np2)/2  + y_planetRing)* module2

        return centerDist_sunPlanet, centerDist_planetRing

    def getBaseDia(self):
        module1 = self.moduleBig  # Module of the gear
        module2 = self.moduleSmall  # Module of the gear
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr      = self.Nr

        # Pressure Angle
        alpha = self.getPressureAngleRad() # Rad

        # Reference Diameter
        D_sun     = module1 * Ns # Sun's reference diameter
        D_planet1 = module1 * Np1 # Planet's reference diameter
        D_planet2 = module2 * Np2 # Planet's reference diameter
        D_ring    = module2 * Nr # Ring's reference diameter

        # Base Diameter
        D_b_sun     = D_sun * np.cos(alpha)
        D_b_planet1 = D_planet1 * np.cos(alpha)
        D_b_planet2 = D_planet2 * np.cos(alpha)
        D_b_ring    = D_ring * np.cos(alpha)

        return D_b_sun, D_b_planet1, D_b_planet2, D_b_ring
 
    def getTipCircleDia(self):
        module1 = self.moduleBig  # Module of the gear
        module2 = self.moduleSmall  # Module of the gear
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr      = self.Nr
        xs      = 0
        xp1     = 0
        xp2     = 0
        xr      = 0
        
        #----------------------------
        # Pressure Angle
        #----------------------------
        alpha = self.getPressureAngleRad() # Rad

        #----------------------------
        # Reference Diameter
        #----------------------------
        D_sun     = module1 * Ns # Sun's reference diameter
        D_planet1 = module1 * Np1 # Planet's reference diameter
        D_planet2 = module2 * Np2 # Planet's reference diameter
        D_ring    = module2 * Nr # Ring's reference diameter

        #----------------------------
        # Center Distance Modification Coefficient
        #----------------------------
        y_sunPlanet, y_planetRing = self.getCenterDistModificationCoeff()

        #----------------------------
        # Tip circle diameter
        #----------------------------
        # Sun
        D_a_sun = D_sun + 2 * module1 * (1 + y_sunPlanet - xp1)

        # Planet
        D_a_planet1  = D_planet1 + 2 * module1 * (1 + self.quadratic_min((y_sunPlanet - xs), xp1))  
        D_a_planet2  = D_planet2 + 2 * module2 * (1 + self.quadratic_min((y_planetRing - xs),xp2)) 
        # D_a_planet = D_planet + 2 * module * (1 + xp) 
        
        # Ring
        D_a_ring = D_ring - 2 * module2 * (1 - xr)
        
        return D_a_sun, D_a_planet1, D_a_planet2, D_a_ring
 
    def getTipPressureAngle(self):
        module1 = self.moduleBig  # Module of the gear
        module2 = self.moduleSmall  # Module of the gear
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr      = self.Nr

        alpha = self.getPressureAngleRad() # Pressure Angle (Rad)
        D_b_sun, D_b_planet1, D_b_planet2, D_b_ring = self.getBaseDia() # Base Diameter
        D_a_sun, D_a_planet1, D_a_planet2, D_a_ring = self.getTipCircleDia() # Tip Circle Diameter

        #----------------------------
        # Tip Pressure angle
        #----------------------------
        alpha_a_sun     = np.arccos(D_b_sun / D_a_sun)
        alpha_a_planet1 = np.arccos(D_b_planet1/D_a_planet1)
        alpha_a_planet2 = np.arccos(D_b_planet2/D_a_planet2)
        alpha_a_ring    = np.arccos(D_b_ring / D_a_ring)

        return alpha_a_sun, alpha_a_planet1, alpha_a_planet2, alpha_a_ring

    def getErrorTipCircleDia_planet(self):
        module1 = self.moduleBig  # Module of the gear
        module2 = self.moduleSmall  # Module of the gear
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr      = self.Nr
        xs      = 0
        xp1     = 0
        xp2     = 0
        xr      = 0
        
        # Centre distance modification coefficient
        y_sunPlanet, y_planetRing = self.getCenterDistModificationCoeff()

        # Tip Circle Diameter
        _, D_a_planet1_quadMin, D_a_planet2_quadMin, _ = self.getTipCircleDia()
        D_a_planet1_actMin = module1 * Np1 + 2 * module1 * (1 + np.minimum((y_sunPlanet - xs),xp1)) # TODO: How will we implement min function 
        D_a_planet2_actMin = module2 * Np2 + 2 * module2 * (1 + np.minimum((y_planetRing - xs),xp2)) # TODO: How will we implement min function 

        return np.abs(D_a_planet1_quadMin - D_a_planet1_actMin), np.abs(D_a_planet2_quadMin - D_a_planet2_actMin)

    #-----------------------------------------
    # Contact Ratio
    #-----------------------------------------
    def contactRatio_sunPlanet(self):
        module1 = self.moduleBig  # Module of the gear
        module2 = self.moduleSmall  # Module of the gear
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr      = self.Nr

        # Working pressure angle
        alpha_w_sunPlanet, _ = self.getWorkingPressureAngle()

        # Tip pressure angle
        alpha_a_sun, alpha_a_planet1, _, _ = self.getTipPressureAngle()

        # Contact ratio
        Approach_CR_sunPlanet = (Np1 / (2 * np.pi)) * (np.tan(alpha_a_planet1) - np.tan(alpha_w_sunPlanet)) # Approach contact ratio
        Recess_CR_sunPlanet   =  (Ns / (2 * np.pi)) * (np.tan(alpha_a_sun) - np.tan(alpha_w_sunPlanet))    # Recess contact ratio

        # write the final formula
        CR_sunPlanet = Approach_CR_sunPlanet + Recess_CR_sunPlanet

        return Approach_CR_sunPlanet, Recess_CR_sunPlanet, CR_sunPlanet

    def contactRatio_planetRing(self):
        module1 = self.moduleBig  # Module of the gear
        module2 = self.moduleSmall  # Module of the gear
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr      = self.Nr

        # Working pressure angle
        _, alpha_w_planetRing = self.getWorkingPressureAngle()

        # Tip pressure angle
        _, _, alpha_a_planet2, alpha_a_ring = self.getTipPressureAngle()

        # Contact ratio
        Approach_CR_planetRing = -(Nr / (2 * np.pi)) * (np.tan(alpha_a_ring) - np.tan(alpha_w_planetRing)) # Approach contact ratio
        Recess_CR_planetRing   =   Np2 / (2 * np.pi) * (np.tan(alpha_a_planet2) - np.tan(alpha_w_planetRing)) # Recess contact ratio
        
        # Contact Ratio
        CR_planetRing = Approach_CR_planetRing + Recess_CR_planetRing

        return Approach_CR_planetRing, Recess_CR_planetRing, CR_planetRing

    #-------------------------------------------
    # Efficiency Calculation
    #-------------------------------------------
    def getEfficiency(self):
        # TODO: VERIFY THIS EFFICIENCY FORMULA
        module1 = self.moduleBig  # Module of the gear
        module2 = self.moduleSmall  # Module of the gear
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr      = self.Nr

        # Contact ratio
        eps_sunPlanetA, eps_sunPlanetR, _ = self.contactRatio_sunPlanet()
        eps_planetRingA, eps_planetRingR, _ = self.contactRatio_planetRing()
        
        # Contact-Ratio-Factor
        epsilon_sunPlanet = eps_sunPlanetA**2 + eps_sunPlanetR**2 - eps_sunPlanetA - eps_sunPlanetR + 1 
        epsilon_planetRing = eps_planetRingA**2 + eps_planetRingR**2 - eps_planetRingA - eps_planetRingR + 1 
        
        # Efficiency
        eff_SP = 1 - self.mu * np.pi * ((1 / Np1) + (1 / Ns)) * epsilon_sunPlanet
        eff_PR = 1 - self.mu * np.pi * ((1 / Np2) - (1 / Nr)) * epsilon_planetRing

        Numerator   = (Ns * Np2 + eff_SP * eff_PR * Np1 * Nr)
        Denominator = (Ns + Np1) * (Np2 + Np1)
        return Numerator / Denominator
    
    #-------------------------------------------------
    # Get functions below (Not much calculations)
    #-------------------------------------------------
    def getPCRadiusSunM(self):
        return ((self.Ns * self.moduleBig / 2) / 1000.0)

    def getPCRadiusPlanetBigM(self):
        return ((self.NpBig * self.moduleBig / 2) / 1000.0)

    def getPCRadiusPlanetSmallM(self):
        return ((self.NpSmall * self.moduleSmall / 2) / 1000.0)

    def getPCRadiusRingM(self):
        return ((self.Nr * self.moduleSmall / 2) / 1000.0)
    
    def getGearboxOuterDiaMaxM(self):
        Rs       = self.Ns * self.moduleBig * 0.5
        RpBig   = self.NpBig * self.moduleBig * 0.5

        return ((Rs  + 2*RpBig)*2/1000.0)

    def getPCRadiusSunMM(self):
        return ((self.Ns * self.moduleBig / 2))

    def getPCRadiusPlanetBigMM(self):
        return ((self.NpBig * self.moduleBig / 2))

    def getPCRadiusPlanetSmallMM(self):
        return ((self.NpSmall * self.moduleSmall / 2))

    def getPCRadiusRingMM(self):#?
        return ((self.Nr * self.moduleSmall) / 2)
    
    def getOuterRadiusRingM(self):
        ringPCDiameterMM = self.Nr * self.moduleSmall 
        ringPCRadiusMM = ringPCDiameterMM / 2
        return (ringPCRadiusMM + self.ringRadialWidthMM) / 1000.0

    def getCarrierRadiusM(self):
        return (((self.Ns + self.NpBig + self.NpBig/2)/2)*self.moduleBig) / 1000.0

    #--------------------------------------------
    # Set functions
    #--------------------------------------------
    def setfwSunMM(self, fwSunMM):
        self.fwSunMM = fwSunMM

    def setfwPlanetBigMM(self, fwPlanetBigMM):
        self.fwPlanetBigMM = fwPlanetBigMM

    def setfwPlanetSmallMM(self, fwPlanetSmallMM):
        self.fwPlanetSmallMM = fwPlanetSmallMM

    def setfwRingMM(self, fwRingMM):
        self.fwRingMM = fwRingMM
    
    def setModuleBig(self, moduleBig):
        self.moduleBig = moduleBig

    def setModuleSmall(self, moduleSmall):
        self.moduleSmall = moduleSmall

    def setNs(self, Ns):
        self.Ns = Ns

    def setNpBig(self, NpBig):
        self.NpBig = NpBig
    
    def setNpSmall(self, NpSmall):
        self.NpSmall = NpSmall
    
    def setNr(self, Nr):
        self.Nr = Nr

    def setNumPlanet(self, numPlanet):
        self.numPlanet = numPlanet
  
    #--------------------------------------------
    # Print Functions
    #--------------------------------------------
    def printParameters(self):
        print("Ns = ", self.Ns)
        print("NpBig = ", self.NpBig)
        print("NpSmall = ", self.NpSmall)
        print("Nr = ", self.Nr)
        print("Module (First Layer) = ", self.moduleBig)
        print("Module (Second Layer) = ", self.moduleSmall)
        print("Number of planets = ", self.numPlanet)
        print("Face width of sun gear = ", round(self.fwSunMM,2), " mm")
        print("Face width of Bigger planet gear = ", round(self.fwPlanetBigMM,2), " mm")
        print("Face width of Smaller planet gear = ", round(self.fwPlanetSmallMM,2), " mm")
        print("Face width of ring gear = ", round(self.fwRingMM,2), " mm")
        print("Carrier width = ", self.carrierWidthMM, " mm")
        print("Ring radial width = ", self.ringRadialWidthMM, " mm")
        print("Pitch circle radius of sun gear = ", self.getPCRadiusSunM() * 1000, " mm")
        print("Pitch circle radius of Bigger planet gear = ", self.getPCRadiusPlanetBigM() * 1000, " mm")
        print("Pitch circle radius of Smaller planet gear = ", self.getPCRadiusPlanetSmallM() * 1000, " mm")
        print("Pitch circle radius of ring gear = ", self.getPCRadiusRingM() * 1000, " mm")
        print("Outer radius of ring gear = ", self.getOuterRadiusRingM() * 1000, " mm")
        print("Carrier radius = ", self.getCarrierRadiusM() * 1000, " mm")
        print("Geometric constraint = ", self.geometricConstraint())
        print("Meshing constraint = ", self.meshingConstraint())
        print("No planet interference constraint = ", self.noPlanetInterferenceConstraint())
        print("Mass of the planetary gearbox = ", self.getMassKG(), " kg")
        print("Efficiency of the planetary gearbox = ", self.getEfficiency())
        
    def printParametersLess(self):
        vars = [self.moduleBig, self.moduleSmall, self.Ns, self.NpBig, self.NpSmall, self.Nr, self.numPlanet]
        faceWidths = [round(self.fwSunMM,2), round(self.fwPlanetBigMM,2), round(self.fwPlanetSmallMM,2), round(self.fwRingMM,2)]
        print("[mB, mS, Ns, NpB, NpS, Nr, numPl]:", vars) 
        print("Face widths = ", faceWidths)
        print(" ")
        print("Gear ratio = ", self.gearRatio())
        print("Efficiency = ", round(self.getEfficiency(),4))
        print("Mass (gearbox, kg) = ", round(self.getMassKG(),3), " kg")
        # print("--------------------------------------------------------------------------")

#-------------------------------------------------------------------------
# Compound Planetary Actuator class
#-------------------------------------------------------------------------
class inrunnerCompoundPlanetaryActuator:
    def __init__(self, 
                 design_parameters,
                 motor_driver_params,
                 motor                    = motor, 
                 inrunnerCompoundPlanetaryGearbox = inrunnerCompoundPlanetaryGearbox, 
                 FOS                      = 2.0, 
                 serviceFactor            = 2.0, 
                 maxGearboxDiameter       = 140.0,
                 stressAnalysisMethodName = "Lewis"):
        
        self.motor                    = motor
        self.inrunnerCompoundPlanetaryGearbox = inrunnerCompoundPlanetaryGearbox
        self.FOS                      = FOS
        self.serviceFactor            = serviceFactor
        self.maxGearboxDiameter       = maxGearboxDiameter # TODO: convert it to 
                                                           # outer diameter of 
                                                           # the motor
        self.stressAnalysisMethodName = stressAnalysisMethodName

        #============================================
        # Motor Parameters
        #============================================
        self.motorLengthMM           = self.motor.getLengthMM()
        self.motorDiaMM              = self.motor.getDiaMM()
        self.motorMassKG             = self.motor.getMassKG()
        self.MaxMotorTorque          = self.motor.maxMotorTorque          # U12_maxTorque          # Nm
        self.MaxMotorAngVelRPM       = self.motor.maxMotorAngVelRPM       # U12_maxAngVelRPM       # RPM
        self.MaxMotorAngVelRadPerSec = self.motor.maxMotorAngVelRadPerSec # U12_maxAngVelRadPerSec # radians/sec

        #============================================
        # Actuator Design Parameters
        #============================================
        self.design_params = design_parameters
        self.motor_driver_params = motor_driver_params
        
        #--------------------------------------------
        # Independent Parameters
        #--------------------------------------------
        self.ringRadialWidthMM    = self.inrunnerCompoundPlanetaryGearbox.ringRadialWidthMM  

        #-----------------------------------------------------
        # Dependent parameters
        #-----------------------------------------------------
        self.setVariables()

    def cost(self):
        massActuator = self.getMassKG_3DP()
        effActuator  = self.inrunnerCompoundPlanetaryGearbox.getEfficiency()
        widthActuator = self.inrunnerCompoundPlanetaryGearbox.fwPlanetBigMM + self.inrunnerCompoundPlanetaryGearbox.fwPlanetSmallMM
        cost = massActuator - 2 * effActuator + 0.2 * widthActuator
        return cost

    def noCarrierInterferenceConstraint(self):
        module    = self.inrunnerCompoundPlanetaryGearbox.moduleBig  # Module of the gear
        Ns        = self.inrunnerCompoundPlanetaryGearbox.Ns
        Np1       = self.inrunnerCompoundPlanetaryGearbox.NpBig
        Np2       = self.inrunnerCompoundPlanetaryGearbox.NpSmall
        Nr        = self.inrunnerCompoundPlanetaryGearbox.Nr
        numPlanet = self.inrunnerCompoundPlanetaryGearbox.numPlanet

        OutputIDrequiredMM = module * (Ns + Np1) + self.bearingIDClearanceMM
        OutputBearings            = bearings_discrete(OutputIDrequiredMM)
        output_bearing_ID   = OutputBearings.getBearingIDMM()
        
        ring_ID = module * Nr - 2*module*1.25
        return ring_ID > output_bearing_ID + 2*self.standard_clearance_1_5mm

    def planetPCDConstraint(self):
        module    = self.inrunnerCompoundPlanetaryGearbox.moduleBig  # Module of the gear
        Ns        = self.inrunnerCompoundPlanetaryGearbox.Ns
        Np1       = self.inrunnerCompoundPlanetaryGearbox.NpBig
        Np2       = self.inrunnerCompoundPlanetaryGearbox.NpSmall
        Nr        = self.inrunnerCompoundPlanetaryGearbox.Nr
        numPlanet = self.inrunnerCompoundPlanetaryGearbox.numPlanet
        
        planet_ID = module * Np2
        planet_bearing_OD = self.planet_bearing_OD

        return planet_ID > planet_bearing_OD + 2*self.standard_clearance_1_5mm*(2/3)

    def sunPCDConstraint(self):
        module    = self.inrunnerCompoundPlanetaryGearbox.moduleBig  # Module of the gear
        Ns        = self.inrunnerCompoundPlanetaryGearbox.Ns
        Np1       = self.inrunnerCompoundPlanetaryGearbox.NpBig
        Np2       = self.inrunnerCompoundPlanetaryGearbox.NpSmall
        Nr        = self.inrunnerCompoundPlanetaryGearbox.Nr
        numPlanet = self.inrunnerCompoundPlanetaryGearbox.numPlanet
        
        sun_ID = module * Ns - 2*module*1.25
        sun_shaft_bearing_ID = self.sun_shaft_bearing_ID

        return sun_ID > sun_shaft_bearing_ID 
    
    def noSecCarrierInterferenceConstraint(self):
        module    = self.inrunnerCompoundPlanetaryGearbox.moduleBig  # Module of the gear
        Ns        = self.inrunnerCompoundPlanetaryGearbox.Ns
        Np1       = self.inrunnerCompoundPlanetaryGearbox.NpBig
        Np2       = self.inrunnerCompoundPlanetaryGearbox.NpSmall
        Nr        = self.inrunnerCompoundPlanetaryGearbox.Nr
        numPlanet = self.inrunnerCompoundPlanetaryGearbox.numPlanet

        OutputIDrequiredMM = module * (Ns + Np1) + self.bearingIDClearanceMM
        OutputBearings            = bearings_discrete(OutputIDrequiredMM)
        output_bearing_ID   = OutputBearings.getBearingIDMM()
        
        sec_carrier_OD = output_bearing_ID
        max_sec_carrier_OD = self.stator_ID
        return max_sec_carrier_OD >= sec_carrier_OD

    def setVariables(self):
        #--------- Optimization Variable-----------
        self.Ns         = self.inrunnerCompoundPlanetaryGearbox.Ns
        self.Np_b       = self.inrunnerCompoundPlanetaryGearbox.NpBig
        self.Np_s       = self.inrunnerCompoundPlanetaryGearbox.NpSmall
        self.Nr         = self.Ns + self.Np_b + self.Np_s
        self.num_planet = self.inrunnerCompoundPlanetaryGearbox.numPlanet
        self.module     = self.inrunnerCompoundPlanetaryGearbox.moduleBig

        #------------------------------------------------------
        # Indepent Constant variables
        #------------------------------------------------------
        #----------------- Gear Profile --------------------
        self.pressure_angle     = self.inrunnerCompoundPlanetaryGearbox.getPressureAngleRad() # 20
        self.pressure_angle_deg = self.inrunnerCompoundPlanetaryGearbox.getPressureAngleRad() * 180 / np.pi # 20

        #-------------Clearances---------------------
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

        #-----------Motor----------------------------
        self.motor_OD             = self.motorDiaMM                     # 86.8
        self.motor_height         = self.motorLengthMM                  # 26.5
        self.rotor_OD             = self.motor.rotor_OD
        self.stator_ID            = self.motor.stator_ID
        self.rotor_height         = self.motor.rotor_height
        self.rotor_ID             = self.motor.rotor_ID
        self.stator_height        = self.motor.stator_height
        self.stator_OD            = self.motor.stator_OD
        self.stator_hole_dia      = self.motor.stator_hole_dia
        self.stator_top_height    = self.motor.stator_top_height
        self.stator_mid_height    = self.motor.stator_mid_height
        self.stator_bottom_height = self.motor.stator_bottom_height
        self.stator_inside_OD     = self.motor.stator_inside_OD
        self.stator_hole_num      = self.motor.stator_hole_num
        self.stator_inside_ID     = self.motor.stator_inside_ID

        # --- Driver Dimensions ---
        self.driver_upper_holes_dist_from_center = self.motor_driver_params["driver_upper_holes_dist_from_center"]
        self.driver_lower_holes_dist_from_center = self.motor_driver_params["driver_lower_holes_dist_from_center"]
        self.driver_side_holes_dist_from_center  = self.motor_driver_params["driver_side_holes_dist_from_center"]
        self.driver_mount_holes_dia              = self.motor_driver_params["driver_mount_holes_dia"]
        self.driver_mount_inserts_OD             = self.motor_driver_params["driver_mount_inserts_OD"]
        self.driver_mount_thickness              = self.motor_driver_params["driver_mount_thickness"]
        self.driver_mount_height                 = self.motor_driver_params["driver_mount_height"]
        self.motor_mount_driver_hole_dia         = self.design_params["motor_mount_driver_hole_dia"] 
        self.motor_mount_driver_hole_num         = self.design_params["motor_mount_driver_hole_num"]

        # --- Rotor Hub ---
        self.rotor_hub_thickness     = self.design_params["rotor_hub_thickness"]
        self.rotor_hub_height        = self.design_params["rotor_hub_height"]
        self.rotor_hub_sun_hole_dia  = self.design_params["rotor_hub_sun_hole_dia"]        
        self.rotor_hub_sun_hole_num = self.design_params["rotor_hub_sun_hole_num"]

        self.rotor_bottom_bearing_ID  = self.design_params["rotor_bottom_bearing_ID"]
        self.rotor_bottom_bearing_OD  = self.design_params["rotor_bottom_bearing_OD"]
        self.rotor_bottom_bearing_width = self.design_params["rotor_bottom_bearing_width"]

        # --- Planet pin and bearing ---
        self.planet_pin_bolt_dia      = self.design_params["planet_pin_bolt_dia"] # 5 
        #self.planet_shaft_dia         = self.design_params["planet_shaft_dia"] # 8  
        self.planet_shaft_step_offset = self.design_params["planet_shaft_step_offset"] # 1  
        self.planet_bearing_OD        = self.design_params["planet_bearing_OD"] # 12 
        self.planet_bearing_width     = self.design_params["planet_bearing_width"] # 3.5
        self.planet_bearing_ID        = self.design_params["planet_bearing_ID"] # 8

        # --- Sun coupler and sun central bolt ---
        self.sun_coupler_hub_thickness = self.design_params["sun_coupler_hub_thickness"] # 4
        self.sun_shaft_bearing_ID      = self.design_params["sun_shaft_bearing_ID"]           # 8
        self.sun_shaft_bearing_OD      = self.design_params["sun_shaft_bearing_OD"]           # 16
        self.sun_shaft_bearing_width   = self.design_params["sun_shaft_bearing_width"]        # 5
        self.sun_central_bolt_dia      = self.design_params["sun_central_bolt_dia"]      # 5

        # --- Carrier & Sec Carrier ---
        self.sec_carrier_thickness = self.design_params["sec_carrier_thickness"] # 5

        self.carrier_trapezoidal_support_sun_offset                 = self.design_params["carrier_trapezoidal_support_sun_offset"]# 5
        self.carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID = self.design_params["carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID"] # 4
        self.carrier_trapezoidal_support_hole_dia                   = self.design_params["carrier_trapezoidal_support_hole_dia"]# 3

        # --- Casings ---
        self.case_mounting_surface_height = self.design_params["case_mounting_surface_height"] # 4
        self.case_mounting_hole_dia       = self.design_params["case_mounting_hole_dia"] # 3

        self.motor_case_thickness = self.design_params["motor_case_thickness"] # 2.5

        self.output_mount_hole_dia  = self.design_params["output_mount_hole_dia"]  # 4

        self.actuactor_mount_hole_dia               = self.design_params["actuactor_mount_hole_dia"]

        self.motor_case_OD_base_to_chamfer          = self.design_params["motor_case_OD_base_to_chamfer"] # 5
        self.pattern_offset_from_motor_case_OD_base = self.design_params["pattern_offset_from_motor_case_OD_base"] # 3
        self.pattern_bulge_dia                      = self.design_params["pattern_bulge_dia"] # 3
        self.pattern_num_bulge                      = self.design_params["pattern_num_bulge"] # 18
        self.pattern_depth                          = self.design_params["pattern_depth"] # 2

        self.ring_gearbox_casing_thickness           = self.design_params["ring_gearbox_casing_thickness"] # 5

        # --- Magnet Mount ---
        self.magnet_mount_hole_dia        = self.design_params["magnet_mount_hole_dia"]
        self.magnet_thickness             = self.design_params["magnet_thickness"]
        self.magnet_dia                   = self.design_params["magnet_dia"]
        self.magnet_mount_thickness       = self.design_params["magnet_mount_thickness"]
        self.magnet_pattern_bulge_dia    = self.design_params["magnet_pattern_bulge_dia"]
        self.magnet_pattern_bulge_number = self.design_params["magnet_pattern_bulge_number"]
        self.magnet_mount_height         = self.design_params["magnet_mount_height"]

        # --- Ring ---
        self.ring_radial_width = self.design_params["ringRadialWidthMM"] # 3
        
        #------------------------------------------------------
        # Dependent variables
        #------------------------------------------------------
        #---------------------------------------------------
        # Gear 
        #---------------------------------------------------
        # --- Gear Profile ---
        self.h_a          = 1 * self.module
        self.h_b          = 1.25 * self.module
        self.h_f          = 1.25 * self.module
        self.clr_tip_root = self.h_f - self.h_a

        self.dp_s      = self.module * self.Ns
        self.db_s      = self.dp_s * np.cos((self.pressure_angle))
        self.alpha_s   = (np.sqrt(self.dp_s ** 2 - self.db_s ** 2) / self.db_s) * 180 / np.pi - self.pressure_angle_deg
        self.beta_s    = (360 / (4 * self.Ns) - self.alpha_s) * 2
        self.fw_s_calc = self.inrunnerCompoundPlanetaryGearbox.fwSunMM

        self.dp_p_b    = self.module * self.Np_b
        self.db_p_b    = self.dp_p_b * np.cos((self.pressure_angle))
        self.alpha_p_b = (np.sqrt(self.dp_p_b ** 2 - self.db_p_b ** 2) / self.db_p_b) * 180 / np.pi - self.pressure_angle_deg
        self.beta_p_b  = (360 / (4 * self.Np_b) - self.alpha_p_b) * 2
        self.fw_p_b    = self.inrunnerCompoundPlanetaryGearbox.fwPlanetBigMM
        
        self.dp_r    = self.module * self.Nr
        self.db_r    = self.dp_r * np.cos((self.pressure_angle))
        self.alpha_r = (np.sqrt(self.dp_r ** 2 - self.db_r ** 2) / self.db_r) * 180 / np.pi - self.pressure_angle_deg
        self.beta_r  = (360 / (4 * self.Nr) + self.alpha_r) * 2
        self.fw_r    = self.inrunnerCompoundPlanetaryGearbox.fwRingMM + self.standard_clearance_1_5mm

        self.dp_p_s    = self.module * self.Np_s
        self.db_p_s    = self.dp_p_s * np.cos((self.pressure_angle))
        self.alpha_p_s = (np.sqrt(self.dp_p_s ** 2 - self.db_p_s ** 2) / self.db_p_s) * 180 / np.pi - self.pressure_angle_deg
        self.beta_p_s  = (360 / (4 * self.Np_s) - self.alpha_p_s) * 2
        self.fw_p_s    = self.fw_r  
        # --- Driver Dimensions ---
        motor_mount_driver_bolt = nuts_and_bolts_dimensions(bolt_dia=self.motor_mount_driver_hole_dia , bolt_type="socket_head")
        
        self.motor_mount_driver_nut_wrench_size = motor_mount_driver_bolt.nut_width_across_flats 
        self.motor_mount_driver_nut_depth       = motor_mount_driver_bolt.nut_thickness

        # --- Planet Pin and Bearing ---
        planet_pin_bolt = nuts_and_bolts_dimensions(bolt_dia=self.planet_pin_bolt_dia , bolt_type="socket_head")
        
        self.planet_pin_socket_head_dia = planet_pin_bolt.bolt_head_dia
        self.planet_pin_nut_wrench_size = planet_pin_bolt.nut_width_across_flats 
        self.planet_pin_nut_depth       = planet_pin_bolt.nut_thickness

        # --- Sun coupler and sun central bolt ---
        sun_central_bolt = nuts_and_bolts_dimensions(bolt_dia = self.sun_central_bolt_dia, bolt_type="socket_head")
        self.sun_central_bolt_socket_head_dia = sun_central_bolt.bolt_head_dia # 8.5
        
        rotor_hub_sun_bolt = nuts_and_bolts_dimensions(bolt_dia = self.rotor_hub_sun_hole_dia, bolt_type="CSK")

        self.rotor_hub_sun_hole_CSK_OD          = rotor_hub_sun_bolt.bolt_head_dia   
        self.rotor_hub_sun_hole_CSK_head_height = rotor_hub_sun_bolt.bolt_head_height

        self.sun_hub_dia = self.rotor_ID - 2*self.rotor_hub_thickness - 2*self.standard_clearance_1_5mm

        #----------------------- Bearings------------------------------------
        OutputIDrequiredMM         = self.module * (self.Ns + self.Np_b) + self.bearingIDClearanceMM
        OutputBearings             = bearings_discrete(OutputIDrequiredMM)
        self.output_bearing_ID     = OutputBearings.getBearingIDMM()
        self.output_bearing_OD     = OutputBearings.getBearingODMM()
        self.output_bearing_width  = OutputBearings.getBearingWidthMM()

        if self.design_params["min_rotor_top_bearing_ID"] < self.module * self.Ns + 2*self.standard_clearance_1_5mm:
            RotorTopBearingIDrequiredMM   = self.module * self.Ns + 2*self.standard_clearance_1_5mm
        else:
            RotorTopBearingIDrequiredMM   = self.design_params["min_rotor_top_bearing_ID"]

        RotorTopBearings              = bearings_discrete(RotorTopBearingIDrequiredMM)
        self.rotor_top_bearing_ID     = RotorTopBearings.getBearingIDMM()
        self.rotor_top_bearing_OD     = RotorTopBearings.getBearingODMM()
        self.rotor_top_bearing_width  = RotorTopBearings.getBearingWidthMM()

        #------------------- Carrier & Sec Carrier-----------------------------        
        carrier_trapezoidal_support_hole = nuts_and_bolts_dimensions(bolt_dia=self.carrier_trapezoidal_support_hole_dia, bolt_type="socket_head")

        self.carrier_trapezoidal_support_hole_socket_head_dia = carrier_trapezoidal_support_hole.bolt_head_dia
        self.carrier_trapezoidal_support_hole_wrench_size     = carrier_trapezoidal_support_hole.nut_width_across_flats        
        self.carrier_trapezoidal_support_nut_depth            = carrier_trapezoidal_support_hole.nut_thickness 

        # --- Planet Pin and Bearing ---
        # planet_pin_bolt = nuts_and_bolts_dimensions(bolt_dia=self.planet_pin_bolt_dia , bolt_type="socket_head")
        
        # self.planet_pin_socket_head_dia = planet_pin_bolt.bolt_head_dia
        # self.planet_pin_nut_wrench_size = planet_pin_bolt.nut_width_across_flats 
        # self.planet_pin_nut_depth       = planet_pin_bolt.nut_thickness

        #--------------------- Casings------------------------------------------
        case_mounting_hole_bolt = nuts_and_bolts_dimensions(bolt_dia=self.case_mounting_hole_dia, bolt_type="socket_head")

        self.case_mounting_hole_allen_socket_dia = case_mounting_hole_bolt.bolt_head_dia
        self.case_mounting_wrench_size       = case_mounting_hole_bolt.nut_width_across_flats
        self.case_mounting_nut_depth     = case_mounting_hole_bolt.nut_thickness

        output_mount_hole_bolt = nuts_and_bolts_dimensions(bolt_dia=self.output_mount_hole_dia, bolt_type="socket_head")

        self.output_mount_nut_wrench_size       = output_mount_hole_bolt.nut_width_across_flats
        self.output_mount_hole_nut_depth        = output_mount_hole_bolt.nut_thickness

        actuactor_mount_hole_bolt = nuts_and_bolts_dimensions(bolt_dia=self.actuactor_mount_hole_dia, bolt_type="socket_head")

        self.actuactor_mount_nut_wrench_size       = actuactor_mount_hole_bolt.nut_width_across_flats
        self.actuactor_mount_nut_depth             = actuactor_mount_hole_bolt.nut_thickness

        self.case_mounting_hole_shift = self.case_mounting_hole_dia / 2 

        # ---- Sun Gear ----

        self.fw_s_used = self.bearing_step_width + self.sec_carrier_thickness +self.clearance_planet +self.fw_p_b+self.fw_p_s

        #-----
        self.actuator_width =  (self.motor_case_thickness
                                + self.motor_height
                                + self.standard_clearance_1_5mm
                                + self.sec_carrier_thickness
                                + self.clearance_planet
                                + self.fw_p_b
                                + self.fw_p_s
                                + self.clearance_planet
                                + self.bearing_step_width
                                + self.output_bearing_width)
                                                               
    def genEquationFile(self, motor_name="NO_MOTOR", gearRatioLL = 0.0, gearRatioUL = 0.0):
        # writing values into text file imported which is imported into solidworks
        self.setVariables()
        file_path = os.path.join(os.path.dirname(__file__), 'CADs', 'INCPG', 'Equation_Files', motor_name, f'incpg_equations_{gearRatioLL}_{gearRatioUL}.txt')
        with open(file_path, 'w') as eqFile:
            l = [
                    f'"Ns"= {self.Ns}\n',
                    f'"Np_b"= {self.Np_b}\n',
                    f'"Np_s"= {self.Np_s}\n',
                    f'"Nr"= {self.Nr}\n',
                    f'"num_planet"= {self.num_planet}\n',
                    f'"module"= {self.module}\n',
                    f'"pressure_angle"= {self.pressure_angle}\n',
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
                    f'"motor_OD"= {self.motor_OD}\n',
                    f'"motor_height"= {self.motor_height}\n',
                    f'"rotor_OD"= {self.rotor_OD}\n',
                    f'"stator_ID"= {self.stator_ID}\n',
                    f'"rotor_height"= {self.rotor_height}\n',
                    f'"rotor_ID"= {self.rotor_ID}\n',
                    f'"stator_height"= {self.stator_height}\n',
                    f'"stator_OD"= {self.stator_OD}\n',
                    f'"stator_hole_dia"= {self.stator_hole_dia}\n',
                    f'"stator_top_height"= {self.stator_top_height}\n',
                    f'"stator_mid_height"= {self.stator_mid_height}\n',
                    f'"stator_bottom_height"= {self.stator_bottom_height}\n',
                    f'"stator_inside_OD"= {self.stator_inside_OD}\n',
                    f'"stator_hole_num"= {self.stator_hole_num}\n',
                    f'"stator_inside_ID"= {self.stator_inside_ID}\n',
                    f'"driver_upper_holes_dist_from_center"= {self.driver_upper_holes_dist_from_center}\n',
                    f'"driver_lower_holes_dist_from_center"= {self.driver_lower_holes_dist_from_center}\n',
                    f'"driver_side_holes_dist_from_center"= {self.driver_side_holes_dist_from_center}\n',
                    f'"driver_mount_holes_dia"= {self.driver_mount_holes_dia}\n',
                    f'"driver_mount_inserts_OD"= {self.driver_mount_inserts_OD}\n',
                    f'"driver_mount_thickness"= {self.driver_mount_thickness}\n',
                    f'"driver_mount_height"= {self.driver_mount_height}\n',
                    f'"motor_mount_driver_hole_dia"= {self.motor_mount_driver_hole_dia}\n',
                    f'"motor_mount_driver_hole_num"= {self.motor_mount_driver_hole_num}\n',
                    f'"rotor_hub_thickness"= {self.rotor_hub_thickness}\n',
                    f'"rotor_hub_height"= {self.rotor_hub_height}\n',
                    f'"rotor_hub_sun_hole_dia"= {self.rotor_hub_sun_hole_dia}\n',
                    f'"rotor_hub_sun_hole_num"= {self.rotor_hub_sun_hole_num}\n',
                    f'"rotor_top_bearing_ID"= {self.rotor_top_bearing_ID}\n',
                    f'"rotor_top_bearing_OD"= {self.rotor_top_bearing_OD}\n',
                    f'"rotor_top_bearing_width"= {self.rotor_top_bearing_width}\n',
                    f'"rotor_bottom_bearing_ID"= {self.rotor_bottom_bearing_ID}\n',
                    f'"rotor_bottom_bearing_OD"= {self.rotor_bottom_bearing_OD}\n',
                    f'"rotor_bottom_bearing_width"= {self.rotor_bottom_bearing_width}\n',
                    f'"planet_pin_bolt_dia"= {self.planet_pin_bolt_dia}\n',
                    f'"planet_shaft_step_offset"= {self.planet_shaft_step_offset}\n',
                    f'"planet_bearing_OD"= {self.planet_bearing_OD}\n',
                    f'"planet_bearing_width"= {self.planet_bearing_width}\n',
                    f'"planet_bearing_ID"= {self.planet_bearing_ID}\n',
                    f'"sun_coupler_hub_thickness"= {self.sun_coupler_hub_thickness}\n',
                    f'"sun_shaft_bearing_ID"= {self.sun_shaft_bearing_ID}\n',
                    f'"sun_shaft_bearing_OD"= {self.sun_shaft_bearing_OD}\n',
                    f'"sun_shaft_bearing_width"= {self.sun_shaft_bearing_width}\n',
                    f'"sun_central_bolt_dia"= {self.sun_central_bolt_dia}\n',
                    f'"sec_carrier_thickness"= {self.sec_carrier_thickness}\n',
                    f'"carrier_trapezoidal_support_sun_offset"= {self.carrier_trapezoidal_support_sun_offset}\n',
                    f'"carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID"= {self.carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID}\n',
                    f'"carrier_trapezoidal_support_hole_dia"= {self.carrier_trapezoidal_support_hole_dia}\n',
                    f'"case_mounting_surface_height"= {self.case_mounting_surface_height}\n',
                    f'"case_mounting_hole_dia"= {self.case_mounting_hole_dia}\n',
                    f'"motor_case_thickness"= {self.motor_case_thickness}\n',
                    f'"output_mount_hole_dia"= {self.output_mount_hole_dia}\n',
                    f'"actuactor_mount_hole_dia"= {self.actuactor_mount_hole_dia}\n',
                    f'"motor_case_OD_base_to_chamfer"= {self.motor_case_OD_base_to_chamfer}\n',
                    f'"pattern_offset_from_motor_case_OD_base"= {self.pattern_offset_from_motor_case_OD_base}\n',
                    f'"pattern_bulge_dia"= {self.pattern_bulge_dia}\n',
                    f'"pattern_num_bulge"= {self.pattern_num_bulge}\n',
                    f'"pattern_depth"= {self.pattern_depth}\n',
                    f'"magnet_mount_hole_dia"= {self.magnet_mount_hole_dia}\n',
                    f'"magnet_thickness"= {self.magnet_thickness}\n',
                    f'"magnet_dia"= {self.magnet_dia}\n',
                    f'"magnet_mount_thickness"= {self.magnet_mount_thickness}\n',
                    f'"magnet_pattern_bulge_dia"= {self.magnet_pattern_bulge_dia}\n',
                    f'"magnet_pattern_bulge_number"= {self.magnet_pattern_bulge_number}\n',
                    f'"magnet_mount_height"= {self.magnet_mount_height}\n',
                    f'"ring_radial_width"= {self.ring_radial_width}\n',
                    f'"ring_gearbox_casing_thickness"= {self.ring_gearbox_casing_thickness}\n',
                    f'"h_a"= {self.h_a}\n',
                    f'"h_b"= {self.h_b}\n',
                    f'"h_f"= {self.h_f}\n',
                    f'"clr_tip_root"= {self.clr_tip_root}\n',
                    f'"dp_s"= {self.dp_s}\n',
                    f'"db_s"= {self.db_s}\n',
                    f'"alpha_s"= {self.alpha_s}\n',
                    f'"beta_s"= {self.beta_s}\n',
                    f'"fw_s_calc"= {self.fw_s_calc}\n',
                    f'"dp_p_b"= {self.dp_p_b}\n',
                    f'"db_p_b"= {self.db_p_b}\n',
                    f'"alpha_p_b"= {self.alpha_p_b}\n',
                    f'"beta_p_b"= {self.beta_p_b}\n',
                    f'"fw_p_b"= {self.fw_p_b}\n',
                    f'"dp_r"= {self.dp_r}\n',
                    f'"db_r"= {self.db_r}\n',
                    f'"alpha_r"= {self.alpha_r}\n',
                    f'"beta_r"= {self.beta_r}\n',
                    f'"fw_r"= {self.fw_r}\n',
                    f'"dp_p_s"= {self.dp_p_s}\n',
                    f'"db_p_s"= {self.db_p_s}\n',
                    f'"alpha_p_s"= {self.alpha_p_s}\n',
                    f'"beta_p_s"= {self.beta_p_s}\n',
                    f'"fw_p_s"= {self.fw_p_s}\n',
                    f'"motor_mount_driver_nut_wrench_size"= {self.motor_mount_driver_nut_wrench_size}\n',
                    f'"motor_mount_driver_nut_depth"= {self.motor_mount_driver_nut_depth}\n',
                    f'"planet_pin_socket_head_dia"= {self.planet_pin_socket_head_dia}\n',
                    f'"planet_pin_nut_wrench_size"= {self.planet_pin_nut_wrench_size}\n',
                    f'"planet_pin_nut_depth"= {self.planet_pin_nut_depth}\n',
                    f'"sun_central_bolt_socket_head_dia"= {self.sun_central_bolt_socket_head_dia}\n',
                    f'"rotor_hub_sun_hole_CSK_OD"= {self.rotor_hub_sun_hole_CSK_OD}\n',
                    f'"rotor_hub_sun_hole_CSK_head_height"= {self.rotor_hub_sun_hole_CSK_head_height}\n',
                    f'"sun_hub_dia"= {self.sun_hub_dia}\n',
                    f'"output_bearing_ID"= {self.output_bearing_ID}\n',
                    f'"output_bearing_OD"= {self.output_bearing_OD}\n',
                    f'"output_bearing_width"= {self.output_bearing_width}\n',
                    f'"carrier_trapezoidal_support_hole_socket_head_dia"= {self.carrier_trapezoidal_support_hole_socket_head_dia}\n',
                    f'"carrier_trapezoidal_support_hole_wrench_size"= {self.carrier_trapezoidal_support_hole_wrench_size}\n',
                    f'"carrier_trapezoidal_support_nut_depth"= {self.carrier_trapezoidal_support_nut_depth}\n',
                    f'"case_mounting_hole_allen_socket_dia"= {self.case_mounting_hole_allen_socket_dia}\n',
                    f'"case_mounting_wrench_size"= {self.case_mounting_wrench_size}\n',
                    f'"case_mounting_nut_depth"= {self.case_mounting_nut_depth}\n',
                    f'"output_mount_nut_wrench_size"= {self.output_mount_nut_wrench_size}\n',
                    f'"output_mount_hole_nut_depth"= {self.output_mount_hole_nut_depth}\n',
                    f'"actuactor_mount_nut_wrench_size"= {self.actuactor_mount_nut_wrench_size}\n',
                    f'"actuactor_mount_nut_depth"= {self.actuactor_mount_nut_depth}\n',
                    f'"case_mounting_hole_shift"= {self.case_mounting_hole_shift}\n',
                    f'"fw_s_used"= {self.fw_s_used}\n', 
            ]
            eqFile.writelines(l)
        eqFile.close()
        
        file_path = os.path.join(os.path.dirname(__file__), 'CADs', 'INCPG', 'Equation_Files', motor_name, f'incpg_equations_{gearRatioLL}_{gearRatioUL}_onshape.txt')
        with open(file_path, 'w') as eqFile:
            l = [
                    f'"Ns"= {self.Ns}\n',
                    f'"Np_b"= {self.Np_b}\n',
                    f'"Np_s"= {self.Np_s}\n',
                    f'"Nr"= {self.Nr}\n',
                    f'"num_planet"= {self.num_planet}\n',
                    f'"module"= {self.module}\n',
                    f'"pressure_angle"= {self.pressure_angle}\n',
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
                    f'"motor_OD"= {self.motor_OD}\n',
                    f'"motor_height"= {self.motor_height}\n',
                    f'"rotor_OD"= {self.rotor_OD}\n',
                    f'"stator_ID"= {self.stator_ID}\n',
                    f'"rotor_height"= {self.rotor_height}\n',
                    f'"rotor_ID"= {self.rotor_ID}\n',
                    f'"stator_height"= {self.stator_height}\n',
                    f'"stator_OD"= {self.stator_OD}\n',
                    f'"stator_hole_dia"= {self.stator_hole_dia}\n',
                    f'"stator_top_height"= {self.stator_top_height}\n',
                    f'"stator_mid_height"= {self.stator_mid_height}\n',
                    f'"stator_bottom_height"= {self.stator_bottom_height}\n',
                    f'"stator_inside_OD"= {self.stator_inside_OD}\n',
                    f'"stator_hole_num"= {self.stator_hole_num}\n',
                    f'"stator_inside_ID"= {self.stator_inside_ID}\n',
                    f'"driver_upper_holes_dist_from_center"= {self.driver_upper_holes_dist_from_center}\n',
                    f'"driver_lower_holes_dist_from_center"= {self.driver_lower_holes_dist_from_center}\n',
                    f'"driver_side_holes_dist_from_center"= {self.driver_side_holes_dist_from_center}\n',
                    f'"driver_mount_holes_dia"= {self.driver_mount_holes_dia}\n',
                    f'"driver_mount_inserts_OD"= {self.driver_mount_inserts_OD}\n',
                    f'"driver_mount_thickness"= {self.driver_mount_thickness}\n',
                    f'"driver_mount_height"= {self.driver_mount_height}\n',
                    f'"motor_mount_driver_hole_dia"= {self.motor_mount_driver_hole_dia}\n',
                    f'"motor_mount_driver_hole_num"= {self.motor_mount_driver_hole_num}\n',
                    f'"rotor_hub_thickness"= {self.rotor_hub_thickness}\n',
                    f'"rotor_hub_height"= {self.rotor_hub_height}\n',
                    f'"rotor_hub_sun_hole_dia"= {self.rotor_hub_sun_hole_dia}\n',
                    f'"rotor_hub_sun_hole_num"= {self.rotor_hub_sun_hole_num}\n',
                    f'"rotor_top_bearing_ID"= {self.rotor_top_bearing_ID}\n',
                    f'"rotor_top_bearing_OD"= {self.rotor_top_bearing_OD}\n',
                    f'"rotor_top_bearing_width"= {self.rotor_top_bearing_width}\n',
                    f'"rotor_bottom_bearing_ID"= {self.rotor_bottom_bearing_ID}\n',
                    f'"rotor_bottom_bearing_OD"= {self.rotor_bottom_bearing_OD}\n',
                    f'"rotor_bottom_bearing_width"= {self.rotor_bottom_bearing_width}\n',
                    f'"planet_pin_bolt_dia"= {self.planet_pin_bolt_dia}\n',
                    f'"planet_shaft_step_offset"= {self.planet_shaft_step_offset}\n',
                    f'"planet_bearing_OD"= {self.planet_bearing_OD}\n',
                    f'"planet_bearing_width"= {self.planet_bearing_width}\n',
                    f'"planet_bearing_ID"= {self.planet_bearing_ID}\n',
                    f'"sun_coupler_hub_thickness"= {self.sun_coupler_hub_thickness}\n',
                    f'"sun_shaft_bearing_ID"= {self.sun_shaft_bearing_ID}\n',
                    f'"sun_shaft_bearing_OD"= {self.sun_shaft_bearing_OD}\n',
                    f'"sun_shaft_bearing_width"= {self.sun_shaft_bearing_width}\n',
                    f'"sun_central_bolt_dia"= {self.sun_central_bolt_dia}\n',
                    f'"sec_carrier_thickness"= {self.sec_carrier_thickness}\n',
                    f'"carrier_trapezoidal_support_sun_offset"= {self.carrier_trapezoidal_support_sun_offset}\n',
                    f'"carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID"= {self.carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID}\n',
                    f'"carrier_trapezoidal_support_hole_dia"= {self.carrier_trapezoidal_support_hole_dia}\n',
                    f'"case_mounting_surface_height"= {self.case_mounting_surface_height}\n',
                    f'"case_mounting_hole_dia"= {self.case_mounting_hole_dia}\n',
                    f'"motor_case_thickness"= {self.motor_case_thickness}\n',
                    f'"output_mount_hole_dia"= {self.output_mount_hole_dia}\n',
                    f'"actuactor_mount_hole_dia"= {self.actuactor_mount_hole_dia}\n',
                    f'"motor_case_OD_base_to_chamfer"= {self.motor_case_OD_base_to_chamfer}\n',
                    f'"pattern_offset_from_motor_case_OD_base"= {self.pattern_offset_from_motor_case_OD_base}\n',
                    f'"pattern_bulge_dia"= {self.pattern_bulge_dia}\n',
                    f'"pattern_num_bulge"= {self.pattern_num_bulge}\n',
                    f'"pattern_depth"= {self.pattern_depth}\n',
                    f'"magnet_mount_hole_dia"= {self.magnet_mount_hole_dia}\n',
                    f'"magnet_thickness"= {self.magnet_thickness}\n',
                    f'"magnet_dia"= {self.magnet_dia}\n',
                    f'"magnet_mount_thickness"= {self.magnet_mount_thickness}\n',
                    f'"magnet_pattern_bulge_dia"= {self.magnet_pattern_bulge_dia}\n',
                    f'"magnet_pattern_bulge_number"= {self.magnet_pattern_bulge_number}\n',
                    f'"magnet_mount_height"= {self.magnet_mount_height}\n',
                    f'"ring_radial_width"= {self.ring_radial_width}\n',
                    f'"ring_gearbox_casing_thickness"= {self.ring_gearbox_casing_thickness}\n',
                    f'"h_a"= {self.h_a}\n',
                    f'"h_b"= {self.h_b}\n',
                    f'"h_f"= {self.h_f}\n',
                    f'"clr_tip_root"= {self.clr_tip_root}\n',
                    f'"dp_s"= {self.dp_s}\n',
                    f'"db_s"= {self.db_s}\n',
                    f'"alpha_s"= {self.alpha_s}\n',
                    f'"beta_s"= {self.beta_s}\n',
                    f'"fw_s_calc"= {self.fw_s_calc}\n',
                    f'"dp_p_b"= {self.dp_p_b}\n',
                    f'"db_p_b"= {self.db_p_b}\n',
                    f'"alpha_p_b"= {self.alpha_p_b}\n',
                    f'"beta_p_b"= {self.beta_p_b}\n',
                    f'"fw_p_b"= {self.fw_p_b}\n',
                    f'"dp_r"= {self.dp_r}\n',
                    f'"db_r"= {self.db_r}\n',
                    f'"alpha_r"= {self.alpha_r}\n',
                    f'"beta_r"= {self.beta_r}\n',
                    f'"fw_r"= {self.fw_r}\n',
                    f'"dp_p_s"= {self.dp_p_s}\n',
                    f'"db_p_s"= {self.db_p_s}\n',
                    f'"alpha_p_s"= {self.alpha_p_s}\n',
                    f'"beta_p_s"= {self.beta_p_s}\n',
                    f'"fw_p_s"= {self.fw_p_s}\n',
                    f'"motor_mount_driver_nut_wrench_size"= {self.motor_mount_driver_nut_wrench_size}\n',
                    f'"motor_mount_driver_nut_depth"= {self.motor_mount_driver_nut_depth}\n',
                    f'"planet_pin_socket_head_dia"= {self.planet_pin_socket_head_dia}\n',
                    f'"planet_pin_nut_wrench_size"= {self.planet_pin_nut_wrench_size}\n',
                    f'"planet_pin_nut_depth"= {self.planet_pin_nut_depth}\n',
                    f'"sun_central_bolt_socket_head_dia"= {self.sun_central_bolt_socket_head_dia}\n',
                    f'"rotor_hub_sun_hole_CSK_OD"= {self.rotor_hub_sun_hole_CSK_OD}\n',
                    f'"rotor_hub_sun_hole_CSK_head_height"= {self.rotor_hub_sun_hole_CSK_head_height}\n',
                    f'"sun_hub_dia"= {self.sun_hub_dia}\n',
                    f'"output_bearing_ID"= {self.output_bearing_ID}\n',
                    f'"output_bearing_OD"= {self.output_bearing_OD}\n',
                    f'"output_bearing_width"= {self.output_bearing_width}\n',
                    f'"carrier_trapezoidal_support_hole_socket_head_dia"= {self.carrier_trapezoidal_support_hole_socket_head_dia}\n',
                    f'"carrier_trapezoidal_support_hole_wrench_size"= {self.carrier_trapezoidal_support_hole_wrench_size}\n',
                    f'"carrier_trapezoidal_support_nut_depth"= {self.carrier_trapezoidal_support_nut_depth}\n',
                    f'"case_mounting_hole_allen_socket_dia"= {self.case_mounting_hole_allen_socket_dia}\n',
                    f'"case_mounting_wrench_size"= {self.case_mounting_wrench_size}\n',
                    f'"case_mounting_nut_depth"= {self.case_mounting_nut_depth}\n',
                    f'"output_mount_nut_wrench_size"= {self.output_mount_nut_wrench_size}\n',
                    f'"output_mount_hole_nut_depth"= {self.output_mount_hole_nut_depth}\n',
                    f'"actuactor_mount_nut_wrench_size"= {self.actuactor_mount_nut_wrench_size}\n',
                    f'"actuactor_mount_nut_depth"= {self.actuactor_mount_nut_depth}\n',
                    f'"case_mounting_hole_shift"= {self.case_mounting_hole_shift}\n',
                    f'"fw_s_used"= {self.fw_s_used}\n',  
            ]
            eqFile.writelines(l)
        eqFile.close()

    def genEquationFile_editCADdirectly(self):
        # writing values into text file imported which is imported into solidworks
        self.setVariables()
        file_path = os.path.join(os.path.dirname(__file__), 'CADs', 'INCPG', 'incpg_equations.txt')
        with open(file_path, 'w') as eqFile:
            l = [
                    f'"Ns"= {self.Ns}\n',
                    f'"Np_b"= {self.Np_b}\n',
                    f'"Np_s"= {self.Np_s}\n',
                    f'"Nr"= {self.Nr}\n',
                    f'"num_planet"= {self.num_planet}\n',
                    f'"module"= {self.module}\n',
                    f'"pressure_angle"= {self.pressure_angle}\n',
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
                    f'"motor_OD"= {self.motor_OD}\n',
                    f'"motor_height"= {self.motor_height}\n',
                    f'"rotor_OD"= {self.rotor_OD}\n',
                    f'"stator_ID"= {self.stator_ID}\n',
                    f'"rotor_height"= {self.rotor_height}\n',
                    f'"rotor_ID"= {self.rotor_ID}\n',
                    f'"stator_height"= {self.stator_height}\n',
                    f'"stator_OD"= {self.stator_OD}\n',
                    f'"stator_hole_dia"= {self.stator_hole_dia}\n',
                    f'"stator_top_height"= {self.stator_top_height}\n',
                    f'"stator_mid_height"= {self.stator_mid_height}\n',
                    f'"stator_bottom_height"= {self.stator_bottom_height}\n',
                    f'"stator_inside_OD"= {self.stator_inside_OD}\n',
                    f'"stator_hole_num"= {self.stator_hole_num}\n',
                    f'"stator_inside_ID"= {self.stator_inside_ID}\n',
                    f'"driver_upper_holes_dist_from_center"= {self.driver_upper_holes_dist_from_center}\n',
                    f'"driver_lower_holes_dist_from_center"= {self.driver_lower_holes_dist_from_center}\n',
                    f'"driver_side_holes_dist_from_center"= {self.driver_side_holes_dist_from_center}\n',
                    f'"driver_mount_holes_dia"= {self.driver_mount_holes_dia}\n',
                    f'"driver_mount_inserts_OD"= {self.driver_mount_inserts_OD}\n',
                    f'"driver_mount_thickness"= {self.driver_mount_thickness}\n',
                    f'"driver_mount_height"= {self.driver_mount_height}\n',
                    f'"motor_mount_driver_hole_dia"= {self.motor_mount_driver_hole_dia}\n',
                    f'"motor_mount_driver_hole_num"= {self.motor_mount_driver_hole_num}\n',
                    f'"rotor_hub_thickness"= {self.rotor_hub_thickness}\n',
                    f'"rotor_hub_height"= {self.rotor_hub_height}\n',
                    f'"rotor_hub_sun_hole_dia"= {self.rotor_hub_sun_hole_dia}\n',
                    f'"rotor_hub_sun_hole_num"= {self.rotor_hub_sun_hole_num}\n',
                    f'"rotor_top_bearing_ID"= {self.rotor_top_bearing_ID}\n',
                    f'"rotor_top_bearing_OD"= {self.rotor_top_bearing_OD}\n',
                    f'"rotor_top_bearing_width"= {self.rotor_top_bearing_width}\n',
                    f'"rotor_bottom_bearing_ID"= {self.rotor_bottom_bearing_ID}\n',
                    f'"rotor_bottom_bearing_OD"= {self.rotor_bottom_bearing_OD}\n',
                    f'"rotor_bottom_bearing_width"= {self.rotor_bottom_bearing_width}\n',
                    f'"planet_pin_bolt_dia"= {self.planet_pin_bolt_dia}\n',
                    f'"planet_shaft_step_offset"= {self.planet_shaft_step_offset}\n',
                    f'"planet_bearing_OD"= {self.planet_bearing_OD}\n',
                    f'"planet_bearing_width"= {self.planet_bearing_width}\n',
                    f'"planet_bearing_ID"= {self.planet_bearing_ID}\n',
                    f'"sun_coupler_hub_thickness"= {self.sun_coupler_hub_thickness}\n',
                    f'"sun_shaft_bearing_ID"= {self.sun_shaft_bearing_ID}\n',
                    f'"sun_shaft_bearing_OD"= {self.sun_shaft_bearing_OD}\n',
                    f'"sun_shaft_bearing_width"= {self.sun_shaft_bearing_width}\n',
                    f'"sun_central_bolt_dia"= {self.sun_central_bolt_dia}\n',
                    f'"sec_carrier_thickness"= {self.sec_carrier_thickness}\n',
                    f'"carrier_trapezoidal_support_sun_offset"= {self.carrier_trapezoidal_support_sun_offset}\n',
                    f'"carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID"= {self.carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID}\n',
                    f'"carrier_trapezoidal_support_hole_dia"= {self.carrier_trapezoidal_support_hole_dia}\n',
                    f'"case_mounting_surface_height"= {self.case_mounting_surface_height}\n',
                    f'"case_mounting_hole_dia"= {self.case_mounting_hole_dia}\n',
                    f'"motor_case_thickness"= {self.motor_case_thickness}\n',
                    f'"output_mount_hole_dia"= {self.output_mount_hole_dia}\n',
                    f'"actuactor_mount_hole_dia"= {self.actuactor_mount_hole_dia}\n',
                    f'"motor_case_OD_base_to_chamfer"= {self.motor_case_OD_base_to_chamfer}\n',
                    f'"pattern_offset_from_motor_case_OD_base"= {self.pattern_offset_from_motor_case_OD_base}\n',
                    f'"pattern_bulge_dia"= {self.pattern_bulge_dia}\n',
                    f'"pattern_num_bulge"= {self.pattern_num_bulge}\n',
                    f'"pattern_depth"= {self.pattern_depth}\n',
                    f'"magnet_mount_hole_dia"= {self.magnet_mount_hole_dia}\n',
                    f'"magnet_thickness"= {self.magnet_thickness}\n',
                    f'"magnet_dia"= {self.magnet_dia}\n',
                    f'"magnet_mount_thickness"= {self.magnet_mount_thickness}\n',
                    f'"magnet_pattern_bulge_dia"= {self.magnet_pattern_bulge_dia}\n',
                    f'"magnet_pattern_bulge_number"= {self.magnet_pattern_bulge_number}\n',
                    f'"magnet_mount_height"= {self.magnet_mount_height}\n',
                    f'"ring_radial_width"= {self.ring_radial_width}\n',
                    f'"ring_gearbox_casing_thickness"= {self.ring_gearbox_casing_thickness}\n',
                    f'"h_a"= {self.h_a}\n',
                    f'"h_b"= {self.h_b}\n',
                    f'"h_f"= {self.h_f}\n',
                    f'"clr_tip_root"= {self.clr_tip_root}\n',
                    f'"dp_s"= {self.dp_s}\n',
                    f'"db_s"= {self.db_s}\n',
                    f'"alpha_s"= {self.alpha_s}\n',
                    f'"beta_s"= {self.beta_s}\n',
                    f'"fw_s_calc"= {self.fw_s_calc}\n',
                    f'"dp_p_b"= {self.dp_p_b}\n',
                    f'"db_p_b"= {self.db_p_b}\n',
                    f'"alpha_p_b"= {self.alpha_p_b}\n',
                    f'"beta_p_b"= {self.beta_p_b}\n',
                    f'"fw_p_b"= {self.fw_p_b}\n',
                    f'"dp_r"= {self.dp_r}\n',
                    f'"db_r"= {self.db_r}\n',
                    f'"alpha_r"= {self.alpha_r}\n',
                    f'"beta_r"= {self.beta_r}\n',
                    f'"fw_r"= {self.fw_r}\n',
                    f'"dp_p_s"= {self.dp_p_s}\n',
                    f'"db_p_s"= {self.db_p_s}\n',
                    f'"alpha_p_s"= {self.alpha_p_s}\n',
                    f'"beta_p_s"= {self.beta_p_s}\n',
                    f'"fw_p_s"= {self.fw_p_s}\n',
                    f'"motor_mount_driver_nut_wrench_size"= {self.motor_mount_driver_nut_wrench_size}\n',
                    f'"motor_mount_driver_nut_depth"= {self.motor_mount_driver_nut_depth}\n',
                    f'"planet_pin_socket_head_dia"= {self.planet_pin_socket_head_dia}\n',
                    f'"planet_pin_nut_wrench_size"= {self.planet_pin_nut_wrench_size}\n',
                    f'"planet_pin_nut_depth"= {self.planet_pin_nut_depth}\n',
                    f'"sun_central_bolt_socket_head_dia"= {self.sun_central_bolt_socket_head_dia}\n',
                    f'"rotor_hub_sun_hole_CSK_OD"= {self.rotor_hub_sun_hole_CSK_OD}\n',
                    f'"rotor_hub_sun_hole_CSK_head_height"= {self.rotor_hub_sun_hole_CSK_head_height}\n',
                    f'"sun_hub_dia"= {self.sun_hub_dia}\n',
                    f'"output_bearing_ID"= {self.output_bearing_ID}\n',
                    f'"output_bearing_OD"= {self.output_bearing_OD}\n',
                    f'"output_bearing_width"= {self.output_bearing_width}\n',
                    f'"carrier_trapezoidal_support_hole_socket_head_dia"= {self.carrier_trapezoidal_support_hole_socket_head_dia}\n',
                    f'"carrier_trapezoidal_support_hole_wrench_size"= {self.carrier_trapezoidal_support_hole_wrench_size}\n',
                    f'"carrier_trapezoidal_support_nut_depth"= {self.carrier_trapezoidal_support_nut_depth}\n',
                    f'"case_mounting_hole_allen_socket_dia"= {self.case_mounting_hole_allen_socket_dia}\n',
                    f'"case_mounting_wrench_size"= {self.case_mounting_wrench_size}\n',
                    f'"case_mounting_nut_depth"= {self.case_mounting_nut_depth}\n',
                    f'"output_mount_nut_wrench_size"= {self.output_mount_nut_wrench_size}\n',
                    f'"output_mount_hole_nut_depth"= {self.output_mount_hole_nut_depth}\n',
                    f'"actuactor_mount_nut_wrench_size"= {self.actuactor_mount_nut_wrench_size}\n',
                    f'"actuactor_mount_nut_depth"= {self.actuactor_mount_nut_depth}\n',
                    f'"case_mounting_hole_shift"= {self.case_mounting_hole_shift}\n',
                    f'"fw_s_used"= {self.fw_s_used}\n',  
            ]
            eqFile.writelines(l)
        eqFile.close()

        file_path = os.path.join(os.path.dirname(__file__), 'CADs', 'INCPG', 'incpg_equations_onshape.txt')
        with open(file_path, 'w') as eqFile:
            l = [
                    f'"Ns"= {self.Ns}\n',
                    f'"Np_b"= {self.Np_b}\n',
                    f'"Np_s"= {self.Np_s}\n',
                    f'"Nr"= {self.Nr}\n',
                    f'"num_planet"= {self.num_planet}\n',
                    f'"module"= {self.module}\n',
                    f'"pressure_angle"= {self.pressure_angle}\n',
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
                    f'"motor_OD"= {self.motor_OD}\n',
                    f'"motor_height"= {self.motor_height}\n',
                    f'"rotor_OD"= {self.rotor_OD}\n',
                    f'"stator_ID"= {self.stator_ID}\n',
                    f'"rotor_height"= {self.rotor_height}\n',
                    f'"rotor_ID"= {self.rotor_ID}\n',
                    f'"stator_height"= {self.stator_height}\n',
                    f'"stator_OD"= {self.stator_OD}\n',
                    f'"stator_hole_dia"= {self.stator_hole_dia}\n',
                    f'"stator_top_height"= {self.stator_top_height}\n',
                    f'"stator_mid_height"= {self.stator_mid_height}\n',
                    f'"stator_bottom_height"= {self.stator_bottom_height}\n',
                    f'"stator_inside_OD"= {self.stator_inside_OD}\n',
                    f'"stator_hole_num"= {self.stator_hole_num}\n',
                    f'"stator_inside_ID"= {self.stator_inside_ID}\n',
                    f'"driver_upper_holes_dist_from_center"= {self.driver_upper_holes_dist_from_center}\n',
                    f'"driver_lower_holes_dist_from_center"= {self.driver_lower_holes_dist_from_center}\n',
                    f'"driver_side_holes_dist_from_center"= {self.driver_side_holes_dist_from_center}\n',
                    f'"driver_mount_holes_dia"= {self.driver_mount_holes_dia}\n',
                    f'"driver_mount_inserts_OD"= {self.driver_mount_inserts_OD}\n',
                    f'"driver_mount_thickness"= {self.driver_mount_thickness}\n',
                    f'"driver_mount_height"= {self.driver_mount_height}\n',
                    f'"motor_mount_driver_hole_dia"= {self.motor_mount_driver_hole_dia}\n',
                    f'"motor_mount_driver_hole_num"= {self.motor_mount_driver_hole_num}\n',
                    f'"rotor_hub_thickness"= {self.rotor_hub_thickness}\n',
                    f'"rotor_hub_height"= {self.rotor_hub_height}\n',
                    f'"rotor_hub_sun_hole_dia"= {self.rotor_hub_sun_hole_dia}\n',
                    f'"rotor_hub_sun_hole_num"= {self.rotor_hub_sun_hole_num}\n',
                    f'"rotor_top_bearing_ID"= {self.rotor_top_bearing_ID}\n',
                    f'"rotor_top_bearing_OD"= {self.rotor_top_bearing_OD}\n',
                    f'"rotor_top_bearing_width"= {self.rotor_top_bearing_width}\n',
                    f'"rotor_bottom_bearing_ID"= {self.rotor_bottom_bearing_ID}\n',
                    f'"rotor_bottom_bearing_OD"= {self.rotor_bottom_bearing_OD}\n',
                    f'"rotor_bottom_bearing_width"= {self.rotor_bottom_bearing_width}\n',
                    f'"planet_pin_bolt_dia"= {self.planet_pin_bolt_dia}\n',
                    f'"planet_shaft_step_offset"= {self.planet_shaft_step_offset}\n',
                    f'"planet_bearing_OD"= {self.planet_bearing_OD}\n',
                    f'"planet_bearing_width"= {self.planet_bearing_width}\n',
                    f'"planet_bearing_ID"= {self.planet_bearing_ID}\n',
                    f'"sun_coupler_hub_thickness"= {self.sun_coupler_hub_thickness}\n',
                    f'"sun_shaft_bearing_ID"= {self.sun_shaft_bearing_ID}\n',
                    f'"sun_shaft_bearing_OD"= {self.sun_shaft_bearing_OD}\n',
                    f'"sun_shaft_bearing_width"= {self.sun_shaft_bearing_width}\n',
                    f'"sun_central_bolt_dia"= {self.sun_central_bolt_dia}\n',
                    f'"sec_carrier_thickness"= {self.sec_carrier_thickness}\n',
                    f'"carrier_trapezoidal_support_sun_offset"= {self.carrier_trapezoidal_support_sun_offset}\n',
                    f'"carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID"= {self.carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID}\n',
                    f'"carrier_trapezoidal_support_hole_dia"= {self.carrier_trapezoidal_support_hole_dia}\n',
                    f'"case_mounting_surface_height"= {self.case_mounting_surface_height}\n',
                    f'"case_mounting_hole_dia"= {self.case_mounting_hole_dia}\n',
                    f'"motor_case_thickness"= {self.motor_case_thickness}\n',
                    f'"output_mount_hole_dia"= {self.output_mount_hole_dia}\n',
                    f'"actuactor_mount_hole_dia"= {self.actuactor_mount_hole_dia}\n',
                    f'"motor_case_OD_base_to_chamfer"= {self.motor_case_OD_base_to_chamfer}\n',
                    f'"pattern_offset_from_motor_case_OD_base"= {self.pattern_offset_from_motor_case_OD_base}\n',
                    f'"pattern_bulge_dia"= {self.pattern_bulge_dia}\n',
                    f'"pattern_num_bulge"= {self.pattern_num_bulge}\n',
                    f'"pattern_depth"= {self.pattern_depth}\n',
                    f'"magnet_mount_hole_dia"= {self.magnet_mount_hole_dia}\n',
                    f'"magnet_thickness"= {self.magnet_thickness}\n',
                    f'"magnet_dia"= {self.magnet_dia}\n',
                    f'"magnet_mount_thickness"= {self.magnet_mount_thickness}\n',
                    f'"magnet_pattern_bulge_dia"= {self.magnet_pattern_bulge_dia}\n',
                    f'"magnet_pattern_bulge_number"= {self.magnet_pattern_bulge_number}\n',
                    f'"magnet_mount_height"= {self.magnet_mount_height}\n',
                    f'"ring_radial_width"= {self.ring_radial_width}\n',
                    f'"ring_gearbox_casing_thickness"= {self.ring_gearbox_casing_thickness}\n',
                    f'"h_a"= {self.h_a}\n',
                    f'"h_b"= {self.h_b}\n',
                    f'"h_f"= {self.h_f}\n',
                    f'"clr_tip_root"= {self.clr_tip_root}\n',
                    f'"dp_s"= {self.dp_s}\n',
                    f'"db_s"= {self.db_s}\n',
                    f'"alpha_s"= {self.alpha_s}\n',
                    f'"beta_s"= {self.beta_s}\n',
                    f'"fw_s_calc"= {self.fw_s_calc}\n',
                    f'"dp_p_b"= {self.dp_p_b}\n',
                    f'"db_p_b"= {self.db_p_b}\n',
                    f'"alpha_p_b"= {self.alpha_p_b}\n',
                    f'"beta_p_b"= {self.beta_p_b}\n',
                    f'"fw_p_b"= {self.fw_p_b}\n',
                    f'"dp_r"= {self.dp_r}\n',
                    f'"db_r"= {self.db_r}\n',
                    f'"alpha_r"= {self.alpha_r}\n',
                    f'"beta_r"= {self.beta_r}\n',
                    f'"fw_r"= {self.fw_r}\n',
                    f'"dp_p_s"= {self.dp_p_s}\n',
                    f'"db_p_s"= {self.db_p_s}\n',
                    f'"alpha_p_s"= {self.alpha_p_s}\n',
                    f'"beta_p_s"= {self.beta_p_s}\n',
                    f'"fw_p_s"= {self.fw_p_s}\n',
                    f'"motor_mount_driver_nut_wrench_size"= {self.motor_mount_driver_nut_wrench_size}\n',
                    f'"motor_mount_driver_nut_depth"= {self.motor_mount_driver_nut_depth}\n',
                    f'"planet_pin_socket_head_dia"= {self.planet_pin_socket_head_dia}\n',
                    f'"planet_pin_nut_wrench_size"= {self.planet_pin_nut_wrench_size}\n',
                    f'"planet_pin_nut_depth"= {self.planet_pin_nut_depth}\n',
                    f'"sun_central_bolt_socket_head_dia"= {self.sun_central_bolt_socket_head_dia}\n',
                    f'"rotor_hub_sun_hole_CSK_OD"= {self.rotor_hub_sun_hole_CSK_OD}\n',
                    f'"rotor_hub_sun_hole_CSK_head_height"= {self.rotor_hub_sun_hole_CSK_head_height}\n',
                    f'"sun_hub_dia"= {self.sun_hub_dia}\n',
                    f'"output_bearing_ID"= {self.output_bearing_ID}\n',
                    f'"output_bearing_OD"= {self.output_bearing_OD}\n',
                    f'"output_bearing_width"= {self.output_bearing_width}\n',
                    f'"carrier_trapezoidal_support_hole_socket_head_dia"= {self.carrier_trapezoidal_support_hole_socket_head_dia}\n',
                    f'"carrier_trapezoidal_support_hole_wrench_size"= {self.carrier_trapezoidal_support_hole_wrench_size}\n',
                    f'"carrier_trapezoidal_support_nut_depth"= {self.carrier_trapezoidal_support_nut_depth}\n',
                    f'"case_mounting_hole_allen_socket_dia"= {self.case_mounting_hole_allen_socket_dia}\n',
                    f'"case_mounting_wrench_size"= {self.case_mounting_wrench_size}\n',
                    f'"case_mounting_nut_depth"= {self.case_mounting_nut_depth}\n',
                    f'"output_mount_nut_wrench_size"= {self.output_mount_nut_wrench_size}\n',
                    f'"output_mount_hole_nut_depth"= {self.output_mount_hole_nut_depth}\n',
                    f'"actuactor_mount_nut_wrench_size"= {self.actuactor_mount_nut_wrench_size}\n',
                    f'"actuactor_mount_nut_depth"= {self.actuactor_mount_nut_depth}\n',
                    f'"case_mounting_hole_shift"= {self.case_mounting_hole_shift}\n',
                    f'"fw_s_used"= {self.fw_s_used}\n',  
            ]
            eqFile.writelines(l)
        eqFile.close()

    #--------------------------------------------
    # Gear tooth stress analysis
    #--------------------------------------------
    def getToothForces(self, constraintCheck=True):
        if constraintCheck:
            # Check if the constraints are satisfied
            if not self.inrunnerCompoundPlanetaryGearbox.geometricConstraint():
                print("Geometric constraint not satisfied")
                return
            if not self.inrunnerCompoundPlanetaryGearbox.meshingConstraint():
                print("Meshing constraint not satisfied")
                return
            if not self.inrunnerCompoundPlanetaryGearbox.noPlanetInterferenceConstraint():
                print("No planet interference constraint not satisfied")
                return

        Ns          = self.inrunnerCompoundPlanetaryGearbox.Ns
        NpBig       = self.inrunnerCompoundPlanetaryGearbox.NpBig
        NpSmall     = self.inrunnerCompoundPlanetaryGearbox.NpSmall
        Nr          = self.inrunnerCompoundPlanetaryGearbox.Nr
        numPlanet   = self.inrunnerCompoundPlanetaryGearbox.numPlanet
        moduleBig   = self.inrunnerCompoundPlanetaryGearbox.moduleBig
        moduleSmall = self.inrunnerCompoundPlanetaryGearbox.moduleSmall

        Rs_Mt = self.inrunnerCompoundPlanetaryGearbox.getPCRadiusSunM()
        RpBig_Mt = self.inrunnerCompoundPlanetaryGearbox.getPCRadiusPlanetBigM()
        RpSmall_Mt = self.inrunnerCompoundPlanetaryGearbox.getPCRadiusPlanetSmallM()
        Rr_Mt = self.inrunnerCompoundPlanetaryGearbox.getPCRadiusRingM()

        wSun     = self.motor.getMaxMotorAngVelRadPerSec()
        wPlanet  = (-Ns / (NpBig + NpSmall) ) * wSun
        wCarrier = wSun/self.inrunnerCompoundPlanetaryGearbox.gearRatio()

        Ft_sp = (self.serviceFactor*self.motor.getMaxMotorTorque()) / (numPlanet * Rs_Mt)
        Ft_rp = ((self.serviceFactor*self.motor.getMaxMotorTorque()) * RpBig_Mt) / (numPlanet * Rs_Mt * RpSmall_Mt)

        Ft = [Ft_sp, Ft_rp]
        return Ft

    def lewisStressAnalysisMinFacewidth(self):
        # Check if the constraints are satisfied
        if not self.inrunnerCompoundPlanetaryGearbox.geometricConstraint():
            print("Geometric constraint not satisfied")
            return
        if not self.inrunnerCompoundPlanetaryGearbox.meshingConstraint():
            print("Meshing constraint not satisfied")
            return
        if not self.inrunnerCompoundPlanetaryGearbox.noPlanetInterferenceConstraint():
            print("No planet interference constraint not satisfied")
            return

        Ns          = self.inrunnerCompoundPlanetaryGearbox.Ns
        NpBig       = self.inrunnerCompoundPlanetaryGearbox.NpBig
        NpSmall     = self.inrunnerCompoundPlanetaryGearbox.NpSmall
        Nr          = self.inrunnerCompoundPlanetaryGearbox.Nr
        numPlanet   = self.inrunnerCompoundPlanetaryGearbox.numPlanet
        moduleBig   = self.inrunnerCompoundPlanetaryGearbox.moduleBig
        moduleSmall = self.inrunnerCompoundPlanetaryGearbox.moduleSmall

        wSun     = self.motor.getMaxMotorAngVelRadPerSec()
        wPlanet  = (-Ns / (NpBig + NpSmall) ) * wSun
        wCarrier = wSun/self.inrunnerCompoundPlanetaryGearbox.gearRatio()

        [Ft_sp, Ft_rp] = self.getToothForces(constraintCheck=False)

        ySun         = 0.154 - 0.912/Ns
        yPlanetBig   = 0.154 - 0.912/NpBig
        yPlanetSmall = 0.154 - 0.912/NpSmall
        yRing        = 0.154 - 0.912/Nr

        V_sp = (self.inrunnerCompoundPlanetaryGearbox.getPCRadiusSunM() * wSun)
        V_rp = (wCarrier*(self.inrunnerCompoundPlanetaryGearbox.getPCRadiusSunM() + self.inrunnerCompoundPlanetaryGearbox.getPCRadiusPlanetBigM()) + 
                wPlanet*(self.inrunnerCompoundPlanetaryGearbox.getPCRadiusPlanetSmallM()))
        
        if V_sp <= 7.5:
            Kv_sun = 3/(3+V_sp)
            Kv_planetBig = 3/(3+V_sp)
        # elif V_sp > 7.5 and V_sp <= 12.5:
        else:
            Kv_sun = 4.5/(4.5 + V_sp)
            Kv_planetBig = 4.5/(4.5 + V_sp)

        if V_rp <= 7.5:
            Kv_planetSmall = 3/(3+V_rp)
            Kv_ring = 3/(3+V_rp)
        elif V_rp > 7.5 and V_rp <= 12.5:
            Kv_planetSmall = 4.5/(4.5 + V_rp)
            Kv_ring = 4.5/(4.5 + V_rp)

        P_big   = np.pi*moduleBig*0.001 # m
        P_small = np.pi*moduleSmall*0.001 # m

        # Lewis static load capacity
        bMin_sun         = (self.FOS * Ft_sp / (self.inrunnerCompoundPlanetaryGearbox.maxGearAllowableStressPa * ySun * Kv_sun * P_big)) # m
        bMin_planetBig   = (self.FOS * Ft_sp / (self.inrunnerCompoundPlanetaryGearbox.maxGearAllowableStressPa * yPlanetBig * Kv_planetBig * P_big))
        bMin_planetSmall = (self.FOS * Ft_rp / (self.inrunnerCompoundPlanetaryGearbox.maxGearAllowableStressPa * yPlanetSmall * Kv_planetSmall * P_small))
        bMin_ring        = (self.FOS * Ft_rp / (self.inrunnerCompoundPlanetaryGearbox.maxGearAllowableStressPa * yRing * Kv_ring * P_small))

        if bMin_ring < bMin_planetSmall:
            bMin_ring = bMin_planetSmall
        else:
            bMin_planetSmall = bMin_ring

        self.inrunnerCompoundPlanetaryGearbox.setfwSunMM(bMin_sun*1000)
        self.inrunnerCompoundPlanetaryGearbox.setfwPlanetBigMM(bMin_planetBig*1000)
        self.inrunnerCompoundPlanetaryGearbox.setfwPlanetSmallMM(bMin_planetSmall*1000)
        self.inrunnerCompoundPlanetaryGearbox.setfwRingMM(bMin_ring*1000)

        # print(f"Lewis:")
        # print(f"bMin_planetSmall = {bMin_planetSmall}")
        # print(f"bMin_planetBig = {bMin_planetBig}")
        # print(f"bMin_sun = {bMin_sun}")
        # print(f"bMin_ring = {bMin_ring}")

    def mitStressAnalysisMinFacewidth(self):
        if not self.inrunnerCompoundPlanetaryGearbox.geometricConstraint():
            print("Geometric constraint not satisfied")
            return
        if not self.inrunnerCompoundPlanetaryGearbox.meshingConstraint():
            print("Meshing constraint not satisfied")
            return
        if not self.inrunnerCompoundPlanetaryGearbox.noPlanetInterferenceConstraint():
            print("No planet interference constraint not satisfied")
            return

        Ns          = self.inrunnerCompoundPlanetaryGearbox.Ns
        NpBig       = self.inrunnerCompoundPlanetaryGearbox.NpBig
        NpSmall     = self.inrunnerCompoundPlanetaryGearbox.NpSmall
        Nr          = self.inrunnerCompoundPlanetaryGearbox.Nr
        numPlanet   = self.inrunnerCompoundPlanetaryGearbox.numPlanet
        moduleBig   = self.inrunnerCompoundPlanetaryGearbox.moduleBig
        moduleSmall = self.inrunnerCompoundPlanetaryGearbox.moduleSmall

        wSun     = self.motor.getMaxMotorAngVelRadPerSec()
        wPlanet  = (-Ns / (NpBig + NpSmall) ) * wSun
        wCarrier = wSun/self.inrunnerCompoundPlanetaryGearbox.gearRatio()

        [Ft_sp, Ft_rp] = self.getToothForces(constraintCheck=False)

        # Lewis static load capacity
        _,_,CR_SP = self.inrunnerCompoundPlanetaryGearbox.contactRatio_sunPlanet()
        _,_,CR_PR = self.inrunnerCompoundPlanetaryGearbox.contactRatio_planetRing()

        qe1 = 1 / CR_SP
        qe2 = 1 / CR_PR

        # qk = 1.85 + 0.35 * (np.log(Ns) / np.log(100)) 
        qk1 = (7.65734266e-08 * Ns**4
             - 2.19500130e-05 * Ns**3
             + 2.33893357e-03 * Ns**2
             - 1.13320908e-01 * Ns
             + 4.44727778)
        qk2 = (7.65734266e-08 * NpSmall**4
             - 2.19500130e-05 * NpSmall**3
             + 2.33893357e-03 * NpSmall**2
             - 1.13320908e-01 * NpSmall
             + 4.44727778)
        
        # Lewis static load capacity
        bMin_sun_mit         = (self.FOS * Ft_sp * qe1 * qk1 / (self.inrunnerCompoundPlanetaryGearbox.maxGearAllowableStressPa * moduleBig * 0.001)) # m
        bMin_planetBig_mit   = (self.FOS * Ft_sp * qe1 * qk1 / (self.inrunnerCompoundPlanetaryGearbox.maxGearAllowableStressPa * moduleBig * 0.001))
        bMin_planetSmall_mit = (self.FOS * Ft_rp * qe2 * qk2 / (self.inrunnerCompoundPlanetaryGearbox.maxGearAllowableStressPa * moduleSmall * 0.001))
        bMin_ring_mit        = (self.FOS * Ft_rp * qe2 * qk2 / (self.inrunnerCompoundPlanetaryGearbox.maxGearAllowableStressPa * moduleSmall * 0.001))

        #------------- Contraint in planet to accomodate its bearings------------------------------------------
        if ((bMin_planetBig_mit + bMin_planetSmall_mit) * 1000 < (self.planet_bearing_width*2 + self.standard_clearance_1_5mm * 2 / 3)) : 
            if ((bMin_planetBig_mit) * 1000 < (self.planet_bearing_width + self.standard_clearance_1_5mm * 1 / 3)): 
                bMin_planetBig_mit = (self.planet_bearing_width + self.standard_clearance_1_5mm * 1 / 3) / 1000
            if ((bMin_planetSmall_mit) * 1000 < (self.planet_bearing_width + self.standard_clearance_1_5mm * 1 / 3)): 
                bMin_planetSmall_mit = (self.planet_bearing_width + self.standard_clearance_1_5mm * 1 / 3) / 1000
            bMin_ring_mit = bMin_planetSmall_mit # FT on both are same

        bMin_sun_mitMM         = bMin_sun_mit * 1000
        bMin_planetBig_mitMM   = bMin_planetBig_mit * 1000
        bMin_planetSmall_mitMM = bMin_planetSmall_mit * 1000
        bMin_ring_mitMM        = bMin_ring_mit * 1000


        self.inrunnerCompoundPlanetaryGearbox.setfwSunMM         ( bMin_sun_mit         * 1000)
        self.inrunnerCompoundPlanetaryGearbox.setfwPlanetBigMM   ( bMin_planetBig_mit   * 1000)
        self.inrunnerCompoundPlanetaryGearbox.setfwPlanetSmallMM ( bMin_planetSmall_mit * 1000)
        self.inrunnerCompoundPlanetaryGearbox.setfwRingMM        ( bMin_ring_mit        * 1000)

        return bMin_sun_mitMM, bMin_planetBig_mitMM, bMin_planetSmall_mitMM, bMin_ring_mitMM

    def AGMAStressAnalysisMinFacewidth(self):
        # Check if the constraints are satisfied
        if not self.inrunnerCompoundPlanetaryGearbox.geometricConstraint():
            print("Geometric constraint not satisfied")
            return
        if not self.inrunnerCompoundPlanetaryGearbox.meshingConstraint():
            print("Meshing constraint not satisfied")
            return
        if not self.inrunnerCompoundPlanetaryGearbox.noPlanetInterferenceConstraint():
            print("No planet interference constraint not satisfied")
            return

        Ns          = self.inrunnerCompoundPlanetaryGearbox.Ns
        NpBig       = self.inrunnerCompoundPlanetaryGearbox.NpBig
        NpSmall     = self.inrunnerCompoundPlanetaryGearbox.NpSmall
        Nr          = self.inrunnerCompoundPlanetaryGearbox.Nr
        numPlanet   = self.inrunnerCompoundPlanetaryGearbox.numPlanet
        moduleBig   = self.inrunnerCompoundPlanetaryGearbox.moduleBig
        moduleSmall = self.inrunnerCompoundPlanetaryGearbox.moduleSmall

        wSun     = self.motor.getMaxMotorAngVelRadPerSec()
        wPlanet  = (-Ns / (NpBig + NpSmall) ) * wSun
        wCarrier = wSun/self.inrunnerCompoundPlanetaryGearbox.gearRatio()

        pressureAngle = self.inrunnerCompoundPlanetaryGearbox.pressureAngleDEG

        [Wt_sp, Wt_rp] = self.getToothForces(constraintCheck=False)

        # T Krishna Rao - Design of Machine Elements - II pg.191
        # Modified Lewis Form Factor Y = pi*y for pressure angle = 20
        Y_sun         = (0.154 - 0.912 / Ns) * np.pi
        Y_planetBig   = (0.154 - 0.912 / NpBig) * np.pi
        Y_planetSmall = (0.154 - 0.912 / NpSmall) * np.pi
        Y_ring        = (0.154 - 0.912 / Nr) * np.pi

        V_sp = abs(self.inrunnerCompoundPlanetaryGearbox.getPCRadiusSunM() * wSun)
        V_rp = abs(wCarrier*(self.inrunnerCompoundPlanetaryGearbox.getPCRadiusSunM() + self.inrunnerCompoundPlanetaryGearbox.getPCRadiusPlanetBigM()) + 
                wPlanet*(self.inrunnerCompoundPlanetaryGearbox.getPCRadiusPlanetSmallM()))
        
        # AGMA 908-B89 pg.16
        # Kf Fatigue stress concentration factor
        H = 0.331 - (0.436 * np.pi * pressureAngle / 180)
        L = 0.324 - (0.492 * np.pi * pressureAngle / 180)
        M = 0.261 + (0.545 * np.pi * pressureAngle / 180)  
        # t -> tooth thickness, r -> fillet radius and l -> tooth height
        t_planetSmall = (13.5 * Y_planetSmall)**(1/2) * moduleSmall
        r_planetSmall = 0.3 * moduleSmall
        l_planetSmall = 2.25 * moduleSmall
        Kf_planetSmall = H + (t_planetSmall / r_planetSmall)**(L) * (t_planetSmall / l_planetSmall)**(M)

        t_planetBig = (13.5 * Y_planetBig)**(1/2) * moduleBig
        r_planetBig = 0.3 * moduleBig
        l_planetBig = 2.25 * moduleBig
        Kf_planetBig = H + (t_planetBig / r_planetBig)**(L) * (t_planetBig / l_planetBig)**(M)

        t_sun = (13.5 * Y_sun)**(1/2) * moduleBig
        r_sun = 0.3 * moduleBig
        l_sun = 2.25 * moduleBig
        Kf_sun = H + (t_sun / r_sun)**(L) * (t_sun / l_sun)**(M)

        t_ring = (13.5 * Y_ring)**(1/2) * moduleSmall
        r_ring = 0.3 * moduleSmall 
        l_ring = 2.25 * moduleSmall
        Kf_ring = H + (t_ring / r_ring)**(L) * (t_ring / l_ring)**(M)

        # Shigley's Mechanical Engineering Design 9th Edition pg.752
        # Yj Geometry factor
        Yj_planetSmall = Y_planetSmall/Kf_planetSmall
        Yj_planetBig = Y_planetBig/Kf_planetBig
        Yj_sun = Y_sun/Kf_sun
        Yj_ring = Y_ring/Kf_ring
        
        # Kv Dynamic factor
        # Shigley's Mechanical Engineering Design 9th Edition pg.756
        Qv = 7      # Quality numbers 3 to 7 will include most commercial-quality gears.
        B_planetSmall =  0.25*(12-Qv)**(2/3)
        A_planetSmall = 50 + 56*(1-B_planetSmall)
        Kv_planetSmall = ((A_planetSmall+np.sqrt(200*V_rp))/A_planetSmall)**B_planetSmall

        B_planetBig =  0.25*(12-Qv)**(2/3)
        A_planetBig = 50 + 56*(1-B_planetBig)
        Kv_planetBig = ((A_planetBig+np.sqrt(200*V_sp))/A_planetBig)**B_planetBig

        B_sun =  0.25*(12-Qv)**(2/3)
        A_sun = 50 + 56*(1-B_sun)
        Kv_sun = ((A_sun+np.sqrt(200*V_sp))/A_sun)**B_sun

        B_ring =  0.25*(12-Qv)**(2/3)
        A_ring = 50 + 56*(1-B_ring)
        Kv_ring = ((A_ring+np.sqrt(200*V_rp))/A_ring)**B_ring

        # Shigley's Mechanical Engineering Design 9th Edition pg.764
        # Ks Size factor (can be omitted if enough information is not available)
        Ks = 1
        
        # NPTEL Fatigue Consideration in Design lecture-7 pg.10 Table-7.4 (https://archive.nptel.ac.in/courses/112/106/112106137/)
        # Kh Load-distribution factor (0-50mm, less rigid mountings, less accurate gears)
        Kh_planet = 1.3
        Kh_sun = 1.3
        Kh_ring = 1.3

        # Shigley's Mechanical Engineering Design 9th Edition pg.764
        # Kb Rim-thickness factor (the gears have a uniform thickness)
        Kb = 1
        
        # AGMA bending stress equation (Shigley's Mechanical Engineering Design 9th Edition pg.746)  
        bMin_planetSmall = (self.FOS * Wt_rp * Kv_planetSmall * Ks * Kh_planet * Kb)/(moduleSmall * Yj_planetSmall * self.inrunnerCompoundPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        bMin_planetBig = (self.FOS * Wt_sp * Kv_planetBig * Ks * Kh_planet * Kb)/(moduleBig * Yj_planetBig * self.inrunnerCompoundPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        bMin_sun = (self.FOS * Wt_sp * Kv_sun * Ks * Kh_sun * Kb) / (moduleBig * Yj_sun * self.inrunnerCompoundPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        bMin_ring = (self.FOS * Wt_rp * Kv_ring * Ks * Kh_ring * Kb) / (moduleSmall * Yj_ring * self.inrunnerCompoundPlanetaryGearbox.maxGearAllowableStressPa * 0.001)

        if bMin_ring < bMin_planetSmall:
            bMin_ring = bMin_planetSmall
        else:
            bMin_planetSmall = bMin_ring

        self.inrunnerCompoundPlanetaryGearbox.setfwSunMM(bMin_sun*1000)
        self.inrunnerCompoundPlanetaryGearbox.setfwPlanetBigMM(bMin_planetBig*1000)
        self.inrunnerCompoundPlanetaryGearbox.setfwPlanetSmallMM(bMin_planetSmall*1000)
        self.inrunnerCompoundPlanetaryGearbox.setfwRingMM(bMin_ring*1000)

    def updateFacewidth(self):
        if self.stressAnalysisMethodName == "Lewis":
            self.lewisStressAnalysisMinFacewidth()
        elif self.stressAnalysisMethodName == "AGMA":
            self.AGMAStressAnalysisMinFacewidth()
        elif self.stressAnalysisMethodName == "MIT":
            self.mitStressAnalysisMinFacewidth()

    def getMassKG_3DP(self):
        module1   = self.inrunnerCompoundPlanetaryGearbox.moduleBig  # Module of the gear
        module2   = self.inrunnerCompoundPlanetaryGearbox.moduleSmall  # Module of the gear
        Ns        = self.inrunnerCompoundPlanetaryGearbox.Ns
        Np1       = self.inrunnerCompoundPlanetaryGearbox.NpBig
        Np2       = self.inrunnerCompoundPlanetaryGearbox.NpSmall
        Nr        = self.inrunnerCompoundPlanetaryGearbox.Nr
        numPlanet = self.inrunnerCompoundPlanetaryGearbox.numPlanet

        #-----------------------------------------
        # Density
        #-----------------------------------------
        density_3DP_material = self.inrunnerCompoundPlanetaryGearbox.densityGears
        density_aluminum     = self.inrunnerCompoundPlanetaryGearbox.densityAluminum

        #-----------------------------------------
        # Face Width
        #-----------------------------------------
        sunFwMM     = self.inrunnerCompoundPlanetaryGearbox.fwSunMM
        planet1FwMM = self.inrunnerCompoundPlanetaryGearbox.fwPlanetBigMM
        planet2FwMM = self.inrunnerCompoundPlanetaryGearbox.fwPlanetSmallMM + self.standard_clearance_1_5mm
        ringFwMM    = self.inrunnerCompoundPlanetaryGearbox.fwRingMM + self.standard_clearance_1_5mm

        sunFwM     = sunFwMM     * 1000 # TODO: check the order of the index order should be always sun, planet1, planet2, ring
        planet1FwM = planet1FwMM * 1000
        planet2FwM = planet2FwMM * 1000
        ringFwM    = ringFwMM    * 1000

        #-----------------------------------------
        # Diameter and Radius
        #-----------------------------------------
        DiaSunMM        = Ns  * module1
        DiaPlanet1MM    = Np1 * module1
        DiaPlanet2MM    = Np2 * module2
        DiaRingMM       = Nr  * module2

        RadiusSunMM     = DiaSunMM     * 0.5
        RadiusPlanet1MM = DiaPlanet1MM * 0.5
        RadiusPlanet2MM = DiaPlanet2MM * 0.5
        RadiusRingMM    = DiaRingMM    * 0.5

        RingOuterRadiusMM = RadiusRingMM + 1.25*module2 + self.inrunnerCompoundPlanetaryGearbox.ringRadialWidthMM

        #-----------------------------------------
        # Bearing Selection
        #-----------------------------------------
        OutputIdrequiredMM      = module1 * (Ns + Np1) + self.bearingIDClearanceMM
        OutputBearings          = bearings_discrete(OutputIdrequiredMM)
        OutputInnerDiaBearingMM = OutputBearings.getBearingIDMM()
        OutputOuterDiaBearingMM = OutputBearings.getBearingODMM()
        OutputWidthBearingMM    = OutputBearings.getBearingWidthMM()
        OutputBearingMassKG     = OutputBearings.getBearingMassKG()

       
        RotorTopBearingIDrequiredMM   = self.rotor_top_bearing_ID 
        RotorTopBearings              = bearings_discrete(RotorTopBearingIDrequiredMM)
        RotorTopBearingMassKG         = RotorTopBearings.getBearingMassKG()

        #======================================
        # Mass Calculation
        #======================================
        #--------------------------------------
        # Independent variables
        #--------------------------------------
        # To be written in Gearbox(cpg) JSON files
        case_mounting_surface_height   = self.case_mounting_surface_height
        standard_clearance_1_5mm       = self.standard_clearance_1_5mm    
        motor_case_thickness           = self.motor_case_thickness        
        clearance_planet               = self.clearance_planet            
        output_mount_hole_dia          = self.output_mount_hole_dia    
        sec_carrier_thickness          = self.sec_carrier_thickness       
        sun_coupler_hub_thickness      = self.sun_coupler_hub_thickness   
        sun_shaft_bearing_OD           = self.sun_shaft_bearing_OD        
        bearing_step_width             = self.bearing_step_width  
        planet_bearing_ID              = self.planet_bearing_ID            
        sun_shaft_bearing_ID           = self.sun_shaft_bearing_ID        
        sun_shaft_bearing_width        = self.sun_shaft_bearing_width     
        motor_case_OD_base_to_chamfer  = self.motor_case_OD_base_to_chamfer #5
        ring_gearbox_casing_thickness  = self.ring_gearbox_casing_thickness

        #--------------------------------------
        # Dependent variables
        #--------------------------------------
        h_b1 = 1.25 * module1
        h_b2 = 1.25 * module2

        fw_s_used = bearing_step_width + sec_carrier_thickness + clearance_planet + planet1FwMM + planet2FwMM

        #--------------------------------------
        # Mass: incpg_motor_casing
        #--------------------------------------
        ring_radial_thickness = self.ringRadialWidthMM
        ring_OD  = Nr * module2 + module2 + ring_radial_thickness*2

        motor_OD          = self.motorDiaMM
        motor_case_ID     = motor_OD
        motor_height      = self.motorLengthMM
        motor_case_height = self.stator_bottom_height + self.stator_mid_height + standard_clearance_1_5mm/2

        motor_case_OD = motor_case_ID + motor_case_thickness * 2

        motor_case_base_ID = self.rotor_bottom_bearing_OD

        motor_case_bearing_structure_height = self.rotor_bottom_bearing_width + bearing_step_width - motor_case_thickness
        motor_case_bearing_structure_OD     = motor_case_base_ID + 2*(standard_clearance_1_5mm/3 + standard_clearance_1_5mm + self.motor_mount_driver_nut_wrench_size)

        motor_case_volume = (  np.pi * (((motor_case_OD * 0.5)**2)-(motor_case_base_ID * 0.5)**2) * motor_case_thickness 
                            + np.pi * ((motor_case_OD * 0.5)**2 - (motor_case_ID * 0.5)**2) * motor_case_height
        ) * 1e-9

        motor_case_mass = motor_case_volume * density_3DP_material

        #--------------------------------------
        # Mass: incpg_gearbox_casing
        #--------------------------------------
        # Mass of the gearbox includes the mass of: 
        # 1. Ring gear
        # 2. Bearing holding structure
        # 3. Case mounting structure
        #--------------------------------------
        ring_ID      = Nr * module2
        ringFwUsedMM = ringFwMM

        output_bearing_ID     = OutputInnerDiaBearingMM 
        output_bearing_OD     = OutputOuterDiaBearingMM 
        output_bearing_width = OutputWidthBearingMM    
        output_bearing_mass   = OutputBearingMassKG      
  
        bearing_holding_structure_OD     = output_bearing_OD + 2*self.actuactor_mount_nut_wrench_size + 2*standard_clearance_1_5mm
        bearing_holding_structure_ID     = output_bearing_OD 
        bearing_holding_structure_height = output_bearing_width + bearing_step_width

        case_mounting_structure_OD     = (Ns+2*Np1)*module1 + 2*standard_clearance_1_5mm + 2*ring_gearbox_casing_thickness
        case_mounting_structure_ID     = case_mounting_structure_OD - 2*ring_gearbox_casing_thickness
        case_mounting_structure_height =(self.rotor_hub_height + sun_coupler_hub_thickness+ bearing_step_width/2
                                         + self.rotor_top_bearing_width + fw_s_used - planet2FwMM +
                                        standard_clearance_1_5mm - standard_clearance_1_5mm/2 - self.stator_top_height - self.stator_mid_height)           
        
        gearbox_casing_bottom_height = self.stator_top_height + standard_clearance_1_5mm/2

        if bearing_holding_structure_OD > case_mounting_structure_OD:
            ring_OD_used = bearing_holding_structure_OD
            ring_casing_chamfer_ID = case_mounting_structure_OD
            ring_casing_chamfer_OD = bearing_holding_structure_OD
        else:
            ring_OD_used = case_mounting_structure_OD
            ring_casing_chamfer_OD = case_mounting_structure_OD
            ring_casing_chamfer_ID = bearing_holding_structure_OD

        ring_casing_chamfer_height = ringFwUsedMM - ring_gearbox_casing_thickness/2

        ring_volume                      = np.pi * (((ring_OD_used*0.5)**2) - ((ring_ID)*0.5)**2) * ringFwUsedMM * 1e-9
        bearing_holding_structure_volume = np.pi * (((bearing_holding_structure_OD*0.5)**2) - 
                                                    ((bearing_holding_structure_ID*0.5)**2)) * bearing_holding_structure_height * 1e-9
        case_mounting_structure_volume   = np.pi * (((case_mounting_structure_OD*0.5)**2) - 
                                                    ((case_mounting_structure_ID*0.5)**2)) * case_mounting_structure_height * 1e-9
        case_mounting_plate_volume       = np.pi * (((motor_case_OD*0.5)**2) - 
                                                    ((case_mounting_structure_ID*0.5)**2)) * motor_case_thickness * 1e-9
        ring_casing_chamfer_volume       = 0.5* np.pi * (((ring_casing_chamfer_OD*0.5)**2) -
                                                    ((ring_casing_chamfer_ID*0.5)**2)) * ring_casing_chamfer_height * 1e-9
        gearbox_casing_bottom_volume = np.pi * (((motor_case_OD*0.5)**2) - ((motor_case_ID*0.5)**2)) * gearbox_casing_bottom_height * 1e-9
        
        large_fillet_ID     = case_mounting_structure_OD
        
        if (motor_OD - case_mounting_structure_OD) > (standard_clearance_1_5mm + planet1FwMM + clearance_planet + sec_carrier_thickness) / 2 :
            large_fillet_height = (standard_clearance_1_5mm + planet1FwMM + clearance_planet + sec_carrier_thickness) / 2
        else:
            large_fillet_height = motor_OD - case_mounting_structure_OD

        large_fillet_OD     = case_mounting_structure_OD + 2 * large_fillet_height
        large_fillet_volume = 0.2146  * (np.pi * (((large_fillet_OD*0.5)**2) - ((large_fillet_ID)*0.5)**2) * large_fillet_height) * 1e-9

    
        gearbox_casing_volume = ring_volume + bearing_holding_structure_volume + case_mounting_structure_volume + case_mounting_plate_volume  - ring_casing_chamfer_volume + gearbox_casing_bottom_volume# + large_fillet_volume(accomated in the air vents in motor casing) 
        gearbox_casing_mass = gearbox_casing_volume * density_3DP_material

        #----------------------------------
        # Mass: cpg_carrier
        #----------------------------------
        carrier_OD     = output_bearing_ID
        carrier_ID     = sun_shaft_bearing_OD - standard_clearance_1_5mm * 2
        carrier_height = output_bearing_width + bearing_step_width

        carrier_shaft_OD = planet_bearing_ID 
        carrier_shaft_height = planet1FwMM  + planet2FwMM + clearance_planet * 2
        carrier_shaft_num = numPlanet * 2 #+ numPlanet # assuming triangular support is twice the mass of shaft

        carrier_volume = (np.pi * (((carrier_OD*0.5)**2) - ((carrier_ID)*0.5)**2) * carrier_height
                        + np.pi * ((carrier_shaft_OD*0.5)**2) * carrier_shaft_height * carrier_shaft_num) * 1e-9

        carrier_mass = carrier_volume * density_3DP_material

        #----------------------------------
        # Mass: cpg_sun
        #----------------------------------
        # Mass of the sun includes the mass of: 
        # 1. sun hub
        # 2. sun gear
        # 3. sun shaft
        # 4. sun magnet mount shaft
        #--------------------------------------
        sun_hub_dia = self.rotor_ID - 2*self.rotor_hub_thickness - 2*standard_clearance_1_5mm
        
        sun_rotor_top_bearing_structure_dia = self.rotor_top_bearing_ID
        sun_rotor_top_bearing_structure_height = bearing_step_width/2 + self.rotor_top_bearing_width
        
        sun_shaft_dia    = sun_shaft_bearing_ID
        sun_shaft_height = sun_shaft_bearing_width + bearing_step_width

        sun_rotor_bottom_bearing_structure_dia    = self.rotor_bottom_bearing_ID
        sun_rotor_bottom_bearing_structure_height = self.rotor_hub_height + self.stator_bottom_height + motor_case_thickness - bearing_step_width 

        sun_hub_volume   = np.pi * ((sun_hub_dia*0.5) ** 2) * sun_coupler_hub_thickness * 1e-9
        sun_rotor_top_bearing_structure_volume = np.pi * ((sun_rotor_top_bearing_structure_dia*0.5) ** 2) * sun_rotor_top_bearing_structure_height * 1e-9
        sun_gear_volume = np.pi * ((DiaSunMM*0.5) ** 2) * fw_s_used * 1e-9
        sun_shaft_volume = np.pi * ((sun_shaft_dia*0.5) ** 2) * sun_shaft_height * 1e-9
        sun_rotor_bottom_bearing_structure_volume = np.pi * ((sun_rotor_bottom_bearing_structure_dia*0.5) ** 2) * sun_rotor_bottom_bearing_structure_height * 1e-9
        central_bolt_volume = (np.pi * ((self.sun_central_bolt_dia*0.5)**2)
                                *(fw_s_used+sun_shaft_height+sun_rotor_top_bearing_structure_height+sun_coupler_hub_thickness+sun_rotor_bottom_bearing_structure_height))* 1e-9

        sun_volume       = sun_hub_volume + sun_rotor_top_bearing_structure_volume+ sun_gear_volume + sun_shaft_volume + sun_rotor_bottom_bearing_structure_volume - central_bolt_volume
        sun_mass         = sun_volume * density_3DP_material

        #--------------------------------------
        # Mass: incpg_planet
        #--------------------------------------
        planet_bore = planet_bearing_ID + standard_clearance_1_5mm 
        planet1_volume = (np.pi * ((DiaPlanet1MM*0.5)**2 - (planet_bore*0.5)**2) * planet1FwMM) * 1e-9
        planet2_volume = (np.pi * ((DiaPlanet2MM*0.5)**2 - (planet_bore*0.5)**2) * planet2FwMM) * 1e-9
        planet_mass   = (planet1_volume + planet2_volume) * density_3DP_material

        #--------------------------------------
        # Mass: incpg_sec_carrier
        #--------------------------------------
        sec_carrier_top_OD = output_bearing_ID
        sec_carrier_top_ID = (DiaSunMM + DiaPlanet1MM) - self.planet_pin_nut_wrench_size - 2*standard_clearance_1_5mm
        sec_carrier_top_thickness = sec_carrier_thickness 

        sec_carrier_bottom_OD = self.rotor_top_bearing_OD + 2*standard_clearance_1_5mm*3 
        sec_carrier_bottom_ID = self.rotor_top_bearing_OD
        sec_carrier_bottom_thickness = self.rotor_top_bearing_width + bearing_step_width 

        sec_carrier_volume = ((np.pi * ((sec_carrier_top_OD*0.5)**2 - (sec_carrier_top_ID*0.5)**2) * sec_carrier_top_thickness)
                            +(np.pi * ((sec_carrier_bottom_OD*0.5)**2 - (sec_carrier_bottom_ID*0.5)**2) * sec_carrier_bottom_thickness)) * 1e-9
        sec_carrier_mass   = sec_carrier_volume * density_3DP_material
        
        #--------------------------------------
        # Mass: rotor_hub
        #--------------------------------------
        # Mass of the rotor_hub includes the mass of: 
        # 1. base hub
        # 2. Top bearing holding structure
        # 3. Bottom bearing holding structure
        #--------------------------------------
        rotor_base_hub_OD = self.rotor_ID
        rotor_base_hub_ID = self.rotor_bottom_bearing_ID + 2*standard_clearance_1_5mm
        rotor_base_hub_height = self.rotor_hub_height

        rotor_hub_thickness = self.rotor_hub_thickness

        rotor_top_hub_ID = rotor_base_hub_OD - 2*rotor_hub_thickness
        rotor_top_hub_height = rotor_base_hub_height

        rotor_bottom_hub_OD = self.rotor_OD
        rotor_bottom_hub_ID = rotor_top_hub_ID
        rotor_bottom_hub_height = rotor_hub_thickness

        rotor_base_hub_volume = np.pi * ((rotor_base_hub_OD*0.5)**2 - (rotor_base_hub_ID*0.5)**2) * rotor_base_hub_height * 1e-9
        rotor_top_hub_volume = np.pi * ((rotor_base_hub_OD*0.5)**2 
                                          - (rotor_top_hub_ID*0.5)**2) * rotor_top_hub_height * 1e-9
        rotor_bottom_hub_volume = np.pi * ((rotor_bottom_hub_OD*0.5)**2 
                                             - (rotor_bottom_hub_ID*0.5)**2) * rotor_bottom_hub_height * 1e-9
        
        rotor_hub_volume = rotor_base_hub_volume + rotor_top_hub_volume #+ rotor_bottom_hub_volume(Commented out to accomodate for the holes in hub)
        rotor_hub_mass = rotor_hub_volume * density_aluminum
       
        #--------------------------------------
        # Mass: incpg_rotor_top_bearing
        #--------------------------------------
        rotor_top_bearing_mass =  RotorTopBearingMassKG

        #--------------------------------------
        # Mass: incpg_rotor_bottom_bearing
        #--------------------------------------
        rotor_bottom_bearing_mass = 0.007 # kg

        #--------------------------------------
        # Mass: incpg_sun_shaft_bearing
        #--------------------------------------
        sun_shaft_bearing_mass       = 4 * 0.001 # kg

        #--------------------------------------
        # Mass: incpg_planet_bearing
        #--------------------------------------
        planet_bearing_mass          = 1 * 0.001 # kg
        planet_bearing_num           = numPlanet * 2
        planet_bearing_combined_mass = planet_bearing_mass * planet_bearing_num

        #--------------------------------------
        # Mass: incpg_output_bearing
        #--------------------------------------
        output_bearing_mass = OutputBearingMassKG # kg

        #--------------------------------------
        # Mass: incpg_bearing_retainer
        #--------------------------------------
        bearing_retainer_OD        = bearing_holding_structure_OD
        bearing_retainer_ID        = output_bearing_OD - standard_clearance_1_5mm * 2

        bearing_retainer_volume = (np.pi * ((bearing_retainer_OD*0.5)**2 - (bearing_retainer_ID*0.5)**2) * bearing_step_width) * 1e-9

        bearing_retainer_mass   = bearing_retainer_volume * density_3DP_material

        self.motor_case_mass                    = motor_case_mass
        self.gearbox_casing_mass                = gearbox_casing_mass
        self.carrier_mass                       = carrier_mass
        self.sun_mass                           = sun_mass
        self.sec_carrier_mass                   = sec_carrier_mass
        self.planet_mass                        = planet_mass
        self.rotor_hub_mass                     = rotor_hub_mass
        self.rotor_top_bearing_mass             = rotor_top_bearing_mass
        self.rotor_bottom_bearing_mass          = rotor_bottom_bearing_mass
        self.planet_bearing_combined_mass       = planet_bearing_combined_mass
        self.sun_shaft_bearing_mass             = sun_shaft_bearing_mass
        self.output_bearing_mass                = output_bearing_mass
        self.bearing_retainer_mass              = bearing_retainer_mass
        

        #----------------------------------------
        # Total Actuator Mass
        #----------------------------------------

        Actuator_mass = (self.motorMassKG 
                        + self.motor_case_mass 
                        + self.gearbox_casing_mass 
                        + self.carrier_mass 
                        + self.sun_mass 
                        + self.sec_carrier_mass 
                        + self.rotor_hub_mass
                        + self.planet_mass * numPlanet
                        + self.rotor_top_bearing_mass
                        + self.rotor_bottom_bearing_mass 
                        + self.planet_bearing_combined_mass 
                        + self.sun_shaft_bearing_mass 
                        + self.output_bearing_mass 
                        + self.bearing_retainer_mass)

        Actuator_mass_without_bearing = (self.motor_case_mass 
                                        + self.gearbox_casing_mass
                                        + self.carrier_mass 
                                        + self.sun_mass 
                                        + self.sec_carrier_mass 
                                        + self.rotor_hub_mass
                                        + self.planet_mass * numPlanet 
                                        + self.bearing_retainer_mass
                                        )
        
        self.Actuator_mass = Actuator_mass
        self.Actuator_mass_without_bearing = Actuator_mass_without_bearing

        return Actuator_mass

    def print_mass_of_parts_3DP(self):
        print("motor_case_mass: ",                 1000 * self.motor_case_mass)
        print("gearbox_casing_mass: ",             1000 * self.gearbox_casing_mass)
        print("carrier_mass: ",                    1000 * self.carrier_mass)
        print("sun_mass: ",                        1000 * self.sun_mass)
        print("sec_carrier_mass: ",                1000 * self.sec_carrier_mass)
        print("planet_mass: ",                     1000 * self.planet_mass)
        print("rotor_hub_mass: ",                  1000 * self.rotor_hub_mass)
        print("planet_bearing_combined_mass: ",    1000 * self.planet_bearing_combined_mass)
        print("sun_shaft_bearing_mass: ",          1000 * self.sun_shaft_bearing_mass)
        print("output_bearing_mass: ",             1000 * self.output_bearing_mass)
        print("bearing_retainer_mass: ",           1000 * self.bearing_retainer_mass)
        print("rotor_top_bearing_mass: ",          1000 * self.rotor_top_bearing_mass)
        print("rotor_bottom_bearing_mass: ",       1000 * self.rotor_bottom_bearing_mass)
        print("Motor mass:",                       1000 * self.motorMassKG)

        print("Actuator_mass_without_bearing:",    1000 * self.Actuator_mass_without_bearing)
        print("Actuator_mass:",                    1000 * self.Actuator_mass)

        print("---------------------------------------------------")
        
class optimizationInrunnerCompoundPlanetaryActuator:
    def __init__(self,
                 design_parameters,
                 gear_standard_parameters,
                 K_Mass                     = 2,
                 K_Eff                      = -1,
                 K_Width                    = 0.2,
                 MODULE_BIG_MIN             = 0.8,
                 MODULE_BIG_MAX             = 1.2,
                 MODULE_SMALL_MIN           = 0.8,
                 MODULE_SMALL_MAX           = 1.2,
                 NUM_PLANET_MIN             = 3,
                 NUM_PLANET_MAX             = 5,
                 NUM_TEETH_SUN_MIN          = 20,
                 NUM_TEETH_PLANET_BIG_MIN   = 20,
                 NUM_TEETH_PLANET_SMALL_MIN = 20,
                 GEAR_RATIO_MIN             = 5,
                 GEAR_RATIO_MAX             = 30,
                 GEAR_RATIO_STEP            = 1):
        
        self.K_Mass                     = K_Mass
        self.K_Eff                      = K_Eff
        self.K_Width                    = K_Width
        self.MODULE_BIG_MIN             = MODULE_BIG_MIN
        self.MODULE_BIG_MAX             = MODULE_BIG_MAX
        self.MODULE_SMALL_MIN           = MODULE_SMALL_MIN
        self.MODULE_SMALL_MAX           = MODULE_SMALL_MAX
        self.NUM_PLANET_MIN             = NUM_PLANET_MIN
        self.NUM_PLANET_MAX             = NUM_PLANET_MAX
        self.NUM_TEETH_SUN_MIN          = NUM_TEETH_SUN_MIN
        self.NUM_TEETH_PLANET_BIG_MIN   = NUM_TEETH_PLANET_BIG_MIN
        self.NUM_TEETH_PLANET_SMALL_MIN = NUM_TEETH_PLANET_SMALL_MIN
        self.GEAR_RATIO_MIN             = GEAR_RATIO_MIN
        self.GEAR_RATIO_MAX             = GEAR_RATIO_MAX
        self.GEAR_RATIO_STEP            = GEAR_RATIO_STEP

        self.Cost                    = 100000
        self.totalGearboxesWithReqGR = 0
        self.totalFeasibleGearboxes  = 0
        self.cntrIterBeforeCons      = 0
        self.iter                    = 1
        self.gearRatioIter           = GEAR_RATIO_MIN
        self.UsePSCasVariable        = 1 # Default Yes

        self.gear_standard_parameters = gear_standard_parameters
        self.design_parameters        = design_parameters
        self.gearRatioReq             = 0
    
    def printOptimizationParameters(self, Actuator=inrunnerCompoundPlanetaryActuator, log=1, csv=0):
        # Motor Parameters
        maxMotorAngVelRPM       = Actuator.motor.maxMotorAngVelRPM
        maxMotorAngVelRadPerSec = Actuator.motor.maxMotorAngVelRadPerSec
        maxMotorTorque          = Actuator.motor.maxMotorTorque
        maxMotorPower           = Actuator.motor.maxMotorPower
        motorMass               = Actuator.motor.massKG
        motorDia                = Actuator.motor.motorDiaMM
        motorLength             = Actuator.motor.motorLengthMM
        
        # Planetary Gearbox Parameters
        maxGearAllowableStressMPa = Actuator.inrunnerCompoundPlanetaryGearbox.maxGearAllowableStressMPa
        
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
            print("K_Mass:                     ", self.K_Mass)
            print("K_Eff:                      ", self.K_Eff)
            print("MODULE_BIG_MIN:             ", self.MODULE_BIG_MIN)
            print("MODULE_BIG_MAX:             ", self.MODULE_BIG_MAX)
            print("MODULE_SMALL_MIN:           ", self.MODULE_SMALL_MIN)
            print("MODULE_SMALL_MAX:           ", self.MODULE_SMALL_MAX)
            print("NUM_PLANET_MIN:             ", self.NUM_PLANET_MIN)
            print("NUM_PLANET_MAX:             ", self.NUM_PLANET_MAX)
            print("NUM_TEETH_SUN_MIN:          ", self.NUM_TEETH_SUN_MIN)
            print("NUM_TEETH_PLANET_BIG_MIN:   ", self.NUM_TEETH_PLANET_BIG_MIN)
            print("NUM_TEETH_PLANET_SMALL_MIN: ", self.NUM_TEETH_PLANET_SMALL_MIN)
            print("GEAR_RATIO_MIN:             ", self.GEAR_RATIO_MIN)
            print("GEAR_RATIO_MAX:             ", self.GEAR_RATIO_MAX)
            print("GEAR_RATIO_STEP:            ", self.GEAR_RATIO_STEP)
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
            print("K_mass, K_Eff, MODULE_BIG_MIN, MODULE_BIG_MAX, MODULE_SMALL_MIN, MODULE_SMALL_MAX, NUM_PLANET_MIN, NUM_PLANET_MAX, NUM_TEETH_SUN_MIN, NUM_TEETH_PLANET_BIG_MIN, NUM_TEETH_PLANET_SMALL_MIN, GEAR_RATIO_MIN, GEAR_RATIO_MAX, GEAR_RATIO_STEP")
            print(self.K_Mass,",", self.K_Eff,",", self.MODULE_BIG_MIN,",", self.MODULE_BIG_MAX,",", self.MODULE_SMALL_MIN,",", self.MODULE_SMALL_MAX,",",self.NUM_PLANET_MIN,",", self.NUM_PLANET_MAX,",", self.NUM_TEETH_SUN_MIN,",", self.NUM_TEETH_PLANET_BIG_MIN,",",self.NUM_TEETH_PLANET_SMALL_MIN,",", self.GEAR_RATIO_MIN,",", self.GEAR_RATIO_MAX,",", self.GEAR_RATIO_STEP)
        
    def printOptimizationResults(self, Actuator=inrunnerCompoundPlanetaryActuator, log=1, csv=0):
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
            iter       = self.iter
            gearRatio       = Actuator.inrunnerCompoundPlanetaryGearbox.gearRatio()
            moduleBig       = Actuator.inrunnerCompoundPlanetaryGearbox.moduleBig
            moduleSmall     = Actuator.inrunnerCompoundPlanetaryGearbox.moduleSmall
            Ns              = Actuator.inrunnerCompoundPlanetaryGearbox.Ns 
            NpBig           = Actuator.inrunnerCompoundPlanetaryGearbox.NpBig
            NpSmall         = Actuator.inrunnerCompoundPlanetaryGearbox.NpSmall 
            Nr              = Actuator.inrunnerCompoundPlanetaryGearbox.Nr 
            numPlanet       = Actuator.inrunnerCompoundPlanetaryGearbox.numPlanet
            fwSunMM         = round(Actuator.inrunnerCompoundPlanetaryGearbox.fwSunMM    , 3)
            fwPlanetBigMM   = round(Actuator.inrunnerCompoundPlanetaryGearbox.fwPlanetBigMM , 3)
            fwPlanetSmallMM = round(Actuator.inrunnerCompoundPlanetaryGearbox.fwPlanetSmallMM , 3)
            fwRingMM        = round(Actuator.inrunnerCompoundPlanetaryGearbox.fwRingMM   , 3)
            if self.UsePSCasVariable == 1 :
                Opt_PSC_ring                 = self.cspgOpt.model.PSCr.value
                Opt_PSC_planetBig            = self.cspgOpt.model.PSCp1.value
                Opt_PSC_planetSmall          = self.cspgOpt.model.PSCp2.value
                Opt_PSC_sun                  = self.cspgOpt.model.PSCs.value
                CenterDist_SP, CenterDist_PR = self.cspgOpt.getCenterDistance(Var = False)
            else :
                Opt_PSC_ring   = 0
                Opt_PSC_planetBig = 0
                Opt_PSC_planetSmall = 0
                Opt_PSC_sun   = 0
                CenterDist_SP = ((Ns + NpBig)/2)* moduleBig
                CenterDist_PR = ((Nr - NpSmall)/2)* moduleSmall

            mass            = round(Actuator.getMassKG_3DP(), 3)
            eff             = round(Actuator.inrunnerCompoundPlanetaryGearbox.getEfficiency(), 3)
            peakTorque      = round(Actuator.motor.getMaxMotorTorque()*Actuator.inrunnerCompoundPlanetaryGearbox.gearRatio(), 3)
            
            tooth_forces    = Actuator.getToothForces()
            Torque_Density  = round(peakTorque/mass, 3)
            
            if self.UsePSCasVariable == 1 : 
                eff  = round(self.cspgOpt.getEfficiency(Var=False), 3)
            
            Cost = self.cost(Actuator=Actuator)
            Output_bearing_mass = Actuator.output_bearing_mass
            Actuator_width = Actuator.actuator_width
            print(iter, ",", gearRatio, ",", moduleBig, ",", moduleSmall, ",", Ns, ",", NpBig, ",", NpSmall, ",", Nr, ",", numPlanet, ",", fwSunMM, ",", fwPlanetBigMM, ",", fwPlanetSmallMM, ",", fwRingMM, ",", mass, ",", eff, ",", peakTorque, ",", Cost, ",", Torque_Density, ",", Output_bearing_mass, ",", Actuator_width)

    def optimizeActuator(self, Actuator=inrunnerCompoundPlanetaryActuator, UsePSCasVariable = 0, log=1, csv=0, printOptParams=1, gearRatioReq = 0):   
        self.UsePSCasVariable = UsePSCasVariable
        totalTime = 0
        self.gearRatioReq = gearRatioReq
        opt_parameters = None
        if UsePSCasVariable == 0:
            totalTime, opt_parameters = self.optimizeActuatorWithoutPSC(Actuator=Actuator, log=log, csv=csv,printOptParams=printOptParams)
        elif UsePSCasVariable == 1:
            totalTime = self.optimizeActuatorWithPSC(Actuator=Actuator, log=log, csv=csv,printOptParams=printOptParams)
        else:
            totalTime = 0
            print("ERROR: \"UsePSCasVariable\" can be either 0 or 1")

        return totalTime, opt_parameters
    
    def optimizeActuatorWithoutPSC(self, Actuator=inrunnerCompoundPlanetaryActuator, log=1, csv=0, printOptParams=1):
        startTime = time.time()
        opt_parameters = None
        if csv and log:
            print("WARNING: Both csv and Log cannot be true")
            print("WARNING: Please set either csv or log to be 0 in \"Optimizer.optimizeActuator(Actuator)\" function")
            print(" ")
            print("Making log to be false and csv to be true")
            log = 0
            csv = 1
        elif not csv and not log:
            print("WARNING: Both csv and Log cannot be false")
            print("WARNING: Please set either csv or log to be 1 in \"Optimizer.optimizeActuator(Actuator)\" function")
            print(" ")
            print("Making log to be False and csv to be true")
            log = 0
            csv = 1
        
        if csv:
            fileName = f"./results/results_BruteForce_{Actuator.motor.motorName}/INCPG_BRUTEFORCE_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}.csv"
        elif log:
            fileName = f"./results/results_BruteForce_{Actuator.motor.motorName}/INCPG_BRUTEFORCE_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}_LOG.txt"
        
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
                # print("iter, gearRatio, moduleBig, moduleSmall, Ns, NpBig, NpSmall, Nr, numPlanet, fwSunMM, fwPlanetBigMM, fwPanetSmallMM, fwRingMM, PSCs, PSCp1, PSCp2, PSCr, CD_SP, CD_PR, mass, eff, peakTorque, Cost, tooth_forces_sp, tooth_forces_rp, Torque_Density")
                # print("iter, gearRatio, moduleBig, moduleSmall, Ns, NpBig, NpSmall, Nr, numPlanet, fwSunMM, fwPlanetBigMM, fwPanetSmallMM, fwRingMM, mass, eff, peakTorque, Cost, tooth_forces_sp, tooth_forces_rp, Torque_Density")
                print("iter, gearRatio, moduleBig, moduleSmall, Ns, NpBig, NpSmall, Nr, numPlanet, fwSunMM, fwPlanetBigMM, fwPanetSmallMM, fwRingMM, mass, eff, peakTorque, Cost, Torque_Density, Output_bearing_mass, Actuator_width")

            while self.gearRatioIter <= self.GEAR_RATIO_MAX:
                opt_done  = 0
                self.iter = 0
                self.Cost = 100000
                MinCost   = self.Cost
                Actuator.inrunnerCompoundPlanetaryGearbox.setModuleBig(self.MODULE_BIG_MIN)
                while Actuator.inrunnerCompoundPlanetaryGearbox.moduleBig <= self.MODULE_BIG_MAX:
                    # Setting Module Small
                    Actuator.inrunnerCompoundPlanetaryGearbox.setModuleSmall(self.MODULE_SMALL_MIN)
                    while (Actuator.inrunnerCompoundPlanetaryGearbox.moduleSmall <= self.MODULE_SMALL_MAX):
                        # Setting Ns
                        Actuator.inrunnerCompoundPlanetaryGearbox.setNs(self.NUM_TEETH_SUN_MIN)
                        while (2*Actuator.inrunnerCompoundPlanetaryGearbox.getPCRadiusSunM()*1000) <= Actuator.maxGearboxDiameter:
                            # Setting Np Big
                            Actuator.inrunnerCompoundPlanetaryGearbox.setNpBig(self.NUM_TEETH_PLANET_BIG_MIN)
                            while (2*Actuator.inrunnerCompoundPlanetaryGearbox.getPCRadiusPlanetBigM()*1000) <= Actuator.maxGearboxDiameter/2:
                                # Setting Np Small
                                Actuator.inrunnerCompoundPlanetaryGearbox.setNpSmall(self.NUM_TEETH_PLANET_SMALL_MIN)
                                while (2*Actuator.inrunnerCompoundPlanetaryGearbox.getPCRadiusPlanetSmallM()*1000) <= (2*Actuator.inrunnerCompoundPlanetaryGearbox.getPCRadiusPlanetBigM()*1000):
                                    # Setting Nr
                                    Actuator.inrunnerCompoundPlanetaryGearbox.setNr(Actuator.inrunnerCompoundPlanetaryGearbox.NpSmall + 
                                                                            Actuator.inrunnerCompoundPlanetaryGearbox.NpBig +
                                                                            Actuator.inrunnerCompoundPlanetaryGearbox.Ns)
                                    # if (2*Actuator.inrunnerCompoundPlanetaryGearbox.getPCRadiusRingM()*1000) <= Actuator.maxGearboxDiameter:
                                    if (Actuator.inrunnerCompoundPlanetaryGearbox.getGearboxOuterDiaMaxM()*1000) <= Actuator.maxGearboxDiameter:
                                        # Setting number of Planet
                                        Actuator.inrunnerCompoundPlanetaryGearbox.setNumPlanet(self.NUM_PLANET_MIN)
                                        while Actuator.inrunnerCompoundPlanetaryGearbox.numPlanet <= self.NUM_PLANET_MAX:
                                            if (Actuator.inrunnerCompoundPlanetaryGearbox.geometricConstraint() and 
                                                Actuator.inrunnerCompoundPlanetaryGearbox.meshingConstraint() and 
                                                Actuator.inrunnerCompoundPlanetaryGearbox.noPlanetInterferenceConstraint() and
                                                Actuator.noCarrierInterferenceConstraint() and
                                                Actuator.sunPCDConstraint() and
                                                Actuator.planetPCDConstraint() and
                                                Actuator.noSecCarrierInterferenceConstraint()
                                                ):
                                                self.totalFeasibleGearboxes += 1
                                                # Fiter for the Gear Ratio
                                                if (Actuator.inrunnerCompoundPlanetaryGearbox.gearRatio() >= self.gearRatioIter and 
                                                    Actuator.inrunnerCompoundPlanetaryGearbox.gearRatio() <= (self.gearRatioIter + self.GEAR_RATIO_STEP)):
                                                    self.totalGearboxesWithReqGR += 1
                                                    Actuator.updateFacewidth()
                                                    
                                                    self.Cost = self.cost(Actuator=Actuator)

                                                    if self.Cost < MinCost:
                                                        MinCost    = self.Cost
                                                        opt_done   = 1
                                                        self.iter += 1
                                                        # Actuator.genEquationFile()
                                                        if (self.gearRatioReq == 0):
                                                            Actuator.genEquationFile(motor_name=Actuator.motor.motorName, gearRatioLL=round(self.gearRatioIter, 1), gearRatioUL = (round(self.gearRatioIter + self.GEAR_RATIO_STEP,1)))
                                                        else:
                                                            Actuator.genEquationFile_editCADdirectly()
                                                    
                                                        opt_parameters = [Actuator.inrunnerCompoundPlanetaryGearbox.gearRatio(),
                                                                          Actuator.inrunnerCompoundPlanetaryGearbox.numPlanet,
                                                                          Actuator.inrunnerCompoundPlanetaryGearbox.Ns,
                                                                          Actuator.inrunnerCompoundPlanetaryGearbox.NpBig,
                                                                          Actuator.inrunnerCompoundPlanetaryGearbox.NpSmall,
                                                                          Actuator.inrunnerCompoundPlanetaryGearbox.Nr,
                                                                          Actuator.inrunnerCompoundPlanetaryGearbox.moduleBig,
                                                                          Actuator.inrunnerCompoundPlanetaryGearbox.moduleSmall]
                                                        opt_planetaryGearbox = inrunnerCompoundPlanetaryGearbox(design_parameters         = self.design_parameters,
                                                                                                        gear_standard_parameters  = self.gear_standard_parameters,
                                                                                                        Ns                        = Actuator.inrunnerCompoundPlanetaryGearbox.Ns,
                                                                                                        NpBig                     = Actuator.inrunnerCompoundPlanetaryGearbox.NpBig,
                                                                                                        NpSmall                   = Actuator.inrunnerCompoundPlanetaryGearbox.NpSmall, 
                                                                                                        Nr                        = Actuator.inrunnerCompoundPlanetaryGearbox.Nr,
                                                                                                        numPlanet                 = Actuator.inrunnerCompoundPlanetaryGearbox.numPlanet,
                                                                                                        moduleBig                 = Actuator.inrunnerCompoundPlanetaryGearbox.moduleBig, # mm
                                                                                                        moduleSmall               = Actuator.inrunnerCompoundPlanetaryGearbox.moduleSmall, # mm
                                                                                                        densityGears              = Actuator.inrunnerCompoundPlanetaryGearbox.densityGears,
                                                                                                        densityStructure          = Actuator.inrunnerCompoundPlanetaryGearbox.densityStructure,
                                                                                                        fwSunMM                   = Actuator.inrunnerCompoundPlanetaryGearbox.fwSunMM, # mm
                                                                                                        fwPlanetBigMM             = Actuator.inrunnerCompoundPlanetaryGearbox.fwPlanetBigMM, # mm
                                                                                                        fwPlanetSmallMM           = Actuator.inrunnerCompoundPlanetaryGearbox.fwPlanetSmallMM, # mm
                                                                                                        fwRingMM                  = Actuator.inrunnerCompoundPlanetaryGearbox.fwRingMM, # mm
                                                                                                        maxGearAllowableStressMPa = Actuator.inrunnerCompoundPlanetaryGearbox.maxGearAllowableStressMPa, # MPa) # kg/m^3
                                                                                                        densityAluminum           = Actuator.inrunnerCompoundPlanetaryGearbox.densityAluminum)  # kg/m^3
                                                                                                        
                                                        opt_actuator = inrunnerCompoundPlanetaryActuator(design_parameters        = self.design_parameters,
                                                                                                 motor                    = Actuator.motor,
                                                                                                 motor_driver_params      = Actuator.motor_driver_params,
                                                                                                 inrunnerCompoundPlanetaryGearbox = opt_planetaryGearbox,
                                                                                                 FOS                      = Actuator.FOS,
                                                                                                 serviceFactor            = Actuator.serviceFactor,
                                                                                                 maxGearboxDiameter       = Actuator.maxGearboxDiameter, # mm 
                                                                                                 stressAnalysisMethodName = "MIT") # Lewis or AGMA
                                                        opt_actuator.updateFacewidth()
                                                        opt_actuator.getMassKG_3DP()                                                        
                                                        # self.printOptimizationResults(Actuator, log, csv)
                                            Actuator.inrunnerCompoundPlanetaryGearbox.setNumPlanet(Actuator.inrunnerCompoundPlanetaryGearbox.numPlanet + 1)
                                        # Actuator.inrunnerCompoundPlanetaryGearbox.setNr(Actuator.inrunnerCompoundPlanetaryGearbox.Nr + 1)
                                    Actuator.inrunnerCompoundPlanetaryGearbox.setNpSmall(Actuator.inrunnerCompoundPlanetaryGearbox.NpSmall + 1)
                                Actuator.inrunnerCompoundPlanetaryGearbox.setNpBig(Actuator.inrunnerCompoundPlanetaryGearbox.NpBig + 1)
                            Actuator.inrunnerCompoundPlanetaryGearbox.setNs(Actuator.inrunnerCompoundPlanetaryGearbox.Ns + 1)
                        Actuator.inrunnerCompoundPlanetaryGearbox.setModuleSmall(Actuator.inrunnerCompoundPlanetaryGearbox.moduleSmall + 0.100)
                        Actuator.inrunnerCompoundPlanetaryGearbox.setModuleSmall(round(Actuator.inrunnerCompoundPlanetaryGearbox.moduleSmall, 1)) # Round Off
                    Actuator.inrunnerCompoundPlanetaryGearbox.setModuleBig(Actuator.inrunnerCompoundPlanetaryGearbox.moduleBig + 0.100)
                    Actuator.inrunnerCompoundPlanetaryGearbox.setModuleBig(round(Actuator.inrunnerCompoundPlanetaryGearbox.moduleBig, 1)) # Round Off
                if (opt_done):
                    self.printOptimizationResults(opt_actuator, log, csv)
                    opt_actuator.print_mass_of_parts_3DP()
                self.gearRatioIter += self.GEAR_RATIO_STEP
            
                if log:
                    print("Number of iterations: ", self.iter)
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

    def optimizeActuatorWithPSC(self, Actuator=inrunnerCompoundPlanetaryActuator, log=1, csv=0):
        startTime = time.time()
        opt_parameters = []
        if csv and log:
            print("WARNING: Both csv and Log cannot be true")
            print("WARNING: Please set either csv or log to be 0 in \"Optimizer.optimizeActuator(Actuator)\" function")
            print(" ")
            print("Making log to be false and csv to be true")
            log = 0
            csv = 1
        elif not csv and not log:
            print("WARNING: Both csv and Log cannot be false")
            print("WARNING: Please set either csv or log to be 1 in \"Optimizer.optimizeActuator(Actuator)\" function")
            print(" ")
            print("Making log to be False and csv to be true")
            log = 0
            csv = 1
        
        if csv:
            fileName = f"./results/results_bilevel_{Actuator.motor.motorName}/INCPG_BILEVEL_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}.csv"
        elif log:
            fileName = f"./results/results_bilevel_{Actuator.motor.motorName}/INCPG_BILEVEL_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}_LOG.txt"
        
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
                print("iter, gearRatio, moduleBig, moduleSmall, Ns, NpBig, NpSmall, Nr, numPlanet, fwSunMM, fwPlanetBigMM, fwPanetSmallMM, fwRingMM, PSCs, PSCp1, PSCp2, PSCr, CD_SP, CD_PR, mass, eff, peakTorque, Cost, tooth_forces_sp, tooth_forces_rp, Torque_Density")

            while self.gearRatioIter <= self.GEAR_RATIO_MAX:
                opt_done  = 0
                self.iter = 0
                self.Cost = 100000
                MinCost   = self.Cost
                Actuator.inrunnerCompoundPlanetaryGearbox.setModuleBig(self.MODULE_BIG_MIN)
                while Actuator.inrunnerCompoundPlanetaryGearbox.moduleBig <= self.MODULE_BIG_MAX:
                    # Setting Module Small
                    Actuator.inrunnerCompoundPlanetaryGearbox.setModuleSmall(self.MODULE_SMALL_MIN)
                    while (Actuator.inrunnerCompoundPlanetaryGearbox.moduleSmall <= self.MODULE_SMALL_MAX):
                        # Setting Ns
                        Actuator.inrunnerCompoundPlanetaryGearbox.setNs(self.NUM_TEETH_SUN_MIN)
                        while (2*Actuator.inrunnerCompoundPlanetaryGearbox.getPCRadiusSunM()*1000) <= Actuator.maxGearboxDiameter:
                            # Setting Np Big
                            Actuator.inrunnerCompoundPlanetaryGearbox.setNpBig(self.NUM_TEETH_PLANET_BIG_MIN)
                            while (2*Actuator.inrunnerCompoundPlanetaryGearbox.getPCRadiusPlanetBigM()*1000) <= Actuator.maxGearboxDiameter/2:
                                # Setting Np Small
                                Actuator.inrunnerCompoundPlanetaryGearbox.setNpSmall(self.NUM_TEETH_PLANET_SMALL_MIN)
                                while (2*Actuator.inrunnerCompoundPlanetaryGearbox.getPCRadiusPlanetSmallM()*1000) <= Actuator.maxGearboxDiameter/2:
                                    # Setting Nr
                                    Actuator.inrunnerCompoundPlanetaryGearbox.setNr(Actuator.inrunnerCompoundPlanetaryGearbox.NpSmall + 
                                                                            Actuator.inrunnerCompoundPlanetaryGearbox.NpBig +
                                                                            Actuator.inrunnerCompoundPlanetaryGearbox.Ns)
                                    # if (2*Actuator.inrunnerCompoundPlanetaryGearbox.getPCRadiusRingM()*1000) <= Actuator.maxGearboxDiameter:
                                    if (Actuator.inrunnerCompoundPlanetaryGearbox.getGearboxOuterDiaMaxM()*1000) <= Actuator.maxGearboxDiameter:
                                        # Setting number of Planet
                                        Actuator.inrunnerCompoundPlanetaryGearbox.setNumPlanet(self.NUM_PLANET_MIN)
                                        while Actuator.inrunnerCompoundPlanetaryGearbox.numPlanet <= self.NUM_PLANET_MAX:
                                            if (Actuator.inrunnerCompoundPlanetaryGearbox.geometricConstraint() and 
                                                Actuator.inrunnerCompoundPlanetaryGearbox.meshingConstraint() and 
                                                Actuator.inrunnerCompoundPlanetaryGearbox.noPlanetInterferenceConstraint()):
                                                self.totalFeasibleGearboxes += 1
                                                # Fiter for the Gear Ratio
                                                if (Actuator.inrunnerCompoundPlanetaryGearbox.gearRatio() >= self.gearRatioIter and 
                                                    Actuator.inrunnerCompoundPlanetaryGearbox.gearRatio() <= (self.gearRatioIter + self.GEAR_RATIO_STEP)):
                                                    self.totalGearboxesWithReqGR += 1
                                                    Actuator.updateFacewidth()
                                                    
                                                    effActuator = Actuator.inrunnerCompoundPlanetaryGearbox.getEfficiency()
                                                    massActuator = Actuator.getMassKG_3DP()

                                                    self.Cost = (self.K_Mass * massActuator) + (self.K_Eff * effActuator)
                                                    if self.Cost < MinCost:
                                                        MinCost = self.Cost
                                                        opt_done = 1
                                                        self.iter += 1
                                                        Actuator.genEquationFile()
                                                        opt_parameters = [Actuator.inrunnerCompoundPlanetaryGearbox.gearRatio(),
                                                                          Actuator.inrunnerCompoundPlanetaryGearbox.numPlanet,
                                                                          Actuator.inrunnerCompoundPlanetaryGearbox.Ns,
                                                                          Actuator.inrunnerCompoundPlanetaryGearbox.NpBig,
                                                                          Actuator.inrunnerCompoundPlanetaryGearbox.NpSmall,
                                                                          Actuator.inrunnerCompoundPlanetaryGearbox.Nr,
                                                                          Actuator.inrunnerCompoundPlanetaryGearbox.moduleBig,
                                                                          Actuator.inrunnerCompoundPlanetaryGearbox.moduleSmall]
                                                        opt_planetaryGearbox = inrunnerCompoundPlanetaryGearbox(design_parameters         = self.design_parameters,
                                                                                                        gear_standard_parameters  = self.gear_standard_parameters,
                                                                                                        Ns                        = Actuator.inrunnerCompoundPlanetaryGearbox.Ns,
                                                                                                        NpBig                     = Actuator.inrunnerCompoundPlanetaryGearbox.NpBig,
                                                                                                        NpSmall                   = Actuator.inrunnerCompoundPlanetaryGearbox.NpSmall, 
                                                                                                        Nr                        = Actuator.inrunnerCompoundPlanetaryGearbox.Nr,
                                                                                                        numPlanet                 = Actuator.inrunnerCompoundPlanetaryGearbox.numPlanet,
                                                                                                        moduleBig                 = Actuator.inrunnerCompoundPlanetaryGearbox.moduleBig, # mm
                                                                                                        moduleSmall               = Actuator.inrunnerCompoundPlanetaryGearbox.moduleSmall, # mm
                                                                                                        densityGears              = Actuator.inrunnerCompoundPlanetaryGearbox.densityGears,
                                                                                                        densityStructure          = Actuator.inrunnerCompoundPlanetaryGearbox.densityStructure,
                                                                                                        fwSunMM                   = Actuator.inrunnerCompoundPlanetaryGearbox.fwSunMM, # mm
                                                                                                        fwPlanetBigMM             = Actuator.inrunnerCompoundPlanetaryGearbox.fwPlanetBigMM, # mm
                                                                                                        fwPlanetSmallMM           = Actuator.inrunnerCompoundPlanetaryGearbox.fwPlanetSmallMM, # mm
                                                                                                        fwRingMM                  = Actuator.inrunnerCompoundPlanetaryGearbox.fwRingMM, # mm
                                                                                                        maxGearAllowableStressMPa = Actuator.inrunnerCompoundPlanetaryGearbox.maxGearAllowableStressMPa,
                                                                                                        densityAluminum           = Actuator.inrunnerCompoundPlanetaryGearbox.densityAluminum)  # kg/m^3
                                                        opt_actuator = inrunnerCompoundPlanetaryActuator(design_parameters        = self.design_parameters,
                                                                                                 motor                    = Actuator.motor,
                                                                                                 inrunnerCompoundPlanetaryGearbox = opt_planetaryGearbox,
                                                                                                 FOS                      = Actuator.FOS,
                                                                                                 serviceFactor            = Actuator.serviceFactor,
                                                                                                 maxGearboxDiameter       = Actuator.maxGearboxDiameter, # mm 
                                                                                                 stressAnalysisMethodName = "Lewis") # Lewis or AGMA
                                            Actuator.inrunnerCompoundPlanetaryGearbox.setNumPlanet(Actuator.inrunnerCompoundPlanetaryGearbox.numPlanet + 1)
                                        # Actuator.inrunnerCompoundPlanetaryGearbox.setNr(Actuator.inrunnerCompoundPlanetaryGearbox.Nr + 1)
                                    Actuator.inrunnerCompoundPlanetaryGearbox.setNpSmall(Actuator.inrunnerCompoundPlanetaryGearbox.NpSmall + 1)
                                Actuator.inrunnerCompoundPlanetaryGearbox.setNpBig(Actuator.inrunnerCompoundPlanetaryGearbox.NpBig + 1)
                            Actuator.inrunnerCompoundPlanetaryGearbox.setNs(Actuator.inrunnerCompoundPlanetaryGearbox.Ns + 1)
                        Actuator.inrunnerCompoundPlanetaryGearbox.setModuleSmall(Actuator.inrunnerCompoundPlanetaryGearbox.moduleSmall + 0.100)
                        Actuator.inrunnerCompoundPlanetaryGearbox.setModuleSmall(round(Actuator.inrunnerCompoundPlanetaryGearbox.moduleSmall, 1)) # Round Off
                    Actuator.inrunnerCompoundPlanetaryGearbox.setModuleBig(Actuator.inrunnerCompoundPlanetaryGearbox.moduleBig + 0.100)
                    Actuator.inrunnerCompoundPlanetaryGearbox.setModuleBig(round(Actuator.inrunnerCompoundPlanetaryGearbox.moduleBig, 1)) # Round Off
                if (opt_done):
                    self.cspgOpt = optimal_continuous_PSC_cpg(GEAR_RATIO_MIN = opt_parameters[0],
                                                              numPlanet      = opt_parameters[1],
                                                              Ns_init        = opt_parameters[2],
                                                              Np1_init       = opt_parameters[3],
                                                              Np2_init       = opt_parameters[4],
                                                              Nr_init        = opt_parameters[5],
                                                              M1_init        = opt_parameters[6] * 10,
                                                              M2_init        = opt_parameters[7] * 10)
                    _, calc_centerDistForManufacturing = self.cspgOpt.solve()
                    self.cspgOpt.solve(optimizeForManufacturing=True,
                                       centerDistForManufacturing=calc_centerDistForManufacturing)
                    self.printOptimizationResults(opt_actuator, log, csv)
                self.gearRatioIter += self.GEAR_RATIO_STEP
            
                if log:
                    print("Number of iterations: ", self.iter)
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

        return totalTime

    def cost(self, Actuator=inrunnerCompoundPlanetaryActuator):
        K_gearRatio = 0
        if self.gearRatioReq != 0:
            K_gearRatio = 10
        
        gearRatio_err = np.sqrt((Actuator.inrunnerCompoundPlanetaryGearbox.gearRatio() - self.gearRatioReq)**2)

        mass = Actuator.getMassKG_3DP()
        eff = Actuator.inrunnerCompoundPlanetaryGearbox.getEfficiency()
        width = Actuator.inrunnerCompoundPlanetaryGearbox.fwPlanetBigMM + Actuator.inrunnerCompoundPlanetaryGearbox.fwPlanetSmallMM
        cost = (self.K_Mass    * mass 
                + self.K_Eff   * eff 
                + self.K_Width * width 
                + K_gearRatio  * gearRatio_err)
        return cost

# ═══════════════════════════════════════════════════════════════════
#   STEP 1 — Read fixed values from ISSPG_fixed.txt
#   Format per line: "name"= value
# ═══════════════════════════════════════════════════════════════════

