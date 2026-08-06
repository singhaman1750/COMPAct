import re
import os
import math
import numpy as np
import sys
import time

from CommonComponents import material, bearings_discrete, nuts_and_bolts_dimensions, motor_driver, motor_frameless_inrunner as motor

class inrunnerWolfromPlanetaryGearbox:
    def __init__(self,
                 design_parameters,
                 gear_standard_parameters,
                 Ns      = 20, # Teeth: sun gear
                 NpBig   = 40, # Teeth: bigger planet gear
                 NpSmall = 20, # Teeth: smaller planet gear
                 NrBig   = 80, # Teeth: bigger ring gear
                 NrSmall = 40, # Teeth: smaller ring gear
                 numPlanet                 = 2,
                 moduleBig                 = 0.5,
                 moduleSmall               = 0.5,
                 densityGears              = 7850,
                 densityStructure          = 2710,
                 fwSunMM                   = 5.0,
                 fwPlanetBigMM             = 5.0,
                 fwPlanetSmallMM           = 5.0,
                 fwRingBigMM               = 5.0,
                 fwRingSmallMM             = 5.0,
                 maxGearAllowableStressMPa = 400,
                 densityAluminum           = 2170):
        
        #-----------------------------------
        # Discrete Optimizaition Variables 
        #-----------------------------------
        self.Ns          = Ns
        self.NpBig       = NpBig
        self.NpSmall     = NpSmall
        self.NrBig       = NrBig
        self.NrSmall     = NrSmall
        self.numPlanet   = numPlanet
        self.moduleBig   = moduleBig
        self.moduleSmall = moduleSmall
        
        #-----------------------------------
        # Material Properties
        #-----------------------------------
        self.densityGears              = densityGears
        self.densityStructure          = densityStructure
        self.densityAluminum           = densityAluminum
        self.maxGearAllowableStressMPa = maxGearAllowableStressMPa         # MPa
        self.maxGearAllowableStressPa  = maxGearAllowableStressMPa * 10**6 # Pa
        
        #-------------------------------
        # Facewidths
        #-------------------------------
        self.fwSunMM         = fwSunMM
        self.fwPlanetBigMM   = fwPlanetBigMM
        self.fwPlanetSmallMM = fwPlanetSmallMM
        self.fwRingBigMM     = fwRingBigMM
        self.fwRingSmallMM   = fwRingSmallMM
        
        #------------------------------
        # Gearbox parameters
        #------------------------------
        self.mu               = gear_standard_parameters["coefficientOfFriction"] # 0.3 # Gear standard parameters
        self.pressureAngleDEG = gear_standard_parameters["pressureAngleDEG"]      # 20  # deg
        
        self.planetMinDistanceMM  = design_parameters["planetMinDistanceMM"]    # mm
        self.ringRadialWidthMMSmall = design_parameters["ringRadialWidthMMSmall"] # ringRadialWidthSmall
        self.ringRadialWidthMMBig   = design_parameters["ringRadialWidthMMBig"]   # ringRadialWidthBig
        # self.carrierWidthMM     = carrierWidthMM
        
        #------------------------------
        # Profile Shift Coefficients TODO: Remove this
        #------------------------------
        self.profileShiftCoefficientRingSmall   = 0.0
        self.profileShiftCoefficientRingBig     = 0.0
        self.profileShiftCoefficientPlanetBig   = self.profileShiftCoefficientRingBig
        self.profileShiftCoefficientPlanetSmall = self.profileShiftCoefficientRingSmall
        self.profileShiftCoefficientSun         = -self.profileShiftCoefficientPlanetBig
        
    def geometricConstraint(self):
        return (((self.Ns + self.NpBig) * self.moduleBig == (self.NrSmall - self.NpSmall) * self.moduleSmall) and
                ((self.Ns + 2 * self.NpBig) == (self.NrBig)) and
                (self.NrBig * self.moduleBig > self.NrSmall * self.moduleSmall))
        
    def meshingConstraint(self):
        # TODO: VERIFY THIS WITH EXAMPLE AND SELF ANALYSIS
        return ((self.Ns % self.numPlanet == 0) and (self.NrSmall % self.numPlanet == 0) and (self.NrBig % self.numPlanet == 0))
    
    def noPlanetInterferenceConstraint(self):
        return 2*(self.Ns + self.NpBig)*self.moduleBig*np.sin(np.pi/self.numPlanet) >= 2*self.moduleBig*self.NpBig + self.planetMinDistanceMM

    def getMassKG(self):
        # Volume of the Sun gear
        fwSunM            = (self.fwSunMM / 1000.0)
        fwPlanetBigM      = (self.fwPlanetBigMM / 1000.0)
        fwPlanetSmallM    = (self.fwPlanetSmallMM / 1000.0)
        fwRingSmallM      = (self.fwRingSmallMM / 1000.0)
        fwRingBigM        = (self.fwRingBigMM / 1000.0)
        carrierWidthM     = (self.carrierWidthMM / 1000.0)

        sunVolume         = np.pi * fwSunM * (self.getPCRadiusSunM()**2)
        planetBigVolume   = np.pi * fwPlanetBigM * (self.getPCRadiusPlanetBigM()**2)
        planetSmallVolume = np.pi * fwPlanetSmallM * (self.getPCRadiusPlanetSmallM()**2)
        ringSmallVolume   = np.pi * fwRingSmallM * (self.getOuterRadiusRingSmallM()**2 - self.getPCRadiusRingSmallM()**2)
        ringBigVolume     = np.pi * fwRingBigM * (self.getOuterRadiusRingBigM()**2 - self.getPCRadiusRingBigM()**2)
        carrierVolume     =  2 * np.pi * carrierWidthM * (self.getCarrierRadiusM()**2)

        # Total mass of the Wolfrom planetary gearbox
        combinedGearVolume = sunVolume + (self.numPlanet * (planetBigVolume + planetSmallVolume)) + ringBigVolume + ringSmallVolume
        TotalMassKG        = (combinedGearVolume * self.densityGears + carrierVolume * self.densityStructure)
        return TotalMassKG

    def gearRatio(self):
        GR1 = 2*self.NrSmall*self.NpBig / (self.Ns * (self.NpBig - self.NpSmall))
        GR2 = ((self.Ns + self.NrBig) * self.NpBig * self.NrSmall) / (self.Ns * (self.NpBig * self.NrSmall - self.NpSmall * self.NrBig))
        if GR1 == GR2:
            pass
        else:
            print("ERROR: Gear ratio mismatch")
        return GR1
    
    #======================================
    # Efficiency Calculations
    #======================================
    #--------------------------------------
    # Utility Functions
    #--------------------------------------
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

    #-----------------------------------------
    # Gear tooth profile parameters
    #-----------------------------------------
    def getPressureAngleRad(self):
        return self.pressureAngleDEG * np.pi / 180  # Pressure angle in radians

    def getWorkingPressureAngle(self):
        module1 = self.moduleBig
        module2 = self.moduleSmall
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr1     = self.NrBig
        Nr2     = self.NrSmall
        xs      = 0
        xp1     = 0
        xp2     = 0
        xr1     = 0
        xr2     = 0

        #---------------------------------
        # Pressure Angle
        #---------------------------------
        alpha = self.getPressureAngleRad()

        #---------------------------------
        # Working pressure angle
        #---------------------------------
        # Sun-Planet-Stg1
        inv_alpha_w_sunPlanet_stg1 = 2*np.tan(alpha)*((xs + xp1)/(Ns + Np1)) + self.involute(alpha)
        alpha_w_sunPlanet_stg1     = self.inverse_involute(inv_alpha_w_sunPlanet_stg1)

        # Planet-Ring-Stg1
        inv_alpha_w_planetRing_stg1 = 2*np.tan(alpha)*((xr1 - xp1)/(Nr1 - Np1)) + self.involute(alpha)
        alpha_w_planetRing_stg1     = self.inverse_involute(inv_alpha_w_planetRing_stg1)

        # Planet-Ring-Stg2
        inv_alpha_w_planetRing_stg2 = 2*np.tan(alpha)*((xr2 - xp2)/(Nr2 - Np2)) + self.involute(alpha)
        alpha_w_planetRing_stg2     = self.inverse_involute(inv_alpha_w_planetRing_stg2)

        return alpha_w_sunPlanet_stg1, alpha_w_planetRing_stg1, alpha_w_planetRing_stg2

    def getCenterDistModificationCoeff(self):
        module1 = self.moduleBig
        module2 = self.moduleSmall
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr1     = self.NrBig
        Nr2     = self.NrSmall
        xs      = 0
        xp1     = 0
        xp2     = 0
        xr1     = 0
        xr2     = 0

        #------------------------------
        # Pressure Angle
        #------------------------------
        alpha = self.getPressureAngleRad()  # Pressure angle in radians

        #------------------------------
        # Working pressure angle
        #------------------------------
        alpha_w_sunPlanet_stg1, alpha_w_planetRing_stg1, alpha_w_planetRing_stg2 = self.getWorkingPressureAngle()

        #------------------------------------------
        # Centre distance modification coefficient
        #------------------------------------------
        y_sunPlanet_stg1  = (( Ns + Np1) / 2) * ((np.cos(alpha) / np.cos(alpha_w_sunPlanet_stg1)) - 1)
        y_planetRing_stg1 = ((Nr1 - Np1) / 2) * ((np.cos(alpha) / np.cos(alpha_w_planetRing_stg1)) - 1)
        y_planetRing_stg2 = ((Nr2 - Np2) / 2) * ((np.cos(alpha) / np.cos(alpha_w_planetRing_stg2)) - 1)

        return y_sunPlanet_stg1, y_planetRing_stg1, y_planetRing_stg2

    def getCenterDistance(self):
        module1 = self.moduleBig
        module2 = self.moduleSmall
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr1     = self.NrBig
        Nr2     = self.NrSmall
        xs      = 0
        xp1     = 0
        xp2     = 0
        xr1     = 0
        xr2     = 0

        #-------------------------------
        # Centre distance modification coefficient
        #-------------------------------
        y_sunPlanet_stg1, y_planetRing_stg1, y_planetRing_stg2 = self.getCenterDistModificationCoeff()

        #-------------------------------
        # Centre distance
        #-------------------------------

        centerDist_sunPlanet_stg1  = ((Ns + Np1)/2   + y_sunPlanet_stg1)* module1
        centerDist_planetRing_stg1 = ((Nr1 - Np1)/2  + y_planetRing_stg1)* module1
        centerDist_planetRing_stg2 = ((Nr2 - Np2)/2  + y_planetRing_stg2)* module2

        return centerDist_sunPlanet_stg1, centerDist_planetRing_stg1, centerDist_planetRing_stg2

    def getBaseDia(self):
        module1 = self.moduleBig
        module2 = self.moduleSmall
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr1     = self.NrBig
        Nr2     = self.NrSmall
        xs      = 0
        xp1     = 0
        xp2     = 0
        xr1     = 0
        xr2     = 0

        # Pressure Angle
        alpha = self.getPressureAngleRad() # Rad

        # Reference Diameter
        D_sun     = module1 * Ns   # Sun's reference diameter
        D_planet1 = module1 * Np1  # Planet's reference diameter
        D_planet2 = module2 * Np2  # Planet's reference diameter
        D_ring1    = module1 * Nr1 # Ring's reference diameter
        D_ring2    = module2 * Nr2 # Ring's reference diameter

        # Base Diameter
        D_b_sun      = D_sun * np.cos(alpha)
        D_b_planet1  = D_planet1 * np.cos(alpha)
        D_b_planet2  = D_planet2 * np.cos(alpha)
        D_b_ring1    = D_ring1 * np.cos(alpha)
        D_b_ring2    = D_ring2 * np.cos(alpha)

        return D_b_sun, D_b_planet1, D_b_planet2, D_b_ring1, D_b_ring2

    def getTipCircleDia(self):
        module1 = self.moduleBig
        module2 = self.moduleSmall
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr1     = self.NrBig
        Nr2     = self.NrSmall
        xs      = 0
        xp1     = 0
        xp2     = 0
        xr1     = 0
        xr2     = 0
        
        #----------------------------
        # Pressure Angle
        #----------------------------
        alpha = self.getPressureAngleRad() # Rad

        #----------------------------
        # Reference Diameter
        #----------------------------
        D_sun     = module1 * Ns  # Sun's reference diameter
        D_planet1 = module1 * Np1 # Planet's reference diameter
        D_planet2 = module2 * Np2 # Planet's reference diameter
        D_ring1   = module1 * Nr1 # Ring's reference diameter
        D_ring2   = module2 * Nr2 # Ring's reference diameter

        #----------------------------
        # Center Distance Modification Coefficient
        #----------------------------
        y_sunPlanet_stg1, y_planetRing_stg1, y_planetRing_stg2 = self.getCenterDistModificationCoeff()

        #----------------------------
        # Tip circle diameter
        #----------------------------
        # Sun
        D_a_sun = D_sun + 2 * module1 * (1 + y_sunPlanet_stg1 - xp1)

        # Planet
        D_a_planet1 = D_planet1 + 2 * module1 * (1 + self.quadratic_min((y_sunPlanet_stg1 - xs), xp1))  
        # D_a_planet2 = D_planet2 + 2 * module2 * (1 + self.quadratic_min((y_planetRing - xs),xp2)) 
        D_a_planet2 = D_planet2 + 2 * module2 * (1 + xp2) 
        
        # Ring
        D_a_ring1 = D_ring1 - 2 * module1 * (1 - xr1)
        D_a_ring2 = D_ring2 - 2 * module2 * (1 - xr2)
        
        return D_a_sun, D_a_planet1, D_a_planet2, D_a_ring1, D_a_ring2

    def getTipPressureAngle(self):
        module1 = self.moduleBig
        module2 = self.moduleSmall
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr1     = self.NrBig
        Nr2     = self.NrSmall
        xs      = 0
        xp1     = 0
        xp2     = 0
        xr1     = 0
        xr2     = 0

        alpha = self.getPressureAngleRad() # Pressure Angle (Rad)
        D_b_sun, D_b_planet1, D_b_planet2, D_b_ring1, D_b_ring2 = self.getBaseDia() # Base Diameter
        D_a_sun, D_a_planet1, D_a_planet2, D_a_ring1, D_a_ring2 = self.getTipCircleDia() # Tip Circle Diameter

        #----------------------------
        # Tip Pressure angle
        #----------------------------
        alpha_a_sun    =  np.arccos(D_b_sun / D_a_sun)
        alpha_a_planet1 = np.arccos(D_b_planet1/D_a_planet1)
        alpha_a_planet2 = np.arccos(D_b_planet2/D_a_planet2)
        alpha_a_ring1   = np.arccos(D_b_ring1 / D_a_ring1)
        alpha_a_ring2   = np.arccos(D_b_ring2 / D_a_ring2)

        return alpha_a_sun, alpha_a_planet1, alpha_a_planet2, alpha_a_ring1, alpha_a_ring2

    def getErrorTipCircleDia_planet(self):
        module1 = self.moduleBig
        module2 = self.moduleSmall
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr1     = self.NrBig
        Nr2     = self.NrSmall
        xs      = 0
        xp1     = 0
        xp2     = 0
        xr1     = 0
        xr2     = 0
        
        # Centre distance modification coefficient
        y_sunPlanet_stg1, y_planetRing_stg1, y_planetRing_stg2 = self.getCenterDistModificationCoeff()

        # Tip Circle Diameter
        _, D_a_planet1_quadMin, D_a_planet2_quadMin, _, _ = self.getTipCircleDia()
        D_a_planet1_actMin = module1 * Np1 + 2 * module1 * (1 + np.minimum((y_sunPlanet_stg1 - xs),xp1)) # TODO: How will we implement min function 
        D_a_planet2_actMin = module2 * Np2 + 2 * module2 * (1 + xp2) # TODO: How will we implement min function 

        return np.abs(D_a_planet1_quadMin - D_a_planet1_actMin), np.abs(D_a_planet2_quadMin - D_a_planet2_actMin)

    #-------------------------------------------------------------------------
    # Contact Ratio
    #-------------------------------------------------------------------------
    def contactRatio_sunPlanet_stg1(self):
        module1 = self.moduleBig
        module2 = self.moduleSmall
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr1     = self.NrBig
        Nr2     = self.NrSmall
        xs      = 0
        xp1     = 0
        xp2     = 0
        xr1     = 0
        xr2     = 0

        # Working pressure angle
        alpha_w_sunPlanet_stg1, _, _ = self.getWorkingPressureAngle()

        # Tip pressure angle
        alpha_a_sun, alpha_a_planet1, _, _, _ = self.getTipPressureAngle()

        # Contact ratio
        Approach_CR_sunPlanet_stg1 = (Np1 / (2 * np.pi)) * (np.tan(alpha_a_planet1) - np.tan(alpha_w_sunPlanet_stg1)) # Approach contact ratio
        Recess_CR_sunPlanet_stg1   = (Ns / (2 * np.pi)) * (np.tan(alpha_a_sun) - np.tan(alpha_w_sunPlanet_stg1))      # Recess contact ratio

        # write the final formula
        CR_sunPlanet_stg1 = Approach_CR_sunPlanet_stg1 + Recess_CR_sunPlanet_stg1

        return Approach_CR_sunPlanet_stg1, Recess_CR_sunPlanet_stg1, CR_sunPlanet_stg1

    def contactRatio_planetRing_stg1(self):
        module1 = self.moduleBig
        module2 = self.moduleSmall
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr1     = self.NrBig
        Nr2     = self.NrSmall
        xs      = 0
        xp1     = 0
        xp2     = 0
        xr1     = 0
        xr2     = 0

        # Working pressure angle
        _, alpha_w_planetRing_stg1, _ = self.getWorkingPressureAngle()

        # Tip pressure angle
        _, alpha_a_planet1, _, alpha_a_ring1, _ = self.getTipPressureAngle()

        # Contact ratio
        Approach_CR_planetRing_stg1 = -(Nr1 / (2 * np.pi)) * (np.tan(alpha_a_ring1) - np.tan(alpha_w_planetRing_stg1)) # Approach contact ratio
        Recess_CR_planetRing_stg1   =   Np1 / (2 * np.pi) * (np.tan(alpha_a_planet1) - np.tan(alpha_w_planetRing_stg1)) # Recess contact ratio
        
        # Contact Ratio
        CR_planetRing_stg1 = Approach_CR_planetRing_stg1 + Recess_CR_planetRing_stg1

        return Approach_CR_planetRing_stg1, Recess_CR_planetRing_stg1, CR_planetRing_stg1

    def contactRatio_planetRing_stg2(self):
        module1 = self.moduleBig
        module2 = self.moduleSmall
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr1     = self.NrBig
        Nr2     = self.NrSmall
        xs      = 0
        xp1     = 0
        xp2     = 0
        xr1     = 0
        xr2     = 0

        # Working pressure angle
        _, _, alpha_w_planetRing_stg2 = self.getWorkingPressureAngle()

        # Tip pressure angle
        _, _, alpha_a_planet2, _, alpha_a_ring2 = self.getTipPressureAngle()

        # Contact ratio
        Approach_CR_planetRing_stg2 = -(Nr2 / (2 * np.pi)) * (np.tan(alpha_a_ring2) - np.tan(alpha_w_planetRing_stg2)) # Approach contact ratio
        Recess_CR_planetRing_stg2   =   Np2 / (2 * np.pi) * (np.tan(alpha_a_planet2) - np.tan(alpha_w_planetRing_stg2)) # Recess contact ratio
        
        # Contact Ratio
        CR_planetRing_stg2 = Approach_CR_planetRing_stg2 + Recess_CR_planetRing_stg2
        
        return Approach_CR_planetRing_stg2, Recess_CR_planetRing_stg2, CR_planetRing_stg2

    #-----------------------------------------
    # Gearbox Efficiency
    #-----------------------------------------
    def getEfficiency(self):
        module1 = self.moduleBig
        module2 = self.moduleSmall
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr1     = self.NrBig
        Nr2     = self.NrSmall
        xs      = 0
        xp1     = 0
        xp2     = 0
        xr1     = 0
        xr2     = 0

        # Contact ratio
        eps_sunPlanet_stg1A, eps_sunPlanet_stg1R, _ = self.contactRatio_sunPlanet_stg1()
        eps_planetRing_stg1A, eps_planetRing_stg1R, _ = self.contactRatio_planetRing_stg1()
        eps_planetRing_stg2A, eps_planetRing_stg2R, _ = self.contactRatio_planetRing_stg2()
        
        # Contact-Ratio-Factor
        epsilon_sunPlanet_stg1  = eps_sunPlanet_stg1A**2 + eps_sunPlanet_stg1R**2 - eps_sunPlanet_stg1A - eps_sunPlanet_stg1R + 1 
        epsilon_planetRing_stg1 = eps_planetRing_stg1A**2 + eps_planetRing_stg1R**2 - eps_planetRing_stg1A - eps_planetRing_stg1R + 1 
        epsilon_planetRing_stg2 = eps_planetRing_stg2A**2 + eps_planetRing_stg2R**2 - eps_planetRing_stg2A - eps_planetRing_stg2R + 1 
        
        # Efficiency
        eff_SP_stg1 = 1 - self.mu * np.pi * ((1 / Np1) + (1 / Ns)) * epsilon_sunPlanet_stg1
        eff_PR_stg1 = 1 - self.mu * np.pi * ((1 / Np1) - (1 / Nr1)) * epsilon_planetRing_stg1
        eff_PR_stg2 = 1 - self.mu * np.pi * ((1 / Np2) - (1 / Nr2)) * epsilon_planetRing_stg2

        I1  = (Nr1 / Ns)
        I2  = (Nr1 * Np2) / (Np1 * Nr2)
        n_a = eff_SP_stg1 # self.getEfficiency_sunPlanet_stg1(Var = Var)
        n_b = eff_PR_stg1 # self.getEfficiency_planetRing_stg1(Var = Var)
        n_c = eff_PR_stg2 # self.getEfficiency_planetRing_stg2(Var = Var)

        Numerator   = (1 + n_a * n_b * I1) * (1 - I2)
        Denominator = (1 + I1) * (1 - n_b * n_c * I2)
        return Numerator / Denominator

    # ---------------------------------------

    def getEfficiency_old(self):
        I1 = self.NrBig / self.Ns
        I2 = (self.NrBig * self.NpSmall) / (self.NpBig * self.NrSmall)
        n_a = self.getEfficiencySunPlanet()
        n_b = self.getEfficiencyPlanetRingBig()
        n_c = self.getEfficiencyPlanetRingSmall()

        # print(" ")
        # print("I1 = ", I1)
        # print("I2 = ", I2)
        # print("n_a = ", n_a)
        # print("n_b = ", n_b)
        # print("n_c = ", n_c)
        # print(" ")

        Numerator = (1 + n_a*n_b*I1)*(1-I2)
        Denominator = (1+I1)*(1-n_b*n_c*I2)
        return Numerator / Denominator

    def getPCRadiusSunM(self):
        return ((self.Ns * self.moduleBig / 2) / 1000.0)

    def getPCRadiusPlanetBigM(self):
        return ((self.NpBig * self.moduleBig / 2) / 1000.0)

    def getPCRadiusPlanetSmallM(self):
        return ((self.NpSmall * self.moduleSmall / 2) / 1000.0)

    def getPCRadiusRingBigM(self):
        return ((self.NrBig * self.moduleBig / 2) / 1000.0)   

    def getPCRadiusRingSmallM(self):
        return ((self.NrSmall * self.moduleSmall / 2) / 1000.0) 

    def getOuterRadiusRingSmallM(self):
        ringPCDiameterMM = self.NrSmall * self.moduleSmall 
        ringPCRadiusMM = ringPCDiameterMM / 2
        return (ringPCRadiusMM + self.ringRadialWidthMMSmall) / 1000.0

    def getOuterRadiusRingBigM(self):
        ringPCDiameterMM = self.NrBig * self.moduleBig
        ringPCRadiusMM = ringPCDiameterMM / 2
        return (ringPCRadiusMM + self.ringRadialWidthMMBig) / 1000.0
    
    def getPCRadiusSunMM(self):
        return ((self.Ns * self.moduleBig / 2))

    def getPCRadiusPlanetBigMM(self):
        return ((self.NpBig * self.moduleBig / 2))

    def getPCRadiusPlanetSmallMM(self):
        return ((self.NpSmall * self.moduleSmall / 2))

    def getPCRadiusRingBigMM(self):
        return ((self.NrBig * self.moduleBig / 2))   

    def getPCRadiusRingSmallMM(self):
        return ((self.NrSmall * self.moduleSmall / 2)) 

    def getOuterRadiusRingSmallMM(self):
        ringPCDiameterMM = self.NrSmall * self.moduleSmall 
        ringPCRadiusMM = ringPCDiameterMM / 2
        return (ringPCRadiusMM + self.ringRadialWidthMMSmall)

    def getOuterRadiusRingBigMM(self):
        ringPCDiameterMM = self.NrBig * self.moduleBig
        ringPCRadiusMM = ringPCDiameterMM / 2
        return (ringPCRadiusMM + self.ringRadialWidthMMBig)
    
    def getCarrierRadiusM(self):
        return (((self.Ns + self.NpBig + self.NpBig/2)/2)*self.moduleBig) / 1000.0

    # Set the face width of the sun gear, planet gear, and ring gear in mm
    def setfwSunMM(self, fwSunMM):
        self.fwSunMM = fwSunMM

    def setfwPlanetBigMM(self, fwPlanetBigMM):
        self.fwPlanetBigMM = fwPlanetBigMM

    def setfwPlanetSmallMM(self, fwPlanetSmallMM):
        self.fwPlanetSmallMM = fwPlanetSmallMM

    def setfwRingBigMM(self, fwRingBigMM):
        self.fwRingBigMM = fwRingBigMM

    def setfwRingSmallMM(self, fwRingSmallMM):
        self.fwRingSmallMM = fwRingSmallMM

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

    def setNrBig(self, NrBig):
        self.NrBig = NrBig

    def setNrSmall(self, NrSmall):
        self.NrSmall = NrSmall
    
    def setNumPlanet(self, numPlanet):
        self.numPlanet = numPlanet

    def getEfficiencySunPlanet(self):
        module = self.moduleBig                                       # Module of the gear
        alpha = self.pressureAngleDEG * np.pi / 180                   # Pressure angle in radians
        
        D_b_sun    = module * self.Ns * np.cos(alpha)                 # Sun's basic circle diameter
        D_b_planet = module * self.NpBig * np.cos(alpha)              # Planet's basic circle diameter

        centerDist = (self.Ns + self.NpBig) * module / 2              # Center distance between the gears
        alpha_w = np.arccos((D_b_sun + D_b_planet) / (2*centerDist))  # Working pressure angle

        # TODO: For non-equal profile shift coefficients: Use this later
        #ya = 0# ??????

        ya = 0 # Addendum of the sun gear 
        xp = self.profileShiftCoefficientPlanetBig
        xs = self.profileShiftCoefficientSun

        # TODO: For non-equal profile shift coefficients: Use this later
        # D_a_sun    = module * sun.numTeeth + 2*module*(1 + ya - xp)             # Sun's tip circle diameter
        # D_a_planet = module * sun.numTeeth + 2*module*(1 + np.min([ya-xs, xp])) # Planet's tip circle diameter
        
        D_a_sun    = module * self.Ns + 2*module*(1 + xs)             # Sun's tip circle diameter
        D_a_planet = module * self.NpBig + 2*module*(1 + xp) # Planet's tip circle diameter

        alpha_a_sun = np.arccos(D_b_sun / D_a_sun) # Sun's Tip pressure angle
        alpha_a_planet = np.arccos(D_b_planet / D_a_planet) # Planet's Tip pressure angle
        
        eps1 = ((self.NpBig) / (2 * np.pi)) * (np.tan(alpha_a_planet) - np.tan(alpha_w) ) # Approach contact ratio
        eps2 = (self.Ns / (2 * np.pi)) * (np.tan(alpha_a_sun) - np.tan(alpha_w) ) # Recess contact ratio
        epsilon = eps1**2 + eps2**2 - eps1 - eps2 + 1 # equivalent contact ratio

        # NOTE: pinion is always an external gear and gear may be an internal or external gear
        eff = 1 - self.mu * np.pi * (( 1 / self.Ns) + (1 / self.NpBig)) * epsilon
        return eff
    
    def getEfficiencyPlanetRingBig(self):
        module = self.moduleBig                      # Module of the gear
        alpha = self.pressureAngleDEG * np.pi / 180  # Pressure angle in radians
        
        D_b_ring    = module * self.NrBig * np.cos(alpha)       # Sun's basic circle diameter
        D_b_planet = module * self.NpBig * np.cos(alpha)        # Planet's basic circle diameter

        centerDist = (self.NrBig - self.NpBig) * module / 2    # Center distance between the gears
        alpha_w = np.arccos((D_b_ring - D_b_planet) / (2*centerDist))  # Working pressure angle

        # TODO: For non-equal profile shift coefficients: Use this later
        #ya = 0# ??????

        ya = 0 # Addendum of the sun gear 
        xr = self.profileShiftCoefficientRingBig
        xp = self.profileShiftCoefficientPlanetBig

        # TODO: For non-equal profile shift coefficients: Use this later
        # D_a_sun    = module * sun.numTeeth + 2*module*(1 + ya - xp)             # Sun's tip circle diameter
        # D_a_planet = module * sun.numTeeth + 2*module*(1 + np.min([ya-xs, xp])) # Planet's tip circle diameter
        
        D_a_ring    = module * self.NrBig - 2*module*(1 - xr)             # Ring's tip circle diameter
        D_a_planet = module * self.NpBig + 2*module*(1 + xp) # Planet's tip circle diameter

        alpha_a_ring = np.arccos(D_b_ring / D_a_ring) # Sun's Tip pressure angle
        alpha_a_planet = np.arccos(D_b_planet / D_a_planet) # Planet's Tip pressure angle
        
        eps1 = ((self.NrBig) / (2 * np.pi)) * (np.tan(alpha_a_ring) - np.tan(alpha_w) ) # Approach contact ratio
        eps2 = (self.NpBig / (2 * np.pi)) * (np.tan(alpha_a_planet) - np.tan(alpha_w) ) # Recess contact ratio
        epsilon = eps1**2 + eps2**2 - eps1 - eps2 + 1 # equivalent contact ratio

        # NOTE: pinion is always an external gear and gear may be an internal or external gear
        eff = 1 - self.mu * np.pi * (( 1 / self.NpBig) - (1 / self.NrBig)) * epsilon
        return eff

    def getEfficiencyPlanetRingSmall(self):
        module = self.moduleSmall                      # Module of the gear
        alpha = self.pressureAngleDEG * np.pi / 180  # Pressure angle in radians
        
        D_b_ring    = module * self.NrSmall * np.cos(alpha)       # Sun's basic circle diameter
        D_b_planet = module * self.NpSmall * np.cos(alpha)    # Planet's basic circle diameter

        centerDist = (self.NrSmall - self.NpSmall) * module / 2    # Center distance between the gears
        alpha_w = np.arccos((D_b_ring - D_b_planet) / (2*centerDist))  # Working pressure angle

        # TODO: For non-equal profile shift coefficients: Use this later
        #ya = 0# ??????

        ya = 0 # Addendum of the sun gear 
        xr = self.profileShiftCoefficientRingSmall
        xp = self.profileShiftCoefficientPlanetSmall

        # TODO: For non-equal profile shift coefficients: Use this later
        # D_a_sun    = module * sun.numTeeth + 2*module*(1 + ya - xp)             # Sun's tip circle diameter
        # D_a_planet = module * sun.numTeeth + 2*module*(1 + np.min([ya-xs, xp])) # Planet's tip circle diameter
        
        D_a_ring    = module * self.NrSmall - 2*module*(1 - xr)             # Ring's tip circle diameter
        D_a_planet = module * self.NpSmall + 2*module*(1 + xp) # Planet's tip circle diameter

        alpha_a_ring = np.arccos(D_b_ring / D_a_ring) # Sun's Tip pressure angle
        alpha_a_planet = np.arccos(D_b_planet / D_a_planet) # Planet's Tip pressure angle
        
        eps1 = ((self.NrSmall) / (2 * np.pi)) * (np.tan(alpha_a_ring) - np.tan(alpha_w) ) # Approach contact ratio
        eps2 = (self.NpSmall / (2 * np.pi)) * (np.tan(alpha_a_planet) - np.tan(alpha_w) ) # Recess contact ratio
        epsilon = eps1**2 + eps2**2 - eps1 - eps2 + 1 # equivalent contact ratio

        # NOTE: pinion is always an external gear and gear may be an internal or external gear
        eff = 1 - self.mu * np.pi * (( 1 / self.NpSmall) - (1 / self.NrSmall)) * epsilon
        return eff

    # Print the planetary gearbox parameters
    def printParameters(self):
        print("Ns = ", self.Ns)
        print("NpBig = ", self.NpBig)
        print("NpSmall = ", self.NpSmall)
        print("NrBig = ", self.NrBig)
        print("NrSmall = ", self.NrSmall)
        print("Module (First Layer) = ", self.moduleBig)
        print("Module (Second Layer) = ", self.moduleSmall)
        print("Number of planets = ", self.numPlanet)
        print("Face width of sun gear = ", round(self.fwSunMM,2), " mm")
        print("Face width of Bigger planet gear = ", round(self.fwPlanetBigMM,2), " mm")
        print("Face width of Smaller planet gear = ", round(self.fwPlanetSmallMM,2), " mm")
        print("Face width of Bigger ring gear = ", round(self.fwRingBigMM,2), " mm")
        print("Face width of Smaller ring gear = ", round(self.fwRingSmallMM,2), " mm")
        print("Carrier width = ", self.carrierWidthMM, " mm")
        print("Bigger Ring radial width = ", self.ringRadialWidthMMBig, " mm")
        print("Smaller Ring radial width = ", self.ringRadialWidthMMSmall, " mm")
        print("Pitch circle radius of sun gear = ", self.getPCRadiusSunM() * 1000, " mm")
        print("Pitch circle radius of Bigger planet gear = ", self.getPCRadiusPlanetBigM() * 1000, " mm")
        print("Pitch circle radius of Smaller planet gear = ", self.getPCRadiusPlanetSmallM() * 1000, " mm")
        print("Pitch circle radius of Big ring gear = ", self.getPCRadiusRingBigM() * 1000, " mm")
        print("Pitch circle radius of Smaller ring gear = ", self.getPCRadiusRingSmallM() * 1000, " mm")
        print("Outer radius of Bigger ring gear = ", self.getOuterRadiusRingBigM() * 1000, " mm")
        print("Outer radius of Smaller ring gear = ", self.getOuterRadiusRingSmallM() * 1000, " mm")
        print("Carrier radius = ", self.getCarrierRadiusM() * 1000, " mm")
        print("Geometric constraint = ", self.geometricConstraint())
        print("Meshing constraint = ", self.meshingConstraint())
        print("No planet interference constraint = ", self.noPlanetInterferenceConstraint())
        print("Mass of the planetary gearbox = ", self.getMassKG(), " kg")
        print("Efficiency of the planetary gearbox = ", self.getEfficiency())
        #print("Maximum allowable stress for the gear material = ", self.getMaxGearAllowableStress(), " MPa")

    # Print the planetary gearbox parameters
    def printParametersLess(self):
        # print("----------------------------3k Planetary Gearbox--------------------------")
        vars = [self.moduleBig, self.moduleSmall, self.Ns, self.NpBig, self.NpSmall, self.NrBig, self.NrSmall, self.numPlanet]
        faceWidths = [round(self.fwSunMM,2), round(self.fwPlanetBigMM,2), round(self.fwPlanetSmallMM,2), round(self.fwRingBigMM,2), round(self.fwRingSmallMM,2)]
        print("[mB, mS, Ns, NpB, NpS, NrB, NrS, numPl]:", vars) 
        print("Face widths = ", faceWidths)
        print(" ")
        print("Gear ratio = ", self.gearRatio())
        print("Efficiency = ", round(self.getEfficiency(),4))
        print("Mass (gearbox, kg) = ", round(self.getMassKG(),3), " kg")
        # print("--------------------------------------------------------------------------")

class inrunnerWolfromPlanetaryActuator:
    def __init__(self, 
                 design_parameters,
                 motor_driver_params,
                 motor                    = motor,
                 inrunnerWolfromPlanetaryGearbox  = inrunnerWolfromPlanetaryGearbox,
                 FOS                      = 2.0,
                 serviceFactor            = 2.0,
                 maxGearboxDiameter       = 140.0,
                 stressAnalysisMethodName = "Lewis"):
        
        self.motor                    = motor
        self.inrunnerWolfromPlanetaryGearbox  = inrunnerWolfromPlanetaryGearbox
        self.FOS                      = FOS
        self.serviceFactor            = serviceFactor
        self.maxGearboxDiameter       = maxGearboxDiameter # TODO: convert it to 
                                                          # outer diameter of 
                                                          # the motor
        self.stressAnalysisMethodName = stressAnalysisMethodName

        self.design_params = design_parameters
        self.motor_driver_params = motor_driver_params

        #--------------------------------------------
        # Motor Specifications
        #--------------------------------------------
        self.motorLengthMM           = self.motor.getLengthMM()
        self.motorDiaMM              = self.motor.getDiaMM()
        self.motorMassKG             = self.motor.getMassKG()
        self.MaxMotorTorque          = self.motor.maxMotorTorque
        self.MaxMotorAngVelRPM       = self.motor.maxMotorAngVelRPM
        self.MaxMotorAngVelRadPerSec = self.motor.maxMotorAngVelRadPerSec

        #-----------------------------------------
        # Actuator Design Free Parameters
        #-----------------------------------------
        self.sCarrierExtrusionDiaMM       = design_parameters["sCarrierExtrusionDiaMM"]       # 12 # TODO: depends on the numPlanet, planet radii and clearance of planets
        self.sCarrierExtrusionClearanceMM = design_parameters["sCarrierExtrusionClearanceMM"] # 2

        self.bearingIDClearanceMM             = design_parameters["bearingIDClearanceMM"]

        self.ring1RadialWidthMM = self.inrunnerWolfromPlanetaryGearbox.ringRadialWidthMMBig   # 5
        self.ring2RadialWidthMM = self.inrunnerWolfromPlanetaryGearbox.ringRadialWidthMMSmall # 5

        # --- Setting the variables ---
        self.setVariables()

        self.actuator_width = 0

    def cost(self):
        massActuator = self.getMassKG_3DP()
        effActuator  = self.inrunnerWolfromPlanetaryGearbox.getEfficiency()
        widthActuator = self.inrunnerWolfromPlanetaryGearbox.fwPlanetBigMM + self.inrunnerWolfromPlanetaryGearbox.fwPlanetSmallMM
        module = self.inrunnerWolfromPlanetaryGearbox.moduleBig
        cost = massActuator - 2 * effActuator + 0.2 * widthActuator
        return cost
    
    def planetPCDConstraint(self):
        module    = self.inrunnerWolfromPlanetaryGearbox.moduleBig  # Module of the gear
        Ns        = self.inrunnerWolfromPlanetaryGearbox.Ns
        Np1       = self.inrunnerWolfromPlanetaryGearbox.NpBig
        Np2       = self.inrunnerWolfromPlanetaryGearbox.NpSmall
        
        planet_ID = module * Np2
        planet_bearing_OD = self.planet_bearing_OD

        return planet_ID > planet_bearing_OD + 2*self.standard_clearance_1_5mm*(2/3)

    def sunPCDConstraint(self):
        module    = self.inrunnerWolfromPlanetaryGearbox.moduleBig  # Module of the gear
        Ns        = self.inrunnerWolfromPlanetaryGearbox.Ns
        Np1       = self.inrunnerWolfromPlanetaryGearbox.NpBig
        Np2       = self.inrunnerWolfromPlanetaryGearbox.NpSmall
        
        sun_ID = module * Ns - 2*module*1.25
        sun_shaft_bearing_ID = self.sun_shaft_bearing_ID

        return sun_ID > sun_shaft_bearing_ID 
    
    def noSecCarrierInterferenceConstraint(self):
        module    = self.inrunnerWolfromPlanetaryGearbox.moduleBig  # Module of the gear
        Ns        = self.inrunnerWolfromPlanetaryGearbox.Ns
        Np1       = self.inrunnerWolfromPlanetaryGearbox.NpBig
        Np2       = self.inrunnerWolfromPlanetaryGearbox.NpSmall
        numPlanet = self.inrunnerWolfromPlanetaryGearbox.numPlanet
        
        sec_carrier_OD = (Np1+Ns)*module + 2*self.standard_clearance_1_5mm + self.planet_pin_socket_head_dia
        max_sec_carrier_OD = self.stator_ID
        return max_sec_carrier_OD >= sec_carrier_OD

    def setVariables(self):
        #--------- Optimization Variable-----------
        self.Ns         = self.inrunnerWolfromPlanetaryGearbox.Ns
        self.Np_b       = self.inrunnerWolfromPlanetaryGearbox.NpBig
        self.Np_s       = self.inrunnerWolfromPlanetaryGearbox.NpSmall
        self.Nr_b       = self.Ns + self.Np_b * 2
        self.Nr_s       = self.Ns + self.Np_b + self.Np_s
        self.module     = self.inrunnerWolfromPlanetaryGearbox.moduleBig
        self.num_planet = self.inrunnerWolfromPlanetaryGearbox.numPlanet

        #------------------------------------------------------
        # Indepent Constant variables
        #------------------------------------------------------
        #----------------- Gear Profile --------------------
        self.pressure_angle     = self.inrunnerWolfromPlanetaryGearbox.getPressureAngleRad() # 20
        self.pressure_angle_deg = self.inrunnerWolfromPlanetaryGearbox.getPressureAngleRad() * 180 / np.pi # 20

        #-------------Clearances---------------------
        self.clearance_planet                           = self.design_params["clearance_planet"]                           # 1.5
        self.clearance_case_mount_holes_shell_thickness = self.design_params["clearance_case_mount_holes_shell_thickness"] # 1
        self.standard_clearance_1_5mm                   = self.design_params["standard_clearance_1_5mm"]                   # 1.5
        self.standard_clearance_2_mm                    = self.design_params["standard_clearance_2_mm"]
       #self.case_mounting_nut_clearance               = self.design_params["case_mounting_nut_clearance"]                # 2
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
        self.stator_top_height    = self.motor.stator_wire_top_height
        self.stator_mid_height    = self.motor.stator_mid_height
        self.stator_bottom_height = self.motor.stator_wire_bottom_height
        self.stator_inside_OD     = self.motor.stator_wire_OD
        self.stator_hole_num      = self.motor.stator_hole_num
        self.stator_inside_ID     = self.motor.stator_wire_ID

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
        self.rotor_hub_sun_hole_num  = self.design_params["rotor_hub_sun_hole_num"]

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
        self.carrier_thickness     = self.design_params["carrier_thickness"] # 7

        self.carrier_trapezoidal_support_sun_offset                 = self.design_params["carrier_trapezoidal_support_sun_offset"]# 5
        self.carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID = self.design_params["carrier_trapezoidal_support_hole_PCD_offset_output_bearing_ID"] # 4
        self.carrier_trapezoidal_support_hole_dia                   = self.design_params["carrier_trapezoidal_support_hole_dia"]# 3

        self.carrier_ring_bearing_OD    = self.design_params["carrier_ring_bearing_OD"] # 26
        self.carrier_ring_bearing_width = self.design_params["carrier_ring_bearing_width"] # 5
        self.carrier_ring_bearing_ID    = self.design_params["carrier_ring_bearing_ID"] # 17

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

        self.ring_gearbox_casing_thickness          = self.design_params["ring_gearbox_casing_thickness"] # 5

        # --- Magnet Mount ---
        self.magnet_mount_hole_dia        = self.design_params["magnet_mount_hole_dia"]
        self.magnet_thickness             = self.design_params["magnet_thickness"]
        self.magnet_dia                   = self.design_params["magnet_dia"]
        self.magnet_mount_thickness       = self.design_params["magnet_mount_thickness"]
        self.magnet_pattern_bulge_dia     = self.design_params["magnet_pattern_bulge_dia"]
        self.magnet_pattern_bulge_number  = self.design_params["magnet_pattern_bulge_number"]
        self.magnet_mount_height          = self.design_params["magnet_mount_height"]

        # --- big Ring ---
        self.big_ring_radial_width = self.design_params["ringRadialWidthMMBig"] # 3
        self.small_ring_radial_width = self.design_params["ringRadialWidthMMSmall"] # 3

        
        #------------------------------------------------------
        # Dependent variables
        #------------------------------------------------------
        #---------------------------------------------------
        # Gear 
        #---------------------------------------------------
        # --- Gear Profile ---
        self.h_a = 1 * self.module
        self.h_f = 1.25 * self.module
        self.h_b = 1.25 * self.module
        self.clr_tip_root = self.h_f - self.h_a
        self.clr_tip_root_s = self.h_f - self.h_a

        # --- Ring ---
        # Big
        self.dp_r_b = self.module * self.Nr_b
        self.db_r_b = self.dp_r_b * np.cos ( self.pressure_angle )
        self.alpha_r_b = ( self.dp_r_b ** 2 - self.db_r_b ** 2 )**0.5 / self.db_r_b * 180 / np.pi - self.pressure_angle_deg
        self.beta_r_b = ( 360 / ( 4 * self.Nr_b ) + self.alpha_r_b ) * 2

        self.fw_r_b = self.inrunnerWolfromPlanetaryGearbox.fwRingBigMM

        #self.ring_OD_b = self.Nr_b * self.module + self.big_ring_radial_width  * 2

        # Small
        self.dp_r_s = self.module * self.Nr_s
        self.db_r_s = self.dp_r_s * np.cos ( self.pressure_angle )
        self.alpha_r_s = ( self.dp_r_s ** 2 - self.db_r_s ** 2 )**0.5 / self.db_r_s * 180 / np.pi - self.pressure_angle_deg
        self.beta_r_s = ( 360 / ( 4 * self.Nr_s ) + self.alpha_r_s ) * 2
        self.fw_r_s = self.inrunnerWolfromPlanetaryGearbox.fwRingSmallMM

        # --- Planet ---
        # Big
        self.dp_p_b = self.module * self.Np_b
        self.db_p_b = self.dp_p_b * np.cos ( self.pressure_angle )
        self.alpha_p_b = ( self.dp_p_b ** 2 - self.db_p_b ** 2 )**0.5 / self.db_p_b * 180 / np.pi - self.pressure_angle_deg
        self.beta_p_b = ( 360 / ( 4 * self.Np_b ) - self.alpha_p_b ) * 2
        self.fw_p_b = self.inrunnerWolfromPlanetaryGearbox.fwPlanetBigMM

        # Small
        self.dp_p_s = self.module * self.Np_s
        self.db_p_s = self.dp_p_s * np.cos ( self.pressure_angle )
        self.alpha_p_s = ( self.dp_p_s ** 2 - self.db_p_s ** 2 )**0.5 / self.db_p_s * 180 / np.pi - self.pressure_angle_deg
        self.beta_p_s = ( 360 / ( 4 * self.Np_s ) - self.alpha_p_s ) * 2

        self.fw_p_s = self.fw_r_s + self.clearance_planet

        # --- Sun gear ---
        self.dp_s = self.module * self.Ns
        self.db_s = self.dp_s * np.cos ( self.pressure_angle )
        self.alpha_s = ( self.dp_s ** 2 - self.db_s ** 2 )**0.5 / self.db_s * 180 / np.pi - self.pressure_angle_deg
        self.beta_s = ( 360 / ( 4 * self.Ns ) - self.alpha_s ) * 2

        self.fw_s_calc = self.inrunnerWolfromPlanetaryGearbox.fwSunMM

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
        OutputIDrequiredMM         = self.module * (self.Nr_b) + 2*self.module + self.small_ring_radial_width 
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
        file_path = os.path.join(os.path.dirname(__file__), 'CADs', 'INWPG', 'Equation_Files', motor_name, f'inwpg_equations_{gearRatioLL}_{gearRatioUL}.txt')
        with open(file_path, 'w') as eqFile:
            l = [
                    f'"Ns"= {self.Ns}\n',
                    f'"Np_b"= {self.Np_b}\n',
                    f'"Np_s"= {self.Np_s}\n',
                    f'"Nr_b"= {self.Nr_b}\n',
                    f'"Nr_s"= {self.Nr_s}\n',
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
                    f'"big_ring_radial_width"= {self.big_ring_radial_width}\n',
                    f'"small_ring_radial_width"= {self.small_ring_radial_width}\n',
                    f'"ring_gearbox_casing_thickness"= {self.ring_gearbox_casing_thickness}\n',
                    f'"h_a"= {self.h_a}\n',
                    f'"h_b"= {self.h_b}\n',
                    f'"h_f"= {self.h_f}\n',
                    f'"clr_tip_root"= {self.clr_tip_root}\n',
                    f'"clr_tip_root_s"= {self.clr_tip_root_s}\n',
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
                    f'"dp_r_b"= {self.dp_r_b}\n',
                    f'"db_r_b"= {self.db_r_b}\n',
                    f'"alpha_r_b"= {self.alpha_r_b}\n',
                    f'"beta_r_b"= {self.beta_r_b}\n',
                    f'"fw_r_b"= {self.fw_r_b}\n',
                    f'"dp_r_s"= {self.dp_r_s}\n',
                    f'"db_r_s"= {self.db_r_s}\n',
                    f'"alpha_r_s"= {self.alpha_r_s}\n',
                    f'"beta_r_s"= {self.beta_r_s}\n',
                    f'"fw_r_s"= {self.fw_r_s}\n',
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
                    f'"carrier_thickness"= {self.carrier_thickness}\n',
                    f'"carrier_ring_bearing_ID"= {self.carrier_ring_bearing_ID}\n',
                    f'"carrier_ring_bearing_OD"= {self.carrier_ring_bearing_OD}\n',
                    f'"carrier_ring_bearing_width"= {self.carrier_ring_bearing_width}\n', 
            ]
            eqFile.writelines(l)
        eqFile.close()
        
        file_path = os.path.join(os.path.dirname(__file__), 'CADs', 'INWPG', 'Equation_Files', motor_name, f'inwpg_equations_{gearRatioLL}_{gearRatioUL}_onshape.txt')
        with open(file_path, 'w') as eqFile:
            l = [
                    f'"Ns"= {self.Ns}\n',
                    f'"Np_b"= {self.Np_b}\n',
                    f'"Np_s"= {self.Np_s}\n',
                    f'"Nr_b"= {self.Nr_b}\n',
                    f'"Nr_s"= {self.Nr_s}\n',
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
                    f'"big_ring_radial_width"= {self.big_ring_radial_width}\n',
                    f'"small_ring_radial_width"= {self.small_ring_radial_width}\n',
                    f'"ring_gearbox_casing_thickness"= {self.ring_gearbox_casing_thickness}\n',
                    f'"h_a"= {self.h_a}\n',
                    f'"h_b"= {self.h_b}\n',
                    f'"h_f"= {self.h_f}\n',
                    f'"clr_tip_root"= {self.clr_tip_root}\n',
                    f'"clr_tip_root_s"= {self.clr_tip_root_s}\n',
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
                    f'"dp_r_b"= {self.dp_r_b}\n',
                    f'"db_r_b"= {self.db_r_b}\n',
                    f'"alpha_r_b"= {self.alpha_r_b}\n',
                    f'"beta_r_b"= {self.beta_r_b}\n',
                    f'"fw_r_b"= {self.fw_r_b}\n',
                    f'"dp_r_s"= {self.dp_r_s}\n',
                    f'"db_r_s"= {self.db_r_s}\n',
                    f'"alpha_r_s"= {self.alpha_r_s}\n',
                    f'"beta_r_s"= {self.beta_r_s}\n',
                    f'"fw_r_s"= {self.fw_r_s}\n',
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
                    f'"carrier_thickness"= {self.carrier_thickness}\n',
                    f'"carrier_ring_bearing_ID"= {self.carrier_ring_bearing_ID}\n',
                    f'"carrier_ring_bearing_OD"= {self.carrier_ring_bearing_OD}\n',
                    f'"carrier_ring_bearing_width"= {self.carrier_ring_bearing_width}\n',   
            ]
            eqFile.writelines(l)
        eqFile.close()

    def genEquationFile_editCADdirectly(self):
        # writing values into text file imported which is imported into solidworks
        self.setVariables()
        file_path = os.path.join(os.path.dirname(__file__), 'CADs', 'INWPG', 'inwpg_equations.txt')
        with open(file_path, 'w') as eqFile:
            l = [
                    f'"Ns"= {self.Ns}\n',
                    f'"Np_b"= {self.Np_b}\n',
                    f'"Np_s"= {self.Np_s}\n',
                    f'"Nr_b"= {self.Nr_b}\n',
                    f'"Nr_s"= {self.Nr_s}\n',
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
                    f'"big_ring_radial_width"= {self.big_ring_radial_width}\n',
                    f'"small_ring_radial_width"= {self.small_ring_radial_width}\n',
                    f'"ring_gearbox_casing_thickness"= {self.ring_gearbox_casing_thickness}\n',
                    f'"h_a"= {self.h_a}\n',
                    f'"h_b"= {self.h_b}\n',
                    f'"h_f"= {self.h_f}\n',
                    f'"clr_tip_root"= {self.clr_tip_root}\n',
                    f'"clr_tip_root_s"= {self.clr_tip_root_s}\n',
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
                    f'"dp_r_b"= {self.dp_r_b}\n',
                    f'"db_r_b"= {self.db_r_b}\n',
                    f'"alpha_r_b"= {self.alpha_r_b}\n',
                    f'"beta_r_b"= {self.beta_r_b}\n',
                    f'"fw_r_b"= {self.fw_r_b}\n',
                    f'"dp_r_s"= {self.dp_r_s}\n',
                    f'"db_r_s"= {self.db_r_s}\n',
                    f'"alpha_r_s"= {self.alpha_r_s}\n',
                    f'"beta_r_s"= {self.beta_r_s}\n',
                    f'"fw_r_s"= {self.fw_r_s}\n',
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
                    f'"carrier_thickness"= {self.carrier_thickness}\n',
                    f'"carrier_ring_bearing_ID"= {self.carrier_ring_bearing_ID}\n',
                    f'"carrier_ring_bearing_OD"= {self.carrier_ring_bearing_OD}\n',
                    f'"carrier_ring_bearing_width"= {self.carrier_ring_bearing_width}\n',   
            ]
            eqFile.writelines(l)
        eqFile.close()

        file_path = os.path.join(os.path.dirname(__file__), 'CADs', 'INWPG', 'inwpg_equations_onshape.txt')
        with open(file_path, 'w') as eqFile:
            l = [
                    f'"Ns"= {self.Ns}\n',
                    f'"Np_b"= {self.Np_b}\n',
                    f'"Np_s"= {self.Np_s}\n',
                    f'"Nr_b"= {self.Nr_b}\n',
                    f'"Nr_s"= {self.Nr_s}\n',
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
                    f'"big_ring_radial_width"= {self.big_ring_radial_width}\n',
                    f'"small_ring_radial_width"= {self.small_ring_radial_width}\n',
                    f'"ring_gearbox_casing_thickness"= {self.ring_gearbox_casing_thickness}\n',
                    f'"h_a"= {self.h_a}\n',
                    f'"h_b"= {self.h_b}\n',
                    f'"h_f"= {self.h_f}\n',
                    f'"clr_tip_root"= {self.clr_tip_root}\n',
                    f'"clr_tip_root_s"= {self.clr_tip_root_s}\n',
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
                    f'"dp_r_b"= {self.dp_r_b}\n',
                    f'"db_r_b"= {self.db_r_b}\n',
                    f'"alpha_r_b"= {self.alpha_r_b}\n',
                    f'"beta_r_b"= {self.beta_r_b}\n',
                    f'"fw_r_b"= {self.fw_r_b}\n',
                    f'"dp_r_s"= {self.dp_r_s}\n',
                    f'"db_r_s"= {self.db_r_s}\n',
                    f'"alpha_r_s"= {self.alpha_r_s}\n',
                    f'"beta_r_s"= {self.beta_r_s}\n',
                    f'"fw_r_s"= {self.fw_r_s}\n',
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
                    f'"carrier_thickness"= {self.carrier_thickness}\n',
                    f'"carrier_ring_bearing_ID"= {self.carrier_ring_bearing_ID}\n',
                    f'"carrier_ring_bearing_OD"= {self.carrier_ring_bearing_OD}\n',
                    f'"carrier_ring_bearing_width"= {self.carrier_ring_bearing_width}\n',   
            ]
            eqFile.writelines(l)
        eqFile.close()
    
    # ----------------------------------------
    # Mass of New Design 
    #-----------------------------------------
    def getToothForces(self, constraintCheck=False):
        if constraintCheck:
            # Check if the constraints are satisfied
            if not self.inrunnerWolfromPlanetaryGearbox.geometricConstraint():
                print("Geometric constraint not satisfied")
                return
            if not self.inrunnerWolfromPlanetaryGearbox.meshingConstraint():
                print("Meshing constraint not satisfied")
                return
            if not self.inrunnerWolfromPlanetaryGearbox.noPlanetInterferenceConstraint():
                print("No planet interference constraint not satisfied")
                return

        Ns          = self.inrunnerWolfromPlanetaryGearbox.Ns
        NpBig       = self.inrunnerWolfromPlanetaryGearbox.NpBig
        NpSmall     = self.inrunnerWolfromPlanetaryGearbox.NpSmall
        NrBig       = self.inrunnerWolfromPlanetaryGearbox.NrBig
        NrSmall     = self.inrunnerWolfromPlanetaryGearbox.NrSmall
        numPlanet   = self.inrunnerWolfromPlanetaryGearbox.numPlanet
        moduleBig   = self.inrunnerWolfromPlanetaryGearbox.moduleBig
        moduleSmall = self.inrunnerWolfromPlanetaryGearbox.moduleSmall

        RpBig_Mt   = self.inrunnerWolfromPlanetaryGearbox.getPCRadiusPlanetBigM()
        RpSmall_Mt = self.inrunnerWolfromPlanetaryGearbox.getPCRadiusPlanetSmallM()
        Rs_Mt      = self.inrunnerWolfromPlanetaryGearbox.getPCRadiusSunM()
        RrBig_Mt   = self.inrunnerWolfromPlanetaryGearbox.getPCRadiusRingBigM()
        RrSmall_Mt = self.inrunnerWolfromPlanetaryGearbox.getPCRadiusRingSmallM()

        wSun       = self.motor.getMaxMotorAngVelRadPerSec()
        wPlanet    = (-Ns / (2*NpBig) ) * wSun
        wCarrier   = (Ns / (Ns + NrBig)) * wSun
        wRingSmall = (Ns * (NpBig - NpSmall) / (2 * NrSmall * NpBig)) * wSun
        
        I1 = NrBig/Ns
        I2 = ( (NrBig * NpSmall) / (NpBig * NrSmall))
        I3 = RpSmall_Mt / RpBig_Mt

        Ft_sp_big = (self.serviceFactor*self.motor.getMaxMotorTorque()*1000) / (numPlanet * moduleBig * (Ns / 2))
        Ft_rp_big = ((self.serviceFactor*self.motor.getMaxMotorTorque()*1000) * (I1 + I2)) / (numPlanet * moduleBig * (NrBig/2) * (1-I2))
        Ft_rp_small = -((self.serviceFactor*self.motor.getMaxMotorTorque()*1000) * (1+I1)) / (numPlanet * moduleSmall * (NrSmall/2) * (1-I2))

        if (RpBig_Mt > RpSmall_Mt):
            Ft_sp_big_alt = (self.serviceFactor*self.motor.getMaxMotorTorque()) / (numPlanet * (Rs_Mt))
            Ft_rp_big_alt = ((self.serviceFactor*self.motor.getMaxMotorTorque()) * (1 + I3)) / (numPlanet * (Rs_Mt) * (1 - I3))
            Ft_rp_small_alt = -((self.serviceFactor*self.motor.getMaxMotorTorque()) * (2)) / (numPlanet * (Rs_Mt) * (1 - I3))

            # check the error in the force calculation
            if np.abs(Ft_sp_big - Ft_sp_big_alt) > 1e-6:
                print("----------------------------------------------")
                print("                   ERROR                      ")
                print("----------------------------------------------")
                print("Ft_sp_big not equal to Ft_sp_big_alt")
                print("Ft_sp_big:", Ft_sp_big)
                print("Ft_sp_big_alt:", Ft_sp_big_alt)

            if np.abs(Ft_rp_big - Ft_rp_big_alt) > 1e-6:
                print("----------------------------------------------")
                print("                   ERROR                      ")
                print("----------------------------------------------")
                print("Ft_rp_big not equal to Ft_rp_big_alt")
                print("Ft_rp_big:", Ft_rp_big)
                print("Ft_rp_big_alt:", Ft_rp_big_alt)

            if np.abs(Ft_rp_small - Ft_rp_small_alt) > 1e-6:
                print("----------------------------------------------")
                print("                   ERROR                      ")
                print("----------------------------------------------")
                print("Ft_rp_small not equal to Ft_rp_small_alt")
                print("Ft_rp_small:", Ft_rp_small)
                print("Ft_rp_small_alt:", Ft_rp_small_alt)
        else:
            print("Invalid value of RpBig and RpSmall")
            print("RpBig:", RpBig_Mt)
            print("NpBig:", NpBig)
            print(" ")
            print("RpSmall:", RpSmall_Mt)
            print("NpSmall:", NpSmall)

        Ft = [Ft_sp_big, Ft_rp_big, Ft_rp_small]
        return Ft

    def lewisStressAnalysisMinFacewidth(self):
        # Check if the constraints are satisfied
        if not self.inrunnerWolfromPlanetaryGearbox.geometricConstraint():
            print("Geometric constraint not satisfied")
            return
        if not self.inrunnerWolfromPlanetaryGearbox.meshingConstraint():
            print("Meshing constraint not satisfied")
            return
        if not self.inrunnerWolfromPlanetaryGearbox.noPlanetInterferenceConstraint():
            print("No planet interference constraint not satisfied")
            return

        Ns          = self.inrunnerWolfromPlanetaryGearbox.Ns
        NpBig       = self.inrunnerWolfromPlanetaryGearbox.NpBig
        NpSmall     = self.inrunnerWolfromPlanetaryGearbox.NpSmall
        NrBig       = self.inrunnerWolfromPlanetaryGearbox.NrBig
        NrSmall     = self.inrunnerWolfromPlanetaryGearbox.NrSmall
        numPlanet   = self.inrunnerWolfromPlanetaryGearbox.numPlanet
        moduleBig   = self.inrunnerWolfromPlanetaryGearbox.moduleBig
        moduleSmall = self.inrunnerWolfromPlanetaryGearbox.moduleSmall

        RpBig = NpBig * moduleBig / 2
        RpSmall = NpSmall * moduleSmall / 2
        Rs = Ns * moduleBig / 2
        RrBig = NrBig * moduleBig / 2
        RrSmall = NrSmall * moduleSmall / 2

        wSun       = self.motor.getMaxMotorAngVelRadPerSec()
        wPlanet    = (-Ns / (2*NpBig) ) * wSun
        wCarrier   = (Ns / (Ns + NrBig)) * wSun
        wRingSmall = (Ns * (NpBig - NpSmall) / (2 * NrSmall * NpBig)) * wSun

        [Ft_sp_big, Ft_rp_big, Ft_rp_small]  = self.getToothForces(False)

        ySun         = 0.154 - 0.912/Ns
        yPlanetBig   = 0.154 - 0.912/NpBig
        yPlanetSmall = 0.154 - 0.912/NpSmall
        yRingSmall   = 0.154 - 0.912/NrSmall
        yRingBig     = 0.154 - 0.912/NrBig

        V_sp_big = (self.inrunnerWolfromPlanetaryGearbox.getPCRadiusSunM() * wSun)
        V_rp_big = (wCarrier*(self.inrunnerWolfromPlanetaryGearbox.getPCRadiusSunM() + self.inrunnerWolfromPlanetaryGearbox.getPCRadiusPlanetBigM()) + 
                    wPlanet*(self.inrunnerWolfromPlanetaryGearbox.getPCRadiusPlanetBigM()))
        V_rp_small = (wCarrier*(self.inrunnerWolfromPlanetaryGearbox.getPCRadiusSunM() + self.inrunnerWolfromPlanetaryGearbox.getPCRadiusPlanetBigM()) +
                      wPlanet*(self.inrunnerWolfromPlanetaryGearbox.getPCRadiusPlanetSmallM()))
        
        # Check 
        V_rp_small_test = wRingSmall*(self.inrunnerWolfromPlanetaryGearbox.getPCRadiusSunM() + self.inrunnerWolfromPlanetaryGearbox.getPCRadiusPlanetBigM()
                                      + self.inrunnerWolfromPlanetaryGearbox.getPCRadiusPlanetSmallM())
        
        if np.abs(V_rp_small - V_rp_small_test) > 1e-6:
            print("----------------------------------------------")
            print("                   ERROR                      ")
            print("----------------------------------------------")
            print("V_rp_small not equal to V_rp_small_test")
            print("V_rp_small:", V_rp_small)
            print("V_rp_small_test:", V_rp_small_test)
        
        if V_sp_big <= 7.5:
            Kv_sun = 3/(3+V_sp_big)
            Kv_planetBig1 = 3/(3+V_sp_big)
        elif V_sp_big > 7.5 and V_sp_big <= 12.5:
            Kv_sun = 4.5/(4.5 + V_sp_big)
            Kv_planetBig1 = 4.5/(4.5 + V_sp_big)
        else:
            Kv_sun = 4.5/(4.5 + V_sp_big)
            Kv_planetBig1 = 4.5/(4.5 + V_sp_big)

        if V_rp_big <= 7.5:
            Kv_planetBig2 = 3/(3+V_rp_big)
            Kv_ringBig = 3/(3+V_rp_big)
        elif V_rp_big > 7.5 and V_rp_big <= 12.5:
            Kv_planetBig2 = 4.5/(4.5 + V_rp_big)
            Kv_ringBig = 4.5/(4.5 + V_rp_big)

        if V_rp_small <= 7.5:
            Kv_planetSmall = 3/(3+V_rp_small)
            Kv_ringSmall = 3/(3+V_rp_small)
        elif V_rp_small > 7.5 and V_rp_small <= 12.5:
            Kv_planetSmall = 4.5/(4.5 + V_rp_small)
            Kv_ringSmall = 4.5/(4.5 + V_rp_small)
        
        P_big   = np.pi*moduleBig*0.001 # m
        P_small = np.pi*moduleSmall*0.001 # m

        # # Print
        # print("V_sp_big:", V_sp_big)
        # print("V_rp_big:", V_rp_big)
        # print("V_rp_small:", V_rp_small)

        # Lewis static load capacity
        bMin_sun         = (self.FOS * np.abs(Ft_sp_big   )/ (self.inrunnerWolfromPlanetaryGearbox.maxGearAllowableStressPa * ySun * Kv_sun * P_big)) # m
        bMin_planetBig1  = (self.FOS * np.abs(Ft_sp_big   )/ (self.inrunnerWolfromPlanetaryGearbox.maxGearAllowableStressPa * yPlanetBig * Kv_planetBig1 * P_big))
        bMin_planetBig2  = (self.FOS * np.abs(Ft_sp_big   )/ (self.inrunnerWolfromPlanetaryGearbox.maxGearAllowableStressPa * yPlanetBig * Kv_planetBig2 * P_big))
        bMin_planetSmall = (self.FOS * np.abs(Ft_rp_small )/ (self.inrunnerWolfromPlanetaryGearbox.maxGearAllowableStressPa * yPlanetSmall * Kv_planetSmall * P_small))
        bMin_ringBig     = (self.FOS * np.abs(Ft_rp_big   )/ (self.inrunnerWolfromPlanetaryGearbox.maxGearAllowableStressPa * yRingBig * Kv_ringBig * P_big))
        bMin_ringSmall   = (self.FOS * np.abs(Ft_rp_small )/ (self.inrunnerWolfromPlanetaryGearbox.maxGearAllowableStressPa * yRingSmall * Kv_ringSmall * P_small))

        # Making the width of the bigger planet to be the maximum of the two
        if bMin_planetBig1 > bMin_planetBig2:
            bMin_planetBig = bMin_planetBig1
        else:
            bMin_planetBig = bMin_planetBig2

        # Making the width of ring and planet in the second layer to be same
        if bMin_ringSmall < bMin_planetSmall:
            bMin_ringSmall = bMin_planetSmall
        else:
            bMin_planetSmall = bMin_ringSmall

        # Making the width of ring and planet in the first layer to be same
        if bMin_ringBig < bMin_planetBig:
            bMin_ringBig = bMin_planetBig
        else:
            bMin_planetBig = bMin_ringBig

        self.inrunnerWolfromPlanetaryGearbox.setfwSunMM         ( bMin_sun*1000 )
        self.inrunnerWolfromPlanetaryGearbox.setfwPlanetBigMM   ( bMin_planetBig*1000 )
        self.inrunnerWolfromPlanetaryGearbox.setfwPlanetSmallMM ( bMin_planetSmall*1000 )
        self.inrunnerWolfromPlanetaryGearbox.setfwRingSmallMM   ( bMin_ringSmall*1000 )
        self.inrunnerWolfromPlanetaryGearbox.setfwRingBigMM     ( bMin_ringBig*1000 )
        # print("Lewis:")
        # print(f"bMin_planetSmall = {bMin_planetSmall}")
        # print(f"bMin_planetBig = {bMin_planetBig}")
        # print(f"bMin_sun = {bMin_sun}")
        # print(f"bMin_ringSmall = {bMin_ringSmall}")
        # print(f"bMin_ringBig = {bMin_ringBig}")

    def AGMAStressAnalysisMinFacewidth(self):
        # Check if the constraints are satisfied
        if not self.inrunnerWolfromPlanetaryGearbox.geometricConstraint():
            print("Geometric constraint not satisfied")
            return
        if not self.inrunnerWolfromPlanetaryGearbox.meshingConstraint():
            print("Meshing constraint not satisfied")
            return
        if not self.inrunnerWolfromPlanetaryGearbox.noPlanetInterferenceConstraint():
            print("No planet interference constraint not satisfied")
            return

        Ns          = self.inrunnerWolfromPlanetaryGearbox.Ns
        NpBig       = self.inrunnerWolfromPlanetaryGearbox.NpBig
        NpSmall     = self.inrunnerWolfromPlanetaryGearbox.NpSmall
        NrBig       = self.inrunnerWolfromPlanetaryGearbox.NrBig
        NrSmall     = self.inrunnerWolfromPlanetaryGearbox.NrSmall
        numPlanet   = self.inrunnerWolfromPlanetaryGearbox.numPlanet
        moduleBig   = self.inrunnerWolfromPlanetaryGearbox.moduleBig
        moduleSmall = self.inrunnerWolfromPlanetaryGearbox.moduleSmall

        RpBig = NpBig * moduleBig / 2
        RpSmall = NpSmall * moduleSmall / 2
        Rs = Ns * moduleBig / 2
        RrBig = NrBig * moduleBig / 2
        RrSmall = NrSmall * moduleSmall / 2

        wSun       = self.motor.getMaxMotorAngVelRadPerSec()
        wPlanet    = (-Ns / (2*NpBig) ) * wSun
        wCarrier   = (Ns / (Ns + NrBig)) * wSun
        wRingSmall = (Ns * (NpBig - NpSmall) / (2 * NrSmall * NpBig)) * wSun

        [Wt_sp_big, Wt_rp_big, Wt_rp_small]  = self.getToothForces(False)

        pressureAngle = self.inrunnerWolfromPlanetaryGearbox.pressureAngleDEG

        # T Krishna Rao - Design of Machine Elements - II pg.191
        # Modified Lewis Form Factor Y = pi*y for pressure angle = 20
        Y_sun         = (0.154 - 0.912/Ns) * np.pi
        Y_planetBig   = (0.154 - 0.912/NpBig) * np.pi
        Y_planetSmall = (0.154 - 0.912/NpSmall) * np.pi
        Y_ringSmall   = (0.154 - 0.912/NrSmall) * np.pi
        Y_ringBig     = (0.154 - 0.912/NrBig) * np.pi

        V_sp_big = np.abs(self.inrunnerWolfromPlanetaryGearbox.getPCRadiusSunM() * wSun)
        V_rp_big = np.abs(wCarrier*(self.inrunnerWolfromPlanetaryGearbox.getPCRadiusSunM() + self.inrunnerWolfromPlanetaryGearbox.getPCRadiusPlanetBigM()) + 
                    wPlanet*(self.inrunnerWolfromPlanetaryGearbox.getPCRadiusPlanetBigM()))
        V_rp_small = np.abs(wCarrier*(self.inrunnerWolfromPlanetaryGearbox.getPCRadiusSunM() + self.inrunnerWolfromPlanetaryGearbox.getPCRadiusPlanetBigM()) +
                      wPlanet*(self.inrunnerWolfromPlanetaryGearbox.getPCRadiusPlanetSmallM()))
        
        # Check 
        V_rp_small_test = wRingSmall*(self.inrunnerWolfromPlanetaryGearbox.getPCRadiusSunM() + self.inrunnerWolfromPlanetaryGearbox.getPCRadiusPlanetBigM()
                                      + self.inrunnerWolfromPlanetaryGearbox.getPCRadiusPlanetSmallM())
        
        if np.abs(V_rp_small - V_rp_small_test) > 1e-6:
            print("----------------------------------------------")
            print("                   ERROR                      ")
            print("----------------------------------------------")
            print("V_rp_small not equal to V_rp_small_test")
            print("V_rp_small:", V_rp_small)
            print("V_rp_small_test:", V_rp_small_test)

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

        t_ringSmall = (13.5 * Y_ringSmall)**(1/2) * moduleSmall
        r_ringSmall = 0.3 * moduleSmall 
        l_ringSmall = 2.25 * moduleSmall
        Kf_ringSmall = H + (t_ringSmall / r_ringSmall)**(L) * (t_ringSmall / l_ringSmall)**(M)

        t_ringBig = (13.5 * Y_ringBig)**(1/2) * moduleBig
        r_ringBig = 0.3 * moduleBig
        l_ringBig = 2.25 * moduleBig
        Kf_ringBig = H + (t_ringBig / r_ringBig)**(L) * (t_ringBig / l_ringBig)**(M)

        # Shigley's Mechanical Engineering Design 9th Edition pg.752
        # Yj Geometry factor
        Yj_planetSmall = Y_planetSmall/Kf_planetSmall
        Yj_planetBig = Y_planetBig/Kf_planetBig
        Yj_sun = Y_sun/Kf_sun
        Yj_ringSmall = Y_ringSmall/Kf_ringSmall
        Yj_ringBig = Y_ringBig/Kf_ringBig 
        
        # Kv Dynamic factor
        # Shigley's Mechanical Engineering Design 9th Edition pg.756
        Qv = 7      # Quality numbers 3 to 7 will include most commercial-quality gears.
        B_planetSmall =  0.25*(12-Qv)**(2/3)
        A_planetSmall = 50 + 56*(1-B_planetSmall)
        Kv_planetSmall = ((A_planetSmall+np.sqrt(200*V_rp_small))/A_planetSmall)**B_planetSmall

        B_planetBig =  0.25*(12-Qv)**(2/3)
        A_planetBig = 50 + 56*(1-B_planetBig)
        Kv_planetBig = ((A_planetBig+np.sqrt(200*max(V_sp_big, V_rp_big)))/A_planetBig)**B_planetBig

        B_sun =  0.25*(12-Qv)**(2/3)
        A_sun = 50 + 56*(1-B_sun)
        Kv_sun = ((A_sun+np.sqrt(200*V_sp_big))/A_sun)**B_sun

        B_ringSmall =  0.25*(12-Qv)**(2/3)
        A_ringSmall = 50 + 56*(1-B_ringSmall)
        Kv_ringSmall = ((A_ringSmall+np.sqrt(200*V_rp_small))/A_ringSmall)**B_planetSmall

        B_ringBig =  0.25*(12-Qv)**(2/3)
        A_ringBig = 50 + 56*(1-B_ringBig)
        Kv_ringBig = ((A_ringBig+np.sqrt(200*V_rp_big))/A_ringBig)**B_planetBig

        # Shigley's Mechanical Engineering Design 9th Edition pg.764
        # Ks Size factor (can be omitted if enough information is not available)
        Ks = 1

        # NPTEL Fatigue Consideration in Design lecture-7 pg.10 Table-7.4 (https://archive.nptel.ac.in/courses/112/106/112106137/)
        # Kh Load-distribution factor (0-50mm, less rigid mountings, less accurate gears)
        Kh = 1.3

        # Shigley's Mechanical Engineering Design 9th Edition pg.764
        # Kb Rim-thickness factor (the gears have a uniform thickness)
        Kb = 1
        
        # AGMA bending stress equation (Shigley's Mechanical Engineering Design 9th Edition pg.746)  
        bMin_planetSmall = (self.FOS * np.abs(Wt_rp_small) * Kv_planetSmall * Ks * Kh * Kb)/(moduleSmall * Yj_planetSmall * self.inrunnerWolfromPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        bMin_planetBig = (self.FOS * np.abs(Wt_rp_big) * Kv_planetBig * Ks * Kh * Kb)/(moduleBig * Yj_planetBig * self.inrunnerWolfromPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        bMin_sun = (self.FOS * np.abs(Wt_sp_big) * Kv_sun * Ks * Kh * Kb) / (moduleBig * Yj_sun * self.inrunnerWolfromPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        bMin_ringSmall = (self.FOS * np.abs(Wt_rp_small) * Kv_ringSmall * Ks * Kh * Kb) / (moduleSmall * Yj_ringSmall * self.inrunnerWolfromPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        bMin_ringBig = (self.FOS * np.abs(Wt_rp_big) * Kv_ringBig * Ks * Kh * Kb) / (moduleBig * Yj_ringBig * self.inrunnerWolfromPlanetaryGearbox.maxGearAllowableStressPa * 0.001)

        # C_pm = 1.1
        # X_planetSmall = (self.FOS * np.abs(Wt_rp_small) * Kv_planetSmall * Ks * Kb)/(moduleSmall * Y_planetSmall * self.inrunnerWolfromPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        # X_planetBig = (self.FOS * np.abs(Wt_rp_big) * Kv_planetBig * Ks * Kb)/(moduleBig * Y_planetBig * self.inrunnerWolfromPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        # X_sun = (self.FOS * np.abs(Wt_sp_big) * Kv_sun * Ks * Kb) / (moduleBig * Y_sun * self.inrunnerWolfromPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        # X_ringSmall = (self.FOS * np.abs(Wt_rp_small) * Kv_ringSmall * Ks * Kb) / (moduleSmall * Y_ringSmall * self.inrunnerWolfromPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        # X_ringBig = (self.FOS * np.abs(Wt_rp_big) * Kv_ringBig * Ks * Kb) / (moduleBig * Y_ringBig * self.inrunnerWolfromPlanetaryGearbox.maxGearAllowableStressPa * 0.001)

        # co_eff_of_fwSqr = 0.93/10000
        # co_eff_of_fw_planetSmall = -(C_pm/(moduleSmall*NpSmall*10*0.03937)) + 1/(39.37*X_planetSmall) - 0.0158
        # co_eff_of_fw_planetBig = -(C_pm/(moduleBig*NpBig*10*0.03937)) + 1/(39.37*X_planetBig) - 0.0158
        # co_eff_of_fw_sun = -(C_pm/(moduleBig*Ns*10*0.03937)) + 1/(39.37*X_sun) - 0.0158
        # co_eff_of_fw_ringSmall = -(C_pm/(moduleSmall*NrSmall*10*0.03937)) + 1/(39.37*X_ringSmall) - 0.0158
        # co_eff_of_fw_ringBig = -(C_pm/(moduleBig*NrBig*10*0.03937)) + 1/(39.37*X_ringBig) - 0.0158
        # constant = -1.0995

        # bMin_planetSmall = max(np.roots([co_eff_of_fwSqr, co_eff_of_fw_planetSmall, constant]))/39.37
        # bMin_planetBig = max(np.roots([co_eff_of_fwSqr, co_eff_of_fw_planetBig, constant]))/39.37
        # bMin_sun = max(np.roots([co_eff_of_fwSqr, co_eff_of_fw_sun, constant]))/39.37
        # bMin_ringSmall = max(np.roots([co_eff_of_fwSqr, co_eff_of_fw_ringSmall, constant]))/39.37
        # bMin_ringBig = max(np.roots([co_eff_of_fwSqr, co_eff_of_fw_ringBig, constant]))/39.37

        # if bMin_planetSmall > 0.026:
        #     co_eff_of_fw_planetSmall = -(C_pm/(moduleSmall*NpSmall*10*0.03937)) + 1/(39.37*X_planetSmall) - 0.1533
        #     constant = -1.08575
        #     bMin_planetSmall = max(np.roots([co_eff_of_fwSqr, co_eff_of_fw_planetSmall, constant]))/39.37

        # if bMin_planetBig > 0.026:
        #     co_eff_of_fw_planetBig = -(C_pm/(moduleBig*NpBig*10*0.03937)) + 1/(39.37*X_planetBig) - 0.1533
        #     constant = -1.08575
        #     bMin_planetBig = max(np.roots([co_eff_of_fwSqr, co_eff_of_fw_planetBig, constant]))/39.37

        # if bMin_ringSmall > 0.026:
        #     co_eff_of_fw_ringSmall = -(C_pm/(moduleSmall*NrSmall*10*0.03937)) + 1/(39.37*X_ringSmall) - 0.1533
        #     constant = -1.08575
        #     bMin_ringSmall = max(np.roots([co_eff_of_fwSqr, co_eff_of_fw_ringSmall, constant]))/39.37

        # if bMin_ringBig > 0.026:
        #     co_eff_of_fw_ringBig = -(C_pm/(moduleBig*NrBig*10*0.03937)) + 1/(39.37*X_ringBig) - 0.1533
        #     constant = -1.08575
        #     bMin_ringBig = max(np.roots([co_eff_of_fwSqr, co_eff_of_fw_ringBig, constant]))/39.37

        # if bMin_sun > 0.026:
        #     co_eff_of_fw_sun = -(C_pm/(moduleBig*Ns*10*0.03937)) + 1/(39.37*X_sun) - 0.1533
        #     constant = -1.08575
        #     bMin_sun = max(np.roots([co_eff_of_fwSqr, co_eff_of_fw_sun, constant]))/39.37

        # Making the width of ring and planet in the second layer to be same
        if bMin_ringSmall < bMin_planetSmall:
            bMin_ringSmall = bMin_planetSmall
        else:
            bMin_planetSmall = bMin_ringSmall

        # Making the width of ring and planet in the first layer to be same
        if bMin_ringBig < bMin_planetBig:
            bMin_ringBig = bMin_planetBig
        else:
            bMin_planetBig = bMin_ringBig

        self.inrunnerWolfromPlanetaryGearbox.setfwSunMM         ( bMin_sun*1000 )
        self.inrunnerWolfromPlanetaryGearbox.setfwPlanetBigMM   ( bMin_planetBig*1000 )
        self.inrunnerWolfromPlanetaryGearbox.setfwPlanetSmallMM ( bMin_planetSmall*1000 )
        self.inrunnerWolfromPlanetaryGearbox.setfwRingSmallMM   ( bMin_ringSmall*1000 )
        self.inrunnerWolfromPlanetaryGearbox.setfwRingBigMM     ( bMin_ringBig*1000 )

        # print("AGMA:")
        # print(f"bMin_planetSmall = {bMin_planetSmall}")
        # print(f"bMin_planetBig = {bMin_planetBig}")
        # print(f"bMin_sun = {bMin_sun}")
        # print(f"bMin_ringSmall = {bMin_ringSmall}")
        # print(f"bMin_ringBig = {bMin_ringBig}")

    def mitStressAnalysisMinFacewidth(self):
        # Check if the constraints are satisfied
        if not self.inrunnerWolfromPlanetaryGearbox.geometricConstraint():
            print("Geometric constraint not satisfied")
            return
        if not self.inrunnerWolfromPlanetaryGearbox.meshingConstraint():
            print("Meshing constraint not satisfied")
            return
        if not self.inrunnerWolfromPlanetaryGearbox.noPlanetInterferenceConstraint():
            print("No planet interference constraint not satisfied")
            return

        Ns          = self.inrunnerWolfromPlanetaryGearbox.Ns
        NpBig       = self.inrunnerWolfromPlanetaryGearbox.NpBig
        NpSmall     = self.inrunnerWolfromPlanetaryGearbox.NpSmall
        NrBig       = self.inrunnerWolfromPlanetaryGearbox.NrBig
        NrSmall     = self.inrunnerWolfromPlanetaryGearbox.NrSmall
        numPlanet   = self.inrunnerWolfromPlanetaryGearbox.numPlanet
        moduleBig   = self.inrunnerWolfromPlanetaryGearbox.moduleBig
        moduleSmall = self.inrunnerWolfromPlanetaryGearbox.moduleSmall

        RpBig = NpBig * moduleBig / 2
        RpSmall = NpSmall * moduleSmall / 2
        Rs = Ns * moduleBig / 2
        RrBig = NrBig * moduleBig / 2
        RrSmall = NrSmall * moduleSmall / 2

        wSun       = self.motor.getMaxMotorAngVelRadPerSec()
        wPlanet    = (-Ns / (2*NpBig) ) * wSun
        wCarrier   = (Ns / (Ns + NrBig)) * wSun
        wRingSmall = (Ns * (NpBig - NpSmall) / (2 * NrSmall * NpBig)) * wSun

        [Ft_sp_big, Ft_rp_big, Ft_rp_small]  = self.getToothForces(False)

        # Lewis static load capacity
        _,_,CR_SP1 = self.inrunnerWolfromPlanetaryGearbox.contactRatio_sunPlanet_stg1()
        _,_,CR_PR1 = self.inrunnerWolfromPlanetaryGearbox.contactRatio_planetRing_stg1()
        _,_,CR_PR2 = self.inrunnerWolfromPlanetaryGearbox.contactRatio_planetRing_stg2()

        qe_sp1 = 1 / CR_SP1
        qe_pr1 = 1 / CR_PR1
        qe_pr2 = 1 / CR_PR2

        qk_sp1 = (7.65734266e-08 * Ns**4
                - 2.19500130e-05 * Ns**3
                + 2.33893357e-03 * Ns**2
                - 1.13320908e-01 * Ns
                + 4.44727778)
        qk_pr1 = (7.65734266e-08 * NpBig**4
                - 2.19500130e-05 * NpBig**3
                + 2.33893357e-03 * NpBig**2
                - 1.13320908e-01 * NpBig
                + 4.44727778)
        qk_pr2 = (7.65734266e-08 * NpSmall**4
                - 2.19500130e-05 * NpSmall**3
                + 2.33893357e-03 * NpSmall**2
                - 1.13320908e-01 * NpSmall
                + 4.44727778)

        # Lewis static load capacity
        bMin_sun_mit           = (self.FOS * np.abs(Ft_sp_big  ) * qe_sp1 * qk_sp1 / (self.inrunnerWolfromPlanetaryGearbox.maxGearAllowableStressPa * moduleBig   * 0.001))
        bMin_planetBig_mit_1   = (self.FOS * np.abs(Ft_sp_big  ) * qe_sp1 * qk_sp1 / (self.inrunnerWolfromPlanetaryGearbox.maxGearAllowableStressPa * moduleBig   * 0.001))
        bMin_planetBig_mit_2   = (self.FOS * np.abs(Ft_rp_big  ) * qe_pr1 * qk_pr1 / (self.inrunnerWolfromPlanetaryGearbox.maxGearAllowableStressPa * moduleBig   * 0.001))
        bMin_planetSmall_mit   = (self.FOS * np.abs(Ft_rp_small) * qe_pr2 * qk_pr2 / (self.inrunnerWolfromPlanetaryGearbox.maxGearAllowableStressPa * moduleSmall * 0.001))
        bMin_ringBig_mit       = (self.FOS * np.abs(Ft_rp_big  ) * qe_pr1 * qk_pr1 / (self.inrunnerWolfromPlanetaryGearbox.maxGearAllowableStressPa * moduleBig   * 0.001))
        bMin_ringSmall_mit     = (self.FOS * np.abs(Ft_rp_small) * qe_pr2 * qk_pr2 / (self.inrunnerWolfromPlanetaryGearbox.maxGearAllowableStressPa * moduleSmall * 0.001))

        if (bMin_planetBig_mit_1 > bMin_planetBig_mit_2):
            bMin_planetBig_mit = bMin_planetBig_mit_1
        else:
            bMin_planetBig_mit = bMin_planetBig_mit_2

        #------------- Contraint in planet to accomodate its bearings------------------------------------------
        if ((bMin_planetBig_mit + bMin_planetSmall_mit) * 1000 < (self.planet_bearing_width*2 + self.standard_clearance_1_5mm * 2 / 3)) : 
            if ((bMin_planetBig_mit) * 1000 < (self.planet_bearing_width + self.standard_clearance_1_5mm * 1 / 3)): 
                bMin_planetBig_mit = (self.planet_bearing_width + self.standard_clearance_1_5mm * 1 / 3) / 1000
            if ((bMin_planetSmall_mit) * 1000 < (self.planet_bearing_width + self.standard_clearance_1_5mm * 1 / 3)): 
                bMin_planetSmall_mit = (self.planet_bearing_width + self.standard_clearance_1_5mm * 1 / 3) / 1000
            bMin_ringBig_mit   = bMin_planetBig_mit
            bMin_ringSmall_mit = bMin_planetSmall_mit

        bMin_sun_mitMM         = bMin_sun_mit * 1000
        bMin_planetBig_mitMM   = bMin_planetBig_mit * 1000
        bMin_planetSmall_mitMM = bMin_planetSmall_mit * 1000
        bMin_ringBig_mitMM     = bMin_ringBig_mit * 1000
        bMin_ringSmall_mitMM   = bMin_ringSmall_mit * 1000

        self.inrunnerWolfromPlanetaryGearbox.setfwSunMM         ( bMin_sun_mit         * 1000 )
        self.inrunnerWolfromPlanetaryGearbox.setfwPlanetBigMM   ( bMin_planetBig_mit   * 1000 )
        self.inrunnerWolfromPlanetaryGearbox.setfwPlanetSmallMM ( bMin_planetSmall_mit * 1000 )
        self.inrunnerWolfromPlanetaryGearbox.setfwRingSmallMM   ( bMin_ringSmall_mit   * 1000 )
        self.inrunnerWolfromPlanetaryGearbox.setfwRingBigMM     ( bMin_ringBig_mit     * 1000 )

        return bMin_sun_mitMM, bMin_planetBig_mitMM, bMin_planetSmall_mitMM, bMin_ringBig_mitMM, bMin_ringSmall_mitMM

    def updateFacewidth(self):
        if self.stressAnalysisMethodName == "Lewis":
            self.lewisStressAnalysisMinFacewidth()
        elif self.stressAnalysisMethodName == "AGMA":
            self.AGMAStressAnalysisMinFacewidth()
        elif self.stressAnalysisMethodName == "MIT":
            self.mitStressAnalysisMinFacewidth()

    def getMassKG_3DP(self):
        module1   = self.inrunnerWolfromPlanetaryGearbox.moduleBig  # Module of the gear
        module2   = self.inrunnerWolfromPlanetaryGearbox.moduleSmall  # Module of the gear
        Ns        = self.inrunnerWolfromPlanetaryGearbox.Ns
        Np1       = self.inrunnerWolfromPlanetaryGearbox.NpBig
        Np2       = self.inrunnerWolfromPlanetaryGearbox.NpSmall
        Nr1       = self.inrunnerWolfromPlanetaryGearbox.NrBig
        numPlanet = self.inrunnerWolfromPlanetaryGearbox.numPlanet

        #-----------------------------------------
        # Density
        #-----------------------------------------
        density_3DP_material = self.inrunnerWolfromPlanetaryGearbox.densityGears
        density_aluminum     = self.inrunnerWolfromPlanetaryGearbox.densityAluminum

        #-----------------------------------------
        # Face Width
        #-----------------------------------------
        sunFwMM     = self.inrunnerWolfromPlanetaryGearbox.fwSunMM
        planet1FwMM = self.inrunnerWolfromPlanetaryGearbox.fwPlanetBigMM
        planet2FwMM = self.inrunnerWolfromPlanetaryGearbox.fwPlanetSmallMM + self.standard_clearance_1_5mm
        ring1FwMM    = self.inrunnerWolfromPlanetaryGearbox.fwRingBigMM + self.standard_clearance_1_5mm

        sunFwM     = sunFwMM     * 1000 # TODO: check the order of the index order should be always sun, planet1, planet2, ring
        planet1FwM = planet1FwMM * 1000
        planet2FwM = planet2FwMM * 1000
        ring1FwM    = ring1FwMM    * 1000

        #-----------------------------------------
        # Diameter and Radius
        #-----------------------------------------
        DiaSunMM        = Ns  * module1
        DiaPlanet1MM    = Np1 * module1
        DiaPlanet2MM    = Np2 * module2
        DiaRing1MM       = Nr1  * module2

        RadiusSunMM     = DiaSunMM     * 0.5
        RadiusPlanet1MM = DiaPlanet1MM * 0.5
        RadiusPlanet2MM = DiaPlanet2MM * 0.5
        RadiusRing1MM    = DiaRing1MM    * 0.5

        RingOuterRadiusMM = RadiusRing1MM + 1.25*module2 + self.inrunnerWolfromPlanetaryGearbox.ringRadialWidthMMBig

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
        big_ring_radial_thickness = self.ring1RadialWidthMM
        ring_OD  = Nr1 * module2 + module2 + big_ring_radial_thickness*2

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
        ring_ID      = Nr1 * module2
        ringFwUsedMM = ring1FwMM

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

class optimizationInrunnerWolfromPlanetaryActuator:
    def __init__(self,
                 design_parameters,
                 gear_standard_parameters,
                 K_Mass                     = 1,
                 K_Eff                      = -2,
                 K_Width                    = 0.2,
                 MODULE_BIG_MIN             = 0.5,
                 MODULE_BIG_MAX             = 1.2,
                 MODULE_SMALL_MIN           = 0.5,
                 MODULE_SMALL_MAX           = 1.2,
                 NUM_PLANET_MIN             = 3,
                 NUM_PLANET_MAX             = 5,
                 NUM_TEETH_SUN_MIN          = 20,
                 NUM_TEETH_PLANET_BIG_MIN   = 20,
                 NUM_TEETH_PLANET_SMALL_MIN = 20,
                 GEAR_RATIO_MIN             = 5,
                 GEAR_RATIO_MAX             = 45,
                 GEAR_RATIO_STEP            = 1.0):
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

        self.Cost                     = 100000
        self.totalGearboxesWithReqGR  = 0
        self.totalFeasibleGearboxes   = 0
        self.cntrIterBeforeCons       = 0
        self.iter                     = 0
        self.gearRatioIter            = self.GEAR_RATIO_MIN
        self.UsePSCasVariable         = 1
        self.design_parameters        = design_parameters
        self.gear_standard_parameters = gear_standard_parameters

        self.gearRatioReq = 0

    def optimizeActuator(self, Actuator = inrunnerWolfromPlanetaryActuator, UsePSCasVariable = 1, log = 0, csv = 1, printOptParams=1, gearRatioReq = 0):
        startTime = time.time()
        self.UsePSCasVariable = UsePSCasVariable
        self.gearRatioReq = gearRatioReq
        opt_parameters = None
        if UsePSCasVariable == 0:
            opt_parameters = self.optimizeActuatorWithoutPSC(Actuator=Actuator, log=log, csv=csv, printOptParams = printOptParams)
        elif UsePSCasVariable == 1:
            opt_parameters =self.optimizeActuatorWithPSC(Actuator=Actuator, log=log, csv=csv, printOptParams=printOptParams)
        else:
            print("ERROR: \"UsePSCasVariable\" can be either 0 or 1")
        
        # Print the time in the file 
        endTime = time.time()
        totalTime = endTime - startTime
        # print("\n")
        # print("Running Time (sec)")
        # print(totalTime) 

        return totalTime, opt_parameters

    def optimizeActuatorWithoutPSC(self, Actuator = inrunnerWolfromPlanetaryActuator, log=1, csv=0, printOptParams = 1):
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
            fileName = f"./results/results_BruteForce_{Actuator.motor.motorName}/INWPG_BRUTEFORCE_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}.csv"
        elif log:
            fileName = f"./results/results_BruteForce_{Actuator.motor.motorName}/INWPG_BRUTEFORCE_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}_LOG.txt"
            
        with open(fileName, "w") as wolfromLogFile:
            sys.stdout = wolfromLogFile
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
                # print("iter, gearRatio, moduleBig, moduleSmall, Ns, NpBig, NpSmall, NrBig, NrSmall, numPlanet, PSCs, PSCp1, PSCp2, PSCr1, PSCr2,fwSunMM, fwPlanetBigMM, fwPanetSmallMM, fwRingBigMM, fwRingSmallMM,  mass, eff, peakTorque, Cost, torque_density")
                print("iter, gearRatio, moduleBig, moduleSmall, Ns, NpBig, NpSmall, NrBig, NrSmall, numPlanet, fwSunMM, fwPlanetBigMM, fwPanetSmallMM, fwRingBigMM, fwRingSmallMM,  mass, eff, peakTorque, Cost, Torque_Density, Outer_Bearing_mass, Actuator_width")

            while self.gearRatioIter <= self.GEAR_RATIO_MAX:
                opt_done = 0
                self.iter = 0
                self.Cost = 100000
                MinCost = self.Cost

                Actuator.inrunnerWolfromPlanetaryGearbox.setModuleBig(self.MODULE_BIG_MIN)
                while Actuator.inrunnerWolfromPlanetaryGearbox.moduleBig <= self.MODULE_BIG_MAX:
                    # Setting Module Small
                    Actuator.inrunnerWolfromPlanetaryGearbox.setModuleSmall(self.MODULE_SMALL_MIN)
                    while (Actuator.inrunnerWolfromPlanetaryGearbox.moduleSmall <= self.MODULE_SMALL_MAX):
                        # Setting Ns
                        Actuator.inrunnerWolfromPlanetaryGearbox.setNs(self.NUM_TEETH_SUN_MIN)
                        while (2*Actuator.inrunnerWolfromPlanetaryGearbox.getPCRadiusSunM()*1000) <= Actuator.maxGearboxDiameter:
                            # Setting Np Big
                            Actuator.inrunnerWolfromPlanetaryGearbox.setNpBig(self.NUM_TEETH_PLANET_BIG_MIN)
                            while (2*Actuator.inrunnerWolfromPlanetaryGearbox.getPCRadiusPlanetBigM()*1000) <= Actuator.maxGearboxDiameter/2:
                                # Setting Np Small
                                Actuator.inrunnerWolfromPlanetaryGearbox.setNpSmall(self.NUM_TEETH_PLANET_SMALL_MIN)
                                while (2*Actuator.inrunnerWolfromPlanetaryGearbox.getPCRadiusPlanetSmallM()*1000) <= Actuator.maxGearboxDiameter/2:
                                    # Setting Nr Small
                                    Actuator.inrunnerWolfromPlanetaryGearbox.setNrSmall(Actuator.inrunnerWolfromPlanetaryGearbox.NpSmall + 
                                                                                Actuator.inrunnerWolfromPlanetaryGearbox.NpBig +
                                                                                Actuator.inrunnerWolfromPlanetaryGearbox.Ns)
                                    # Setting Nr Big
                                    Actuator.inrunnerWolfromPlanetaryGearbox.setNrBig(2*Actuator.inrunnerWolfromPlanetaryGearbox.NpBig +
                                                                                Actuator.inrunnerWolfromPlanetaryGearbox.Ns)
                                    if ((2*Actuator.inrunnerWolfromPlanetaryGearbox.getPCRadiusRingBigM()*1000) <= Actuator.maxGearboxDiameter):# and Actuator.getIdRequired2MM() <= 100): # and ((2*Actuator.inrunnerWolfromPlanetaryGearbox.getPCRadiusRingSmallM()*1000) <= maxGearBoxDia):
                                        # TODO: Ask Deepak: What is getIDRequired2MM()? and also tell him to write a more meaningful function name
                                        # Setting number of Planet
                                        Actuator.inrunnerWolfromPlanetaryGearbox.setNumPlanet(self.NUM_PLANET_MIN)
                                        while Actuator.inrunnerWolfromPlanetaryGearbox.numPlanet <= self.NUM_PLANET_MAX:
                                            if (Actuator.inrunnerWolfromPlanetaryGearbox.geometricConstraint() and 
                                                Actuator.inrunnerWolfromPlanetaryGearbox.meshingConstraint() and 
                                                Actuator.inrunnerWolfromPlanetaryGearbox.noPlanetInterferenceConstraint() and
                                                Actuator.sunPCDConstraint() and
                                                Actuator.planetPCDConstraint() and
                                                Actuator.noSecCarrierInterferenceConstraint()):
                                                self.totalFeasibleGearboxes += 1
                                                # Fiter for the Gear Ratio
                                                if (Actuator.inrunnerWolfromPlanetaryGearbox.gearRatio() >= self.gearRatioIter and 
                                                    Actuator.inrunnerWolfromPlanetaryGearbox.gearRatio() <= (self.gearRatioIter + 1)):
                                                    self.totalGearboxesWithReqGR += 1
                                                    
                                                    # Cost Calculation
                                                    Actuator.updateFacewidth()

                                                    self.Cost = self.cost(Actuator=Actuator)
                                                    if self.Cost < MinCost:
                                                        MinCost = self.Cost
                                                        self.iter += 1
                                                        opt_done = 1
                                                        # Actuator.genEquationFile()
                                                        if (self.gearRatioReq == 0):
                                                            Actuator.genEquationFile(motor_name=Actuator.motor.motorName, gearRatioLL=round(self.gearRatioIter, 1), gearRatioUL = (round(self.gearRatioIter + self.GEAR_RATIO_STEP,1)))
                                                        else:
                                                            Actuator.genEquationFile_editCADdirectly()

                                                        opt_parameters = [Actuator.inrunnerWolfromPlanetaryGearbox.gearRatio(),
                                                                          Actuator.inrunnerWolfromPlanetaryGearbox.numPlanet,
                                                                          Actuator.inrunnerWolfromPlanetaryGearbox.Ns,
                                                                          Actuator.inrunnerWolfromPlanetaryGearbox.NpBig,
                                                                          Actuator.inrunnerWolfromPlanetaryGearbox.NrBig,
                                                                          Actuator.inrunnerWolfromPlanetaryGearbox.NpSmall,
                                                                          Actuator.inrunnerWolfromPlanetaryGearbox.NrSmall,
                                                                          Actuator.inrunnerWolfromPlanetaryGearbox.moduleBig,
                                                                          Actuator.inrunnerWolfromPlanetaryGearbox.moduleSmall]
                                                        opt_planetaryGearbox = inrunnerWolfromPlanetaryGearbox  (design_parameters         = self.design_parameters,
                                                                                                         gear_standard_parameters  = self.gear_standard_parameters,
                                                                                                         Ns                        = Actuator.inrunnerWolfromPlanetaryGearbox.Ns,
                                                                                                         NpBig                     = Actuator.inrunnerWolfromPlanetaryGearbox.NpBig,
                                                                                                         NpSmall                   = Actuator.inrunnerWolfromPlanetaryGearbox.NpSmall,
                                                                                                         NrBig                     = Actuator.inrunnerWolfromPlanetaryGearbox.NrBig,
                                                                                                         NrSmall                   = Actuator.inrunnerWolfromPlanetaryGearbox.NrSmall,
                                                                                                         numPlanet                 = Actuator.inrunnerWolfromPlanetaryGearbox.numPlanet,
                                                                                                         moduleBig                 = Actuator.inrunnerWolfromPlanetaryGearbox.moduleBig,
                                                                                                         moduleSmall               = Actuator.inrunnerWolfromPlanetaryGearbox.moduleSmall,
                                                                                                         densityGears              = Actuator.inrunnerWolfromPlanetaryGearbox.densityGears,
                                                                                                         densityStructure          = Actuator.inrunnerWolfromPlanetaryGearbox.densityStructure,
                                                                                                         fwSunMM                   = Actuator.inrunnerWolfromPlanetaryGearbox.fwSunMM,
                                                                                                         fwPlanetBigMM             = Actuator.inrunnerWolfromPlanetaryGearbox.fwPlanetBigMM,
                                                                                                         fwPlanetSmallMM           = Actuator.inrunnerWolfromPlanetaryGearbox.fwPlanetSmallMM,
                                                                                                         fwRingBigMM               = Actuator.inrunnerWolfromPlanetaryGearbox.fwRingBigMM,
                                                                                                         fwRingSmallMM             = Actuator.inrunnerWolfromPlanetaryGearbox.fwRingSmallMM,
                                                                                                         maxGearAllowableStressMPa = Actuator.inrunnerWolfromPlanetaryGearbox.maxGearAllowableStressMPa,
                                                                                                         densityAluminum           = Actuator.inrunnerWolfromPlanetaryGearbox.densityAluminum)
                                                        opt_actuator = inrunnerWolfromPlanetaryActuator(design_parameters        = self.design_parameters,
                                                                                                motor                    = Actuator.motor, 
                                                                                                motor_driver_params      = Actuator.motor_driver_params,
                                                                                                inrunnerWolfromPlanetaryGearbox  = opt_planetaryGearbox, 
                                                                                                FOS                      = Actuator.FOS, 
                                                                                                serviceFactor            = Actuator.serviceFactor, 
                                                                                                maxGearboxDiameter       = Actuator.maxGearboxDiameter, # mm 
                                                                                                stressAnalysisMethodName = "MIT") # Lewis or AGMA
                                                        
                                                        opt_actuator.updateFacewidth()
                                                        opt_actuator.getMassKG_3DP()
                                            
                                                        # self.printOptimizationResults(Actuator, log, csv)
                                            Actuator.inrunnerWolfromPlanetaryGearbox.setNumPlanet(Actuator.inrunnerWolfromPlanetaryGearbox.numPlanet + 1)
                                        # Actuator.inrunnerWolfromPlanetaryGearbox.setNrBig(Actuator.inrunnerWolfromPlanetaryGearbox.NrBig + 1)
                                        # Actuator.inrunnerWolfromPlanetaryGearbox.setNrSmall(Actuator.inrunnerWolfromPlanetaryGearbox.NrSmall + 1)
                                    Actuator.inrunnerWolfromPlanetaryGearbox.setNpSmall(Actuator.inrunnerWolfromPlanetaryGearbox.NpSmall + 1)
                                Actuator.inrunnerWolfromPlanetaryGearbox.setNpBig(Actuator.inrunnerWolfromPlanetaryGearbox.NpBig + 1)
                            Actuator.inrunnerWolfromPlanetaryGearbox.setNs(Actuator.inrunnerWolfromPlanetaryGearbox.Ns + 1)
                        Actuator.inrunnerWolfromPlanetaryGearbox.setModuleSmall(Actuator.inrunnerWolfromPlanetaryGearbox.moduleSmall + 0.100)
                        Actuator.inrunnerWolfromPlanetaryGearbox.setModuleSmall(round(Actuator.inrunnerWolfromPlanetaryGearbox.moduleSmall, 1)) # Round Off
                    Actuator.inrunnerWolfromPlanetaryGearbox.setModuleBig(Actuator.inrunnerWolfromPlanetaryGearbox.moduleBig + 0.100)
                    Actuator.inrunnerWolfromPlanetaryGearbox.setModuleBig(round(Actuator.inrunnerWolfromPlanetaryGearbox.moduleBig, 1)) # Round Off
                if (opt_done == 1):
                    self.printOptimizationResults(opt_actuator, log, csv)  
                self.gearRatioIter += self.GEAR_RATIO_STEP
    
                if log:
                    print("Number of iterations: ", self.iter)
                    print("Total Feasible Gearboxes:", self.totalFeasibleGearboxes)
                    print("Total Gearboxes with requires Gear Ratio:", self.totalGearboxesWithReqGR)
                    print("*****************************************************************")
                    print("----------------------------END----------------------------------")
                    print(" ")

        sys.stdout = sys.__stdout__

        return opt_parameters

    def optimizeActuatorWithPSC(self, Actuator = inrunnerWolfromPlanetaryActuator, log=1, csv=0, printOptParams = 1):
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
            fileName = f"./results/results_bilevel_{Actuator.motor.motorName}/WPG_BILEVEL_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}_CSV.csv"
        elif log:
            fileName = f"./results/results_bilevel_{Actuator.motor.motorName}/WPG_BILEVEL_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}_LOG.txt"
        
        with open(fileName, "w") as wolfromLogFile:
            sys.stdout = wolfromLogFile
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
                print("iter, gearRatio, moduleBig, moduleSmall, Ns, NpBig, NpSmall, NrBig, NrSmall, numPlanet,PSCs, PSCp1, PSCp2, PSCr1, PSCr2, fwSunMM, fwPlanetBigMM, fwPanetSmallMM, fwRingBigMM, fwRingSmallMM, CD_SP1, CD_PR1, CD_PR2, mass, eff, peakTorque, Cost, Torque_Density")
            while self.gearRatioIter <= self.GEAR_RATIO_MAX: 
                self.iter = 0
                opt_done = 0
                self.Cost = 100000
                MinCost = self.Cost
                opt_parameters = []
                Actuator.inrunnerWolfromPlanetaryGearbox.setModuleBig(self.MODULE_BIG_MIN)
                while Actuator.inrunnerWolfromPlanetaryGearbox.moduleBig <= self.MODULE_BIG_MAX:
                    # Setting Module Small
                    Actuator.inrunnerWolfromPlanetaryGearbox.setModuleSmall(self.MODULE_SMALL_MIN)
                    while (Actuator.inrunnerWolfromPlanetaryGearbox.moduleSmall <= self.MODULE_SMALL_MAX):
                        # Setting Ns
                        Actuator.inrunnerWolfromPlanetaryGearbox.setNs(self.NUM_TEETH_SUN_MIN)
                        while (2*Actuator.inrunnerWolfromPlanetaryGearbox.getPCRadiusSunM()*1000) <= Actuator.maxGearboxDiameter:
                            # Setting Np Big
                            Actuator.inrunnerWolfromPlanetaryGearbox.setNpBig(self.NUM_TEETH_PLANET_BIG_MIN)
                            while (2*Actuator.inrunnerWolfromPlanetaryGearbox.getPCRadiusPlanetBigM()*1000) <= Actuator.maxGearboxDiameter/2:
                                # Setting Np Small
                                Actuator.inrunnerWolfromPlanetaryGearbox.setNpSmall(self.NUM_TEETH_PLANET_SMALL_MIN)
                                while (2*Actuator.inrunnerWolfromPlanetaryGearbox.getPCRadiusPlanetSmallM()*1000) <= Actuator.maxGearboxDiameter/2:
                                    # Setting Nr Small
                                    Actuator.inrunnerWolfromPlanetaryGearbox.setNrSmall(Actuator.inrunnerWolfromPlanetaryGearbox.NpSmall + 
                                                                                Actuator.inrunnerWolfromPlanetaryGearbox.NpBig +
                                                                                Actuator.inrunnerWolfromPlanetaryGearbox.Ns)
                                    # Setting Nr Big
                                    Actuator.inrunnerWolfromPlanetaryGearbox.setNrBig(2*Actuator.inrunnerWolfromPlanetaryGearbox.NpBig +
                                                                                Actuator.inrunnerWolfromPlanetaryGearbox.Ns)
                                    if ((2*Actuator.inrunnerWolfromPlanetaryGearbox.getPCRadiusRingBigM()*1000) <= Actuator.maxGearboxDiameter and Actuator.getIdRequired2MM() <= 100): # and ((2*Actuator.inrunnerWolfromPlanetaryGearbox.getPCRadiusRingSmallM()*1000) <= maxGearBoxDia):
                                        # TODO: Ask Deepak: What is getIDRequired2MM()? and also tell him to write a more meaningful function name
                                        # Setting number of Planet
                                        Actuator.inrunnerWolfromPlanetaryGearbox.setNumPlanet(self.NUM_PLANET_MIN)
                                        while Actuator.inrunnerWolfromPlanetaryGearbox.numPlanet <= self.NUM_PLANET_MAX:
                                            if (Actuator.inrunnerWolfromPlanetaryGearbox.geometricConstraint() and 
                                                Actuator.inrunnerWolfromPlanetaryGearbox.meshingConstraint() and 
                                                Actuator.inrunnerWolfromPlanetaryGearbox.noPlanetInterferenceConstraint()):
                                                self.totalFeasibleGearboxes += 1
                                                # Fiter for the Gear Ratio
                                                if (Actuator.inrunnerWolfromPlanetaryGearbox.gearRatio() >= self.gearRatioIter and 
                                                    Actuator.inrunnerWolfromPlanetaryGearbox.gearRatio() <= (self.gearRatioIter + 1)):
                                                    
                                                    self.totalGearboxesWithReqGR += 1
                                                    
                                                    # Cost Calculation
                                                    Actuator.updateFacewidth()
                                                    # massActuator = Actuator.getMassStructureKG()
                                                    massActuator = Actuator.getMassKG_3DP()
                                                    effActuator = Actuator.inrunnerWolfromPlanetaryGearbox.getEfficiency()
                                                    self.Cost = (self.K_Mass * massActuator) + (self.K_Eff * effActuator)
                                                    
                                                    if self.Cost < MinCost:
                                                        MinCost = self.Cost
                                                        self.iter += 1
                                                        opt_done = 1
                                                        Actuator.genEquationFile()

                                                        opt_parameters = [Actuator.inrunnerWolfromPlanetaryGearbox.gearRatio(),
                                                                          Actuator.inrunnerWolfromPlanetaryGearbox.numPlanet,
                                                                          Actuator.inrunnerWolfromPlanetaryGearbox.Ns,
                                                                          Actuator.inrunnerWolfromPlanetaryGearbox.NpBig,
                                                                          Actuator.inrunnerWolfromPlanetaryGearbox.NrBig,
                                                                          Actuator.inrunnerWolfromPlanetaryGearbox.NpSmall,
                                                                          Actuator.inrunnerWolfromPlanetaryGearbox.NrSmall,
                                                                          Actuator.inrunnerWolfromPlanetaryGearbox.moduleBig,
                                                                          Actuator.inrunnerWolfromPlanetaryGearbox.moduleSmall]
                                                        opt_planetaryGearbox = inrunnerWolfromPlanetaryGearbox  (design_parameters         = self.design_parameters,
                                                                                                         gear_standard_parameters  = self.gear_standard_parameters,
                                                                                                         Ns                        = Actuator.inrunnerWolfromPlanetaryGearbox.Ns,
                                                                                                         NpBig                     = Actuator.inrunnerWolfromPlanetaryGearbox.NpBig,
                                                                                                         NpSmall                   = Actuator.inrunnerWolfromPlanetaryGearbox.NpSmall,
                                                                                                         NrBig                     = Actuator.inrunnerWolfromPlanetaryGearbox.NrBig,
                                                                                                         NrSmall                   = Actuator.inrunnerWolfromPlanetaryGearbox.NrSmall,
                                                                                                         numPlanet                 = Actuator.inrunnerWolfromPlanetaryGearbox.numPlanet,
                                                                                                         moduleBig                 = Actuator.inrunnerWolfromPlanetaryGearbox.moduleBig,
                                                                                                         moduleSmall               = Actuator.inrunnerWolfromPlanetaryGearbox.moduleSmall,
                                                                                                         densityGears              = Actuator.inrunnerWolfromPlanetaryGearbox.densityGears,
                                                                                                         densityStructure          = Actuator.inrunnerWolfromPlanetaryGearbox.densityStructure,
                                                                                                         fwSunMM                   = Actuator.inrunnerWolfromPlanetaryGearbox.fwSunMM,
                                                                                                         fwPlanetBigMM             = Actuator.inrunnerWolfromPlanetaryGearbox.fwPlanetBigMM,
                                                                                                         fwPlanetSmallMM           = Actuator.inrunnerWolfromPlanetaryGearbox.fwPlanetSmallMM,
                                                                                                         fwRingBigMM               = Actuator.inrunnerWolfromPlanetaryGearbox.fwRingBigMM,
                                                                                                         fwRingSmallMM             = Actuator.inrunnerWolfromPlanetaryGearbox.fwRingSmallMM,
                                                                                                         maxGearAllowableStressMPa = Actuator.inrunnerWolfromPlanetaryGearbox.maxGearAllowableStressMPa,
                                                                                                         densityAluminum           = Actuator.inrunnerWolfromPlanetaryGearbox.densityAluminum)
                                                        opt_actuator = inrunnerWolfromPlanetaryActuator(design_parameters        = self.design_parameters,
                                                                                                motor                    = Actuator.motor, 
                                                                                                inrunnerWolfromPlanetaryGearbox  = opt_planetaryGearbox, 
                                                                                                FOS                      = Actuator.FOS, 
                                                                                                serviceFactor            = Actuator.serviceFactor, 
                                                                                                maxGearboxDiameter       = Actuator.maxGearboxDiameter, # mm 
                                                                                                stressAnalysisMethodName = "Lewis") # Lewis or AGMA
                                            
                                            Actuator.inrunnerWolfromPlanetaryGearbox.setNumPlanet(Actuator.inrunnerWolfromPlanetaryGearbox.numPlanet + 1)
                                        # Actuator.inrunnerWolfromPlanetaryGearbox.setNrBig(Actuator.inrunnerWolfromPlanetaryGearbox.NrBig + 1)
                                        # Actuator.inrunnerWolfromPlanetaryGearbox.setNrSmall(Actuator.inrunnerWolfromPlanetaryGearbox.NrSmall + 1)
                                    Actuator.inrunnerWolfromPlanetaryGearbox.setNpSmall(Actuator.inrunnerWolfromPlanetaryGearbox.NpSmall + 1)
                                Actuator.inrunnerWolfromPlanetaryGearbox.setNpBig(Actuator.inrunnerWolfromPlanetaryGearbox.NpBig + 1)
                            Actuator.inrunnerWolfromPlanetaryGearbox.setNs(Actuator.inrunnerWolfromPlanetaryGearbox.Ns + 1)
                        Actuator.inrunnerWolfromPlanetaryGearbox.setModuleSmall(Actuator.inrunnerWolfromPlanetaryGearbox.moduleSmall + 0.100)
                        Actuator.inrunnerWolfromPlanetaryGearbox.setModuleSmall(round(Actuator.inrunnerWolfromPlanetaryGearbox.moduleSmall, 1)) # Round Off
                    Actuator.inrunnerWolfromPlanetaryGearbox.setModuleBig(Actuator.inrunnerWolfromPlanetaryGearbox.moduleBig + 0.100)
                    Actuator.inrunnerWolfromPlanetaryGearbox.setModuleBig(round(Actuator.inrunnerWolfromPlanetaryGearbox.moduleBig, 1)) # Round Off
                if (opt_done == 1):
                    self.wpgOpt = optimal_continuous_PSC_wpg(GEAR_RATIO_MIN = opt_parameters[0],
                                                             numPlanet      = opt_parameters[1],
                                                             Ns_init        = opt_parameters[2],
                                                             Np1_init       = opt_parameters[3],
                                                             Nr1_init       = opt_parameters[4],
                                                             Np2_init       = opt_parameters[5],
                                                             Nr2_init       = opt_parameters[6],
                                                             M1_init        = opt_parameters[7] * 10,
                                                             M2_init        = opt_parameters[8] * 10)
                    _, calc_centerDistForManufacturing = self.wpgOpt.solve()
                    self.wpgOpt.solve(optimizeForManufacturing=True,
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

        sys.stdout = sys.__stdout__

        return opt_parameters

    def printOptimizationParameters(self, Actuator = inrunnerWolfromPlanetaryActuator, log=1, csv=0):
        # Motor Parameters
        maxMotorAngVelRPM       = Actuator.motor.maxMotorAngVelRPM
        maxMotorAngVelRadPerSec = Actuator.motor.maxMotorAngVelRadPerSec
        maxMotorTorque          = Actuator.motor.maxMotorTorque
        maxMotorPower           = Actuator.motor.maxMotorPower
        motorMass               = Actuator.motor.massKG
        motorDia                = Actuator.motor.motorDiaMM
        motorLength             = Actuator.motor.motorLengthMM
        
        # Planetary Gearbox Parameters
        maxGearAllowableStressMPa = Actuator.inrunnerWolfromPlanetaryGearbox.maxGearAllowableStressMPa
        
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

    def printOptimizationResults(self, Actuator = inrunnerWolfromPlanetaryActuator, log=1, csv=0):
        Actuator.setVariables()
        if log:
            # Printing the parameters below
            print("Iteration: ", self.iter)
            Actuator.printParametersLess()
            Actuator.printVolumeAndMassParameters()
            if self.UsePSCasVariable == 1 :
                Opt_PSC_ring1 = self.wpgOpt.model.PSCr1.value
                Opt_PSC_ring2 = self.wpgOpt.model.PSCr2.value
                Opt_PSC_planet1 = self.wpgOpt.model.PSCp1.value
                Opt_PSC_planet2 = self.wpgOpt.model.PSCp2.value
                Opt_PSC_sun = self.wpgOpt.model.PSCs.value
            else :
                Opt_PSC_ring1   = 0
                Opt_PSC_ring2   = 0
                Opt_PSC_planet1 = 0
                Opt_PSC_planet2 = 0
                Opt_PSC_sun     = 0            
            eff = round(Actuator.planetaryGearbox.getEfficiency(), 3)
            if self.UsePSCasVariable == 1 : 
                eff  = round(self.wpgOpt.getEfficiency(Var=False), 3)
                print ("Efficiency with PSC", eff)
                print(f"PSC Values - Ring: {Opt_PSC_ring1}, Planet: {Opt_PSC_planet1}, Ring2: {Opt_PSC_ring2}, Planet2: {Opt_PSC_planet2}, Sun: {Opt_PSC_sun}")
            print(" ")
            print("Cost:", self.Cost)
            print("*****************************************************************")
            print(" ")
            print("Cost:", self.Cost)
            print("*****************************************************************")
        elif csv:
            iter            = self.iter
            gearRatio       = Actuator.inrunnerWolfromPlanetaryGearbox.gearRatio()
            moduleBig       = Actuator.inrunnerWolfromPlanetaryGearbox.moduleBig
            moduleSmall     = Actuator.inrunnerWolfromPlanetaryGearbox.moduleSmall
            Ns              = Actuator.inrunnerWolfromPlanetaryGearbox.Ns 
            NpBig           = Actuator.inrunnerWolfromPlanetaryGearbox.NpBig
            NpSmall         = Actuator.inrunnerWolfromPlanetaryGearbox.NpSmall 
            NrBig           = Actuator.inrunnerWolfromPlanetaryGearbox.NrBig
            NrSmall         = Actuator.inrunnerWolfromPlanetaryGearbox.NrSmall 
            numPlanet       = Actuator.inrunnerWolfromPlanetaryGearbox.numPlanet
            fwSunMM         = round(Actuator.inrunnerWolfromPlanetaryGearbox.fwSunMM    , 3)
            fwPlanetBigMM   = round(Actuator.inrunnerWolfromPlanetaryGearbox.fwPlanetBigMM , 3)
            fwPlanetSmallMM = round(Actuator.inrunnerWolfromPlanetaryGearbox.fwPlanetSmallMM , 3)
            fwRingBigMM     = round(Actuator.inrunnerWolfromPlanetaryGearbox.fwRingBigMM   , 3)
            fwRingSmallMM   = round(Actuator.inrunnerWolfromPlanetaryGearbox.fwRingSmallMM   , 3)
            if self.UsePSCasVariable == 1 :
                Opt_PSC_ring1   = self.wpgOpt.model.PSCr1.value
                Opt_PSC_ring2   = self.wpgOpt.model.PSCr2.value
                Opt_PSC_planet1 = self.wpgOpt.model.PSCp1.value
                Opt_PSC_planet2 = self.wpgOpt.model.PSCp2.value
                Opt_PSC_sun     = self.wpgOpt.model.PSCs.value
                Opt_CD_SP1, Opt_CD_PR1, Opt_CD_PR2 = self.wpgOpt.getCenterDistance(Var=False)
            else :
                Opt_PSC_ring1   = 0.0
                Opt_PSC_ring2   = 0.0
                Opt_PSC_planet1 = 0.0
                Opt_PSC_planet2 = 0.0
                Opt_PSC_sun     = 0.0
                Opt_CD_SP1 = ((Ns      + NpBig)/2)   * moduleBig
                Opt_CD_PR1 = ((NrBig   - NpBig)/2)   * moduleBig
                Opt_CD_PR2 = ((NrSmall - NpSmall)/2) * moduleSmall

            # mass       = round(Actuator.getMassStructureKG(), 3)
            mass       = round(Actuator.getMassKG_3DP(), 3)
            eff        = round(Actuator.inrunnerWolfromPlanetaryGearbox.getEfficiency(), 3)
            if self.UsePSCasVariable == 1 :
                eff  = round(self.wpgOpt.getEfficiency(Var=False), 3)
            peakTorque      = round(Actuator.motor.getMaxMotorTorque()*Actuator.inrunnerWolfromPlanetaryGearbox.gearRatio(), 3)
            Cost       = Actuator.cost() #self.K_Mass * mass + self.K_Eff * eff
            torque_density  = round(peakTorque/mass, 3)
            Outer_bearing_mass = Actuator.output_bearing_mass
            Actuator_width = Actuator.actuator_width
            print(iter,",", gearRatio,",",moduleBig,",",moduleSmall,",", Ns,",", NpBig,",", NpSmall,",", NrBig,",",NrSmall,",", numPlanet,",", fwSunMM,",", fwPlanetBigMM,",",fwPlanetSmallMM,",", fwRingBigMM,",",fwRingSmallMM,",", mass, ",", eff,",", peakTorque,",", Cost, ",", torque_density, ",", Outer_bearing_mass, ",", Actuator_width)

    def cost(self, Actuator=inrunnerWolfromPlanetaryActuator):
        K_gearRatio = 0
        if self.gearRatioReq != 0:
            K_gearRatio = 1
        
        gearRatio_err = np.sqrt((Actuator.inrunnerWolfromPlanetaryGearbox.gearRatio() - self.gearRatioReq)**2)

        mass = Actuator.getMassKG_3DP()
        eff = Actuator.inrunnerWolfromPlanetaryGearbox.getEfficiency()
        width = Actuator.inrunnerWolfromPlanetaryGearbox.fwPlanetBigMM + Actuator.inrunnerWolfromPlanetaryGearbox.fwPlanetSmallMM
        cost = (self.K_Mass    * mass 
                + self.K_Eff   * eff 
                + self.K_Width * width 
                + K_gearRatio  * gearRatio_err)
        return cost