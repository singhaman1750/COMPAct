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
        self.data_bearings = [[10,19,5,0.005],[12,21,5,0.006],[15,24,5,0.007],[17,26,5,0.007],[20,32,7,0.017],[25,37,7,0.021],[28,52,12,0.096],[30,42,7,0.024],[32,58,13,0.122],[35,47,7,0.027],[40,52,7,0.031],[45,58,7,0.038],[50,65,7,0.050],[55,72,9,0.081],[60,78,10,0.103],[65,85,10,0.128],[70,90,10,0.134],[75,95,10,0.149],[80,100,10,0.151],[85,110,13,0.263],
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

        # Only dk is stored for CSK, t is calculated as (dk - d) / 2
        csk_table = {
            3.0: {"dk": 6},
            4.0: {"dk": 8},
            5.0: {"dk": 10},
            6.0: {"dk": 12},
            8.0: {"dk": 16},
            10.0: {"dk": 20},
            12.0: {"dk": 24},
            16.0: {"dk": 30},
            20.0: {"dk": 36}
        }

        if bolt_type == "socket_head":
            spec = socket_head_table.get(diameter)
            if not spec:
                raise ValueError(f"Socket head bolt M{diameter} not found.")
            return [spec["d2"], spec["k"]]  # Return d2, k

        elif bolt_type == "CSK":
            spec = csk_table.get(diameter)
            if not spec:
                raise ValueError(f"CSK bolt M{diameter} not found.")
            dk = spec["dk"]
            t = (dk - diameter) / 2
            return [dk, round(t, 3)]  # Rounded for clarity

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
            7.0: {"width_across_flats": None, "height": 5.5},  # ISO not defined
            8.0: {"width_across_flats": 13, "height": 6.5},
            10.0: {"width_across_flats": 16, "height": 8},
            12.0: {"width_across_flats": 18, "height": 10},
            14.0: {"width_across_flats": 21, "height": 13},
            16.0: {"width_across_flats": 24, "height": 13},
            18.0: {"width_across_flats": 27, "height": 15},
            20.0: {"width_across_flats": 30, "height": 16},
            24.0: {"width_across_flats": 36, "height": 18},
            27.0: {"width_across_flats": 40, "height": 20},
            30.0: {"width_across_flats": 43, "height": 22},
        }

        spec = nut_table.get(diameter)
        if not spec:
            raise ValueError(f"No nut data found for bolt diameter M{diameter}")

        width_across_flats = spec["width_across_flats"]
        height = spec["height"]

        return [width_across_flats, height]

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

#-------------------------------------------------------------------------
# Compound Planetary Gearbox
#-------------------------------------------------------------------------
class compoundPlanetaryGearbox:
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
# 3K - Planetary Gearbox (wolfrom Planetary Gearbox)
#-------------------------------------------------------------------------
class wolfromPlanetaryGearbox:
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
                 maxGearAllowableStressMPa = 400):
        
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
        self.ringRadialWidthSmall = design_parameters["ringRadialWidthMMSmall"] # ringRadialWidthSmall
        self.ringRadialWidthBig   = design_parameters["ringRadialWidthMMBig"]   # ringRadialWidthBig
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

        # Total mass of the compound planetary gearbox
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
        return (ringPCRadiusMM + self.ringRadialWidthSmall) / 1000.0

    def getOuterRadiusRingBigM(self):
        ringPCDiameterMM = self.NrBig * self.moduleBig
        ringPCRadiusMM = ringPCDiameterMM / 2
        return (ringPCRadiusMM + self.ringRadialWidthBig) / 1000.0
    
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
        return (ringPCRadiusMM + self.ringRadialWidthSmall)

    def getOuterRadiusRingBigMM(self):
        ringPCDiameterMM = self.NrBig * self.moduleBig
        ringPCRadiusMM = ringPCDiameterMM / 2
        return (ringPCRadiusMM + self.ringRadialWidthBig)
    
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
        print("Bigger Ring radial width = ", self.ringRadialWidthBig, " mm")
        print("Smaller Ring radial width = ", self.ringRadialWidthSmall, " mm")
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

#-------------------------------------------------------------------------
# Double Stage Planetary Gearbox
#-------------------------------------------------------------------------
class doubleStagePlanetaryGearbox:
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

#=========================================================================
# Motor class
#=========================================================================
class motor:
    def __init__(self, 
                 maxMotorAngVelRPM     = 1190, # RPM
                 maxMotorTorque        = 8.83, # Nm
                 maxMotorPower         = 8.83 * 1190 * 2*np.pi/60, # W 
                 motorMass             = 0.778, # KG
                 motorDia              = 106.8, # mm
                 motorLength           = 47.6,  # mm
                 motor_mount_hole_PCD       = 32,
                 motor_mount_hole_dia       = 4,
                 motor_mount_hole_num       = 4,
                 motor_output_hole_PCD      = 23,
                 motor_output_hole_dia      = 4,
                 motor_output_hole_num      = 4,
                 wire_slot_dist_from_center = 30,
                 wire_slot_length           = 10,
                 wire_slot_radius           = 4,
                 motorName             = "U12"):
        
        self.motorName                  = motorName
        self.maxMotorAngVelRPM          = maxMotorAngVelRPM
        self.maxMotorAngVelRadPerSec    = maxMotorAngVelRPM * (2 * np.pi / 60)
        self.maxMotorTorque             = maxMotorTorque
        self.maxMotorPower              = maxMotorPower
        self.massKG                     = motorMass     # kg
        self.motorDiaMM                 = motorDia      # mm #TODO: make use of this parameter
        self.motorLengthMM              = motorLength   # mm #TODO: make use of this parameter
        self.motor_mount_hole_PCD       = motor_mount_hole_PCD 
        self.motor_mount_hole_dia       = motor_mount_hole_dia
        self.motor_mount_hole_num       = motor_mount_hole_num
        self.motor_output_hole_PCD      = motor_output_hole_PCD 
        self.motor_output_hole_dia      = motor_output_hole_dia
        self.motor_output_hole_num      = motor_output_hole_num
        self.wire_slot_dist_from_center = wire_slot_dist_from_center 
        self.wire_slot_length           = wire_slot_length 
        self.wire_slot_radius           = wire_slot_radius

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
# Motor Driver class
#=========================================================================
class motor_driver:
    def __init__(self, driver_name, motor_driver_data):
        self.driver_name                          = driver_name
        self.driver_upper_holes_dist_from_center  = motor_driver_data["driver_upper_holes_dist_from_center"]
        self.driver_lower_holes_dist_from_center  = motor_driver_data["driver_lower_holes_dist_from_center"]
        self.driver_side_holes_dist_from_center   = motor_driver_data["driver_side_holes_dist_from_center"]
        self.driver_mount_holes_dia               = motor_driver_data["driver_mount_holes_dia"]
        self.driver_mount_inserts_OD              = motor_driver_data["driver_mount_inserts_OD"]
        self.driver_mount_thickness               = motor_driver_data["driver_mount_thickness"]
        self.driver_mount_height                  = motor_driver_data["driver_mount_height"]

        # self.print_vars()
    
    def print_vars(self):
        print("driver_name:", self.driver_name)
        print("driver_upper_holes_dist_from_center: ", self.driver_upper_holes_dist_from_center)
        print("driver_lower_holes_dist_from_center: ", self.driver_lower_holes_dist_from_center)
        print("driver_side_holes_dist_from_center: ", self.driver_side_holes_dist_from_center)
        print("driver_mount_holes_dia: ", self.driver_mount_holes_dia)
        print("driver_mount_inserts_OD: ", self.driver_mount_inserts_OD)
        print("driver_mount_thickness: ", self.driver_mount_thickness)
        print("driver_mount_height: ", self.driver_mount_height)
        print("---")

#=========================================================================
# Actuator classes
#=========================================================================
#-------------------------------------------------------------------------
# Single Stage Actuator class
#-------------------------------------------------------------------------
class singleStagePlanetaryActuator:
    def __init__(self, 
                 design_params,
                 motor_driver_params,
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
        self.ringRadialWidthMM = self.planetaryGearbox.ringRadialWidthMM

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
        self.case_mounting_nut_clearance                = self.design_params["case_mounting_nut_clearance"]                # 2
        self.standard_fillet_1_5mm                      = self.design_params["standard_fillet_1_5mm"]                      # 1.5
        self.standard_bearing_insertion_chamfer         = self.design_params["standard_bearing_insertion_chamfer"]         # 0.5
        self.bearingIDClearanceMM                       = self.design_params["bearingIDClearanceMM"]
        self.clearance_sun_coupler_sec_carrier          = self.design_params["clearance_sun_coupler_sec_carrier"]          # 1.5
        self.ring_to_chamfer_clearance                  = self.design_params["ring_to_chamfer_clearance"]                  # 2
        self.tight_clearance_3DP                        = self.design_params["tight_clearance_3DP"]        
        self.loose_clearance_3DP                        = self.design_params["loose_clearance_3DP"]

        # --- Secondary Carrier dimensions ---
        self.sec_carrier_thickness = self.design_params["sec_carrier_thickness"] # 5

        # --- Sun coupler, sun gear & sun gear dimensions ---
        self.sun_shaft_bearing_ID      = self.design_params["sun_shaft_bearing_ID"]      # 8
        self.sun_shaft_bearing_OD      = self.design_params["sun_shaft_bearing_OD"]      # 16
        self.sun_coupler_hub_thickness = self.design_params["sun_coupler_hub_thickness"] # 4
        self.sun_shaft_bearing_width   = self.design_params["sun_shaft_bearing_width"]   # 5
        self.sun_central_bolt_dia      = self.design_params["sun_central_bolt_dia"]      # 5

        # --- casing Motor and gearbox casing dimensions ---
        self.case_mounting_surface_height             = self.design_params["case_mounting_surface_height"] # 4
        self.case_mounting_hole_dia                   = self.design_params["case_mounting_hole_dia"] # 3
        self.case_mounting_bolt_depth                 = self.design_params["case_mounting_bolt_depth"] # 4.5
        self.base_plate_thickness                     = self.design_params["base_plate_thickness"] # 4
        self.Motor_case_thickness                     = self.design_params["Motor_case_thickness"] # 2.5
        self.air_flow_hole_offset                     = self.design_params["air_flow_hole_offset"] # 3
        self.central_hole_offset_from_motor_mount_PCD = self.design_params["central_hole_offset_from_motor_mount_PCD"] # 5
        self.output_mounting_hole_dia                 = self.design_params["output_mounting_hole_dia"] # 4
        self.output_mounting_nut_depth                = self.design_params["output_mounting_nut_depth"] # 3
        self.Motor_case_OD_base_to_chamfer            = self.design_params["Motor_case_OD_base_to_chamfer"] # 5
        self.pattern_offset_from_motor_case_OD_base   = self.design_params["pattern_offset_from_motor_case_OD_base"] # 3 
        self.pattern_bulge_dia                        = self.design_params["pattern_bulge_dia"] # 3
        self.pattern_num_bulge                        = self.design_params["pattern_num_bulge"] # 18
        self.pattern_depth                            = self.design_params["pattern_depth"] # 2

        # --- carrier dimensions ---
        self.carrier_trapezoidal_support_sun_offset                 = self.design_params["carrier_trapezoidal_support_sun_offset"] # 5
        self.carrier_trapezoidal_support_hole_PCD_offset_bearing_ID = self.design_params["carrier_trapezoidal_support_hole_PCD_offset_bearing_ID"] # 4
        self.carrier_trapezoidal_support_hole_dia                   = self.design_params["carrier_trapezoidal_support_hole_dia"] # 3
        self.carrier_bearing_step_width                             = self.design_params["carrier_bearing_step_width"] # 1.5
        
        # --- Driver Dimensions ---
        self.driver_upper_holes_dist_from_center = self.motor_driver_params["driver_upper_holes_dist_from_center"]
        self.driver_lower_holes_dist_from_center = self.motor_driver_params["driver_lower_holes_dist_from_center"]
        self.driver_side_holes_dist_from_center  = self.motor_driver_params["driver_side_holes_dist_from_center"]
        self.driver_mount_holes_dia              = self.motor_driver_params["driver_mount_holes_dia"]
        self.driver_mount_inserts_OD             = self.motor_driver_params["driver_mount_inserts_OD"]
        self.driver_mount_thickness              = self.motor_driver_params["driver_mount_thickness"]
        self.driver_mount_height                 = self.motor_driver_params["driver_mount_height"]

        # --- Planet Gear dimensions ---
        self.planet_pin_bolt_dia      = self.design_params["planet_pin_bolt_dia"] # 5 
        self.planet_shaft_dia         = self.design_params["planet_shaft_dia"] # 8  
        self.planet_shaft_step_offset = self.design_params["planet_shaft_step_offset"] # 1  
        self.planet_bearing_OD        = self.design_params["planet_bearing_OD"] # 12 
        self.planet_bearing_width     = self.design_params["planet_bearing_width"] # 3.5
        self.planet_bore              = self.design_params["planet_bore"] # 10

        # --- bearing retainer dimensions ---
        self.bearing_retainer_thickness = self.design_params["bearing_retainer_thickness"] # 2

        # --- carrier nuts and bolts ---
        carrier_trapezoidal_support_hole = nuts_and_bolts_dimensions(bolt_dia=self.carrier_trapezoidal_support_hole_dia, bolt_type="socket_head")

        self.carrier_trapezoidal_support_hole_socket_head_dia = carrier_trapezoidal_support_hole.bolt_head_dia
        self.carrier_trapezoidal_support_hole_wrench_size     = carrier_trapezoidal_support_hole.nut_width_across_flats

        # --- Motor --- 
        self.motor_OD                   = self.motorDiaMM
        self.motor_height               = self.motorLengthMM
        self.motor_mount_hole_PCD       = self.motor.motor_mount_hole_PCD 
        self.motor_mount_hole_dia       = self.motor.motor_mount_hole_dia
        self.motor_mount_hole_num       = self.motor.motor_mount_hole_num
        self.motor_output_hole_PCD      = self.motor.motor_output_hole_PCD 
        self.motor_output_hole_dia      = self.motor.motor_output_hole_dia
        self.motor_output_hole_num      = self.motor.motor_output_hole_num
        self.wire_slot_dist_from_center = self.motor.wire_slot_dist_from_center 
        self.wire_slot_length           = self.motor.wire_slot_length 
        self.wire_slot_radius           = self.motor.wire_slot_radius

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
        planet_pin_bolt = nuts_and_bolts_dimensions(bolt_dia=self.planet_pin_bolt_dia, bolt_type="socket_head")
        
        self.planet_pin_socket_head_dia = planet_pin_bolt.bolt_head_dia
        self.planet_pin_bolt_wrench_size = planet_pin_bolt.nut_width_across_flats
        # ---

        self.dp_r    = self.module * self.Nr
        self.db_r    = self.dp_r * np.cos(self.pressure_angle)
        self.fw_r    = self.planetaryGearbox.fwRingMM
        self.alpha_r = (np.sqrt(self.dp_r**2 - self.db_r**2) / self.db_r) * 180 / np.pi - self.pressure_angle * 180 / np.pi 
        self.beta_r  = (360 / (4 * self.Nr) + self.alpha_r) * 2
        self.ring_radial_thickness = self.ringRadialWidthMM

        self.ring_OD = self.dp_r + 2 * self.ring_radial_thickness

        # --- casing Motor and gearbox casing dimensions ---
        if self.ring_OD < self.motor_OD :
            self.clearance_motor_and_case = 5 
        else :
            self.clearance_motor_and_case = (self.ring_OD - self.motor_OD) / 2 + 5
        
        self.Motor_case_ID = self.motor_OD + self.clearance_motor_and_case * 2
        self.motor_case_OD_base = self.motor_OD + self.clearance_motor_and_case * 2 + self.Motor_case_thickness * 2

        self.case_dist = self.sec_carrier_thickness + self.clearance_planet + self.sun_coupler_hub_thickness - self.case_mounting_surface_height

        self.case_mounting_hole_shift = self.case_mounting_hole_dia / 2 - 0.5
        self.case_mounting_PCD = self.motor_case_OD_base + self.case_mounting_hole_shift * 2

        case_mounting_hole_bolt = nuts_and_bolts_dimensions(bolt_dia=self.case_mounting_hole_dia, bolt_type="socket_head")

        self.case_mounting_hole_allen_socket_dia = case_mounting_hole_bolt.bolt_head_dia
        self.Motor_case_OD_max = self.case_mounting_PCD + self.case_mounting_hole_allen_socket_dia + self.clearance_case_mount_holes_shell_thickness * 2

        self.case_mounting_wrench_size       = case_mounting_hole_bolt.nut_width_across_flats
        self.case_mounting_nut_thickness     = case_mounting_hole_bolt.nut_thickness         

        # --- Bearing Dimensions ---
        IdrequiredMM        = self.module * (self.Ns + self.Np) + self.bearingIDClearanceMM
        Bearings            = bearings_discrete(IdrequiredMM)
        self.bearing_ID     = Bearings.getBearingIDMM()
        self.bearing_OD     = Bearings.getBearingODMM()
        self.bearing_height = Bearings.getBearingWidthMM()

        outer_check = self.bearing_OD + self.output_mounting_hole_dia * 4
        inner_check = self.Nr * self.module + 2 * self.h_b
        if outer_check > inner_check:
            self.bearing_mount_thickness = self.output_mounting_hole_dia * 2
        else:
            self.bearing_mount_thickness = ((inner_check - outer_check) / 2) + self.output_mounting_hole_dia * 2 + self.standard_clearance_1_5mm

        self.output_mounting_PCD = self.bearing_OD + self.bearing_mount_thickness
        self.carrier_PCD         = (self.Np + self.Ns) * self.module

        output_mounting_hole_bolt = nuts_and_bolts_dimensions(bolt_dia=self.output_mounting_hole_dia, bolt_type="socket_head")

        self.output_mounting_nut_thickness   = output_mounting_hole_bolt.nut_thickness         
        self.output_mounting_nut_wrench_size = output_mounting_hole_bolt.nut_width_across_flats

        # ------------ Motors ------------------
        motor_output_hole_bolt = nuts_and_bolts_dimensions(bolt_dia = self.motor_output_hole_dia, bolt_type="CSK")

        self.motor_output_hole_CSK_OD          = motor_output_hole_bolt.bolt_head_dia   
        self.motor_output_hole_CSK_head_height = motor_output_hole_bolt.bolt_head_height

        # --- Sun coupler & sun gear dimensions ---
        self.sun_hub_dia = self.motor_output_hole_PCD + self.motor_output_hole_dia + self.standard_clearance_1_5mm * 4
        
        sun_central_bolt = nuts_and_bolts_dimensions(bolt_dia = self.sun_central_bolt_dia, bolt_type="socket_head")
        self.sun_central_bolt_socket_head_dia   = sun_central_bolt.bolt_head_dia
        
        self.fw_s_used = self.fw_p + self.clearance_planet + self.sec_carrier_thickness + self.standard_clearance_1_5mm

        #------------------------------------------
        self.actuator_width = (  self.motor_height 
                               + self.case_mounting_surface_height
                               + self.standard_clearance_1_5mm
                               + self.base_plate_thickness
                               + self.case_dist
                               + self.bearing_height
                               + self.standard_clearance_1_5mm
                               + self.fw_r
                               + self.clearance_planet 
                               + self.bearing_retainer_thickness)

    def genEquationFile(self, motor_name="NO_MOTOR", gearRatioLL = 0.0, gearRatioUL = 0.0):
        self.setVariables()
        file_path = os.path.join(os.path.dirname(__file__), 'SSPG', 'Equation_Files', motor_name, f'sspg_equations_{gearRatioLL}_{gearRatioUL}.txt')
        with open(file_path, 'w') as eqFile:
            eqFile.writelines([
                # ---------------- Optimization Variables ----------------
                f'"Ns"= {self.Ns}\n',
                f'"Np"= {self.Np}\n',
                f'"Nr"= {self.Nr}\n',
                f'"module"= {self.module}\n',
                f'"num_planet"= {self.num_planet}\n',

                # ---------------- Independent Variables ------------------
                f'"pressure angle"= {self.pressure_angle_deg}deg\n',
                f'"pressure_angle"= {self.pressure_angle_deg}deg\n',
                f'"h_a"= {self.h_a}\n',
                f'"h_b"= {self.h_b}\n',
                f'"clr_tip_root"= {self.clr_tip_root}\n',
                f'"h_f"= {self.h_f}\n',
                f'"planet_bore"= {self.planet_bore}\n',
                f'"motor_OD"= {self.motor_OD}\n',
                f'"motor_height"= {self.motor_height}\n',
                f'"bearing_ID"= {self.bearing_ID}\n',
                f'"bearing_OD"= {self.bearing_OD}\n',
                f'"bearing_height"= {self.bearing_height}\n',

                # ---------------- Motor Mounting & Clearances -------------
                f'"clearance_planet"= {self.clearance_planet}\n',
                f'"sec_carrier_thickness"= {self.sec_carrier_thickness}\n',
                f'"sun_coupler_hub_thickness"= {self.sun_coupler_hub_thickness}\n',
                f'"clearance_sun_coupler_sec_carrier"= {self.clearance_sun_coupler_sec_carrier}\n',
                f'"clearance_motor_and_case"= {self.clearance_motor_and_case}\n',
                f'"case_mounting_surface_height"= {self.case_mounting_surface_height}\n',
                f'"Motor_case_thickness"= {self.Motor_case_thickness}\n',
                f'"Motor_case_ID"= {self.Motor_case_ID}\n',
                f'"motor_case_OD_base"= {self.motor_case_OD_base}\n',
                f'"case_mounting_hole_dia"= {self.case_mounting_hole_dia}\n',
                f'"case_mounting_hole_shift"= {self.case_mounting_hole_shift}\n',
                f'"case_mounting_PCD"= {self.case_mounting_PCD}\n',
                f'"case_mounting_hole_allen_socket_dia"= {self.case_mounting_hole_allen_socket_dia}\n',
                f'"clearance_case_mount_holes_shell_thickness"= {self.clearance_case_mount_holes_shell_thickness}\n',
                f'"Motor_case_OD_max"= {self.Motor_case_OD_max}\n',
                f'"base_plate_thickness"= {self.base_plate_thickness}\n',

                # ---------------- Gear Geometry ---------------------------
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

                # ---------------- Derived Distances & Constraints ----------
                f'"case_dist"= {self.case_dist}\n',
                f'"bearing mount thickness"= {self.bearing_mount_thickness}\n',
                f'"output_mounting_PCD"= {self.output_mounting_PCD}\n',
                f'"carrier_PCD"= {self.carrier_PCD}\n',

                # ---------------- Motor Mount -----------------------------
                f'"motor_mount_hole_PCD"= {self.motor_mount_hole_PCD}\n',
                f'"motor_mount_hole_dia"= {self.motor_mount_hole_dia}\n',
                f'"motor_mount_hole_num"= {self.motor_mount_hole_num}\n',
                f'"motor_output_hole_PCD"= {self.motor_output_hole_PCD}\n',
                f'"motor_output_hole_dia"= {self.motor_output_hole_dia}\n',
                f'"motor_output_hole_num"= {self.motor_output_hole_num}\n',
                f'"motor_output_hole_CSK_OD"= {self.motor_output_hole_CSK_OD}\n',
                f'"motor_output_hole_CSK_head_height"= {self.motor_output_hole_CSK_head_height}\n',

                # ---------------- Bolt & Fastener Details ------------------
                f'"output_mounting_nut_thickness"= {self.output_mounting_nut_thickness}\n',
                f'"output_mounting_nut_depth"= {self.output_mounting_nut_depth}\n',
                f'"output_mounting_nut_wrench_size"= {self.output_mounting_nut_wrench_size}\n',
                f'"output_mounting_hole_dia"= {self.output_mounting_hole_dia}\n',                
                f'"case_mounting_bolt_depth"= {self.case_mounting_bolt_depth}\n',
                f'"case_mounting_wrench_size"= {self.case_mounting_wrench_size}\n',
                f'"case_mounting_nut_clearance"= {self.case_mounting_nut_clearance}\n',
                f'"case_mounting_nut_thickness"= {self.case_mounting_nut_thickness}\n',

                # ---------------- Miscellaneous Constants ------------------
                f'"central_hole_offset_from_motor_mount_PCD"= {self.central_hole_offset_from_motor_mount_PCD}\n',
                f'"wire_slot_dist_from_center"= {self.wire_slot_dist_from_center}\n',
                f'"wire_slot_length"= {self.wire_slot_length}\n',
                f'"wire_slot_radius"= {self.wire_slot_radius}\n',
                f'"driver_upper_holes_dist_from_center"= {self.driver_upper_holes_dist_from_center}\n',
                f'"driver_lower_holes_dist_from_center"= {self.driver_lower_holes_dist_from_center}\n',
                f'"driver_side_holes_dist_from_center"= {self.driver_side_holes_dist_from_center}\n',
                f'"driver_mount_holes_dia"= {self.driver_mount_holes_dia}\n',
                f'"driver_mount_inserts_OD"= {self.driver_mount_inserts_OD}\n',
                f'"driver_mount_thickness"= {self.driver_mount_thickness}\n',
                f'"driver_mount_height"= {self.driver_mount_height}\n',
                f'"air_flow_hole_offset"= {self.air_flow_hole_offset}\n',

                # ---------------- Shaft, Hub & Bearing ---------------------
                f'"ring_radial_thickness"= {self.ring_radial_thickness}\n',
                f'"ring_OD"= {self.ring_OD}\n',
                f'"ring_to_chamfer_clearance"= {self.ring_to_chamfer_clearance}\n',
                f'"Motor_case_OD_base_to_chamfer"= {self.Motor_case_OD_base_to_chamfer}\n',
                f'"pattern_offset_from_motor_case_OD_base"= {self.pattern_offset_from_motor_case_OD_base}\n',
                f'"pattern_bulge_dia"= {self.pattern_bulge_dia}\n',
                f'"pattern_num_bulge"= {self.pattern_num_bulge}\n',
                f'"pattern_depth"= {self.pattern_depth}\n',
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
                f'"fw_s_used"= {self.fw_s_used}\n',
                f'"bearing_retainer_thickness"= {self.bearing_retainer_thickness}\n',
                f'"tight_clearance_3DP" = {self.tight_clearance_3DP}\n',
                f'"loose_clearance_3DP" = {self.loose_clearance_3DP}\n'                
            ])

    def genEquationFile_old(self):
        self.setVariables()
        file_path = os.path.join(os.path.dirname(__file__), 'SSPG', 'sspg_equations.txt')
        with open(file_path, 'w') as eqFile:
            eqFile.writelines([
                # ---------------- Optimization Variables ----------------
                f'"Ns"= {self.Ns}\n',
                f'"Np"= {self.Np}\n',
                f'"Nr"= {self.Nr}\n',
                f'"module"= {self.module}\n',
                f'"num_planet"= {self.num_planet}\n',

                # ---------------- Independent Variables ------------------
                f'"pressure angle"= {self.pressure_angle_deg}deg\n',
                f'"pressure_angle"= {self.pressure_angle_deg}deg\n',
                f'"h_a"= {self.h_a}\n',
                f'"h_b"= {self.h_b}\n',
                f'"clr_tip_root"= {self.clr_tip_root}\n',
                f'"h_f"= {self.h_f}\n',
                f'"planet_bore"= {self.planet_bore}\n',
                f'"motor_OD"= {self.motor_OD}\n',
                f'"motor_height"= {self.motor_height}\n',
                f'"bearing_ID"= {self.bearing_ID}\n',
                f'"bearing_OD"= {self.bearing_OD}\n',
                f'"bearing_height"= {self.bearing_height}\n',

                # ---------------- Motor Mounting & Clearances -------------
                f'"clearance_planet"= {self.clearance_planet}\n',
                f'"sec_carrier_thickness"= {self.sec_carrier_thickness}\n',
                f'"sun_coupler_hub_thickness"= {self.sun_coupler_hub_thickness}\n',
                f'"clearance_sun_coupler_sec_carrier"= {self.clearance_sun_coupler_sec_carrier}\n',
                f'"clearance_motor_and_case"= {self.clearance_motor_and_case}\n',
                f'"case_mounting_surface_height"= {self.case_mounting_surface_height}\n',
                f'"Motor_case_thickness"= {self.Motor_case_thickness}\n',
                f'"Motor_case_ID"= {self.Motor_case_ID}\n',
                f'"motor_case_OD_base"= {self.motor_case_OD_base}\n',
                f'"case_mounting_hole_dia"= {self.case_mounting_hole_dia}\n',
                f'"case_mounting_hole_shift"= {self.case_mounting_hole_shift}\n',
                f'"case_mounting_PCD"= {self.case_mounting_PCD}\n',
                f'"case_mounting_hole_allen_socket_dia"= {self.case_mounting_hole_allen_socket_dia}\n',
                f'"clearance_case_mount_holes_shell_thickness"= {self.clearance_case_mount_holes_shell_thickness}\n',
                f'"Motor_case_OD_max"= {self.Motor_case_OD_max}\n',
                f'"base_plate_thickness"= {self.base_plate_thickness}\n',

                # ---------------- Gear Geometry ---------------------------
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

                # ---------------- Derived Distances & Constraints ----------
                f'"case_dist"= {self.case_dist}\n',
                f'"bearing mount thickness"= {self.bearing_mount_thickness}\n',
                f'"output_mounting_PCD"= {self.output_mounting_PCD}\n',
                f'"carrier_PCD"= {self.carrier_PCD}\n',

                # ---------------- Motor Mount -----------------------------
                f'"motor_mount_hole_PCD"= {self.motor_mount_hole_PCD}\n',
                f'"motor_mount_hole_dia"= {self.motor_mount_hole_dia}\n',
                f'"motor_mount_hole_num"= {self.motor_mount_hole_num}\n',
                f'"motor_output_hole_PCD"= {self.motor_output_hole_PCD}\n',
                f'"motor_output_hole_dia"= {self.motor_output_hole_dia}\n',
                f'"motor_output_hole_num"= {self.motor_output_hole_num}\n',
                f'"motor_output_hole_CSK_OD"= {self.motor_output_hole_CSK_OD}\n',
                f'"motor_output_hole_CSK_head_height"= {self.motor_output_hole_CSK_head_height}\n',

                # ---------------- Bolt & Fastener Details ------------------
                f'"output_mounting_nut_thickness"= {self.output_mounting_nut_thickness}\n',
                f'"output_mounting_nut_depth"= {self.output_mounting_nut_depth}\n',
                f'"output_mounting_nut_wrench_size"= {self.output_mounting_nut_wrench_size}\n',
                f'"output_mounting_hole_dia"= {self.output_mounting_hole_dia}\n',                
                f'"case_mounting_bolt_depth"= {self.case_mounting_bolt_depth}\n',
                f'"case_mounting_wrench_size"= {self.case_mounting_wrench_size}\n',
                f'"case_mounting_nut_clearance"= {self.case_mounting_nut_clearance}\n',
                f'"case_mounting_nut_thickness"= {self.case_mounting_nut_thickness}\n',

                # ---------------- Miscellaneous Constants ------------------
                f'"central_hole_offset_from_motor_mount_PCD"= {self.central_hole_offset_from_motor_mount_PCD}\n',
                f'"wire_slot_dist_from_center"= {self.wire_slot_dist_from_center}\n',
                f'"wire_slot_length"= {self.wire_slot_length}\n',
                f'"wire_slot_radius"= {self.wire_slot_radius}\n',
                f'"driver_upper_holes_dist_from_center"= {self.driver_upper_holes_dist_from_center}\n',
                f'"driver_lower_holes_dist_from_center"= {self.driver_lower_holes_dist_from_center}\n',
                f'"driver_side_holes_dist_from_center"= {self.driver_side_holes_dist_from_center}\n',
                f'"driver_mount_holes_dia"= {self.driver_mount_holes_dia}\n',
                f'"driver_mount_inserts_OD"= {self.driver_mount_inserts_OD}\n',
                f'"driver_mount_thickness"= {self.driver_mount_thickness}\n',
                f'"driver_mount_height"= {self.driver_mount_height}\n',
                f'"air_flow_hole_offset"= {self.air_flow_hole_offset}\n',

                # ---------------- Shaft, Hub & Bearing ---------------------
                f'"ring_radial_thickness"= {self.ring_radial_thickness}\n',
                f'"ring_OD"= {self.ring_OD}\n',
                f'"ring_to_chamfer_clearance"= {self.ring_to_chamfer_clearance}\n',
                f'"Motor_case_OD_base_to_chamfer"= {self.Motor_case_OD_base_to_chamfer}\n',
                f'"pattern_offset_from_motor_case_OD_base"= {self.pattern_offset_from_motor_case_OD_base}\n',
                f'"pattern_bulge_dia"= {self.pattern_bulge_dia}\n',
                f'"pattern_num_bulge"= {self.pattern_num_bulge}\n',
                f'"pattern_depth"= {self.pattern_depth}\n',
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
                f'"fw_s_used"= {self.fw_s_used}\n',
                f'"bearing_retainer_thickness"= {self.bearing_retainer_thickness}\n',
                f'"tight_clearance_3DP" = {self.tight_clearance_3DP}\n',
                f'"loose_clearance_3DP" = {self.loose_clearance_3DP}\n'                
            ])

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
        module    = self.planetaryGearbox.module
        Ns        = self.planetaryGearbox.Ns
        Np        = self.planetaryGearbox.Np
        Nr        = self.planetaryGearbox.Nr
        numPlanet = self.planetaryGearbox.numPlanet

        #------------------------------------
        # density of materials
        #------------------------------------
        # density of both gears and the structural materials is the same in 3D printed gearbox
        density_3DP_material = self.planetaryGearbox.densityGears

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
        # To be written in Gearbox(sspg) JSON files
        case_mounting_surface_height = self.case_mounting_surface_height
        standard_clearance_1_5mm     = self.standard_clearance_1_5mm    
        base_plate_thickness         = self.base_plate_thickness        
        Motor_case_thickness         = self.Motor_case_thickness        
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

        # To be written in Motor JSON files
        motor_output_hole_PCD = self.motor.motor_output_hole_PCD
        motor_output_hole_dia = self.motor.motor_output_hole_dia

        #--------------------------------------
        # Dependent variables
        #--------------------------------------
        h_b = 1.25 * module

        #--------------------------------------
        # Mass: sspg_motor_casing
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

        Motor_case_mass = Motor_case_volume * density_3DP_material

        #--------------------------------------
        # Mass: sspg_gearbox_casing
        #--------------------------------------
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

        gearbox_casing_mass = (ring_volume + bearing_holding_structure_volume + case_mounting_structure_volume + large_fillet_volume) * density_3DP_material

        #----------------------------------
        # Mass: sspg_carrier
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

        #----------------------------------
        # Mass: sspg_sun
        #----------------------------------
        sun_hub_dia = motor_output_hole_PCD + motor_output_hole_dia + standard_clearance_1_5mm * 4

        sun_shaft_dia    = sun_shaft_bearing_ID
        sun_shaft_height = sun_shaft_bearing_width + 2 * standard_clearance_1_5mm

        fw_s_used        = planetFwMM + clearance_planet + sec_carrier_thickness + standard_clearance_1_5mm

        sun_hub_volume   = np.pi * ((sun_hub_dia*0.5) ** 2) * sun_coupler_hub_thickness * 1e-9
        sun_gear_volume  = np.pi * ((DiaSunMM * 0.5) ** 2) * fw_s_used * 1e-9
        sun_shaft_volume = np.pi * ((sun_shaft_dia*0.5) ** 2) * sun_shaft_height * 1e-9

        sun_volume       = sun_hub_volume + sun_gear_volume + sun_shaft_volume
        sun_mass         = sun_volume * density_3DP_material

        #--------------------------------------
        # Mass: sspg_planet
        #--------------------------------------
        planet_volume = (np.pi * ((DiaPlanetMM*0.5)**2 - (planet_bore*0.5)**2) * planetFwMM) * 1e-9
        planet_mass   = planet_volume * density_3DP_material

        #--------------------------------------
        # Mass: sspg_sec_carrier
        #--------------------------------------
        sec_carrier_OD = bearing_ID
        sec_carrier_ID = (DiaSunMM + DiaPlanetMM) - planet_shaft_dia - 2 * standard_clearance_1_5mm

        sec_carrier_volume = (np.pi * ((sec_carrier_OD*0.5)**2 - (sec_carrier_ID*0.5)**2) * sec_carrier_thickness) * 1e-9
        sec_carrier_mass   = sec_carrier_volume * density_3DP_material

        #--------------------------------------
        # Mass: sspg_sun_shaft_bearing
        #--------------------------------------
        sun_shaft_bearing_mass       = 4 * 0.001 # kg

        #--------------------------------------
        # Mass: sspg_planet_bearing
        #--------------------------------------
        planet_bearing_mass          = 1 * 0.001 # kg
        planet_bearing_num           = numPlanet * 2
        planet_bearing_combined_mass = planet_bearing_mass * planet_bearing_num

        #--------------------------------------
        # Mass: sspg_planet_bearing
        #--------------------------------------
        bearing_mass = BearingMassKG # kg

        #--------------------------------------
        # Mass: sspg_bearing_retainer
        #--------------------------------------
        bearing_retainer_OD        = bearing_holding_structure_OD
        bearing_retainer_ID        = bearing_OD - standard_clearance_1_5mm * 2

        bearing_retainer_volume = (np.pi * ((bearing_retainer_OD*0.5)**2 - (bearing_retainer_ID*0.5)**2) * bearing_retainer_thickness) * 1e-9

        bearing_retainer_mass   = bearing_retainer_volume * density_3DP_material

        self.Motor_case_mass              = Motor_case_mass
        self.gearbox_casing_mass          = gearbox_casing_mass
        self.carrier_mass                 = carrier_mass
        self.sun_mass                     = sun_mass
        self.sec_carrier_mass             = sec_carrier_mass
        self.planet_mass                  = planet_mass
        self.planet_bearing_combined_mass = planet_bearing_combined_mass
        self.sun_shaft_bearing_mass       = sun_shaft_bearing_mass
        self.bearing_mass                 = bearing_mass
        self.bearing_retainer_mass        = bearing_retainer_mass

        #----------------------------------------
        # Total Actuator Mass
        #----------------------------------------
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

#-------------------------------------------------------------------------
# Compound Planetary Actuator class
#-------------------------------------------------------------------------
class compoundPlanetaryActuator:
    def __init__(self, 
                 design_parameters,
                 motor_driver_params,
                 motor                    = motor, 
                 compoundPlanetaryGearbox = compoundPlanetaryGearbox, 
                 FOS                      = 2.0, 
                 serviceFactor            = 2.0, 
                 maxGearboxDiameter       = 140.0,
                 stressAnalysisMethodName = "Lewis"):
        
        self.motor                    = motor
        self.compoundPlanetaryGearbox = compoundPlanetaryGearbox
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
        self.ringRadialWidthMM    = self.compoundPlanetaryGearbox.ringRadialWidthMM  

        #-----------------------------------------------------
        # Dependent parameters
        #-----------------------------------------------------
        self.setVariables()

    def cost(self):
        massActuator = self.getMassKG_3DP()
        effActuator  = self.compoundPlanetaryGearbox.getEfficiency()
        widthActuator = self.compoundPlanetaryGearbox.fwPlanetBigMM + self.compoundPlanetaryGearbox.fwPlanetSmallMM
        cost = massActuator - 2 * effActuator + 0.2 * widthActuator
        return cost

    def setVariables(self):
        #--------- Optimization Variable-----------
        self.Ns         = self.compoundPlanetaryGearbox.Ns
        self.Np_b       = self.compoundPlanetaryGearbox.NpBig
        self.Np_s       = self.compoundPlanetaryGearbox.NpSmall
        self.Nr         = self.Ns + self.Np_b + self.Np_s
        self.num_planet = self.compoundPlanetaryGearbox.numPlanet
        self.module     = self.compoundPlanetaryGearbox.moduleBig

        #------------------------------------------------------
        # Indepent Constant variables
        #------------------------------------------------------
        #----------------- Gear Profile --------------------
        self.pressure_angle     = self.compoundPlanetaryGearbox.getPressureAngleRad() # 20
        self.pressure_angle_deg = self.compoundPlanetaryGearbox.getPressureAngleRad() * 180 / np.pi # 20

        #-------------Clearances---------------------
        self.clearance_planet                           = self.design_params["clearance_planet"]                           # 1.5
        self.clearance_case_mount_holes_shell_thickness = self.design_params["clearance_case_mount_holes_shell_thickness"] # 1
        self.standard_clearance_1_5mm                   = self.design_params["standard_clearance_1_5mm"]                   # 1.5
        self.case_mounting_nut_clearance                = self.design_params["case_mounting_nut_clearance"]                # 2
        self.standard_fillet_1_5mm                      = self.design_params["standard_fillet_1_5mm"]                      # 1.5
        self.standard_bearing_insertion_chamfer         = self.design_params["standard_bearing_insertion_chamfer"]         # 0.5
        self.bearingIDClearanceMM                       = self.design_params["bearingIDClearanceMM"]                       # 10
        self.clearance_sun_coupler_sec_carrier          = self.design_params["clearance_sun_coupler_sec_carrier"]          # standard_clearance_1_5mm
        self.ring_to_chamfer_clearance                  = self.design_params["ring_to_chamfer_clearance"]                  # clearance_planet
        self.tight_clearance_3DP                        = self.design_params["tight_clearance_3DP"]        
        self.loose_clearance_3DP                        = self.design_params["loose_clearance_3DP"]

        #-----------Motor----------------------------
        self.motor_OD                   = self.motorDiaMM                     # 86.8
        self.motor_height               = self.motorLengthMM                  # 26.5
        self.motor_mount_hole_PCD       = self.motor.motor_mount_hole_PCD     # 32
        self.motor_mount_hole_dia       = self.motor.motor_mount_hole_dia     # 4
        self.motor_mount_hole_num       = self.motor.motor_mount_hole_num     # 4
        self.motor_output_hole_PCD      = self.motor.motor_output_hole_PCD    # 23
        self.motor_output_hole_dia      = self.motor.motor_output_hole_dia    # 4
        self.motor_output_hole_num      = self.motor.motor_output_hole_num    # 4
        self.wire_slot_dist_from_center = self.motor.wire_slot_dist_from_center # 30
        self.wire_slot_length           = self.motor.wire_slot_length         # 10
        self.wire_slot_radius           = self.motor.wire_slot_radius         # 4

        self.driver_upper_holes_dist_from_center = self.motor_driver_params["driver_upper_holes_dist_from_center"] # 23
        self.driver_lower_holes_dist_from_center = self.motor_driver_params["driver_lower_holes_dist_from_center"] # 15
        self.driver_side_holes_dist_from_center  = self.motor_driver_params["driver_side_holes_dist_from_center"]  # 20
        self.driver_mount_holes_dia              = self.motor_driver_params["driver_mount_holes_dia"]  # 2.5
        self.driver_mount_inserts_OD             = self.motor_driver_params["driver_mount_inserts_OD"] # 3.5
        self.driver_mount_thickness              = self.motor_driver_params["driver_mount_thickness"]  # 1.5
        self.driver_mount_height                 = self.motor_driver_params["driver_mount_height"]     # 4

        self.central_hole_offset_from_motor_mount_PCD = self.design_params["central_hole_offset_from_motor_mount_PCD"] # 5

        # --- Planet pin and bearing ---
        self.planet_pin_bolt_dia      = self.design_params["planet_pin_bolt_dia"] # 5
        self.planet_shaft_dia         = self.design_params["planet_shaft_dia"] # 8
        self.planet_shaft_step_offset = self.design_params["planet_shaft_step_offset"] # 1
        self.planet_bearing_OD        = self.design_params["planet_bearing_OD"] # 12
        self.planet_bearing_width     = self.design_params["planet_bearing_width"] # 3
        self.planet_bore              = self.design_params["planet_bore"] # 10

        # --- Sun coupler and sun central bolt ---
        self.sun_shaft_bearing_ID      = self.design_params["sun_shaft_bearing_ID"] # 8
        self.sun_shaft_bearing_OD      = self.design_params["sun_shaft_bearing_OD"] # 16
        self.sun_coupler_hub_thickness = self.design_params["sun_coupler_hub_thickness"] # 4
        self.sun_shaft_bearing_width   = self.design_params["sun_shaft_bearing_width"] # 4
        self.sun_central_bolt_dia      = self.design_params["sun_central_bolt_dia"] # 5

        # --- Bearings ---         
        self.bearing_retainer_thickness = self.design_params["bearing_retainer_thickness"] # 2

        # --- Carrier & Sec Carrier ---
        self.sec_carrier_thickness = self.design_params["sec_carrier_thickness"] # 5

        self.carrier_trapezoidal_support_sun_offset                 = self.design_params["carrier_trapezoidal_support_sun_offset"]# 5
        self.carrier_trapezoidal_support_hole_PCD_offset_bearing_ID = self.design_params["carrier_trapezoidal_support_hole_PCD_offset_bearing_ID"]# 4
        self.carrier_trapezoidal_support_hole_dia                   = self.design_params["carrier_trapezoidal_support_hole_dia"]# 3
        self.carrier_bearing_step_width                             = self.design_params["carrier_bearing_step_width"]# 1.5

        # --- Casings ---
        self.case_mounting_surface_height = self.design_params["case_mounting_surface_height"] # 4
        self.case_mounting_hole_dia       = self.design_params["case_mounting_hole_dia"] # 3
        self.case_mounting_bolt_depth     = self.design_params["case_mounting_bolt_depth"] # 4.5

        self.base_plate_thickness = self.design_params["base_plate_thickness"] # 4
        self.Motor_case_thickness = self.design_params["Motor_case_thickness"] # 2.5
        self.air_flow_hole_offset = self.design_params["air_flow_hole_offset"] # 3

        self.output_mounting_hole_dia  = self.design_params["output_mounting_hole_dia"]  # 4
        self.output_mounting_nut_depth = self.design_params["output_mounting_nut_depth"] # 3
        self.output_mounting_hole_num  = self.design_params["output_mounting_hole_num"]  # 4

        self.Motor_case_OD_base_to_chamfer          = self.design_params["Motor_case_OD_base_to_chamfer"] # 5
        self.pattern_offset_from_motor_case_OD_base = self.design_params["pattern_offset_from_motor_case_OD_base"] # 3
        self.pattern_bulge_dia                      = self.design_params["pattern_bulge_dia"] # 3
        self.pattern_num_bulge                      = self.design_params["pattern_num_bulge"] # 18
        self.pattern_depth                          = self.design_params["pattern_depth"] # 2

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
        self.fw_s_calc = self.compoundPlanetaryGearbox.fwSunMM

        self.dp_p_b    = self.module * self.Np_b
        self.db_p_b    = self.dp_p_b * np.cos((self.pressure_angle))
        self.alpha_p_b = (np.sqrt(self.dp_p_b ** 2 - self.db_p_b ** 2) / self.db_p_b) * 180 / np.pi - self.pressure_angle_deg
        self.beta_p_b  = (360 / (4 * self.Np_b) - self.alpha_p_b) * 2
        self.fw_p_b    = self.compoundPlanetaryGearbox.fwPlanetBigMM
        
        self.dp_r    = self.module * self.Nr
        self.db_r    = self.dp_r * np.cos((self.pressure_angle))
        self.alpha_r = (np.sqrt(self.dp_r ** 2 - self.db_r ** 2) / self.db_r) * 180 / np.pi - self.pressure_angle_deg
        self.beta_r  = (360 / (4 * self.Nr) + self.alpha_r) * 2
        self.fw_r    = self.compoundPlanetaryGearbox.fwRingMM

        self.dp_p_s    = self.module * self.Np_s
        self.db_p_s    = self.dp_p_s * np.cos((self.pressure_angle))
        self.alpha_p_s = (np.sqrt(self.dp_p_s ** 2 - self.db_p_s ** 2) / self.db_p_s) * 180 / np.pi - self.pressure_angle_deg
        self.beta_p_s  = (360 / (4 * self.Np_s) - self.alpha_p_s) * 2
        self.fw_p_s    = self.fw_r + self.clearance_planet

        # --- Motor ---
        motor_output_hole_bolt = nuts_and_bolts_dimensions(bolt_dia = self.motor_output_hole_dia, bolt_type="CSK")

        self.motor_output_hole_CSK_OD          = motor_output_hole_bolt.bolt_head_dia   
        self.motor_output_hole_CSK_head_height = motor_output_hole_bolt.bolt_head_height

        # --- Planet Pin and Bearing ---
        planet_pin_bolt = nuts_and_bolts_dimensions(bolt_dia=self.planet_pin_bolt_dia, bolt_type="socket_head")

        self.planet_pin_socket_head_dia  = planet_pin_bolt.bolt_head_dia # 8.5
        self.planet_pin_bolt_wrench_size = planet_pin_bolt.nut_width_across_flats # 8        

        # --- Sun coupler and sun central bolt ---
        sun_central_bolt = nuts_and_bolts_dimensions(bolt_dia = self.sun_central_bolt_dia, bolt_type="socket_head")
        self.sun_central_bolt_socket_head_dia = sun_central_bolt.bolt_head_dia # 8.5
        
        self.sun_hub_dia = self.motor_output_hole_PCD + self.motor_output_hole_dia + self.standard_clearance_1_5mm * 4

        #----------------------- Bearings------------------------------------
        IdrequiredMM = self.module * (self.Ns + self.Np_b) + self.bearingIDClearanceMM
        Bearings            = bearings_discrete(IdrequiredMM)
        self.bearing_ID     = Bearings.getBearingIDMM()
        self.bearing_OD     = Bearings.getBearingODMM()
        self.bearing_height = Bearings.getBearingWidthMM()

        #------------------- Carrier & Sec Carrier-----------------------------
        self.carrier_PCD = (self.Np_b + self.Ns) * self.module
        
        carrier_trapezoidal_support_hole = nuts_and_bolts_dimensions(bolt_dia=self.carrier_trapezoidal_support_hole_dia, bolt_type="socket_head")

        self.carrier_trapezoidal_support_hole_socket_head_dia = carrier_trapezoidal_support_hole.bolt_head_dia
        self.carrier_trapezoidal_support_hole_wrench_size     = carrier_trapezoidal_support_hole.nut_width_across_flats        

        #--------------------- Casings------------------------------------------
        case_mounting_hole_bolt = nuts_and_bolts_dimensions(bolt_dia=self.case_mounting_hole_dia, bolt_type="socket_head")

        self.case_mounting_hole_allen_socket_dia = case_mounting_hole_bolt.bolt_head_dia # 5.5
        self.case_mounting_wrench_size           = case_mounting_hole_bolt.nut_width_across_flats # 5.5
        self.case_mounting_nut_thickness         = case_mounting_hole_bolt.nut_thickness # 2.4

        output_mounting_hole_bolt = nuts_and_bolts_dimensions(bolt_dia=self.output_mounting_hole_dia, bolt_type="socket_head")

        self.output_mounting_nut_thickness   = output_mounting_hole_bolt.nut_thickness # 3.2
        self.output_mounting_nut_wrench_size = output_mounting_hole_bolt.nut_width_across_flats # 7

        self.case_dist = self.sec_carrier_thickness + self.clearance_planet * 2 + self.sun_coupler_hub_thickness + self.fw_p_b - self.case_mounting_surface_height
        self.case_mounting_hole_shift = self.case_mounting_hole_dia / 2 - 0.5

        # IIF: clearance_motor_and_case
        if (self.Ns + self.Np_b * 2) * self.module < self.motor_OD:
            self.clearance_motor_and_case = 5
        else:
            self.clearance_motor_and_case = ((self.Ns + self.Np_b * 2) * self.module - self.motor_OD) * 0.5 + 5

        self.Motor_case_ID = self.motor_OD + self.clearance_motor_and_case * 2
        self.motor_case_OD_base = self.motor_OD + self.clearance_motor_and_case * 2 + self.Motor_case_thickness * 2
        self.case_mounting_PCD = self.motor_case_OD_base + self.case_mounting_hole_shift * 2
        self.Motor_case_OD_max = self.case_mounting_PCD + self.case_mounting_hole_allen_socket_dia + self.clearance_case_mount_holes_shell_thickness * 2

        # IIF: bearing_mount_thickness
        if (self.bearing_OD + self.output_mounting_hole_dia * 4) > (self.Nr * self.module + 2 * self.h_b):
            self.bearing_mount_thickness = self.output_mounting_hole_dia * 2
        else:
            self.bearing_mount_thickness = ((self.Nr * self.module + 2 * self.h_b - (self.bearing_OD + self.output_mounting_hole_dia * 4)) / 2) + self.output_mounting_hole_dia * 2 + self.standard_clearance_1_5mm

        self.output_mounting_PCD = self.bearing_OD + self.bearing_mount_thickness

        # IIF: ring_radial_thickness
        if self.Nr * self.module + 5 * 2 > self.bearing_OD:
            self.ring_radial_thickness = 5
        else:
            self.ring_radial_thickness = (self.bearing_OD + self.standard_clearance_1_5mm * 2 - self.Nr * self.module) / 2

        self.ring_OD = self.Nr * self.module + self.ring_radial_thickness * 2
        self.fw_s_used = self.fw_p_s + self.fw_p_b + self.clearance_planet + self.sec_carrier_thickness + self.standard_clearance_1_5mm #TODO: Move to bottom

        #-----
        self.actuator_width =  (self.fw_r
                               + self.clearance_planet
                               + self.bearing_height
                               + self.clearance_planet
                               + self.case_dist
                               + self.bearing_retainer_thickness
                               + self.motor_height
                               + self.case_mounting_surface_height
                               + self.standard_clearance_1_5mm
                               + self.base_plate_thickness)
                                                               
    def genEquationFile(self, motor_name="NO_MOTOR", gearRatioLL = 0.0, gearRatioUL = 0.0):
        # writing values into text file imported which is imported into solidworks
        self.setVariables()
        file_path = os.path.join(os.path.dirname(__file__), 'CPG', 'Equation_Files', motor_name, f'cpg_equations_{gearRatioLL}_{gearRatioUL}.txt')
        with open(file_path, 'w') as eqFile:
            l = [
                    f'"Ns"= {self.Ns}\n',
                    f'"Np_b"= {self.Np_b}\n',
                    f'"Np_s"= {self.Np_s}\n',
                    f'"Nr"= {self.Nr}\n',
                    f'"num_planet"= {self.num_planet}\n',
                    f'"module"= {self.module}\n',
                    f'"motor_OD"= {self.motor_OD}\n',
                    f'"motor_height"= {self.motor_height}\n',
                    f'"pressure_angle"= {self.pressure_angle_deg}\n',
                    f'"pressure angle"= {self.pressure_angle_deg}\n',
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
                    f'"case_dist"= {self.case_dist}\n',
                    f'"Motor_case_OD_max"= {self.Motor_case_OD_max}\n',
                    f'"case_mounting_PCD"= {self.case_mounting_PCD}\n',
                    f'"bearing_mount_thickness"= {self.bearing_mount_thickness}\n',
                    f'"case_mounting_hole_dia"= {self.case_mounting_hole_dia}\n',
                    f'"output_mounting_PCD"= {self.output_mounting_PCD}\n',
                    f'"output_mounting_hole_dia"= {self.output_mounting_hole_dia}\n',
                    f'"clearance_case_mount_holes_shell_thickness"= {self.clearance_case_mount_holes_shell_thickness}\n',
                    f'"motor_case_OD_base"= {self.motor_case_OD_base}\n',
                    f'"sec_carrier_thickness"= {self.sec_carrier_thickness}\n',
                    f'"sun_coupler_hub_thickness"= {self.sun_coupler_hub_thickness}\n',
                    f'"clearance_sun_coupler_sec_carrier"= {self.clearance_sun_coupler_sec_carrier}\n',
                    f'"clearance_motor_and_case"= {self.clearance_motor_and_case}\n',
                    f'"Motor_case_thickness"= {self.Motor_case_thickness}\n',
                    f'"Motor_case_ID"= {self.Motor_case_ID}\n',
                    f'"case_mounting_hole_shift"= {self.case_mounting_hole_shift}\n',
                    f'"output_mounting_nut_wrench_size"= {self.output_mounting_nut_wrench_size}\n',
                    f'"output_mounting_nut_thickness"= {self.output_mounting_nut_thickness}\n',
                    f'"case_mounting_hole_allen_socket_dia"= {self.case_mounting_hole_allen_socket_dia}\n',
                    f'"output_mounting_nut_depth"= {self.output_mounting_nut_depth}\n',
                    f'"case_mounting_bolt_depth"= {self.case_mounting_bolt_depth}\n',
                    f'"ring_radial_thickness"= {self.ring_radial_thickness}\n',
                    f'"ring_OD"= {self.ring_OD}\n',
                    f'"ring_to_chamfer_clearance"= {self.ring_to_chamfer_clearance}\n',
                    f'"Motor_case_OD_base_to_chamfer"= {self.Motor_case_OD_base_to_chamfer}\n',
                    f'"pattern_offset_from_motor_case_OD_base"= {self.pattern_offset_from_motor_case_OD_base}\n',
                    f'"pattern_bulge_dia"= {self.pattern_bulge_dia}\n',
                    f'"pattern_num_bulge"= {self.pattern_num_bulge}\n',
                    f'"pattern_depth"= {self.pattern_depth}\n',
                    f'"case_mounting_wrench_size"= {self.case_mounting_wrench_size}\n',
                    f'"case_mounting_nut_clearance"= {self.case_mounting_nut_clearance}\n',
                    f'"base_plate_thickness"= {self.base_plate_thickness}\n',
                    f'"case_mounting_nut_thickness"= {self.case_mounting_nut_thickness}\n',
                    f'"case_mounting_surface_height"= {self.case_mounting_surface_height}\n',
                    f'"motor_mount_hole_PCD"= {self.motor_mount_hole_PCD}\n',
                    f'"motor_mount_hole_dia"= {self.motor_mount_hole_dia}\n',
                    f'"motor_mount_hole_num"= {self.motor_mount_hole_num}\n',
                    f'"central_hole_offset_from_motor_mount_PCD"= {self.central_hole_offset_from_motor_mount_PCD}\n',
                    f'"wire_slot_dist_from_center"= {self.wire_slot_dist_from_center}\n',
                    f'"wire_slot_length"= {self.wire_slot_length}\n',
                    f'"wire_slot_radius"= {self.wire_slot_radius}\n',
                    f'"driver_upper_holes_dist_from_center"= {self.driver_upper_holes_dist_from_center}\n',
                    f'"driver_lower_holes_dist_from_center"= {self.driver_lower_holes_dist_from_center}\n',
                    f'"driver_side_holes_dist_from_center"= {self.driver_side_holes_dist_from_center}\n',
                    f'"driver_mount_holes_dia"= {self.driver_mount_holes_dia}\n',
                    f'"driver_mount_inserts_OD"= {self.driver_mount_inserts_OD}\n',
                    f'"driver_mount_thickness"= {self.driver_mount_thickness}\n',
                    f'"driver_mount_height"= {self.driver_mount_height}\n',
                    f'"air_flow_hole_offset"= {self.air_flow_hole_offset}\n',
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
                    f'"standard_bearing_insertion_chamfer"= {self.standard_bearing_insertion_chamfer}\n',
                    f'"carrier_trapezoidal_support_hole_wrench_size"= {self.carrier_trapezoidal_support_hole_wrench_size}\n',
                    f'"planet_pin_bolt_wrench_size"= {self.planet_pin_bolt_wrench_size}\n',
                    f'"planet_bearing_OD"= {self.planet_bearing_OD}\n',
                    f'"planet_bearing_width"= {self.planet_bearing_width}\n',
                    f'"planet_bore"= {self.planet_bore}\n',
                    f'"motor_output_hole_PCD"= {self.motor_output_hole_PCD}\n',
                    f'"motor_output_hole_dia"= {self.motor_output_hole_dia}\n',
                    f'"motor_output_hole_num"= {self.motor_output_hole_num}\n',
                    f'"sun_shaft_bearing_ID"= {self.sun_shaft_bearing_ID}\n',
                    f'"sun_hub_dia"= {self.sun_hub_dia}\n',
                    f'"sun_central_bolt_dia"= {self.sun_central_bolt_dia}\n',
                    f'"sun_central_bolt_socket_head_dia"= {self.sun_central_bolt_socket_head_dia}\n',
                    f'"fw_s_used"= {self.fw_s_used}\n',
                    f'"motor_output_hole_CSK_OD"= {self.motor_output_hole_CSK_OD}\n',
                    f'"motor_output_hole_CSK_head_height"= {self.motor_output_hole_CSK_head_height}\n',
                    f'"bearing_retainer_thickness"= {self.bearing_retainer_thickness}\n',
                    f'"fw_p_b"= {self.fw_p_b}\n',
                    f'"dp_p_s"= {self.dp_p_s}\n',
                    f'"db_p_s"= {self.db_p_s}\n',
                    f'"alpha_p_s"= {self.alpha_p_s}\n',
                    f'"beta_p_s"= {self.beta_p_s}\n',
                    f'"tight_clearance_3DP" = {self.tight_clearance_3DP}\n',
                    f'"loose_clearance_3DP" = {self.loose_clearance_3DP}\n' 
            ]
            eqFile.writelines(l)
        eqFile.close()

    def genEquationFile_old(self):
        # writing values into text file imported which is imported into solidworks
        self.setVariables()
        file_path = os.path.join(os.path.dirname(__file__), 'CPG', 'cpg_equations.txt')
        with open(file_path, 'w') as eqFile:
            l = [
                    f'"Ns"= {self.Ns}\n',
                    f'"Np_b"= {self.Np_b}\n',
                    f'"Np_s"= {self.Np_s}\n',
                    f'"Nr"= {self.Nr}\n',
                    f'"num_planet"= {self.num_planet}\n',
                    f'"module"= {self.module}\n',
                    f'"motor_OD"= {self.motor_OD}\n',
                    f'"motor_height"= {self.motor_height}\n',
                    f'"pressure_angle"= {self.pressure_angle_deg}\n',
                    f'"pressure angle"= {self.pressure_angle_deg}\n',
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
                    f'"case_dist"= {self.case_dist}\n',
                    f'"Motor_case_OD_max"= {self.Motor_case_OD_max}\n',
                    f'"case_mounting_PCD"= {self.case_mounting_PCD}\n',
                    f'"bearing_mount_thickness"= {self.bearing_mount_thickness}\n',
                    f'"case_mounting_hole_dia"= {self.case_mounting_hole_dia}\n',
                    f'"output_mounting_PCD"= {self.output_mounting_PCD}\n',
                    f'"output_mounting_hole_dia"= {self.output_mounting_hole_dia}\n',
                    f'"clearance_case_mount_holes_shell_thickness"= {self.clearance_case_mount_holes_shell_thickness}\n',
                    f'"motor_case_OD_base"= {self.motor_case_OD_base}\n',
                    f'"sec_carrier_thickness"= {self.sec_carrier_thickness}\n',
                    f'"sun_coupler_hub_thickness"= {self.sun_coupler_hub_thickness}\n',
                    f'"clearance_sun_coupler_sec_carrier"= {self.clearance_sun_coupler_sec_carrier}\n',
                    f'"clearance_motor_and_case"= {self.clearance_motor_and_case}\n',
                    f'"Motor_case_thickness"= {self.Motor_case_thickness}\n',
                    f'"Motor_case_ID"= {self.Motor_case_ID}\n',
                    f'"case_mounting_hole_shift"= {self.case_mounting_hole_shift}\n',
                    f'"output_mounting_nut_wrench_size"= {self.output_mounting_nut_wrench_size}\n',
                    f'"output_mounting_nut_thickness"= {self.output_mounting_nut_thickness}\n',
                    f'"case_mounting_hole_allen_socket_dia"= {self.case_mounting_hole_allen_socket_dia}\n',
                    f'"output_mounting_nut_depth"= {self.output_mounting_nut_depth}\n',
                    f'"case_mounting_bolt_depth"= {self.case_mounting_bolt_depth}\n',
                    f'"ring_radial_thickness"= {self.ring_radial_thickness}\n',
                    f'"ring_OD"= {self.ring_OD}\n',
                    f'"ring_to_chamfer_clearance"= {self.ring_to_chamfer_clearance}\n',
                    f'"Motor_case_OD_base_to_chamfer"= {self.Motor_case_OD_base_to_chamfer}\n',
                    f'"pattern_offset_from_motor_case_OD_base"= {self.pattern_offset_from_motor_case_OD_base}\n',
                    f'"pattern_bulge_dia"= {self.pattern_bulge_dia}\n',
                    f'"pattern_num_bulge"= {self.pattern_num_bulge}\n',
                    f'"pattern_depth"= {self.pattern_depth}\n',
                    f'"case_mounting_wrench_size"= {self.case_mounting_wrench_size}\n',
                    f'"case_mounting_nut_clearance"= {self.case_mounting_nut_clearance}\n',
                    f'"base_plate_thickness"= {self.base_plate_thickness}\n',
                    f'"case_mounting_nut_thickness"= {self.case_mounting_nut_thickness}\n',
                    f'"case_mounting_surface_height"= {self.case_mounting_surface_height}\n',
                    f'"motor_mount_hole_PCD"= {self.motor_mount_hole_PCD}\n',
                    f'"motor_mount_hole_dia"= {self.motor_mount_hole_dia}\n',
                    f'"motor_mount_hole_num"= {self.motor_mount_hole_num}\n',
                    f'"central_hole_offset_from_motor_mount_PCD"= {self.central_hole_offset_from_motor_mount_PCD}\n',
                    f'"wire_slot_dist_from_center"= {self.wire_slot_dist_from_center}\n',
                    f'"wire_slot_length"= {self.wire_slot_length}\n',
                    f'"wire_slot_radius"= {self.wire_slot_radius}\n',
                    f'"driver_upper_holes_dist_from_center"= {self.driver_upper_holes_dist_from_center}\n',
                    f'"driver_lower_holes_dist_from_center"= {self.driver_lower_holes_dist_from_center}\n',
                    f'"driver_side_holes_dist_from_center"= {self.driver_side_holes_dist_from_center}\n',
                    f'"driver_mount_holes_dia"= {self.driver_mount_holes_dia}\n',
                    f'"driver_mount_inserts_OD"= {self.driver_mount_inserts_OD}\n',
                    f'"driver_mount_thickness"= {self.driver_mount_thickness}\n',
                    f'"driver_mount_height"= {self.driver_mount_height}\n',
                    f'"air_flow_hole_offset"= {self.air_flow_hole_offset}\n',
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
                    f'"standard_bearing_insertion_chamfer"= {self.standard_bearing_insertion_chamfer}\n',
                    f'"carrier_trapezoidal_support_hole_wrench_size"= {self.carrier_trapezoidal_support_hole_wrench_size}\n',
                    f'"planet_pin_bolt_wrench_size"= {self.planet_pin_bolt_wrench_size}\n',
                    f'"planet_bearing_OD"= {self.planet_bearing_OD}\n',
                    f'"planet_bearing_width"= {self.planet_bearing_width}\n',
                    f'"planet_bore"= {self.planet_bore}\n',
                    f'"motor_output_hole_PCD"= {self.motor_output_hole_PCD}\n',
                    f'"motor_output_hole_dia"= {self.motor_output_hole_dia}\n',
                    f'"motor_output_hole_num"= {self.motor_output_hole_num}\n',
                    f'"sun_shaft_bearing_ID"= {self.sun_shaft_bearing_ID}\n',
                    f'"sun_hub_dia"= {self.sun_hub_dia}\n',
                    f'"sun_central_bolt_dia"= {self.sun_central_bolt_dia}\n',
                    f'"sun_central_bolt_socket_head_dia"= {self.sun_central_bolt_socket_head_dia}\n',
                    f'"fw_s_used"= {self.fw_s_used}\n',
                    f'"motor_output_hole_CSK_OD"= {self.motor_output_hole_CSK_OD}\n',
                    f'"motor_output_hole_CSK_head_height"= {self.motor_output_hole_CSK_head_height}\n',
                    f'"bearing_retainer_thickness"= {self.bearing_retainer_thickness}\n',
                    f'"fw_p_b"= {self.fw_p_b}\n',
                    f'"dp_p_s"= {self.dp_p_s}\n',
                    f'"db_p_s"= {self.db_p_s}\n',
                    f'"alpha_p_s"= {self.alpha_p_s}\n',
                    f'"beta_p_s"= {self.beta_p_s}\n',
                    f'"tight_clearance_3DP" = {self.tight_clearance_3DP}\n',
                    f'"loose_clearance_3DP" = {self.loose_clearance_3DP}\n' 
            ]
            eqFile.writelines(l)
        eqFile.close()

    #--------------------------------------------
    # Gear tooth stress analysis
    #--------------------------------------------
    def getToothForces(self, constraintCheck=True):
        if constraintCheck:
            # Check if the constraints are satisfied
            if not self.compoundPlanetaryGearbox.geometricConstraint():
                print("Geometric constraint not satisfied")
                return
            if not self.compoundPlanetaryGearbox.meshingConstraint():
                print("Meshing constraint not satisfied")
                return
            if not self.compoundPlanetaryGearbox.noPlanetInterferenceConstraint():
                print("No planet interference constraint not satisfied")
                return

        Ns          = self.compoundPlanetaryGearbox.Ns
        NpBig       = self.compoundPlanetaryGearbox.NpBig
        NpSmall     = self.compoundPlanetaryGearbox.NpSmall
        Nr          = self.compoundPlanetaryGearbox.Nr
        numPlanet   = self.compoundPlanetaryGearbox.numPlanet
        moduleBig   = self.compoundPlanetaryGearbox.moduleBig
        moduleSmall = self.compoundPlanetaryGearbox.moduleSmall

        Rs_Mt = self.compoundPlanetaryGearbox.getPCRadiusSunM()
        RpBig_Mt = self.compoundPlanetaryGearbox.getPCRadiusPlanetBigM()
        RpSmall_Mt = self.compoundPlanetaryGearbox.getPCRadiusPlanetSmallM()
        Rr_Mt = self.compoundPlanetaryGearbox.getPCRadiusRingM()

        wSun     = self.motor.getMaxMotorAngVelRadPerSec()
        wPlanet  = (-Ns / (NpBig + NpSmall) ) * wSun
        wCarrier = wSun/self.compoundPlanetaryGearbox.gearRatio()

        Ft_sp = (self.serviceFactor*self.motor.getMaxMotorTorque()) / (numPlanet * Rs_Mt)
        Ft_rp = ((self.serviceFactor*self.motor.getMaxMotorTorque()) * RpBig_Mt) / (numPlanet * Rs_Mt * RpSmall_Mt)

        Ft = [Ft_sp, Ft_rp]
        return Ft

    def lewisStressAnalysisMinFacewidth(self):
        # Check if the constraints are satisfied
        if not self.compoundPlanetaryGearbox.geometricConstraint():
            print("Geometric constraint not satisfied")
            return
        if not self.compoundPlanetaryGearbox.meshingConstraint():
            print("Meshing constraint not satisfied")
            return
        if not self.compoundPlanetaryGearbox.noPlanetInterferenceConstraint():
            print("No planet interference constraint not satisfied")
            return

        Ns          = self.compoundPlanetaryGearbox.Ns
        NpBig       = self.compoundPlanetaryGearbox.NpBig
        NpSmall     = self.compoundPlanetaryGearbox.NpSmall
        Nr          = self.compoundPlanetaryGearbox.Nr
        numPlanet   = self.compoundPlanetaryGearbox.numPlanet
        moduleBig   = self.compoundPlanetaryGearbox.moduleBig
        moduleSmall = self.compoundPlanetaryGearbox.moduleSmall

        wSun     = self.motor.getMaxMotorAngVelRadPerSec()
        wPlanet  = (-Ns / (NpBig + NpSmall) ) * wSun
        wCarrier = wSun/self.compoundPlanetaryGearbox.gearRatio()

        [Ft_sp, Ft_rp] = self.getToothForces(constraintCheck=False)

        ySun         = 0.154 - 0.912/Ns
        yPlanetBig   = 0.154 - 0.912/NpBig
        yPlanetSmall = 0.154 - 0.912/NpSmall
        yRing        = 0.154 - 0.912/Nr

        V_sp = (self.compoundPlanetaryGearbox.getPCRadiusSunM() * wSun)
        V_rp = (wCarrier*(self.compoundPlanetaryGearbox.getPCRadiusSunM() + self.compoundPlanetaryGearbox.getPCRadiusPlanetBigM()) + 
                wPlanet*(self.compoundPlanetaryGearbox.getPCRadiusPlanetSmallM()))
        
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
        bMin_sun         = (self.FOS * Ft_sp / (self.compoundPlanetaryGearbox.maxGearAllowableStressPa * ySun * Kv_sun * P_big)) # m
        bMin_planetBig   = (self.FOS * Ft_sp / (self.compoundPlanetaryGearbox.maxGearAllowableStressPa * yPlanetBig * Kv_planetBig * P_big))
        bMin_planetSmall = (self.FOS * Ft_rp / (self.compoundPlanetaryGearbox.maxGearAllowableStressPa * yPlanetSmall * Kv_planetSmall * P_small))
        bMin_ring        = (self.FOS * Ft_rp / (self.compoundPlanetaryGearbox.maxGearAllowableStressPa * yRing * Kv_ring * P_small))

        if bMin_ring < bMin_planetSmall:
            bMin_ring = bMin_planetSmall
        else:
            bMin_planetSmall = bMin_ring

        self.compoundPlanetaryGearbox.setfwSunMM(bMin_sun*1000)
        self.compoundPlanetaryGearbox.setfwPlanetBigMM(bMin_planetBig*1000)
        self.compoundPlanetaryGearbox.setfwPlanetSmallMM(bMin_planetSmall*1000)
        self.compoundPlanetaryGearbox.setfwRingMM(bMin_ring*1000)

        # print(f"Lewis:")
        # print(f"bMin_planetSmall = {bMin_planetSmall}")
        # print(f"bMin_planetBig = {bMin_planetBig}")
        # print(f"bMin_sun = {bMin_sun}")
        # print(f"bMin_ring = {bMin_ring}")

    def mitStressAnalysisMinFacewidth(self):
        if not self.compoundPlanetaryGearbox.geometricConstraint():
            print("Geometric constraint not satisfied")
            return
        if not self.compoundPlanetaryGearbox.meshingConstraint():
            print("Meshing constraint not satisfied")
            return
        if not self.compoundPlanetaryGearbox.noPlanetInterferenceConstraint():
            print("No planet interference constraint not satisfied")
            return

        Ns          = self.compoundPlanetaryGearbox.Ns
        NpBig       = self.compoundPlanetaryGearbox.NpBig
        NpSmall     = self.compoundPlanetaryGearbox.NpSmall
        Nr          = self.compoundPlanetaryGearbox.Nr
        numPlanet   = self.compoundPlanetaryGearbox.numPlanet
        moduleBig   = self.compoundPlanetaryGearbox.moduleBig
        moduleSmall = self.compoundPlanetaryGearbox.moduleSmall

        wSun     = self.motor.getMaxMotorAngVelRadPerSec()
        wPlanet  = (-Ns / (NpBig + NpSmall) ) * wSun
        wCarrier = wSun/self.compoundPlanetaryGearbox.gearRatio()

        [Ft_sp, Ft_rp] = self.getToothForces(constraintCheck=False)

        # Lewis static load capacity
        _,_,CR_SP = self.compoundPlanetaryGearbox.contactRatio_sunPlanet()
        _,_,CR_PR = self.compoundPlanetaryGearbox.contactRatio_planetRing()

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
        bMin_sun_mit         = (self.FOS * Ft_sp * qe1 * qk1 / (self.compoundPlanetaryGearbox.maxGearAllowableStressPa * moduleBig * 0.001)) # m
        bMin_planetBig_mit   = (self.FOS * Ft_sp * qe1 * qk1 / (self.compoundPlanetaryGearbox.maxGearAllowableStressPa * moduleBig * 0.001))
        bMin_planetSmall_mit = (self.FOS * Ft_rp * qe2 * qk2 / (self.compoundPlanetaryGearbox.maxGearAllowableStressPa * moduleSmall * 0.001))
        bMin_ring_mit        = (self.FOS * Ft_rp * qe2 * qk2 / (self.compoundPlanetaryGearbox.maxGearAllowableStressPa * moduleSmall * 0.001))

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


        self.compoundPlanetaryGearbox.setfwSunMM         ( bMin_sun_mit         * 1000)
        self.compoundPlanetaryGearbox.setfwPlanetBigMM   ( bMin_planetBig_mit   * 1000)
        self.compoundPlanetaryGearbox.setfwPlanetSmallMM ( bMin_planetSmall_mit * 1000)
        self.compoundPlanetaryGearbox.setfwRingMM        ( bMin_ring_mit        * 1000)

        return bMin_sun_mitMM, bMin_planetBig_mitMM, bMin_planetSmall_mitMM, bMin_ring_mitMM

    def AGMAStressAnalysisMinFacewidth(self):
        # Check if the constraints are satisfied
        if not self.compoundPlanetaryGearbox.geometricConstraint():
            print("Geometric constraint not satisfied")
            return
        if not self.compoundPlanetaryGearbox.meshingConstraint():
            print("Meshing constraint not satisfied")
            return
        if not self.compoundPlanetaryGearbox.noPlanetInterferenceConstraint():
            print("No planet interference constraint not satisfied")
            return

        Ns          = self.compoundPlanetaryGearbox.Ns
        NpBig       = self.compoundPlanetaryGearbox.NpBig
        NpSmall     = self.compoundPlanetaryGearbox.NpSmall
        Nr          = self.compoundPlanetaryGearbox.Nr
        numPlanet   = self.compoundPlanetaryGearbox.numPlanet
        moduleBig   = self.compoundPlanetaryGearbox.moduleBig
        moduleSmall = self.compoundPlanetaryGearbox.moduleSmall

        wSun     = self.motor.getMaxMotorAngVelRadPerSec()
        wPlanet  = (-Ns / (NpBig + NpSmall) ) * wSun
        wCarrier = wSun/self.compoundPlanetaryGearbox.gearRatio()

        pressureAngle = self.compoundPlanetaryGearbox.pressureAngleDEG

        [Wt_sp, Wt_rp] = self.getToothForces(constraintCheck=False)

        # T Krishna Rao - Design of Machine Elements - II pg.191
        # Modified Lewis Form Factor Y = pi*y for pressure angle = 20
        Y_sun         = (0.154 - 0.912 / Ns) * np.pi
        Y_planetBig   = (0.154 - 0.912 / NpBig) * np.pi
        Y_planetSmall = (0.154 - 0.912 / NpSmall) * np.pi
        Y_ring        = (0.154 - 0.912 / Nr) * np.pi

        V_sp = abs(self.compoundPlanetaryGearbox.getPCRadiusSunM() * wSun)
        V_rp = abs(wCarrier*(self.compoundPlanetaryGearbox.getPCRadiusSunM() + self.compoundPlanetaryGearbox.getPCRadiusPlanetBigM()) + 
                wPlanet*(self.compoundPlanetaryGearbox.getPCRadiusPlanetSmallM()))
        
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
        bMin_planetSmall = (self.FOS * Wt_rp * Kv_planetSmall * Ks * Kh_planet * Kb)/(moduleSmall * Yj_planetSmall * self.compoundPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        bMin_planetBig = (self.FOS * Wt_sp * Kv_planetBig * Ks * Kh_planet * Kb)/(moduleBig * Yj_planetBig * self.compoundPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        bMin_sun = (self.FOS * Wt_sp * Kv_sun * Ks * Kh_sun * Kb) / (moduleBig * Yj_sun * self.compoundPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        bMin_ring = (self.FOS * Wt_rp * Kv_ring * Ks * Kh_ring * Kb) / (moduleSmall * Yj_ring * self.compoundPlanetaryGearbox.maxGearAllowableStressPa * 0.001)

        if bMin_ring < bMin_planetSmall:
            bMin_ring = bMin_planetSmall
        else:
            bMin_planetSmall = bMin_ring

        self.compoundPlanetaryGearbox.setfwSunMM(bMin_sun*1000)
        self.compoundPlanetaryGearbox.setfwPlanetBigMM(bMin_planetBig*1000)
        self.compoundPlanetaryGearbox.setfwPlanetSmallMM(bMin_planetSmall*1000)
        self.compoundPlanetaryGearbox.setfwRingMM(bMin_ring*1000)

    def updateFacewidth(self):
        if self.stressAnalysisMethodName == "Lewis":
            self.lewisStressAnalysisMinFacewidth()
        elif self.stressAnalysisMethodName == "AGMA":
            self.AGMAStressAnalysisMinFacewidth()
        elif self.stressAnalysisMethodName == "MIT":
            self.mitStressAnalysisMinFacewidth()

    def getMassKG_3DP(self):
        module1   = self.compoundPlanetaryGearbox.moduleBig  # Module of the gear
        module2   = self.compoundPlanetaryGearbox.moduleSmall  # Module of the gear
        Ns        = self.compoundPlanetaryGearbox.Ns
        Np1       = self.compoundPlanetaryGearbox.NpBig
        Np2       = self.compoundPlanetaryGearbox.NpSmall
        Nr        = self.compoundPlanetaryGearbox.Nr
        numPlanet = self.compoundPlanetaryGearbox.numPlanet

        #-----------------------------------------
        # Density
        #-----------------------------------------
        density_3DP_material = self.compoundPlanetaryGearbox.densityGears

        #-----------------------------------------
        # Face Width
        #-----------------------------------------
        sunFwMM     = self.compoundPlanetaryGearbox.fwSunMM
        planet1FwMM = self.compoundPlanetaryGearbox.fwPlanetBigMM
        planet2FwMM = self.compoundPlanetaryGearbox.fwPlanetSmallMM
        ringFwMM    = self.compoundPlanetaryGearbox.fwRingMM

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

        RingOuterRadiusMM = RadiusRingMM + self.compoundPlanetaryGearbox.ringRadialWidthMM

        #-----------------------------------------
        # Bearing Selection
        #-----------------------------------------
        IdrequiredMM      = module1 * (Ns + Np1) + self.bearingIDClearanceMM
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
        # To be written in Gearbox(cpg) JSON files
        case_mounting_surface_height   = self.case_mounting_surface_height
        standard_clearance_1_5mm       = self.standard_clearance_1_5mm    
        base_plate_thickness           = self.base_plate_thickness        
        Motor_case_thickness           = self.Motor_case_thickness        
        clearance_planet               = self.clearance_planet            
        output_mounting_hole_dia       = self.output_mounting_hole_dia    
        sec_carrier_thickness          = self.sec_carrier_thickness       
        sun_coupler_hub_thickness      = self.sun_coupler_hub_thickness   
        sun_shaft_bearing_OD           = self.sun_shaft_bearing_OD        
        carrier_bearing_step_width     = self.carrier_bearing_step_width  
        planet_shaft_dia               = self.planet_shaft_dia            
        sun_shaft_bearing_ID           = self.sun_shaft_bearing_ID        
        sun_shaft_bearing_width        = self.sun_shaft_bearing_width     
        planet_bore                    = self.planet_bore                 
        bearing_retainer_thickness     = self.bearing_retainer_thickness
        Motor_case_OD_base_to_chamfer  = self.Motor_case_OD_base_to_chamfer #5

        # To be written in Motor JSON files
        motor_output_hole_PCD = self.motor.motor_output_hole_PCD
        motor_output_hole_dia = self.motor.motor_output_hole_dia

        planet2FwMM += standard_clearance_1_5mm #clearnce to ensure big planet doesnt rub against the ring

        #--------------------------------------
        # Dependent variables
        #--------------------------------------
        h_b1 = 1.25 * module1
        h_b2 = 1.25 * module2

        #--------------------------------------
        # Mass: cpg_motor_casing
        #--------------------------------------
        ring_radial_thickness = self.ringRadialWidthMM
        ring_OD  = Nr * module2 + ring_radial_thickness*2


        gearbox_OD =  (Ns + Np1 * 2) * module1
        motor_OD = self.motorDiaMM

        if (gearbox_OD < motor_OD):
            clearance_motor_and_case = 5
        else: 
            clearance_motor_and_case = (gearbox_OD - motor_OD)/2 + 5

        Motor_case_ID     = motor_OD + clearance_motor_and_case * 2
        motor_height      = self.motorLengthMM
        Motor_case_height = motor_height + case_mounting_surface_height + standard_clearance_1_5mm

        Motor_case_OD = Motor_case_ID + Motor_case_thickness * 2

        Motor_case_volume = (  np.pi * ((Motor_case_OD * 0.5)**2) * base_plate_thickness 
                            + np.pi * ((Motor_case_OD * 0.5)**2 - (Motor_case_ID * 0.5)**2) * Motor_case_height
        ) * 1e-9

        Motor_case_mass = Motor_case_volume * density_3DP_material

        #--------------------------------------
        # Mass: cpg_gearbox_casing
        #--------------------------------------
        # Mass of the gearbox includes the mass of:
        # 1. Ring gear
        # 2. Bearing holding structure
        # 3. Case mounting structure
        #--------------------------------------
        ring_ID      = Nr * module2
        ringFwUsedMM = ringFwMM + clearance_planet

        bearing_ID     = InnerDiaBearingMM 
        bearing_OD     = OuterDiaBearingMM 
        bearing_height = WidthBearingMM    
        bearing_mass   = BearingMassKG      

        if ((bearing_OD + output_mounting_hole_dia * 4) > (Nr * module2 + 2 * h_b2)):
            bearing_mount_thickness  = output_mounting_hole_dia * 2
        else:
            bearing_mount_thickness = ((((Nr * module2 + 2 * h_b2) - (bearing_OD + output_mounting_hole_dia * 4))/2) 
                                    + output_mounting_hole_dia * 2 + standard_clearance_1_5mm)        

        bearing_holding_structure_OD     = bearing_OD + bearing_mount_thickness * 2
        bearing_holding_structure_ID     = bearing_OD
        bearing_holding_structure_height = bearing_height + standard_clearance_1_5mm

        case_dist                      = sec_carrier_thickness + clearance_planet * 2 + sun_coupler_hub_thickness + planet1FwMM - case_mounting_surface_height
        case_mounting_structure_OD     = Motor_case_OD
        case_mounting_structure_ID     = case_mounting_structure_OD - Motor_case_OD_base_to_chamfer *  2
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

        gearbox_casing_mass = (ring_volume + bearing_holding_structure_volume + case_mounting_structure_volume + large_fillet_volume) * density_3DP_material

        #----------------------------------
        # Mass: cpg_carrier
        #----------------------------------
        carrier_OD     = bearing_ID
        carrier_ID     = sun_shaft_bearing_OD - standard_clearance_1_5mm * 2
        carrier_height = bearing_height + carrier_bearing_step_width

        carrier_shaft_OD = planet_shaft_dia
        carrier_shaft_height = planet1FwMM  + planet2FwMM + clearance_planet * 2
        carrier_shaft_num = numPlanet * 2 + numPlanet # assuming triangular support is twice the mass of shaft

        carrier_volume = (np.pi * (((carrier_OD*0.5)**2) - ((carrier_ID)*0.5)**2) * carrier_height
                        + np.pi * ((carrier_shaft_OD*0.5)**2) * carrier_shaft_height * carrier_shaft_num) * 1e-9

        carrier_mass = carrier_volume * density_3DP_material

        #----------------------------------
        # Mass: cpg_sun
        #----------------------------------
        sun_hub_dia = motor_output_hole_PCD + motor_output_hole_dia + standard_clearance_1_5mm * 4

        sun_shaft_dia    = sun_shaft_bearing_ID
        sun_shaft_height = sun_shaft_bearing_width + 2 * standard_clearance_1_5mm

        fw_s_used        = planet1FwMM + planet2FwMM + clearance_planet + sec_carrier_thickness + standard_clearance_1_5mm

        sun_hub_volume   = np.pi * ((sun_hub_dia*0.5) ** 2) * sun_coupler_hub_thickness * 1e-9
        sun_gear_volume  = np.pi * ((DiaSunMM * 0.5) ** 2) * fw_s_used * 1e-9
        sun_shaft_volume = np.pi * ((sun_shaft_dia*0.5) ** 2) * sun_shaft_height * 1e-9

        sun_volume       = sun_hub_volume + sun_gear_volume + sun_shaft_volume
        sun_mass         = sun_volume * density_3DP_material

        #--------------------------------------
        # Mass: cpg_planet
        #--------------------------------------
        planet1_volume = (np.pi * ((DiaPlanet1MM*0.5)**2 - (planet_bore*0.5)**2) * planet1FwMM) * 1e-9
        planet2_volume = (np.pi * ((DiaPlanet2MM*0.5)**2 - (planet_bore*0.5)**2) * planet2FwMM) * 1e-9
        planet_mass   = (planet1_volume + planet2_volume) * density_3DP_material

        #--------------------------------------
        # Mass: cpg_sec_carrier
        #--------------------------------------
        sec_carrier_OD = bearing_ID
        sec_carrier_ID = (DiaSunMM + DiaPlanet1MM) - planet_shaft_dia - 2 * standard_clearance_1_5mm

        sec_carrier_volume = (np.pi * ((sec_carrier_OD*0.5)**2 - (sec_carrier_ID*0.5)**2) * sec_carrier_thickness) * 1e-9
        sec_carrier_mass   = sec_carrier_volume * density_3DP_material

        #--------------------------------------
        # Mass: cpg_sun_shaft_bearing
        #--------------------------------------
        sun_shaft_bearing_mass       = 4 * 0.001 # kg

        #--------------------------------------
        # Mass: cpg_planet_bearing
        #--------------------------------------
        planet_bearing_mass          = 1 * 0.001 # kg
        planet_bearing_num           = numPlanet * 2
        planet_bearing_combined_mass = planet_bearing_mass * planet_bearing_num

        #--------------------------------------
        # Mass: cpg_bearing
        #--------------------------------------
        bearing_mass = BearingMassKG # kg

        #--------------------------------------
        # Mass: cpg_bearing_retainer
        #--------------------------------------
        bearing_retainer_OD        = bearing_holding_structure_OD
        bearing_retainer_ID        = bearing_OD - standard_clearance_1_5mm * 2

        bearing_retainer_volume = (np.pi * ((bearing_retainer_OD*0.5)**2 - (bearing_retainer_ID*0.5)**2) * bearing_retainer_thickness) * 1e-9

        bearing_retainer_mass   = bearing_retainer_volume * density_3DP_material

        self.Motor_case_mass              = Motor_case_mass
        self.gearbox_casing_mass          = gearbox_casing_mass
        self.carrier_mass                 = carrier_mass
        self.sun_mass                     = sun_mass
        self.sec_carrier_mass             = sec_carrier_mass
        self.planet_mass                  = planet_mass
        self.planet_bearing_combined_mass = planet_bearing_combined_mass
        self.sun_shaft_bearing_mass       = sun_shaft_bearing_mass
        self.bearing_mass                 = bearing_mass
        self.bearing_retainer_mass        = bearing_retainer_mass

        #----------------------------------------
        # Total Actuator Mass
        #----------------------------------------

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

#-------------------------------------------------------------------------
# 3K Planetary Actuator class (Wolfrom Planetary Actuator Class)
#-------------------------------------------------------------------------
class wolfromPlanetaryActuator:
    def __init__(self, 
                 design_parameters,
                 motor_driver_params,
                 motor                    = motor,
                 wolfromPlanetaryGearbox  = wolfromPlanetaryGearbox,
                 FOS                      = 2.0,
                 serviceFactor            = 2.0,
                 maxGearboxDiameter       = 140.0,
                 stressAnalysisMethodName = "Lewis"):
        
        self.motor                    = motor
        self.wolfromPlanetaryGearbox  = wolfromPlanetaryGearbox
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

        self.gearbox_casing_thickness         = design_parameters["gearbox_casing_thickness"]
        self.small_ring_gear_casing_thickness = design_parameters["small_ring_gear_casing_thickness"]
        self.bearingIDClearanceMM             = design_parameters["bearingIDClearanceMM"]

        self.ring1RadialWidthMM = self.wolfromPlanetaryGearbox.ringRadialWidthBig   # 5
        self.ring2RadialWidthMM = self.wolfromPlanetaryGearbox.ringRadialWidthSmall # 5

        # --- Setting the variables ---
        self.setVariables()

        self.actuator_width = 0

    def cost(self):
        massActuator = self.getMassKG_3DP()
        effActuator  = self.wolfromPlanetaryGearbox.getEfficiency()
        widthActuator = self.wolfromPlanetaryGearbox.fwPlanetBigMM + self.wolfromPlanetaryGearbox.fwPlanetSmallMM
        module = self.wolfromPlanetaryGearbox.moduleBig
        cost = massActuator - 2 * effActuator + 0.2 * widthActuator
        return cost

    def setVariables(self):
        # --- Optimization Variables --- 
        self.Ns         = self.wolfromPlanetaryGearbox.Ns
        self.Np_b       = self.wolfromPlanetaryGearbox.NpBig
        self.Np_s       = self.wolfromPlanetaryGearbox.NpSmall
        self.Nr_b       = self.Ns + self.Np_b * 2
        self.Nr_s       = self.Ns + self.Np_b + self.Np_s
        self.module     = self.wolfromPlanetaryGearbox.moduleBig
        self.num_planet = self.wolfromPlanetaryGearbox.numPlanet

        #------------------------
        # --- Fixed Variables ---
        #------------------------
        # --- Clearances --- 
        self.clearance_planet                           = self.design_params["clearance_planet"]
        self.clearance_sun_coupler_sec_carrier          = self.design_params["clearance_sun_coupler_sec_carrier"]
        self.clearance_case_mount_holes_shell_thickness = self.design_params["clearance_case_mount_holes_shell_thickness"]
        self.case_mounting_nut_clearance                = self.design_params["case_mounting_nut_clearance"]
        self.standard_clearance_1_5mm                   = self.design_params["standard_clearance_1_5mm"]
        self.standard_fillet_1_5mm                      = self.design_params["standard_fillet_1_5mm"]
        self.standard_bearing_insertion_chamfer         = self.design_params["standard_bearing_insertion_chamfer"]
        self.tight_clearance_3DP                        = self.design_params["tight_clearance_3DP"]        
        self.loose_clearance_3DP                        = self.design_params["loose_clearance_3DP"]

        # --- Gear Variables ---
        self.pressure_angle = self.wolfromPlanetaryGearbox.getPressureAngleRad()
        self.pressure_angle_deg = self.wolfromPlanetaryGearbox.getPressureAngleRad() * 180 / np.pi

        # --- Motor ---
        self.motor_OD                            = self.motorDiaMM                     # 86.8
        self.motor_height                        = self.motorLengthMM                  # 26.5
        self.motor_mount_hole_PCD                = self.motor.motor_mount_hole_PCD     # 32
        self.motor_mount_hole_dia                = self.motor.motor_mount_hole_dia     # 4
        self.motor_mount_hole_num                = self.motor.motor_mount_hole_num     # 4
        self.motor_output_hole_PCD               = self.motor.motor_output_hole_PCD    # 23
        self.motor_output_hole_dia               = self.motor.motor_output_hole_dia    # 4
        self.motor_output_hole_num               = self.motor.motor_output_hole_num    # 4
        self.wire_slot_dist_from_center          = self.motor.wire_slot_dist_from_center # 30
        self.wire_slot_length                    = self.motor.wire_slot_length         # 10
        self.wire_slot_radius                    = self.motor.wire_slot_radius         # 4

        self.driver_upper_holes_dist_from_center = self.motor_driver_params["driver_upper_holes_dist_from_center"] # 23
        self.driver_lower_holes_dist_from_center = self.motor_driver_params["driver_lower_holes_dist_from_center"] # 15
        self.driver_side_holes_dist_from_center  = self.motor_driver_params["driver_side_holes_dist_from_center"]  # 20
        self.driver_mount_holes_dia              = self.motor_driver_params["driver_mount_holes_dia"]  # 2.5
        self.driver_mount_inserts_OD             = self.motor_driver_params["driver_mount_inserts_OD"] # 3.5
        self.driver_mount_thickness              = self.motor_driver_params["driver_mount_thickness"]  # 1.5
        self.driver_mount_height                 = self.motor_driver_params["driver_mount_height"]     # 4

        self.central_hole_offset_from_motor_mount_PCD = self.design_params["central_hole_offset_from_motor_mount_PCD"] # 5

        motor_output_hole_bolt = nuts_and_bolts_dimensions(bolt_dia = self.motor_output_hole_dia, bolt_type="CSK")
        self.motor_output_hole_CSK_OD          = motor_output_hole_bolt.bolt_head_dia   
        self.motor_output_hole_CSK_head_height = motor_output_hole_bolt.bolt_head_height


        # --- Motor & gearbox Casing ---
        self.case_mounting_hole_dia                 = self.design_params["case_mounting_hole_dia"] #3
        self.case_mounting_bolt_depth               = self.design_params["case_mounting_bolt_depth"]   #4.5
        self.output_mounting_hole_dia               = self.design_params["output_mounting_hole_dia"]   #4
        self.Motor_case_thickness                   = self.design_params["Motor_case_thickness"]   #2.5
        self.output_mounting_nut_depth              = self.design_params["output_mounting_nut_depth"]  #3
        self.Motor_case_OD_base_to_chamfer          = self.design_params["Motor_case_OD_base_to_chamfer"]  #5
        self.pattern_offset_from_motor_case_OD_base = self.design_params["pattern_offset_from_motor_case_OD_base"] #3
        self.pattern_bulge_dia                      = self.design_params["pattern_bulge_dia"]  #3
        self.pattern_num_bulge                      = self.design_params["pattern_num_bulge"]  #18
        self.pattern_depth                          = self.design_params["pattern_depth"]  #2
        self.base_plate_thickness                   = self.design_params["base_plate_thickness"]   #4
        self.case_mounting_surface_height           = self.design_params["case_mounting_surface_height"]   #4
        self.air_flow_hole_offset                   = self.design_params["air_flow_hole_offset"]   #3

        case_mounting_hole_bolt = nuts_and_bolts_dimensions(bolt_dia=self.case_mounting_hole_dia, bolt_type="socket_head")

        self.case_mounting_hole_allen_socket_dia = case_mounting_hole_bolt.bolt_head_dia # 5.5
        self.case_mounting_wrench_size           = case_mounting_hole_bolt.nut_width_across_flats # 5.5
        self.case_mounting_nut_thickness         = case_mounting_hole_bolt.nut_thickness # 2.4

        output_mounting_hole_bolt = nuts_and_bolts_dimensions(bolt_dia=self.output_mounting_hole_dia, bolt_type="socket_head")

        self.output_mounting_nut_thickness   = output_mounting_hole_bolt.nut_thickness # 3.2
        self.output_mounting_nut_wrench_size = output_mounting_hole_bolt.nut_width_across_flats # 7

        # --- Sun gear ---
        self.sun_shaft_bearing_ID      = self.design_params["sun_shaft_bearing_ID"] # 8
        self.sun_shaft_bearing_OD      = self.design_params["sun_shaft_bearing_OD"] # 16
        self.sun_coupler_hub_thickness = self.design_params["sun_coupler_hub_thickness"] # 4
        self.sun_shaft_bearing_width   = self.design_params["sun_shaft_bearing_width"] # 4
        self.sun_central_bolt_dia      = self.design_params["sun_central_bolt_dia"] # 5

        sun_central_bolt = nuts_and_bolts_dimensions(bolt_dia = self.sun_central_bolt_dia, bolt_type="socket_head")
        self.sun_central_bolt_socket_head_dia = sun_central_bolt.bolt_head_dia # 8.5

        self.fw_s_calc = self.wolfromPlanetaryGearbox.fwSunMM

        # --- Planet Gear ---

        self.planet_pin_bolt_dia      = self.design_params["planet_pin_bolt_dia"] # 5
        self.planet_shaft_dia         = self.design_params["planet_shaft_dia"] # 8
        self.planet_shaft_step_offset = self.design_params["planet_shaft_step_offset"] # 1
        self.planet_bearing_OD        = self.design_params["planet_bearing_OD"] # 12
        self.planet_bearing_width     = self.design_params["planet_bearing_width"] # 3
        self.planet_bore              = self.design_params["planet_bore"] # 10

        planet_pin_bolt = nuts_and_bolts_dimensions(bolt_dia=self.planet_pin_bolt_dia, bolt_type="socket_head")
        self.planet_pin_socket_head_dia  = planet_pin_bolt.bolt_head_dia # 8.5
        self.planet_pin_bolt_wrench_size = planet_pin_bolt.nut_width_across_flats # 8    

        self.fw_p_b = self.wolfromPlanetaryGearbox.fwPlanetBigMM

        # --- Ring Gear ---
        self.ring_radial_thickness = self.design_params["ring_radial_thickness"]
        self.fw_r_s = self.wolfromPlanetaryGearbox.fwRingSmallMM

        # --- Gearbox Casing ---
        self.gear_casing_thickness = self.design_params["gear_casing_thickness"]

        # --- Carrier & Sec Carrier--- 
        self.sec_carrier_thickness = self.design_params["sec_carrier_thickness"] # 5

        self.carrier_trapezoidal_support_sun_offset                 = self.design_params["carrier_trapezoidal_support_sun_offset"]# 5
        self.carrier_trapezoidal_support_hole_PCD_offset_bearing_ID = self.design_params["carrier_trapezoidal_support_hole_PCD_offset_bearing_ID"]# 4
        self.carrier_trapezoidal_support_hole_dia                   = self.design_params["carrier_trapezoidal_support_hole_dia"]# 3
        self.carrier_bearing_step_width                             = self.design_params["carrier_bearing_step_width"]# 1.5

        self.carrier_PCD = (self.Np_b + self.Ns) * self.module
        
        carrier_trapezoidal_support_hole = nuts_and_bolts_dimensions(bolt_dia=self.carrier_trapezoidal_support_hole_dia, bolt_type="socket_head")

        self.carrier_trapezoidal_support_hole_socket_head_dia = carrier_trapezoidal_support_hole.bolt_head_dia
        self.carrier_trapezoidal_support_hole_wrench_size     = carrier_trapezoidal_support_hole.nut_width_across_flats        

        self.carrier_thickness                                      = self.design_params["carrier_thickness"]

        # --- Bearing Retainer --- 
        self.bearing_retainer_thickness                            = self.design_params["bearing_retainer_thickness"]#2

        # --- Small Ring ---
        self.small_ring_output_wall_thickness                                           = self.design_params["small_ring_output_wall_thickness"]
        self.small_ring_output_wall_to_bearing_shaft_attachement_hole_dia               = self.design_params["small_ring_output_wall_to_bearing_shaft_attachement_hole_dia"]
        self.small_ring_output_wall_to_bearing_shaft_attachement_hole_depth             = self.design_params["small_ring_output_wall_to_bearing_shaft_attachement_hole_depth"]
        self.small_ring_output_wall_to_bearing_shaft_attachement_hole_pcd               = self.design_params["small_ring_output_wall_to_bearing_shaft_attachement_hole_pcd"]        
        self.small_ring_output_wall_to_bearing_shaft_attachement_hole_num               = self.design_params["small_ring_output_wall_to_bearing_shaft_attachement_hole_num"]
        self.carrier_small_ring_inner_bearing_ID                                        = self.design_params["carrier_small_ring_inner_bearing_ID"]
        self.carrier_small_ring_inner_bearing_flap                                      = self.design_params["carrier_small_ring_inner_bearing_flap"]
        self.small_ring_case_thickness                                                  = self.design_params["small_ring_case_thickness"]

        carrier_small_ring_inner_bearing               = bearings_discrete(self.carrier_small_ring_inner_bearing_ID)
        self.carrier_small_ring_inner_bearing_OD       = carrier_small_ring_inner_bearing.getBearingODMM()
        self.carrier_small_ring_inner_bearing_height   = carrier_small_ring_inner_bearing.getBearingWidthMM()


        small_ring_output_wall_to_bearing_shaft_attachement_bolt = nuts_and_bolts_dimensions(bolt_dia=self.small_ring_output_wall_to_bearing_shaft_attachement_hole_dia, bolt_type="CSK")

        self.small_ring_output_wall_to_bearing_shaft_attachement_nut_wrench             = small_ring_output_wall_to_bearing_shaft_attachement_bolt.nut_width_across_flats
        self.small_ring_output_wall_to_bearing_shaft_attachement_nut_thickness          = small_ring_output_wall_to_bearing_shaft_attachement_bolt.nut_thickness

        self.small_ring_output_wall_to_bearing_shaft_attachement_hole_CSK_OD            = small_ring_output_wall_to_bearing_shaft_attachement_bolt.bolt_head_dia
        self.small_ring_output_wall_to_bearing_shaft_attachement_hole_CSK_head_height   = small_ring_output_wall_to_bearing_shaft_attachement_bolt.bolt_head_height

        #----------------------------
        #---- Dependent Variables ---
        #---------------------------- 
        # --- Clearances --- 
        self.ring_to_chamfer_clearance = self.clearance_planet

        # --- Gear profile parameters ---
        self.h_a = 1 * self.module
        self.h_f = 1.25 * self.module
        self.h_b = 1.25 * self.module
        self.clr_tip_root = self.h_f - self.h_a
        self.clr_tip_root_s = self.h_f - self.h_a

        # --- Ring ---
        # Big
        self.dp_r_b = self.module * self.Nr_b
        self.db_r_b = self.dp_r_b * np.cos ( self.pressure_angle )
        self.fw_r_b = self.fw_p_b
        self.alpha_r_b = ( self.dp_r_b ** 2 - self.db_r_b ** 2 )**0.5 / self.db_r_b * 180 / np.pi - self.pressure_angle_deg
        self.beta_r_b = ( 360 / ( 4 * self.Nr_b ) + self.alpha_r_b ) * 2

        self.ring_OD_b = self.Nr_b * self.module + self.ring_radial_thickness * 2

        # Small
        self.dp_r_s = self.module * self.Nr_s
        self.db_r_s = self.dp_r_s * np.cos ( self.pressure_angle )
        self.alpha_r_s = ( self.dp_r_s ** 2 - self.db_r_s ** 2 )**0.5 / self.db_r_s * 180 / np.pi - self.pressure_angle_deg
        self.beta_r_s = ( 360 / ( 4 * self.Nr_s ) + self.alpha_r_s ) * 2

        # --- Planet ---
        # Big
        self.dp_p_b = self.module * self.Np_b
        self.db_p_b = self.dp_p_b * np.cos ( self.pressure_angle )
        self.alpha_p_b = ( self.dp_p_b ** 2 - self.db_p_b ** 2 )**0.5 / self.db_p_b * 180 / np.pi - self.pressure_angle_deg
        self.beta_p_b = ( 360 / ( 4 * self.Np_b ) - self.alpha_p_b ) * 2

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

        self.sun_hub_dia = self.motor_output_hole_PCD + self.motor_output_hole_dia + self.standard_clearance_1_5mm * 2

        self.fw_s_used = self.fw_p_s + self.fw_p_b + self.clearance_planet + self.sec_carrier_thickness + self.standard_clearance_1_5mm - self.carrier_small_ring_inner_bearing_flap +  self.standard_clearance_1_5mm

        # --- Bearing ---
        IdrequiredMM = self.module * (self.Ns + self.Np_b) + self.bearingIDClearanceMM
        Bearings            = bearings_discrete(IdrequiredMM)
        self.bearing_ID     = Bearings.getBearingIDMM()
        self.bearing_OD     = Bearings.getBearingODMM()
        self.bearing_height = Bearings.getBearingWidthMM()

        # --- Motor & Gearbox casing ---
        self.case_dist = self.sec_carrier_thickness + self.clearance_planet + self.sun_coupler_hub_thickness - self.case_mounting_surface_height
        self.case_mounting_hole_shift = self.case_mounting_hole_dia / 2 - 0.5
        self.clearance_motor_and_case = (5 if ((self.Ns + self.Np_b * 2) * self.module) < self.motor_OD else (((self.Ns + self.Np_b * 2) * self.module - self.motor_OD) * 0.5 + 5) )
        self.motor_case_OD_base = self.motor_OD + self.clearance_motor_and_case * 2 + self.Motor_case_thickness * 2
        self.case_mounting_PCD = self.motor_case_OD_base + self.case_mounting_hole_shift * 2
        self.Motor_case_OD_max = self.case_mounting_PCD + self.case_mounting_hole_allen_socket_dia + self.clearance_case_mount_holes_shell_thickness * 2
        self.bearing_mount_thickness = (self.output_mounting_hole_dia * 2 if (self.bearing_OD + self.output_mounting_hole_dia * 4) > (self.Nr_s * self.module + 2 * self.h_b) else ((self.Nr_s * self.module + 2 * self.h_b - (self.bearing_OD + self.output_mounting_hole_dia * 4)) / 2) + self.output_mounting_hole_dia * 2 + self.standard_clearance_1_5mm)
        self.output_mounting_PCD = self.bearing_OD + self.bearing_mount_thickness
        self.Motor_case_ID = self.motor_OD + self.clearance_motor_and_case * 2

        self.gear_casing_big_ring_to_bearing_dist = self.fw_p_s + self.clearance_planet + self.carrier_thickness + self.standard_clearance_1_5mm*2/3 + self.small_ring_case_thickness - self.standard_clearance_1_5mm # last - is because of change in flap position

        # --- Carrier ---
        self.carrier_PCD = ( self.Np_b + self.Ns ) * self.module

    def genEquationFile(self, motor_name="NO_MOTOR", gearRatioLL = 0.0, gearRatioUL = 0.0):
        # writing values into text file imported which is imported into solidworks
        self.setVariables()
        file_path = os.path.join(os.path.dirname(__file__), 'WPG', 'Equation_Files', motor_name, f'wpg_equations_{gearRatioLL}_{gearRatioUL}.txt')
        # print("File Path: ",file_path)
        with open(file_path, 'w') as eqFile:
            l = [
                f'"Np_b" = {self.Np_b}\n',
                f'"Np_s" = {self.Np_s}\n',
                f'"Nr_b" = {self.Nr_b}\n',
                f'"Nr_s" = {self.Nr_s}\n',
                f'"Ns" = {self.Ns}\n',
                f'"Motor_case_ID" = {self.Motor_case_ID}\n',
                f'"Motor_case_OD_base_to_chamfer" = {self.Motor_case_OD_base_to_chamfer}\n',
                f'"Motor_case_OD_max" = {self.Motor_case_OD_max}\n',
                f'"Motor_case_thickness" = {self.Motor_case_thickness}\n',
                f'"air_flow_hole_offset" = {self.air_flow_hole_offset}\n',
                f'"standard_bearing_insertion_chamfer" = {self.standard_bearing_insertion_chamfer}\n',
                f'"alpha_p_b" = {self.alpha_p_b}\n',
                f'"alpha_p_s" = {self.alpha_p_s}\n',
                f'"alpha_r_b" = {self.alpha_r_b}\n',
                f'"alpha_r_s" = {self.alpha_r_s}\n',
                f'"alpha_s" = {self.alpha_s}\n',
                f'"base_plate_thickness" = {self.base_plate_thickness}\n',
                f'"bearing_ID" = {self.bearing_ID}\n',
                f'"bearing_OD" = {self.bearing_OD}\n',
                f'"bearing_height" = {self.bearing_height}\n',
                f'"bearing mount thickness" = {self.bearing_mount_thickness}\n',
                f'"bearing_retainer_thickness" = {self.bearing_retainer_thickness}\n',
                f'"beta_p_b" = {self.beta_p_b}\n',
                f'"beta_p_s" = {self.beta_p_s}\n',
                f'"beta_r_b" = {self.beta_r_b}\n',
                f'"beta_r_s" = {self.beta_r_s}\n',
                f'"beta_s" = {self.beta_s}\n',
                f'"carrier_PCD" = {self.carrier_PCD}\n',
                f'"carrier_bearing_step_width" = {self.carrier_bearing_step_width}\n',
                f'"carrier_small_ring_inner_bearing_ID" = {self.carrier_small_ring_inner_bearing_ID}\n',
                f'"carrier_small_ring_inner_bearing_OD" = {self.carrier_small_ring_inner_bearing_OD}\n',
                f'"carrier_small_ring_inner_bearing_flap" = {self.carrier_small_ring_inner_bearing_flap}\n',
                f'"carrier_small_ring_inner_bearing_height" = {self.carrier_small_ring_inner_bearing_height}\n',
                f'"carrier_thickness" = {self.carrier_thickness}\n',
                f'"carrier_trapezoidal_support_hole_PCD_offset_bearing_ID" = {self.carrier_trapezoidal_support_hole_PCD_offset_bearing_ID}\n',
                f'"carrier_trapezoidal_support_hole_dia" = {self.carrier_trapezoidal_support_hole_dia}\n',
                f'"carrier_trapezoidal_support_hole_socket_head_dia" = {self.carrier_trapezoidal_support_hole_socket_head_dia}\n',
                f'"carrier_trapezoidal_support_hole_wrench_size" = {self.carrier_trapezoidal_support_hole_wrench_size}\n',
                f'"carrier_trapezoidal_support_sun_offset" = {self.carrier_trapezoidal_support_sun_offset}\n',
                f'"case_dist" = {self.case_dist}\n',
                f'"case_mounting_PCD" = {self.case_mounting_PCD}\n',
                f'"case_mounting_bolt_depth" = {self.case_mounting_bolt_depth}\n',
                f'"case_mounting_hole_allen_socket_dia" = {self.case_mounting_hole_allen_socket_dia}\n',
                f'"case_mounting_hole_dia" = {self.case_mounting_hole_dia}\n',
                f'"case_mounting_hole_shift" = {self.case_mounting_hole_shift}\n',
                f'"case_mounting_nut_clearance" = {self.case_mounting_nut_clearance}\n',
                f'"case_mounting_nut_thickness" = {self.case_mounting_nut_thickness}\n',
                f'"case_mounting_surface_height" = {self.case_mounting_surface_height}\n',
                f'"case_mounting_wrench_size" = {self.case_mounting_wrench_size}\n',
                f'"central_hole_offset_from_motor_mount_PCD" = {self.central_hole_offset_from_motor_mount_PCD}\n',
                f'"clearance_case_mount_holes_shell_thickness" = {self.clearance_case_mount_holes_shell_thickness}\n',
                f'"clearance_motor_and_case" = {self.clearance_motor_and_case}\n',
                f'"clearance_planet" = {self.clearance_planet}\n',
                f'"clearance_sun_coupler_sec_carrier" = {self.clearance_sun_coupler_sec_carrier}\n',
                f'"clr_tip_root" = {self.clr_tip_root}\n',
                f'"clr_tip_root_s" = {self.clr_tip_root_s}\n',
                f'"db_p_b" = {self.db_p_b}\n',
                f'"db_p_s" = {self.db_p_s}\n',
                f'"db_r_b" = {self.db_r_b}\n',
                f'"db_r_s" = {self.db_r_s}\n',
                f'"db_s" = {self.db_s}\n',
                f'"dp_p_b" = {self.dp_p_b}\n',
                f'"dp_p_s" = {self.dp_p_s}\n',
                f'"dp_r_b" = {self.dp_r_b}\n',
                f'"dp_r_s" = {self.dp_r_s}\n',
                f'"dp_s" = {self.dp_s}\n',
                f'"driver_lower_holes_dist_from_center" = {self.driver_lower_holes_dist_from_center}\n',
                f'"driver_mount_height" = {self.driver_mount_height}\n',
                f'"driver_mount_holes_dia" = {self.driver_mount_holes_dia}\n',
                f'"driver_mount_inserts_OD" = {self.driver_mount_inserts_OD}\n',
                f'"driver_mount_thickness" = {self.driver_mount_thickness}\n',
                f'"driver_side_holes_dist_from_center" = {self.driver_side_holes_dist_from_center}\n',
                f'"driver_upper_holes_dist_from_center" = {self.driver_upper_holes_dist_from_center}\n',
                f'"fw_p_b" = {self.fw_p_b}\n',
                f'"fw_p_s" = {self.fw_p_s}\n',
                f'"fw_r_b" = {self.fw_r_b}\n',
                f'"fw_r_s" = {self.fw_r_s}\n',
                f'"fw_s_calc" = {self.fw_s_calc}\n',
                f'"fw_s_used" = {self.fw_s_used}\n',
                f'"gear_casing_big_ring_to_bearing_dist" = {self.gear_casing_big_ring_to_bearing_dist}\n',
                f'"gear_casing_thickness" = {self.gear_casing_thickness}\n',
                f'"h_a" = {self.h_a}\n',
                f'"h_b" = {self.h_b}\n',
                f'"h_f" = {self.h_f}\n',
                f'"module" = {self.module}\n',
                f'"motor_OD" = {self.motor_OD}\n',
                f'"motor_case_OD_base" = {self.motor_case_OD_base}\n',
                f'"motor_height" = {self.motor_height}\n',
                f'"motor_mount_hole_PCD" = {self.motor_mount_hole_PCD}\n',
                f'"motor_mount_hole_dia" = {self.motor_mount_hole_dia}\n',
                f'"motor_mount_hole_num" = {self.motor_mount_hole_num}\n',
                f'"motor_output_hole_CSK_OD" = {self.motor_output_hole_CSK_OD}\n',
                f'"motor_output_hole_CSK_head_height" = {self.motor_output_hole_CSK_head_height}\n',
                f'"motor_output_hole_PCD" = {self.motor_output_hole_PCD}\n',
                f'"motor_output_hole_dia" = {self.motor_output_hole_dia}\n',
                f'"motor_output_hole_num" = {self.motor_output_hole_num}\n',
                f'"num_planet" = {self.num_planet}\n',
                f'"output_mounting_PCD" = {self.output_mounting_PCD}\n',
                f'"output_mounting_hole_dia" = {self.output_mounting_hole_dia}\n',
                f'"output_mounting_nut_depth" = {self.output_mounting_nut_depth}\n',
                f'"output_mounting_nut_thickness" = {self.output_mounting_nut_thickness}\n',
                f'"output_mounting_nut_wrench_size" = {self.output_mounting_nut_wrench_size}\n',
                f'"pattern_bulge_dia" = {self.pattern_bulge_dia}\n',
                f'"pattern_depth" = {self.pattern_depth}\n',
                f'"pattern_num_bulge" = {self.pattern_num_bulge}\n',
                f'"pattern_offset_from_motor_case_OD_base" = {self.pattern_offset_from_motor_case_OD_base}\n',
                f'"planet_bearing_OD" = {self.planet_bearing_OD}\n',
                f'"planet_bearing_width" = {self.planet_bearing_width}\n',
                f'"planet_bore" = {self.planet_bore}\n',
                f'"planet_pin_bolt_dia" = {self.planet_pin_bolt_dia}\n',
                f'"planet_pin_bolt_wrench_size" = {self.planet_pin_bolt_wrench_size}\n',
                f'"planet_pin_socket_head_dia" = {self.planet_pin_socket_head_dia}\n',
                f'"planet_shaft_dia" = {self.planet_shaft_dia}\n',
                f'"planet_shaft_step_offset" = {self.planet_shaft_step_offset}\n',
                f'"pressure_angle" = {self.pressure_angle_deg}\n',
                f'"pressure angle" = {self.pressure_angle_deg}\n',
                f'"ring_OD_b" = {self.ring_OD_b}\n',
                f'"ring_radial_thickness" = {self.ring_radial_thickness}\n',
                f'"ring_to_chamfer_clearance" = {self.ring_to_chamfer_clearance}\n',
                f'"sec_carrier_thickness" = {self.sec_carrier_thickness}\n',
                f'"small_ring_case_thickness" = {self.small_ring_case_thickness}\n',
                f'"small_ring_output_wall_thickness" = {self.small_ring_output_wall_thickness}\n',
                f'"small_ring_output_wall_to_bearing_shaft_attachement_hole_CSK_OD" = {self.small_ring_output_wall_to_bearing_shaft_attachement_hole_CSK_OD}\n',
                f'"small_ring_output_wall_to_bearing_shaft_attachement_hole_CSK_head_height" = {self.small_ring_output_wall_to_bearing_shaft_attachement_hole_CSK_head_height}\n',
                f'"small_ring_output_wall_to_bearing_shaft_attachement_hole_depth" = {self.small_ring_output_wall_to_bearing_shaft_attachement_hole_depth}\n',
                f'"small_ring_output_wall_to_bearing_shaft_attachement_hole_dia" = {self.small_ring_output_wall_to_bearing_shaft_attachement_hole_dia}\n',
                f'"small_ring_output_wall_to_bearing_shaft_attachement_hole_num" = {self.small_ring_output_wall_to_bearing_shaft_attachement_hole_num}\n',
                f'"small_ring_output_wall_to_bearing_shaft_attachement_hole_pcd" = {self.small_ring_output_wall_to_bearing_shaft_attachement_hole_pcd}\n',
                f'"small_ring_output_wall_to_bearing_shaft_attachement_nut_thickness" = {self.small_ring_output_wall_to_bearing_shaft_attachement_nut_thickness}\n',
                f'"small_ring_output_wall_to_bearing_shaft_attachement_nut_wrench" = {self.small_ring_output_wall_to_bearing_shaft_attachement_nut_wrench}\n',
                f'"standard_clearance_1_5mm" = {self.standard_clearance_1_5mm}\n',
                f'"standard_fillet_1_5mm" = {self.standard_fillet_1_5mm}\n',
                f'"sun_central_bolt_dia" = {self.sun_central_bolt_dia}\n',
                f'"sun_central_bolt_socket_head_dia" = {self.sun_central_bolt_socket_head_dia}\n',
                f'"sun_coupler_hub_thickness" = {self.sun_coupler_hub_thickness}\n',
                f'"sun_hub_dia" = {self.sun_hub_dia}\n',
                f'"sun_shaft_bearing_ID" = {self.sun_shaft_bearing_ID}\n',
                f'"sun_shaft_bearing_OD" = {self.sun_shaft_bearing_OD}\n',
                f'"sun_shaft_bearing_width" = {self.sun_shaft_bearing_width}\n',
                f'"wire_slot_dist_from_center" = {self.wire_slot_dist_from_center}\n',
                f'"wire_slot_length" = {self.wire_slot_length}\n',
                f'"wire_slot_radius" = {self.wire_slot_radius}\n',
                f'"tight_clearance_3DP" = {self.tight_clearance_3DP}\n',
                f'"loose_clearance_3DP" = {self.loose_clearance_3DP}\n' 
            ]
            eqFile.writelines(l)

    def genEquationFile_old(self):
        # writing values into text file imported which is imported into solidworks
        self.setVariables()
        file_path = os.path.join(os.path.dirname(__file__), 'WPG', 'wpg_equations.txt')
        # print("File Path: ",file_path)
        with open(file_path, 'w') as eqFile:
            l = [
                f'"Np_b" = {self.Np_b}\n',
                f'"Np_s" = {self.Np_s}\n',
                f'"Nr_b" = {self.Nr_b}\n',
                f'"Nr_s" = {self.Nr_s}\n',
                f'"Ns" = {self.Ns}\n',
                f'"Motor_case_ID" = {self.Motor_case_ID}\n',
                f'"Motor_case_OD_base_to_chamfer" = {self.Motor_case_OD_base_to_chamfer}\n',
                f'"Motor_case_OD_max" = {self.Motor_case_OD_max}\n',
                f'"Motor_case_thickness" = {self.Motor_case_thickness}\n',
                f'"air_flow_hole_offset" = {self.air_flow_hole_offset}\n',
                f'"standard_bearing_insertion_chamfer" = {self.standard_bearing_insertion_chamfer}\n',
                f'"alpha_p_b" = {self.alpha_p_b}\n',
                f'"alpha_p_s" = {self.alpha_p_s}\n',
                f'"alpha_r_b" = {self.alpha_r_b}\n',
                f'"alpha_r_s" = {self.alpha_r_s}\n',
                f'"alpha_s" = {self.alpha_s}\n',
                f'"base_plate_thickness" = {self.base_plate_thickness}\n',
                f'"bearing_ID" = {self.bearing_ID}\n',
                f'"bearing_OD" = {self.bearing_OD}\n',
                f'"bearing_height" = {self.bearing_height}\n',
                f'"bearing mount thickness" = {self.bearing_mount_thickness}\n',
                f'"bearing_retainer_thickness" = {self.bearing_retainer_thickness}\n',
                f'"beta_p_b" = {self.beta_p_b}\n',
                f'"beta_p_s" = {self.beta_p_s}\n',
                f'"beta_r_b" = {self.beta_r_b}\n',
                f'"beta_r_s" = {self.beta_r_s}\n',
                f'"beta_s" = {self.beta_s}\n',
                f'"carrier_PCD" = {self.carrier_PCD}\n',
                f'"carrier_bearing_step_width" = {self.carrier_bearing_step_width}\n',
                f'"carrier_small_ring_inner_bearing_ID" = {self.carrier_small_ring_inner_bearing_ID}\n',
                f'"carrier_small_ring_inner_bearing_OD" = {self.carrier_small_ring_inner_bearing_OD}\n',
                f'"carrier_small_ring_inner_bearing_flap" = {self.carrier_small_ring_inner_bearing_flap}\n',
                f'"carrier_small_ring_inner_bearing_height" = {self.carrier_small_ring_inner_bearing_height}\n',
                f'"carrier_thickness" = {self.carrier_thickness}\n',
                f'"carrier_trapezoidal_support_hole_PCD_offset_bearing_ID" = {self.carrier_trapezoidal_support_hole_PCD_offset_bearing_ID}\n',
                f'"carrier_trapezoidal_support_hole_dia" = {self.carrier_trapezoidal_support_hole_dia}\n',
                f'"carrier_trapezoidal_support_hole_socket_head_dia" = {self.carrier_trapezoidal_support_hole_socket_head_dia}\n',
                f'"carrier_trapezoidal_support_hole_wrench_size" = {self.carrier_trapezoidal_support_hole_wrench_size}\n',
                f'"carrier_trapezoidal_support_sun_offset" = {self.carrier_trapezoidal_support_sun_offset}\n',
                f'"case_dist" = {self.case_dist}\n',
                f'"case_mounting_PCD" = {self.case_mounting_PCD}\n',
                f'"case_mounting_bolt_depth" = {self.case_mounting_bolt_depth}\n',
                f'"case_mounting_hole_allen_socket_dia" = {self.case_mounting_hole_allen_socket_dia}\n',
                f'"case_mounting_hole_dia" = {self.case_mounting_hole_dia}\n',
                f'"case_mounting_hole_shift" = {self.case_mounting_hole_shift}\n',
                f'"case_mounting_nut_clearance" = {self.case_mounting_nut_clearance}\n',
                f'"case_mounting_nut_thickness" = {self.case_mounting_nut_thickness}\n',
                f'"case_mounting_surface_height" = {self.case_mounting_surface_height}\n',
                f'"case_mounting_wrench_size" = {self.case_mounting_wrench_size}\n',
                f'"central_hole_offset_from_motor_mount_PCD" = {self.central_hole_offset_from_motor_mount_PCD}\n',
                f'"clearance_case_mount_holes_shell_thickness" = {self.clearance_case_mount_holes_shell_thickness}\n',
                f'"clearance_motor_and_case" = {self.clearance_motor_and_case}\n',
                f'"clearance_planet" = {self.clearance_planet}\n',
                f'"clearance_sun_coupler_sec_carrier" = {self.clearance_sun_coupler_sec_carrier}\n',
                f'"clr_tip_root" = {self.clr_tip_root}\n',
                f'"clr_tip_root_s" = {self.clr_tip_root_s}\n',
                f'"db_p_b" = {self.db_p_b}\n',
                f'"db_p_s" = {self.db_p_s}\n',
                f'"db_r_b" = {self.db_r_b}\n',
                f'"db_r_s" = {self.db_r_s}\n',
                f'"db_s" = {self.db_s}\n',
                f'"dp_p_b" = {self.dp_p_b}\n',
                f'"dp_p_s" = {self.dp_p_s}\n',
                f'"dp_r_b" = {self.dp_r_b}\n',
                f'"dp_r_s" = {self.dp_r_s}\n',
                f'"dp_s" = {self.dp_s}\n',
                f'"driver_lower_holes_dist_from_center" = {self.driver_lower_holes_dist_from_center}\n',
                f'"driver_mount_height" = {self.driver_mount_height}\n',
                f'"driver_mount_holes_dia" = {self.driver_mount_holes_dia}\n',
                f'"driver_mount_inserts_OD" = {self.driver_mount_inserts_OD}\n',
                f'"driver_mount_thickness" = {self.driver_mount_thickness}\n',
                f'"driver_side_holes_dist_from_center" = {self.driver_side_holes_dist_from_center}\n',
                f'"driver_upper_holes_dist_from_center" = {self.driver_upper_holes_dist_from_center}\n',
                f'"fw_p_b" = {self.fw_p_b}\n',
                f'"fw_p_s" = {self.fw_p_s}\n',
                f'"fw_r_b" = {self.fw_r_b}\n',
                f'"fw_r_s" = {self.fw_r_s}\n',
                f'"fw_s_calc" = {self.fw_s_calc}\n',
                f'"fw_s_used" = {self.fw_s_used}\n',
                f'"gear_casing_big_ring_to_bearing_dist" = {self.gear_casing_big_ring_to_bearing_dist}\n',
                f'"gear_casing_thickness" = {self.gear_casing_thickness}\n',
                f'"h_a" = {self.h_a}\n',
                f'"h_b" = {self.h_b}\n',
                f'"h_f" = {self.h_f}\n',
                f'"module" = {self.module}\n',
                f'"motor_OD" = {self.motor_OD}\n',
                f'"motor_case_OD_base" = {self.motor_case_OD_base}\n',
                f'"motor_height" = {self.motor_height}\n',
                f'"motor_mount_hole_PCD" = {self.motor_mount_hole_PCD}\n',
                f'"motor_mount_hole_dia" = {self.motor_mount_hole_dia}\n',
                f'"motor_mount_hole_num" = {self.motor_mount_hole_num}\n',
                f'"motor_output_hole_CSK_OD" = {self.motor_output_hole_CSK_OD}\n',
                f'"motor_output_hole_CSK_head_height" = {self.motor_output_hole_CSK_head_height}\n',
                f'"motor_output_hole_PCD" = {self.motor_output_hole_PCD}\n',
                f'"motor_output_hole_dia" = {self.motor_output_hole_dia}\n',
                f'"motor_output_hole_num" = {self.motor_output_hole_num}\n',
                f'"num_planet" = {self.num_planet}\n',
                f'"output_mounting_PCD" = {self.output_mounting_PCD}\n',
                f'"output_mounting_hole_dia" = {self.output_mounting_hole_dia}\n',
                f'"output_mounting_nut_depth" = {self.output_mounting_nut_depth}\n',
                f'"output_mounting_nut_thickness" = {self.output_mounting_nut_thickness}\n',
                f'"output_mounting_nut_wrench_size" = {self.output_mounting_nut_wrench_size}\n',
                f'"pattern_bulge_dia" = {self.pattern_bulge_dia}\n',
                f'"pattern_depth" = {self.pattern_depth}\n',
                f'"pattern_num_bulge" = {self.pattern_num_bulge}\n',
                f'"pattern_offset_from_motor_case_OD_base" = {self.pattern_offset_from_motor_case_OD_base}\n',
                f'"planet_bearing_OD" = {self.planet_bearing_OD}\n',
                f'"planet_bearing_width" = {self.planet_bearing_width}\n',
                f'"planet_bore" = {self.planet_bore}\n',
                f'"planet_pin_bolt_dia" = {self.planet_pin_bolt_dia}\n',
                f'"planet_pin_bolt_wrench_size" = {self.planet_pin_bolt_wrench_size}\n',
                f'"planet_pin_socket_head_dia" = {self.planet_pin_socket_head_dia}\n',
                f'"planet_shaft_dia" = {self.planet_shaft_dia}\n',
                f'"planet_shaft_step_offset" = {self.planet_shaft_step_offset}\n',
                f'"pressure_angle" = {self.pressure_angle_deg}\n',
                f'"pressure angle" = {self.pressure_angle_deg}\n',
                f'"ring_OD_b" = {self.ring_OD_b}\n',
                f'"ring_radial_thickness" = {self.ring_radial_thickness}\n',
                f'"ring_to_chamfer_clearance" = {self.ring_to_chamfer_clearance}\n',
                f'"sec_carrier_thickness" = {self.sec_carrier_thickness}\n',
                f'"small_ring_case_thickness" = {self.small_ring_case_thickness}\n',
                f'"small_ring_output_wall_thickness" = {self.small_ring_output_wall_thickness}\n',
                f'"small_ring_output_wall_to_bearing_shaft_attachement_hole_CSK_OD" = {self.small_ring_output_wall_to_bearing_shaft_attachement_hole_CSK_OD}\n',
                f'"small_ring_output_wall_to_bearing_shaft_attachement_hole_CSK_head_height" = {self.small_ring_output_wall_to_bearing_shaft_attachement_hole_CSK_head_height}\n',
                f'"small_ring_output_wall_to_bearing_shaft_attachement_hole_depth" = {self.small_ring_output_wall_to_bearing_shaft_attachement_hole_depth}\n',
                f'"small_ring_output_wall_to_bearing_shaft_attachement_hole_dia" = {self.small_ring_output_wall_to_bearing_shaft_attachement_hole_dia}\n',
                f'"small_ring_output_wall_to_bearing_shaft_attachement_hole_num" = {self.small_ring_output_wall_to_bearing_shaft_attachement_hole_num}\n',
                f'"small_ring_output_wall_to_bearing_shaft_attachement_hole_pcd" = {self.small_ring_output_wall_to_bearing_shaft_attachement_hole_pcd}\n',
                f'"small_ring_output_wall_to_bearing_shaft_attachement_nut_thickness" = {self.small_ring_output_wall_to_bearing_shaft_attachement_nut_thickness}\n',
                f'"small_ring_output_wall_to_bearing_shaft_attachement_nut_wrench" = {self.small_ring_output_wall_to_bearing_shaft_attachement_nut_wrench}\n',
                f'"standard_clearance_1_5mm" = {self.standard_clearance_1_5mm}\n',
                f'"standard_fillet_1_5mm" = {self.standard_fillet_1_5mm}\n',
                f'"sun_central_bolt_dia" = {self.sun_central_bolt_dia}\n',
                f'"sun_central_bolt_socket_head_dia" = {self.sun_central_bolt_socket_head_dia}\n',
                f'"sun_coupler_hub_thickness" = {self.sun_coupler_hub_thickness}\n',
                f'"sun_hub_dia" = {self.sun_hub_dia}\n',
                f'"sun_shaft_bearing_ID" = {self.sun_shaft_bearing_ID}\n',
                f'"sun_shaft_bearing_OD" = {self.sun_shaft_bearing_OD}\n',
                f'"sun_shaft_bearing_width" = {self.sun_shaft_bearing_width}\n',
                f'"wire_slot_dist_from_center" = {self.wire_slot_dist_from_center}\n',
                f'"wire_slot_length" = {self.wire_slot_length}\n',
                f'"wire_slot_radius" = {self.wire_slot_radius}\n',
                f'"tight_clearance_3DP" = {self.tight_clearance_3DP}\n',
                f'"loose_clearance_3DP" = {self.loose_clearance_3DP}\n' 
            ]
            eqFile.writelines(l)
    
    # ----------------------------------------
    # Mass of New Design 
    #-----------------------------------------
    def getToothForces(self, constraintCheck=False):
        if constraintCheck:
            # Check if the constraints are satisfied
            if not self.wolfromPlanetaryGearbox.geometricConstraint():
                print("Geometric constraint not satisfied")
                return
            if not self.wolfromPlanetaryGearbox.meshingConstraint():
                print("Meshing constraint not satisfied")
                return
            if not self.wolfromPlanetaryGearbox.noPlanetInterferenceConstraint():
                print("No planet interference constraint not satisfied")
                return

        Ns          = self.wolfromPlanetaryGearbox.Ns
        NpBig       = self.wolfromPlanetaryGearbox.NpBig
        NpSmall     = self.wolfromPlanetaryGearbox.NpSmall
        NrBig       = self.wolfromPlanetaryGearbox.NrBig
        NrSmall     = self.wolfromPlanetaryGearbox.NrSmall
        numPlanet   = self.wolfromPlanetaryGearbox.numPlanet
        moduleBig   = self.wolfromPlanetaryGearbox.moduleBig
        moduleSmall = self.wolfromPlanetaryGearbox.moduleSmall

        RpBig_Mt   = self.wolfromPlanetaryGearbox.getPCRadiusPlanetBigM()
        RpSmall_Mt = self.wolfromPlanetaryGearbox.getPCRadiusPlanetSmallM()
        Rs_Mt      = self.wolfromPlanetaryGearbox.getPCRadiusSunM()
        RrBig_Mt   = self.wolfromPlanetaryGearbox.getPCRadiusRingBigM()
        RrSmall_Mt = self.wolfromPlanetaryGearbox.getPCRadiusRingSmallM()

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
        if not self.wolfromPlanetaryGearbox.geometricConstraint():
            print("Geometric constraint not satisfied")
            return
        if not self.wolfromPlanetaryGearbox.meshingConstraint():
            print("Meshing constraint not satisfied")
            return
        if not self.wolfromPlanetaryGearbox.noPlanetInterferenceConstraint():
            print("No planet interference constraint not satisfied")
            return

        Ns          = self.wolfromPlanetaryGearbox.Ns
        NpBig       = self.wolfromPlanetaryGearbox.NpBig
        NpSmall     = self.wolfromPlanetaryGearbox.NpSmall
        NrBig       = self.wolfromPlanetaryGearbox.NrBig
        NrSmall     = self.wolfromPlanetaryGearbox.NrSmall
        numPlanet   = self.wolfromPlanetaryGearbox.numPlanet
        moduleBig   = self.wolfromPlanetaryGearbox.moduleBig
        moduleSmall = self.wolfromPlanetaryGearbox.moduleSmall

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

        V_sp_big = (self.wolfromPlanetaryGearbox.getPCRadiusSunM() * wSun)
        V_rp_big = (wCarrier*(self.wolfromPlanetaryGearbox.getPCRadiusSunM() + self.wolfromPlanetaryGearbox.getPCRadiusPlanetBigM()) + 
                    wPlanet*(self.wolfromPlanetaryGearbox.getPCRadiusPlanetBigM()))
        V_rp_small = (wCarrier*(self.wolfromPlanetaryGearbox.getPCRadiusSunM() + self.wolfromPlanetaryGearbox.getPCRadiusPlanetBigM()) +
                      wPlanet*(self.wolfromPlanetaryGearbox.getPCRadiusPlanetSmallM()))
        
        # Check 
        V_rp_small_test = wRingSmall*(self.wolfromPlanetaryGearbox.getPCRadiusSunM() + self.wolfromPlanetaryGearbox.getPCRadiusPlanetBigM()
                                      + self.wolfromPlanetaryGearbox.getPCRadiusPlanetSmallM())
        
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
        bMin_sun         = (self.FOS * np.abs(Ft_sp_big   )/ (self.wolfromPlanetaryGearbox.maxGearAllowableStressPa * ySun * Kv_sun * P_big)) # m
        bMin_planetBig1  = (self.FOS * np.abs(Ft_sp_big   )/ (self.wolfromPlanetaryGearbox.maxGearAllowableStressPa * yPlanetBig * Kv_planetBig1 * P_big))
        bMin_planetBig2  = (self.FOS * np.abs(Ft_sp_big   )/ (self.wolfromPlanetaryGearbox.maxGearAllowableStressPa * yPlanetBig * Kv_planetBig2 * P_big))
        bMin_planetSmall = (self.FOS * np.abs(Ft_rp_small )/ (self.wolfromPlanetaryGearbox.maxGearAllowableStressPa * yPlanetSmall * Kv_planetSmall * P_small))
        bMin_ringBig     = (self.FOS * np.abs(Ft_rp_big   )/ (self.wolfromPlanetaryGearbox.maxGearAllowableStressPa * yRingBig * Kv_ringBig * P_big))
        bMin_ringSmall   = (self.FOS * np.abs(Ft_rp_small )/ (self.wolfromPlanetaryGearbox.maxGearAllowableStressPa * yRingSmall * Kv_ringSmall * P_small))

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

        self.wolfromPlanetaryGearbox.setfwSunMM         ( bMin_sun*1000 )
        self.wolfromPlanetaryGearbox.setfwPlanetBigMM   ( bMin_planetBig*1000 )
        self.wolfromPlanetaryGearbox.setfwPlanetSmallMM ( bMin_planetSmall*1000 )
        self.wolfromPlanetaryGearbox.setfwRingSmallMM   ( bMin_ringSmall*1000 )
        self.wolfromPlanetaryGearbox.setfwRingBigMM     ( bMin_ringBig*1000 )
        # print("Lewis:")
        # print(f"bMin_planetSmall = {bMin_planetSmall}")
        # print(f"bMin_planetBig = {bMin_planetBig}")
        # print(f"bMin_sun = {bMin_sun}")
        # print(f"bMin_ringSmall = {bMin_ringSmall}")
        # print(f"bMin_ringBig = {bMin_ringBig}")

    def AGMAStressAnalysisMinFacewidth(self):
        # Check if the constraints are satisfied
        if not self.wolfromPlanetaryGearbox.geometricConstraint():
            print("Geometric constraint not satisfied")
            return
        if not self.wolfromPlanetaryGearbox.meshingConstraint():
            print("Meshing constraint not satisfied")
            return
        if not self.wolfromPlanetaryGearbox.noPlanetInterferenceConstraint():
            print("No planet interference constraint not satisfied")
            return

        Ns          = self.wolfromPlanetaryGearbox.Ns
        NpBig       = self.wolfromPlanetaryGearbox.NpBig
        NpSmall     = self.wolfromPlanetaryGearbox.NpSmall
        NrBig       = self.wolfromPlanetaryGearbox.NrBig
        NrSmall     = self.wolfromPlanetaryGearbox.NrSmall
        numPlanet   = self.wolfromPlanetaryGearbox.numPlanet
        moduleBig   = self.wolfromPlanetaryGearbox.moduleBig
        moduleSmall = self.wolfromPlanetaryGearbox.moduleSmall

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

        pressureAngle = self.wolfromPlanetaryGearbox.pressureAngleDEG

        # T Krishna Rao - Design of Machine Elements - II pg.191
        # Modified Lewis Form Factor Y = pi*y for pressure angle = 20
        Y_sun         = (0.154 - 0.912/Ns) * np.pi
        Y_planetBig   = (0.154 - 0.912/NpBig) * np.pi
        Y_planetSmall = (0.154 - 0.912/NpSmall) * np.pi
        Y_ringSmall   = (0.154 - 0.912/NrSmall) * np.pi
        Y_ringBig     = (0.154 - 0.912/NrBig) * np.pi

        V_sp_big = np.abs(self.wolfromPlanetaryGearbox.getPCRadiusSunM() * wSun)
        V_rp_big = np.abs(wCarrier*(self.wolfromPlanetaryGearbox.getPCRadiusSunM() + self.wolfromPlanetaryGearbox.getPCRadiusPlanetBigM()) + 
                    wPlanet*(self.wolfromPlanetaryGearbox.getPCRadiusPlanetBigM()))
        V_rp_small = np.abs(wCarrier*(self.wolfromPlanetaryGearbox.getPCRadiusSunM() + self.wolfromPlanetaryGearbox.getPCRadiusPlanetBigM()) +
                      wPlanet*(self.wolfromPlanetaryGearbox.getPCRadiusPlanetSmallM()))
        
        # Check 
        V_rp_small_test = wRingSmall*(self.wolfromPlanetaryGearbox.getPCRadiusSunM() + self.wolfromPlanetaryGearbox.getPCRadiusPlanetBigM()
                                      + self.wolfromPlanetaryGearbox.getPCRadiusPlanetSmallM())
        
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
        bMin_planetSmall = (self.FOS * np.abs(Wt_rp_small) * Kv_planetSmall * Ks * Kh * Kb)/(moduleSmall * Yj_planetSmall * self.wolfromPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        bMin_planetBig = (self.FOS * np.abs(Wt_rp_big) * Kv_planetBig * Ks * Kh * Kb)/(moduleBig * Yj_planetBig * self.wolfromPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        bMin_sun = (self.FOS * np.abs(Wt_sp_big) * Kv_sun * Ks * Kh * Kb) / (moduleBig * Yj_sun * self.wolfromPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        bMin_ringSmall = (self.FOS * np.abs(Wt_rp_small) * Kv_ringSmall * Ks * Kh * Kb) / (moduleSmall * Yj_ringSmall * self.wolfromPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        bMin_ringBig = (self.FOS * np.abs(Wt_rp_big) * Kv_ringBig * Ks * Kh * Kb) / (moduleBig * Yj_ringBig * self.wolfromPlanetaryGearbox.maxGearAllowableStressPa * 0.001)

        # C_pm = 1.1
        # X_planetSmall = (self.FOS * np.abs(Wt_rp_small) * Kv_planetSmall * Ks * Kb)/(moduleSmall * Y_planetSmall * self.wolfromPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        # X_planetBig = (self.FOS * np.abs(Wt_rp_big) * Kv_planetBig * Ks * Kb)/(moduleBig * Y_planetBig * self.wolfromPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        # X_sun = (self.FOS * np.abs(Wt_sp_big) * Kv_sun * Ks * Kb) / (moduleBig * Y_sun * self.wolfromPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        # X_ringSmall = (self.FOS * np.abs(Wt_rp_small) * Kv_ringSmall * Ks * Kb) / (moduleSmall * Y_ringSmall * self.wolfromPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        # X_ringBig = (self.FOS * np.abs(Wt_rp_big) * Kv_ringBig * Ks * Kb) / (moduleBig * Y_ringBig * self.wolfromPlanetaryGearbox.maxGearAllowableStressPa * 0.001)

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

        self.wolfromPlanetaryGearbox.setfwSunMM         ( bMin_sun*1000 )
        self.wolfromPlanetaryGearbox.setfwPlanetBigMM   ( bMin_planetBig*1000 )
        self.wolfromPlanetaryGearbox.setfwPlanetSmallMM ( bMin_planetSmall*1000 )
        self.wolfromPlanetaryGearbox.setfwRingSmallMM   ( bMin_ringSmall*1000 )
        self.wolfromPlanetaryGearbox.setfwRingBigMM     ( bMin_ringBig*1000 )

        # print("AGMA:")
        # print(f"bMin_planetSmall = {bMin_planetSmall}")
        # print(f"bMin_planetBig = {bMin_planetBig}")
        # print(f"bMin_sun = {bMin_sun}")
        # print(f"bMin_ringSmall = {bMin_ringSmall}")
        # print(f"bMin_ringBig = {bMin_ringBig}")

    def mitStressAnalysisMinFacewidth(self):
        # Check if the constraints are satisfied
        if not self.wolfromPlanetaryGearbox.geometricConstraint():
            print("Geometric constraint not satisfied")
            return
        if not self.wolfromPlanetaryGearbox.meshingConstraint():
            print("Meshing constraint not satisfied")
            return
        if not self.wolfromPlanetaryGearbox.noPlanetInterferenceConstraint():
            print("No planet interference constraint not satisfied")
            return

        Ns          = self.wolfromPlanetaryGearbox.Ns
        NpBig       = self.wolfromPlanetaryGearbox.NpBig
        NpSmall     = self.wolfromPlanetaryGearbox.NpSmall
        NrBig       = self.wolfromPlanetaryGearbox.NrBig
        NrSmall     = self.wolfromPlanetaryGearbox.NrSmall
        numPlanet   = self.wolfromPlanetaryGearbox.numPlanet
        moduleBig   = self.wolfromPlanetaryGearbox.moduleBig
        moduleSmall = self.wolfromPlanetaryGearbox.moduleSmall

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
        _,_,CR_SP1 = self.wolfromPlanetaryGearbox.contactRatio_sunPlanet_stg1()
        _,_,CR_PR1 = self.wolfromPlanetaryGearbox.contactRatio_planetRing_stg1()
        _,_,CR_PR2 = self.wolfromPlanetaryGearbox.contactRatio_planetRing_stg2()

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
        bMin_sun_mit           = (self.FOS * np.abs(Ft_sp_big  ) * qe_sp1 * qk_sp1 / (self.wolfromPlanetaryGearbox.maxGearAllowableStressPa * moduleBig   * 0.001))
        bMin_planetBig_mit_1   = (self.FOS * np.abs(Ft_sp_big  ) * qe_sp1 * qk_sp1 / (self.wolfromPlanetaryGearbox.maxGearAllowableStressPa * moduleBig   * 0.001))
        bMin_planetBig_mit_2   = (self.FOS * np.abs(Ft_rp_big  ) * qe_pr1 * qk_pr1 / (self.wolfromPlanetaryGearbox.maxGearAllowableStressPa * moduleBig   * 0.001))
        bMin_planetSmall_mit   = (self.FOS * np.abs(Ft_rp_small) * qe_pr2 * qk_pr2 / (self.wolfromPlanetaryGearbox.maxGearAllowableStressPa * moduleSmall * 0.001))
        bMin_ringBig_mit       = (self.FOS * np.abs(Ft_rp_big  ) * qe_pr1 * qk_pr1 / (self.wolfromPlanetaryGearbox.maxGearAllowableStressPa * moduleBig   * 0.001))
        bMin_ringSmall_mit     = (self.FOS * np.abs(Ft_rp_small) * qe_pr2 * qk_pr2 / (self.wolfromPlanetaryGearbox.maxGearAllowableStressPa * moduleSmall * 0.001))

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

        self.wolfromPlanetaryGearbox.setfwSunMM         ( bMin_sun_mit         * 1000 )
        self.wolfromPlanetaryGearbox.setfwPlanetBigMM   ( bMin_planetBig_mit   * 1000 )
        self.wolfromPlanetaryGearbox.setfwPlanetSmallMM ( bMin_planetSmall_mit * 1000 )
        self.wolfromPlanetaryGearbox.setfwRingSmallMM   ( bMin_ringSmall_mit   * 1000 )
        self.wolfromPlanetaryGearbox.setfwRingBigMM     ( bMin_ringBig_mit     * 1000 )

        return bMin_sun_mitMM, bMin_planetBig_mitMM, bMin_planetSmall_mitMM, bMin_ringBig_mitMM, bMin_ringSmall_mitMM

    def updateFacewidth(self):
        if self.stressAnalysisMethodName == "Lewis":
            self.lewisStressAnalysisMinFacewidth()
        elif self.stressAnalysisMethodName == "AGMA":
            self.AGMAStressAnalysisMinFacewidth()
        elif self.stressAnalysisMethodName == "MIT":
            self.mitStressAnalysisMinFacewidth()

    def getMassKG_3DP(self):
        module1   = self.wolfromPlanetaryGearbox.moduleBig
        module2   = self.wolfromPlanetaryGearbox.moduleSmall
        Ns        = self.wolfromPlanetaryGearbox.Ns
        Np1       = self.wolfromPlanetaryGearbox.NpBig
        Nr1       = self.wolfromPlanetaryGearbox.NrBig
        Np2       = self.wolfromPlanetaryGearbox.NpSmall
        Nr2       = self.wolfromPlanetaryGearbox.NrSmall
        numPlanet = self.wolfromPlanetaryGearbox.numPlanet 

        #----------------------------------
        # Density of Materials
        #----------------------------------
        density_3DP_material = self.wolfromPlanetaryGearbox.densityGears

        #----------------------------------
        # Diameter and Radius
        #----------------------------------
        DiaSunMM     =  Ns * module1
        DiaPlanet1MM = Np1 * module1
        DiaRing1MM   = Nr1 * module1
        DiaPlanet2MM = Np2 * module2
        DiaRing2MM   = Nr2 * module2

        Rs_MM  = DiaSunMM / 2
        Rp1_MM = DiaPlanet1MM / 2
        Rp2_MM = DiaPlanet2MM / 2
        Rr1_MM = DiaRing1MM / 2
        Rr2_MM = DiaRing2MM / 2
        
        Ring1OuterRadiusMM = Rr1_MM + self.ring1RadialWidthMM
        Ring2OuterRadiusMM = Rr2_MM + self.ring2RadialWidthMM

        ring1_radial_thickness = self.ring1RadialWidthMM
        ring2_radial_thickness = self.ring2RadialWidthMM

        #----------------------------------
        # Facewidths
        #----------------------------------         
        sunFwMM     = self.wolfromPlanetaryGearbox.fwSunMM
        planet1FwMM = self.wolfromPlanetaryGearbox.fwPlanetBigMM
        planet2FwMM = self.wolfromPlanetaryGearbox.fwPlanetSmallMM
        ring1FwMM   = self.wolfromPlanetaryGearbox.fwRingBigMM
        ring2FwMM   = self.wolfromPlanetaryGearbox.fwRingSmallMM

        sunFwM     = sunFwMM     * 0.001 
        planet1FwM = planet1FwMM * 0.001
        planet2FwM = planet2FwMM * 0.001
        ring1FwM   = ring1FwMM   * 0.001
        ring2FwM   = ring2FwMM   * 0.001

        #-----------------------------------------
        # Motor Dimensions & Mass
        #-----------------------------------------
        MotorLengthMM = self.motorLengthMM
        MotorDiaMM    = self.motorDiaMM
        MotorMassKG   = self.motorMassKG

        #--------------------------------------
        # Independent variables
        #--------------------------------------
        # To be written in Gearbox(dspg) JSON files
        case_mounting_surface_height = self.case_mounting_surface_height
        standard_clearance_1_5mm     = self.standard_clearance_1_5mm    
        base_plate_thickness         = self.base_plate_thickness        
        Motor_case_thickness         = self.Motor_case_thickness        
        clearance_planet             = self.clearance_planet            
        output_mounting_hole_dia     = self.output_mounting_hole_dia    
        sec_carrier_thickness        = self.sec_carrier_thickness       
        sun_coupler_hub_thickness    = self.sun_coupler_hub_thickness   
        # sun_shaft_bearing_OD       = self.sun_shaft_bearing_OD        
        # carrier_bearing_step_width = self.carrier_bearing_step_width  
        planet_shaft_dia             = self.planet_shaft_dia            
        sun_shaft_bearing_ID         = self.sun_shaft_bearing_ID        
        sun_shaft_bearing_width      = self.sun_shaft_bearing_width     
        planet_bore                  = self.planet_bore                 
        # bearing_retainer_thickness = self.bearing_retainer_thickness 
        carrier_small_ring_inner_bearing_flap = self.carrier_small_ring_inner_bearing_flap # 2
        carrier_small_ring_inner_bearing_ID   = self.carrier_small_ring_inner_bearing_ID # 20
        gear_casing_big_ring_to_bearing_dist  = self.gear_casing_big_ring_to_bearing_dist
        Motor_case_OD_base_to_chamfer = self.Motor_case_OD_base_to_chamfer # 5
        planet_pin_socket_head_dia    = self.planet_pin_socket_head_dia
        carrier_thickness             = self.carrier_thickness # 4
        small_ring_output_wall_thickness = self.small_ring_output_wall_thickness # 5
        gearbox_casing_thickness         = self.gearbox_casing_thickness # 4
        small_ring_gear_casing_thickness = self.small_ring_gear_casing_thickness # 4
        bearingIDClearanceMM             = self.bearingIDClearanceMM

        # To be written in Motor JSON files
        motor_output_hole_PCD = self.motor.motor_output_hole_PCD
        motor_output_hole_dia = self.motor.motor_output_hole_dia

        #-------------------------------
        # Bearings: Bearing1 & Bearing2
        #-------------------------------
        IdRequiredMM      = module1 * (Ns + Np1) + bearingIDClearanceMM 
                                                                               
        Bearing           = bearings_discrete(IdRequiredMM)

        InnerDiaBearingMM = Bearing.getBearingIDMM()
        OuterDiaBearingMM = Bearing.getBearingODMM()
        WidthBearingMM    = Bearing.getBearingWidthMM()
        BearingMassKG     = Bearing.getBearingMassKG()

        # --- Bearing dimensions --- 
        bearing_ID     = InnerDiaBearingMM 
        bearing_OD     = OuterDiaBearingMM 
        bearing_height = WidthBearingMM 

        #-------------------------------------------------------
        # wpg_bearing
        #-------------------------------------------------------   
        bearing_mass   = BearingMassKG 

        #-------------------------------------------------------
        # wpg_carrier_ring_small_bearing
        #-------------------------------------------------------
        carrier_small_ring_inner_bearing = bearings_discrete(carrier_small_ring_inner_bearing_ID)
        carrier_small_ring_inner_bearing_OD = carrier_small_ring_inner_bearing.getBearingODMM()
        carrier_small_ring_inner_bearing_height = carrier_small_ring_inner_bearing.getBearingWidthMM()

        carrier_small_ring_inner_bearing_mass = carrier_small_ring_inner_bearing.getBearingMassKG()

        #-------------------------------------------------------
        # wpg_carrier
        #-------------------------------------------------------
        carrier_OD     = ((Ns + Np1) * module1 + planet_pin_socket_head_dia + standard_clearance_1_5mm * 2)
        carrier_ID     = carrier_small_ring_inner_bearing_OD
        carrier_height = carrier_thickness

        carrier_bearing_mount_ID     = carrier_small_ring_inner_bearing_OD
        carrier_bearing_mount_OD     = standard_clearance_1_5mm * (8/3) + carrier_small_ring_inner_bearing_OD
        carrier_bearing_mount_height = carrier_small_ring_inner_bearing_height - carrier_thickness + standard_clearance_1_5mm

        carrier_shaft_OD     = planet_shaft_dia
        carrier_shaft_height = planet1FwMM  + planet2FwMM + clearance_planet * 2
        carrier_shaft_num    = numPlanet * 2 + numPlanet # assuming support triangle weighs twice as much as shaft

        carrier_volume = (np.pi * (((carrier_OD*0.5)**2) - ((carrier_ID)*0.5)**2) * carrier_height
                        + np.pi * (((carrier_bearing_mount_OD*0.5)**2) - ((carrier_bearing_mount_ID)*0.5)**2) * carrier_bearing_mount_height  
                        + np.pi * ((carrier_shaft_OD*0.5)**2) * carrier_shaft_height * carrier_shaft_num) * 1e-9

        carrier_mass = carrier_volume * density_3DP_material

        #-------------------------------------------------------
        # wpg_motor_casing
        #-------------------------------------------------------
        ring1_OD  = Nr1 * module1 + ring1_radial_thickness*2
        motor_OD = self.motorDiaMM

        if (ring1_OD < motor_OD):
            clearance_motor_and_case = 5
        else: 
            clearance_motor_and_case = (ring1_OD - motor_OD)/2 + 5

        motor_height      = self.motorLengthMM
        Motor_case_height = motor_height + case_mounting_surface_height + standard_clearance_1_5mm

        Motor_case_ID     = motor_OD + clearance_motor_and_case * 2
        Motor_case_OD = Motor_case_ID + Motor_case_thickness * 2

        Motor_case_volume = ( np.pi * ((Motor_case_OD * 0.5)**2) * base_plate_thickness 
                            + np.pi * ((Motor_case_OD * 0.5)**2 - (Motor_case_ID * 0.5)**2) * Motor_case_height) * 1e-9

        Motor_case_mass = Motor_case_volume * density_3DP_material

        #-------------------------------------------------------
        # wpg_gearbox_casing
        # ---
        # Mass of the gearbox casign includes the mass of:
        # 1. Bearing holding structure
        # 2. Spacer wall for ring-2
        # 3. Ring gear-1
        # 4. Case mounting structure
        #-------------------------------------------------------
        ring1_ID     = Nr1 * module2
        ringFwUsedMM = ring1FwMM

        # --- Bearing holding structure --- 
        if ((bearing_OD + output_mounting_hole_dia * 4) > ((Nr2 * module2 + 2 * ring2_radial_thickness) + standard_clearance_1_5mm * 2)):
            bearing_mount_thickness  = output_mounting_hole_dia * 2
        else:
            bearing_mount_thickness = (((
                                        ((Nr2 * module2 + 2 * ring2_radial_thickness) + standard_clearance_1_5mm * 2) 
                                        - (bearing_OD + output_mounting_hole_dia * 4))/2) 
                                        + output_mounting_hole_dia * 2 + standard_clearance_1_5mm)        

        bearing_holding_structure_ID     = bearing_OD
        bearing_holding_structure_OD     = bearing_OD + bearing_mount_thickness * 2
        bearing_holding_structure_height = bearing_height + standard_clearance_1_5mm

        bearing_holding_structure_volume = np.pi * (((bearing_holding_structure_OD*0.5)**2) - 
                                                    ((bearing_holding_structure_ID*0.5)**2)) * bearing_holding_structure_height * 1e-9
        # --- Spacer wall for ring-2 --- 
        spacer_wall_for_ring2_ID     = ((Nr2 * module2 + 2 * ring2_radial_thickness) + standard_clearance_1_5mm * 2)
        spacer_wall_for_ring2_OD     = spacer_wall_for_ring2_ID + gearbox_casing_thickness * 2
        spacer_wall_for_ring2_height = gear_casing_big_ring_to_bearing_dist

        spacer_wall_for_ring2_volume = np.pi * (((spacer_wall_for_ring2_OD*0.5)**2) - 
                                                ((spacer_wall_for_ring2_ID*0.5)**2)) * spacer_wall_for_ring2_height * 1e-9

        # --- Ring gear-1 --- 
        ring_gear1_ID     = (Nr1 * module1)
        ring_gear1_OD     = ring_gear1_ID + ring1_radial_thickness * 2
        ring_gear1_height = ring1FwMM

        ring_gear1_volume = np.pi * (((ring_gear1_OD*0.5)**2) - 
                                     ((ring_gear1_ID*0.5)**2)) * ring_gear1_height * 1e-9

        # --- Case mounting structure --- 
        case_dist = (sec_carrier_thickness 
                     + clearance_planet
                     + sun_coupler_hub_thickness 
                     - case_mounting_surface_height)

        case_mounting_structure_ID     = Motor_case_OD - Motor_case_OD_base_to_chamfer * 2
        case_mounting_structure_OD     = Motor_case_OD
        case_mounting_structure_height = case_dist

        case_mounting_structure_volume  = np.pi * (((case_mounting_structure_OD*0.5)**2) - 
                                                    ((case_mounting_structure_ID*0.5)**2)) * case_mounting_structure_height * 1e-9


        large_fillet_ID     = ring1_OD
        large_fillet_OD     = Motor_case_OD
        large_fillet_height = ring1FwMM/2
        large_fillet_volume = 0.5 * (np.pi * (((large_fillet_OD*0.5)**2) - ((large_fillet_ID)*0.5)**2) * large_fillet_height) * 1e-9


        gearbox_casing_mass = (bearing_holding_structure_volume
                               + spacer_wall_for_ring2_volume
                               + case_mounting_structure_volume 
                               + large_fillet_volume
                               + ring_gear1_volume) * density_3DP_material

        #-------------------------------------------------------
        # wpg_motor
        #-------------------------------------------------------
        motor_mass = self.motorMassKG
        
        #-------------------------------------------------------
        # wpg_planet_bearing
        #-------------------------------------------------------
        planet_bearing_mass          = 1 * 0.001 # kg
        planet_bearing_num           = numPlanet * 2
        planet_bearing_combined_mass = planet_bearing_mass * planet_bearing_num

        #-------------------------------------------------------
        # wpg_planet
        #-------------------------------------------------------
        planet1_volume = (np.pi * ((DiaPlanet1MM*0.5)**2 - (planet_bore*0.5)**2) * planet1FwMM) * 1e-9
        planet2_volume = (np.pi * ((DiaPlanet2MM*0.5)**2 - (planet_bore*0.5)**2) * planet2FwMM) * 1e-9
        planet_mass   = (planet1_volume + planet2_volume) * density_3DP_material

        #-------------------------------------------------------
        # wpg_sec_carrier
        #-------------------------------------------------------
        sec_carrier_OD = ((Ns + Np1) * module1 + planet_shaft_dia + self.planet_shaft_step_offset * 2 + standard_clearance_1_5mm * 2)
        sec_carrier_ID = (DiaSunMM + DiaPlanet1MM) - planet_shaft_dia - 2 * standard_clearance_1_5mm

        sec_carrier_volume = (np.pi * ((sec_carrier_OD*0.5)**2 - (sec_carrier_ID*0.5)**2) * sec_carrier_thickness) * 1e-9
        sec_carrier_mass   = sec_carrier_volume * density_3DP_material

        #-------------------------------------------------------
        # wpg_small_ring_bearing_shaft
        #-------------------------------------------------------
        small_ring_bearing_shaft_dia = carrier_small_ring_inner_bearing_ID
        small_ring_bearing_shaft_height = (bearing_height 
                                         + carrier_thickness
                                         + carrier_small_ring_inner_bearing_flap)
        
        small_ring_bearing_shaft_volume = (np.pi 
                                        * (small_ring_bearing_shaft_dia * 0.5)**2 
                                        *  small_ring_bearing_shaft_height) * 1e-9
        
        small_ring_bearing_shaft_mass = small_ring_bearing_shaft_volume * density_3DP_material

        #-------------------------------------------------------
        # wpg_small_ring
        # ---
        # 1. Ring gear2
        # 2. ring2bearing_spacer_cone_shell
        # 3. ring2bearing_spacer_disc
        # 4. bearing_holding_structure
        # 5. output_wall
        # 6. sun_shaft_bearing_holding_structure
        #-------------------------------------------------------

        # --- Ring gear2 ---
        ring_gear2_ID     = (Nr2 * module2)
        ring_gear2_OD     = ring_gear2_ID + ring2_radial_thickness * 2
        ring_gear2_height = ring2FwMM

        ring_gear2_volume = np.pi * (((ring_gear2_OD*0.5)**2) - 
                                     ((ring_gear2_ID*0.5)**2)) * ring_gear2_height * 1e-9

        # --- ring2bearing_spacer_cone_shell ---
        ring2bearing_spacer_cone_shell_base   = small_ring_gear_casing_thickness
        ring2bearing_spacer_cone_shell_height = carrier_thickness + standard_clearance_1_5mm + clearance_planet
        ring2bearing_spacer_cone_shell_radius = ((ring_gear2_OD + carrier_OD) / 2) /2
        
        ring2bearing_spacer_cone_shell_volume = (2 * np.pi * ring2bearing_spacer_cone_shell_radius
                                                 * ring2bearing_spacer_cone_shell_height
                                                 * ring2bearing_spacer_cone_shell_base) * 1e-9

        # --- ring2bearing_spacer_disc ---
        ring2bearing_spacer_disc_ID     = bearing_ID - 2 * small_ring_gear_casing_thickness
        ring2bearing_spacer_disc_OD     = carrier_OD + small_ring_gear_casing_thickness * 2
        ring2bearing_spacer_disc_height = small_ring_gear_casing_thickness
        
        ring2bearing_spacer_disc_volume = np.pi * (((ring2bearing_spacer_disc_OD*0.5)**2) - 
                                                   ((ring2bearing_spacer_disc_ID*0.5)**2)) * ring2bearing_spacer_disc_height * 1e-9

        # --- bearing_holding_structure ---
        bearing_holding_structure_OD     = bearing_ID
        bearing_holding_structure_ID     = bearing_ID - 2 * small_ring_gear_casing_thickness
        bearing_holding_structure_height = bearing_height + standard_clearance_1_5mm * (2/3)

        bearing_holding_structure_volume = np.pi * (((bearing_holding_structure_OD*0.5)**2) - 
                                                   ((bearing_holding_structure_ID*0.5)**2)) * bearing_holding_structure_height * 1e-9

        # --- output_wall ---
        output_wall_dia    = bearing_ID - 2 * small_ring_gear_casing_thickness
        output_wall_height = small_ring_output_wall_thickness
        output_wall_volume = np.pi * (output_wall_dia / 2)**2 * output_wall_height * 1e-9

        # --- sun_shaft_bearing_holding_structure ---
        # truncated hollow cone Volume = 0.5 * Hollow cylinder volume. 
        # 45deg chamfer (height = width)
        sun_shaft_bearing_holding_structure_ID     = carrier_small_ring_inner_bearing_ID
        sun_shaft_bearing_holding_structure_height = (bearing_height + carrier_thickness - carrier_small_ring_inner_bearing_height)
        sun_shaft_bearing_holding_structure_OD     = (sun_shaft_bearing_holding_structure_ID 
                                                      + sun_shaft_bearing_holding_structure_height * 2)
        
        sun_shaft_bearing_holding_structure_volume = (0.5 
                                                      * np.pi 
                                                      * (((sun_shaft_bearing_holding_structure_OD*0.5)**2) - 
                                                         ((sun_shaft_bearing_holding_structure_ID*0.5)**2)) 
                                                      * sun_shaft_bearing_holding_structure_height * 1e-9)

        small_ring_mass = (ring_gear2_volume 
                         + ring2bearing_spacer_cone_shell_volume 
                         + ring2bearing_spacer_disc_volume
                         + bearing_holding_structure_volume
                         + output_wall_volume
                         + sun_shaft_bearing_holding_structure_volume) * density_3DP_material

        #-------------------------------------------------------
        # wpg_sun_shaft_bearing
        #-------------------------------------------------------
        sun_shaft_bearing_mass       = 1 * 0.001 # kg

        #-------------------------------------------------------
        # wpg_sun
        #-------------------------------------------------------
        sun_hub_dia = motor_output_hole_PCD + motor_output_hole_dia + standard_clearance_1_5mm * 4

        sun_shaft_dia    = sun_shaft_bearing_ID
        sun_shaft_height = sun_shaft_bearing_width + 2 * standard_clearance_1_5mm

        fw_s_used        = (planet1FwMM 
                            + planet2FwMM 
                            + clearance_planet 
                            + sec_carrier_thickness 
                            + 2 * standard_clearance_1_5mm 
                            - carrier_small_ring_inner_bearing_flap)

        sun_hub_volume   = np.pi * ((sun_hub_dia*0.5) ** 2) * sun_coupler_hub_thickness * 1e-9
        sun_gear_volume  = np.pi * ((DiaSunMM * 0.5) ** 2) * fw_s_used * 1e-9
        sun_shaft_volume = np.pi * ((sun_shaft_dia*0.5) ** 2) * sun_shaft_height * 1e-9

        sun_volume       = sun_hub_volume + sun_gear_volume + sun_shaft_volume
        sun_mass         = sun_volume * density_3DP_material

        Actuator_mass = (carrier_small_ring_inner_bearing_mass + 
                        carrier_mass + 
                        gearbox_casing_mass +
                        bearing_mass +
                        Motor_case_mass + 
                        motor_mass +
                        planet_bearing_combined_mass +
                        planet_mass * numPlanet +
                        sec_carrier_mass +
                        small_ring_bearing_shaft_mass +
                        small_ring_mass +
                        sun_shaft_bearing_mass +
                        sun_mass)

        self.carrier_small_ring_inner_bearing_mass = carrier_small_ring_inner_bearing_mass
        self.carrier_mass                          = carrier_mass
        self.gearbox_casing_mass                   = gearbox_casing_mass
        self.bearing_mass                          = bearing_mass
        self.Motor_case_mass                       = Motor_case_mass
        self.motor_mass                            = motor_mass
        self.planet_bearing_combined_mass          = planet_bearing_combined_mass
        self.planet_mass                           = planet_mass
        self.sec_carrier_mass                      = sec_carrier_mass
        self.small_ring_bearing_shaft_mass         = small_ring_bearing_shaft_mass
        self.small_ring_mass                       = small_ring_mass
        self.sun_shaft_bearing_mass                = sun_shaft_bearing_mass
        self.sun_mass                              = sun_mass

        return Actuator_mass

    def print_mass_of_parts_3DP(self):
        print("carrier_small_ring_inner_bearing_mass :", 1000 * self.carrier_small_ring_inner_bearing_mass)
        print("carrier_mass :", 1000 * self.carrier_mass)                         
        print("gearbox_casing_mass :", 1000 * self.gearbox_casing_mass)            
        print("bearing_mass :", 1000 * self.bearing_mass)      
        print("Motor_case_mass :", 1000 * self.Motor_case_mass)                      
        print("motor_mass :", 1000 * self.motor_mass)                           
        print("planet_bearing_combined_mass :", 1000 * self.planet_bearing_combined_mass)         
        print("planet_mass :", 1000 * self.planet_mass)                          
        print("sec_carrier_mass :", 1000 * self.sec_carrier_mass)                     
        print("small_ring_bearing_shaft_mass :", 1000 * self.small_ring_bearing_shaft_mass)        
        print("small_ring_mass :", 1000 * self.small_ring_mass)                      
        print("sun_shaft_bearing_mass :", 1000 * self.sun_shaft_bearing_mass)               
        print("sun_mass :", 1000 * self.sun_mass)                             

#-------------------------------------------------------------------------
# Double Stage Actuator class
#-------------------------------------------------------------------------
class doubleStagePlanetaryActuator:
    def __init__(self, 
                 design_parameters,
                 motor_driver_params,
                 motor = motor, 
                 doubleStagePlanetaryGearbox = doubleStagePlanetaryGearbox, 
                 FOS=2.0, 
                 serviceFactor=2.0, 
                 maxGearboxDiameter=140.0,
                 stressAnalysisMethodName = "Lewis"):
      
        self.motor = motor
        self.doubleStagePlanetaryGearbox = doubleStagePlanetaryGearbox
        self.FOS = FOS
        self.serviceFactor = serviceFactor
        self.maxGearboxDiameter = maxGearboxDiameter # TODO: convert it to 
                                                     # outer diameter of 
                                                     # the motor
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
        self.Bearing_ID_stg1_MM        : float | None = None
        self.Bearing_OD_stg1_MM        : float | None = None
        self.Bearing_thickness_stg1_MM : float | None = None
        self.Bearing_mass_stg1_KG      : float | None = None

        self.bearing_mounting_thickness_stg1 : float | None = None

        self.design_params       = design_parameters
        self.motor_driver_params = motor_driver_params

        # ===== Set the Design Variables =====
        self.setVariables()

        self.actuator_width = 0

    def cost(self):
        mass = self.getMassKG_3DP()
        eff = self.doubleStagePlanetaryGearbox.getEfficiency()
        width = self.doubleStagePlanetaryGearbox.Stage1.fwPlanetMM + self.doubleStagePlanetaryGearbox.Stage2.fwPlanetMM
        cost = mass - 2 * eff + 0.2 * width
        return cost 

    def setVariables_stg1(self):
        ## --------------------------------------------------------------------
        ## Stage 1 - Input Parameters & Constants
        ## --------------------------------------------------------------------
        
        # Input gear parameters from the parent object
        self.Ns1 = self.doubleStagePlanetaryGearbox.Stage1.Ns
        self.Np1 = self.doubleStagePlanetaryGearbox.Stage1.Np
        self.num_planet1 = self.doubleStagePlanetaryGearbox.Stage1.numPlanet
        self.module1 = self.doubleStagePlanetaryGearbox.Stage1.module

        self.fw_s1_calc = self.doubleStagePlanetaryGearbox.Stage1.fwSunMM
        self.fw_r1      = self.doubleStagePlanetaryGearbox.Stage1.fwRingMM

        # Shared constants and design parameters
        self.pressure_angle = self.doubleStagePlanetaryGearbox.Stage1.getPressureAngleRad() * 180 / np.pi

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
        self.Motor_case_thickness                       = self.design_params["Motor_case_thickness"] # 2.5
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
        ## Motor, Driver, and Base Plate Dimensions
        ## --------------------------------------------------------------------
        self.motor_OD                   = self.motorDiaMM    # 88.6
        self.motor_height               = self.motorLengthMM # 43
        self.motor_mount_hole_PCD       = self.motor.motor_mount_hole_PCD # 32
        self.motor_mount_hole_dia       = self.motor.motor_mount_hole_dia # 4
        self.motor_mount_hole_num       = self.motor.motor_mount_hole_num # 4
        self.motor_output_hole_PCD      = self.motor.motor_output_hole_PCD # 23
        self.motor_output_hole_dia      = self.motor.motor_output_hole_dia # 4
        self.motor_output_hole_num      = self.motor.motor_output_hole_num # 4
        self.wire_slot_dist_from_center = self.motor.wire_slot_dist_from_center # 30
        self.wire_slot_length           = self.motor.wire_slot_length # 10
        self.wire_slot_radius           = self.motor.wire_slot_radius # 4
        
        motor_output_hole_bolt = nuts_and_bolts_dimensions(bolt_dia = self.motor_output_hole_dia, bolt_type="CSK")

        self.motor_output_hole_CSK_OD          = motor_output_hole_bolt.bolt_head_dia
        self.motor_output_hole_CSK_head_height = motor_output_hole_bolt.bolt_head_height

        self.central_hole_offset_from_motor_mount_PCD = self.design_params["central_hole_offset_from_motor_mount_PCD"] # 5
        
        self.base_plate_thickness = self.design_params["base_plate_thickness"] # 4
        self.air_flow_hole_offset = self.design_params["air_flow_hole_offset"] # 3

        # === Driver ===
        self.driver_upper_holes_dist_from_center = self.motor_driver_params["driver_upper_holes_dist_from_center"] # 23
        self.driver_lower_holes_dist_from_center = self.motor_driver_params["driver_lower_holes_dist_from_center"] # 15
        self.driver_side_holes_dist_from_center  = self.motor_driver_params["driver_side_holes_dist_from_center"]  # 20
        self.driver_mount_holes_dia              = self.motor_driver_params["driver_mount_holes_dia"]              # 2.5
        self.driver_mount_inserts_OD             = self.motor_driver_params["driver_mount_inserts_OD"]             # 3.5
        self.driver_mount_thickness              = self.motor_driver_params["driver_mount_thickness"]              # 1.5
        self.driver_mount_height                 = self.motor_driver_params["driver_mount_height"]                 # 4

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
        req_bearing1_ID = self.module1 * (self.Ns1 + self.Np1) + self.bearingIDClearanceMM
        Bearing1 = bearings_discrete(req_bearing1_ID)
        self.bearing1_ID = Bearing1.getBearingIDMM()
        self.bearing1_OD = Bearing1.getBearingODMM()
        self.bearing1_height = Bearing1.getBearingWidthMM()


        case_mounting_bolt = nuts_and_bolts_dimensions(bolt_dia = self.case_mounting_hole_dia, bolt_type="socket_head")
        
        self.case_mounting_hole_allen_socket_dia = case_mounting_bolt.bolt_head_dia
        self.case_mounting_wrench_size           = case_mounting_bolt.nut_width_across_flats # 5.5
        self.case_mounting_nut_thickness         = case_mounting_bolt.nut_thickness # 2.4

        # Housing and case calculations
        self.ring_OD1 = self.Nr1 * self.module1 + self.ring_radial_thickness * 2
        self.clearance_motor_and_case = (5 if self.ring_OD1 < self.motor_OD else (self.ring_OD1 - self.motor_OD) / 2 + 5)
        self.motor_case_OD_base = self.motor_OD + self.clearance_motor_and_case * 2 + self.Motor_case_thickness * 2
        self.Motor_case_ID = self.motor_OD + self.clearance_motor_and_case * 2
        self.case_mounting_hole_shift = self.case_mounting_hole_dia / 2 - 0.5
        self.case_mounting_PCD = self.motor_case_OD_base + self.case_mounting_hole_shift * 2
        self.Motor_case_OD_max = self.case_mounting_PCD + self.case_mounting_hole_allen_socket_dia + self.clearance_case_mount_holes_shell_thickness * 2

        # Mounting thickness and PCD
        self.bearing_mount_thickness1 = (self.output_mounting_hole_dia1 * 2 if (self.bearing1_OD + self.output_mounting_hole_dia1 * 4) > (self.Nr1 * self.module1 + 2 * self.h_b1) else ((self.Nr1 * self.module1 + 2 * self.h_b1 - (self.bearing1_OD + self.output_mounting_hole_dia1 * 4)) / 2) + self.output_mounting_hole_dia1 * 2 + self.standard_clearance_1_5mm)
        self.output_mounting_PCD1 = self.bearing1_OD + self.bearing_mount_thickness1
        
        # Carrier and final assembly dimensions
        self.carrier_PCD1 = (self.Np1 + self.Ns1) * self.module1
        self.fw_s1_used = self.fw_p1 + self.clearance_planet + self.sec_carrier_thickness1 + self.standard_clearance_1_5mm
        self.case_dist1 = self.sec_carrier_thickness1 + self.clearance_planet + self.sun_coupler_hub_thickness1 - self.case_mounting_surface_height
        self.sun_hub_dia1 = self.motor_output_hole_PCD + self.motor_output_hole_dia + self.standard_clearance_1_5mm * 4

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

        output_mounting_bolt1 =  nuts_and_bolts_dimensions(bolt_dia = self.output_mounting_hole_dia1, bolt_type="socket_head")

        self.output_mounting_nut_wrench_size1 = output_mounting_bolt1.nut_width_across_flats # 7
        self.output_mounting_nut_thickness1   = output_mounting_bolt1.nut_thickness # 3.2 

        planet_pin_bolt1 = nuts_and_bolts_dimensions(bolt_dia = self.planet_pin_bolt_dia1, bolt_type="socket_head")

        self.planet_pin_socket_head_dia1  = planet_pin_bolt1.bolt_head_dia    # 8.5
        self.planet_pin_bolt_wrench_size1 = planet_pin_bolt1.nut_width_across_flats # 8
        
        carrier_trapezoidal_support_hole_bolt1 = nuts_and_bolts_dimensions(bolt_dia = self.carrier_trapezoidal_support_hole_dia1, bolt_type="socket_head")

        self.carrier_trapezoidal_support_hole_socket_head_dia1 = carrier_trapezoidal_support_hole_bolt1.bolt_head_dia    # 5.5
        self.carrier_trapezoidal_support_hole_wrench_size1     = carrier_trapezoidal_support_hole_bolt1.nut_width_across_flats # 5.5

        sun_central_bolt1 = nuts_and_bolts_dimensions(bolt_dia = self.sun_central_bolt_dia1, bolt_type="socket_head")

        self.sun_central_bolt_socket_head_dia1 = sun_central_bolt1.bolt_head_dia # 8.5

    def setVariables_stg2(self):
        ## --------------------------------------------------------------------
        ## Stage 2 - Input Parameters & Constants
        ## --------------------------------------------------------------------

        # Input gear parameters from the parent object
        self.Ns2 = self.doubleStagePlanetaryGearbox.Stage2.Ns
        self.Np2 = self.doubleStagePlanetaryGearbox.Stage2.Np
        self.module2 = self.doubleStagePlanetaryGearbox.Stage2.module
        self.num_planet2 = self.doubleStagePlanetaryGearbox.Stage2.numPlanet


        self.fw_s2_calc = self.doubleStagePlanetaryGearbox.Stage2.fwSunMM
        self.fw_r2      = self.doubleStagePlanetaryGearbox.Stage2.fwRingMM

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

        self.output_mounting_hole_dia2             = self.design_params["output_mounting_hole_dia2"] # 4
        self.planet_pin_bolt_dia2                  = self.design_params["planet_pin_bolt_dia2"] # 5
        self.carrier_trapezoidal_support_hole_dia2 = self.design_params["carrier_trapezoidal_support_hole_dia2"] # 3
        self.sun_central_bolt_dia2                 = self.design_params["sun_central_bolt_dia2"] # 5
        self.stg1_stg2_mounting_hole_dia           = self.design_params["stg1_stg2_mounting_hole_dia"] # 4
        self.stg1_stg2_mounting_pattern_width      = self.design_params["stg1_stg2_mounting_pattern_width"] # 12
        self.output_mounting_nut_depth2            = self.design_params["output_mounting_nut_depth2"] # 3

        
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

        # Stage 2 Bearing lookup
        req_bearing2_ID = self.module2 * (self.Ns2 + self.Np2) + self.bearingIDClearanceMM
        Bearing2 = bearings_discrete(req_bearing2_ID)
        self.bearing2_ID = Bearing2.getBearingIDMM()
        self.bearing2_OD = Bearing2.getBearingODMM()
        self.bearing2_height = Bearing2.getBearingWidthMM()

        # Output mounting hole/nut dimensions
        output_mounting_hole2 = nuts_and_bolts_dimensions(bolt_dia=self.output_mounting_hole_dia2)
        self.output_mounting_nut_wrench_size2 = output_mounting_hole2.nut_width_across_flats
        self.output_mounting_nut_thickness2 = output_mounting_hole2.nut_thickness

        # Planet pin bolt dimensions
        planet_bolt2 = nuts_and_bolts_dimensions(bolt_dia=self.planet_pin_bolt_dia2, bolt_type="socket_head")
        self.planet_pin_socket_head_dia2 = planet_bolt2.bolt_head_dia
        self.planet_pin_bolt_wrench_size2 = planet_bolt2.nut_width_across_flats
        
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
        self.fw_s2_used = self.fw_p2 + self.clearance_planet + self.sec_carrier_thickness2 + self.standard_clearance_1_5mm
        self.bearing_mount_thickness2 = (self.output_mounting_hole_dia2 * 2) if ((self.bearing2_OD + self.output_mounting_hole_dia2 * 4) > (self.Nr2 * self.module2 + 2 * self.h_b2)) else (((self.Nr2 * self.module2 + 2 * self.h_b2 - (self.bearing2_OD + self.output_mounting_hole_dia2 * 4)) / 2) + self.output_mounting_hole_dia2 * 2 + self.standard_clearance_1_5mm)
        self.output_mounting_PCD2 = self.bearing2_OD + self.bearing_mount_thickness2
        self.case_dist2 = self.sec_carrier_thickness2 + self.clearance_planet + self.standard_clearance_1_5mm - self.bearing_retainer_thickness2
        
        # Interface variables
        # Note: This final definition for stg1_stg2_mounting_extra_width is used, as it appears last.
        # It depends on variables from Stage 1 (self.bearing1_OD, self.bearing_mount_thickness1).
        self.stg1_stg2_mounting_extra_width = (0) if ((self.Nr2 * self.module2 + self.ring_radial_thickness * 2 + self.stg1_stg2_allen_socket_head_dia) / 2 + self.standard_clearance_1_5mm * 2 + self.stg1_stg2_allen_socket_head_dia / 2 - (self.bearing1_OD + self.bearing_mount_thickness1 * 2) / 2) < 0 else ((self.Nr2 * self.module2 + self.ring_radial_thickness * 2 + self.stg1_stg2_allen_socket_head_dia) / 2 + self.standard_clearance_1_5mm * 2 + self.stg1_stg2_allen_socket_head_dia / 2 - (self.bearing1_OD + self.bearing_mount_thickness1 * 2) / 2)

    def setVariables(self):
        self.setVariables_stg1()
        self.setVariables_stg2()

    def genEquationFile(self):
       self.setVariables()
       file_path = os.path.join(os.path.dirname(__file__),'DSPG', 'dspg_equations_stg1.txt')
       with open(file_path, 'w') as file1:
        lines = [
                f'"Ns" = {self.Ns1}\n',
                f'"Np" = {self.Np1}\n',
                f'"Nr" = {self.Nr1}\n',
                f'"num_planet" = {self.num_planet1}\n',
                f'"module" = {self.module1}\n',
                f'"pressure angle" = {self.pressure_angle}\n',
                f'"pressure_angle" = {self.pressure_angle}\n',
                f'"motor_mount_hole_PCD" = {self.motor_mount_hole_PCD}\n',
                f'"motor_mount_hole_dia" = {self.motor_mount_hole_dia}\n',
                f'"motor_mount_hole_num" = {self.motor_mount_hole_num}\n',
                f'"motor_output_hole_PCD" = {self.motor_output_hole_PCD}\n',
                f'"motor_output_hole_dia" = {self.motor_output_hole_dia}\n',
                f'"motor_output_hole_num" = {self.motor_output_hole_num}\n',
                f'"motor_OD" = {self.motor_OD}\n',
                f'"motor_height" = {self.motor_height}\n',
                f'"wire_slot_dist_from_center" = {self.wire_slot_dist_from_center}\n',
                f'"wire_slot_length" = {self.wire_slot_length}\n',
                f'"wire_slot_radius" = {self.wire_slot_radius}\n',
                f'"h_a" = {self.h_a1}\n',
                f'"h_b" = {self.h_b1}\n',
                f'"h_f" = {self.h_f1}\n',
                f'"clr_tip_root" = {self.clr_tip_root1}\n',
                f'"dp_s" = {self.dp_s1}\n',
                f'"db_s" = {self.db_s1}\n',
                f'"fw_s_calc" = {self.fw_s1_calc}\n',
                f'"alpha_s" = {self.alpha_s1}\n',
                f'"beta_s" = {self.beta_s1}\n',
                f'"dp_p" = {self.dp_p1}\n',
                f'"db_p" = {self.db_p1}\n',
                f'"fw_p" = {self.fw_p1}\n',
                f'"alpha_p" = {self.alpha_p1}\n',
                f'"beta_p" = {self.beta_p1}\n',
                f'"dp_r" = {self.dp_r1}\n',
                f'"db_r" = {self.db_r1}\n',
                f'"fw_r" = {self.fw_r1}\n',
                f'"alpha_r" = {self.alpha_r1}\n',
                f'"beta_r" = {self.beta_r1}\n',
                f'"bearing_ID" = {self.bearing1_ID}\n',
                f'"bearing_OD" = {self.bearing1_OD}\n',
                f'"bearing_height" = {self.bearing1_height}\n',
                f'"clearance_planet" = {self.clearance_planet}\n',
                f'"case_dist" = {self.case_dist1}\n',
                f'"Motor_case_OD_max" = {self.Motor_case_OD_max}\n',
                f'"case_mounting_PCD" = {self.case_mounting_PCD}\n',
                f'"bearing mount thickness" = {self.bearing_mount_thickness1}\n',
                f'"case_mounting_hole_dia" = {self.case_mounting_hole_dia}\n',
                f'"output_mounting_PCD" = {self.output_mounting_PCD1}\n',
                f'"output_mounting_hole_dia" = {self.output_mounting_hole_dia1}\n',
                f'"clearance_case_mount_holes_shell_thickness" = {self.clearance_case_mount_holes_shell_thickness}\n',
                f'"motor_case_OD_base" = {self.motor_case_OD_base}\n',
                f'"sec_carrier_thickness" = {self.sec_carrier_thickness1}\n',
                f'"sun_coupler_hub_thickness" = {self.sun_coupler_hub_thickness1}\n',
                f'"clearance_sun_coupler_sec_carrier" = {self.clearance_sun_coupler_sec_carrier}\n',
                f'"clearance_motor_and_case" = {self.clearance_motor_and_case}\n',
                f'"Motor_case_thickness" = {self.Motor_case_thickness}\n',
                f'"Motor_case_ID" = {self.Motor_case_ID}\n',
                f'"case_mounting_hole_shift" = {self.case_mounting_hole_shift}\n',
                f'"output_mounting_nut_wrench_size" = {self.output_mounting_nut_wrench_size1}\n',
                f'"output_mounting_nut_thickness" = {self.output_mounting_nut_thickness1}\n',
                f'"case_mounting_hole_allen_socket_dia" = {self.case_mounting_hole_allen_socket_dia}\n',
                f'"output_mounting_nut_depth" = {self.output_mounting_nut_depth1}\n',
                f'"case_mounting_bolt_depth" = {self.case_mounting_bolt_depth}\n',
                f'"ring_radial_thickness" = {self.ring_radial_thickness}\n',
                f'"ring_OD" = {self.ring_OD1}\n',
                f'"ring_to_chamfer_clearance" = {self.ring_to_chamfer_clearance1}\n',
                f'"Motor_case_OD_base_to_chamfer" = {self.Motor_case_OD_base_to_chamfer}\n',
                f'"pattern_offset_from_motor_case_OD_base" = {self.pattern_offset_from_motor_case_OD_base}\n',
                f'"pattern_bulge_dia" = {self.pattern_bulge_dia}\n',
                f'"pattern_num_bulge" = {self.pattern_num_bulge}\n',
                f'"pattern_depth" = {self.pattern_depth}\n',
                f'"case_mounting_wrench_size" = {self.case_mounting_wrench_size}\n',
                f'"case_mounting_nut_clearance" = {self.case_mounting_nut_clearance}\n',
                f'"base_plate_thickness" = {self.base_plate_thickness}\n',
                f'"case_mounting_nut_thickness" = {self.case_mounting_nut_thickness}\n',
                f'"case_mounting_surface_height" = {self.case_mounting_surface_height}\n',
                f'"central_hole_offset_from_motor_mount_PCD" = {self.central_hole_offset_from_motor_mount_PCD}\n',
                f'"driver_upper_holes_dist_from_center" = {self.driver_upper_holes_dist_from_center}\n',
                f'"driver_lower_holes_dist_from_center" = {self.driver_lower_holes_dist_from_center}\n',
                f'"driver_side_holes_dist_from_center" = {self.driver_side_holes_dist_from_center}\n',
                f'"driver_mount_holes_dia" = {self.driver_mount_holes_dia}\n',
                f'"driver_mount_inserts_OD" = {self.driver_mount_inserts_OD}\n',
                f'"driver_mount_thickness" = {self.driver_mount_thickness}\n',
                f'"driver_mount_height" = {self.driver_mount_height}\n',
                f'"air_flow_hole_offset" = {self.air_flow_hole_offset}\n',
                f'"planet_pin_bolt_dia" = {self.planet_pin_bolt_dia1}\n',
                f'"planet_pin_socket_head_dia" = {self.planet_pin_socket_head_dia1}\n',
                f'"carrier_PCD" = {self.carrier_PCD1}\n',
                f'"planet_shaft_dia" = {self.planet_shaft_dia1}\n',
                f'"planet_shaft_step_offset" = {self.planet_shaft_step_offset}\n',
                f'"carrier_trapezoidal_support_sun_offset" = {self.carrier_trapezoidal_support_sun_offset1}\n',
                f'"carrier_trapezoidal_support_hole_PCD_offset_bearing_ID" = {self.carrier_trapezoidal_support_hole_PCD_offset_bearing_ID1}\n',
                f'"carrier_trapezoidal_support_hole_dia" = {self.carrier_trapezoidal_support_hole_dia1}\n',
                f'"carrier_trapezoidal_support_hole_socket_head_dia" = {self.carrier_trapezoidal_support_hole_socket_head_dia1}\n',
                f'"carrier_bearing_step_width" = {self.carrier_bearing_step_width}\n',
                f'"standard_clearance_1_5mm" = {self.standard_clearance_1_5mm}\n',
                f'"standard_fillet_1_5mm" = {self.standard_fillet_1_5mm}\n',
                f'"sun_shaft_bearing_OD" = {self.sun_shaft_bearing_OD1}\n',
                f'"sun_shaft_bearing_width" = {self.sun_shaft_bearing_width1}\n',
                f'"standard_bearing_insertion_chamfer" = {self.standard_bearing_insertion_chamfer}\n',
                f'"carrier_trapezoidal_support_hole_wrench_size" = {self.carrier_trapezoidal_support_hole_wrench_size1}\n',
                f'"planet_pin_bolt_wrench_size" = {self.planet_pin_bolt_wrench_size1}\n',
                f'"planet_bearing_OD" = {self.planet_bearing_OD1}\n',
                f'"planet_bearing_width" = {self.planet_bearing_width1}\n',
                f'"planet_bore" = {self.planet_bore1}\n',
                f'"sun_shaft_bearing_ID" = {self.sun_shaft_bearing_ID1}\n',
                f'"sun_hub_dia" = {self.sun_hub_dia1}\n',
                f'"sun_central_bolt_dia" = {self.sun_central_bolt_dia1}\n',
                f'"sun_central_bolt_socket_head_dia" = {self.sun_central_bolt_socket_head_dia1}\n',
                f'"fw_s_used" = {self.fw_s1_used}\n',
                f'"motor_output_hole_CSK_OD" = {self.motor_output_hole_CSK_OD}\n',
                f'"motor_output_hole_CSK_head_height" = {self.motor_output_hole_CSK_head_height}\n',
                f'"bearing_retainer_thickness" = {self.bearing_retainer_thickness1}\n',
                f'"stg1_stg2_mounting_pattern_width" = {self.stg1_stg2_mounting_pattern_width}\n',
                f'"stg1_stg2_allen_socket_head_dia" = {self.stg1_stg2_allen_socket_head_dia}\n',
                f'"stg1_stg2_mounting_hole_dia" = {self.stg1_stg2_mounting_hole_dia}\n',
                f'"Ns2" = {self.Ns2}\n',
                f'"Np2" = {self.Np2}\n',
                f'"Nr2" = {self.Nr2}\n',
                f'"module2" = {self.module2}\n',
                f'"stg1_stg2_mounting_extra_width" = {self.stg1_stg2_mounting_extra_width}\n',
                f'"dp_s2" = {self.dp_s2}\n',
                f'"db_s2" = {self.db_s2}\n',
                f'"fw_s_calc2" = {self.fw_s2_calc}\n',
                f'"alpha_s2" = {self.alpha_s2}\n',
                f'"beta_s2" = {self.beta_s2}\n',
                f'"fw_s_used2" = {self.fw_s2_used}\n',
                f'"fw_p2" = {self.fw_p2}\n',
                f'"tight_clearance_3DP" = {self.tight_clearance_3DP}\n',
                f'"loose_clearance_3DP" = {self.loose_clearance_3DP}\n' 
            ]
        file1.writelines(lines)
       file1.close()
       file_path = os.path.join(os.path.dirname(__file__),'DSPG', 'dspg_equations_stg2.txt')
       with open(file_path, 'w') as file2:
        lines = [
            f'"Ns" = {self.Ns2}\n',
            f'"Np" = {self.Np2}\n',
            f'"Nr" = {self.Nr2}\n',
            f'"module" = {self.module2}\n',
            f'"pressure_angle" = {self.pressure_angle}\n',
            f'"h_a" = {self.h_a2}\n',
            f'"h_f" = {self.h_f2}\n',
            f'"clr_tip_root" = {self.clr_tip_root2}\n',
            f'"dp_r" = {self.dp_r2}\n',
            f'"db_r" = {self.db_r2}\n',
            f'"fw_r" = {self.fw_r2}\n',
            f'"alpha_r" = {self.alpha_r2}\n',
            f'"beta_r" = {self.beta_r2}\n',
            f'"bearing_ID" = {self.bearing2_ID}\n',
            f'"bearing_OD" = {self.bearing2_OD}\n',
            f'"bearing_height" = {self.bearing2_height}\n',
            f'"clearance_planet" = {self.clearance_planet}\n',
            f'"case_dist" = {self.case_dist2}\n',
            f'"Motor_case_OD_max" = {self.Motor_case_OD_max}\n',
            f'"case_mounting_PCD" = {self.case_mounting_PCD}\n',
            f'"bearing mount thickness" = {self.bearing_mount_thickness2}\n',
            f'"case_mounting_hole_dia" = {self.case_mounting_hole_dia}\n',
            f'"output_mounting_PCD" = {self.output_mounting_PCD2}\n',
            f'"output_mounting_hole_dia" = {self.output_mounting_hole_dia2}\n',
            f'"clearance_case_mount_holes_shell_thickness" = {self.clearance_case_mount_holes_shell_thickness}\n',
            f'"motor_case_OD_base" = {self.motor_case_OD_base}\n',
            f'"sec_carrier_thickness" = {self.sec_carrier_thickness2}\n',
            f'"sun_coupler_hub_thickness" = {getattr(self, "sun_coupler_hub_thickness1", "N/A")}\n', # Note: Using stg1 value
            f'"clearance_sun_coupler_sec_carrier" = {self.clearance_sun_coupler_sec_carrier}\n',
            f'"clearance_motor_and_case" = {self.clearance_motor_and_case}\n',
            f'"motor_OD" = {self.motor_OD}\n',
            f'"Motor_case_thickness" = {self.Motor_case_thickness}\n',
            f'"Motor_case_ID" = {self.Motor_case_ID}\n',
            f'"case_mounting_hole_shift" = {self.case_mounting_hole_shift}\n',
            f'"output_mounting_nut_wrench_size" = {self.output_mounting_nut_wrench_size2}\n',
            f'"output_mounting_nut_thickness" = {self.output_mounting_nut_thickness2}\n',
            f'"case_mounting_hole_allen_socket_dia" = {self.case_mounting_hole_allen_socket_dia}\n',
            f'"output_mounting_nut_depth" = {self.output_mounting_nut_depth2}\n',
            f'"case_mounting_bolt_depth" = {self.case_mounting_bolt_depth}\n',
            f'"ring_radial_thickness" = {self.ring_radial_thickness}\n',
            f'"ring_OD" = {self.ring_OD2}\n',
            f'"ring_to_chamfer_clearance" = {self.ring_to_chamfer_clearance2}\n',
            f'"Motor_case_OD_base_to_chamfer" = {self.Motor_case_OD_base_to_chamfer}\n',
            f'"pattern_offset_from_motor_case_OD_base" = {self.pattern_offset_from_motor_case_OD_base}\n',
            f'"pattern_bulge_dia" = {self.pattern_bulge_dia}\n',
            f'"pattern_num_bulge" = {self.pattern_num_bulge}\n',
            f'"pattern_depth" = {self.pattern_depth}\n',
            f'"motor_height" = {self.motor_height}\n',
            f'"case_mounting_wrench_size" = {self.case_mounting_wrench_size}\n',
            f'"case_mounting_nut_clearance" = {self.case_mounting_nut_clearance}\n',
            f'"base_plate_thickness" = {self.base_plate_thickness}\n',
            f'"case_mounting_nut_thickness" = {self.case_mounting_nut_thickness}\n',
            f'"case_mounting_surface_height" = {self.case_mounting_surface_height}\n',
            f'"motor_mount_hole_PCD" = {self.motor_mount_hole_PCD}\n',
            f'"motor_mount_hole_dia" = {self.motor_mount_hole_dia}\n',
            f'"motor_mount_hole_num" = {self.motor_mount_hole_num}\n',
            f'"central_hole_offset_from_motor_mount_PCD" = {self.central_hole_offset_from_motor_mount_PCD}\n',
            f'"wire_slot_dist_from_center" = {self.wire_slot_dist_from_center}\n',
            f'"wire_slot_length" = {self.wire_slot_length}\n',
            f'"wire_slot_radius" = {self.wire_slot_radius}\n',
            f'"driver_upper_holes_dist_from_center" = {self.driver_upper_holes_dist_from_center}\n',
            f'"driver_lower_holes_dist_from_center" = {self.driver_lower_holes_dist_from_center}\n',
            f'"driver_side_holes_dist_from_center" = {self.driver_side_holes_dist_from_center}\n',
            f'"driver_mount_holes_dia" = {self.driver_mount_holes_dia}\n',
            f'"driver_mount_inserts_OD" = {self.driver_mount_inserts_OD}\n',
            f'"driver_mount_thickness" = {self.driver_mount_thickness}\n',
            f'"driver_mount_height" = {self.driver_mount_height}\n',
            f'"air_flow_hole_offset" = {self.air_flow_hole_offset}\n',
            f'"num_planet" = {self.num_planet2}\n',
            f'"planet_pin_bolt_dia" = {self.planet_pin_bolt_dia2}\n',
            f'"planet_pin_socket_head_dia" = {self.planet_pin_socket_head_dia2}\n',
            f'"carrier_PCD" = {self.carrier_PCD2}\n',
            f'"planet_shaft_dia" = {self.planet_shaft_dia2}\n',
            f'"fw_p" = {self.fw_p2}\n',
            f'"planet_shaft_step_offset" = {self.planet_shaft_step_offset2}\n',
            f'"carrier_trapezoidal_support_sun_offset" = {self.carrier_trapezoidal_support_sun_offset2}\n',
            f'"carrier_trapezoidal_support_hole_PCD_offset_bearing_ID" = {self.carrier_trapezoidal_support_hole_PCD_offset_bearing_ID2}\n',
            f'"carrier_trapezoidal_support_hole_dia" = {self.carrier_trapezoidal_support_hole_dia2}\n',
            f'"carrier_trapezoidal_support_hole_socket_head_dia" = {self.carrier_trapezoidal_support_hole_socket_head_dia2}\n',
            f'"carrier_bearing_step_width" = {self.carrier_bearing_step_width2}\n',
            f'"standard_clearance_1_5mm" = {self.standard_clearance_1_5mm}\n',
            f'"standard_fillet_1_5mm" = {self.standard_fillet_1_5mm}\n',
            f'"sun_shaft_bearing_OD" = {self.sun_shaft_bearing_OD2}\n',
            f'"sun_shaft_bearing_width" = {self.sun_shaft_bearing_width2}\n',
            f'"standard_bearing_insertion_chamfer" = {self.standard_bearing_insertion_chamfer}\n',
            f'"carrier_trapezoidal_support_hole_wrench_size" = {self.carrier_trapezoidal_support_hole_wrench_size2}\n',
            f'"planet_pin_bolt_wrench_size" = {self.planet_pin_bolt_wrench_size2}\n',
            f'"pressure angle" = {self.pressure_angle}\n', 
            f'"motor_output_hole_PCD" = {self.motor_output_hole_PCD}\n',
            f'"motor_output_hole_dia" = {self.motor_output_hole_dia}\n',
            f'"motor_output_hole_num" = {self.motor_output_hole_num}\n',
            f'"h_b" = {self.h_b2}\n',
            f'"dp_s" = {self.dp_s2}\n',
            f'"db_s" = {self.db_s2}\n',
            f'"fw_s_calc" = {self.fw_s2_calc}\n',
            f'"alpha_s" = {self.alpha_s2}\n',
            f'"beta_s" = {self.beta_s2}\n',
            f'"dp_p" = {self.dp_p2}\n',
            f'"db_p" = {self.db_p2}\n',
            f'"alpha_p" = {self.alpha_p2}\n',
            f'"beta_p" = {self.beta_p2}\n',
            f'"planet_bearing_OD" = {self.planet_bearing_OD2}\n',
            f'"planet_bearing_width" = {self.planet_bearing_width2}\n',
            f'"planet_bore" = {self.planet_bore2}\n',
            f'"sun_shaft_bearing_ID" = {self.sun_shaft_bearing_ID2}\n',
            f'"sun_hub_dia" = {self.sun_hub_dia1}\n', 
            f'"sun_central_bolt_dia" = {self.sun_central_bolt_dia2}\n',
            f'"sun_central_bolt_socket_head_dia" = {self.sun_central_bolt_socket_head_dia2}\n',
            f'"fw_s_used" = {self.fw_s2_used}\n',
            f'"motor_output_hole_CSK_OD" = {self.motor_output_hole_CSK_OD}\n',
            f'"motor_output_hole_CSK_head_height" = {self.motor_output_hole_CSK_head_height}\n',
            f'"bearing_retainer_thickness" = {self.bearing_retainer_thickness2}\n',
            f'"Ns1" = {self.Ns1}\n',
            f'"Np1" = {self.Np1}\n',
            f'"Nr1" = {self.Nr1}\n',
            f'"module1" = {self.module1}\n',
            f'"bearing1_ID" = {self.bearing1_ID}\n',
            f'"bearing1_OD" = {self.bearing1_OD}\n',
            f'"bearing1_height1" = {self.bearing1_height}\n',
            f'"bearing mount thickness1" = {self.bearing_mount_thickness1}\n',
            f'"output_mounting_PCD1" = {self.output_mounting_PCD1}\n',
            f'"num_planet1" = {self.num_planet1}\n',
            f'"stg1_stg2_mounting_pattern_width" = {self.stg1_stg2_mounting_pattern_width}\n',
            f'"stg1_stg2_allen_socket_head_dia" = {self.stg1_stg2_allen_socket_head_dia}\n',
            f'"stg1_stg2_mounting_hole_dia" = {self.stg1_stg2_mounting_hole_dia}\n',
            f'"stg1_stg2_mounting_extra_width" = {self.stg1_stg2_mounting_extra_width}\n',
            f'"tight_clearance_3DP" = {self.tight_clearance_3DP}\n',
            f'"loose_clearance_3DP" = {self.loose_clearance_3DP}\n' 
            ]
        file2.writelines(lines)
       file2.close()

    #--------------------------------
    # Update Facewidths
    #--------------------------------
    def getToothForces(self, constraintCheck=True):
        if constraintCheck:
            # Check if the constraints are satisfied
            if not self.doubleStagePlanetaryGearbox.Stage1.geometricConstraint():
                print("Geometric constraint not satisfied in Layer 1")
                return
            if not self.doubleStagePlanetaryGearbox.Stage1.meshingConstraint():
                print("Meshing constraint not satisfied in Layer 1")
                return
            if not self.doubleStagePlanetaryGearbox.Stage1.noPlanetInterferenceConstraint():
                print("No planet interference constraint not satisfied in Layer 1")
                return
            if not self.doubleStagePlanetaryGearbox.Stage2.geometricConstraint():
                print("Geometric constraint not satisfied in Layer 2")
                return
            if not self.doubleStagePlanetaryGearbox.Stage2.meshingConstraint():
                print("Meshing constraint not satisfied in Layer 2")
                return
            if not self.doubleStagePlanetaryGearbox.Stage2.noPlanetInterferenceConstraint():
                print("No planet interference constraint not satisfied in Layer 2")
                return
        
        Ns1 = self.doubleStagePlanetaryGearbox.Stage1.Ns
        Np1 = self.doubleStagePlanetaryGearbox.Stage1.Np
        Nr1 = self.doubleStagePlanetaryGearbox.Stage1.Nr
        module1 = self.doubleStagePlanetaryGearbox.Stage1.module
        numPlanet1 = self.doubleStagePlanetaryGearbox.Stage1.numPlanet

        Ns2 = self.doubleStagePlanetaryGearbox.Stage2.Ns
        Np2 = self.doubleStagePlanetaryGearbox.Stage2.Np
        Nr2 = self.doubleStagePlanetaryGearbox.Stage2.Nr
        module2 = self.doubleStagePlanetaryGearbox.Stage2.module
        numPlanet2 = self.doubleStagePlanetaryGearbox.Stage2.numPlanet

        Rs1_Mt = self.doubleStagePlanetaryGearbox.Stage1.getPCRadiusSunM()
        Rp1_Mt = self.doubleStagePlanetaryGearbox.Stage1.getPCRadiusPlanetM()
        Rr1_Mt = self.doubleStagePlanetaryGearbox.Stage1.getPCRadiusRingM()

        Rs2_Mt = self.doubleStagePlanetaryGearbox.Stage2.getPCRadiusSunM()
        Rp2_Mt = self.doubleStagePlanetaryGearbox.Stage2.getPCRadiusPlanetM()
        Rr2_Mt = self.doubleStagePlanetaryGearbox.Stage2.getPCRadiusRingM()

        GR1 = self.doubleStagePlanetaryGearbox.Stage1.gearRatio()
        GR2 = self.doubleStagePlanetaryGearbox.Stage2.gearRatio()
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
        if not self.doubleStagePlanetaryGearbox.Stage1.geometricConstraint():
            print("Geometric constraint not satisfied in Layer 1")
            return
        if not self.doubleStagePlanetaryGearbox.Stage1.meshingConstraint():
            print("Meshing constraint not satisfied in Layer 1")
            return
        if not self.doubleStagePlanetaryGearbox.noPlanetInterferenceConstraint():
            print("No planet interference constraint not satisfied")
            return
        if not self.doubleStagePlanetaryGearbox.Stage2.geometricConstraint():
            print("Geometric constraint not satisfied in Layer 2")
            return
        if not self.doubleStagePlanetaryGearbox.Stage2.meshingConstraint():
            print("Meshing constraint not satisfied in Layer 2")
            return
        # if not self.doubleStagePlanetaryGearbox.Stage2.noPlanetInterferenceConstraint():
        #     print("No planet interference constraint not satisfied in Layer 2")
        #     return
        
        Ns1 = self.doubleStagePlanetaryGearbox.Stage1.Ns
        Np1 = self.doubleStagePlanetaryGearbox.Stage1.Np
        Nr1 = self.doubleStagePlanetaryGearbox.Stage1.Nr
        module1 = self.doubleStagePlanetaryGearbox.Stage1.module
        numPlanet1 = self.doubleStagePlanetaryGearbox.Stage1.numPlanet

        Ns2 = self.doubleStagePlanetaryGearbox.Stage2.Ns
        Np2 = self.doubleStagePlanetaryGearbox.Stage2.Np
        Nr2 = self.doubleStagePlanetaryGearbox.Stage2.Nr
        module2 = self.doubleStagePlanetaryGearbox.Stage2.module
        numPlanet2 = self.doubleStagePlanetaryGearbox.Stage2.numPlanet

        Rs1_Mt = self.doubleStagePlanetaryGearbox.Stage1.getPCRadiusSunM()
        Rp1_Mt = self.doubleStagePlanetaryGearbox.Stage1.getPCRadiusPlanetM()
        Rr1_Mt = self.doubleStagePlanetaryGearbox.Stage1.getPCRadiusRingM()

        Rs2_Mt = self.doubleStagePlanetaryGearbox.Stage2.getPCRadiusSunM()
        Rp2_Mt = self.doubleStagePlanetaryGearbox.Stage2.getPCRadiusPlanetM()
        Rr2_Mt = self.doubleStagePlanetaryGearbox.Stage2.getPCRadiusRingM()

        GR1 = self.doubleStagePlanetaryGearbox.Stage1.gearRatio()
        GR2 = self.doubleStagePlanetaryGearbox.Stage2.gearRatio()
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

        P1 = np.pi*self.doubleStagePlanetaryGearbox.Stage1.module*0.001 # m
        P2 = np.pi*self.doubleStagePlanetaryGearbox.Stage2.module*0.001 # m

        bMin_sun1      = (self.FOS * Ft1 / (self.doubleStagePlanetaryGearbox.Stage1.maxGearAllowableStressPa * ySun1 * Kv_sun1 * P1)) # m
        bMin_planet1_1 = (self.FOS * Ft1 / (self.doubleStagePlanetaryGearbox.Stage1.maxGearAllowableStressPa * yPlanet1 * Kv_sun1 * P1))
        bMin_planet1_2 = (self.FOS * Ft1 / (self.doubleStagePlanetaryGearbox.Stage1.maxGearAllowableStressPa * yPlanet1 * Kv_planet1 * P1))
        bMin_ring1     = (self.FOS * Ft1 / (self.doubleStagePlanetaryGearbox.Stage1.maxGearAllowableStressPa * yRing1 * Kv_ring1 * P1)) 
  
        bMin_sun2      = (self.FOS * Ft2 / (self.doubleStagePlanetaryGearbox.Stage2.maxGearAllowableStressPa * ySun2 * Kv_sun2 * P2)) # m
        bMin_planet2_1 = (self.FOS * Ft2 / (self.doubleStagePlanetaryGearbox.Stage2.maxGearAllowableStressPa * yPlanet2 * Kv_sun2 * P2))
        bMin_planet2_2 = (self.FOS * Ft2 / (self.doubleStagePlanetaryGearbox.Stage2.maxGearAllowableStressPa * yPlanet2 * Kv_planet2 * P2))
        bMin_ring2     = (self.FOS * Ft2 / (self.doubleStagePlanetaryGearbox.Stage2.maxGearAllowableStressPa * yRing2 * Kv_ring2 * P2))

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

        self.doubleStagePlanetaryGearbox.Stage1.setfwSunMM(bMin_sun1*1000)
        self.doubleStagePlanetaryGearbox.Stage1.setfwPlanetMM(bMin_planet1*1000)
        self.doubleStagePlanetaryGearbox.Stage1.setfwRingMM(bMin_ring1*1000)
        self.doubleStagePlanetaryGearbox.Stage2.setfwSunMM(bMin_sun2*1000)
        self.doubleStagePlanetaryGearbox.Stage2.setfwPlanetMM(bMin_planet2*1000)
        self.doubleStagePlanetaryGearbox.Stage2.setfwRingMM(bMin_ring2*1000)

    def AGMAStressAnalysisMinFacewidth(self):
        # Check if the constraints are satisfied
        if not self.doubleStagePlanetaryGearbox.Stage1.geometricConstraint():
            print("Geometric constraint not satisfied in Layer 1")
            return
        if not self.doubleStagePlanetaryGearbox.Stage1.meshingConstraint():
            print("Meshing constraint not satisfied in Layer 1")
            return
        if not self.doubleStagePlanetaryGearbox.Stage1.noPlanetInterferenceConstraint():
            print("No planet interference constraint not satisfied in Layer 1")
            return
        if not self.doubleStagePlanetaryGearbox.Stage2.geometricConstraint():
            print("Geometric constraint not satisfied in Layer 2")
            return
        if not self.doubleStagePlanetaryGearbox.Stage2.meshingConstraint():
            print("Meshing constraint not satisfied in Layer 2")
            return
        if not self.doubleStagePlanetaryGearbox.Stage2.noPlanetInterferenceConstraint():
            print("No planet interference constraint not satisfied in Layer 2")
            return
        
        Ns1 = self.doubleStagePlanetaryGearbox.Stage1.Ns
        Np1 = self.doubleStagePlanetaryGearbox.Stage1.Np
        Nr1 = self.doubleStagePlanetaryGearbox.Stage1.Nr
        module1 = self.doubleStagePlanetaryGearbox.Stage1.module
        numPlanet1 = self.doubleStagePlanetaryGearbox.Stage1.numPlanet

        Ns2 = self.doubleStagePlanetaryGearbox.Stage2.Ns
        Np2 = self.doubleStagePlanetaryGearbox.Stage2.Np
        Nr2 = self.doubleStagePlanetaryGearbox.Stage2.Nr
        module2 = self.doubleStagePlanetaryGearbox.Stage2.module
        numPlanet2 = self.doubleStagePlanetaryGearbox.Stage2.numPlanet

        Rs1_Mt = self.doubleStagePlanetaryGearbox.Stage1.getPCRadiusSunM()
        Rp1_Mt = self.doubleStagePlanetaryGearbox.Stage1.getPCRadiusPlanetM()
        Rr1_Mt = self.doubleStagePlanetaryGearbox.Stage1.getPCRadiusRingM()

        Rs2_Mt = self.doubleStagePlanetaryGearbox.Stage2.getPCRadiusSunM()
        Rp2_Mt = self.doubleStagePlanetaryGearbox.Stage2.getPCRadiusPlanetM()
        Rr2_Mt = self.doubleStagePlanetaryGearbox.Stage2.getPCRadiusRingM()

        GR1 = self.doubleStagePlanetaryGearbox.Stage1.gearRatio()
        GR2 = self.doubleStagePlanetaryGearbox.Stage2.gearRatio()
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

        pressureAngle1 = self.doubleStagePlanetaryGearbox.Stage1.pressureAngle
        pressureAngle2 = self.doubleStagePlanetaryGearbox.Stage2.pressureAngle

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
        bMin_planet1 = (self.FOS * Wt1 * Kv_planet1 * Ks * Kh * Kb)/(module1 * Yj_planet1 * self.doubleStagePlanetaryGearbox.Stage1.maxGearAllowableStressPa * 0.001)
        bMin_sun1 = (self.FOS * Wt1 * Kv_sun1 * Ks * Kh * Kb) / (module1 * Yj_sun1 * self.doubleStagePlanetaryGearbox.Stage1.maxGearAllowableStressPa * 0.001)
        bMin_ring1 = (self.FOS * Wt1 * Kv_ring1 * Ks * Kh * Kb) / (module1 * Yj_ring1 * self.doubleStagePlanetaryGearbox.Stage1.maxGearAllowableStressPa * 0.001)
        # Stage 2
        bMin_planet2 = (self.FOS * Wt2 * Kv_planet2 * Ks * Kh * Kb)/(module2 * Yj_planet2 * self.doubleStagePlanetaryGearbox.Stage2.maxGearAllowableStressPa * 0.001)
        bMin_sun2 = (self.FOS * Wt2 * Kv_sun2 * Ks * Kh * Kb) / (module2 * Yj_sun2 * self.doubleStagePlanetaryGearbox.Stage2.maxGearAllowableStressPa * 0.001)
        bMin_ring2 = (self.FOS * Wt2 * Kv_ring2 * Ks * Kh * Kb) / (module2 * Yj_ring2 * self.doubleStagePlanetaryGearbox.Stage2.maxGearAllowableStressPa * 0.001)

        if bMin_ring1 < bMin_planet1:
            bMin_ring1 = bMin_planet1
        else:
            bMin_planet1 = bMin_ring1

        if bMin_ring2 < bMin_planet2:
            bMin_ring2 = bMin_planet2
        else:
            bMin_planet2 = bMin_ring2

        self.doubleStagePlanetaryGearbox.Stage1.setfwSunMM(bMin_sun1*1000)
        self.doubleStagePlanetaryGearbox.Stage1.setfwPlanetMM(bMin_planet1*1000)
        self.doubleStagePlanetaryGearbox.Stage1.setfwRingMM(bMin_ring1*1000)
        self.doubleStagePlanetaryGearbox.Stage2.setfwSunMM(bMin_sun2*1000)
        self.doubleStagePlanetaryGearbox.Stage2.setfwPlanetMM(bMin_planet2*1000)
        self.doubleStagePlanetaryGearbox.Stage2.setfwRingMM(bMin_ring2*1000)

    def mitStressAnalysisMinFacewidth(self):
        # Check if the constraints are satisfied
        if not self.doubleStagePlanetaryGearbox.Stage1.geometricConstraint():
            print("Geometric constraint not satisfied in Layer 1")
            return
        if not self.doubleStagePlanetaryGearbox.Stage1.meshingConstraint():
            print("Meshing constraint not satisfied in Layer 1")
            return
        if not self.doubleStagePlanetaryGearbox.noPlanetInterferenceConstraint():
            print("No planet interference constraint not satisfied")
            return
        if not self.doubleStagePlanetaryGearbox.Stage2.geometricConstraint():
            print("Geometric constraint not satisfied in Layer 2")
            return
        if not self.doubleStagePlanetaryGearbox.Stage2.meshingConstraint():
            print("Meshing constraint not satisfied in Layer 2")
            return
        # if not self.doubleStagePlanetaryGearbox.Stage2.noPlanetInterferenceConstraint():
        #     print("No planet interference constraint not satisfied in Layer 2")
        #     return
        
        Ns1 = self.doubleStagePlanetaryGearbox.Stage1.Ns
        Np1 = self.doubleStagePlanetaryGearbox.Stage1.Np
        Nr1 = self.doubleStagePlanetaryGearbox.Stage1.Nr
        module1 = self.doubleStagePlanetaryGearbox.Stage1.module
        numPlanet1 = self.doubleStagePlanetaryGearbox.Stage1.numPlanet

        Ns2 = self.doubleStagePlanetaryGearbox.Stage2.Ns
        Np2 = self.doubleStagePlanetaryGearbox.Stage2.Np
        Nr2 = self.doubleStagePlanetaryGearbox.Stage2.Nr
        module2 = self.doubleStagePlanetaryGearbox.Stage2.module
        numPlanet2 = self.doubleStagePlanetaryGearbox.Stage2.numPlanet

        Rs1_Mt = self.doubleStagePlanetaryGearbox.Stage1.getPCRadiusSunM()
        Rp1_Mt = self.doubleStagePlanetaryGearbox.Stage1.getPCRadiusPlanetM()
        Rr1_Mt = self.doubleStagePlanetaryGearbox.Stage1.getPCRadiusRingM()

        Rs2_Mt = self.doubleStagePlanetaryGearbox.Stage2.getPCRadiusSunM()
        Rp2_Mt = self.doubleStagePlanetaryGearbox.Stage2.getPCRadiusPlanetM()
        Rr2_Mt = self.doubleStagePlanetaryGearbox.Stage2.getPCRadiusRingM()

        GR1 = self.doubleStagePlanetaryGearbox.Stage1.gearRatio()
        GR2 = self.doubleStagePlanetaryGearbox.Stage2.gearRatio()
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

        _,_,CR1 = self.doubleStagePlanetaryGearbox.Stage1.contactRatio_sunPlanet()
        qe1 = 1 / CR1
        # qk = 1.85 + 0.35 * (np.log(Ns) / np.log(100)) 
        qk1 = (7.65734266e-08 * Ns1**4
            - 2.19500130e-05 * Ns1**3
            + 2.33893357e-03 * Ns1**2
            - 1.13320908e-01 * Ns1
            + 4.44727778)
        bMin_sun_mit1    = (self.FOS * Ft1 * qe1 * qk1 / (self.doubleStagePlanetaryGearbox.Stage1.maxGearAllowableStressPa * module1 * 0.001)) # m
        bMin_planet_mit1 = (self.FOS * Ft1 * qe1 * qk1 / (self.doubleStagePlanetaryGearbox.Stage1.maxGearAllowableStressPa * module1 * 0.001))
        bMin_ring_mit1   = (self.FOS * Ft1 * qe1 * qk1 / (self.doubleStagePlanetaryGearbox.Stage1.maxGearAllowableStressPa * module1 * 0.001))


        _,_,CR2 = self.doubleStagePlanetaryGearbox.Stage2.contactRatio_sunPlanet()
        qe2 = 1 / CR2
        # qk = 1.85 + 0.35 * (np.log(Ns) / np.log(100)) 
        qk2 = (7.65734266e-08 * Ns2**4
            - 2.19500130e-05 * Ns2**3
            + 2.33893357e-03 * Ns2**2
            - 1.13320908e-01 * Ns2
            + 4.44727778)
        bMin_sun_mit2    = (self.FOS * Ft2 * qe2 * qk2 / (self.doubleStagePlanetaryGearbox.Stage2.maxGearAllowableStressPa * module2 * 0.001)) # m
        bMin_planet_mit2 = (self.FOS * Ft2 * qe2 * qk2 / (self.doubleStagePlanetaryGearbox.Stage2.maxGearAllowableStressPa * module2 * 0.001))
        bMin_ring_mit2   = (self.FOS * Ft2 * qe2 * qk2 / (self.doubleStagePlanetaryGearbox.Stage2.maxGearAllowableStressPa * module2 * 0.001))

        #------------- Contraint in planet to accomodate its bearings------------------------------------------
        if (bMin_planet_mit1 * 1000 < (self.planet_bearing_width1*2 + self.standard_clearance_1_5mm * 2 / 3)) : 
            bMin_planet_mit1 = (self.planet_bearing_width1*2 + self.standard_clearance_1_5mm * 2 / 3) / 1000
            bMin_ring_mit1 = bMin_planet_mit1 # FT on both are same

        if (bMin_planet_mit2 * 1000 < (self.planet_bearing_width2*2 + self.standard_clearance_1_5mm * 2 / 3)) : 
            bMin_planet_mit2 = (self.planet_bearing_width2*2 + self.standard_clearance_1_5mm * 2 / 3) / 1000
            bMin_ring_mit2 = bMin_planet_mit2 # FT on both are same



        self.doubleStagePlanetaryGearbox.Stage1.setfwSunMM      (bMin_sun_mit1*1000)
        self.doubleStagePlanetaryGearbox.Stage1.setfwPlanetMM   (bMin_planet_mit1*1000)
        self.doubleStagePlanetaryGearbox.Stage1.setfwRingMM     (bMin_ring_mit1*1000)
        self.doubleStagePlanetaryGearbox.Stage2.setfwSunMM      (bMin_sun_mit2*1000)
        self.doubleStagePlanetaryGearbox.Stage2.setfwPlanetMM   (bMin_planet_mit2*1000)
        self.doubleStagePlanetaryGearbox.Stage2.setfwRingMM     (bMin_ring_mit2*1000)

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
        module    = self.doubleStagePlanetaryGearbox.Stage1.module
        Ns        = self.doubleStagePlanetaryGearbox.Stage1.Ns
        Np        = self.doubleStagePlanetaryGearbox.Stage1.Np
        Nr        = self.doubleStagePlanetaryGearbox.Stage1.Nr
        numPlanet = self.doubleStagePlanetaryGearbox.Stage1.numPlanet
        module2    = self.doubleStagePlanetaryGearbox.Stage2.module
        Ns2        = self.doubleStagePlanetaryGearbox.Stage2.Ns
        # Np        = self.doubleStagePlanetaryGearbox.Stage2.Np
        Nr2         = self.doubleStagePlanetaryGearbox.Stage2.Nr
        # numPlanet = self.doubleStagePlanetaryGearbox.Stage2.numPlanet

        #------------------------------------
        # density of materials
        #------------------------------------
        density_3DP_material = self.doubleStagePlanetaryGearbox.densityGears

        #------------------------------------
        # Face Width
        #------------------------------------
        sunFwMM     = self.doubleStagePlanetaryGearbox.Stage1.fwSunMM
        planetFwMM  = self.doubleStagePlanetaryGearbox.Stage1.fwPlanetMM
        ringFwMM    = self.doubleStagePlanetaryGearbox.Stage1.fwRingMM
        # sun2FwMM     = self.doubleStagePlanetaryGearbox.Stage2.fwSunMM
        planet2FwMM  = self.doubleStagePlanetaryGearbox.Stage2.fwPlanetMM
        # ring2FwMM    = self.doubleStagePlanetaryGearbox.Stage2.fwRingMM

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

        self.Bearing_ID_stg1_MM        = InnerDiaBearingMM # Bearings.getBearingIDMM()
        self.Bearing_OD_stg1_MM        = OuterDiaBearingMM # Bearings.getBearingODMM()
        self.Bearing_thickness_stg1_MM = WidthBearingMM    # Bearings.getBearingWidthMM()
        self.Bearing_mass_stg1_KG      = BearingMassKG     # Bearings.getBearingMassKG()

        #======================================
        # Mass Calculation
        #======================================
        #--------------------------------------
        # Independent variables
        #--------------------------------------
        # To be written in Gearbox(dspg) JSON files
        case_mounting_surface_height    = self.case_mounting_surface_height
        standard_clearance_1_5mm        = self.standard_clearance_1_5mm    
        base_plate_thickness            = self.base_plate_thickness        
        Motor_case_thickness            = self.Motor_case_thickness        
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

        # To be written in Motor JSON files
        motor_output_hole_PCD = self.motor.motor_output_hole_PCD
        motor_output_hole_dia = self.motor.motor_output_hole_dia

        #--------------------------------------
        # Dependent variables
        #--------------------------------------
        h_b = 1.25 * module

        #--------------------------------------
        # Mass: dspg_motor_casing
        #--------------------------------------
        ring_radial_thickness = self.ring_radial_thickness

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

        Motor_case_mass = Motor_case_volume * density_3DP_material

        #--------------------------------------
        # Mass: dspg_gearbox_casing
        #--------------------------------------
        # Mass of the gearbox includes the mass of:
        # 1. Ring gear
        # 2. Bearing holding structure
        # 3. Case mounting structure
        #--------------------------------------
        ring_ID        = Nr * module
        ringFwUsedMM   = ringFwMM + clearance_planet

        bearing_ID     = InnerDiaBearingMM 
        bearing_OD     = OuterDiaBearingMM 
        bearing_height = WidthBearingMM    
        bearing_mass   = BearingMassKG      

        if ((bearing_OD + output_mounting_hole_dia * 4) > (Nr * module + 2 * h_b)):
            bearing_mount_thickness  = output_mounting_hole_dia * 2
        else:
            bearing_mount_thickness = ((((Nr * module + 2 * h_b) - (bearing_OD + output_mounting_hole_dia * 4))/2) 
                                    + output_mounting_hole_dia * 2 + standard_clearance_1_5mm)        

        self.bearing_mounting_thickness_stg1 = bearing_mount_thickness

        stg1_stg2_mounting_PCD = (Nr2 * module2 + ring_radial_thickness * 2 + stg1_stg2_allen_socket_head_dia) / 2
        stg1_stg2_required_clearance = stg1_stg2_mounting_PCD + standard_clearance_1_5mm * 2 + (stg1_stg2_allen_socket_head_dia / 2)
        stg1_stg2_bearing_clearance  = (bearing_OD + bearing_mount_thickness * 2) / 2

        if(stg1_stg2_required_clearance > stg1_stg2_bearing_clearance):
            stg1_stg2_mounting_extra_width = stg1_stg2_required_clearance - stg1_stg2_bearing_clearance
        else:
            stg1_stg2_mounting_extra_width = 0

        bearing_holding_structure_OD     = bearing_OD + bearing_mount_thickness * 2 + stg1_stg2_mounting_extra_width * 2
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

        gearbox_casing_mass = (ring_volume + bearing_holding_structure_volume + case_mounting_structure_volume + large_fillet_volume) * density_3DP_material

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

        sun2_shaft_dia    = sun_shaft_bearing_ID
        sun2_shaft_height = sun_shaft_bearing_width + 2 * standard_clearance_1_5mm

        fw_s2_used        = planet2FwMM + clearance_planet + sec_carrier_thickness + standard_clearance_1_5mm

        sun2_gear_volume  = np.pi * ((Dia2SunMM * 0.5) ** 2) * fw_s2_used * 1e-9
        sun2_shaft_volume = np.pi * ((sun2_shaft_dia*0.5) ** 2) * sun2_shaft_height * 1e-9

        sun2_volume       = sun2_gear_volume + sun2_shaft_volume
        sun2_mass         = sun2_volume * density_3DP_material

        carrier_mass = carrier_volume * density_3DP_material

        carrier_stg1_mass = sun2_mass + carrier_mass

        #----------------------------------
        # Mass: dspg_sun
        #----------------------------------
        sun_hub_dia = motor_output_hole_PCD + motor_output_hole_dia + standard_clearance_1_5mm * 4

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
        bearing_retainer_OD        = bearing_holding_structure_OD
        bearing_retainer_ID        = bearing_OD - standard_clearance_1_5mm * 2


        bearing_retainer_volume = (np.pi * ((bearing_retainer_OD*0.5)**2 - (bearing_retainer_ID*0.5)**2) * bearing_retainer_thickness) * 1e-9

        bearing_retainer_mass   = bearing_retainer_volume * density_3DP_material

        self.Motor_case_mass_stg1              = Motor_case_mass
        self.gearbox_casing_mass_stg1          = gearbox_casing_mass
        self.carrier_mass_stg1                 = carrier_stg1_mass
        self.sun_mass_stg1                     = sun_mass
        self.sec_carrier_mass_stg1             = sec_carrier_mass
        self.planet_mass_stg1                  = planet_mass
        self.planet_bearing_combined_mass_stg1 = planet_bearing_combined_mass
        self.sun_shaft_bearing_mass_stg1       = sun_shaft_bearing_mass
        self.bearing_mass_stg1                 = bearing_mass
        self.bearing_retainer_mass_stg1        = bearing_retainer_mass

        #----------------------------------------
        # Total Actuator Mass
        #----------------------------------------
        Actuator_mass = (self.motorMassKG 
                        + self.Motor_case_mass_stg1 
                        + self.gearbox_casing_mass_stg1 
                        + self.carrier_mass_stg1 
                        + self.sun_mass_stg1 
                        + self.sec_carrier_mass_stg1 
                        + self.planet_mass_stg1 * numPlanet 
                        + self.planet_bearing_combined_mass_stg1 
                        + self.sun_shaft_bearing_mass_stg1 
                        + self.bearing_mass_stg1 
                        + self.bearing_retainer_mass_stg1)
        
        return Actuator_mass

    def getMassKG_3DP_stg2(self):
        module1    = self.doubleStagePlanetaryGearbox.Stage1.module
        Ns1        = self.doubleStagePlanetaryGearbox.Stage1.Ns
        Np1        = self.doubleStagePlanetaryGearbox.Stage1.Np
        Nr1        = self.doubleStagePlanetaryGearbox.Stage1.Nr
        numPlanet1 = self.doubleStagePlanetaryGearbox.Stage1.numPlanet
        module     = self.doubleStagePlanetaryGearbox.Stage2.module
        Ns         = self.doubleStagePlanetaryGearbox.Stage2.Ns
        Np         = self.doubleStagePlanetaryGearbox.Stage2.Np
        Nr         = self.doubleStagePlanetaryGearbox.Stage2.Nr
        numPlanet  = self.doubleStagePlanetaryGearbox.Stage2.numPlanet

        #------------------------------------
        # density of materials
        #------------------------------------
        density_3DP_material = self.doubleStagePlanetaryGearbox.densityGears

        #------------------------------------
        # Face Width
        #------------------------------------
        sun1FwMM     = self.doubleStagePlanetaryGearbox.Stage1.fwSunMM
        planet1FwMM  = self.doubleStagePlanetaryGearbox.Stage1.fwPlanetMM
        ring1FwMM    = self.doubleStagePlanetaryGearbox.Stage1.fwRingMM
        
        sunFwMM     = self.doubleStagePlanetaryGearbox.Stage2.fwSunMM
        planetFwMM  = self.doubleStagePlanetaryGearbox.Stage2.fwPlanetMM
        ringFwMM    = self.doubleStagePlanetaryGearbox.Stage2.fwRingMM

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
        base_plate_thickness            = self.base_plate_thickness        
        Motor_case_thickness            = self.Motor_case_thickness        
        clearance_planet                = self.clearance_planet            
        output_mounting_hole_dia        = self.output_mounting_hole_dia2    
        sec_carrier_thickness           = self.sec_carrier_thickness2       
        sun_shaft_bearing_OD            = self.sun_shaft_bearing_OD2        
        carrier_bearing_step_width      = self.carrier_bearing_step_width  
        planet_shaft_dia                = self.planet_shaft_dia2            
        sun_shaft_bearing_ID            = self.sun_shaft_bearing_ID2        
        sun_shaft_bearing_width         = self.sun_shaft_bearing_width2     
        planet_bore                     = self.planet_bore2                 
        bearing_retainer_thickness      = self.bearing_retainer_thickness2  
        stg1_stg2_allen_socket_head_dia = self.stg1_stg2_allen_socket_head_dia


        # To be written in Motor JSON files
        motor_output_hole_PCD = self.motor.motor_output_hole_PCD
        motor_output_hole_dia = self.motor.motor_output_hole_dia

        #--------------------------------------
        # Dependent variables
        #--------------------------------------
        h_b = 1.25 * module

        #--------------------------------------
        # Mass: dspg_gearbox_casing
        #--------------------------------------
        # Mass of the gearbox includes the mass of:
        # 1. Ring gear
        # 2. Bearing holding structure
        # 3. Case mounting structure
        #--------------------------------------
        ring_radial_thickness = self.ring_radial_thickness
        ring_ID               = Nr * module
        ring_OD               = Nr * module + ring_radial_thickness*2
        ringFwUsedMM          = ringFwMM + clearance_planet

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

        case_dist                  = (sec_carrier_thickness 
                                      + clearance_planet 
                                      + standard_clearance_1_5mm
                                      - bearing_retainer_thickness)
        case_mounting_structure_ID = ring_OD
        
        #IF( (("Nr" * "module" + "ring_radial_thickness" * 2 + "stg1_stg2_allen_socket_head_dia") / 2 + "standard_clearance_1_5mm" * 2 + "stg1_stg2_allen_socket_head_dia" / 2) > (("bearing1_OD" + "bearing mount thickness1" * 2) / 2), (("Nr" * "module" + "ring_radial_thickness" * 2 + "stg1_stg2_allen_socket_head_dia") / 2 + "standard_clearance_1_5mm" * 2 + "stg1_stg2_allen_socket_head_dia" / 2), (("bearing1_OD" + "bearing mount thickness1" * 2) / 2) )

        stg1_stg2_mounting_radius_gear_side = (((Nr * module) + (ring_radial_thickness * 2))/2 
                                               + stg1_stg2_allen_socket_head_dia 
                                               + standard_clearance_1_5mm * 2)
        
        stg1_stg2_mounting_radius_bearing_side = (self.Bearing_OD_stg1_MM + self.bearing_mounting_thickness_stg1* 2) / 2

        if (stg1_stg2_mounting_radius_gear_side > stg1_stg2_mounting_radius_bearing_side):
            case_mounting_structure_OD = stg1_stg2_mounting_radius_gear_side * 2
        else:
            case_mounting_structure_OD = stg1_stg2_mounting_radius_bearing_side * 2

        case_mounting_structure_height = case_dist

        ring_volume                      = np.pi * (((ring_OD*0.5)**2) - ((ring_ID)*0.5)**2) * ringFwUsedMM * 1e-9
        bearing_holding_structure_volume = np.pi * (((bearing_holding_structure_OD*0.5)**2) - 
                                                    ((bearing_holding_structure_ID*0.5)**2)) * bearing_holding_structure_height * 1e-9
        case_mounting_structure_volume   = np.pi * (((case_mounting_structure_OD*0.5)**2) - 
                                                    ((case_mounting_structure_ID*0.5)**2)) * case_mounting_structure_height * 1e-9
        
        large_fillet_ID     = ring_OD
        large_fillet_OD     = case_mounting_structure_OD
        large_fillet_height = ringFwMM
        large_fillet_volume = 0.5 * (np.pi * (((large_fillet_OD*0.5)**2) - ((large_fillet_ID)*0.5)**2) * large_fillet_height) * 1e-9

        gearbox_casing_mass = (ring_volume + bearing_holding_structure_volume + case_mounting_structure_volume + large_fillet_volume) * density_3DP_material

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
        bearing_retainer_OD = bearing_holding_structure_OD
        bearing_retainer_ID = bearing_OD - standard_clearance_1_5mm * 2

        bearing_retainer_volume = (np.pi * ((bearing_retainer_OD * 0.5)**2 - (bearing_retainer_ID * 0.5)**2) * bearing_retainer_thickness) * 1e-9

        bearing_retainer_mass   = bearing_retainer_volume * density_3DP_material

        self.gearbox_casing_mass_stg2          = gearbox_casing_mass
        self.carrier_mass_stg2                 = carrier_mass
        self.sec_carrier_mass_stg2             = sec_carrier_mass
        self.planet_mass_stg2                  = planet_mass
        self.planet_bearing_combined_mass_stg2 = planet_bearing_combined_mass
        self.sun_shaft_bearing_mass_stg2       = sun_shaft_bearing_mass
        self.bearing_mass_stg2                 = bearing_mass
        self.bearing_retainer_mass_stg2        = bearing_retainer_mass

        #----------------------------------------
        # Total Actuator Mass
        #----------------------------------------
        Actuator_mass = (self.gearbox_casing_mass_stg2 
                       + self.carrier_mass_stg2 
                       + self.sec_carrier_mass_stg2 
                       + self.planet_mass_stg2 * numPlanet 
                       + self.planet_bearing_combined_mass_stg2 
                       + self.sun_shaft_bearing_mass_stg2 
                       + self.bearing_mass_stg2 
                       + self.bearing_retainer_mass_stg2)
        
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
            # mass       = round(Actuator.getMassKG_3DP(), 3)
            mass       = round(Actuator.getMassKG_3DP(), 3)
            eff        = round(Actuator.planetaryGearbox.getEfficiency(), 3)
            
            # Update it is PSC are non-zero
            if self.UsePSCasVariable == 1 : 
                eff  = round(self.sspgOpt.getEfficiency(Var=False), 3)
            
            peakTorque = round(Actuator.motor.getMaxMotorTorque()*Actuator.planetaryGearbox.gearRatio(), 3)
            Cost       = self.cost(Actuator = Actuator) 
            Torque_Density = peakTorque / mass
            Outer_Bearing_mass = Actuator.bearing_mass
            Actuator_width = Actuator.actuator_width
            ## Don't delete the comment -- this is to verify if the Center distance and the PSC (should be all zero) are correct or not
            # print(iter,",", gearRatio,",",module,",", Ns,",", Np,",", Nr,",", numPlanet,",",  fwSunMM,",", fwPlanetMM,",", fwRingMM,",",Opt_PSC_sun,",", Opt_PSC_planet,",", Opt_PSC_ring,",", Opt_CD_SP, ",", Opt_CD_PR,",", mass,",", eff,",", peakTorque,",", Cost, ",", Torque_Density, ",", Outer_Bearing_mass, ",", Actuator_width)
            print(iter,",", gearRatio,",",module,",", Ns,",", Np,",", Nr,",", numPlanet,",",  fwSunMM,",", fwPlanetMM,",", fwRingMM,",", mass,",", eff,",", peakTorque,",", Cost, ",", Torque_Density, ",", Outer_Bearing_mass, ",", Actuator_width)

    def optimizeActuator(self, Actuator=singleStagePlanetaryActuator, UsePSCasVariable = 1, log = 0, csv = 1, gearRatioReq = 0, printOptParams = 1):
        self.UsePSCasVariable = UsePSCasVariable
        totalTime = 0
        self.gearRatioReq = gearRatioReq
        if UsePSCasVariable == 0:
            totalTime = self.optimizeActuatorWithoutPSC(Actuator=Actuator, log=log, csv=csv, printOptParams = printOptParams)
        elif UsePSCasVariable == 1:
            totalTime = self.optimizeActuatorWithPSC(Actuator=Actuator, log=log, csv=csv, printOptParams = printOptParams)
        else:
            totalTime = 0
            print("ERROR: \"UsePSCasVariable\" can be either 0 or 1")
        
        return totalTime

    def optimizeActuatorWithoutPSC(self, Actuator=singleStagePlanetaryActuator, log=1, csv=0, printOptParams = 1): 
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
                                        Actuator.planetaryGearbox.noPlanetInterferenceConstraint()):

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
                                                Actuator.genEquationFile(motor_name=Actuator.motor.motorName, gearRatioLL=round(self.gearRatioIter, 1), gearRatioUL = (round(self.gearRatioIter + self.GEAR_RATIO_STEP,1)))
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
                                                                                                   densityStructure          = Actuator.planetaryGearbox.densityStructure) # 2710 kg/m^3: Aluminum

                                                opt_actuator = singleStagePlanetaryActuator(design_params            = self.design_params,
                                                                                            motor                    = Actuator.motor, 
                                                                                            motor_driver_params      = Actuator.motor_driver_params,
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
            if(printOptParams):
                print("\n")
                print("Running Time (sec)")
                print(totalTime) 

        sys.stdout = sys.__stdout__
        return totalTime

    def optimizeActuatorWithPSC(self, Actuator=singleStagePlanetaryActuator, log=1, csv=0, printOptParams = 1):
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
                                                                                                       module                    = Actuator.planetaryGearbox.module,     # mm
                                                                                                       numPlanet                 = Actuator.planetaryGearbox.numPlanet,
                                                                                                       fwSunMM                   = Actuator.planetaryGearbox.fwSunMM,    # mm
                                                                                                       fwPlanetMM                = Actuator.planetaryGearbox.fwPlanetMM, # mm
                                                                                                       fwRingMM                  = Actuator.planetaryGearbox.fwRingMM,   # mm
                                                                                                       maxGearAllowableStressMPa = Actuator.planetaryGearbox.maxGearAllowableStressMPa, # 400 MPa
                                                                                                       densityGears              = Actuator.planetaryGearbox.densityGears,     # 7850 kg/m^3: Steel
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

    def cost(self, Actuator=singleStagePlanetaryActuator):
        K_gearRatio = 0
        if self.gearRatioReq != 0:
            K_gearRatio = 1
        
        gearRatio_err = np.sqrt((Actuator.planetaryGearbox.gearRatio() - self.gearRatioReq)**2)

        mass = Actuator.getMassKG_3DP()
        eff = Actuator.planetaryGearbox.getEfficiency()
        width = Actuator.planetaryGearbox.fwPlanetMM
        cost = (self.K_Mass    * mass 
                + self.K_Eff   * eff 
                + self.K_Width * width 
                + K_gearRatio  * gearRatio_err)
        return cost

#------------------------------------------------------------
# Class: Optimization of Compound Planetary Actuator
#------------------------------------------------------------
class optimizationCompoundPlanetaryActuator:
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
    
    def printOptimizationParameters(self, Actuator=compoundPlanetaryActuator, log=1, csv=0):
        # Motor Parameters
        maxMotorAngVelRPM       = Actuator.motor.maxMotorAngVelRPM
        maxMotorAngVelRadPerSec = Actuator.motor.maxMotorAngVelRadPerSec
        maxMotorTorque          = Actuator.motor.maxMotorTorque
        maxMotorPower           = Actuator.motor.maxMotorPower
        motorMass               = Actuator.motor.massKG
        motorDia                = Actuator.motor.motorDiaMM
        motorLength             = Actuator.motor.motorLengthMM
        
        # Planetary Gearbox Parameters
        maxGearAllowableStressMPa = Actuator.compoundPlanetaryGearbox.maxGearAllowableStressMPa
        
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
        
    def printOptimizationResults(self, Actuator=compoundPlanetaryActuator, log=1, csv=0):
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
            gearRatio       = Actuator.compoundPlanetaryGearbox.gearRatio()
            moduleBig       = Actuator.compoundPlanetaryGearbox.moduleBig
            moduleSmall     = Actuator.compoundPlanetaryGearbox.moduleSmall
            Ns              = Actuator.compoundPlanetaryGearbox.Ns 
            NpBig           = Actuator.compoundPlanetaryGearbox.NpBig
            NpSmall         = Actuator.compoundPlanetaryGearbox.NpSmall 
            Nr              = Actuator.compoundPlanetaryGearbox.Nr 
            numPlanet       = Actuator.compoundPlanetaryGearbox.numPlanet
            fwSunMM         = round(Actuator.compoundPlanetaryGearbox.fwSunMM    , 3)
            fwPlanetBigMM   = round(Actuator.compoundPlanetaryGearbox.fwPlanetBigMM , 3)
            fwPlanetSmallMM = round(Actuator.compoundPlanetaryGearbox.fwPlanetSmallMM , 3)
            fwRingMM        = round(Actuator.compoundPlanetaryGearbox.fwRingMM   , 3)
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
            eff             = round(Actuator.compoundPlanetaryGearbox.getEfficiency(), 3)
            peakTorque      = round(Actuator.motor.getMaxMotorTorque()*Actuator.compoundPlanetaryGearbox.gearRatio(), 3)
            
            tooth_forces    = Actuator.getToothForces()
            Torque_Density  = round(peakTorque/mass, 3)
            
            if self.UsePSCasVariable == 1 : 
                eff  = round(self.cspgOpt.getEfficiency(Var=False), 3)
            
            Cost = self.cost(Actuator=Actuator)
            Outer_Bearing_mass = Actuator.bearing_mass
            Actuator_width = Actuator.actuator_width
            print(iter, ",", gearRatio, ",", moduleBig, ",", moduleSmall, ",", Ns, ",", NpBig, ",", NpSmall, ",", Nr, ",", numPlanet, ",", fwSunMM, ",", fwPlanetBigMM, ",", fwPlanetSmallMM, ",", fwRingMM, ",", mass, ",", eff, ",", peakTorque, ",", Cost, ",", Torque_Density, ",", Outer_Bearing_mass, ",", Actuator_width)

    def optimizeActuator(self, Actuator=compoundPlanetaryActuator, UsePSCasVariable = 1, log=1, csv=0, printOptParams=1, gearRatioReq = 0):   
        self.UsePSCasVariable = UsePSCasVariable
        totalTime = 0
        self.gearRatioReq = gearRatioReq
        if UsePSCasVariable == 0:
            totalTime = self.optimizeActuatorWithoutPSC(Actuator=Actuator, log=log, csv=csv,printOptParams=printOptParams)
        elif UsePSCasVariable == 1:
            totalTime = self.optimizeActuatorWithPSC(Actuator=Actuator, log=log, csv=csv,printOptParams=printOptParams)
        else:
            totalTime = 0
            print("ERROR: \"UsePSCasVariable\" can be either 0 or 1")

        return totalTime
    
    def optimizeActuatorWithoutPSC(self, Actuator=compoundPlanetaryActuator, log=1, csv=0, printOptParams=1):
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
            fileName = f"./results/results_BruteForce_{Actuator.motor.motorName}/CPG_BRUTEFORCE_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}.csv"
        elif log:
            fileName = f"./results/results_BruteForce_{Actuator.motor.motorName}/CPG_BRUTEFORCE_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}_LOG.txt"
        
        with open(fileName, "w") as file1:
            sys.stdout = file1
            if (printOptParams):
                self.printOptimizationParameters(Actuator, log, csv)
                print(" ")

            if self.gearRatioReq != 0:
                self.GEAR_RATIO_MIN = self.gearRatioReq - self.GEAR_RATIO_STEP/2
                self.GEAR_RATIO_MAX = self.gearRatioReq + (self.GEAR_RATIO_STEP/2 - 1e-6)

            if log:
                print("*****************************************************************")
                print("FOR MINIMUM GEAR RATIO ", self.gearRatioIter)
                print("*****************************************************************")
                print(" ")
            elif csv:
                # Printing the optimization iterations below
                # print("iter, gearRatio, moduleBig, moduleSmall, Ns, NpBig, NpSmall, Nr, numPlanet, fwSunMM, fwPlanetBigMM, fwPanetSmallMM, fwRingMM, PSCs, PSCp1, PSCp2, PSCr, CD_SP, CD_PR, mass, eff, peakTorque, Cost, tooth_forces_sp, tooth_forces_rp, Torque_Density")
                # print("iter, gearRatio, moduleBig, moduleSmall, Ns, NpBig, NpSmall, Nr, numPlanet, fwSunMM, fwPlanetBigMM, fwPanetSmallMM, fwRingMM, mass, eff, peakTorque, Cost, tooth_forces_sp, tooth_forces_rp, Torque_Density")
                print("iter, gearRatio, moduleBig, moduleSmall, Ns, NpBig, NpSmall, Nr, numPlanet, fwSunMM, fwPlanetBigMM, fwPanetSmallMM, fwRingMM, mass, eff, peakTorque, Cost, Torque_Density, Outer_Bearing_mass, Actuator_width")

            while self.gearRatioIter <= self.GEAR_RATIO_MAX:
                opt_done  = 0
                self.iter = 0
                self.Cost = 100000
                MinCost   = self.Cost
                Actuator.compoundPlanetaryGearbox.setModuleBig(self.MODULE_BIG_MIN)
                while Actuator.compoundPlanetaryGearbox.moduleBig <= self.MODULE_BIG_MAX:
                    # Setting Module Small
                    Actuator.compoundPlanetaryGearbox.setModuleSmall(self.MODULE_SMALL_MIN)
                    while (Actuator.compoundPlanetaryGearbox.moduleSmall <= self.MODULE_SMALL_MAX):
                        # Setting Ns
                        Actuator.compoundPlanetaryGearbox.setNs(self.NUM_TEETH_SUN_MIN)
                        while (2*Actuator.compoundPlanetaryGearbox.getPCRadiusSunM()*1000) <= Actuator.maxGearboxDiameter:
                            # Setting Np Big
                            Actuator.compoundPlanetaryGearbox.setNpBig(self.NUM_TEETH_PLANET_BIG_MIN)
                            while (2*Actuator.compoundPlanetaryGearbox.getPCRadiusPlanetBigM()*1000) <= Actuator.maxGearboxDiameter/2:
                                # Setting Np Small
                                Actuator.compoundPlanetaryGearbox.setNpSmall(self.NUM_TEETH_PLANET_SMALL_MIN)
                                while (2*Actuator.compoundPlanetaryGearbox.getPCRadiusPlanetSmallM()*1000) <= Actuator.maxGearboxDiameter/2:
                                    # Setting Nr
                                    Actuator.compoundPlanetaryGearbox.setNr(Actuator.compoundPlanetaryGearbox.NpSmall + 
                                                                            Actuator.compoundPlanetaryGearbox.NpBig +
                                                                            Actuator.compoundPlanetaryGearbox.Ns)
                                    # if (2*Actuator.compoundPlanetaryGearbox.getPCRadiusRingM()*1000) <= Actuator.maxGearboxDiameter:
                                    if (Actuator.compoundPlanetaryGearbox.getGearboxOuterDiaMaxM()*1000) <= Actuator.maxGearboxDiameter:
                                        # Setting number of Planet
                                        Actuator.compoundPlanetaryGearbox.setNumPlanet(self.NUM_PLANET_MIN)
                                        while Actuator.compoundPlanetaryGearbox.numPlanet <= self.NUM_PLANET_MAX:
                                            if (Actuator.compoundPlanetaryGearbox.geometricConstraint() and 
                                                Actuator.compoundPlanetaryGearbox.meshingConstraint() and 
                                                Actuator.compoundPlanetaryGearbox.noPlanetInterferenceConstraint()):
                                                self.totalFeasibleGearboxes += 1
                                                # Fiter for the Gear Ratio
                                                if (Actuator.compoundPlanetaryGearbox.gearRatio() >= self.gearRatioIter and 
                                                    Actuator.compoundPlanetaryGearbox.gearRatio() <= (self.gearRatioIter + self.GEAR_RATIO_STEP)):
                                                    self.totalGearboxesWithReqGR += 1
                                                    Actuator.updateFacewidth()
                                                    
                                                    self.Cost = self.cost(Actuator=Actuator)

                                                    if self.Cost < MinCost:
                                                        MinCost    = self.Cost
                                                        opt_done   = 1
                                                        self.iter += 1
                                                        # Actuator.genEquationFile()
                                                        Actuator.genEquationFile(motor_name=Actuator.motor.motorName, gearRatioLL=round(self.gearRatioIter, 1), gearRatioUL = (round(self.gearRatioIter + self.GEAR_RATIO_STEP,1)))
                                                        opt_parameters = [Actuator.compoundPlanetaryGearbox.gearRatio(),
                                                                          Actuator.compoundPlanetaryGearbox.numPlanet,
                                                                          Actuator.compoundPlanetaryGearbox.Ns,
                                                                          Actuator.compoundPlanetaryGearbox.NpBig,
                                                                          Actuator.compoundPlanetaryGearbox.NpSmall,
                                                                          Actuator.compoundPlanetaryGearbox.Nr,
                                                                          Actuator.compoundPlanetaryGearbox.moduleBig,
                                                                          Actuator.compoundPlanetaryGearbox.moduleSmall]
                                                        opt_planetaryGearbox = compoundPlanetaryGearbox(design_parameters         = self.design_parameters,
                                                                                                        gear_standard_parameters  = self.gear_standard_parameters,
                                                                                                        Ns                        = Actuator.compoundPlanetaryGearbox.Ns,
                                                                                                        NpBig                     = Actuator.compoundPlanetaryGearbox.NpBig,
                                                                                                        NpSmall                   = Actuator.compoundPlanetaryGearbox.NpSmall, 
                                                                                                        Nr                        = Actuator.compoundPlanetaryGearbox.Nr,
                                                                                                        numPlanet                 = Actuator.compoundPlanetaryGearbox.numPlanet,
                                                                                                        moduleBig                 = Actuator.compoundPlanetaryGearbox.moduleBig, # mm
                                                                                                        moduleSmall               = Actuator.compoundPlanetaryGearbox.moduleSmall, # mm
                                                                                                        densityGears              = Actuator.compoundPlanetaryGearbox.densityGears,
                                                                                                        densityStructure          = Actuator.compoundPlanetaryGearbox.densityStructure,
                                                                                                        fwSunMM                   = Actuator.compoundPlanetaryGearbox.fwSunMM, # mm
                                                                                                        fwPlanetBigMM             = Actuator.compoundPlanetaryGearbox.fwPlanetBigMM, # mm
                                                                                                        fwPlanetSmallMM           = Actuator.compoundPlanetaryGearbox.fwPlanetSmallMM, # mm
                                                                                                        fwRingMM                  = Actuator.compoundPlanetaryGearbox.fwRingMM, # mm
                                                                                                        maxGearAllowableStressMPa = Actuator.compoundPlanetaryGearbox.maxGearAllowableStressMPa) # MPa) # kg/m^3
                                                        opt_actuator = compoundPlanetaryActuator(design_parameters        = self.design_parameters,
                                                                                                 motor                    = Actuator.motor,
                                                                                                 motor_driver_params      = Actuator.motor_driver_params,
                                                                                                 compoundPlanetaryGearbox = opt_planetaryGearbox,
                                                                                                 FOS                      = Actuator.FOS,
                                                                                                 serviceFactor            = Actuator.serviceFactor,
                                                                                                 maxGearboxDiameter       = Actuator.maxGearboxDiameter, # mm 
                                                                                                 stressAnalysisMethodName = "MIT") # Lewis or AGMA
                                                        opt_actuator.updateFacewidth()
                                                        opt_actuator.getMassKG_3DP()

                                                        # self.printOptimizationResults(Actuator, log, csv)
                                            Actuator.compoundPlanetaryGearbox.setNumPlanet(Actuator.compoundPlanetaryGearbox.numPlanet + 1)
                                        # Actuator.compoundPlanetaryGearbox.setNr(Actuator.compoundPlanetaryGearbox.Nr + 1)
                                    Actuator.compoundPlanetaryGearbox.setNpSmall(Actuator.compoundPlanetaryGearbox.NpSmall + 1)
                                Actuator.compoundPlanetaryGearbox.setNpBig(Actuator.compoundPlanetaryGearbox.NpBig + 1)
                            Actuator.compoundPlanetaryGearbox.setNs(Actuator.compoundPlanetaryGearbox.Ns + 1)
                        Actuator.compoundPlanetaryGearbox.setModuleSmall(Actuator.compoundPlanetaryGearbox.moduleSmall + 0.100)
                        Actuator.compoundPlanetaryGearbox.setModuleSmall(round(Actuator.compoundPlanetaryGearbox.moduleSmall, 1)) # Round Off
                    Actuator.compoundPlanetaryGearbox.setModuleBig(Actuator.compoundPlanetaryGearbox.moduleBig + 0.100)
                    Actuator.compoundPlanetaryGearbox.setModuleBig(round(Actuator.compoundPlanetaryGearbox.moduleBig, 1)) # Round Off
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

        return totalTime

    def optimizeActuatorWithPSC(self, Actuator=compoundPlanetaryActuator, log=1, csv=0):
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
            fileName = f"./results/results_bilevel_{Actuator.motor.motorName}/CPG_BILEVEL_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}.csv"
        elif log:
            fileName = f"./results/results_bilevel_{Actuator.motor.motorName}/CPG_BILEVEL_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}_LOG.txt"
        
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
                Actuator.compoundPlanetaryGearbox.setModuleBig(self.MODULE_BIG_MIN)
                while Actuator.compoundPlanetaryGearbox.moduleBig <= self.MODULE_BIG_MAX:
                    # Setting Module Small
                    Actuator.compoundPlanetaryGearbox.setModuleSmall(self.MODULE_SMALL_MIN)
                    while (Actuator.compoundPlanetaryGearbox.moduleSmall <= self.MODULE_SMALL_MAX):
                        # Setting Ns
                        Actuator.compoundPlanetaryGearbox.setNs(self.NUM_TEETH_SUN_MIN)
                        while (2*Actuator.compoundPlanetaryGearbox.getPCRadiusSunM()*1000) <= Actuator.maxGearboxDiameter:
                            # Setting Np Big
                            Actuator.compoundPlanetaryGearbox.setNpBig(self.NUM_TEETH_PLANET_BIG_MIN)
                            while (2*Actuator.compoundPlanetaryGearbox.getPCRadiusPlanetBigM()*1000) <= Actuator.maxGearboxDiameter/2:
                                # Setting Np Small
                                Actuator.compoundPlanetaryGearbox.setNpSmall(self.NUM_TEETH_PLANET_SMALL_MIN)
                                while (2*Actuator.compoundPlanetaryGearbox.getPCRadiusPlanetSmallM()*1000) <= Actuator.maxGearboxDiameter/2:
                                    # Setting Nr
                                    Actuator.compoundPlanetaryGearbox.setNr(Actuator.compoundPlanetaryGearbox.NpSmall + 
                                                                            Actuator.compoundPlanetaryGearbox.NpBig +
                                                                            Actuator.compoundPlanetaryGearbox.Ns)
                                    # if (2*Actuator.compoundPlanetaryGearbox.getPCRadiusRingM()*1000) <= Actuator.maxGearboxDiameter:
                                    if (Actuator.compoundPlanetaryGearbox.getGearboxOuterDiaMaxM()*1000) <= Actuator.maxGearboxDiameter:
                                        # Setting number of Planet
                                        Actuator.compoundPlanetaryGearbox.setNumPlanet(self.NUM_PLANET_MIN)
                                        while Actuator.compoundPlanetaryGearbox.numPlanet <= self.NUM_PLANET_MAX:
                                            if (Actuator.compoundPlanetaryGearbox.geometricConstraint() and 
                                                Actuator.compoundPlanetaryGearbox.meshingConstraint() and 
                                                Actuator.compoundPlanetaryGearbox.noPlanetInterferenceConstraint()):
                                                self.totalFeasibleGearboxes += 1
                                                # Fiter for the Gear Ratio
                                                if (Actuator.compoundPlanetaryGearbox.gearRatio() >= self.gearRatioIter and 
                                                    Actuator.compoundPlanetaryGearbox.gearRatio() <= (self.gearRatioIter + self.GEAR_RATIO_STEP)):
                                                    self.totalGearboxesWithReqGR += 1
                                                    Actuator.updateFacewidth()
                                                    
                                                    effActuator = Actuator.compoundPlanetaryGearbox.getEfficiency()
                                                    massActuator = Actuator.getMassKG_3DP()

                                                    self.Cost = (self.K_Mass * massActuator) + (self.K_Eff * effActuator)
                                                    if self.Cost < MinCost:
                                                        MinCost = self.Cost
                                                        opt_done = 1
                                                        self.iter += 1
                                                        Actuator.genEquationFile()
                                                        opt_parameters = [Actuator.compoundPlanetaryGearbox.gearRatio(),
                                                                          Actuator.compoundPlanetaryGearbox.numPlanet,
                                                                          Actuator.compoundPlanetaryGearbox.Ns,
                                                                          Actuator.compoundPlanetaryGearbox.NpBig,
                                                                          Actuator.compoundPlanetaryGearbox.NpSmall,
                                                                          Actuator.compoundPlanetaryGearbox.Nr,
                                                                          Actuator.compoundPlanetaryGearbox.moduleBig,
                                                                          Actuator.compoundPlanetaryGearbox.moduleSmall]
                                                        opt_planetaryGearbox = compoundPlanetaryGearbox(design_parameters         = self.design_parameters,
                                                                                                        gear_standard_parameters  = self.gear_standard_parameters,
                                                                                                        Ns                        = Actuator.compoundPlanetaryGearbox.Ns,
                                                                                                        NpBig                     = Actuator.compoundPlanetaryGearbox.NpBig,
                                                                                                        NpSmall                   = Actuator.compoundPlanetaryGearbox.NpSmall, 
                                                                                                        Nr                        = Actuator.compoundPlanetaryGearbox.Nr,
                                                                                                        numPlanet                 = Actuator.compoundPlanetaryGearbox.numPlanet,
                                                                                                        moduleBig                 = Actuator.compoundPlanetaryGearbox.moduleBig, # mm
                                                                                                        moduleSmall               = Actuator.compoundPlanetaryGearbox.moduleSmall, # mm
                                                                                                        densityGears              = Actuator.compoundPlanetaryGearbox.densityGears,
                                                                                                        densityStructure          = Actuator.compoundPlanetaryGearbox.densityStructure,
                                                                                                        fwSunMM                   = Actuator.compoundPlanetaryGearbox.fwSunMM, # mm
                                                                                                        fwPlanetBigMM             = Actuator.compoundPlanetaryGearbox.fwPlanetBigMM, # mm
                                                                                                        fwPlanetSmallMM           = Actuator.compoundPlanetaryGearbox.fwPlanetSmallMM, # mm
                                                                                                        fwRingMM                  = Actuator.compoundPlanetaryGearbox.fwRingMM, # mm
                                                                                                        maxGearAllowableStressMPa = Actuator.compoundPlanetaryGearbox.maxGearAllowableStressMPa) # MPa) # kg/m^3
                                                        opt_actuator = compoundPlanetaryActuator(design_parameters        = self.design_parameters,
                                                                                                 motor                    = Actuator.motor,
                                                                                                 compoundPlanetaryGearbox = opt_planetaryGearbox,
                                                                                                 FOS                      = Actuator.FOS,
                                                                                                 serviceFactor            = Actuator.serviceFactor,
                                                                                                 maxGearboxDiameter       = Actuator.maxGearboxDiameter, # mm 
                                                                                                 stressAnalysisMethodName = "Lewis") # Lewis or AGMA
                                            Actuator.compoundPlanetaryGearbox.setNumPlanet(Actuator.compoundPlanetaryGearbox.numPlanet + 1)
                                        # Actuator.compoundPlanetaryGearbox.setNr(Actuator.compoundPlanetaryGearbox.Nr + 1)
                                    Actuator.compoundPlanetaryGearbox.setNpSmall(Actuator.compoundPlanetaryGearbox.NpSmall + 1)
                                Actuator.compoundPlanetaryGearbox.setNpBig(Actuator.compoundPlanetaryGearbox.NpBig + 1)
                            Actuator.compoundPlanetaryGearbox.setNs(Actuator.compoundPlanetaryGearbox.Ns + 1)
                        Actuator.compoundPlanetaryGearbox.setModuleSmall(Actuator.compoundPlanetaryGearbox.moduleSmall + 0.100)
                        Actuator.compoundPlanetaryGearbox.setModuleSmall(round(Actuator.compoundPlanetaryGearbox.moduleSmall, 1)) # Round Off
                    Actuator.compoundPlanetaryGearbox.setModuleBig(Actuator.compoundPlanetaryGearbox.moduleBig + 0.100)
                    Actuator.compoundPlanetaryGearbox.setModuleBig(round(Actuator.compoundPlanetaryGearbox.moduleBig, 1)) # Round Off
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

    def cost(self, Actuator=compoundPlanetaryActuator):
        K_gearRatio = 0
        if self.gearRatioReq != 0:
            K_gearRatio = 1
        
        gearRatio_err = np.sqrt((Actuator.compoundPlanetaryGearbox.gearRatio() - self.gearRatioReq)**2)

        mass = Actuator.getMassKG_3DP()
        eff = Actuator.compoundPlanetaryGearbox.getEfficiency()
        width = Actuator.compoundPlanetaryGearbox.fwPlanetBigMM + Actuator.compoundPlanetaryGearbox.fwPlanetSmallMM
        cost = (self.K_Mass    * mass 
                + self.K_Eff   * eff 
                + self.K_Width * width 
                + K_gearRatio  * gearRatio_err)
        return cost

#------------------------------------------------------------
# Class: Optimization of Wolfrom Planetary Actuator
#------------------------------------------------------------
class optimizationWolfromPlanetaryActuator:
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

    def optimizeActuator(self, Actuator = wolfromPlanetaryActuator, UsePSCasVariable = 1, log = 0, csv = 1, printOptParams=1, gearRatioReq = 0):
        startTime = time.time()
        self.UsePSCasVariable = UsePSCasVariable
        self.gearRatioReq = gearRatioReq
        if UsePSCasVariable == 0:
            self.optimizeActuatorWithoutPSC(Actuator=Actuator, log=log, csv=csv, printOptParams = printOptParams)
        elif UsePSCasVariable == 1:
            self.optimizeActuatorWithPSC(Actuator=Actuator, log=log, csv=csv, printOptParams=printOptParams)
        else:
            print("ERROR: \"UsePSCasVariable\" can be either 0 or 1")
        
        # Print the time in the file 
        endTime = time.time()
        totalTime = endTime - startTime
        # print("\n")
        # print("Running Time (sec)")
        # print(totalTime) 

        return (totalTime)

    def optimizeActuatorWithoutPSC(self, Actuator = wolfromPlanetaryActuator, log=1, csv=0, printOptParams = 1):
        opt_parameters = []
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
            fileName = f"./results/results_BruteForce_{Actuator.motor.motorName}/WPG_BRUTEFORCE_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}.csv"
        elif log:
            fileName = f"./results/results_BruteForce_{Actuator.motor.motorName}/WPG_BRUTEFORCE_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}_LOG.txt"
            
        with open(fileName, "w") as wolfromLogFile:
            sys.stdout = wolfromLogFile
            if (printOptParams):
                self.printOptimizationParameters(Actuator, log, csv)
                print(" ")
            
            if self.gearRatioReq != 0:
                self.GEAR_RATIO_MIN = self.gearRatioReq - self.GEAR_RATIO_STEP/2
                self.GEAR_RATIO_MAX = self.gearRatioReq + (self.GEAR_RATIO_STEP/2 - 1e-6)

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

                Actuator.wolfromPlanetaryGearbox.setModuleBig(self.MODULE_BIG_MIN)
                while Actuator.wolfromPlanetaryGearbox.moduleBig <= self.MODULE_BIG_MAX:
                    # Setting Module Small
                    Actuator.wolfromPlanetaryGearbox.setModuleSmall(self.MODULE_SMALL_MIN)
                    while (Actuator.wolfromPlanetaryGearbox.moduleSmall <= self.MODULE_SMALL_MAX):
                        # Setting Ns
                        Actuator.wolfromPlanetaryGearbox.setNs(self.NUM_TEETH_SUN_MIN)
                        while (2*Actuator.wolfromPlanetaryGearbox.getPCRadiusSunM()*1000) <= Actuator.maxGearboxDiameter:
                            # Setting Np Big
                            Actuator.wolfromPlanetaryGearbox.setNpBig(self.NUM_TEETH_PLANET_BIG_MIN)
                            while (2*Actuator.wolfromPlanetaryGearbox.getPCRadiusPlanetBigM()*1000) <= Actuator.maxGearboxDiameter/2:
                                # Setting Np Small
                                Actuator.wolfromPlanetaryGearbox.setNpSmall(self.NUM_TEETH_PLANET_SMALL_MIN)
                                while (2*Actuator.wolfromPlanetaryGearbox.getPCRadiusPlanetSmallM()*1000) <= Actuator.maxGearboxDiameter/2:
                                    # Setting Nr Small
                                    Actuator.wolfromPlanetaryGearbox.setNrSmall(Actuator.wolfromPlanetaryGearbox.NpSmall + 
                                                                                Actuator.wolfromPlanetaryGearbox.NpBig +
                                                                                Actuator.wolfromPlanetaryGearbox.Ns)
                                    # Setting Nr Big
                                    Actuator.wolfromPlanetaryGearbox.setNrBig(2*Actuator.wolfromPlanetaryGearbox.NpBig +
                                                                                Actuator.wolfromPlanetaryGearbox.Ns)
                                    if ((2*Actuator.wolfromPlanetaryGearbox.getPCRadiusRingBigM()*1000) <= Actuator.maxGearboxDiameter):# and Actuator.getIdRequired2MM() <= 100): # and ((2*Actuator.wolfromPlanetaryGearbox.getPCRadiusRingSmallM()*1000) <= maxGearBoxDia):
                                        # TODO: Ask Deepak: What is getIDRequired2MM()? and also tell him to write a more meaningful function name
                                        # Setting number of Planet
                                        Actuator.wolfromPlanetaryGearbox.setNumPlanet(self.NUM_PLANET_MIN)
                                        while Actuator.wolfromPlanetaryGearbox.numPlanet <= self.NUM_PLANET_MAX:
                                            if (Actuator.wolfromPlanetaryGearbox.geometricConstraint() and 
                                                Actuator.wolfromPlanetaryGearbox.meshingConstraint() and 
                                                Actuator.wolfromPlanetaryGearbox.noPlanetInterferenceConstraint()):
                                                self.totalFeasibleGearboxes += 1
                                                # Fiter for the Gear Ratio
                                                if (Actuator.wolfromPlanetaryGearbox.gearRatio() >= self.gearRatioIter and 
                                                    Actuator.wolfromPlanetaryGearbox.gearRatio() <= (self.gearRatioIter + 1)):
                                                    self.totalGearboxesWithReqGR += 1
                                                    
                                                    # Cost Calculation
                                                    Actuator.updateFacewidth()

                                                    self.Cost = self.cost(Actuator=Actuator)
                                                    if self.Cost < MinCost:
                                                        MinCost = self.Cost
                                                        self.iter += 1
                                                        opt_done = 1
                                                        # Actuator.genEquationFile()
                                                        Actuator.genEquationFile(motor_name=Actuator.motor.motorName, gearRatioLL=round(self.gearRatioIter, 1), gearRatioUL = (round(self.gearRatioIter + self.GEAR_RATIO_STEP,1)))

                                                        opt_parameters = [Actuator.wolfromPlanetaryGearbox.gearRatio(),
                                                                          Actuator.wolfromPlanetaryGearbox.numPlanet,
                                                                          Actuator.wolfromPlanetaryGearbox.Ns,
                                                                          Actuator.wolfromPlanetaryGearbox.NpBig,
                                                                          Actuator.wolfromPlanetaryGearbox.NrBig,
                                                                          Actuator.wolfromPlanetaryGearbox.NpSmall,
                                                                          Actuator.wolfromPlanetaryGearbox.NrSmall,
                                                                          Actuator.wolfromPlanetaryGearbox.moduleBig,
                                                                          Actuator.wolfromPlanetaryGearbox.moduleSmall]
                                                        opt_planetaryGearbox = wolfromPlanetaryGearbox  (design_parameters         = self.design_parameters,
                                                                                                         gear_standard_parameters  = self.gear_standard_parameters,
                                                                                                         Ns                        = Actuator.wolfromPlanetaryGearbox.Ns,
                                                                                                         NpBig                     = Actuator.wolfromPlanetaryGearbox.NpBig,
                                                                                                         NpSmall                   = Actuator.wolfromPlanetaryGearbox.NpSmall,
                                                                                                         NrBig                     = Actuator.wolfromPlanetaryGearbox.NrBig,
                                                                                                         NrSmall                   = Actuator.wolfromPlanetaryGearbox.NrSmall,
                                                                                                         numPlanet                 = Actuator.wolfromPlanetaryGearbox.numPlanet,
                                                                                                         moduleBig                 = Actuator.wolfromPlanetaryGearbox.moduleBig,
                                                                                                         moduleSmall               = Actuator.wolfromPlanetaryGearbox.moduleSmall,
                                                                                                         densityGears              = Actuator.wolfromPlanetaryGearbox.densityGears,
                                                                                                         densityStructure          = Actuator.wolfromPlanetaryGearbox.densityStructure,
                                                                                                         fwSunMM                   = Actuator.wolfromPlanetaryGearbox.fwSunMM,
                                                                                                         fwPlanetBigMM             = Actuator.wolfromPlanetaryGearbox.fwPlanetBigMM,
                                                                                                         fwPlanetSmallMM           = Actuator.wolfromPlanetaryGearbox.fwPlanetSmallMM,
                                                                                                         fwRingBigMM               = Actuator.wolfromPlanetaryGearbox.fwRingBigMM,
                                                                                                         fwRingSmallMM             = Actuator.wolfromPlanetaryGearbox.fwRingSmallMM,
                                                                                                         maxGearAllowableStressMPa = Actuator.wolfromPlanetaryGearbox.maxGearAllowableStressMPa)
                                                        opt_actuator = wolfromPlanetaryActuator(design_parameters        = self.design_parameters,
                                                                                                motor                    = Actuator.motor, 
                                                                                                motor_driver_params      = Actuator.motor_driver_params,
                                                                                                wolfromPlanetaryGearbox  = opt_planetaryGearbox, 
                                                                                                FOS                      = Actuator.FOS, 
                                                                                                serviceFactor            = Actuator.serviceFactor, 
                                                                                                maxGearboxDiameter       = Actuator.maxGearboxDiameter, # mm 
                                                                                                stressAnalysisMethodName = "MIT") # Lewis or AGMA
                                                        
                                                        opt_actuator.updateFacewidth()
                                                        opt_actuator.getMassKG_3DP()
                                            
                                                        # self.printOptimizationResults(Actuator, log, csv)
                                            Actuator.wolfromPlanetaryGearbox.setNumPlanet(Actuator.wolfromPlanetaryGearbox.numPlanet + 1)
                                        # Actuator.wolfromPlanetaryGearbox.setNrBig(Actuator.wolfromPlanetaryGearbox.NrBig + 1)
                                        # Actuator.wolfromPlanetaryGearbox.setNrSmall(Actuator.wolfromPlanetaryGearbox.NrSmall + 1)
                                    Actuator.wolfromPlanetaryGearbox.setNpSmall(Actuator.wolfromPlanetaryGearbox.NpSmall + 1)
                                Actuator.wolfromPlanetaryGearbox.setNpBig(Actuator.wolfromPlanetaryGearbox.NpBig + 1)
                            Actuator.wolfromPlanetaryGearbox.setNs(Actuator.wolfromPlanetaryGearbox.Ns + 1)
                        Actuator.wolfromPlanetaryGearbox.setModuleSmall(Actuator.wolfromPlanetaryGearbox.moduleSmall + 0.100)
                        Actuator.wolfromPlanetaryGearbox.setModuleSmall(round(Actuator.wolfromPlanetaryGearbox.moduleSmall, 1)) # Round Off
                    Actuator.wolfromPlanetaryGearbox.setModuleBig(Actuator.wolfromPlanetaryGearbox.moduleBig + 0.100)
                    Actuator.wolfromPlanetaryGearbox.setModuleBig(round(Actuator.wolfromPlanetaryGearbox.moduleBig, 1)) # Round Off
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

    def optimizeActuatorWithPSC(self, Actuator = wolfromPlanetaryActuator, log=1, csv=0, printOptParams = 1):
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
                Actuator.wolfromPlanetaryGearbox.setModuleBig(self.MODULE_BIG_MIN)
                while Actuator.wolfromPlanetaryGearbox.moduleBig <= self.MODULE_BIG_MAX:
                    # Setting Module Small
                    Actuator.wolfromPlanetaryGearbox.setModuleSmall(self.MODULE_SMALL_MIN)
                    while (Actuator.wolfromPlanetaryGearbox.moduleSmall <= self.MODULE_SMALL_MAX):
                        # Setting Ns
                        Actuator.wolfromPlanetaryGearbox.setNs(self.NUM_TEETH_SUN_MIN)
                        while (2*Actuator.wolfromPlanetaryGearbox.getPCRadiusSunM()*1000) <= Actuator.maxGearboxDiameter:
                            # Setting Np Big
                            Actuator.wolfromPlanetaryGearbox.setNpBig(self.NUM_TEETH_PLANET_BIG_MIN)
                            while (2*Actuator.wolfromPlanetaryGearbox.getPCRadiusPlanetBigM()*1000) <= Actuator.maxGearboxDiameter/2:
                                # Setting Np Small
                                Actuator.wolfromPlanetaryGearbox.setNpSmall(self.NUM_TEETH_PLANET_SMALL_MIN)
                                while (2*Actuator.wolfromPlanetaryGearbox.getPCRadiusPlanetSmallM()*1000) <= Actuator.maxGearboxDiameter/2:
                                    # Setting Nr Small
                                    Actuator.wolfromPlanetaryGearbox.setNrSmall(Actuator.wolfromPlanetaryGearbox.NpSmall + 
                                                                                Actuator.wolfromPlanetaryGearbox.NpBig +
                                                                                Actuator.wolfromPlanetaryGearbox.Ns)
                                    # Setting Nr Big
                                    Actuator.wolfromPlanetaryGearbox.setNrBig(2*Actuator.wolfromPlanetaryGearbox.NpBig +
                                                                                Actuator.wolfromPlanetaryGearbox.Ns)
                                    if ((2*Actuator.wolfromPlanetaryGearbox.getPCRadiusRingBigM()*1000) <= Actuator.maxGearboxDiameter and Actuator.getIdRequired2MM() <= 100): # and ((2*Actuator.wolfromPlanetaryGearbox.getPCRadiusRingSmallM()*1000) <= maxGearBoxDia):
                                        # TODO: Ask Deepak: What is getIDRequired2MM()? and also tell him to write a more meaningful function name
                                        # Setting number of Planet
                                        Actuator.wolfromPlanetaryGearbox.setNumPlanet(self.NUM_PLANET_MIN)
                                        while Actuator.wolfromPlanetaryGearbox.numPlanet <= self.NUM_PLANET_MAX:
                                            if (Actuator.wolfromPlanetaryGearbox.geometricConstraint() and 
                                                Actuator.wolfromPlanetaryGearbox.meshingConstraint() and 
                                                Actuator.wolfromPlanetaryGearbox.noPlanetInterferenceConstraint()):
                                                self.totalFeasibleGearboxes += 1
                                                # Fiter for the Gear Ratio
                                                if (Actuator.wolfromPlanetaryGearbox.gearRatio() >= self.gearRatioIter and 
                                                    Actuator.wolfromPlanetaryGearbox.gearRatio() <= (self.gearRatioIter + 1)):
                                                    
                                                    self.totalGearboxesWithReqGR += 1
                                                    
                                                    # Cost Calculation
                                                    Actuator.updateFacewidth()
                                                    # massActuator = Actuator.getMassStructureKG()
                                                    massActuator = Actuator.getMassKG_3DP()
                                                    effActuator = Actuator.wolfromPlanetaryGearbox.getEfficiency()
                                                    self.Cost = (self.K_Mass * massActuator) + (self.K_Eff * effActuator)
                                                    
                                                    if self.Cost < MinCost:
                                                        MinCost = self.Cost
                                                        self.iter += 1
                                                        opt_done = 1
                                                        Actuator.genEquationFile()

                                                        opt_parameters = [Actuator.wolfromPlanetaryGearbox.gearRatio(),
                                                                          Actuator.wolfromPlanetaryGearbox.numPlanet,
                                                                          Actuator.wolfromPlanetaryGearbox.Ns,
                                                                          Actuator.wolfromPlanetaryGearbox.NpBig,
                                                                          Actuator.wolfromPlanetaryGearbox.NrBig,
                                                                          Actuator.wolfromPlanetaryGearbox.NpSmall,
                                                                          Actuator.wolfromPlanetaryGearbox.NrSmall,
                                                                          Actuator.wolfromPlanetaryGearbox.moduleBig,
                                                                          Actuator.wolfromPlanetaryGearbox.moduleSmall]
                                                        opt_planetaryGearbox = wolfromPlanetaryGearbox  (design_parameters         = self.design_parameters,
                                                                                                         gear_standard_parameters  = self.gear_standard_parameters,
                                                                                                         Ns                        = Actuator.wolfromPlanetaryGearbox.Ns,
                                                                                                         NpBig                     = Actuator.wolfromPlanetaryGearbox.NpBig,
                                                                                                         NpSmall                   = Actuator.wolfromPlanetaryGearbox.NpSmall,
                                                                                                         NrBig                     = Actuator.wolfromPlanetaryGearbox.NrBig,
                                                                                                         NrSmall                   = Actuator.wolfromPlanetaryGearbox.NrSmall,
                                                                                                         numPlanet                 = Actuator.wolfromPlanetaryGearbox.numPlanet,
                                                                                                         moduleBig                 = Actuator.wolfromPlanetaryGearbox.moduleBig,
                                                                                                         moduleSmall               = Actuator.wolfromPlanetaryGearbox.moduleSmall,
                                                                                                         densityGears              = Actuator.wolfromPlanetaryGearbox.densityGears,
                                                                                                         densityStructure          = Actuator.wolfromPlanetaryGearbox.densityStructure,
                                                                                                         fwSunMM                   = Actuator.wolfromPlanetaryGearbox.fwSunMM,
                                                                                                         fwPlanetBigMM             = Actuator.wolfromPlanetaryGearbox.fwPlanetBigMM,
                                                                                                         fwPlanetSmallMM           = Actuator.wolfromPlanetaryGearbox.fwPlanetSmallMM,
                                                                                                         fwRingBigMM               = Actuator.wolfromPlanetaryGearbox.fwRingBigMM,
                                                                                                         fwRingSmallMM             = Actuator.wolfromPlanetaryGearbox.fwRingSmallMM,
                                                                                                         maxGearAllowableStressMPa = Actuator.wolfromPlanetaryGearbox.maxGearAllowableStressMPa)
                                                        opt_actuator = wolfromPlanetaryActuator(design_parameters        = self.design_parameters,
                                                                                                motor                    = Actuator.motor, 
                                                                                                wolfromPlanetaryGearbox  = opt_planetaryGearbox, 
                                                                                                FOS                      = Actuator.FOS, 
                                                                                                serviceFactor            = Actuator.serviceFactor, 
                                                                                                maxGearboxDiameter       = Actuator.maxGearboxDiameter, # mm 
                                                                                                stressAnalysisMethodName = "Lewis") # Lewis or AGMA
                                            
                                            Actuator.wolfromPlanetaryGearbox.setNumPlanet(Actuator.wolfromPlanetaryGearbox.numPlanet + 1)
                                        # Actuator.wolfromPlanetaryGearbox.setNrBig(Actuator.wolfromPlanetaryGearbox.NrBig + 1)
                                        # Actuator.wolfromPlanetaryGearbox.setNrSmall(Actuator.wolfromPlanetaryGearbox.NrSmall + 1)
                                    Actuator.wolfromPlanetaryGearbox.setNpSmall(Actuator.wolfromPlanetaryGearbox.NpSmall + 1)
                                Actuator.wolfromPlanetaryGearbox.setNpBig(Actuator.wolfromPlanetaryGearbox.NpBig + 1)
                            Actuator.wolfromPlanetaryGearbox.setNs(Actuator.wolfromPlanetaryGearbox.Ns + 1)
                        Actuator.wolfromPlanetaryGearbox.setModuleSmall(Actuator.wolfromPlanetaryGearbox.moduleSmall + 0.100)
                        Actuator.wolfromPlanetaryGearbox.setModuleSmall(round(Actuator.wolfromPlanetaryGearbox.moduleSmall, 1)) # Round Off
                    Actuator.wolfromPlanetaryGearbox.setModuleBig(Actuator.wolfromPlanetaryGearbox.moduleBig + 0.100)
                    Actuator.wolfromPlanetaryGearbox.setModuleBig(round(Actuator.wolfromPlanetaryGearbox.moduleBig, 1)) # Round Off
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

    def printOptimizationParameters(self, Actuator = wolfromPlanetaryActuator, log=1, csv=0):
        # Motor Parameters
        maxMotorAngVelRPM       = Actuator.motor.maxMotorAngVelRPM
        maxMotorAngVelRadPerSec = Actuator.motor.maxMotorAngVelRadPerSec
        maxMotorTorque          = Actuator.motor.maxMotorTorque
        maxMotorPower           = Actuator.motor.maxMotorPower
        motorMass               = Actuator.motor.massKG
        motorDia                = Actuator.motor.motorDiaMM
        motorLength             = Actuator.motor.motorLengthMM
        
        # Planetary Gearbox Parameters
        maxGearAllowableStressMPa = Actuator.wolfromPlanetaryGearbox.maxGearAllowableStressMPa
        
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

    def printOptimizationResults(self, Actuator = wolfromPlanetaryActuator, log=1, csv=0):
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
            gearRatio       = Actuator.wolfromPlanetaryGearbox.gearRatio()
            moduleBig       = Actuator.wolfromPlanetaryGearbox.moduleBig
            moduleSmall     = Actuator.wolfromPlanetaryGearbox.moduleSmall
            Ns              = Actuator.wolfromPlanetaryGearbox.Ns 
            NpBig           = Actuator.wolfromPlanetaryGearbox.NpBig
            NpSmall         = Actuator.wolfromPlanetaryGearbox.NpSmall 
            NrBig           = Actuator.wolfromPlanetaryGearbox.NrBig
            NrSmall         = Actuator.wolfromPlanetaryGearbox.NrSmall 
            numPlanet       = Actuator.wolfromPlanetaryGearbox.numPlanet
            fwSunMM         = round(Actuator.wolfromPlanetaryGearbox.fwSunMM    , 3)
            fwPlanetBigMM   = round(Actuator.wolfromPlanetaryGearbox.fwPlanetBigMM , 3)
            fwPlanetSmallMM = round(Actuator.wolfromPlanetaryGearbox.fwPlanetSmallMM , 3)
            fwRingBigMM     = round(Actuator.wolfromPlanetaryGearbox.fwRingBigMM   , 3)
            fwRingSmallMM   = round(Actuator.wolfromPlanetaryGearbox.fwRingSmallMM   , 3)
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
            eff        = round(Actuator.wolfromPlanetaryGearbox.getEfficiency(), 3)
            if self.UsePSCasVariable == 1 :
                eff  = round(self.wpgOpt.getEfficiency(Var=False), 3)
            peakTorque      = round(Actuator.motor.getMaxMotorTorque()*Actuator.wolfromPlanetaryGearbox.gearRatio(), 3)
            Cost       = Actuator.cost() #self.K_Mass * mass + self.K_Eff * eff
            torque_density  = round(peakTorque/mass, 3)
            Outer_bearing_mass = Actuator.bearing_mass
            Actuator_width = Actuator.actuator_width
            print(iter,",", gearRatio,",",moduleBig,",",moduleSmall,",", Ns,",", NpBig,",", NpSmall,",", NrBig,",",NrSmall,",", numPlanet,",", Opt_PSC_sun,",",  Opt_PSC_planet1,",", Opt_PSC_planet2,",", Opt_PSC_ring1,",",Opt_PSC_ring2,",", fwSunMM,",", fwPlanetBigMM,",",fwPlanetSmallMM,",", fwRingBigMM,",",fwRingSmallMM,",", mass, ",", eff,",", peakTorque,",", Cost, ",", torque_density, ",", Outer_bearing_mass, ",", Actuator_width)

    def cost(self, Actuator=wolfromPlanetaryActuator):
        K_gearRatio = 0
        if self.gearRatioReq != 0:
            K_gearRatio = 1
        
        gearRatio_err = np.sqrt((Actuator.wolfromPlanetaryGearbox.gearRatio() - self.gearRatioReq)**2)

        mass = Actuator.getMassKG_3DP()
        eff = Actuator.wolfromPlanetaryGearbox.getEfficiency()
        width = Actuator.wolfromPlanetaryGearbox.fwPlanetBigMM + Actuator.wolfromPlanetaryGearbox.fwPlanetSmallMM
        cost = (self.K_Mass    * mass 
                + self.K_Eff   * eff 
                + self.K_Width * width 
                + K_gearRatio  * gearRatio_err)
        return cost

#------------------------------------------------------------
# Class: Optimization of Double Stage Planetary Actuator
#------------------------------------------------------------
class optimizationDoubleStagePlanetaryActuator:
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

    def optimizeActuator(self, Actuator=doubleStagePlanetaryActuator, UsePSCasVariable=1, log=1, csv=0, gearRatioReq = 0, printOptParams = 1):
        self.UsePSCasVariable = UsePSCasVariable
        totalTime = 0
        self.gearRatioReq = gearRatioReq
        if UsePSCasVariable == 0:
            totalTime = self.optimizeActuatorWithoutPSC(Actuator=Actuator, log=log, csv=csv, printOptParams=printOptParams)
        elif UsePSCasVariable == 1:
            totalTime = self.optimizeActuatorWithPSC(Actuator=Actuator, log=log, csv=csv, printOptParams=printOptParams)
        else:
            totalTime = 0
            print("ERROR: \"UsePSCasVariable\" can be either 0 or 1")

        return totalTime
    
    def optimizeActuatorWithoutPSC(self, Actuator=doubleStagePlanetaryActuator, log=1, csv=0, printOptParams = 1):
        startTime = time.time()
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
            fileName = f"./results/results_BruteForce_{Actuator.motor.motorName}/DSPG_BRUTEFORCE_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}.csv"
        elif log:
            fileName = f"./results/results_BruteForce_{Actuator.motor.motorName}/DSPG_BRUTEFORCE_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}_LOG.txt"
        
        with open(fileName, "w") as DSPGLogFile:
            sys.stdout = DSPGLogFile
            if(printOptParams):
                self.printOptimizationParameters(Actuator, log, csv)
                print(" ")
            
            if log:
                print("*****************************************************************")
                print("FOR MINIMUM GEAR RATIO ", self.gearRatioIter)
                print("*****************************************************************")
                print(" ")
            elif csv:
                # Printing the optimization iterations below
                # print("iter, gearRatio, module1, module2, Ns1, Np1, Nr1, numPlanet1, Ns2, Np2, Nr2, numPlanet2, fwSun1MM, fwPlanet1MM, fwRing1MM, fwSun2MM, fwPlanet2MM, fwRing2MM, Opt_PSC_sun1,  Opt_PSC_planet1, Opt_PSC_ring1, Opt_PSC_sun2, Opt_PSC_planet2, Opt_PSC_ring2, Opt_CD_SP1, Opt_CD_PR1, Opt_CD_SP2, Opt_CD_PR2, mass, eff, peakTorque, Cost, Torque_Density")
                print("iter, gearRatio, module1, module2, Ns1, Np1, Nr1, numPlanet1, Ns2, Np2, Nr2, numPlanet2, fwSun1MM, fwPlanet1MM, fwRing1MM, fwSun2MM, fwPlanet2MM, fwRing2MM, mass, eff, peakTorque, Cost, Torque_Density, ")

            while self.gearRatioIter <= self.GEAR_RATIO_MAX:
                opt_done  = 0
                self.iter = 0
                self.Cost = 100000
                MinCost   = self.Cost

                Actuator.doubleStagePlanetaryGearbox.Stage1.setModule(self.MODULE_STAGE1_MIN)
                while Actuator.doubleStagePlanetaryGearbox.Stage1.module <= self.MODULE_STAGE1_MAX:
                    Actuator.doubleStagePlanetaryGearbox.Stage2.setModule(self.MODULE_STAGE2_MIN)
                    while Actuator.doubleStagePlanetaryGearbox.Stage2.module <= self.MODULE_STAGE2_MAX:
                        # Setting Ns
                        Actuator.doubleStagePlanetaryGearbox.Stage1.setNs(self.NUM_TEETH_SUN_MIN)
                        while 2*Actuator.doubleStagePlanetaryGearbox.Stage1.getPCRadiusSunMM() <= Actuator.maxGearboxDiameter:
                            # Setting Np
                            Actuator.doubleStagePlanetaryGearbox.Stage1.setNp(self.NUM_TEETH_PLANET_MIN)
                            while 2*Actuator.doubleStagePlanetaryGearbox.Stage1.getPCRadiusPlanetMM() <= Actuator.maxGearboxDiameter/2:
                                # Setting Nr
                                Actuator.doubleStagePlanetaryGearbox.Stage1.setNr(2*Actuator.doubleStagePlanetaryGearbox.Stage1.Np + 
                                                                                Actuator.doubleStagePlanetaryGearbox.Stage1.Ns)
                                if 2*Actuator.doubleStagePlanetaryGearbox.Stage1.getPCRadiusRingMM() <= Actuator.maxGearboxDiameter:
                                # while 2*Actuator.doubleStagePlanetaryGearbox.Stage1.getPCRadiusRingMM() <= maxGearBoxDia:
                                    # Setting number of Planet
                                    Actuator.doubleStagePlanetaryGearbox.Stage1.setNumPlanet(self.NUM_PLANET_STAGE1_MIN)
                                    while Actuator.doubleStagePlanetaryGearbox.Stage1.numPlanet <= self.NUM_PLANET_STAGE1_MAX:
                                        # # Setting Nr
                                        Actuator.doubleStagePlanetaryGearbox.Stage2.setNs(self.NUM_TEETH_SUN_MIN)
                                        while 2*Actuator.doubleStagePlanetaryGearbox.Stage2.getPCRadiusSunMM() <= Actuator.maxGearboxDiameter:
                                            # Setting Np
                                            Actuator.doubleStagePlanetaryGearbox.Stage2.setNp(self.NUM_TEETH_PLANET_MIN)
                                            while 2*Actuator.doubleStagePlanetaryGearbox.Stage2.getPCRadiusPlanetMM() <= Actuator.maxGearboxDiameter/2:
                                                # Setting Ns
                                                Actuator.doubleStagePlanetaryGearbox.Stage2.setNr(2*Actuator.doubleStagePlanetaryGearbox.Stage2.Np + 
                                                                                                Actuator.doubleStagePlanetaryGearbox.Stage2.Ns)
                                                if 2*Actuator.doubleStagePlanetaryGearbox.Stage2.getPCRadiusRingMM() <= Actuator.maxGearboxDiameter:
                                                # while 2*Actuator.doubleStagePlanetaryGearbox.Stage2.getPCRadiusRingMM() <= maxGearBoxDia:
                                                    # Setting number of Planet
                                                    Actuator.doubleStagePlanetaryGearbox.Stage2.setNumPlanet(self.NUM_PLANET_STAGE2_MIN)
                                                    while Actuator.doubleStagePlanetaryGearbox.Stage2.numPlanet <= self.NUM_PLANET_STAGE2_MAX:
                                                        self.cntrIterBeforeCons += 1
                                                        #print("Before Constraints", cntrIterBeforeCons)
                                                        if (Actuator.doubleStagePlanetaryGearbox.geometricConstraint() and 
                                                            Actuator.doubleStagePlanetaryGearbox.meshingConstraint() and 
                                                            Actuator.doubleStagePlanetaryGearbox.noPlanetInterferenceConstraint()):
                                                            self.totalFeasibleGearboxes += 1
                                                            # Fiter for the Gear Ratio
                                                            if (Actuator.doubleStagePlanetaryGearbox.gearRatio() >= self.gearRatioIter and 
                                                                Actuator.doubleStagePlanetaryGearbox.gearRatio() <= (self.gearRatioIter + 1)):

                                                                self.totalGearboxesWithReqGR += 1

                                                                Actuator.updateFacewidth()
                                                                # effActuator = Actuator.doubleStagePlanetaryGearbox.getEfficiency()
                                                                # massActuator = Actuator.getMassKG_3DP()
                                                                
                                                                self.Cost = self.cost(Actuator=Actuator)

                                                                if self.Cost < MinCost:
                                                                    MinCost = self.Cost
                                                                    self.iter +=1
                                                                    Actuator.genEquationFile()
                                                                    opt_done = 1
                                                                    opt_parameters = [Actuator.doubleStagePlanetaryGearbox.gearRatio(),
                                                                                      Actuator.doubleStagePlanetaryGearbox.Stage1.numPlanet,
                                                                                      Actuator.doubleStagePlanetaryGearbox.Stage2.numPlanet,
                                                                                      Actuator.doubleStagePlanetaryGearbox.Stage1.Ns,
                                                                                      Actuator.doubleStagePlanetaryGearbox.Stage1.Np,
                                                                                      Actuator.doubleStagePlanetaryGearbox.Stage1.Nr,
                                                                                      Actuator.doubleStagePlanetaryGearbox.Stage2.Ns,
                                                                                      Actuator.doubleStagePlanetaryGearbox.Stage2.Np,
                                                                                      Actuator.doubleStagePlanetaryGearbox.Stage2.Nr,
                                                                                      Actuator.doubleStagePlanetaryGearbox.Stage1.module, 
                                                                                      Actuator.doubleStagePlanetaryGearbox.Stage2.module]
                                                                    opt_planetaryGearbox = doubleStagePlanetaryGearbox(design_parameters         = self.design_parameters,
                                                                                                                       gear_standard_parameters  = self.gear_standard_parameters,
                                                                                                                       Ns1                       = Actuator.doubleStagePlanetaryGearbox.Stage1.Ns,
                                                                                                                       Np1                       = Actuator.doubleStagePlanetaryGearbox.Stage1.Np,
                                                                                                                       Nr1                       = Actuator.doubleStagePlanetaryGearbox.Stage1.Nr,
                                                                                                                       Ns2                       = Actuator.doubleStagePlanetaryGearbox.Stage2.Ns,
                                                                                                                       Np2                       = Actuator.doubleStagePlanetaryGearbox.Stage2.Np,
                                                                                                                       Nr2                       = Actuator.doubleStagePlanetaryGearbox.Stage2.Nr,  
                                                                                                                       numPlanet1                = Actuator.doubleStagePlanetaryGearbox.Stage1.numPlanet,
                                                                                                                       numPlanet2                = Actuator.doubleStagePlanetaryGearbox.Stage2.numPlanet,
                                                                                                                       module1                   = Actuator.doubleStagePlanetaryGearbox.Stage1.module, # mm
                                                                                                                       module2                   = Actuator.doubleStagePlanetaryGearbox.Stage2.module, # mm
                                                                                                                       densityGears              = Actuator.doubleStagePlanetaryGearbox.Stage1.densityGears,
                                                                                                                       densityStructure          = Actuator.doubleStagePlanetaryGearbox.Stage1.densityStructure, 
                                                                                                                       fwSun1MM                  = Actuator.doubleStagePlanetaryGearbox.Stage1.fwSunMM, # mm
                                                                                                                       fwPlanet1MM               = Actuator.doubleStagePlanetaryGearbox.Stage1.fwPlanetMM, # mm
                                                                                                                       fwRing1MM                 = Actuator.doubleStagePlanetaryGearbox.Stage1.fwRingMM, # mm
                                                                                                                       fwSun2MM                  = Actuator.doubleStagePlanetaryGearbox.Stage2.fwSunMM, # mm
                                                                                                                       fwPlanet2MM               = Actuator.doubleStagePlanetaryGearbox.Stage2.fwPlanetMM, # mm
                                                                                                                       fwRing2MM                 = Actuator.doubleStagePlanetaryGearbox.Stage2.fwRingMM, # mm
                                                                                                                       maxGearAllowableStressMPa = Actuator.doubleStagePlanetaryGearbox.Stage1.maxGearAllowableStressMPa) # MPa
                                                                    opt_actuator = doubleStagePlanetaryActuator(design_parameters           = self.design_parameters,
                                                                                                                motor                       = Actuator.motor, 
                                                                                                                motor_driver_params         = Actuator.motor_driver_params,
                                                                                                                doubleStagePlanetaryGearbox = opt_planetaryGearbox, 
                                                                                                                FOS                         = Actuator.FOS, 
                                                                                                                serviceFactor               = Actuator.serviceFactor, 
                                                                                                                maxGearboxDiameter          = Actuator.maxGearboxDiameter, # mm 
                                                                                                                stressAnalysisMethodName    = "MIT") # Lewis or AGMA or MIT
                                                                    opt_actuator.updateFacewidth()
                                                                    opt_actuator.getMassKG_3DP()
                                                                    # self.printOptimizationResults(Actuator, log, csv)
                                                        Actuator.doubleStagePlanetaryGearbox.Stage2.setNumPlanet(Actuator.doubleStagePlanetaryGearbox.Stage2.numPlanet + 1)
                                                    # Actuator.doubleStagePlanetaryGearbox.Stage2.setNr(Actuator.doubleStagePlanetaryGearbox.Stage2.Ns + 1)
                                                Actuator.doubleStagePlanetaryGearbox.Stage2.setNp(Actuator.doubleStagePlanetaryGearbox.Stage2.Np + 1)
                                            Actuator.doubleStagePlanetaryGearbox.Stage2.setNs(Actuator.doubleStagePlanetaryGearbox.Stage2.Ns + 1)
                                        Actuator.doubleStagePlanetaryGearbox.Stage1.setNumPlanet(Actuator.doubleStagePlanetaryGearbox.Stage1.numPlanet + 1)
                                    # Actuator.doubleStagePlanetaryGearbox.Stage1.setNr(Actuator.doubleStagePlanetaryGearbox.Stage1.Nr + 1)
                                Actuator.doubleStagePlanetaryGearbox.Stage1.setNp(Actuator.doubleStagePlanetaryGearbox.Stage1.Np + 1)
                            Actuator.doubleStagePlanetaryGearbox.Stage1.setNs(Actuator.doubleStagePlanetaryGearbox.Stage1.Ns + 1)
                        Actuator.doubleStagePlanetaryGearbox.Stage2.setModule(Actuator.doubleStagePlanetaryGearbox.Stage2.module + 0.100)
                        Actuator.doubleStagePlanetaryGearbox.Stage2.setModule(round(Actuator.doubleStagePlanetaryGearbox.Stage2.module,1))
                    Actuator.doubleStagePlanetaryGearbox.Stage1.setModule(Actuator.doubleStagePlanetaryGearbox.Stage1.module + 0.100)
                    Actuator.doubleStagePlanetaryGearbox.Stage1.setModule(round(Actuator.doubleStagePlanetaryGearbox.Stage1.module,1))
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

        return totalTime

    def optimizeActuatorWithPSC(self, Actuator=doubleStagePlanetaryActuator, log=1, csv=0):
        startTime = time.time()
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
            fileName = f"./results/results_bilevel_{Actuator.motor.motorName}/DSPG_BILEVEL_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}.csv"
        elif log:
            fileName = f"./results/results_bilevel_{Actuator.motor.motorName}/DSPG_BILEVEL_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}_LOG.txt"
        
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

                Actuator.doubleStagePlanetaryGearbox.Stage1.setModule(self.MODULE_STAGE1_MIN)
                while Actuator.doubleStagePlanetaryGearbox.Stage1.module <= self.MODULE_STAGE1_MAX:
                    Actuator.doubleStagePlanetaryGearbox.Stage2.setModule(self.MODULE_STAGE2_MIN)
                    while Actuator.doubleStagePlanetaryGearbox.Stage2.module <= self.MODULE_STAGE2_MAX:
                        # Setting Ns
                        Actuator.doubleStagePlanetaryGearbox.Stage1.setNs(self.NUM_TEETH_SUN_MIN)
                        while 2*Actuator.doubleStagePlanetaryGearbox.Stage1.getPCRadiusSunMM() <= Actuator.maxGearboxDiameter:
                            # Setting Np
                            Actuator.doubleStagePlanetaryGearbox.Stage1.setNp(self.NUM_TEETH_PLANET_MIN)
                            while 2*Actuator.doubleStagePlanetaryGearbox.Stage1.getPCRadiusPlanetMM() <= Actuator.maxGearboxDiameter/2:
                                # Setting Nr
                                Actuator.doubleStagePlanetaryGearbox.Stage1.setNr(2*Actuator.doubleStagePlanetaryGearbox.Stage1.Np + 
                                                                                Actuator.doubleStagePlanetaryGearbox.Stage1.Ns)
                                if 2*Actuator.doubleStagePlanetaryGearbox.Stage1.getPCRadiusRingMM() <= Actuator.maxGearboxDiameter:
                                # while 2*Actuator.doubleStagePlanetaryGearbox.Stage1.getPCRadiusRingMM() <= maxGearBoxDia:
                                    # Setting number of Planet
                                    Actuator.doubleStagePlanetaryGearbox.Stage1.setNumPlanet(self.NUM_PLANET_STAGE1_MIN)
                                    while Actuator.doubleStagePlanetaryGearbox.Stage1.numPlanet <= self.NUM_PLANET_STAGE1_MAX:
                                        # # Setting Nr
                                        Actuator.doubleStagePlanetaryGearbox.Stage2.setNs(self.NUM_TEETH_SUN_MIN)
                                        while 2*Actuator.doubleStagePlanetaryGearbox.Stage2.getPCRadiusSunMM() <= Actuator.maxGearboxDiameter:
                                            # Setting Np
                                            Actuator.doubleStagePlanetaryGearbox.Stage2.setNp(self.NUM_TEETH_PLANET_MIN)
                                            while 2*Actuator.doubleStagePlanetaryGearbox.Stage2.getPCRadiusPlanetMM() <= Actuator.maxGearboxDiameter/2:
                                                # Setting Ns
                                                Actuator.doubleStagePlanetaryGearbox.Stage2.setNr(2*Actuator.doubleStagePlanetaryGearbox.Stage2.Np + 
                                                                                                Actuator.doubleStagePlanetaryGearbox.Stage2.Ns)
                                                if 2*Actuator.doubleStagePlanetaryGearbox.Stage2.getPCRadiusRingMM() <= Actuator.maxGearboxDiameter:
                                                # while 2*Actuator.doubleStagePlanetaryGearbox.Stage2.getPCRadiusRingMM() <= maxGearBoxDia:
                                                    # Setting number of Planet
                                                    Actuator.doubleStagePlanetaryGearbox.Stage2.setNumPlanet(self.NUM_PLANET_STAGE2_MIN)
                                                    while Actuator.doubleStagePlanetaryGearbox.Stage2.numPlanet <= self.NUM_PLANET_STAGE2_MAX:
                                                        self.cntrIterBeforeCons += 1
                                                        #print("Before Constraints", cntrIterBeforeCons)
                                                        if (Actuator.doubleStagePlanetaryGearbox.geometricConstraint() and 
                                                            Actuator.doubleStagePlanetaryGearbox.meshingConstraint() and 
                                                            Actuator.doubleStagePlanetaryGearbox.noPlanetInterferenceConstraint()):
                                                            self.totalFeasibleGearboxes += 1
                                                            # Fiter for the Gear Ratio
                                                            if (Actuator.doubleStagePlanetaryGearbox.gearRatio() >= self.gearRatioIter and 
                                                                Actuator.doubleStagePlanetaryGearbox.gearRatio() <= (self.gearRatioIter + self.GEAR_RATIO_STEP)):

                                                                self.totalGearboxesWithReqGR += 1

                                                                Actuator.updateFacewidth()
                                                                effActuator = Actuator.doubleStagePlanetaryGearbox.getEfficiency()
                                                                # massActuator = Actuator.getMassStructureKG()
                                                                massActuator = Actuator.getMassKG_3DP()
                                                                self.Cost = (self.K_Mass * massActuator) + (self.K_Eff * effActuator)

                                                                if self.Cost < MinCost:
                                                                    MinCost = self.Cost
                                                                    self.iter +=1
                                                                    opt_done = 1
                                                                    Actuator.genEquationFile()
                                                                    opt_parameters = [Actuator.doubleStagePlanetaryGearbox.gearRatio(),
                                                                                      Actuator.doubleStagePlanetaryGearbox.Stage1.numPlanet,
                                                                                      Actuator.doubleStagePlanetaryGearbox.Stage2.numPlanet,
                                                                                      Actuator.doubleStagePlanetaryGearbox.Stage1.Ns,
                                                                                      Actuator.doubleStagePlanetaryGearbox.Stage1.Np,
                                                                                      Actuator.doubleStagePlanetaryGearbox.Stage1.Nr,
                                                                                      Actuator.doubleStagePlanetaryGearbox.Stage2.Ns,
                                                                                      Actuator.doubleStagePlanetaryGearbox.Stage2.Np,
                                                                                      Actuator.doubleStagePlanetaryGearbox.Stage2.Nr,
                                                                                      Actuator.doubleStagePlanetaryGearbox.Stage1.module, 
                                                                                      Actuator.doubleStagePlanetaryGearbox.Stage2.module]
                                                                    opt_planetaryGearbox = doubleStagePlanetaryGearbox(design_parameters         = self.design_parameters,
                                                                                                                       gear_standard_parameters  = self.gear_standard_parameters,
                                                                                                                       Ns1                       = Actuator.doubleStagePlanetaryGearbox.Stage1.Ns,
                                                                                                                       Np1                       = Actuator.doubleStagePlanetaryGearbox.Stage1.Np,
                                                                                                                       Nr1                       = Actuator.doubleStagePlanetaryGearbox.Stage1.Nr,
                                                                                                                       Ns2                       = Actuator.doubleStagePlanetaryGearbox.Stage2.Ns,
                                                                                                                       Np2                       = Actuator.doubleStagePlanetaryGearbox.Stage2.Np,
                                                                                                                       Nr2                       = Actuator.doubleStagePlanetaryGearbox.Stage2.Nr,  
                                                                                                                       numPlanet1                = Actuator.doubleStagePlanetaryGearbox.Stage1.numPlanet,
                                                                                                                       numPlanet2                = Actuator.doubleStagePlanetaryGearbox.Stage2.numPlanet,
                                                                                                                       module1                   = Actuator.doubleStagePlanetaryGearbox.Stage1.module, # mm
                                                                                                                       module2                   = Actuator.doubleStagePlanetaryGearbox.Stage2.module, # mm
                                                                                                                       densityGears              = Actuator.doubleStagePlanetaryGearbox.Stage1.densityGears,
                                                                                                                       densityStructure          = Actuator.doubleStagePlanetaryGearbox.Stage1.densityStructure, 
                                                                                                                       fwSun1MM                  = Actuator.doubleStagePlanetaryGearbox.Stage1.fwSunMM, # mm
                                                                                                                       fwPlanet1MM               = Actuator.doubleStagePlanetaryGearbox.Stage1.fwPlanetMM, # mm
                                                                                                                       fwRing1MM                 = Actuator.doubleStagePlanetaryGearbox.Stage1.fwRingMM, # mm
                                                                                                                       fwSun2MM                  = Actuator.doubleStagePlanetaryGearbox.Stage2.fwSunMM, # mm
                                                                                                                       fwPlanet2MM               = Actuator.doubleStagePlanetaryGearbox.Stage2.fwPlanetMM, # mm
                                                                                                                       fwRing2MM                 = Actuator.doubleStagePlanetaryGearbox.Stage2.fwRingMM, # mm
                                                                                                                       maxGearAllowableStressMPa = Actuator.doubleStagePlanetaryGearbox.Stage1.maxGearAllowableStressMPa) # MPa
                                                                    opt_actuator = doubleStagePlanetaryActuator(design_parameters           = self.design_parameters,
                                                                                                                motor                       = Actuator.motor, 
                                                                                                                doubleStagePlanetaryGearbox = opt_planetaryGearbox, 
                                                                                                                FOS                         = Actuator.FOS, 
                                                                                                                serviceFactor               = Actuator.serviceFactor, 
                                                                                                                maxGearboxDiameter          = Actuator.maxGearboxDiameter, # mm 
                                                                                                                stressAnalysisMethodName    = "Lewis") # Lewis or AGMA
                                                                    # self.printOptimizationResults(Actuator, log, csv)
                                                        Actuator.doubleStagePlanetaryGearbox.Stage2.setNumPlanet(Actuator.doubleStagePlanetaryGearbox.Stage2.numPlanet + 1)
                                                    # Actuator.doubleStagePlanetaryGearbox.Stage2.setNr(Actuator.doubleStagePlanetaryGearbox.Stage2.Ns + 1)
                                                Actuator.doubleStagePlanetaryGearbox.Stage2.setNp(Actuator.doubleStagePlanetaryGearbox.Stage2.Np + 1)
                                            Actuator.doubleStagePlanetaryGearbox.Stage2.setNs(Actuator.doubleStagePlanetaryGearbox.Stage2.Ns + 1)
                                        Actuator.doubleStagePlanetaryGearbox.Stage1.setNumPlanet(Actuator.doubleStagePlanetaryGearbox.Stage1.numPlanet + 1)
                                    # Actuator.doubleStagePlanetaryGearbox.Stage1.setNr(Actuator.doubleStagePlanetaryGearbox.Stage1.Nr + 1)
                                Actuator.doubleStagePlanetaryGearbox.Stage1.setNp(Actuator.doubleStagePlanetaryGearbox.Stage1.Np + 1)
                            Actuator.doubleStagePlanetaryGearbox.Stage1.setNs(Actuator.doubleStagePlanetaryGearbox.Stage1.Ns + 1)
                        Actuator.doubleStagePlanetaryGearbox.Stage2.setModule(Actuator.doubleStagePlanetaryGearbox.Stage2.module + 0.100)
                        Actuator.doubleStagePlanetaryGearbox.Stage2.setModule(round(Actuator.doubleStagePlanetaryGearbox.Stage2.module,1))
                    Actuator.doubleStagePlanetaryGearbox.Stage1.setModule(Actuator.doubleStagePlanetaryGearbox.Stage1.module + 0.100)
                    Actuator.doubleStagePlanetaryGearbox.Stage1.setModule(round(Actuator.doubleStagePlanetaryGearbox.Stage1.module,1))
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

        return totalTime

    def printOptimizationParameters(self, Actuator=doubleStagePlanetaryActuator, log=1, csv=0):
        # Motor Parameters
        maxMotorAngVelRPM       = Actuator.motor.maxMotorAngVelRPM
        maxMotorAngVelRadPerSec = Actuator.motor.maxMotorAngVelRadPerSec
        maxMotorTorque          = Actuator.motor.maxMotorTorque
        maxMotorPower           = Actuator.motor.maxMotorPower
        motorMass               = Actuator.motor.massKG
        motorDia                = Actuator.motor.motorDiaMM
        motorLength             = Actuator.motor.motorLengthMM
        
        # Planetary Gearbox Parameters
        maxGearAllowableStressMPa = Actuator.doubleStagePlanetaryGearbox.maxGearAllowableStressMPa
        
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

    def printOptimizationResults(self, Actuator=doubleStagePlanetaryActuator, log=1, csv=0):
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
            gearRatio   = Actuator.doubleStagePlanetaryGearbox.gearRatio()
            module1     = Actuator.doubleStagePlanetaryGearbox.Stage1.module
            Ns1         = Actuator.doubleStagePlanetaryGearbox.Stage1.Ns
            Np1         = Actuator.doubleStagePlanetaryGearbox.Stage1.Np
            Nr1         = Actuator.doubleStagePlanetaryGearbox.Stage1.Nr
            numPlanet1  = Actuator.doubleStagePlanetaryGearbox.Stage1.numPlanet
            module2     = Actuator.doubleStagePlanetaryGearbox.Stage2.module
            Ns2         = Actuator.doubleStagePlanetaryGearbox.Stage2.Ns
            Np2         = Actuator.doubleStagePlanetaryGearbox.Stage2.Np
            Nr2         = Actuator.doubleStagePlanetaryGearbox.Stage2.Nr
            numPlanet2  = Actuator.doubleStagePlanetaryGearbox.Stage2.numPlanet
            fwSun1MM    = round(Actuator.doubleStagePlanetaryGearbox.Stage1.fwSunMM    , 3)
            fwPlanet1MM = round(Actuator.doubleStagePlanetaryGearbox.Stage1.fwPlanetMM , 3)
            fwRing1MM   = round(Actuator.doubleStagePlanetaryGearbox.Stage1.fwRingMM   , 3)
            fwSun2MM    = round(Actuator.doubleStagePlanetaryGearbox.Stage2.fwSunMM    , 3)
            fwPlanet2MM = round(Actuator.doubleStagePlanetaryGearbox.Stage2.fwPlanetMM , 3)
            fwRing2MM   = round(Actuator.doubleStagePlanetaryGearbox.Stage2.fwRingMM   , 3)
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
            eff         = round(Actuator.doubleStagePlanetaryGearbox.getEfficiency(), 3)
            if (self.UsePSCasVariable == 1):
                eff = self.dspgOpt.getEfficiency(Var = False)
            
            peakTorque  = round(Actuator.motor.getMaxMotorTorque()*Actuator.doubleStagePlanetaryGearbox.gearRatio(), 3)
            Cost        = self.cost(Actuator=Actuator)
            Torque_Density =  peakTorque/mass
            Outer_Bearing_mass_stg1 = Actuator.bearing_mass_stg1
            Outer_Bearing_mass_stg2 = Actuator.bearing_mass_stg2
            Actuator_width = Actuator.actuator_width
            print(iter,",", gearRatio,",", module1,",", module2,",", Ns1,",", Np1,",", Nr1,",", numPlanet1,",", Ns2,",", Np2,",", Nr2,",", numPlanet2,",", fwSun1MM,",", fwPlanet1MM,",", fwRing1MM,",", fwSun2MM,",", fwPlanet2MM,",", fwRing2MM,"," , mass, ",", eff, ",", peakTorque, ",", Cost,",", Torque_Density,",", Outer_Bearing_mass_stg1,",", Outer_Bearing_mass_stg2,",",Actuator_width)

    def cost(self, Actuator=doubleStagePlanetaryActuator):
        K_gearRatio = 0
        if self.gearRatioReq != 0:
            K_gearRatio = 1
        
        gearRatio_err = np.sqrt((Actuator.doubleStagePlanetaryGearbox.gearRatio() - self.gearRatioReq)**2)

        mass = Actuator.getMassKG_3DP()
        eff = Actuator.doubleStagePlanetaryGearbox.getEfficiency()
        width = Actuator.doubleStagePlanetaryGearbox.Stage1.fwPlanetMM + Actuator.doubleStagePlanetaryGearbox.Stage2.fwPlanetMM
        cost = (self.K_Mass    * mass 
                + self.K_Eff   * eff 
                + self.K_Width * width 
                + K_gearRatio  * gearRatio_err)
        return cost