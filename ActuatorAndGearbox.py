from typing import Any
import numpy as np
import os
import sys
import time
from pyomo.environ import *
from pyomo.opt import SolverFactory
from pyomo.util.infeasible import log_infeasible_constraints
# from sklearn.linear_model import LinearRegression

#-------------------------------------------------------------------------
# class material
#-------------------------------------------------------------------------
class material:
    def __init__(self, density, maxAllowableStressMPa = 400, bhn = 2, youngsModulus = 10):
        self.maxAllowableStressMPa = maxAllowableStressMPa
        self.bhn = bhn
        self.youngsModulus = youngsModulus
        self.density = density

#-------------------------------------------------------------------------
# class bearings
#-------------------------------------------------------------------------
class bearings_discrete:
    def __init__(self,idRequiredMM):
        # Bearing dataset entered according to e1102 in [idMM,odMM,widthMM,massKG] format pg no b10-12
        self.data_bearings = [[25,37,7,0.021],[28,52,12,0.096],[30,42,7,0.024],[32,58,13,0.122],[35,47,7,0.027],[40,52,7,0.031],[45,58,7,0.038],[50,65,7,0.050],[55,72,9,0.081],[60,78,10,0.103],[65,85,10,0.128],[70,90,10,0.134],[75,95,10,0.149],[80,100,10,0.151],[85,110,13,0.263],
                              [90,115,13,0.276],[95,120,13,0.297],[100,125,13,0.31],[105,130,13,0.324],[110,140,16,0.497],[120,150,16,0.537],[130,165,18,0.758],[140,170,18,0.832],[150,190,20,1.15],[160,200,20,1.23]]
        self.idRequiredMM = idRequiredMM
        self.indexBearing =   0
        while (self.data_bearings[self.indexBearing][0] < self.idRequiredMM):
            self.indexBearing +=1
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
        return self.data_bearings[self.indexBearing][0]
    
    def getBearingODMM(self):
        return self.data_bearings[self.indexBearing][1]
    
    def getBearingWidthMM(self):
        return self.data_bearings[self.indexBearing][2]
    
    def getBearingMassKG(self):
        return self.data_bearings[self.indexBearing][3]

    # # Continuous functions
    # def getBearingIDMM(self):
    #     return self.idRequiredMM  # Identity function for d

    # def getBearingODMM(self):
    #     return np.round(self.lr_D.predict(np.array([[self.idRequiredMM]]))[0],3)

    # def getBearingWidthMM(self):
    #     return np.round(self.lr_B.predict(np.array([[self.idRequiredMM]]))[0],2)

    # def getBearingMassKG(self):
    #     return np.round(self.lr_L.predict(np.array([[self.idRequiredMM]]))[0],3)

class bearings_continuous:
    def __init__(self,idRequiredMM):
        # Bearing dataset entered according to e1102 in [idMM,odMM,widthMM,massKG] format pg no b10-12
        self.data_bearings = [[25,37,7,0.021],
                              [28,52,12,0.096],
                              [30,42,7,0.024],
                              [32,58,13,0.122],
                              [35,47,7,0.027],
                              [40,52,7,0.031],
                              [45,58,7,0.038],
                              [50,65,7,0.050],
                              [55,72,9,0.081],
                              [60,78,10,0.103],
                              [65,85,10,0.128],
                              [70,90,10,0.134],
                              [75,95,10,0.149],
                              [80,100,10,0.151],
                              [85,110,13,0.263],
                              [90,115,13,0.276],
                              [95,120,13,0.297],
                              [100,125,13,0.31],
                              [105,130,13,0.324],
                              [110,140,16,0.497],
                              [120,150,16,0.537],
                              [130,165,18,0.758],
                              [140,170,18,0.832],
                              [150,190,20,1.15],
                              [160,200,20,1.23]]
        self.idRequiredMM = idRequiredMM
        self.indexBearing =   0

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

#=========================================================================
# Gearbox classes
#=========================================================================
#-------------------------------------------------------------------------
# Single Layer Planetary Gearbox
#-------------------------------------------------------------------------
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
                 densityCarrier            = 2710.0, 
                 densityStructure          = 2710.0
                 ):
        
        self.Ns        = Ns
        self.Np        = Np
        self.Nr        = Nr
        self.numPlanet = numPlanet
        self.module    = module

        self.maxGearAllowableStressMPa = maxGearAllowableStressMPa # MPa
        self.maxGearAllowableStressPa  = maxGearAllowableStressMPa * 10**6 # Pa
        self.densityGears              = densityGears
        self.densityCarrier            = densityCarrier
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
        self.fwSunM    = fwSunMM / 1000.0
        self.fwRingM   = fwRingMM / 1000.0
        self.fwPlanetM = fwPlanetMM / 1000.0

        # Coefficient of friction and Pressure Angles
        self.mu            = gear_standard_parameters["coefficientOfFriction"]# 0.3 # Coefficient of friction
        self.pressureAngle = gear_standard_parameters["pressureAngleDEG"]# 20  # deg

        self.ringRadialWidthMM   = design_params["ringRadialWidthMM"]          # mm 
        self.ringRadialWidthM    = design_params["ringRadialWidthMM"] / 1000.0 # m
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
        return 2 * (Rs + Rp) * np.sin(np.pi/(2*numPlanet)) - Rp - sCarrierExtrusionRadiusMM >= self.sCarrierExtrusionClearanceMM

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
    
    def getOuterRadiusRingMM(self):
        return ((self.Nr * self.module / 2) + self.ringRadialWidthMM)
    
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
    
    def getOuterRadiusRingM(self):
        return (((self.Nr * self.module / 2)/1000.0) + self.ringRadialWidthM)

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

#=========================================================================
# Motor class
#=========================================================================
class motor:
    def __init__(self, 
                 maxMotorAngVelRPM = 1190, # RPM
                 maxMotorTorque    = 8.83, # Nm
                 maxMotorPower     = 8.83 * 1190 * 2*np.pi/60, # W 
                 motorMass         = 0.778, # KG
                 motorDia          = 106.8, # mm
                 motorLength       = 47.6,  # mm
                 motorStatorID     = 70,    # mm
                 motorStatorOD     = 95,    # mm
                 motorStatorHeight = 45.6,  # mm
                 motorName         = "U12"):
        
        self.motorName               = motorName
        self.maxMotorAngVelRPM       = maxMotorAngVelRPM
        self.maxMotorAngVelRadPerSec = maxMotorAngVelRPM * (2 * np.pi / 60)
        self.maxMotorTorque          = maxMotorTorque
        self.maxMotorPower           = maxMotorPower
        self.massKG                  = motorMass # kg
        self.motorDiaMM              = motorDia # mm #TODO: make use of this parameter
        self.motorStatorIDMM         = motorStatorID
        self.motorLengthMM           = motorLength # mm #TODO: make use of this parameter
        self.motorStatorODMM         = motorStatorOD
        self.motorStatorHeightMM     = motorStatorHeight
        self.motorRotorWidthMM       = 2 # mm

    # Maximum motor angular velocity in rad/s
    def getMaxMotorAngVelRadPerSec(self):
        return self.maxMotorAngVelRadPerSec
    
    # Maximum motor power in W
    def getMaxMotorPower(self):
        return self.maxMotorPower
    
    # Maximum motor torque in Nm
    def getMaxMotorTorque(self):
        return self.maxMotorTorque
    
    # Mass of the motor in kg
    def getMassKG(self):
        return self.massKG
    
    #dimension of the motor in MM
    def getDiaMM(self):
        return self.motorDiaMM
    
    def getLengthMM(self):
        return self.motorLengthMM
    
    #dimensions of Stator
    def getStatorIDMM(self):
        return self.motorStatorIDMM
    
    def getStatorODMM(self):
        return self.motorStatorODMM
    
    def getStatorHeight(self):
        return self.motorStatorHeightMM
    
    # Print the motor parameters
    def printParameters(self):
        print("Maximum motor angular velocity = ", self.maxMotorAngVelRPM, " RPM")
        print("Maximum motor power = ", self.maxMotorPower, " W")
        print("Maximum motor torque = ", self.maxMotorTorque, " Nm")
        print("Maximum motor angular velocity = ", self.maxMotorAngVelRadPerSec, " rad/s")
        print("Mass of the motor = ", self.massKG, " kg")
        print ('Diameter of the motor = ', self.motorDiaMM, ' mm')
        print( " Length of the motor = ", self.motorLengthMM, ' mm')
        if (self.motorStatorIDMM != 0 and self.motorStatorODMM != 0 and self.motorStatorHeightMM !=0):
            print (' Inner Diameter of Stator = ', self.motorStatorIDMM, ' mm')
            print (' Outer Diameter of Stator = ', self.motorStatorODMM, ' mm')
            print (' Height of Stator = ', self.motorStatorIDMM, ' mm')

#=========================================================================
# Actuator classes
#=========================================================================
#-------------------------------------------------------------------------
# Single Stage Actuator class
#-------------------------------------------------------------------------
class singleStagePlanetaryActuator:
    def __init__(self, 
                 design_params,
                 motor                    = motor, 
                 planetaryGearbox         = singleStagePlanetaryGearbox, 
                 FOS                      = 2.0, 
                 serviceFactor            = 2.0, 
                 maxGearboxDiameter       = 140.0,
                 stressAnalysisMethodName = "Lewis"):
        
        self.motor              = motor
        self.planetaryGearbox   = planetaryGearbox
        self.FOS                = FOS
        self.serviceFactor      = serviceFactor
        self.maxGearboxDiameter = maxGearboxDiameter # TODO: convert it to 
                                                     # outer diameter of 
                                                     # the motor
        self.stressAnalysisMethodName = stressAnalysisMethodName

        #============================================
        # Motor Parameters
        #============================================
        self.motorLengthMM           = self.motor.getLengthMM()
        self.motorDiaMM              = self.motor.getDiaMM()
        self.motorMassKG             = self.motor.getMassKG()
        self.MaxMotorTorque          = self.motor.maxMotorTorque          # Nm
        self.MaxMotorAngVelRPM       = self.motor.maxMotorAngVelRPM       # RPM
        self.MaxMotorAngVelRadPerSec = self.motor.maxMotorAngVelRadPerSec # radians/sec
        self.MotorInnerDiaMM         = self.motor.motorStatorIDMM         # mm 
        self.motorRotorWidthMM       = self.motor.motorRotorWidthMM

        #============================================
        # Actuator Design Parameters
        #============================================
        #--------------------------------------------
        # Independent parameters
        #--------------------------------------------
        self.ringRadialWidthMM = self.planetaryGearbox.ringRadialWidthMM

        self.carrier1ShaftHeightMM       = design_params["carrier1ShaftHeightMM"]         # 10
        self.mainCase2AttachmentHeightMM = design_params["mainCase2AttachmentHeightMM"]   # 6

        self.baseThicknessMM              = design_params["baseThicknessMM"]              # 3
        self.sCarrierThicknessMM          = design_params["sCarrierThicknessMM"]          # 5 # secondary carrier 
        self.mainCoverThicknessMM         = design_params["mainCoverThicknessMM"]         # 2
        self.planetBoreMM                 = design_params["planetBoreMM"]                 # 8
        self.sunBoreMM                    = design_params["sunBoreMM"]                    # 6
        self.couplerRadiusMM              = design_params["couplerRadiusMM"]              # 16.5
        self.couplerThicknessMM           = design_params["couplerThicknessMM"]           # 3
        self.couplerShaftHeightMM         = design_params["couplerShaftHeightMM"]         # 12
        self.sCarrierExtrusionDiaMM       = design_params["sCarrierExtrusionDiaMM"]       # 8 # 12
        self.sCarrierExtrusionClearanceMM = design_params["sCarrierExtrusionClearanceMM"] # 1 # clearance between the extrusion and the planets
        self.clearanceMotorandCaseMM      = design_params["clearanceMotorandCaseMM"]      # 2.3
        self.clearanceRingandCaseMM       = design_params["clearanceRingandCaseMM"]       # 1.5
        self.clearance1RingandCaseMM      = design_params["clearance1RingandCaseMM"]      # 1.5 # additional clearance
        self.clearanceCarrierPlanetMM     = design_params["clearanceCarrierPlanetMM"]     # 1.5
        self.upperHousingHeight           = design_params["upperHousingHeight"]           # 5
        self.clearanceSCarrierMotorMM     = design_params["clearanceSCarrierMotorMM"]     # 2
        self.carrierIDClearanceMM         = design_params["carrierIDClearanceMM"]         # 2
        self.sCarrierIDClearanceMM        = design_params["sCarrierIDClearanceMM"]        # 2
        self.bearingIDClearanceMM         = design_params["bearingIDClearanceMM"]         # 10
        
        self.smallBearingMassKG = design_params["smallBearingMassKG"] # 0.015
        self.smallBearingODMM   = design_params["smallBearingODMM"]   # 19
        self.smallBearingWidth  = design_params["smallBearingWidth"]  # 5

        #-----------------------------------------------------
        # Dependent parameters
        #-----------------------------------------------------
        # Initializing here with None values
        # Will be updated in Mass calculation function
        #-----------------------------------------------------
        self.carrierInnerDiameterMM  : float | None = None 
        self.sCarrierInnerDiameterMM : float | None = None 

        self.InnerDiaBearingMM : float | None = None
        self.OuterDiaBearingMM : float | None = None
        self.WidthBearingMM    : float | None = None
        
        self.LengthMainCoverMM                 : float | None = None
        self.CarrierThicknessMM                : float | None = None
        self.MainCoverInnerRadiusMM            : float | None = None
        self.MainCoverOuterRadiusMM            : float | None = None
        self.MainCoverProtrusion1RadiusMM      : float | None = None
        self.HeightMainCoverProtrusion1MM      : float | None = None
        self.RadiusBaseMM                      : float | None = None
        self.RadiusCouplerShaftMM              : float | None = None
        self.CarrierOuterDiameterMM            : float | None = None
        self.CarrierExtrusionDiameterMM        : float | None = None
        self.CarrierExtrusionHeightMM          : float | None = None
        self.SecondaryCarrierExtrusionHeightMM : float | None = None
        self.SecondaryCarrierOuterDiameterMM   : float | None = None

        ##  3D printed actuator mass functions
        self.Motor_case_mass               : float | None = None
        self.gearbox_casing_mass           : float | None = None
        self.carrier_mass                  : float | None = None
        self.sun_mass                      : float | None = None
        self.sec_carrier_mass              : float | None = None
        self.planet_mass                   : float | None = None
        self.planet_bearing_combined_mass  : float | None = None
        self.sun_shaft_bearing_mass        : float | None = None
        self.bearing_mass                  : float | None = None
        self.bearing_retainer_mass         : float | None = None

    #-------------------------------------------------------------------------
    # Mass Calculation
    #-------------------------------------------------------------------------
    def getMassKG_new(self):
        module    = self.planetaryGearbox.module
        Ns        = self.planetaryGearbox.Ns
        Np        = self.planetaryGearbox.Np
        Nr        = self.planetaryGearbox.Nr
        numPlanet = self.planetaryGearbox.numPlanet

        #------------------------------------
        # density of materials
        #------------------------------------
        densityGears = 7850
        densityAl    = 2710

        #------------------------------------
        # Face Width
        #------------------------------------
        sunFwMM     = self.planetaryGearbox.fwSunMM
        planetFwMM  = self.planetaryGearbox.fwPlanetMM
        ringFwMM    = self.planetaryGearbox.fwRingMM

        sunFwM    = sunFwMM    * 0.001
        planetFwM = planetFwMM * 0.001
        ringFwM   = ringFwMM   * 0.001

        #------------------------------------
        # Diameter and Radius
        #------------------------------------
        DiaSunMM          = Ns * module
        DiaPlanetMM       = Np * module
        DiaRingMM         = Nr * module

        RadiusSunMM       = DiaSunMM    * 0.5
        RadiusPlanetMM    = DiaPlanetMM * 0.5
        RadiusRingMM      = DiaRingMM   * 0.5

        RingOuterRadiusMM = RadiusRingMM + self.ringRadialWidthMM

        #------------------------------------
        # Carrier Inner Diameters
        #------------------------------------
        carrierInnerDiameterMM         = (RadiusPlanetMM + RadiusSunMM - self.planetBoreMM/2)*2           - self.carrierIDClearanceMM             
        sCarrierInnerDiameterMM        = (RadiusPlanetMM + RadiusSunMM - self.sCarrierExtrusionDiaMM/2)*2 - self.sCarrierIDClearanceMM  
        clearanceSCarrierMotorMM_plus_couplerThicknessMM  = self.clearanceSCarrierMotorMM + self.couplerThicknessMM

        #------------------------------------
        # Bearing Selection
        #------------------------------------
        IdrequiredMM      = module * (Ns + Np) + self.bearingIDClearanceMM
        Bearings          = bearings_continuous(IdrequiredMM)
        InnerDiaBearingMM = Bearings.getBearingIDMM()
        OuterDiaBearingMM = Bearings.getBearingODMM()
        WidthBearingMM    = Bearings.getBearingWidthMM()
        BearingMassKG     = Bearings.getBearingMassKG() 

        # ClearanceCarrierMotorMM = self.clearanceSCarrierMotorMM
        ClearanceCarrierMotorMM = clearanceSCarrierMotorMM_plus_couplerThicknessMM

        #====================================
        # Dimensions of design
        #====================================
        #------------------------------------
        # Main Cover Dimensions
        #------------------------------------
        MainCoverInnerRadiusMM = self.motorDiaMM * 0.5 + self.clearanceMotorandCaseMM
        MainCoverOuterRadiusMM = MainCoverInnerRadiusMM + self.mainCoverThicknessMM
        LengthMainCoverMM      = (self.motorLengthMM + 
                                  ringFwMM + 
                                  self.baseThicknessMM + 
                                  WidthBearingMM + 
                                  self.sCarrierThicknessMM + 
                                  self.clearanceCarrierPlanetMM * 2 + 
                                  clearanceSCarrierMotorMM_plus_couplerThicknessMM)

        MainCoverProtrusion1RadiusMM = OuterDiaBearingMM * 0.5
        HeightMainCoverProtrusion1MM = WidthBearingMM
        MainCoverProtrusion2RadiusMM = RadiusRingMM + self.ringRadialWidthMM
        HeightMainCoverProtrusion2MM = ringFwMM + self.clearanceCarrierPlanetMM

        #------------------------------------
        # Base, Couple and Carrier Dimensions
        #------------------------------------
        RadiusBaseMM                      = MainCoverInnerRadiusMM
        RadiusCouplerShaftMM              = self.sunBoreMM * 0.5
        CarrierOuterDiameterMM            = InnerDiaBearingMM
        CarrierThicknessMM                = WidthBearingMM
        CarrierExtrusionDiameterMM        = self.planetBoreMM
        CarrierExtrusionHeightMM          = planetFwMM + self.clearanceCarrierPlanetMM * 2
        SecondaryCarrierExtrusionHeightMM = CarrierExtrusionHeightMM
        SecondaryCarrierOuterDiameterMM   = CarrierOuterDiameterMM
        
        #------------------------------------
        # Upper Housing Dimensions
        #------------------------------------
        UpperHousingRadiusMM = RingOuterRadiusMM + self.mainCoverThicknessMM

        #====================================
        # Volume Calculation
        #====================================
        #------------------------------------
        # Gears Volume
        #------------------------------------
        SunVolumeM    = np.pi * sunFwMM * ((RadiusSunMM**2) - (self.sunBoreMM * 0.5)**2) * 10**-9
        PlanetVolumeM = np.pi * planetFwMM * ((RadiusPlanetMM**2) - (self.planetBoreMM * 0.5)**2) * 10**-9
        RingVolumeM   = np.pi * ringFwMM * (RingOuterRadiusMM**2 - RadiusRingMM**2) * 10**-9
        
        #------------------------------------
        # Carrier Volume
        #------------------------------------
        CarrierVolumeM           = (np.pi * CarrierThicknessMM * ((CarrierOuterDiameterMM * 0.5)**2 - (carrierInnerDiameterMM * 0.5)**2) +
                                    np.pi * CarrierExtrusionHeightMM * (CarrierExtrusionDiameterMM * 0.5)**2 *  numPlanet) * 10**-9
        SecondaryCarrierVolumeM  = (np.pi * self.sCarrierThicknessMM * ((SecondaryCarrierOuterDiameterMM * 0.5)**2 - (sCarrierInnerDiameterMM * 0.5)**2) +
                                    np.pi * SecondaryCarrierExtrusionHeightMM * (self.sCarrierExtrusionDiaMM * 0.5)**2 *  numPlanet) * 10**-9
        
        #------------------------------------
        # Base Volume and Main Case Volume
        #------------------------------------
        BaseVolumeM              = np.pi * self.baseThicknessMM * RadiusBaseMM**2 * 10**-9
        MainCaseShellVolumeM     = np.pi * (MainCoverOuterRadiusMM**2 - MainCoverInnerRadiusMM**2) * (LengthMainCoverMM - HeightMainCoverProtrusion1MM - HeightMainCoverProtrusion2MM) * 10**-9
        MainCaseHousingVolumeM   = (np.pi * ((UpperHousingRadiusMM)**2 - MainCoverProtrusion1RadiusMM**2) * HeightMainCoverProtrusion1MM +
                                    np.pi * ((UpperHousingRadiusMM)**2 - MainCoverProtrusion2RadiusMM**2) * HeightMainCoverProtrusion2MM) * 10**-9
        MainCaseRemainingVolumeM = np.pi * ((MainCoverOuterRadiusMM)**2 - (UpperHousingRadiusMM)**2) * self.upperHousingHeight * 10**-9
        MainCaseVolumeM          = MainCaseShellVolumeM + MainCaseHousingVolumeM + MainCaseRemainingVolumeM
        
        #------------------------------------
        # Coupler Volume
        #------------------------------------
        CouplerVolumeM  = np.pi * (self.couplerRadiusMM**2 * self.couplerThicknessMM + RadiusCouplerShaftMM**2 * self.couplerShaftHeightMM) * 10**-9

        #====================================
        # Mass Calculation
        #====================================
        MassOfGears     = (SunVolumeM + (PlanetVolumeM * numPlanet) + RingVolumeM) * densityGears
        MassOfAlParts   = ((CarrierVolumeM + SecondaryCarrierVolumeM + BaseVolumeM + MainCaseVolumeM + CouplerVolumeM) * densityAl)

        MassStructureKG = (MassOfGears + MassOfAlParts + BearingMassKG + self.motorMassKG)

        #------------------------------------
        # Mass without casing
        #------------------------------------
        MassStructureWithoutCasingKG = (MassOfGears + 
                                        (CarrierVolumeM + SecondaryCarrierVolumeM) * densityAl + 
                                        BearingMassKG)
        
        #------------------------------------------------
        # Updating the design dependent parameters 
        #------------------------------------------------
        self.carrierInnerDiameterMM  = carrierInnerDiameterMM
        self.sCarrierInnerDiameterMM = sCarrierInnerDiameterMM

        self.InnerDiaBearingMM = InnerDiaBearingMM
        self.OuterDiaBearingMM = OuterDiaBearingMM
        self.WidthBearingMM    = WidthBearingMM  

        self.LengthMainCoverMM                 = LengthMainCoverMM                 
        self.CarrierThicknessMM                = CarrierThicknessMM                
        self.MainCoverInnerRadiusMM            = MainCoverInnerRadiusMM            
        self.MainCoverOuterRadiusMM            = MainCoverOuterRadiusMM            
        self.MainCoverProtrusion1RadiusMM      = MainCoverProtrusion1RadiusMM      
        self.HeightMainCoverProtrusion1MM      = HeightMainCoverProtrusion1MM      
        self.RadiusBaseMM                      = RadiusBaseMM                      
        self.RadiusCouplerShaftMM              = RadiusCouplerShaftMM              
        self.CarrierOuterDiameterMM            = CarrierOuterDiameterMM            
        self.CarrierExtrusionDiameterMM        = CarrierExtrusionDiameterMM        
        self.CarrierExtrusionHeightMM          = CarrierExtrusionHeightMM          
        self.SecondaryCarrierExtrusionHeightMM = SecondaryCarrierExtrusionHeightMM 
        self.SecondaryCarrierOuterDiameterMM   = SecondaryCarrierOuterDiameterMM   

        return MassStructureKG

    #---------------------------------------------
    # Generate Equation file for template CAD model
    #---------------------------------------------
    def genEquationFile_old(self):
        # Writing values into text file imported which is imported into SolidWorks
        file_path = os.path.join(os.path.dirname(__file__), 'template_CAD_designs', 'single_stage_GB', 'equations_single_stage.txt')
        with open(file_path, 'w') as eqFile:
            l = [
                '"sun_width"= ' + str(self.planetaryGearbox.fwSunMM) + 'mm\n',
                '"planet_width"= ' + str(self.planetaryGearbox.fwPlanetMM) + 'mm\n',
                '"ring_width"= ' + str(self.planetaryGearbox.fwRingMM) + 'mm\n',
                '"motor_radius" = ' + str(self.motorDiaMM * 0.5) + 'mm\n',
                '"motor_height" = ' + str(self.motorLengthMM) + 'mm\n',
                '"gear_module" = ' + str(self.planetaryGearbox.module) + 'mm\n',
                '"Sun_teeth" = ' + str(self.planetaryGearbox.Ns) + 'mm\n',
                '"Planet_teeth" = ' + str(self.planetaryGearbox.Np) + 'mm\n',
                '"Ring_teeth" = ' + str(self.planetaryGearbox.Nr) + 'mm\n',
                '"Inner_diameter" = ' + str(self.getInnerDiaBearingMM()) + 'mm\n',
                '"Outer_diameter" = ' + str(self.getOuterDiaBearingMM()) + 'mm\n',
                '"Width_bearing" = ' + str(self.getWidthBearingMM()) + 'mm\n',
                '"Base_thickness" = ' + str(self.baseThicknessMM) + 'mm\n',
                '"secondary_carrier_thickness" = ' + str(self.sCarrierThicknessMM) + 'mm\n',
                '"main_cover_thickness" = ' + str(self.mainCoverThicknessMM) + 'mm\n',
                '"planet_bore" = ' + str(self.planetBoreMM) + 'mm\n',
                '"sun_bore" = ' + str(self.sunBoreMM) + 'mm\n',
                '"coupler_radius" = ' + str(self.couplerRadiusMM) + 'mm\n',
                '"coupler_thickness" = ' + str(self.couplerThicknessMM) + 'mm\n',
                '"coupler_shaft_height" = ' + str(self.couplerShaftHeightMM) + 'mm\n',
                '"carrier_inner_diameter" = ' + str(self.carrierInnerDiameterMM) + 'mm\n',
                '"secondary_carrier_inner_diameter" = ' + str(self.sCarrierInnerDiameterMM) + 'mm\n',
                '"secondary_carrier_extrusion_diameter" = ' + str(self.sCarrierExtrusionDiaMM) + 'mm\n',
                '"length_main_cover" = ' + str(self.getLengthMainCoverMM()) + 'mm\n',
                '"carrier_thickness" = ' + str(self.getCarrierThicknessMM()) + 'mm\n',
                '"main_cover_inner_radius" = ' + str(self.getMainCoverInnerRadiusMM()) + 'mm\n',
                '"main_cover_outer_radius" = ' + str(self.getMainCoverOuterRadiusMM()) + 'mm\n',
                '"main_cover_protrusion_radius" = ' + str(self.getMainCoverProtrusion1RadiusMM()) + 'mm\n',
                '"height_main_cover_protrusion" = ' + str(self.getHeightMainCoverProtrusion1MM()) + 'mm\n',
                '"radius_base" = ' + str(self.getRadiusBaseMM()) + 'mm\n',
                '"radius_coupler_shaft" = ' + str(self.getRadiusCouplerShaftMM()) + 'mm\n',
                '"carrier_outer_diameter" = ' + str(self.getCarrierOuterDiameterMM()) + 'mm\n',
                '"carrier_extrusion_diameter" = ' + str(self.getCarrierExtrusionDiameterMM()) + 'mm\n',
                '"carrier_extrusion_height" = ' + str(self.getCarrierExtrusionHeightMM()) + 'mm\n',
                '"secondary_carrier_extrusion_height" = ' + str(self.getSecondaryCarrierExtrusionHeightMM()) + 'mm\n',
                '"secondary_carrier_outer_diameter" = ' + str(self.getSecondaryCarrierOuterDiameterMM()) + 'mm\n',
                '"UpperHousingHeight" = ' + str(self.upperHousingHeight) + 'mm\n'
            ]
            eqFile.writelines(l)
    
    def genEquationFile(self):
        # Writing values into text file imported which is imported into SolidWorks
        file_path = os.path.join(os.path.dirname(__file__), 'template_CAD_designs', 'single_stage_GB', 'equations_single_stage.txt')
        with open(file_path, 'w') as eqFile:
            l = [
                '"sun_width"= ' + str(self.planetaryGearbox.fwSunMM) + 'mm\n',
                '"planet_width"= ' + str(self.planetaryGearbox.fwPlanetMM) + 'mm\n',
                '"ring_width"= ' + str(self.planetaryGearbox.fwRingMM) + 'mm\n',
                '"motor_radius" = ' + str(self.motorDiaMM * 0.5) + 'mm\n',
                '"motor_height" = ' + str(self.motorLengthMM) + 'mm\n',
                '"gear_module" = ' + str(self.planetaryGearbox.module) + 'mm\n',
                '"Sun_teeth" = ' + str(self.planetaryGearbox.Ns) + 'mm\n',
                '"Planet_teeth" = ' + str(self.planetaryGearbox.Np) + 'mm\n',
                '"Ring_teeth" = ' + str(self.planetaryGearbox.Nr) + 'mm\n',
                '"Inner_diameter" = ' + str(self.InnerDiaBearingMM) + 'mm\n',
                '"Outer_diameter" = ' + str(self.OuterDiaBearingMM) + 'mm\n',
                '"Width_bearing" = ' + str(self.WidthBearingMM) + 'mm\n',
                '"Base_thickness" = ' + str(self.baseThicknessMM) + 'mm\n',
                '"secondary_carrier_thickness" = ' + str(self.sCarrierThicknessMM) + 'mm\n',
                '"main_cover_thickness" = ' + str(self.mainCoverThicknessMM) + 'mm\n',
                '"planet_bore" = ' + str(self.planetBoreMM) + 'mm\n',
                '"sun_bore" = ' + str(self.sunBoreMM) + 'mm\n',
                '"coupler_radius" = ' + str(self.couplerRadiusMM) + 'mm\n',
                '"coupler_thickness" = ' + str(self.couplerThicknessMM) + 'mm\n',
                '"coupler_shaft_height" = ' + str(self.couplerShaftHeightMM) + 'mm\n',
                '"carrier_inner_diameter" = ' + str(self.carrierInnerDiameterMM) + 'mm\n',
                '"secondary_carrier_inner_diameter" = ' + str(self.sCarrierInnerDiameterMM) + 'mm\n',
                '"secondary_carrier_extrusion_diameter" = ' + str(self.sCarrierExtrusionDiaMM) + 'mm\n',
                '"length_main_cover" = ' + str(self.LengthMainCoverMM) + 'mm\n',
                '"carrier_thickness" = ' + str(self.CarrierThicknessMM) + 'mm\n',
                '"main_cover_inner_radius" = ' + str(self.MainCoverInnerRadiusMM) + 'mm\n',
                '"main_cover_outer_radius" = ' + str(self.MainCoverOuterRadiusMM) + 'mm\n',
                '"main_cover_protrusion_radius" = ' + str(self.MainCoverProtrusion1RadiusMM) + 'mm\n',
                '"height_main_cover_protrusion" = ' + str(self.HeightMainCoverProtrusion1MM) + 'mm\n',
                '"radius_base" = ' + str(self.RadiusBaseMM) + 'mm\n',
                '"radius_coupler_shaft" = ' + str(self.RadiusCouplerShaftMM) + 'mm\n',
                '"carrier_outer_diameter" = ' + str(self.CarrierOuterDiameterMM) + 'mm\n',
                '"carrier_extrusion_diameter" = ' + str(self.CarrierExtrusionDiameterMM) + 'mm\n',
                '"carrier_extrusion_height" = ' + str(self.CarrierExtrusionHeightMM) + 'mm\n',
                '"secondary_carrier_extrusion_height" = ' + str(self.SecondaryCarrierExtrusionHeightMM) + 'mm\n',
                '"secondary_carrier_outer_diameter" = ' + str(self.SecondaryCarrierOuterDiameterMM) + 'mm\n',
                '"UpperHousingHeight" = ' + str(self.upperHousingHeight) + 'mm\n'
            ]
            eqFile.writelines(l)

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

        # Ft = (self.serviceFactor*self.motor.getMaxMotorTorque())/( numPlanet * Rs_Mt)
        
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

        # Wear Resistance
        f_sp = self.getErrInAction(V_sp) # mm
        #print("V_sp:",V_sp)
        # TODO: Remove this: error in action should be between 0.0125 and 0.1 mm
        if f_sp < 0.0125:
            f_sp = 0.0125
        elif f_sp > 0.1:
            f_sp = 0.1
        
        C_sp = self.getDynamicLoadFactorC(f_sp)*1000 # N/m 
        d1 = 2*self.planetaryGearbox.getPCRadiusSunM()
        Q = (2*self.planetaryGearbox.Np) / (self.planetaryGearbox.Ns + self.planetaryGearbox.Np)
        K = (10**6)*((1.43*((self.planetaryGearbox.enduranceStressSunMPa)**2)*np.sin(self.planetaryGearbox.pressureAngle*(np.pi/180))) / (self.planetaryGearbox.equivYoungsModulusSP))
        FOS_wear = 1
        Kw = d1*Q*K
        Pw = Kw / C_sp
        Qw = 21*V_sp*((Kw / C_sp) - FOS_wear)
        Rw = -1*((Kw / C_sp) + FOS_wear)
        Sw = -1*((Kw / C_sp) + FOS_wear)*(Ft + 21*V_sp)
        x_star_w = self.solveCubicEquation(Pw, Qw, Rw, Sw)
        bMin_wear = ((x_star_w)**2 - Ft)/C_sp

        # Endurance Resistance
        FOS_en = 1.25
        Ken = self.planetaryGearbox.enduranceStressSunMPa * np.pi * ySun * self.planetaryGearbox.module * 1000
        Pen = Ken / C_sp
        Qen = 21*V_sp*((Ken / C_sp) - FOS_en)
        Ren = -1*((Ken / C_sp) + FOS_en)
        Sen = -1*((Ken / C_sp) + FOS_en)*(Ft + 21*V_sp)
        x_star_en = self.solveCubicEquation(Pen, Qen, Ren, Sen)
        bMin_en = ((x_star_en)**2 - Ft)/C_sp

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

        # ySun    = 0.154 - 0.912 / Ns
        # yPlanet = 0.154 - 0.912 / Np
        # yRing   = 0.154 - 0.912 / Nr

        # V_sp = ( wSun * Rs_Mt )
        # V_rp = ( wCarrier*(Rs_Mt + Rp_Mt) + (wPlanet * Rp_Mt) )
        
        # if V_sp <= 7.5:
        #     Kv_sun = 3/(3+V_sp)
        # elif V_sp > 7.5 and V_sp <= 12.5:
        #     Kv_sun = 4.5/(4.5 + V_sp)

        # if V_rp <= 7.5:
        #     Kv_planet = 3/(3+V_rp)
        # elif V_rp > 7.5 and V_rp <= 12.5:
        #     Kv_planet = 4.5/(4.5 + V_rp)

        # Kv_ring = Kv_planet

        # P = np.pi*module*0.001 # m
        
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

        bMin_sun_mitMM    = bMin_sun_mit    * 1000
        bMin_planet_mitMM = bMin_planet_mit * 1000
        bMin_ring_mitMM   = bMin_ring_mit   * 1000

        self.planetaryGearbox.setfwSunMM    ( bMin_sun_mit    * 1000)
        self.planetaryGearbox.setfwPlanetMM ( bMin_planet_mit * 1000)
        self.planetaryGearbox.setfwRingMM   ( bMin_ring_mit   * 1000)

        # bMin_sun_lewisMM, bMin_planet_lewisMM, bMin_ring_lewisMM = self.lewisStressAnalysisMinFacewidth()

        return bMin_sun_mitMM, bMin_planet_mitMM, bMin_ring_mitMM

    def dynamicLoadSun(self):
        Ft = (self.serviceFactor*self.motor.getMaxMotorTorque()*1000)/(self.planetaryGearbox.numPlanet*self.planetaryGearbox.module*self.planetaryGearbox.Ns)
        V = self.planetaryGearbox.getPCRadiusSunM()*self.motor.getMaxMotorAngVelRadPerSec()
        f = self.getErrInAction(V) # mm

        # TODO: Remove this: error in action should be between 0.0125 and 0.1 mm
        if f < 0.0125:
            f = 0.0125
        elif f > 0.1:
            f = 0.1

        C = self.getDynamicLoadFactorC(f)*1000 # N/m 
        b = self.planetaryGearbox.fwSunM # m
        Fi = 21*V*(Ft + b*C) / (21*V + np.sqrt((Ft + b*C)))
        Fd = Ft + Fi
        #print("Tangential velocity of sun gear = ", V, " m/s")
        #print("Error in action = ", f, " mm")
        #print("Dynamic load factor = ", C, " N/m")
        #print("Tangential load on sun gear = ", Ft, " N")
        #print("Instantaeneous load on sun gear = ", Fi, " N")
        #print("Dynamic load on sun gear = ", Fd, " N")
        return Fd
    
    def getErrInAction(self, V):
        #SOURCE: Fig 4.4, T.Krishna Rao, Design of Machine Elements-II, Vol-2-I, 2019, p. 200
        # Approximated as a hypebola
        return 0.00064344 + (0.514643889/(V+2.340794435)) # mm

    def getDynamicLoadFactorC(self, f, pinionMaterial="Steel", gearMaterial="Steel", toothForm = "20 deg Full Depth"):
        # SOURCE: Table 4.3, T.Krishna Rao, Design of Machine Elements-II, Vol-2-I, 2019, p. 201
        #TODO: Simplify the code using the linear model given in the above book @ p. 194
        C_ci_ci_14_5 = [69.85, 139.70, 279.40, 419.10, 558.80]
        C_st_ci_14_5 = [96.04, 192.08, 384.16, 576.34, 768.32]
        C_st_st_14_5 = [139.70, 279.48, 558.80, 838.20, 1117.60]    
        
        C_ci_ci_20_FD = [72.5, 145.0, 290.0, 435.0, 580.0]
        C_st_ci_20_FD = [99.57, 192.14, 398.28, 597.42, 796.56]
        C_st_st_20_FD = [145.0, 290.0, 580.0, 870.0, 1116.0]
        
        C_ci_ci_20_stub = [75.05, 150.10, 300.20, 450.30, 600.40]
        C_st_ci_20_stub = [103.01, 206.02, 412.04, 618.06, 824.08]
        C_st_st_20_stub = [150.10, 300.20, 600.40, 900.60, 1200.80]
        
        if (toothForm == "14.5 deg"):
            if (pinionMaterial == "Cast iron" and gearMaterial == "Cast iron"):
                if f >= 0.0125 and f <= 0.025:
                    return ((C_ci_ci_14_5[1]-C_ci_ci_14_5[0])/(0.0125))*(f-0.0125) + C_ci_ci_14_5[0]
                elif f > 0.025 and f <= 0.05:
                    return ((C_ci_ci_14_5[2]-C_ci_ci_14_5[1])/(0.025))*(f-0.025) + C_ci_ci_14_5[1]
                elif f > 0.05 and f <= 0.075:
                    return ((C_ci_ci_14_5[3]-C_ci_ci_14_5[2])/(0.025))*(f-0.05) + C_ci_ci_14_5[2]
                elif f > 0.075 and f <= 0.1:
                    return ((C_ci_ci_14_5[4]-C_ci_ci_14_5[3])/(0.025))*(f-0.075) + C_ci_ci_14_5[3]
                else:
                    print("Invalid value of f")
                    return -1
            elif (pinionMaterial == "Steel" and gearMaterial == "Cast iron"):
                if f >= 0.0125 and f <= 0.025:
                    return ((C_st_ci_14_5[1]-C_st_ci_14_5[0])/(0.0125))*(f-0.0125) + C_st_ci_14_5[0]
                elif f > 0.025 and f <= 0.05:
                    return ((C_st_ci_14_5[2]-C_st_ci_14_5[1])/(0.025))*(f-0.025) + C_st_ci_14_5[1]
                elif f > 0.05 and f <= 0.075:
                    return ((C_st_ci_14_5[3]-C_st_ci_14_5[2])/(0.025))*(f-0.05) + C_st_ci_14_5[2]
                elif f > 0.075 and f <= 0.1:
                    return ((C_st_ci_14_5[4]-C_st_ci_14_5[3])/(0.025))*(f-0.075) + C_st_ci_14_5[3]
                else:
                    print("Invalid value of f")
                    return -1
            elif (pinionMaterial == "Steel" and gearMaterial == "Steel"):
                if f >= 0.0125 and f <= 0.025:
                    return ((C_st_st_14_5[1]-C_st_st_14_5[0])/(0.0125))*(f-0.0125) + C_st_st_14_5[0]
                elif f > 0.025 and f <= 0.05:
                    return ((C_st_st_14_5[2]-C_st_st_14_5[1])/(0.025))*(f-0.025) + C_st_st_14_5[1]
                elif f > 0.05 and f <= 0.075:
                    return ((C_st_st_14_5[3]-C_st_st_14_5[2])/(0.025))*(f-0.05) + C_st_st_14_5[2]
                elif f > 0.075 and f <= 0.1:
                    return ((C_st_st_14_5[4]-C_st_st_14_5[3])/(0.025))*(f-0.075) + C_st_st_14_5[3]
                else:
                    print("Invalid value of f")
                    return -1
        elif (toothForm == "20 deg Full Depth"):
            if (pinionMaterial == "Cast iron" and gearMaterial == "Cast iron"):
                if f >= 0.0125 and f <= 0.025:
                    return ((C_ci_ci_20_FD[1]-C_ci_ci_20_FD[0])/(0.0125))*(f-0.0125) + C_ci_ci_20_FD[0]
                elif f > 0.025 and f <= 0.05:
                    return ((C_ci_ci_20_FD[2]-C_ci_ci_20_FD[1])/(0.025))*(f-0.025) + C_ci_ci_20_FD[1]
                elif f > 0.05 and f <= 0.075:
                    return ((C_ci_ci_20_FD[3]-C_ci_ci_20_FD[2])/(0.025))*(f-0.05) + C_ci_ci_20_FD[2]
                elif f > 0.075 and f <= 0.1:
                    return ((C_ci_ci_20_FD[4]-C_ci_ci_20_FD[3])/(0.025))*(f-0.075) + C_ci_ci_20_FD[3]
                else:
                    print("Invalid value of f")
                    return -1
            elif (pinionMaterial == "Steel" and gearMaterial == "Cast iron"):
                if f >= 0.0125 and f <= 0.025:
                    return ((C_st_ci_20_FD[1]-C_st_ci_20_FD[0])/(0.0125))*(f-0.0125) + C_st_ci_20_FD[0]
                elif f > 0.025 and f <= 0.05:
                    return ((C_st_ci_20_FD[2]-C_st_ci_20_FD[1])/(0.025))*(f-0.025) + C_st_ci_20_FD[1]
                elif f > 0.05 and f <= 0.075:
                    return ((C_st_ci_20_FD[3]-C_st_ci_20_FD[2])/(0.025))*(f-0.05) + C_st_ci_20_FD[2]
                elif f > 0.075 and f <= 0.1:
                    return ((C_st_ci_20_FD[4]-C_st_ci_20_FD[3])/(0.025))*(f-0.075) + C_st_ci_20_FD[3]
                else:
                    print("Invalid value of f")
                    return -1
            elif (pinionMaterial == "Steel" and gearMaterial == "Steel"):
                if f >= 0.0125 and f < 0.025:
                    return ((C_st_st_20_FD[1]-C_st_st_20_FD[0])/(0.0125))*(f-0.0125) + C_st_st_20_FD[0]
                elif f > 0.025 and f <= 0.05:
                    return ((C_st_st_20_FD[2]-C_st_st_20_FD[1])/(0.025))*(f-0.025) + C_st_st_20_FD[1]
                elif f > 0.05 and f <= 0.075:
                    return ((C_st_st_20_FD[3]-C_st_st_20_FD[2])/(0.025))*(f-0.05) + C_st_st_20_FD[2]
                elif f > 0.075 and f <= 0.1:
                    return ((C_st_st_20_FD[4]-C_st_st_20_FD[3])/(0.025))*(f-0.075) + C_st_st_20_FD[3]
                else:
                    print("Invalid value of f")
                    return -1
        elif (toothForm == "20 deg stub"):
            if (pinionMaterial == "Cast iron" and gearMaterial == "Cast iron"):
                if f >= 0.0125 and f <= 0.025:
                    return ((C_ci_ci_20_stub[1]-C_ci_ci_20_stub[0])/(0.0125))*(f-0.0125) + C_ci_ci_20_stub[0]
                elif f > 0.025 and f <= 0.05:
                    return ((C_ci_ci_20_stub[2]-C_ci_ci_20_stub[1])/(0.025))*(f-0.025) + C_ci_ci_20_stub[1]
                elif f > 0.05 and f <= 0.075:
                    return ((C_ci_ci_20_stub[3]-C_ci_ci_20_stub[2])/(0.025))*(f-0.05) + C_ci_ci_20_stub[2]
                elif f > 0.075 and f <= 0.1:
                    return ((C_ci_ci_20_stub[4]-C_ci_ci_20_stub[3])/(0.025))*(f-0.075) + C_ci_ci_20_stub[3]
                else:
                    print("Invalid value of f")
                    return -1
            elif (pinionMaterial == "Steel" and gearMaterial == "Cast iron"):
                if f >= 0.0125 and f <= 0.025:
                    return ((C_st_ci_20_stub[1]-C_st_ci_20_stub[0])/(0.0125))*(f-0.0125) + C_st_ci_20_stub[0]
                elif f > 0.025 and f <= 0.05:
                    return ((C_st_ci_20_stub[2]-C_st_ci_20_stub[1])/(0.025))*(f-0.025) + C_st_ci_20_stub[1]
                elif f > 0.05 and f <= 0.075:
                    return ((C_st_ci_20_stub[3]-C_st_ci_20_stub[2])/(0.025))*(f-0.05) + C_st_ci_20_stub[2]
                elif f > 0.075 and f <= 0.1:
                    return ((C_st_ci_20_stub[4]-C_st_ci_20_stub[3])/(0.025))*(f-0.075) + C_st_ci_20_stub[3]
                else:
                    print("Invalid value of f")
                    return -1
            elif (pinionMaterial == "Steel" and gearMaterial == "Steel"):
                if f >= 0.0125 and f <= 0.025:
                    return ((C_st_st_20_stub[1]-C_st_st_20_stub[0])/(0.0125))*(f-0.0125) + C_st_st_20_stub[0]
                elif f > 0.025 and f <= 0.05:
                    return ((C_st_st_20_stub[2]-C_st_st_20_stub[1])/(0.025))*(f-0.025) + C_st_st_20_stub[1]
                elif f > 0.05 and f <= 0.075:
                    return ((C_st_st_20_stub[3]-C_st_st_20_stub[2])/(0.025))*(f-0.05) + C_st_st_20_stub[2]
                elif f > 0.075 and f <= 0.1:
                    return ((C_st_st_20_stub[4]-C_st_st_20_stub[3])/(0.025))*(f-0.075) + C_st_st_20_stub[3]
                else:
                    print("Invalid value of f")
                    return -1    
        return -1 # kN/m 
    
    def solveCubicEquation(self, a, b, c, d):
        # Finding the roots
        roots = np.roots([a, b, c, d])
        #print("Roots of the polynomial:", roots)

        # Selecting the smallest positive real root
        smallest_positive_real_root = None
        for root in roots:
            if np.isreal(root) and root > 0:
                if smallest_positive_real_root is None or root < smallest_positive_real_root:
                    smallest_positive_real_root = root

        #print("Smallest positive real root:", smallest_positive_real_root)
        return smallest_positive_real_root
    
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

        # C_pm = 1.1
        # X_planet = (self.FOS * Wt * Kv_planet * Ks * Kb)/(module * Y_planet * self.planetaryGearbox.maxGearAllowableStressPa * 0.001)
        # X_sun = (self.FOS * Wt * Kv_sun * Ks * Kb) / (module * Y_sun * self.planetaryGearbox.maxGearAllowableStressPa * 0.001)
        # X_ring = (self.FOS * Wt * Kv_ring * Ks * Kb) / (module * Y_ring * self.planetaryGearbox.maxGearAllowableStressPa * 0.001)

        # co_eff_of_fwSqr = 0.93/10000
        # co_eff_of_fw_planet = -(C_pm/(module*Np*10*0.03937)) + 1/(39.37*X_planet) - 0.0158
        # co_eff_of_fw_sun = -(C_pm/(module*Ns*10*0.03937)) + 1/(39.37*X_sun) - 0.0158
        # co_eff_of_fw_ring = -(C_pm/(module*Nr*10*0.03937)) + 1/(39.37*X_ring) - 0.0158
        # constant = -1.0995

        # bMin_planet = max(np.roots([co_eff_of_fwSqr, co_eff_of_fw_planet, constant]))/39.37
        # bMin_sun = max(np.roots([co_eff_of_fwSqr, co_eff_of_fw_sun, constant]))/39.37
        # bMin_ring = max(np.roots([co_eff_of_fwSqr, co_eff_of_fw_ring, constant]))/39.37

        # if bMin_planet > 0.026:
        #     co_eff_of_fw_planet = -(C_pm/(module*Np*10*0.03937)) + 1/(39.37*X_planet) - 0.1533
        #     constant = -1.08575
        #     bMin_planet = max(np.roots([co_eff_of_fwSqr, co_eff_of_fw_planet, constant]))/39.37

        # if bMin_ring > 0.026:
        #     co_eff_of_fw_ring = -(C_pm/(module*Nr*10*0.03937)) + 1/(39.37*X_ring) - 0.1533
        #     constant = -1.08575
        #     bMin_ring = max(np.roots([co_eff_of_fwSqr, co_eff_of_fw_ring, constant]))/39.37

        # if bMin_sun > 0.026:
        #     co_eff_of_fw_sun = -(C_pm/(module*Ns*10*0.03937)) + 1/(39.37*X_sun) - 0.1533
        #     constant = -1.08575
        #     bMin_sun = max(np.roots([co_eff_of_fwSqr, co_eff_of_fw_sun, constant]))/39.37

        if bMin_ring < bMin_planet:
            bMin_ring = bMin_planet
        else:
            bMin_planet = bMin_ring

        self.planetaryGearbox.setfwSunMM    ( bMin_sun    * 1000)
        self.planetaryGearbox.setfwPlanetMM ( bMin_planet * 1000)
        self.planetaryGearbox.setfwRingMM   ( bMin_ring   * 1000)

        # print("AGMA:")
        # print(f"bMin_planet = {self.planetaryGearbox.fwPlanetMM}")
        # print(f"bMin_sun = {self.planetaryGearbox.fwSunMM}")
        # print(f"bMin_ring = {self.planetaryGearbox.fwRingMM}")
        # print(f"Yj_planet = {Yj_planet}")
        # print(f"Yj_sun = {Yj_sun}")
        # print(f"Yj_ring = {Yj_ring}")
        # print(f"Kf_planet = {Kf_planet}")
        # print(f"Kf_sun = {Kf_sun}")
        # print(f"Kf_ring = {Kf_ring}")

    def updateFacewidth(self):
        if self.stressAnalysisMethodName == "Lewis":
            self.lewisStressAnalysisMinFacewidth()
        elif self.stressAnalysisMethodName == "AGMA":
            self.AGMAStressAnalysisMinFacewidth()
        elif self.stressAnalysisMethodName == "MIT":
            self.mitStressAnalysisMinFacewidth()

    def getMassKG_3DP(self):
        module    = self.planetaryGearbox.module
        Ns        = self.planetaryGearbox.Ns
        Np        = self.planetaryGearbox.Np
        Nr        = self.planetaryGearbox.Nr
        numPlanet = self.planetaryGearbox.numPlanet

        #------------------------------------
        # density of materials
        #------------------------------------
        densityPLA = 1020 # PLA

        #------------------------------------
        # Face Width
        #------------------------------------
        sunFwMM     = self.planetaryGearbox.fwSunMM
        planetFwMM  = self.planetaryGearbox.fwPlanetMM
        ringFwMM    = self.planetaryGearbox.fwRingMM

        sunFwM    = sunFwMM    * 0.001
        planetFwM = planetFwMM * 0.001
        ringFwM   = ringFwMM   * 0.001

        #------------------------------------
        # Diameter and Radius
        #------------------------------------
        DiaSunMM          = Ns * module
        DiaPlanetMM       = Np * module
        DiaRingMM         = Nr * module

        RadiusSunMM       = DiaSunMM    * 0.5
        RadiusPlanetMM    = DiaPlanetMM * 0.5
        RadiusRingMM      = DiaRingMM   * 0.5
        
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
        case_mounting_surface_height = 4   #mm
        standard_clearance_1_5mm     = 1.5 #mm
        base_plate_thickness         = 4   #mm
        Motor_case_thickness         = 2.5 #mm
        clearance_planet             = 1.5
        output_mounting_hole_dia     = 4
        h_b                          = 1.25 * module
        sec_carrier_thickness        = 5
        sun_coupler_hub_thickness    = 4
        sun_shaft_bearing_OD         = 16
        carrier_bearing_step_width   = 1.5
        planet_shaft_dia             = 8
        motor_output_hole_PCD        = 23 # TODO: Shift it to motor parameters in the JSON file
        motor_output_hole_dia        = 4  # TODO: Shift it to motor parameters in the JSON file
        sun_shaft_bearing_ID         = 8
        sun_shaft_bearing_width      = 5
        planet_bore = 10
        bearing_retainer_thickness = 2

        #--------------------------------------
        # sspg_motor_casing
        #--------------------------------------

        ring_radial_thickness = self.ringRadialWidthMM

        ring_OD  = Nr * module + ring_radial_thickness*2
        motor_OD = self.motorDiaMM

        if (ring_OD < motor_OD):
            clearance_motor_and_case = 5
        else: 
            clearance_motor_and_case = (ring_OD - motor_OD)/2 + 5

        Motor_case_ID     = motor_OD + clearance_motor_and_case * 2
        motor_height      = self.motorLengthMM
        Motor_case_height = motor_height + case_mounting_surface_height + standard_clearance_1_5mm

        Motor_case_OD = Motor_case_ID + Motor_case_thickness * 2

        Motor_case_volume = (  np.pi * ((Motor_case_OD * 0.5)**2) * base_plate_thickness 
                             + np.pi * ((Motor_case_OD * 0.5)**2 - (Motor_case_ID * 0.5)**2) * Motor_case_height
        ) * 1e-9

        Motor_case_mass = Motor_case_volume * densityPLA

        #--------------------------------------
        # sspg_gearbox_casing
        # ---
        # Mass of the gearbox includes the mass of:
        # 1. Ring gear
        # 2. Bearing holding structure
        # 3. Case mounting structure
        #--------------------------------------
        ring_ID      = Nr * module
        ringFwUsedMM = ringFwMM + clearance_planet

        bearing_ID     = InnerDiaBearingMM 
        bearing_OD     = OuterDiaBearingMM 
        bearing_height = WidthBearingMM    
        bearing_mass   = BearingMassKG      

        if ((bearing_OD + output_mounting_hole_dia * 4) > (Nr * module + 2 * h_b)):
            bearing_mount_thickness  = output_mounting_hole_dia * 2
        else:
            bearing_mount_thickness = ((((Nr * module + 2 * h_b) - (bearing_OD + output_mounting_hole_dia * 4))/2) 
                                       + output_mounting_hole_dia * 2 + standard_clearance_1_5mm)        

        bearing_holding_structure_OD     = bearing_OD + bearing_mount_thickness * 2
        bearing_holding_structure_ID     = bearing_OD
        bearing_holding_structure_height = bearing_height + standard_clearance_1_5mm

        case_dist                      = sec_carrier_thickness + clearance_planet + sun_coupler_hub_thickness - case_mounting_surface_height
        case_mounting_structure_ID     = ring_OD
        case_mounting_structure_OD     = Motor_case_OD
        case_mounting_structure_height = case_dist

        ring_volume                      = np.pi * (((ring_OD*0.5)**2) - ((ring_ID)*0.5)**2) * ringFwUsedMM * 1e-9
        bearing_holding_structure_volume = np.pi * (((bearing_holding_structure_OD*0.5)**2) - 
                                                    ((bearing_holding_structure_ID*0.5)**2)) * bearing_holding_structure_height * 1e-9
        case_mounting_structure_volume   = np.pi * (((case_mounting_structure_OD*0.5)**2) - 
                                                    ((case_mounting_structure_ID*0.5)**2)) * case_mounting_structure_height * 1e-9
        
        large_fillet_ID     = ring_OD
        large_fillet_OD     = Motor_case_OD
        large_fillet_height = ringFwMM
        large_fillet_volume = 0.5 * (np.pi * (((large_fillet_OD*0.5)**2) - ((large_fillet_ID)*0.5)**2) * large_fillet_height) * 1e-9

        gearbox_casing_mass = (ring_volume + bearing_holding_structure_volume + case_mounting_structure_volume + large_fillet_volume) * densityPLA

        #----------------------------------
        # sspg_carrier
        # ---
        #----------------------------------
        carrier_OD     = bearing_ID
        carrier_ID     = sun_shaft_bearing_OD - standard_clearance_1_5mm * 2
        carrier_height = bearing_height + carrier_bearing_step_width

        carrier_shaft_OD = planet_shaft_dia
        carrier_shaft_height = planetFwMM + clearance_planet * 2
        carrier_shaft_num = numPlanet * 2

        carrier_volume = (np.pi * (((carrier_OD*0.5)**2) - ((carrier_ID)*0.5)**2) * carrier_height
                          + np.pi * ((carrier_shaft_OD*0.5)**2) * carrier_shaft_height * carrier_shaft_num) * 1e-9

        carrier_mass = carrier_volume * densityPLA

        #----------------------------------
        # sspg_sun
        # ---
        #----------------------------------
        sun_hub_dia = motor_output_hole_PCD + motor_output_hole_dia + standard_clearance_1_5mm * 4

        sun_shaft_dia    = sun_shaft_bearing_ID
        sun_shaft_height = sun_shaft_bearing_width + 2 * standard_clearance_1_5mm

        fw_s_used        = planetFwMM + clearance_planet + sec_carrier_thickness + standard_clearance_1_5mm

        sun_hub_volume   = np.pi * ((sun_hub_dia*0.5) ** 2) * sun_coupler_hub_thickness * 1e-9
        sun_gear_volume  = np.pi * ((DiaSunMM * 0.5) ** 2) * fw_s_used * 1e-9
        sun_shaft_volume = np.pi * ((sun_shaft_dia*0.5) ** 2) * sun_shaft_height * 1e-9

        sun_volume       = sun_hub_volume + sun_gear_volume + sun_shaft_volume
        sun_mass         = sun_volume * densityPLA

        #--------------------------------------
        # sspg_planet
        #--------------------------------------
        planet_volume = (np.pi * ((DiaPlanetMM*0.5)**2 - (planet_bore*0.5)) * planetFwMM) * 1e-9
        planet_mass   = planet_volume * densityPLA

        #--------------------------------------
        # sspg_sec_carrier
        #--------------------------------------
        sec_carrier_OD = bearing_ID
        sec_carrier_ID = (DiaSunMM + DiaPlanetMM) - planet_shaft_dia - 2 * standard_clearance_1_5mm

        sec_carrier_volume = (np.pi * ((sec_carrier_OD*0.5)**2 - (sec_carrier_ID*0.5)) * sec_carrier_thickness) * 1e-9
        sec_carrier_mass   = sec_carrier_volume * densityPLA

        #--------------------------------------
        # sspg_sun_shaft_bearing
        #--------------------------------------
        sun_shaft_bearing_mass = 4 * 0.001 # kg

        #--------------------------------------
        # sspg_planet_bearing
        #--------------------------------------
        planet_bearing_mass          = 1 * 0.001 # kg
        planet_bearing_num           = numPlanet * 2
        planet_bearing_combined_mass = planet_bearing_mass * planet_bearing_num

        #--------------------------------------
        # sspg_planet_bearing
        #--------------------------------------
        bearing_mass = BearingMassKG # kg

        #--------------------------------------
        # sspg_bearing_retainer
        #--------------------------------------
        bearing_retainer_OD        = bearing_holding_structure_OD
        bearing_retainer_ID        = bearing_OD - standard_clearance_1_5mm

        bearing_retainer_volume = (np.pi * ((bearing_retainer_OD*0.5)**2 - (bearing_retainer_ID*0.5)**2) * bearing_retainer_thickness) * 1e-9

        bearing_retainer_mass = bearing_retainer_volume * densityPLA


        self.Motor_case_mass               = Motor_case_mass
        self.gearbox_casing_mass           = gearbox_casing_mass
        self.carrier_mass                  = carrier_mass
        self.sun_mass                      = sun_mass
        self.sec_carrier_mass              = sec_carrier_mass
        self.planet_mass                   = planet_mass
        self.planet_bearing_combined_mass  = planet_bearing_combined_mass
        self.sun_shaft_bearing_mass        = sun_shaft_bearing_mass
        self.bearing_mass                  = bearing_mass
        self.bearing_retainer_mass         = bearing_retainer_mass

        Actuator_mass = (self.motorMassKG 
                         + self.Motor_case_mass 
                         + self.gearbox_casing_mass 
                         + self.carrier_mass 
                         + self.sun_mass 
                         + self.sec_carrier_mass 
                         + self.planet_mass * numPlanet 
                         + self.planet_bearing_combined_mass 
                         + self.sun_shaft_bearing_mass 
                         + self.bearing_mass 
                         + self.bearing_retainer_mass)
        
        return Actuator_mass
    
    def print_mass_of_parts_3DP(self):
        print("Motor_case_mass: ",              1000 * self.Motor_case_mass)
        print("gearbox_casing_mass: ",          1000 * self.gearbox_casing_mass)
        print("carrier_mass: ",                 1000 * self.carrier_mass)
        print("sun_mass: ",                     1000 * self.sun_mass)
        print("sec_carrier_mass: ",             1000 * self.sec_carrier_mass)
        print("planet_mass: ",                  1000 * self.planet_mass)
        print("planet_bearing_combined_mass: ", 1000 * self.planet_bearing_combined_mass)
        print("sun_shaft_bearing_mass: ",       1000 * self.sun_shaft_bearing_mass)
        print("bearing_mass: ",                 1000 * self.bearing_mass)
        print("bearing_retainer_mass: ",        1000 * self.bearing_retainer_mass)
        print("Motor mass:",                    1000 * self.motorMassKG)
        print("---------------------------------------------------")

#========================================================================
# Class: Actuator Optimization
#========================================================================
#------------------------------------------------------------
# Class: Optimization of Single stage Actuator
#------------------------------------------------------------
class optimizationSingleStageActuator:
    def __init__(self,
                 design_params,
                 gear_standard_paramaeters,
                 K_Mass               = 1.0,
                 K_Eff                = -2.0,
                 MODULE_MIN           = 0.5,
                 MODULE_MAX           = 1.2,
                 NUM_PLANET_MIN       = 3,
                 NUM_PLANET_MAX       = 7,
                 NUM_TEETH_SUN_MIN    = 20,
                 NUM_TEETH_PLANET_MIN = 20,
                 GEAR_RATIO_MIN       = 5,
                 GEAR_RATIO_MAX       = 12,
                 GEAR_RATIO_STEP      = 1):
        
        self.K_Mass                        = K_Mass
        self.K_Eff                         = K_Eff
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

    def printOptimizationParameters(self, Actuator=singleStagePlanetaryActuator, log=1, csv=0):
        # Motor Parameters
        maxMotorAngVelRPM       = Actuator.motor.maxMotorAngVelRPM
        maxMotorAngVelRadPerSec = Actuator.motor.maxMotorAngVelRadPerSec
        maxMotorTorque          = Actuator.motor.maxMotorTorque
        maxMotorPower           = Actuator.motor.maxMotorPower
        motorMass               = Actuator.motor.massKG
        motorDia                = Actuator.motor.motorDiaMM
        motorLength             = Actuator.motor.motorLengthMM

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
            print("K_Mass:                       ", self.K_Mass)
            print("K_Eff:                        ", self.K_Eff)
            print("MODULE_MIN:                   ", self.MODULE_MIN)
            print("MODULE_MAX:                   ", self.MODULE_MAX)
            print("NUM_PLANET_MIN:               ", self.NUM_PLANET_MIN)
            print("NUM_PLANET_MAX:               ", self.NUM_PLANET_MAX)
            print("NUM_TEETH_SUN_MIN:            ", self.NUM_TEETH_SUN_MIN)
            print("NUM_TEETH_PLANET_MIN:         ", self.NUM_TEETH_PLANET_MIN)
            print("GEAR_RATIO_MIN:               ", self.GEAR_RATIO_MIN)
            print("GEAR_RATIO_MAX:               ", self.GEAR_RATIO_MAX)
            print("GEAR_RATIO_STEP:              ", self.GEAR_RATIO_STEP)
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
            print("K_mass, K_Eff, MODULE_MIN, MODULE_MAX, NUM_PLANET_MIN, NUM_PLANET_MAX, NUM_TEETH_SUN_MIN, NUM_TEETH_PLANET_MIN, GEAR_RATIO_MIN, GEAR_RATIO_MAX, GEAR_RATIO_STEP")
            print(self.K_Mass,",", self.K_Eff,",", self.MODULE_MIN,",", self.MODULE_MAX,",", self.NUM_PLANET_MIN,",", self.NUM_PLANET_MAX,",", self.NUM_TEETH_SUN_MIN,",", self.NUM_TEETH_PLANET_MIN,",", self.GEAR_RATIO_MIN,",", self.GEAR_RATIO_MAX,",", self.GEAR_RATIO_STEP)

    def printOptimizationResults(self, Actuator=singleStagePlanetaryActuator, log=1, csv=0):
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
            # mass       = round(Actuator.getMassKG_new(), 3)
            mass       = round(Actuator.getMassKG_3DP(), 3)
            eff        = round(Actuator.planetaryGearbox.getEfficiency(), 3)
            
            # Update it is PSC are non-zero
            if self.UsePSCasVariable == 1 : 
                eff  = round(self.sspgOpt.getEfficiency(Var=False), 3)
            
            peakTorque = round(Actuator.motor.getMaxMotorTorque()*Actuator.planetaryGearbox.gearRatio(), 3)
            Cost       = self.K_Mass * mass + self.K_Eff * eff
            Torque_Density = peakTorque / mass
            print(iter,",", gearRatio,",",module,",", Ns,",", Np,",", Nr,",", numPlanet,",",  fwSunMM,",", fwPlanetMM,",", fwRingMM,",",Opt_PSC_sun,",", Opt_PSC_planet,",", Opt_PSC_ring,",", Opt_CD_SP, ",", Opt_CD_PR,",", mass,",", eff,",", peakTorque,",", Cost, ",", Torque_Density)

    def optimizeActuator(self, Actuator=singleStagePlanetaryActuator, UsePSCasVariable = 1, log = 0, csv = 1):
        self.UsePSCasVariable = UsePSCasVariable
        totalTime = 0
        if UsePSCasVariable == 0:
            totalTime = self.optimizeActuatorWithoutPSC(Actuator, log, csv)
        elif UsePSCasVariable == 1:
            totalTime = self.optimizeActuatorWith_MINLP_PSC(Actuator, log, csv)
        else:
            totalTime = 0
            print("ERROR: \"UsePSCasVariable\" can be either 0 or 1")
        
        return totalTime

    def optimizeActuatorWithoutPSC(self, Actuator=singleStagePlanetaryActuator, log=1, csv=0): 
        startTime = time.time()
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
            fileName = f"./results/results_BruteForce_{Actuator.motor.motorName}/SSPG_BRUTEFORCE_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}.csv"
        elif log:
            fileName = f"./results/results_BruteForce_{Actuator.motor.motorName}/SSPG_BRUTEFORCE_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}.txt"
            
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
                # print("iter, gearRatio, module, Ns, Np, Nr, numPlanet, fwSunMM, fwPlanetMM, fwRingMM, mass, eff, peakTorque, Cost, Torque_Density")

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
                                        Actuator.planetaryGearbox.noPlanetInterferenceConstraint()):

                                        self.totalFeasibleGearboxes += 1
                                        if ((Actuator.planetaryGearbox.gearRatio() >= self.gearRatioIter) and
                                            (Actuator.planetaryGearbox.gearRatio() <= self.gearRatioIter + self.GEAR_RATIO_STEP)):
                                            self.totalGearboxesWithRequiredGR += 1
                                            Actuator.updateFacewidth()

                                            effActuator = Actuator.planetaryGearbox.getEfficiency()
                                            # massActuator = Actuator.getMassKG_new()
                                            massActuator = Actuator.getMassKG_3DP()

                                            self.Cost = (self.K_Mass * massActuator) + (self.K_Eff * effActuator)
                                            #self.Cost = massActuator/effActuator
                                            if self.Cost <= MinCost:
                                                MinCost = self.Cost
                                                self.iter+=1
                                                opt_done = 1
                                                # Actuator.genEquationFile()
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
                                                                                                   module                    = Actuator.planetaryGearbox.module,     # mm
                                                                                                   numPlanet                 = Actuator.planetaryGearbox.numPlanet,
                                                                                                   fwSunMM                   = Actuator.planetaryGearbox.fwSunMM,    # mm
                                                                                                   fwPlanetMM                = Actuator.planetaryGearbox.fwPlanetMM, # mm
                                                                                                   fwRingMM                  = Actuator.planetaryGearbox.fwRingMM,   # mm
                                                                                                   maxGearAllowableStressMPa = Actuator.planetaryGearbox.maxGearAllowableStressMPa, # 400 MPa
                                                                                                   densityGears              = Actuator.planetaryGearbox.densityGears,     # 7850 kg/m^3: Steel
                                                                                                   densityCarrier            = Actuator.planetaryGearbox.densityCarrier,   # 2710 kg/m^3: Aluminum
                                                                                                   densityStructure          = Actuator.planetaryGearbox.densityStructure) # 2710 kg/m^3: Aluminum

                                                opt_actuator = singleStagePlanetaryActuator(design_params            = self.design_params,
                                                                                            motor                    = Actuator.motor, 
                                                                                            planetaryGearbox         = opt_planetaryGearbox, 
                                                                                            FOS                      = Actuator.FOS, 
                                                                                            serviceFactor            = Actuator.serviceFactor, 
                                                                                            maxGearboxDiameter       = Actuator.maxGearboxDiameter, # mm 
                                                                                            stressAnalysisMethodName = "MIT") # Lewis or AGMA
                                                opt_actuator.updateFacewidth()
                                                opt_actuator.getMassKG_3DP()
                                                # opt_actuator.print_mass_of_parts_3DP()

                                                # self.printOptimizationResults(Actuator, log, csv)
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
            print("\n")
            print("Running Time (sec)")
            print(totalTime) 

        sys.stdout = sys.__stdout__
        return totalTime

    def optimizeActuatorWith_MINLP_PSC(self, Actuator=singleStagePlanetaryActuator, log=1, csv=0):
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
                                                # massActuator = Actuator.getMassKG_new()
                                                massActuator = Actuator.getMassKG_3DP()

                                                self.Cost = (self.K_Mass * massActuator) + (self.K_Eff * effActuator)
                                                if self.Cost <= MinCost:
                                                    MinCost    = self.Cost
                                                    self.iter += 1
                                                    opt_done   = 1
                                                    # Actuator.genEquationFile()
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
                                                                                                       module                    = Actuator.planetaryGearbox.module,     # mm
                                                                                                       numPlanet                 = Actuator.planetaryGearbox.numPlanet,
                                                                                                       fwSunMM                   = Actuator.planetaryGearbox.fwSunMM,    # mm
                                                                                                       fwPlanetMM                = Actuator.planetaryGearbox.fwPlanetMM, # mm
                                                                                                       fwRingMM                  = Actuator.planetaryGearbox.fwRingMM,   # mm
                                                                                                       maxGearAllowableStressMPa = Actuator.planetaryGearbox.maxGearAllowableStressMPa, # 400 MPa
                                                                                                       densityGears              = Actuator.planetaryGearbox.densityGears,     # 7850 kg/m^3: Steel
                                                                                                       densityCarrier            = Actuator.planetaryGearbox.densityCarrier,   # 2710 kg/m^3: Aluminum
                                                                                                       densityStructure          = Actuator.planetaryGearbox.densityStructure) # 2710 kg/m^3: Aluminum

                                                    opt_actuator = singleStagePlanetaryActuator(design_params            = self.design_params,
                                                                                                motor                    = Actuator.motor, 
                                                                                                planetaryGearbox         = opt_planetaryGearbox, 
                                                                                                FOS                      = Actuator.FOS, 
                                                                                                serviceFactor            = Actuator.serviceFactor, 
                                                                                                maxGearboxDiameter       = Actuator.maxGearboxDiameter, # mm 
                                                                                                stressAnalysisMethodName = "Lewis") # Lewis or AGMA
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

#------------------------------------------------------------
# Continuous optimization of the Profile shift coefficients
#------------------------------------------------------------
class optimal_continuous_PSC_sspg:
    def __init__(self,
                 GEAR_RATIO_MIN = 16, 
                 numPlanet = 3, 
                 Ns = 20,
                 Np = 30,
                 Nr = 80,
                 M= 5):
        #---------------------------------
        # Define variables
        #---------------------------------
        # Define Model
        self.model = ConcreteModel()
        # Number of teeth on gears
        self.Ns = Ns
        self.Np = Np
        self.Nr = Nr   
        self.M =  M    
        self.pressureAngle = 20
        self.mu = 0.3
  
        self.model.PSCs = Var(within=Reals, bounds=(-1.0,1.0), initialize = 0.0)
        self.model.PSCp = Var(within=Reals, bounds=(-1.0,1.0), initialize = 0.0)
        self.model.PSCr = Var(within=Reals, bounds=(-1.0,1.0), initialize = 0.0)

        # Define objective
        self.model.obj = Objective(expr=self.getCost(Var = True), sense=maximize)

        # Constraints
        self.model.centerDistEqualityConstraint = Constraint(expr = self.centerDistEqualityConstraint())

    #-------------------------------------------------------------------------
    # Constraints
    #-------------------------------------------------------------------------
    def centerDistEqualityConstraint(self):
        centerDist_SP, centerDist_PR = self.getCenterDistance()
        return (centerDist_SP == centerDist_PR)

    def contactRatio_SP_GreaterThan1(self):
        _, _, CR_SP = self.contactRatio_sunPlanet()
        return (CR_SP >= 1.1)

    def contactRatio_PR_GreaterThan1(self):
        _, _, CR_PR = self.contactRatio_planetRing()
        return (CR_PR >= 1.1)

    # Used when optimizing for manufacturing
    def centerDistManufacturingFriendlyConstraint(self, centerDistForManufacturing):
        _, r = self.getCenterDistance()
        return (r == centerDistForManufacturing) 
    
    #-------------------------------------------------------------------------
    # Gear Tooth profile parameters
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
        return (tan(alpha) - alpha)

    # Define the differentiable quadratic approximation of the min function
    def quadratic_min(self, a, b, k=0.01):
        return (a + b - sqrt((a - b)**2 + k**2)) / 2
    
    def getPressureAngleRad(self, Var=True):
        return self.pressureAngle * np.pi / 180  # Pressure angle in radians

    def getWorkingPressureAngle(self, Var=True):
        module = self.M * 0.1  # Module of the gear
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr  
        if (Var == True):
            xs = self.model.PSCs
            xp = self.model.PSCp
            xr = self.model.PSCr

        elif (Var == False):
            xs = self.model.PSCs.value
            xp = self.model.PSCp.value
            xr = self.model.PSCr.value
        
        #---------------------------------
        # Pressure Angle
        #---------------------------------
        alpha = self.getPressureAngleRad(Var=Var)

        #---------------------------------
        # Working pressure angle
        #---------------------------------
        # Sun-Planet
        inv_alpha_w_sunPlanet = 2*tan(alpha)*((xs + xp)/(Ns + Np)) + self.involute(alpha)
        alpha_w_sunPlanet = self.inverse_involute(inv_alpha_w_sunPlanet)

        # Planet-Ring
        inv_alpha_w_planetRing = 2*tan(alpha)*((xr-xp)/(Nr - Np)) + self.involute(alpha)
        alpha_w_planetRing = self.inverse_involute(inv_alpha_w_planetRing)

        return alpha_w_sunPlanet, alpha_w_planetRing
    
    def getCenterDistance(self, Var = True):
        module = self.M * 0.1  # Module of the gear
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr   
        #-------------------------------
        # Centre distance modification coefficient
        #-------------------------------
        y_sunPlanet, y_planetRing = self.getCenterDistModificationCoeff(Var=Var)

        #-------------------------------
        # Centre distance
        #-------------------------------
        centerDist_sunPlanet = ((Ns + Np)/2  + y_sunPlanet)* module
        centerDist_planetRing = ((Nr - Np)/2  + y_planetRing)* module

        return centerDist_sunPlanet, centerDist_planetRing

    def getCenterDistModificationCoeff(self, Var = True):
        module = self.M * 0.1  # Module of the gear
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr   
        #------------------------------
        # Pressure Angle
        #------------------------------
        alpha = self.getPressureAngleRad(Var=Var)  # Pressure angle in radians

        #------------------------------
        # Working pressure angle
        #------------------------------
        alpha_w_sunPlanet, alpha_w_planetRing = self.getWorkingPressureAngle(Var=Var)

        #------------------------------
        # Centre distance modification coefficient
        #------------------------------
        y_sunPlanet  = ((Ns + Np) / 2) * ((cos(alpha) / cos(alpha_w_sunPlanet)) - 1)
        y_planetRing = ((Nr - Np) / 2) * ((cos(alpha) / cos(alpha_w_planetRing)) - 1)

        return y_sunPlanet, y_planetRing

    def getBaseDia(self,Var=True):
        module = self.M * 0.1  # Module of the gear
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr   
        # Pressure Angle
        alpha = self.getPressureAngleRad(Var = Var) # Rad

        # Reference Diameter
        D_sun    = module * Ns # Sun's reference diameter
        D_planet = module * Np # Planet's reference diameter
        D_ring   = module * Nr # Ring's reference diameter

        # Base Diameter
        D_b_sun    = D_sun * cos(alpha)
        D_b_planet = D_planet * cos(alpha)
        D_b_ring   = D_ring * cos(alpha)

        return D_b_sun, D_b_planet, D_b_ring

    def getTipCircleDia(self, Var=True):
        module = self.M * 0.1  # Module of the gear
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr   
        if (Var == True):
            xs = self.model.PSCs
            xp = self.model.PSCp
            xr = self.model.PSCr
        elif (Var == False):
            Nr     = self.Nr
            xs = self.model.PSCs.value
            xp = self.model.PSCp.value
            xr = self.model.PSCr.value

        #----------------------------
        # Pressure Angle
        #----------------------------
        alpha = self.getPressureAngleRad(Var = Var) # Rad

        #----------------------------
        # Reference Diameter
        #----------------------------
        D_sun    = module * Ns # Sun's reference diameter
        D_planet = module * Np # Planet's reference diameter
        D_ring   = module * Nr # Ring's reference diameter

        #----------------------------
        # Center Distance Modification Coefficient
        #----------------------------
        y_sunPlanet, y_planetRing = self.getCenterDistModificationCoeff(Var = Var)

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

    def getTipPressureAngle(self, Var=True):
        module = self.M * 0.1  # Module of the gear
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr   

        alpha = self.getPressureAngleRad(Var = Var) # Pressure Angle (Rad)
        D_b_sun, D_b_planet, D_b_ring = self.getBaseDia(Var = Var) # Base Diameter
        D_a_sun, D_a_planet, D_a_ring = self.getTipCircleDia(Var = Var) # Tip Circle Diameter

        #----------------------------
        # Tip Pressure angle
        #----------------------------
        alpha_a_sun    = acos(D_b_sun / D_a_sun)
        alpha_a_planet = acos(D_b_planet/D_a_planet)
        alpha_a_ring   = acos(D_b_ring / D_a_ring)

        return alpha_a_sun, alpha_a_planet, alpha_a_ring

    def getErrorTipCircleDia_planet(self, Var = True):
        module = self.M * 0.1  # Module of the gear
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr   
        if (Var == True):
            xs = self.model.PSCs
            xp = self.model.PSCp
            xr = self.model.PSCr

        elif (Var == False):
            xs = self.model.PSCs.value
            xp = self.model.PSCp.value
            xr = self.model.PSCr.value

        # Centre distance modification coefficient
        y_sunPlanet, _ = self.getCenterDistModificationCoeff(Var=Var)

        # Tip Circle Diameter
        _, D_a_planet_1, _ = self.getTipCircleDia(Var=Var)
        D_a_planet_2 = module * Np + 2*module*(1 + np.minimum((y_sunPlanet - xs),xp)) # TODO: How will we implement min function 

        return np.abs(D_a_planet_1 - D_a_planet_2)
    
    #-------------------------------------------------------------------------
    # Contact Ratio
    #-------------------------------------------------------------------------
    def contactRatio_sunPlanet(self, Var = True):
        module = self.M * 0.1  # Module of the gear
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr   
        # Working pressure angle
        alpha_w_sunPlanet, _ = self.getWorkingPressureAngle(Var=Var)

        # Tip pressure angle
        alpha_a_sun, alpha_a_planet, _ = self.getTipPressureAngle(Var=Var)

        # Contact ratio
        Approach_CR_sunPlanet = (Np / (2 * np.pi)) * (tan(alpha_a_planet) - tan(alpha_w_sunPlanet)) # Approach contact ratio
        Recess_CR_sunPlanet   = (Ns / (2 * np.pi)) * (tan(alpha_a_sun) - tan(alpha_w_sunPlanet))    # Recess contact ratio

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

    def contactRatio_planetRing(self, Var = True):
        module = self.M * 0.1  # Module of the gear
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr   

        # Working pressure angle
        _, alpha_w_planetRing = self.getWorkingPressureAngle(Var=Var)

        # Tip pressure angle
        _, alpha_a_planet, alpha_a_ring = self.getTipPressureAngle(Var=Var)

        # Contact ratio
        Approach_CR_planetRing = -(Nr / (2 * np.pi)) * (tan(alpha_a_ring) - tan(alpha_w_planetRing)) # Approach contact ratio
        Recess_CR_planetRing   =   Np / (2 * np.pi) * (tan(alpha_a_planet) - tan(alpha_w_planetRing)) # Recess contact ratio
        
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
    def getEfficiency(self, Var = True):
        module = self.M * 0.1  # Module of the gear
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr   
        xs = self.model.PSCs.value
        xp = self.model.PSCp.value
        xr = self.model.PSCr.value
        # Contact ratio
        eps_sunPlanetA, eps_sunPlanetR, _ = self.contactRatio_sunPlanet(Var=Var)
        eps_planetRingA, eps_planetRingR, _ = self.contactRatio_planetRing(Var=Var)
        
        # Contact-Ratio-Factor
        epsilon_sunPlanet = eps_sunPlanetA**2 + eps_sunPlanetR**2 - eps_sunPlanetA - eps_sunPlanetR + 1 
        epsilon_planetRing = eps_planetRingA**2 + eps_planetRingR**2 - eps_planetRingA - eps_planetRingR + 1 
        
        # Efficiency
        eff_SP = 1 - self.mu * np.pi * ((1 / Np) + (1 / Ns)) * epsilon_sunPlanet
        eff_PR = 1 - self.mu * np.pi * ((1 / Np) - (1 / Nr)) * epsilon_planetRing

        Eff = (1 + eff_SP * eff_PR * (Nr / Ns)) / (1 + (Nr / Ns))
        return Eff

    #-------------------------------------------------------------------------
    # Cost Calculation
    #-------------------------------------------------------------------------
    def getCost(self, Var = True):
        module = self.M * 0.1  # Module of the gear
        Ns     = self.Ns
        Np     = self.Np
        Nr     = self.Nr   
        K_eff = 1
        return K_eff * self.getEfficiency(Var = Var)

    #-------------------------------------------------------------------------
    # Solution
    #-------------------------------------------------------------------------
    def solve(self, optimizeForManufacturing=False, centerDistForManufacturing = 0):
        # NOTE: This constraint ensures the center distance is suitable for manufacturing, 
        # e.g., a value like 14.5mm is preferable over 14.5567367mm.
        if (optimizeForManufacturing == True):
            self.model.centerDistManufacturingFriendlyConstraint = (
                Constraint(expr = self.centerDistManufacturingFriendlyConstraint(centerDistForManufacturing))
            )

        solver = SolverFactory('mindtpy')
        results = solver.solve(self.model, 
                               strategy='OA',
                               mip_solver='gurobi_persistent',
                            #    mip_solver_args = dict(solver='cplex', warmstart=True),
                               nlp_solver='ipopt',
                               single_tree=True,
                               tee=False)
        
        _, actual_centerDist = self.getCenterDistance(Var = False)

        # Calculate the Preferred center distance for manufacturing
        calc_centerDistForManufacturing = int(actual_centerDist * 10) * 0.1

        return results, calc_centerDistForManufacturing
    
    def display(self):
        self.model.display()
