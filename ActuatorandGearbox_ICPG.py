from typing import Any
import numpy as np
import os
import sys
import time
import math

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
        self.data_bearings = [[10,19,5,0.005],[12,21,5,0.006],[15,24,5,0.007],[17,26,5,0.007],[20,32,7,0.017],[25,37,7,0.021],[28,52,12,0.096],[30,42,7,0.024],[32,58,13,0.122],[35,47,7,0.027],[40,52,7,0.031],[45,58,7,0.038],[50,65,7,0.050],[55,72,9,0.081],[60,78,10,0.103],[65,85,10,0.128],[70,90,10,0.134],[75,95,10,0.149],[80,100,10,0.151],[85,110,13,0.263],
                              [90,115,13,0.276],[95,120,13,0.297],[100,125,13,0.31],[105,130,13,0.324],[110,140,16,0.497],[120,150,16,0.537],[130,165,18,0.758],[140,170,18,0.832],[150,190,20,1.15],[160,200,20,1.23]]
        self.idRequiredMM = idRequiredMM
        self.indexBearing =   0
        while (self.indexBearing < len(self.data_bearings) - 1 and self.data_bearings[self.indexBearing][0] < self.idRequiredMM):
            self.indexBearing +=1

    def getBearingIDMM(self):
        return self.data_bearings[self.indexBearing][0]
    
    def getBearingODMM(self):
        return self.data_bearings[self.indexBearing][1]
    
    def getBearingWidthMM(self):
        return self.data_bearings[self.indexBearing][2]
    
    def getBearingMassKG(self):
        return self.data_bearings[self.indexBearing][3]

#-------------------------------------------------------------------------
# Nuts and bolts class
#-------------------------------------------------------------------------
class nuts_and_bolts_dimensions:
    def __init__(self, bolt_dia, bolt_type="socket_head"):
        self.bolt_dia  = bolt_dia
        self.bolt_type = bolt_type
        self.bolt_head_dia, self.bolt_head_height = self.get_bolt_head_dimensions(diameter=self.bolt_dia, bolt_type=self.bolt_type)
        self.nut_width_across_flats, self.nut_thickness = self.get_nut_dimensions(diameter=self.bolt_dia)

    def get_bolt_head_dimensions(self, diameter, bolt_type="socket_head"):
        diameter = float(diameter)
        socket_head_table = {
            1.6: {"d2": (3.00), "k": (1.60)},
            2.0: {"d2": (3.80), "k": (2.00)},
            2.5: {"d2": (4.50), "k": (2.50)},
            3.0: {"d2": (5.50), "k": (3.00)},
            4.0: {"d2": (7.00), "k": (4.00)},
            5.0: {"d2": (8.50), "k": (5.00)},
            6.0: {"d2": (10.00), "k": (6.00)},
            8.0: {"d2": (13.00), "k": (8.00)},
            10.0: {"d2": (16.00), "k": (10.00)}
        }
        csk_table = {
            3.0: {"dk": 6}, 4.0: {"dk": 8}, 5.0: {"dk": 10}, 6.0: {"dk": 12},
            8.0: {"dk": 16}, 10.0: {"dk": 20}, 12.0: {"dk": 24}, 16.0: {"dk": 30}, 20.0: {"dk": 36}
        }
        if bolt_type == "socket_head":
            spec = socket_head_table.get(diameter)
            if not spec: raise ValueError(f"Socket head bolt M{diameter} not found.")
            return [spec["d2"], spec["k"]]
        elif bolt_type == "CSK":
            spec = csk_table.get(diameter)
            if not spec: raise ValueError(f"CSK bolt M{diameter} not found.")
            dk = spec["dk"]
            t = (dk - diameter) / 2
            return [dk, round(t, 3)]
        else:
            raise ValueError("bolt_type must be 'socket_head' or 'CSK'")

    def get_nut_dimensions(self, diameter):
        diameter = float(diameter)
        nut_table = {
            2.0: {"width_across_flats": 4, "height": 1.6},
            2.5: {"width_across_flats": 5, "height": 2},
            3.0: {"width_across_flats": 5.5, "height": 2.4},
            4.0: {"width_across_flats": 7, "height": 3.2},
            5.0: {"width_across_flats": 8, "height": 4},
            6.0: {"width_across_flats": 10, "height": 5},
            7.0: {"width_across_flats": 7, "height": 5.5},  # ISO fallback
            8.0: {"width_across_flats": 13, "height": 6.5},
            10.0: {"width_across_flats": 16, "height": 8},
            12.0: {"width_across_flats": 18, "height": 10},
        }
        spec = nut_table.get(diameter)
        if not spec: raise ValueError(f"No nut data found for bolt diameter M{diameter}")
        return [spec["width_across_flats"], spec["height"]]

#=========================================================================
# Gearbox classes
#=========================================================================
class internalcompoundPlanetaryGearbox:
    def __init__(self,
                 design_parameters,
                 gear_standard_parameters,
                 Ns                        = 20,
                 NpBig                     = 20,
                 NpSmall                   = 20,
                 Nr                        = 60,
                 numPlanet                 = 2,
                 moduleBig                 = 0.8,
                 moduleSmall               = 0.8,
                 fwSunMM                   = 5.0,
                 fwPlanetBigMM             = 5.0,
                 fwPlanetSmallMM           = 5.0,
                 fwRingMM                  = 5.0,
                 densityGears              = 7850.0,
                 densityStructure          = 2710.0,
                 maxGearAllowableStressMPa = 400.0):
        
        self.Ns                        = Ns
        self.NpBig                     = NpBig
        self.NpSmall                   = NpSmall
        self.Nr                        = Nr
        self.numPlanet                 = numPlanet
        self.moduleBig                 = moduleBig
        self.moduleSmall               = moduleSmall
        self.densityGears              = densityGears
        self.densityStructure          = densityStructure
        self.fwSunMM                   = fwSunMM
        self.fwPlanetBigMM             = fwPlanetBigMM
        self.fwPlanetSmallMM           = fwPlanetSmallMM
        self.fwRingMM                  = fwRingMM
        self.maxGearAllowableStressMPa = maxGearAllowableStressMPa
        self.maxGearAllowableStressPa  = maxGearAllowableStressMPa * 10 ** 6

        self.mu               = gear_standard_parameters["coefficientOfFriction"]
        self.pressureAngleDEG = gear_standard_parameters["pressureAngleDEG"]

        self.ringRadialWidthMM = design_parameters["ringRadialWidthMM"]
        self.planetMinDistanceMM          = design_parameters["planetMinDistanceMM"]
        self.sCarrierExtrusionDiaMM       = design_parameters["sCarrierExtrusionDiaMM"]
        self.sCarrierExtrusionClearanceMM = design_parameters["sCarrierExtrusionClearanceMM"]

    def geometricConstraint(self):
        return ((self.Ns + self.NpBig) * self.moduleBig == (self.Nr - self.NpSmall) * self.moduleSmall)
        
    def meshingConstraint(self):
        return ((self.Ns % self.numPlanet == 0) and (self.Nr % self.numPlanet == 0))
    
    def noPlanetInterferenceConstraint_old(self):
        return 2*(self.Ns + self.NpBig)*self.moduleBig*np.sin(np.pi/self.numPlanet) >= 2*self.moduleBig*self.NpBig + self.planetMinDistanceMM

    def noPlanetInterferenceConstraint(self):
        module1   = self.moduleBig
        module2   = self.moduleSmall
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
        fwSunM            = (self.fwSunMM / 1000.0)
        fwPlanetBigM      = (self.fwPlanetBigMM / 1000.0)
        fwPlanetSmallM    = (self.fwPlanetSmallMM / 1000.0)
        fwRingM           = (self.fwRingMM / 1000.0)
        carrierWidthM     = 0.005 # Placeholder for old logic
        sunVolume         = np.pi * fwSunM * (self.getPCRadiusSunM()**2)
        planetBigVolume   = np.pi * fwPlanetBigM * (self.getPCRadiusPlanetBigM()**2)
        planetSmallVolume = np.pi * fwPlanetSmallM * (self.getPCRadiusPlanetSmallM()**2)
        ringVolume        = np.pi * fwRingM * (self.getOuterRadiusRingM()**2 - self.getPCRadiusRingM()**2)
        carrierVolume     = 2 * np.pi * carrierWidthM * (self.getCarrierRadiusM()**2)
        
        combinedGearVolume = sunVolume + (self.numPlanet * planetBigVolume) + planetSmallVolume + ringVolume
        TotalMassKG        = (combinedGearVolume * self.densityGears + carrierVolume * self.densityStructure)
        return TotalMassKG
    
    def gearRatio(self):
        Rs = self.Ns * self.moduleBig
        RpBig = self.NpBig * self.moduleBig
        RpSmall = self.NpSmall * self.moduleSmall
        Rr = self.Nr * self.moduleSmall
        GR = ((Rs + RpBig) * (RpSmall + RpBig)) / (Rs * RpSmall)
        return GR

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
        return self.pressureAngleDEG * np.pi / 180
 
    def getWorkingPressureAngle(self):
        module1 = self.moduleBig
        module2 = self.moduleSmall
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr      = self.Nr
        xs, xp1, xp2, xr = 0, 0, 0, 0
        
        alpha = self.getPressureAngleRad()
        inv_alpha_w_sunPlanet = 2*np.tan(alpha)*((xs + xp1)/(Ns + Np1)) + self.involute(alpha)
        alpha_w_sunPlanet = self.inverse_involute(inv_alpha_w_sunPlanet)
        inv_alpha_w_planetRing = 2*np.tan(alpha)*((xr-xp2)/(Nr - Np2)) + self.involute(alpha)
        alpha_w_planetRing = self.inverse_involute(inv_alpha_w_planetRing)
        return alpha_w_sunPlanet, alpha_w_planetRing

    def getCenterDistModificationCoeff(self):
        module1 = self.moduleBig
        module2 = self.moduleSmall
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr      = self.Nr

        alpha = self.getPressureAngleRad()
        alpha_w_sunPlanet, alpha_w_planetRing = self.getWorkingPressureAngle()
        y_sunPlanet  = ((Ns + Np1) / 2) * ((np.cos(alpha) / np.cos(alpha_w_sunPlanet)) - 1)
        y_planetRing = ((Nr - Np2) / 2) * ((np.cos(alpha) / np.cos(alpha_w_planetRing)) - 1)
        return y_sunPlanet, y_planetRing

    def getCenterDistance(self):
        module1 = self.moduleBig
        module2 = self.moduleSmall
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr      = self.Nr
    
        y_sunPlanet, y_planetRing = self.getCenterDistModificationCoeff()
        centerDist_sunPlanet = ((Ns + Np1)/2  + y_sunPlanet)* module1
        centerDist_planetRing = ((Nr - Np2)/2  + y_planetRing)* module2
        return centerDist_sunPlanet, centerDist_planetRing

    def getBaseDia(self):
        module1 = self.moduleBig
        module2 = self.moduleSmall
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr      = self.Nr

        alpha = self.getPressureAngleRad()
        D_sun     = module1 * Ns
        D_planet1 = module1 * Np1
        D_planet2 = module2 * Np2
        D_ring    = module2 * Nr

        D_b_sun     = D_sun * np.cos(alpha)
        D_b_planet1 = D_planet1 * np.cos(alpha)
        D_b_planet2 = D_planet2 * np.cos(alpha)
        D_b_ring    = D_ring * np.cos(alpha)
        return D_b_sun, D_b_planet1, D_b_planet2, D_b_ring
 
    def getTipCircleDia(self):
        module1 = self.moduleBig
        module2 = self.moduleSmall
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr      = self.Nr
        xs, xp1, xp2, xr = 0, 0, 0, 0
        
        alpha = self.getPressureAngleRad()
        D_sun     = module1 * Ns
        D_planet1 = module1 * Np1
        D_planet2 = module2 * Np2
        D_ring    = module2 * Nr

        y_sunPlanet, y_planetRing = self.getCenterDistModificationCoeff()

        D_a_sun = D_sun + 2 * module1 * (1 + y_sunPlanet - xp1)
        D_a_planet1  = D_planet1 + 2 * module1 * (1 + self.quadratic_min((y_sunPlanet - xs), xp1))  
        D_a_planet2  = D_planet2 + 2 * module2 * (1 + self.quadratic_min((y_planetRing - xs),xp2)) 
        D_a_ring = D_ring - 2 * module2 * (1 - xr)
        
        return D_a_sun, D_a_planet1, D_a_planet2, D_a_ring
 
    def getTipPressureAngle(self):
        module1 = self.moduleBig
        module2 = self.moduleSmall
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr      = self.Nr

        alpha = self.getPressureAngleRad()
        D_b_sun, D_b_planet1, D_b_planet2, D_b_ring = self.getBaseDia()
        D_a_sun, D_a_planet1, D_a_planet2, D_a_ring = self.getTipCircleDia()

        alpha_a_sun     = np.arccos(D_b_sun / D_a_sun)
        alpha_a_planet1 = np.arccos(D_b_planet1/D_a_planet1)
        alpha_a_planet2 = np.arccos(D_b_planet2/D_a_planet2)
        alpha_a_ring    = np.arccos(D_b_ring / D_a_ring)

        return alpha_a_sun, alpha_a_planet1, alpha_a_planet2, alpha_a_ring

    def getErrorTipCircleDia_planet(self):
        module1 = self.moduleBig
        module2 = self.moduleSmall
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr      = self.Nr
        xs, xp1, xp2, xr = 0, 0, 0, 0
        
        y_sunPlanet, y_planetRing = self.getCenterDistModificationCoeff()

        _, D_a_planet1_quadMin, D_a_planet2_quadMin, _ = self.getTipCircleDia()
        D_a_planet1_actMin = module1 * Np1 + 2 * module1 * (1 + np.minimum((y_sunPlanet - xs),xp1)) 
        D_a_planet2_actMin = module2 * Np2 + 2 * module2 * (1 + np.minimum((y_planetRing - xs),xp2))

        return np.abs(D_a_planet1_quadMin - D_a_planet1_actMin), np.abs(D_a_planet2_quadMin - D_a_planet2_actMin)

    def contactRatio_sunPlanet(self):
        module1 = self.moduleBig
        module2 = self.moduleSmall
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr      = self.Nr

        alpha_w_sunPlanet, _ = self.getWorkingPressureAngle()
        alpha_a_sun, alpha_a_planet1, _, _ = self.getTipPressureAngle()

        Approach_CR_sunPlanet = (Np1 / (2 * np.pi)) * (np.tan(alpha_a_planet1) - np.tan(alpha_w_sunPlanet))
        Recess_CR_sunPlanet   =  (Ns / (2 * np.pi)) * (np.tan(alpha_a_sun) - np.tan(alpha_w_sunPlanet))    
        CR_sunPlanet = Approach_CR_sunPlanet + Recess_CR_sunPlanet
        return Approach_CR_sunPlanet, Recess_CR_sunPlanet, CR_sunPlanet

    def contactRatio_planetRing(self):
        module1 = self.moduleBig
        module2 = self.moduleSmall
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr      = self.Nr

        _, alpha_w_planetRing = self.getWorkingPressureAngle()
        _, _, alpha_a_planet2, alpha_a_ring = self.getTipPressureAngle()

        Approach_CR_planetRing = -(Nr / (2 * np.pi)) * (np.tan(alpha_a_ring) - np.tan(alpha_w_planetRing))
        Recess_CR_planetRing   =   Np2 / (2 * np.pi) * (np.tan(alpha_a_planet2) - np.tan(alpha_w_planetRing)) 
        CR_planetRing = Approach_CR_planetRing + Recess_CR_planetRing
        return Approach_CR_planetRing, Recess_CR_planetRing, CR_planetRing

    def getEfficiency(self):
        module1 = self.moduleBig
        module2 = self.moduleSmall
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr      = self.Nr

        eps_sunPlanetA, eps_sunPlanetR, _ = self.contactRatio_sunPlanet()
        eps_planetRingA, eps_planetRingR, _ = self.contactRatio_planetRing()
        
        epsilon_sunPlanet = eps_sunPlanetA**2 + eps_sunPlanetR**2 - eps_sunPlanetA - eps_sunPlanetR + 1 
        epsilon_planetRing = eps_planetRingA**2 + eps_planetRingR**2 - eps_planetRingA - eps_planetRingR + 1 
        
        eff_SP = 1 - self.mu * np.pi * ((1 / Np1) + (1 / Ns)) * epsilon_sunPlanet
        eff_PR = 1 - self.mu * np.pi * ((1 / Np2) - (1 / Nr)) * epsilon_planetRing

        Numerator   = (Ns * Np2 + eff_SP * eff_PR * Np1 * Nr)
        Denominator = (Ns + Np1) * (Np2 + Np1)
        return Numerator / Denominator
    
    def getPCRadiusSunM(self): return ((self.Ns * self.moduleBig / 2) / 1000.0)
    def getPCRadiusPlanetBigM(self): return ((self.NpBig * self.moduleBig / 2) / 1000.0)
    def getPCRadiusPlanetSmallM(self): return ((self.NpSmall * self.moduleSmall / 2) / 1000.0)
    def getPCRadiusRingM(self): return ((self.Nr * self.moduleSmall / 2) / 1000.0)
    
    def getGearboxOuterDiaMaxM(self):
        Rs       = self.Ns * self.moduleBig * 0.5
        RpBig   = self.NpBig * self.moduleBig * 0.5
        return ((Rs  + 2*RpBig)*2/1000.0)

    def getPCRadiusSunMM(self): return ((self.Ns * self.moduleBig / 2))
    def getPCRadiusPlanetBigMM(self): return ((self.NpBig * self.moduleBig / 2))
    def getPCRadiusPlanetSmallMM(self): return ((self.NpSmall * self.moduleSmall / 2))
    def getPCRadiusRingMM(self): return ((self.Nr * self.moduleSmall) / 2)
    
    def getOuterRadiusRingM(self):
        ringPCDiameterMM = self.Nr * self.moduleSmall 
        ringPCRadiusMM = ringPCDiameterMM / 2
        return (ringPCRadiusMM + self.ringRadialWidthMM) / 1000.0

    def getCarrierRadiusM(self): return (((self.Ns + self.NpBig + self.NpBig/2)/2)*self.moduleBig) / 1000.0

    def setfwSunMM(self, fwSunMM): self.fwSunMM = fwSunMM
    def setfwPlanetBigMM(self, fwPlanetBigMM): self.fwPlanetBigMM = fwPlanetBigMM
    def setfwPlanetSmallMM(self, fwPlanetSmallMM): self.fwPlanetSmallMM = fwPlanetSmallMM
    def setfwRingMM(self, fwRingMM): self.fwRingMM = fwRingMM
    def setModuleBig(self, moduleBig): self.moduleBig = moduleBig
    def setModuleSmall(self, moduleSmall): self.moduleSmall = moduleSmall
    def setNs(self, Ns): self.Ns = Ns
    def setNpBig(self, NpBig): self.NpBig = NpBig
    def setNpSmall(self, NpSmall): self.NpSmall = NpSmall
    def setNr(self, Nr): self.Nr = Nr
    def setNumPlanet(self, numPlanet): self.numPlanet = numPlanet

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
        # Note: carrierWidthMM might need to be defined in __init__ or bypassed if not used in ICPG
        # print("Carrier width = ", getattr(self, 'carrierWidthMM', 0), " mm") 
        print("Ring radial width = ", self.ringRadialWidthMM, " mm")
        print("Pitch circle radius of sun gear = ", self.getPCRadiusSunM() * 1000, " mm")
        print("Pitch circle radius of Bigger planet gear = ", self.getPCRadiusPlanetBigM() * 1000, " mm")
        print("Pitch circle radius of Smaller planet gear = ", self.getPCRadiusPlanetSmallM() * 1000, " mm")
        print("Pitch circle radius of ring gear = ", self.getPCRadiusRingM() * 1000, " mm")
        print("Outer radius of ring gear = ", self.getOuterRadiusRingM() * 1000, " mm")
        # print("Carrier radius = ", self.getCarrierRadiusM() * 1000, " mm")
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
        # print("--------------------------------------------------------------------------")#=========================================================================
# Motor class
#=========================================================================
class motor:
    def __init__(self,
                 Kv=55, maxContinuousCurrent=20, ratedVoltage=48, power=4560, massKG=0.352,
                 statorODMM=81, statorIDMM=55, statorHeightMM=23.8, statorMountingHolesPCDMM=63,
                 rotorODMM=92.6, rotorIDMM=82.6, rotorHeightMM=21.6, rotorBottomIDMM=51,
                 rotorBottomThicknessMM=2.6, rotorCSKHeadUpperDiaMM=8, rotorMountHolePCDMM=62,
                 rotorMountHoleDiaMM=4, motorName="MotorR100"):

        # Basic parameters
        self.motorName = motorName
        self.Kv = Kv
        self.maxContinuousCurrent = maxContinuousCurrent
        self.ratedVoltage = ratedVoltage
        self.maxMotorPower = power
        self.massKG = massKG
        
        # Performance calculations
        self.maxMotorAngVelRPM = Kv * ratedVoltage
        self.maxMotorAngVelRadPerSec = self.maxMotorAngVelRPM * (2 * np.pi / 60)
        # Using the continuous current formula for accurate torque
        self.maxMotorTorque = self.maxContinuousCurrent / (self.Kv * 2 * np.pi / 60)
        
        # Stator Dimensions
        self.statorODMM = statorODMM
        self.statorIDMM = statorIDMM
        self.statorHeightMM = statorHeightMM
        self.statorMountingHolesPCDMM = statorMountingHolesPCDMM
        
        # Rotor Dimensions
        self.rotorODMM = rotorODMM
        self.rotorIDMM = rotorIDMM
        self.rotorHeightMM = rotorHeightMM
        self.rotorBottomIDMM = rotorBottomIDMM
        self.rotorBottomThicknessMM = rotorBottomThicknessMM
        self.rotorCSKHeadUpperDiaMM = rotorCSKHeadUpperDiaMM
        self.rotorMountHolePCDMM = rotorMountHolePCDMM
        self.rotorMountHoleDiaMM = rotorMountHoleDiaMM
        
        # Compatibility aliases (so your Actuator class works without modification)
        self.motorDiaMM = rotorODMM
        self.motorLengthMM = statorHeightMM

    #-------------------------------------------------------------------------
    # Getters (Required for compatibility with old Actuator code)
    #-------------------------------------------------------------------------
    def getMaxMotorAngVelRadPerSec(self): return self.maxMotorAngVelRadPerSec
    def getMaxMotorPower(self):           return self.maxMotorPower
    def getMaxMotorTorque(self):          return self.maxMotorTorque
    def getMassKG(self):                  return self.massKG
    def getDiaMM(self):                   return self.motorDiaMM
    def getLengthMM(self):                return self.motorLengthMM
    
    def getStatorODMM(self):              return self.statorODMM
    def getStatorIDMM(self):              return self.statorIDMM
    def getStatorHeightMM(self):          return self.statorHeightMM
    
    def getRotorODMM(self):               return self.rotorODMM
    def getRotorIDMM(self):               return self.rotorIDMM
    def getRotorHeightMM(self):           return self.rotorHeightMM

    #-------------------------------------------------------------------------
    # Print Function
    #-------------------------------------------------------------------------
    def printParameters(self):
        print("Maximum motor angular velocity = ", round(self.maxMotorAngVelRPM, 2), " RPM")
        print("Maximum motor power          = ", self.maxMotorPower, " W")
        print("Maximum continuous torque    = ", round(self.maxMotorTorque, 3), " Nm")
        print("Maximum motor angular velocity = ", round(self.maxMotorAngVelRadPerSec, 2), " rad/s")
        print("Mass of the motor            = ", self.massKG, " kg")
        print("---------------- Stator ----------------")
        print(" Outer Diameter of Stator = ", self.statorODMM, " mm")
        print(" Inner Diameter of Stator = ", self.statorIDMM, " mm")
        print(" Height of Stator         = ", self.statorHeightMM, " mm")
        print("---------------- Rotor -----------------")
        print(" Outer Diameter of Rotor  = ", self.rotorODMM, " mm")
        print(" Inner Diameter of Rotor  = ", self.rotorIDMM, " mm")
        print(" Height of Rotor          = ", self.rotorHeightMM, " mm")

#=========================================================================
# Actuator classes
#=========================================================================
class internalcompoundPlanetaryActuator:
    def __init__(self,
                 design_parameters,
                 motor_driver_params      = None,
                 motor                    = motor,
                 internalcompoundPlanetaryGearbox = internalcompoundPlanetaryGearbox,
                 FOS                      = 2.0,
                 serviceFactor            = 2.0,
                 maxGearboxDiameter       = 140.0,
                 stressAnalysisMethodName = "Lewis"):

        self.motor                    = motor
        self.internalcompoundPlanetaryGearbox = internalcompoundPlanetaryGearbox
        self.FOS                      = FOS
        self.serviceFactor            = serviceFactor
        self.maxGearboxDiameter       = maxGearboxDiameter
        self.stressAnalysisMethodName = stressAnalysisMethodName

        self.motorLengthMM           = self.motor.getStatorHeightMM()
        self.motorDiaMM              = self.motor.getRotorODMM()
        self.motorMassKG             = self.motor.getMassKG()
        self.MaxMotorTorque          = self.motor.getMaxMotorTorque()
        self.MaxMotorAngVelRPM       = self.motor.getMaxMotorAngVelRadPerSec()
        self.MaxMotorAngVelRadPerSec = self.motor.getMaxMotorAngVelRadPerSec()

        self.design_params     = design_parameters
        self.ringRadialWidthMM = self.internalcompoundPlanetaryGearbox.ringRadialWidthMM
        self.setVariables()

    def cost(self):
        massActuator  = self.getMassKG_3DP()
        effActuator   = self.internalcompoundPlanetaryGearbox.getEfficiency()
        widthActuator = self.internalcompoundPlanetaryGearbox.fwPlanetBigMM + self.internalcompoundPlanetaryGearbox.fwPlanetSmallMM
        cost = massActuator - 2 * effActuator + 0.2 * widthActuator
        return cost

    def setVariables(self):
        #--------- Optimisation variables ---------
        self.Ns         = self.internalcompoundPlanetaryGearbox.Ns
        self.Np_b       = self.internalcompoundPlanetaryGearbox.NpBig
        self.Np_s       = self.internalcompoundPlanetaryGearbox.NpSmall
        self.Nr         = self.internalcompoundPlanetaryGearbox.Nr
        self.num_planet = self.internalcompoundPlanetaryGearbox.numPlanet
        self.module     = self.internalcompoundPlanetaryGearbox.moduleBig

        #--------- Independent Constant variables ---------
        self.pressure_angle     = self.internalcompoundPlanetaryGearbox.getPressureAngleRad()
        self.pressure_angle_deg = self.internalcompoundPlanetaryGearbox.getPressureAngleRad() * 180 / np.pi # 20

        self.clearance_planet                   = self.design_params["clearance_planet"]
        self.standard_clearance_1_5mm           = self.design_params["standard_clearance_1_5mm"]
        self.standard_fillet_1_5mm              = self.design_params["standard_fillet_1_5mm"]
        self.standard_bearing_insertion_chamfer = self.design_params["standard_bearing_insertion_chamfer"]
        self.tight_clearance_3DP                = self.design_params["tight_clearance_3DP"]
        self.loose_clearance_3DP                = self.design_params["loose_clearance_3DP"]
        self.bearingIDClearance_3DP             = self.design_params["bearingIDClearanceMM"]

        self.motor_OD      = self.motorDiaMM
        self.motor_height  = self.motorLengthMM

        self.stator_OD                 = self.motor.getStatorODMM()
        self.stator_ID                 = self.motor.getStatorIDMM()
        self.stator_height             = self.motor.getStatorHeightMM()
        self.stator_mounting_holes_PCD = self.motor.statorMountingHolesPCDMM

        self.Rotor_OD                 = self.motor.getRotorODMM()
        self.Rotor_ID                 = self.motor.getRotorIDMM()
        self.Rotor_height             = self.motor.getRotorHeightMM()
        self.Rotor_bottom_ID          = self.motor.rotorBottomIDMM
        self.rotor_bottom_thickness   = self.motor.rotorBottomThicknessMM
        self.Rotor_csk_head_upper_dia = self.motor.rotorCSKHeadUpperDiaMM
        self.rotor_mount_hole_PCD     = self.motor.rotorMountHolePCDMM
        self.rotor_mount_hole_dia     = self.motor.rotorMountHoleDiaMM
        self.rotor_mount_hole_num     = getattr(self.motor, 'rotorMountHoleNum', 6)

        self.planet_pin_bolt_dia      = self.design_params["planet_pin_bolt_dia"]
        self.planet_shaft_dia         = self.design_params["planet_shaft_dia"]
        self.planet_shaft_step_offset = self.design_params["planet_shaft_step_offset"]
        self.planet_bearing_OD        = self.design_params["planet_bearing_OD"]
        self.planet_bearing_width     = self.design_params["planet_bearing_width"]
        self.planet_bore              = self.design_params["planet_bore"]

        self.sun_shaft_bearing_ID      = self.design_params["sun_shaft_bearing_ID"]
        self.sun_shaft_bearing_OD      = self.design_params["sun_shaft_bearing_OD"]
        self.sun_coupler_hub_thickness = self.design_params["sun_coupler_hub_thickness"]
        self.sun_shaft_bearing_width   = self.design_params["sun_shaft_bearing_width"]
        self.sun_central_bolt_dia      = self.design_params["sun_central_bolt_dia"]

        self.sun_bottom_casing_bearing_ID     = self.design_params["sun_bottom_casing_bearing_ID"]
        self.sun_bottom_casing_bearing_OD     = self.design_params["sun_bottom_casing_bearing_OD"]
        self.sun_bottom_casing_bearing_height = self.design_params["sun_bottom_casing_bearing_height"]
        self.sun_gear_rotor_nut_wrench_size   = self.design_params["sun_gear_rotor_nut_wrench_size"]
        self.sun_gear_rotor_nut_height        = self.design_params["sun_gear_rotor_nut_height"]

        self.bearing_retainer_thickness = self.design_params["bearing_retainer_thickness"]
        self.bearing_retainer_hole_dia  = self.design_params["bearing_retainer_hole_dia"]
        self.bearing_retainer_hole_num  = self.design_params["bearing_retainer_hole_num"]

        self.sec_carrier_thickness = self.design_params["sec_carrier_thickness"]
        self.carrier_trapezoidal_support_sun_offset                 = self.design_params["carrier_trapezoidal_support_sun_offset"]
        self.carrier_trapezoidal_support_hole_PCD_offset_bearing_ID = self.design_params["carrier_trapezoidal_support_hole_PCD_offset_bearing_ID"]
        self.carrier_trapezoidal_support_hole_dia                   = self.design_params["carrier_trapezoidal_support_hole_dia"]
        self.carrier_bearing_step_width                             = self.design_params["carrier_bearing_step_width"]

        self.Motor_case_thickness                = self.design_params["Motor_case_thickness"]
        self.ring_gear_thickness_mounting_casing = self.design_params["ring_gear_thickness_mounting_casing"]

        #--------- Dependent variables ---------
        self.h_a          = 1 * self.module
        self.h_b          = 1.25 * self.module
        self.h_f          = 1.25 * self.module
        self.clr_tip_root = self.h_f - self.h_a

        self.dp_s      = self.module * self.Ns
        self.db_s      = self.dp_s * np.cos((self.pressure_angle))
        self.alpha_s   = (np.sqrt(self.dp_s ** 2 - self.db_s ** 2) / self.db_s) * 180 / np.pi - self.pressure_angle_deg
        self.beta_s    = (360 / (4 * self.Ns) - self.alpha_s) * 2
        self.fw_s_calc = self.internalcompoundPlanetaryGearbox.fwSunMM

        self.dp_p_b    = self.module * self.Np_b
        self.db_p_b    = self.dp_p_b * np.cos((self.pressure_angle))
        self.alpha_p_b = (np.sqrt(self.dp_p_b ** 2 - self.db_p_b ** 2) / self.db_p_b) * 180 / np.pi - self.pressure_angle_deg
        self.beta_p_b  = (360 / (4 * self.Np_b) - self.alpha_p_b) * 2
        self.fw_p_b    = self.internalcompoundPlanetaryGearbox.fwPlanetBigMM
        
        self.dp_r    = self.module * self.Nr
        self.db_r    = self.dp_r * np.cos((self.pressure_angle))
        self.alpha_r = (np.sqrt(self.dp_r ** 2 - self.db_r ** 2) / self.db_r) * 180 / np.pi - self.pressure_angle_deg
        self.beta_r  = (360 / (4 * self.Nr) + self.alpha_r) * 2
        self.fw_r    = self.internalcompoundPlanetaryGearbox.fwRingMM

        self.dp_p_s    = self.module * self.Np_s
        self.db_p_s    = self.dp_p_s * np.cos((self.pressure_angle))
        self.alpha_p_s = (np.sqrt(self.dp_p_s ** 2 - self.db_p_s ** 2) / self.db_p_s) * 180 / np.pi - self.pressure_angle_deg
        self.beta_p_s  = (360 / (4 * self.Np_s) - self.alpha_p_s) * 2
        self.fw_p_s    = self.fw_r + self.clearance_planet

        planet_pin_bolt = nuts_and_bolts_dimensions(bolt_dia=self.planet_pin_bolt_dia, bolt_type="socket_head")
        self.planet_pin_socket_head_dia  = planet_pin_bolt.bolt_head_dia
        self.planet_pin_bolt_wrench_size = planet_pin_bolt.nut_width_across_flats

        sun_central_bolt = nuts_and_bolts_dimensions(bolt_dia=self.sun_central_bolt_dia, bolt_type="socket_head")
        self.sun_central_bolt_socket_head_dia = sun_central_bolt.bolt_head_dia

        sun_hub_dia_calc = (self.rotor_mount_hole_PCD + self.rotor_mount_hole_dia + self.standard_clearance_1_5mm * 4)
        cap = self.Rotor_OD - self.standard_clearance_1_5mm * 2
        self.sun_hub_dia = cap if sun_hub_dia_calc > self.Rotor_OD else sun_hub_dia_calc

        self.carrier_PCD = self.module * (self.Ns + self.Np_b)
        bearing_id_calc = self.carrier_PCD + self.bearingIDClearance_3DP
        Bearings = bearings_discrete(bearing_id_calc)
        self.bearing_ID     = Bearings.getBearingIDMM()
        self.bearing_OD     = Bearings.getBearingODMM()
        self.bearing_height = Bearings.getBearingWidthMM()

        carrier_trap_hole = nuts_and_bolts_dimensions(bolt_dia=self.carrier_trapezoidal_support_hole_dia, bolt_type="socket_head")
        self.carrier_trapezoidal_support_hole_socket_head_dia = carrier_trap_hole.bolt_head_dia
        self.carrier_trapezoidal_support_hole_wrench_size     = carrier_trap_hole.nut_width_across_flats

        fw_s_used_calc = (self.standard_clearance_1_5mm / 2 + self.sec_carrier_thickness + self.clearance_planet + self.fw_p_s + self.fw_p_b)
        fw_s_used_floor = self.stator_height + self.rotor_bottom_thickness
        stator_radial_clearance = (self.stator_ID - self.bearing_OD) / 2
        floor_applies = stator_radial_clearance < self.standard_clearance_1_5mm * 2

        if floor_applies and fw_s_used_calc < fw_s_used_floor:
            self.fw_s_used = fw_s_used_floor
        else:
            self.fw_s_used = fw_s_used_calc

        self.actuator_width = self.fw_s_used + self.bearing_height + self.sun_coupler_hub_thickness + self.standard_clearance_1_5mm*3.5 + self.sun_bottom_casing_bearing_height+ self.bearing_retainer_thickness
        self.ring_OD = self.stator_ID

    def _equation_lines(self):
        return [
            f'"Ns"= {self.Ns}\n',
            f'"Np_b"= {self.Np_b}\n',
            f'"Np_s"= {self.Np_s}\n',
            f'"Nr"= {self.Nr}\n',
            f'"num_planet"= {self.num_planet}\n',
            f'"module"= {self.module}\n',
            f'"pressure_angle"= {self.pressure_angle_deg}\n',
            f'"h_a"= {self.h_a}\n',
            f'"h_b"= {self.h_b}\n',
            f'"clr_tip_root"= {self.clr_tip_root}\n',
            f'"dp_s"= {self.dp_s}\n',
            f'"db_s"= {self.db_s}\n',
            f'"fw_s_calc"= {self.fw_s_calc}\n',
            f'"alpha_s"= {self.alpha_s}\n',
            f'"beta_s"= {self.beta_s}\n',
            f'"dp_p_b"= {self.dp_p_b}\n',
            f'"db_p_b"= {self.db_p_b}\n',
            f'"fw_p_s"= {self.fw_p_s}\n',
            f'"alpha_p_b"= {self.alpha_p_b}\n',
            f'"beta_p_b"= {self.beta_p_b}\n',
            f'"h_f"= {self.h_f}\n',
            f'"dp_r"= {self.dp_r}\n',
            f'"db_r"= {self.db_r}\n',
            f'"fw_r"= {self.fw_r}\n',
            f'"alpha_r"= {self.alpha_r}\n',
            f'"beta_r"= {self.beta_r}\n',
            f'"bearing_ID"= {self.bearing_ID}\n',
            f'"bearing_OD"= {self.bearing_OD}\n',
            f'"bearing_height"= {self.bearing_height}\n',
            f'"clearance_planet"= {self.clearance_planet}\n',
            f'"sec_carrier_thickness"= {self.sec_carrier_thickness}\n',
            f'"sun_coupler_hub_thickness"= {self.sun_coupler_hub_thickness}\n',
            f'"rotor_mount_hole_PCD"= {self.rotor_mount_hole_PCD}\n',
            f'"rotor_mount_hole_dia"= {self.rotor_mount_hole_dia}\n',
            f'"rotor_mount_hole_num"= {self.rotor_mount_hole_num}\n',
            f'"planet_pin_bolt_dia"= {self.planet_pin_bolt_dia}\n',
            f'"planet_pin_socket_head_dia"= {self.planet_pin_socket_head_dia}\n',
            f'"carrier_PCD"= {self.carrier_PCD}\n',
            f'"planet_shaft_dia"= {self.planet_shaft_dia}\n',
            f'"planet_shaft_step_offset"= {self.planet_shaft_step_offset}\n',
            f'"carrier_trapezoidal_support_sun_offset"= {self.carrier_trapezoidal_support_sun_offset}\n',
            f'"carrier_trapezoidal_support_hole_PCD_offset_bearing_ID"= {self.carrier_trapezoidal_support_hole_PCD_offset_bearing_ID}\n',
            f'"carrier_trapezoidal_support_hole_dia"= {self.carrier_trapezoidal_support_hole_dia}\n',
            f'"carrier_trapezoidal_support_hole_socket_head_dia"= {self.carrier_trapezoidal_support_hole_socket_head_dia}\n',
            f'"carrier_bearing_step_width"= {self.carrier_bearing_step_width}\n',
            f'"standard_clearance_1_5mm"= {self.standard_clearance_1_5mm}\n',
            f'"standard_fillet_1_5mm"= {self.standard_fillet_1_5mm}\n',
            f'"sun_shaft_bearing_OD"= {self.sun_shaft_bearing_OD}\n',
            f'"sun_shaft_bearing_width"= {self.sun_shaft_bearing_width}\n',
            f'"sun_shaft_bearing_ID"= {self.sun_shaft_bearing_ID}\n',
            f'"standard_bearing_insertion_chamfer"= {self.standard_bearing_insertion_chamfer}\n',
            f'"carrier_trapezoidal_support_hole_wrench_size"= {self.carrier_trapezoidal_support_hole_wrench_size}\n',
            f'"planet_pin_bolt_wrench_size"= {self.planet_pin_bolt_wrench_size}\n',
            f'"planet_bearing_OD"= {self.planet_bearing_OD}\n',
            f'"planet_bearing_width"= {self.planet_bearing_width}\n',
            f'"planet_bore"= {self.planet_bore}\n',
            f'"sun_hub_dia"= {self.sun_hub_dia}\n',
            f'"sun_central_bolt_dia"= {self.sun_central_bolt_dia}\n',
            f'"sun_central_bolt_socket_head_dia"= {self.sun_central_bolt_socket_head_dia}\n',
            f'"fw_p_b"= {self.fw_p_b}\n',
            f'"fw_s_used"= {self.fw_s_used}\n',
            f'"bearing_retainer_thickness"= {self.bearing_retainer_thickness}\n',
            f'"dp_p_s"= {self.dp_p_s}\n',
            f'"db_p_s"= {self.db_p_s}\n',
            f'"alpha_p_s"= {self.alpha_p_s}\n',
            f'"beta_p_s"= {self.beta_p_s}\n',
            f'"tight_clearance_3DP"= {self.tight_clearance_3DP}\n',
            f'"loose_clearance_3DP"= {self.loose_clearance_3DP}\n',
            f'"sun_bottom_casing_bearing_ID"= {self.sun_bottom_casing_bearing_ID}\n',
            f'"sun_bottom_casing_bearing_OD"= {self.sun_bottom_casing_bearing_OD}\n',
            f'"sun_bottom_casing_bearing_height"= {self.sun_bottom_casing_bearing_height}\n',
            f'"sun_gear_rotor_nut_wrench_size"= {self.sun_gear_rotor_nut_wrench_size}\n',
            f'"sun_gear_rotor_nut_height"= {self.sun_gear_rotor_nut_height}\n',
            f'"stator_OD"= {self.stator_OD}\n',
            f'"stator_ID"= {self.stator_ID}\n',
            f'"stator_height"= {self.stator_height}\n',
            f'"stator_mounting_holes_PCD"= {self.stator_mounting_holes_PCD}\n',
            f'"bearing_retainer_hole_dia"= {self.bearing_retainer_hole_dia}\n',
            f'"bearing_retainer_hole_num"= {self.bearing_retainer_hole_num}\n',
            f'"Rotor_ID"= {self.Rotor_ID}\n',
            f'"Rotor_OD"= {self.Rotor_OD}\n',
            f'"Rotor_height"= {self.Rotor_height}\n',
            f'"Rotor_bottom_ID"= {self.Rotor_bottom_ID}\n',
            f'"rotor_bottom_thickness"= {self.rotor_bottom_thickness}\n',
            f'"Rotor_csk_head_upper_dia"= {self.Rotor_csk_head_upper_dia}\n',
            f'"ring_gear_thickness_mounting_casing"= {self.ring_gear_thickness_mounting_casing}\n',
            f'"motor_casing_thickness"= {self.Motor_case_thickness}\n',
        ]

# -------------------------------------------------------------------------
    # RESTORED: Your original three-print-function architecture
    # -------------------------------------------------------------------------
    def printParameters(self):
        print("Ns = ", self.Ns)
        print("Np_b = ", self.Np_b)
        print("Np_s = ", self.Np_s)
        print("Nr = ", self.Nr)
        print("Module = ", self.module)
        print("Number of planets = ", self.num_planet)
        print("Face width of sun gear = ", round(self.fw_s_used, 2), " mm")
        print("Face width of Big planet gear = ", round(self.fw_p_b, 2), " mm")
        print("Face width of Small planet gear = ", round(self.fw_p_s, 2), " mm")
        print("Mass of the gearbox = ", round(self.gearbox_mass_kg, 3), " kg")
        print("Efficiency = ", round(self.getEfficiency(), 4))
        print("--------------------------------------------------------------------------")

    def printParametersLess(self):
        vars = [self.module, self.Ns, self.Np_b, self.Np_s, self.Nr, self.num_planet]
        print("[m, Ns, NpB, NpS, Nr, numPl]:", vars)
        print("Gear ratio = ", self.gearRatio())
        print("Efficiency = ", round(self.getEfficiency(), 4))
        print("Mass (gearbox, kg) = ", round(self.gearbox_mass_kg, 3), " kg")
        print("--------------------------------------------------------------------------")

    def printVolumeAndMassParameters(self):
        print("--- Mass Breakdown (kg) ---")
        print("Sun Mass:          ", round(self.sun_gear_mass_kg, 4))
        print("Planet Mass:       ", round(self.planet_mass_kg, 4))
        print("Ring Mass:         ", round(self.ring_gear_mass_kg, 4))
        print("Carrier Mass:      ", round(self.carrier_mass_kg, 4))
        print("Motor Casing Mass: ", round(self.motor_casing_mass_kg, 4))
        print("Bearing Mass:      ", round(self.bearing_mass_kg, 4))
        print("--------------------------------------------------------------------------")
        
        # The specific lines isolating the masses
        total_actuator_mass = self.gearbox_mass_kg + self.motorMassKG
        
        print("GEARBOX ONLY MASS: ", round(self.gearbox_mass_kg, 3), " kg")
        print("MOTOR ONLY MASS:   ", round(self.motorMassKG, 3), " kg")
        print("TOTAL ACTUATOR:    ", round(total_actuator_mass, 3), " kg")
        print("--------------------------------------------------------------------------")



    def genEquationFile(self, motor_name="NO_MOTOR", gearRatioLL=0.0, gearRatioUL=0.0):
        self.setVariables()
        lines = self._equation_lines()
        
        path_sw = os.path.join(os.path.dirname(__file__), 'CADs', 'ICPG', 'Equation_Files',
                               motor_name, f'icpg_equations_{gearRatioLL}_{gearRatioUL}.txt')
        os.makedirs(os.path.dirname(path_sw), exist_ok=True)
        with open(path_sw, 'w') as f:
            f.writelines(lines)

        path_os = os.path.join(os.path.dirname(__file__), 'CADs', 'ICPG', 'Equation_Files',
                               motor_name, f'icpg_equations_{gearRatioLL}_{gearRatioUL}_onshape.txt')
        with open(path_os, 'w') as f:
            f.writelines(lines)

    def genEquationFile_editCADdirectly(self):
        self.setVariables()
        lines = self._equation_lines()
        
        path_sw = os.path.join(os.path.dirname(__file__), 'CADs', 'ICPG', 'icpg_equations.txt')
        os.makedirs(os.path.dirname(path_sw), exist_ok=True)
        with open(path_sw, 'w') as f:
            f.writelines(lines)

        path_os = os.path.join(os.path.dirname(__file__), 'CADs', 'ICPG', 'icpg_equations_onshape.txt')
        with open(path_os, 'w') as f:
            f.writelines(lines)

    #--------------------------------------------
    # Gear tooth stress analysis
    #--------------------------------------------
    def getToothForces(self, constraintCheck=True):
        if constraintCheck:
            # Check if the constraints are satisfied
            if not self.internalcompoundPlanetaryGearbox.geometricConstraint():
                print("Geometric constraint not satisfied")
                return
            if not self.internalcompoundPlanetaryGearbox.meshingConstraint():
                print("Meshing constraint not satisfied")
                return
            if not self.internalcompoundPlanetaryGearbox.noPlanetInterferenceConstraint():
                print("No planet interference constraint not satisfied")
                return

        Ns          = self.internalcompoundPlanetaryGearbox.Ns
        NpBig       = self.internalcompoundPlanetaryGearbox.NpBig
        NpSmall     = self.internalcompoundPlanetaryGearbox.NpSmall
        Nr          = self.internalcompoundPlanetaryGearbox.Nr
        numPlanet   = self.internalcompoundPlanetaryGearbox.numPlanet
        moduleBig   = self.internalcompoundPlanetaryGearbox.moduleBig
        moduleSmall = self.internalcompoundPlanetaryGearbox.moduleSmall

        Rs_Mt = self.internalcompoundPlanetaryGearbox.getPCRadiusSunM()
        RpBig_Mt = self.internalcompoundPlanetaryGearbox.getPCRadiusPlanetBigM()
        RpSmall_Mt = self.internalcompoundPlanetaryGearbox.getPCRadiusPlanetSmallM()
        Rr_Mt = self.internalcompoundPlanetaryGearbox.getPCRadiusRingM()

        wSun     = self.motor.getMaxMotorAngVelRadPerSec()
        wPlanet  = (-Ns / (NpBig + NpSmall) ) * wSun
        wCarrier = wSun/self.internalcompoundPlanetaryGearbox.gearRatio()

        Ft_sp = (self.serviceFactor*self.motor.getMaxMotorTorque()) / (numPlanet * Rs_Mt)
        Ft_rp = ((self.serviceFactor*self.motor.getMaxMotorTorque()) * RpBig_Mt) / (numPlanet * Rs_Mt * RpSmall_Mt)

        Ft = [Ft_sp, Ft_rp]
        return Ft

    def lewisStressAnalysisMinFacewidth(self):
        # Check if the constraints are satisfied
        if not self.internalcompoundPlanetaryGearbox.geometricConstraint():
            print("Geometric constraint not satisfied")
            return
        if not self.internalcompoundPlanetaryGearbox.meshingConstraint():
            print("Meshing constraint not satisfied")
            return
        if not self.internalcompoundPlanetaryGearbox.noPlanetInterferenceConstraint():
            print("No planet interference constraint not satisfied")
            return

        Ns          = self.internalcompoundPlanetaryGearbox.Ns
        NpBig       = self.internalcompoundPlanetaryGearbox.NpBig
        NpSmall     = self.internalcompoundPlanetaryGearbox.NpSmall
        Nr          = self.internalcompoundPlanetaryGearbox.Nr
        numPlanet   = self.internalcompoundPlanetaryGearbox.numPlanet
        moduleBig   = self.internalcompoundPlanetaryGearbox.moduleBig
        moduleSmall = self.internalcompoundPlanetaryGearbox.moduleSmall

        wSun     = self.motor.getMaxMotorAngVelRadPerSec()
        wPlanet  = (-Ns / (NpBig + NpSmall) ) * wSun
        wCarrier = wSun/self.internalcompoundPlanetaryGearbox.gearRatio()

        [Ft_sp, Ft_rp] = self.getToothForces(constraintCheck=False)

        ySun         = 0.154 - 0.912/Ns
        yPlanetBig   = 0.154 - 0.912/NpBig
        yPlanetSmall = 0.154 - 0.912/NpSmall
        yRing        = 0.154 - 0.912/Nr

        V_sp = (self.internalcompoundPlanetaryGearbox.getPCRadiusSunM() * wSun)
        V_rp = (wCarrier*(self.internalcompoundPlanetaryGearbox.getPCRadiusSunM() + self.internalcompoundPlanetaryGearbox.getPCRadiusPlanetBigM()) + 
                wPlanet*(self.internalcompoundPlanetaryGearbox.getPCRadiusPlanetSmallM()))
        
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
        bMin_sun         = (self.FOS * Ft_sp / (self.internalcompoundPlanetaryGearbox.maxGearAllowableStressPa * ySun * Kv_sun * P_big)) # m
        bMin_planetBig   = (self.FOS * Ft_sp / (self.internalcompoundPlanetaryGearbox.maxGearAllowableStressPa * yPlanetBig * Kv_planetBig * P_big))
        bMin_planetSmall = (self.FOS * Ft_rp / (self.internalcompoundPlanetaryGearbox.maxGearAllowableStressPa * yPlanetSmall * Kv_planetSmall * P_small))
        bMin_ring        = (self.FOS * Ft_rp / (self.internalcompoundPlanetaryGearbox.maxGearAllowableStressPa * yRing * Kv_ring * P_small))

        if bMin_ring < bMin_planetSmall:
            bMin_ring = bMin_planetSmall
        else:
            bMin_planetSmall = bMin_ring

        self.internalcompoundPlanetaryGearbox.setfwSunMM(bMin_sun*1000)
        self.internalcompoundPlanetaryGearbox.setfwPlanetBigMM(bMin_planetBig*1000)
        self.internalcompoundPlanetaryGearbox.setfwPlanetSmallMM(bMin_planetSmall*1000)
        self.internalcompoundPlanetaryGearbox.setfwRingMM(bMin_ring*1000)

        # print(f"Lewis:")
        # print(f"bMin_planetSmall = {bMin_planetSmall}")
        # print(f"bMin_planetBig = {bMin_planetBig}")
        # print(f"bMin_sun = {bMin_sun}")
        # print(f"bMin_ring = {bMin_ring}")

    def mitStressAnalysisMinFacewidth(self):
        if not self.internalcompoundPlanetaryGearbox.geometricConstraint():
            print("Geometric constraint not satisfied")
            return
        if not self.internalcompoundPlanetaryGearbox.meshingConstraint():
            print("Meshing constraint not satisfied")
            return
        if not self.internalcompoundPlanetaryGearbox.noPlanetInterferenceConstraint():
            print("No planet interference constraint not satisfied")
            return

        Ns          = self.internalcompoundPlanetaryGearbox.Ns
        NpBig       = self.internalcompoundPlanetaryGearbox.NpBig
        NpSmall     = self.internalcompoundPlanetaryGearbox.NpSmall
        Nr          = self.internalcompoundPlanetaryGearbox.Nr
        numPlanet   = self.internalcompoundPlanetaryGearbox.numPlanet
        moduleBig   = self.internalcompoundPlanetaryGearbox.moduleBig
        moduleSmall = self.internalcompoundPlanetaryGearbox.moduleSmall

        wSun     = self.motor.getMaxMotorAngVelRadPerSec()
        wPlanet  = (-Ns / (NpBig + NpSmall) ) * wSun
        wCarrier = wSun/self.internalcompoundPlanetaryGearbox.gearRatio()

        [Ft_sp, Ft_rp] = self.getToothForces(constraintCheck=False)

        # Lewis static load capacity
        _,_,CR_SP = self.internalcompoundPlanetaryGearbox.contactRatio_sunPlanet()
        _,_,CR_PR = self.internalcompoundPlanetaryGearbox.contactRatio_planetRing()

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
        bMin_sun_mit         = (self.FOS * Ft_sp * qe1 * qk1 / (self.internalcompoundPlanetaryGearbox.maxGearAllowableStressPa * moduleBig * 0.001)) # m
        bMin_planetBig_mit   = (self.FOS * Ft_sp * qe1 * qk1 / (self.internalcompoundPlanetaryGearbox.maxGearAllowableStressPa * moduleBig * 0.001))
        bMin_planetSmall_mit = (self.FOS * Ft_rp * qe2 * qk2 / (self.internalcompoundPlanetaryGearbox.maxGearAllowableStressPa * moduleSmall * 0.001))
        bMin_ring_mit        = (self.FOS * Ft_rp * qe2 * qk2 / (self.internalcompoundPlanetaryGearbox.maxGearAllowableStressPa * moduleSmall * 0.001))

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


        self.internalcompoundPlanetaryGearbox.setfwSunMM         ( bMin_sun_mit         * 1000)
        self.internalcompoundPlanetaryGearbox.setfwPlanetBigMM   ( bMin_planetBig_mit   * 1000)
        self.internalcompoundPlanetaryGearbox.setfwPlanetSmallMM ( bMin_planetSmall_mit * 1000)
        self.internalcompoundPlanetaryGearbox.setfwRingMM        ( bMin_ring_mit        * 1000)

        return bMin_sun_mitMM, bMin_planetBig_mitMM, bMin_planetSmall_mitMM, bMin_ring_mitMM

    def AGMAStressAnalysisMinFacewidth(self):
        # Check if the constraints are satisfied
        if not self.internalcompoundPlanetaryGearbox.geometricConstraint():
            print("Geometric constraint not satisfied")
            return
        if not self.internalcompoundPlanetaryGearbox.meshingConstraint():
            print("Meshing constraint not satisfied")
            return
        if not self.internalcompoundPlanetaryGearbox.noPlanetInterferenceConstraint():
            print("No planet interference constraint not satisfied")
            return

        Ns          = self.internalcompoundPlanetaryGearbox.Ns
        NpBig       = self.internalcompoundPlanetaryGearbox.NpBig
        NpSmall     = self.internalcompoundPlanetaryGearbox.NpSmall
        Nr          = self.internalcompoundPlanetaryGearbox.Nr
        numPlanet   = self.internalcompoundPlanetaryGearbox.numPlanet
        moduleBig   = self.internalcompoundPlanetaryGearbox.moduleBig
        moduleSmall = self.internalcompoundPlanetaryGearbox.moduleSmall

        wSun     = self.motor.getMaxMotorAngVelRadPerSec()
        wPlanet  = (-Ns / (NpBig + NpSmall) ) * wSun
        wCarrier = wSun/self.internalcompoundPlanetaryGearbox.gearRatio()

        pressureAngle = self.internalcompoundPlanetaryGearbox.pressureAngleDEG

        [Wt_sp, Wt_rp] = self.getToothForces(constraintCheck=False)

        # T Krishna Rao - Design of Machine Elements - II pg.191
        # Modified Lewis Form Factor Y = pi*y for pressure angle = 20
        Y_sun         = (0.154 - 0.912 / Ns) * np.pi
        Y_planetBig   = (0.154 - 0.912 / NpBig) * np.pi
        Y_planetSmall = (0.154 - 0.912 / NpSmall) * np.pi
        Y_ring        = (0.154 - 0.912 / Nr) * np.pi

        V_sp = abs(self.internalcompoundPlanetaryGearbox.getPCRadiusSunM() * wSun)
        V_rp = abs(wCarrier*(self.internalcompoundPlanetaryGearbox.getPCRadiusSunM() + self.internalcompoundPlanetaryGearbox.getPCRadiusPlanetBigM()) + 
                wPlanet*(self.internalcompoundPlanetaryGearbox.getPCRadiusPlanetSmallM()))
        
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
        bMin_planetSmall = (self.FOS * Wt_rp * Kv_planetSmall * Ks * Kh_planet * Kb)/(moduleSmall * Yj_planetSmall * self.internalcompoundPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        bMin_planetBig = (self.FOS * Wt_sp * Kv_planetBig * Ks * Kh_planet * Kb)/(moduleBig * Yj_planetBig * self.internalcompoundPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        bMin_sun = (self.FOS * Wt_sp * Kv_sun * Ks * Kh_sun * Kb) / (moduleBig * Yj_sun * self.internalcompoundPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        bMin_ring = (self.FOS * Wt_rp * Kv_ring * Ks * Kh_ring * Kb) / (moduleSmall * Yj_ring * self.internalcompoundPlanetaryGearbox.maxGearAllowableStressPa * 0.001)

        if bMin_ring < bMin_planetSmall:
            bMin_ring = bMin_planetSmall
        else:
            bMin_planetSmall = bMin_ring

        self.internalcompoundPlanetaryGearbox.setfwSunMM(bMin_sun*1000)
        self.internalcompoundPlanetaryGearbox.setfwPlanetBigMM(bMin_planetBig*1000)
        self.internalcompoundPlanetaryGearbox.setfwPlanetSmallMM(bMin_planetSmall*1000)
        self.internalcompoundPlanetaryGearbox.setfwRingMM(bMin_ring*1000)

    def updateFacewidth(self):
        if self.stressAnalysisMethodName == "Lewis":
            self.lewisStressAnalysisMinFacewidth()
        elif self.stressAnalysisMethodName == "AGMA":
            self.AGMAStressAnalysisMinFacewidth()
        elif self.stressAnalysisMethodName == "MIT":
            self.mitStressAnalysisMinFacewidth()

    def getMassKG_3DP(self):
        self.setVariables() # Refresh dependencies first

        densitySteel = self.internalcompoundPlanetaryGearbox.densityGears 
        densityAlum  = self.internalcompoundPlanetaryGearbox.densityStructure

        fwSunM         = self.fw_s_used / 1000
        fwPlanetBigM   = self.fw_p_b    / 1000
        fwPlanetSmallM = self.fw_p_s    / 1000
        fwRingM        = (self.fw_r + self.standard_clearance_1_5mm * 2) / 1000

        # PLANET GEAR
        Rp_big              = (self.Np_b * self.module / 2) / 1000
        Rp_small            = (self.Np_s * self.module / 2) / 1000
        Rp_bore             = (self.planet_bore / 2) / 1000
        Rp_bearing_OD       = (self.planet_bearing_OD/2)/1000
        fwBearingPlanet     = (self.planet_bearing_width)/1000

        planetBigVolume     = math.pi * fwPlanetBigM   * Rp_big   ** 2
        planetSmallVolume   = math.pi * fwPlanetSmallM * Rp_small ** 2
        planetBoreVolume    = math.pi * (fwPlanetBigM + fwPlanetSmallM) * Rp_bore ** 2
        planetBearingVolume = math.pi * fwBearingPlanet * (Rp_bearing_OD**2 - Rp_bore**2)
        planetVolume        = planetBigVolume + planetSmallVolume - planetBoreVolume - 2 * planetBearingVolume

        # SUN GEAR
        R_sun               = (self.Ns * self.module / 2) / 1000
        R_sun_base_coupler  = (self.sun_hub_dia / 2) / 1000
        R_sun_bore          = (self.sun_central_bolt_dia / 2) / 1000
        SunBaseThicknessM   = self.sun_coupler_hub_thickness / 1000

        sunVolume           = math.pi * fwSunM          * R_sun            ** 2
        sunBaseVolume       = math.pi * SunBaseThicknessM * R_sun_base_coupler ** 2
        sunBoreVolume       = math.pi * (fwSunM + SunBaseThicknessM) * R_sun_bore ** 2
        sunGearVolume       = sunVolume + sunBaseVolume - sunBoreVolume

        # SECONDARY CARRIER
        R_sec_carrier_small = ( (self.carrier_PCD / 2)
                               - (self.planet_shaft_dia + self.planet_shaft_step_offset) / 2
                               - self.standard_clearance_1_5mm / 2 ) / 1000
        R_sec_carrier_big   = (self.bearing_ID / 2) / 1000
        secCarrierThicknessM = self.sec_carrier_thickness / 1000
        secCarrierVolume    = ( math.pi * secCarrierThicknessM
                              * (R_sec_carrier_big ** 2 - R_sec_carrier_small ** 2) )

        # MAIN CARRIER
        Rc                        = (self.bearing_ID / 2) / 1000
        Rc_planet_cylinder        = (((self.Np_b * self.module) / 2)*(2/5)) / 1000
        Rc_Sun_cylinder           = (((self.Ns * self.module)/2)+self.carrier_trapezoidal_support_sun_offset/2)/1000
        carrierWidthM             = fwPlanetBigM + fwPlanetSmallM 
        carrierCylinderPlanetWidthM = fwPlanetBigM + fwPlanetSmallM
        
        carrierVolume             = math.pi * carrierWidthM              * Rc                 ** 2
        carrierCylinderPlanetVol  = math.pi * carrierCylinderPlanetWidthM * Rc_planet_cylinder ** 2
        #carrierCylinderSunVol     = math.pi * carrierCylinderPlanetWidthM * Rc_Sun_cylinder ** 2 
        carrierTotalVolume        = carrierVolume - 3* carrierCylinderPlanetVol 

        # RING GEAR
        Rr                        = (self.Nr * self.module / 2) / 1000
        Rr_outer                  = (self.stator_ID / 2) / 1000
        MountingThicknessRingGear = self.ring_gear_thickness_mounting_casing / 1000
        Rr_mounting_outer         = ((self.Rotor_OD + self.standard_clearance_1_5mm + self.Motor_case_thickness * 2) / 2) / 1000
        Rr_bearing_support_inner  = ((self.bearing_OD / 2)) / 1000
        Rr_bearing_support_outer  = ((self.stator_mounting_holes_PCD + self.standard_clearance_1_5mm * 5) / 2) / 1000

        ringVolume                = math.pi * (fwRingM-(self.fw_s_used - self.rotor_bottom_thickness - self.stator_height - self.ring_gear_thickness_mounting_casing)/1000) * (Rr_outer ** 2 - Rr ** 2)
        ringMountingVolume        = math.pi * MountingThicknessRingGear  * (Rr_mounting_outer ** 2   - Rr_outer                 ** 2)
        ringBearingSupportVolume  = math.pi * ( (self.bearing_height + self.tight_clearance_3DP ) / 1000 ) * (Rr_bearing_support_outer ** 2 - Rr_bearing_support_inner ** 2)
        ringMiddleSectionVolume   = math.pi * ((self.carrier_bearing_step_width + self.clearance_planet + self.fw_s_used - self.rotor_bottom_thickness - self.stator_height - self.ring_gear_thickness_mounting_casing)/1000) * (Rr_bearing_support_outer ** 2 - Rr ** 2)
        ringGearVolume            = ringVolume + ringMountingVolume + ringBearingSupportVolume + ringMiddleSectionVolume

        # MOTOR CASING
        R_motor_casing_inner      = ((self.Rotor_OD + self.standard_clearance_1_5mm) / 2) / 1000
        R_motor_casing_outer      = R_motor_casing_inner + self.Motor_case_thickness / 1000
        R_motor_casing_bearing    = (self.sun_bottom_casing_bearing_OD / 2) / 1000
        Motor_casing_height_top   = ((self.rotor_bottom_thickness + self.stator_height + self.sun_coupler_hub_thickness
                                      + self.loose_clearance_3DP + self.standard_clearance_1_5mm)) / 1000
        Motor_casing_thick_bottom = ((self.sun_bottom_casing_bearing_height + self.standard_clearance_1_5mm) ) / 1000

        motorCasingVolume = (
            math.pi * Motor_casing_height_top * (R_motor_casing_outer**2 - R_motor_casing_inner**2)
            + math.pi * Motor_casing_thick_bottom * (R_motor_casing_outer**2 - R_motor_casing_bearing**2)
            + 6 * math.pi * (Motor_casing_height_top+Motor_casing_thick_bottom) * ((3.5/1000)**2 - (1.5/1000)**2 )
        )

        # BEARING MASS
        Bearings = bearings_discrete(self.bearing_ID)
        bearingMass = self.num_planet * Bearings.getBearingMassKG()
        self.bearing_mass = bearingMass 


        planetMass      = self.num_planet * planetVolume    * densitySteel
        sunGearMass     = sunGearVolume                     * densitySteel
        ringGearMass    = ringGearVolume                    * densitySteel
        secCarrierMass  = secCarrierVolume                  * densityAlum
        carrierMass     = carrierTotalVolume                * densityAlum
        motorCasingMass = motorCasingVolume                 * densityAlum
      
        gearbox_mass_kg = ( planetMass + sunGearMass + ringGearMass
                            + secCarrierMass + carrierMass
                            + motorCasingMass + bearingMass ) 
        
        self.planet_mass_kg       = planetMass
        self.sun_gear_mass_kg     = sunGearMass
        self.ring_gear_mass_kg    = ringGearMass
        self.sec_carrier_mass_kg  = secCarrierMass
        self.carrier_mass_kg      = carrierMass
        self.motor_casing_mass_kg = motorCasingMass
        self.gearbox_mass_kg      = gearbox_mass_kg 
        self.total_sum_except_motor_and_baering = planetMass + sunGearMass +  ringGearMass + secCarrierMass + carrierMass + motorCasingMass

        return gearbox_mass_kg + self.motorMassKG


    def print_mass_of_parts_3DP(self):
        print(f"Motor mass:                     {1000 * self.motorMassKG:.2f} g")
        print("---------------------------------------------------")



#------------------------------------------------------------
# Class: Optimization of Compound Planetary Actuator
#------------------------------------------------------------
class optimizationInternalCompoundPlanetaryActuator:
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
        self.UsePSCasVariable        = 1 

        self.gear_standard_parameters = gear_standard_parameters
        self.design_parameters        = design_parameters
        self.gearRatioReq             = 0
    
    def printOptimizationParameters(self, Actuator=internalcompoundPlanetaryActuator, log=1, csv=0):
        #motor parameters
        maxMotorAngVelRPM       = Actuator.motor.maxMotorAngVelRPM
        maxMotorAngVelRadPerSec = Actuator.motor.maxMotorAngVelRadPerSec
        maxMotorTorque          = Actuator.motor.maxMotorTorque
        maxMotorPower           = Actuator.motor.maxMotorPower
        motorMass               = Actuator.motor.massKG
        motorDia                = Actuator.motor.rotorODMM
        motorLength             = Actuator.motor.statorHeightMM
        # Planetary Gearbox Parameters
        maxGearAllowableStressMPa = Actuator.internalcompoundPlanetaryGearbox.maxGearAllowableStressMPa
        # Gear strength parameters
        FOS                      = Actuator.FOS
        serviceFactor            = Actuator.serviceFactor
        maxGearBoxDia            = Actuator.maxGearboxDiameter
        stressAnalysisMethodName = Actuator.stressAnalysisMethodName
        
        if log:
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
        
    def printOptimizationResults(self, Actuator=internalcompoundPlanetaryActuator, log=1, csv=0):
        Actuator.setVariables()
        if log:
            print("Iteration: ", self.iter)
            Actuator.printParametersLess()
            print(" ")
            print("Cost:", self.Cost)
            print("*****************************************************************")
        elif csv:
            iter       = self.iter
            gearRatio       = Actuator.internalcompoundPlanetaryGearbox.gearRatio()
            moduleBig       = Actuator.internalcompoundPlanetaryGearbox.moduleBig
            moduleSmall     = Actuator.internalcompoundPlanetaryGearbox.moduleSmall
            Ns              = Actuator.internalcompoundPlanetaryGearbox.Ns 
            NpBig           = Actuator.internalcompoundPlanetaryGearbox.NpBig
            NpSmall         = Actuator.internalcompoundPlanetaryGearbox.NpSmall 
            Nr              = Actuator.internalcompoundPlanetaryGearbox.Nr 
            numPlanet       = Actuator.internalcompoundPlanetaryGearbox.numPlanet
            fwSunMM         = round(Actuator.internalcompoundPlanetaryGearbox.fwSunMM    , 3)
            fwPlanetBigMM   = round(Actuator.internalcompoundPlanetaryGearbox.fwPlanetBigMM , 3)
            fwPlanetSmallMM = round(Actuator.internalcompoundPlanetaryGearbox.fwPlanetSmallMM , 3)
            fwRingMM        = round(Actuator.internalcompoundPlanetaryGearbox.fwRingMM   , 3)
            if self.UsePSCasVariable == 1 :
                try:
                    Opt_PSC_ring                 = self.cspgOpt.model.PSCr.value
                    Opt_PSC_planetBig            = self.cspgOpt.model.PSCp1.value
                    Opt_PSC_planetSmall          = self.cspgOpt.model.PSCp2.value
                    Opt_PSC_sun                  = self.cspgOpt.model.PSCs.value
                    CenterDist_SP, CenterDist_PR = self.cspgOpt.getCenterDistance(Var = False)
                except:
                    Opt_PSC_ring, Opt_PSC_planetBig, Opt_PSC_planetSmall, Opt_PSC_sun = 0, 0, 0, 0
                    CenterDist_SP = ((Ns + NpBig)/2)* moduleBig
                    CenterDist_PR = ((Nr - NpSmall)/2)* moduleSmall
            else :
                Opt_PSC_ring   = 0
                Opt_PSC_planetBig = 0
                Opt_PSC_planetSmall = 0
                Opt_PSC_sun   = 0
                CenterDist_SP = ((Ns + NpBig)/2)* moduleBig
                CenterDist_PR = ((Nr - NpSmall)/2)* moduleSmall

            mass            = round(Actuator.getMassKG_3DP(), 3)
            eff             = round(Actuator.internalcompoundPlanetaryGearbox.getEfficiency(), 3)
            peakTorque      = round(Actuator.motor.getMaxMotorTorque()*Actuator.internalcompoundPlanetaryGearbox.gearRatio(), 3)
            
            tooth_forces    = Actuator.getToothForces()
            Torque_Density  = round(peakTorque/mass, 3)
            
            if self.UsePSCasVariable == 1 : 
                try:
                    eff  = round(self.cspgOpt.getEfficiency(Var=False), 3)
                except:
                    pass
            
            Cost = self.cost(Actuator=Actuator)
            Outer_Bearing_mass = Actuator.bearing_mass
            Actuator_width = Actuator.actuator_width
            print(iter, ",", gearRatio, ",", moduleBig, ",", moduleSmall, ",", Ns, ",", NpBig, ",", NpSmall, ",", Nr, ",", numPlanet, ",", fwSunMM, ",", fwPlanetBigMM, ",", fwPlanetSmallMM, ",", fwRingMM, ",", mass, ",", eff, ",", peakTorque, ",", Cost, ",", Torque_Density, ",", Outer_Bearing_mass, ",", Actuator_width)

    def optimizeActuator(self, Actuator=internalcompoundPlanetaryActuator, UsePSCasVariable = 0, log=1, csv=0, printOptParams=1, gearRatioReq = 0):   
        self.UsePSCasVariable = UsePSCasVariable
        totalTime = 0
        self.gearRatioReq = gearRatioReq
        opt_parameters = None
        if UsePSCasVariable == 0:
            totalTime, opt_parameters = self.optimizeActuatorWithoutPSC(Actuator=Actuator, log=log, csv=csv,printOptParams=printOptParams)
        elif UsePSCasVariable == 1:
            totalTime = self.optimizeActuatorWithPSC(Actuator=Actuator, log=log, csv=csv)
        else:
            totalTime = 0
            print("ERROR: \"UsePSCasVariable\" can be either 0 or 1")

        return totalTime, opt_parameters
    
    def optimizeActuatorWithoutPSC(self, Actuator=internalcompoundPlanetaryActuator, log=1, csv=0, printOptParams=1):
        startTime = time.time()
        opt_parameters = None
        if csv and log:
            log = 0
            csv = 1
        elif not csv and not log:
            log = 0
            csv = 1
        
        if csv:
            fileName = f"ICPG_BRUTEFORCE_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}.csv"
        elif log:
            fileName = f"ICPG_BRUTEFORCE_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}_LOG.txt"
        
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
                print("iter, gearRatio, moduleBig, moduleSmall, Ns, NpBig, NpSmall, Nr, numPlanet, fwSunMM, fwPlanetBigMM, fwPanetSmallMM, fwRingMM, mass, eff, peakTorque, Cost, Torque_Density, Outer_Bearing_mass, Actuator_width")

            while self.gearRatioIter <= self.GEAR_RATIO_MAX:
                opt_done  = 0
                self.iter = 0
                self.Cost = 100000
                MinCost   = self.Cost
                Actuator.internalcompoundPlanetaryGearbox.setModuleBig(self.MODULE_BIG_MIN)
                while Actuator.internalcompoundPlanetaryGearbox.moduleBig <= self.MODULE_BIG_MAX:
                    # Setting Module Small
                    Actuator.internalcompoundPlanetaryGearbox.setModuleSmall(self.MODULE_SMALL_MIN)
                    while (Actuator.internalcompoundPlanetaryGearbox.moduleSmall <= self.MODULE_SMALL_MAX):
                        # Setting Ns
                        Actuator.internalcompoundPlanetaryGearbox.setNs(self.NUM_TEETH_SUN_MIN)
                        while (2*Actuator.internalcompoundPlanetaryGearbox.getPCRadiusSunM()*1000) <= Actuator.maxGearboxDiameter:
                            # Setting Np Big
                            Actuator.internalcompoundPlanetaryGearbox.setNpBig(self.NUM_TEETH_PLANET_BIG_MIN)
                            while (2*Actuator.internalcompoundPlanetaryGearbox.getPCRadiusPlanetBigM()*1000) <= Actuator.maxGearboxDiameter/2:
                                # Setting Np Small
                                Actuator.internalcompoundPlanetaryGearbox.setNpSmall(self.NUM_TEETH_PLANET_SMALL_MIN)
                                while (2*Actuator.internalcompoundPlanetaryGearbox.getPCRadiusPlanetSmallM()*1000) <= Actuator.maxGearboxDiameter/2:
                                    # Setting Nr
                                    Actuator.internalcompoundPlanetaryGearbox.setNr(Actuator.internalcompoundPlanetaryGearbox.NpSmall + 
                                                                            Actuator.internalcompoundPlanetaryGearbox.NpBig +
                                                                            Actuator.internalcompoundPlanetaryGearbox.Ns)
                                    if (Actuator.internalcompoundPlanetaryGearbox.getGearboxOuterDiaMaxM()*1000) <= Actuator.maxGearboxDiameter:
                                        # Setting number of Planet
                                        Actuator.internalcompoundPlanetaryGearbox.setNumPlanet(self.NUM_PLANET_MIN)
                                        while Actuator.internalcompoundPlanetaryGearbox.numPlanet <= self.NUM_PLANET_MAX:
                                            if (Actuator.internalcompoundPlanetaryGearbox.geometricConstraint() and 
                                                Actuator.internalcompoundPlanetaryGearbox.meshingConstraint() and 
                                                Actuator.internalcompoundPlanetaryGearbox.noPlanetInterferenceConstraint()):
                                                self.totalFeasibleGearboxes += 1
                                                # Fiter for the Gear Ratio
                                                if (Actuator.internalcompoundPlanetaryGearbox.gearRatio() >= self.gearRatioIter - 1e-6 and 
                                                    Actuator.internalcompoundPlanetaryGearbox.gearRatio() <= (self.gearRatioIter + self.GEAR_RATIO_STEP + 1e-6)):
                                                    self.totalGearboxesWithReqGR += 1
                                                    Actuator.updateFacewidth()
                                                    
                                                    self.Cost = self.cost(Actuator=Actuator)

                                                    if self.Cost < MinCost:
                                                        MinCost    = self.Cost
                                                        opt_done   = 1
                                                        self.iter += 1
                                                        if (self.gearRatioReq == 0):
                                                            Actuator.genEquationFile(motor_name=Actuator.motor.motorName, gearRatioLL=round(self.gearRatioIter, 1), gearRatioUL = (round(self.gearRatioIter + self.GEAR_RATIO_STEP,1)))
                                                        else:
                                                            Actuator.genEquationFile_editCADdirectly()
                                                        
                                                        opt_parameters = [Actuator.internalcompoundPlanetaryGearbox.gearRatio(),
                                                                          Actuator.internalcompoundPlanetaryGearbox.numPlanet,
                                                                          Actuator.internalcompoundPlanetaryGearbox.Ns,
                                                                          Actuator.internalcompoundPlanetaryGearbox.NpBig,
                                                                          Actuator.internalcompoundPlanetaryGearbox.NpSmall,
                                                                          Actuator.internalcompoundPlanetaryGearbox.Nr,
                                                                          Actuator.internalcompoundPlanetaryGearbox.moduleBig,
                                                                          Actuator.internalcompoundPlanetaryGearbox.moduleSmall,
                                                                          Actuator.getMassKG_3DP(),          # [8] Total Gearbox
                                                                          Actuator.bearing_mass,          # [9] Bearings
                                                                          Actuator.sun_gear_mass_kg,         # [10] Sun
                                                                          Actuator.planet_mass_kg,           # [11] Planets
                                                                          Actuator.ring_gear_mass_kg,        # [12] Ring
                                                                          Actuator.carrier_mass_kg,          # [13] Carrier
                                                                          Actuator.sec_carrier_mass_kg,      # [14] Sec Carrier
                                                                          Actuator.motor_casing_mass_kg,
                                                                          Actuator.total_sum_except_motor_and_baering]     # [15] motorcasing mass
                                                        opt_planetaryGearbox = internalcompoundPlanetaryGearbox(design_parameters         = self.design_parameters,
                                                                                                        gear_standard_parameters  = self.gear_standard_parameters,
                                                                                                        Ns                        = Actuator.internalcompoundPlanetaryGearbox.Ns,
                                                                                                        NpBig                     = Actuator.internalcompoundPlanetaryGearbox.NpBig,
                                                                                                        NpSmall                   = Actuator.internalcompoundPlanetaryGearbox.NpSmall, 
                                                                                                        Nr                        = Actuator.internalcompoundPlanetaryGearbox.Nr,
                                                                                                        numPlanet                 = Actuator.internalcompoundPlanetaryGearbox.numPlanet,
                                                                                                        moduleBig                 = Actuator.internalcompoundPlanetaryGearbox.moduleBig, # mm
                                                                                                        moduleSmall               = Actuator.internalcompoundPlanetaryGearbox.moduleSmall, # mm
                                                                                                        densityGears              = Actuator.internalcompoundPlanetaryGearbox.densityGears,
                                                                                                        densityStructure          = Actuator.internalcompoundPlanetaryGearbox.densityStructure,
                                                                                                        fwSunMM                   = Actuator.internalcompoundPlanetaryGearbox.fwSunMM, # mm
                                                                                                        fwPlanetBigMM             = Actuator.internalcompoundPlanetaryGearbox.fwPlanetBigMM, # mm
                                                                                                        fwPlanetSmallMM           = Actuator.internalcompoundPlanetaryGearbox.fwPlanetSmallMM, # mm
                                                                                                        fwRingMM                  = Actuator.internalcompoundPlanetaryGearbox.fwRingMM, # mm
                                                                                                        maxGearAllowableStressMPa = Actuator.internalcompoundPlanetaryGearbox.maxGearAllowableStressMPa) # MPa) # kg/m^3
                                                        opt_actuator = internalcompoundPlanetaryActuator(design_parameters        = self.design_parameters,
                                                                                                 motor                    = Actuator.motor,
                                                                                                 motor_driver_params      = None,
                                                                                                 internalcompoundPlanetaryGearbox = opt_planetaryGearbox,
                                                                                                 FOS                      = Actuator.FOS,
                                                                                                 serviceFactor            = Actuator.serviceFactor,
                                                                                                 maxGearboxDiameter       = Actuator.maxGearboxDiameter, # mm 
                                                                                                 stressAnalysisMethodName = "MIT") # Lewis or AGMA
                                                        opt_actuator.updateFacewidth()
                                                        opt_actuator.getMassKG_3DP()

                                            Actuator.internalcompoundPlanetaryGearbox.setNumPlanet(Actuator.internalcompoundPlanetaryGearbox.numPlanet + 1)
                                    Actuator.internalcompoundPlanetaryGearbox.setNpSmall(Actuator.internalcompoundPlanetaryGearbox.NpSmall + 1)
                                Actuator.internalcompoundPlanetaryGearbox.setNpBig(Actuator.internalcompoundPlanetaryGearbox.NpBig + 1)
                            Actuator.internalcompoundPlanetaryGearbox.setNs(Actuator.internalcompoundPlanetaryGearbox.Ns + 1)
                        Actuator.internalcompoundPlanetaryGearbox.setModuleSmall(Actuator.internalcompoundPlanetaryGearbox.moduleSmall + 0.100)
                        Actuator.internalcompoundPlanetaryGearbox.setModuleSmall(round(Actuator.internalcompoundPlanetaryGearbox.moduleSmall, 1)) # Round Off
                    Actuator.internalcompoundPlanetaryGearbox.setModuleBig(Actuator.internalcompoundPlanetaryGearbox.moduleBig + 0.100)
                    Actuator.internalcompoundPlanetaryGearbox.setModuleBig(round(Actuator.internalcompoundPlanetaryGearbox.moduleBig, 1)) # Round Off
                if (opt_done):
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
            if(printOptParams):
                print("\n")
                print("Running Time (sec)")
                print(totalTime) 

        sys.stdout = sys.__stdout__

        return totalTime, opt_parameters

    def optimizeActuatorWithPSC(self, Actuator=internalcompoundPlanetaryActuator, log=1, csv=0):
        startTime = time.time()
        opt_parameters = []
        if csv and log:
            log = 0
            csv = 1
        elif not csv and not log:
            log = 0
            csv = 1
        
        if csv:
            fileName = f"CPG_BILEVEL_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}.csv"
        elif log:
            fileName = f"CPG_BILEVEL_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}_LOG.txt"
        
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
                print(" ")
                print("iter, gearRatio, moduleBig, moduleSmall, Ns, NpBig, NpSmall, Nr, numPlanet, fwSunMM, fwPlanetBigMM, fwPanetSmallMM, fwRingMM, PSCs, PSCp1, PSCp2, PSCr, CD_SP, CD_PR, mass, eff, peakTorque, Cost, tooth_forces_sp, tooth_forces_rp, Torque_Density")

            while self.gearRatioIter <= self.GEAR_RATIO_MAX:
                opt_done  = 0
                self.iter = 0
                self.Cost = 100000
                MinCost   = self.Cost
                Actuator.internalcompoundPlanetaryGearbox.setModuleBig(self.MODULE_BIG_MIN)
                while Actuator.internalcompoundPlanetaryGearbox.moduleBig <= self.MODULE_BIG_MAX:
                    # Setting Module Small
                    Actuator.internalcompoundPlanetaryGearbox.setModuleSmall(self.MODULE_SMALL_MIN)
                    while (Actuator.internalcompoundPlanetaryGearbox.moduleSmall <= self.MODULE_SMALL_MAX):
                        # Setting Ns
                        Actuator.internalcompoundPlanetaryGearbox.setNs(self.NUM_TEETH_SUN_MIN)
                        while (2*Actuator.internalcompoundPlanetaryGearbox.getPCRadiusSunM()*1000) <= Actuator.maxGearboxDiameter:
                            # Setting Np Big
                            Actuator.internalcompoundPlanetaryGearbox.setNpBig(self.NUM_TEETH_PLANET_BIG_MIN)
                            while (2*Actuator.internalcompoundPlanetaryGearbox.getPCRadiusPlanetBigM()*1000) <= Actuator.maxGearboxDiameter/2:
                                # Setting Np Small
                                Actuator.internalcompoundPlanetaryGearbox.setNpSmall(self.NUM_TEETH_PLANET_SMALL_MIN)
                                while (2*Actuator.internalcompoundPlanetaryGearbox.getPCRadiusPlanetSmallM()*1000) <= Actuator.maxGearboxDiameter/2:
                                    # Setting Nr
                                    Actuator.internalcompoundPlanetaryGearbox.setNr(Actuator.internalcompoundPlanetaryGearbox.NpSmall + 
                                                                            Actuator.internalcompoundPlanetaryGearbox.NpBig +
                                                                            Actuator.internalcompoundPlanetaryGearbox.Ns)
                                    if (Actuator.internalcompoundPlanetaryGearbox.getGearboxOuterDiaMaxM()*1000) <= Actuator.maxGearboxDiameter:
                                        # Setting number of Planet
                                        Actuator.internalcompoundPlanetaryGearbox.setNumPlanet(self.NUM_PLANET_MIN)
                                        while Actuator.internalcompoundPlanetaryGearbox.numPlanet <= self.NUM_PLANET_MAX:
                                            if (Actuator.internalcompoundPlanetaryGearbox.geometricConstraint() and 
                                                Actuator.internalcompoundPlanetaryGearbox.meshingConstraint() and 
                                                Actuator.internalcompoundPlanetaryGearbox.noPlanetInterferenceConstraint()):
                                                self.totalFeasibleGearboxes += 1
                                                # Fiter for the Gear Ratio
                                                if (Actuator.internalcompoundPlanetaryGearbox.gearRatio() >= self.gearRatioIter and 
                                                    Actuator.internalcompoundPlanetaryGearbox.gearRatio() <= (self.gearRatioIter + self.GEAR_RATIO_STEP)):
                                                    self.totalGearboxesWithReqGR += 1
                                                    Actuator.updateFacewidth()
                                                    
                                                    effActuator = Actuator.internalcompoundPlanetaryGearbox.getEfficiency()
                                                    massActuator = Actuator.getMassKG_3DP()

                                                    self.Cost = (self.K_Mass * massActuator) + (self.K_Eff * effActuator)
                                                    if self.Cost < MinCost:
                                                        MinCost = self.Cost
                                                        opt_done = 1
                                                        self.iter += 1
                                                        Actuator.genEquationFile()
                                                        opt_parameters = [Actuator.internalcompoundPlanetaryGearbox.gearRatio(),
                                                                          Actuator.internalcompoundPlanetaryGearbox.numPlanet,
                                                                          Actuator.internalcompoundPlanetaryGearbox.Ns,
                                                                          Actuator.internalcompoundPlanetaryGearbox.NpBig,
                                                                          Actuator.internalcompoundPlanetaryGearbox.NpSmall,
                                                                          Actuator.internalcompoundPlanetaryGearbox.Nr,
                                                                          Actuator.internalcompoundPlanetaryGearbox.moduleBig,
                                                                          Actuator.internalcompoundPlanetaryGearbox.moduleSmall]
                                                        opt_planetaryGearbox = internalcompoundPlanetaryGearbox(design_parameters         = self.design_parameters,
                                                                                                        gear_standard_parameters  = self.gear_standard_parameters,
                                                                                                        Ns                        = Actuator.internalcompoundPlanetaryGearbox.Ns,
                                                                                                        NpBig                     = Actuator.internalcompoundPlanetaryGearbox.NpBig,
                                                                                                        NpSmall                   = Actuator.internalcompoundPlanetaryGearbox.NpSmall, 
                                                                                                        Nr                        = Actuator.internalcompoundPlanetaryGearbox.Nr,
                                                                                                        numPlanet                 = Actuator.internalcompoundPlanetaryGearbox.numPlanet,
                                                                                                        moduleBig                 = Actuator.internalcompoundPlanetaryGearbox.moduleBig, # mm
                                                                                                        moduleSmall               = Actuator.internalcompoundPlanetaryGearbox.moduleSmall, # mm
                                                                                                        densityGears              = Actuator.internalcompoundPlanetaryGearbox.densityGears,
                                                                                                        densityStructure          = Actuator.internalcompoundPlanetaryGearbox.densityStructure,
                                                                                                        fwSunMM                   = Actuator.internalcompoundPlanetaryGearbox.fwSunMM, # mm
                                                                                                        fwPlanetBigMM             = Actuator.internalcompoundPlanetaryGearbox.fwPlanetBigMM, # mm
                                                                                                        fwPlanetSmallMM           = Actuator.internalcompoundPlanetaryGearbox.fwPlanetSmallMM, # mm
                                                                                                        fwRingMM                  = Actuator.internalcompoundPlanetaryGearbox.fwRingMM, # mm
                                                                                                        maxGearAllowableStressMPa = Actuator.internalcompoundPlanetaryGearbox.maxGearAllowableStressMPa) # MPa) # kg/m^3
                                                        opt_actuator = internalcompoundPlanetaryActuator(design_parameters        = self.design_parameters,
                                                                                                 motor                    = Actuator.motor,
                                                                                                 internalcompoundPlanetaryGearbox = opt_planetaryGearbox,
                                                                                                 FOS                      = Actuator.FOS,
                                                                                                 serviceFactor            = Actuator.serviceFactor,
                                                                                                 maxGearboxDiameter       = Actuator.maxGearboxDiameter, # mm 
                                                                                                 stressAnalysisMethodName = "Lewis") # Lewis or AGMA
                                            Actuator.internalcompoundPlanetaryGearbox.setNumPlanet(Actuator.internalcompoundPlanetaryGearbox.numPlanet + 1)
                                    Actuator.internalcompoundPlanetaryGearbox.setNpSmall(Actuator.internalcompoundPlanetaryGearbox.NpSmall + 1)
                                Actuator.internalcompoundPlanetaryGearbox.setNpBig(Actuator.internalcompoundPlanetaryGearbox.NpBig + 1)
                            Actuator.internalcompoundPlanetaryGearbox.setNs(Actuator.internalcompoundPlanetaryGearbox.Ns + 1)
                        Actuator.internalcompoundPlanetaryGearbox.setModuleSmall(Actuator.internalcompoundPlanetaryGearbox.moduleSmall + 0.100)
                        Actuator.internalcompoundPlanetaryGearbox.setModuleSmall(round(Actuator.internalcompoundPlanetaryGearbox.moduleSmall, 1)) # Round Off
                    Actuator.internalcompoundPlanetaryGearbox.setModuleBig(Actuator.internalcompoundPlanetaryGearbox.moduleBig + 0.100)
                    Actuator.internalcompoundPlanetaryGearbox.setModuleBig(round(Actuator.internalcompoundPlanetaryGearbox.moduleBig, 1)) # Round Off
                if (opt_done):
                    try:
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
                    except NameError:
                        pass # Continues execution if external PSC optimizer is missing in local environment
                        
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

    def cost(self, Actuator=internalcompoundPlanetaryActuator):
        K_gearRatio = 0
        if self.gearRatioReq != 0:
            K_gearRatio = 10
        
        gearRatio_err = np.sqrt((Actuator.internalcompoundPlanetaryGearbox.gearRatio() - self.gearRatioReq)**2)

        mass = Actuator.getMassKG_3DP()
        eff = Actuator.internalcompoundPlanetaryGearbox.getEfficiency()
        width = Actuator.internalcompoundPlanetaryGearbox.fwPlanetBigMM + Actuator.internalcompoundPlanetaryGearbox.fwPlanetSmallMM
        cost = (self.K_Mass    * mass 
                + self.K_Eff   * eff 
                + self.K_Width * width 
                + K_gearRatio  * gearRatio_err)
        return cost