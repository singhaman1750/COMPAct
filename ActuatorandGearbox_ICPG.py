from typing import Any
import numpy as np
import os
import sys
import time
import math


from CommonComponents import material, bearings_discrete, nuts_and_bolts_dimensions, motor_frameless_outrunner as motor


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  INTERNAL COMPOUND PLANETARY GEARBOX                                    ║
# ╚══════════════════════════════════════════════════════════════════════════╝
class internalcompoundPlanetaryGearbox:
    # NOTE: Logic in this class is intentionally unchanged.
    #       Section comments have been added for navigation only.

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

        # ── Gear tooth counts ──────────────────────────────────────────────
        self.Ns        = Ns
        self.NpBig     = NpBig
        self.NpSmall   = NpSmall
        self.Nr        = Nr
        self.numPlanet = numPlanet

        # ── Module (pitch) ─────────────────────────────────────────────────
        self.moduleBig   = moduleBig
        self.moduleSmall = moduleSmall

        # ── Face widths (mm) ───────────────────────────────────────────────
        self.fwSunMM         = fwSunMM
        self.fwPlanetBigMM   = fwPlanetBigMM
        self.fwPlanetSmallMM = fwPlanetSmallMM
        self.fwRingMM        = fwRingMM

        # ── Material / stress ──────────────────────────────────────────────
        self.densityGears              = densityGears
        self.densityStructure          = densityStructure
        self.maxGearAllowableStressMPa = maxGearAllowableStressMPa
        self.maxGearAllowableStressPa  = maxGearAllowableStressMPa * 10 ** 6

        # ── Standard gear parameters ───────────────────────────────────────
        self.mu               = gear_standard_parameters["coefficientOfFriction"]
        self.pressureAngleDEG = gear_standard_parameters["pressureAngleDEG"]

        # ── Design / geometric parameters ─────────────────────────────────
        self.ringRadialWidthMM            = design_parameters["ringRadialWidthMM"]
        self.planetMinDistanceMM          = design_parameters["planetMinDistanceMM"]
        self.sCarrierExtrusionDiaMM       = design_parameters["sCarrierExtrusionDiaMM"]
        self.sCarrierExtrusionClearanceMM = design_parameters["sCarrierExtrusionClearanceMM"]

    # ── Constraint checks ──────────────────────────────────────────────────
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

    # ── Mass estimate ──────────────────────────────────────────────────────
    def getMassKG(self):
        fwSunM            = (self.fwSunMM / 1000.0)
        fwPlanetBigM      = (self.fwPlanetBigMM / 1000.0)
        fwPlanetSmallM    = (self.fwPlanetSmallMM / 1000.0)
        fwRingM           = (self.fwRingMM / 1000.0)
        carrierWidthM     = 0.005  # placeholder
        sunVolume         = np.pi * fwSunM * (self.getPCRadiusSunM()**2)
        planetBigVolume   = np.pi * fwPlanetBigM * (self.getPCRadiusPlanetBigM()**2)
        planetSmallVolume = np.pi * fwPlanetSmallM * (self.getPCRadiusPlanetSmallM()**2)
        ringVolume        = np.pi * fwRingM * (self.getOuterRadiusRingM()**2 - self.getPCRadiusRingM()**2)
        carrierVolume     = 2 * np.pi * carrierWidthM * (self.getCarrierRadiusM()**2)

        combinedGearVolume = sunVolume + (self.numPlanet * planetBigVolume) + planetSmallVolume + ringVolume
        TotalMassKG        = (combinedGearVolume * self.densityGears + carrierVolume * self.densityStructure)
        return TotalMassKG

    # ── Gear ratio ─────────────────────────────────────────────────────────
    def gearRatio(self):
        Rs      = self.Ns * self.moduleBig
        RpBig   = self.NpBig * self.moduleBig
        RpSmall = self.NpSmall * self.moduleSmall
        Rr      = self.Nr * self.moduleSmall
        GR      = ((Rs + RpBig) * (RpSmall + RpBig)) / (Rs * RpSmall)
        return GR

    # ── Involute helpers ───────────────────────────────────────────────────
    def inverse_involute(self, inv_alpha):
        alpha = (  (3*inv_alpha)**(1/3)
                 - (2*inv_alpha)/5
                 + (9/175)*(3)**(2/3)*inv_alpha**(5/3)
                 - (2/175)*(3)**(1/3)*(inv_alpha)**(7/3)
                 - (144/67375)*(inv_alpha)**(3)
                 + (3258/3128125)*(3)**(2/3)*(inv_alpha)**(11/3)
                 - (49711/153278125)*(3)**(1/3)*(inv_alpha)**(13/3))
        return alpha

    def involute(self, alpha):
        return (np.tan(alpha) - alpha)

    def quadratic_min(self, a, b, k=0.01):
        return (a + b - np.sqrt((a - b)**2 + k**2)) / 2

    # ── Pressure angle & geometry ──────────────────────────────────────────
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
        inv_alpha_w_sunPlanet   = 2*np.tan(alpha)*((xs + xp1)/(Ns + Np1)) + self.involute(alpha)
        alpha_w_sunPlanet       = self.inverse_involute(inv_alpha_w_sunPlanet)
        inv_alpha_w_planetRing  = 2*np.tan(alpha)*((xr-xp2)/(Nr - Np2)) + self.involute(alpha)
        alpha_w_planetRing      = self.inverse_involute(inv_alpha_w_planetRing)
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
        centerDist_sunPlanet  = ((Ns + Np1)/2  + y_sunPlanet)  * module1
        centerDist_planetRing = ((Nr - Np2)/2  + y_planetRing) * module2
        return centerDist_sunPlanet, centerDist_planetRing

    def getBaseDia(self):
        module1 = self.moduleBig
        module2 = self.moduleSmall
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr      = self.Nr

        alpha     = self.getPressureAngleRad()
        D_sun     = module1 * Ns
        D_planet1 = module1 * Np1
        D_planet2 = module2 * Np2
        D_ring    = module2 * Nr

        D_b_sun     = D_sun     * np.cos(alpha)
        D_b_planet1 = D_planet1 * np.cos(alpha)
        D_b_planet2 = D_planet2 * np.cos(alpha)
        D_b_ring    = D_ring    * np.cos(alpha)
        return D_b_sun, D_b_planet1, D_b_planet2, D_b_ring

    def getTipCircleDia(self):
        module1 = self.moduleBig
        module2 = self.moduleSmall
        Ns      = self.Ns
        Np1     = self.NpBig
        Np2     = self.NpSmall
        Nr      = self.Nr
        xs, xp1, xp2, xr = 0, 0, 0, 0

        alpha     = self.getPressureAngleRad()
        D_sun     = module1 * Ns
        D_planet1 = module1 * Np1
        D_planet2 = module2 * Np2
        D_ring    = module2 * Nr

        y_sunPlanet, y_planetRing = self.getCenterDistModificationCoeff()

        D_a_sun     = D_sun     + 2 * module1 * (1 + y_sunPlanet - xp1)
        D_a_planet1 = D_planet1 + 2 * module1 * (1 + self.quadratic_min((y_sunPlanet - xs), xp1))
        D_a_planet2 = D_planet2 + 2 * module2 * (1 + self.quadratic_min((y_planetRing - xs), xp2))
        D_a_ring    = D_ring    - 2 * module2 * (1 - xr)
        return D_a_sun, D_a_planet1, D_a_planet2, D_a_ring

    def getTipPressureAngle(self):
        alpha = self.getPressureAngleRad()
        D_b_sun, D_b_planet1, D_b_planet2, D_b_ring = self.getBaseDia()
        D_a_sun, D_a_planet1, D_a_planet2, D_a_ring = self.getTipCircleDia()

        alpha_a_sun     = np.arccos(D_b_sun     / D_a_sun)
        alpha_a_planet1 = np.arccos(D_b_planet1 / D_a_planet1)
        alpha_a_planet2 = np.arccos(D_b_planet2 / D_a_planet2)
        alpha_a_ring    = np.arccos(D_b_ring    / D_a_ring)
        return alpha_a_sun, alpha_a_planet1, alpha_a_planet2, alpha_a_ring

    def getErrorTipCircleDia_planet(self):
        module1 = self.moduleBig
        module2 = self.moduleSmall
        Np1     = self.NpBig
        Np2     = self.NpSmall
        xs, xp1, xp2, xr = 0, 0, 0, 0

        y_sunPlanet, y_planetRing = self.getCenterDistModificationCoeff()
        _, D_a_planet1_quadMin, D_a_planet2_quadMin, _ = self.getTipCircleDia()

        D_a_planet1_actMin = module1 * Np1 + 2 * module1 * (1 + np.minimum((y_sunPlanet - xs), xp1))
        D_a_planet2_actMin = module2 * Np2 + 2 * module2 * (1 + np.minimum((y_planetRing - xs), xp2))
        return np.abs(D_a_planet1_quadMin - D_a_planet1_actMin), np.abs(D_a_planet2_quadMin - D_a_planet2_actMin)

    # ── Contact ratios ─────────────────────────────────────────────────────
    def contactRatio_sunPlanet(self):
        Ns  = self.Ns
        Np1 = self.NpBig

        alpha_w_sunPlanet, _ = self.getWorkingPressureAngle()
        alpha_a_sun, alpha_a_planet1, _, _ = self.getTipPressureAngle()

        Approach_CR_sunPlanet = (Np1 / (2 * np.pi)) * (np.tan(alpha_a_planet1) - np.tan(alpha_w_sunPlanet))
        Recess_CR_sunPlanet   = (Ns  / (2 * np.pi)) * (np.tan(alpha_a_sun)     - np.tan(alpha_w_sunPlanet))
        CR_sunPlanet = Approach_CR_sunPlanet + Recess_CR_sunPlanet
        return Approach_CR_sunPlanet, Recess_CR_sunPlanet, CR_sunPlanet

    def contactRatio_planetRing(self):
        Np2 = self.NpSmall
        Nr  = self.Nr

        _, alpha_w_planetRing = self.getWorkingPressureAngle()
        _, _, alpha_a_planet2, alpha_a_ring = self.getTipPressureAngle()

        Approach_CR_planetRing = -(Nr  / (2 * np.pi)) * (np.tan(alpha_a_ring)    - np.tan(alpha_w_planetRing))
        Recess_CR_planetRing   =  (Np2 / (2 * np.pi)) * (np.tan(alpha_a_planet2) - np.tan(alpha_w_planetRing))
        CR_planetRing = Approach_CR_planetRing + Recess_CR_planetRing
        return Approach_CR_planetRing, Recess_CR_planetRing, CR_planetRing

    # ── Efficiency ─────────────────────────────────────────────────────────
    def getEfficiency(self):
        Ns  = self.Ns
        Np1 = self.NpBig
        Np2 = self.NpSmall
        Nr  = self.Nr

        eps_sunPlanetA, eps_sunPlanetR, _   = self.contactRatio_sunPlanet()
        eps_planetRingA, eps_planetRingR, _ = self.contactRatio_planetRing()

        epsilon_sunPlanet  = eps_sunPlanetA**2  + eps_sunPlanetR**2  - eps_sunPlanetA  - eps_sunPlanetR  + 1
        epsilon_planetRing = eps_planetRingA**2 + eps_planetRingR**2 - eps_planetRingA - eps_planetRingR + 1

        eff_SP = 1 - self.mu * np.pi * ((1 / Np1) + (1 / Ns))  * epsilon_sunPlanet
        eff_PR = 1 - self.mu * np.pi * ((1 / Np2) - (1 / Nr))  * epsilon_planetRing

        Numerator   = (Ns * Np2 + eff_SP * eff_PR * Np1 * Nr)
        Denominator = (Ns + Np1) * (Np2 + Np1)
        return Numerator / Denominator

    # ── Pitch / outer radii (SI) ───────────────────────────────────────────
    def getPCRadiusSunM(self):         return (self.Ns     * self.moduleBig   / 2) / 1000.0
    def getPCRadiusPlanetBigM(self):   return (self.NpBig  * self.moduleBig   / 2) / 1000.0
    def getPCRadiusPlanetSmallM(self): return (self.NpSmall* self.moduleSmall / 2) / 1000.0
    def getPCRadiusRingM(self):        return (self.Nr     * self.moduleSmall / 2) / 1000.0

    def getGearboxOuterDiaMaxM(self):
        Rs    = self.Ns    * self.moduleBig * 0.5
        RpBig = self.NpBig * self.moduleBig * 0.5
        return (Rs + 2*RpBig) * 2 / 1000.0

    # ── Pitch / outer radii (mm) ───────────────────────────────────────────
    def getPCRadiusSunMM(self):         return (self.Ns     * self.moduleBig   / 2)
    def getPCRadiusPlanetBigMM(self):   return (self.NpBig  * self.moduleBig   / 2)
    def getPCRadiusPlanetSmallMM(self): return (self.NpSmall* self.moduleSmall / 2)
    def getPCRadiusRingMM(self):        return (self.Nr     * self.moduleSmall / 2)

    def getOuterRadiusRingM(self):
        ringPCRadiusMM = (self.Nr * self.moduleSmall) / 2
        return (ringPCRadiusMM + self.ringRadialWidthMM) / 1000.0

    def getCarrierRadiusM(self):
        return (((self.Ns + self.NpBig + self.NpBig/2) / 2) * self.moduleBig) / 1000.0

    # ── Setters ────────────────────────────────────────────────────────────
    def setfwSunMM(self, fwSunMM):               self.fwSunMM         = fwSunMM
    def setfwPlanetBigMM(self, fwPlanetBigMM):   self.fwPlanetBigMM   = fwPlanetBigMM
    def setfwPlanetSmallMM(self, fwPlanetSmallMM): self.fwPlanetSmallMM = fwPlanetSmallMM
    def setfwRingMM(self, fwRingMM):             self.fwRingMM        = fwRingMM
    def setModuleBig(self, moduleBig):           self.moduleBig       = moduleBig
    def setModuleSmall(self, moduleSmall):       self.moduleSmall     = moduleSmall
    def setNs(self, Ns):                         self.Ns              = Ns
    def setNpBig(self, NpBig):                   self.NpBig           = NpBig
    def setNpSmall(self, NpSmall):               self.NpSmall         = NpSmall
    def setNr(self, Nr):                         self.Nr              = Nr
    def setNumPlanet(self, numPlanet):           self.numPlanet       = numPlanet

    # ── Print helpers ──────────────────────────────────────────────────────
    def printParameters(self):
        print("Ns = ",                             self.Ns)
        print("NpBig = ",                          self.NpBig)
        print("NpSmall = ",                        self.NpSmall)
        print("Nr = ",                             self.Nr)
        print("Module (First Layer) = ",           self.moduleBig)
        print("Module (Second Layer) = ",          self.moduleSmall)
        print("Number of planets = ",              self.numPlanet)
        print("Face width of sun gear = ",         round(self.fwSunMM, 2),         " mm")
        print("Face width of Bigger planet = ",    round(self.fwPlanetBigMM, 2),   " mm")
        print("Face width of Smaller planet = ",   round(self.fwPlanetSmallMM, 2), " mm")
        print("Face width of ring gear = ",        round(self.fwRingMM, 2),        " mm")
        print("Ring radial width = ",              self.ringRadialWidthMM,          " mm")
        print("PC radius of sun = ",               self.getPCRadiusSunM()         * 1000, " mm")
        print("PC radius of planet (big) = ",      self.getPCRadiusPlanetBigM()   * 1000, " mm")
        print("PC radius of planet (small) = ",    self.getPCRadiusPlanetSmallM() * 1000, " mm")
        print("PC radius of ring = ",              self.getPCRadiusRingM()         * 1000, " mm")
        print("Outer radius of ring = ",           self.getOuterRadiusRingM()      * 1000, " mm")
        print("Geometric constraint = ",           self.geometricConstraint())
        print("Meshing constraint = ",             self.meshingConstraint())
        print("No planet interference = ",         self.noPlanetInterferenceConstraint())
        print("Mass (gearbox) = ",                 self.getMassKG(),               " kg")
        print("Efficiency = ",                     self.getEfficiency())

    def printParametersLess(self):
        vars_      = [self.moduleBig, self.moduleSmall, self.Ns, self.NpBig, self.NpSmall, self.Nr, self.numPlanet]
        faceWidths = [round(self.fwSunMM,2), round(self.fwPlanetBigMM,2),
                      round(self.fwPlanetSmallMM,2), round(self.fwRingMM,2)]
        print("[mB, mS, Ns, NpB, NpS, Nr, numPl]:", vars_)
        print("Face widths = ",      faceWidths)
        print(" ")
        print("Gear ratio = ",       self.gearRatio())
        print("Efficiency = ",       round(self.getEfficiency(), 4))
        print("Mass (gearbox) = ",   round(self.getMassKG(), 3), " kg")


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  MOTOR                                                                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝
class internalcompoundPlanetaryActuator:

    def __init__(self,
                 design_parameters,
                 motor_driver_params                  = None,
                 motor                                = motor,
                 internalcompoundPlanetaryGearbox     = internalcompoundPlanetaryGearbox,
                 FOS                                  = 2.0,
                 serviceFactor                        = 2.0,
                 maxGearboxDiameter                   = 140.0,
                 stressAnalysisMethodName             = "Lewis"):

        self.motor                            = motor
        self.internalcompoundPlanetaryGearbox = internalcompoundPlanetaryGearbox
        self.FOS                              = FOS
        self.serviceFactor                    = serviceFactor
        self.maxGearboxDiameter               = maxGearboxDiameter
        self.stressAnalysisMethodName         = stressAnalysisMethodName

        # ── Motor convenience aliases ──────────────────────────────────────
        self.motorLengthMM           = self.motor.getStatorHeightMM()
        self.motorDiaMM              = self.motor.getRotorODMM()
        self.motorMassKG             = self.motor.getMassKG()
        self.MaxMotorTorque          = self.motor.getMaxMotorTorque()
        self.MaxMotorAngVelRPM       = self.motor.getMaxMotorAngVelRadPerSec()
        self.MaxMotorAngVelRadPerSec = self.motor.getMaxMotorAngVelRadPerSec()

        self.design_params     = design_parameters
        self.ringRadialWidthMM = self.internalcompoundPlanetaryGearbox.ringRadialWidthMM
        self.setVariables()

    # ── Cost function ──────────────────────────────────────────────────────
    def cost(self):
        massActuator  = self.getMassKG_3DP()
        effActuator   = self.internalcompoundPlanetaryGearbox.getEfficiency()
        widthActuator = (self.internalcompoundPlanetaryGearbox.fwPlanetBigMM
                         + self.internalcompoundPlanetaryGearbox.fwPlanetSmallMM)
        return massActuator - 2 * effActuator + 0.2 * widthActuator

    # ══════════════════════════════════════════════════════════════════════
    # setVariables – pulls all parameters into self for downstream use
    # ══════════════════════════════════════════════════════════════════════
    def setVariables(self):

        # ── Optimisation: gear tooth counts ───────────────────────────────
        self.Ns         = self.internalcompoundPlanetaryGearbox.Ns
        self.Np_b       = self.internalcompoundPlanetaryGearbox.NpBig
        self.Np_s       = self.internalcompoundPlanetaryGearbox.NpSmall
        self.Nr         = self.internalcompoundPlanetaryGearbox.Nr
        self.num_planet = self.internalcompoundPlanetaryGearbox.numPlanet
        self.module     = self.internalcompoundPlanetaryGearbox.moduleBig

        # ── Gear geometry constants ────────────────────────────────────────
        self.pressure_angle     = self.internalcompoundPlanetaryGearbox.getPressureAngleRad()
        self.pressure_angle_deg = self.pressure_angle * 180 / np.pi

        # Addendum, dedendum, tip-root clearance
        self.h_a          = 1    * self.module
        self.h_b          = 1.25 * self.module
        self.h_f          = 1.25 * self.module
        self.clr_tip_root = self.h_f - self.h_a

        # Sun gear pitch / base geometry
        self.dp_s      = self.module * self.Ns
        self.db_s      = self.dp_s * np.cos(self.pressure_angle)
        self.alpha_s   = (np.sqrt(self.dp_s**2 - self.db_s**2) / self.db_s) * 180 / np.pi - self.pressure_angle_deg
        self.beta_s    = (360 / (4 * self.Ns) - self.alpha_s) * 2
        self.fw_s_calc = self.internalcompoundPlanetaryGearbox.fwSunMM

        # Big planet pitch / base geometry
        self.dp_p_b    = self.module * self.Np_b
        self.db_p_b    = self.dp_p_b * np.cos(self.pressure_angle)
        self.alpha_p_b = (np.sqrt(self.dp_p_b**2 - self.db_p_b**2) / self.db_p_b) * 180 / np.pi - self.pressure_angle_deg
        self.beta_p_b  = (360 / (4 * self.Np_b) - self.alpha_p_b) * 2
        self.fw_p_b    = self.internalcompoundPlanetaryGearbox.fwPlanetBigMM

        # Ring gear pitch / base geometry
        self.dp_r    = self.module * self.Nr
        self.db_r    = self.dp_r * np.cos(self.pressure_angle)
        self.alpha_r = (np.sqrt(self.dp_r**2 - self.db_r**2) / self.db_r) * 180 / np.pi - self.pressure_angle_deg
        self.beta_r  = (360 / (4 * self.Nr) + self.alpha_r) * 2
        self.fw_r    = self.internalcompoundPlanetaryGearbox.fwRingMM

        # Small planet pitch / base geometry
        self.dp_p_s    = self.module * self.Np_s
        self.db_p_s    = self.dp_p_s * np.cos(self.pressure_angle)
        self.alpha_p_s = (np.sqrt(self.dp_p_s**2 - self.db_p_s**2) / self.db_p_s) * 180 / np.pi - self.pressure_angle_deg
        self.beta_p_s  = (360 / (4 * self.Np_s) - self.alpha_p_s) * 2
        self.fw_p_s    = self.fw_r + self.design_params["clearance_planet"]

        # ── Clearance / tolerance constants ───────────────────────────────
        self.clearance_planet                   = self.design_params["clearance_planet"]
        self.standard_clearance_1_5mm           = self.design_params["standard_clearance_1_5mm"]
        self.standard_fillet_1_5mm              = self.design_params["standard_fillet_1_5mm"]
        self.standard_bearing_insertion_chamfer = self.design_params["standard_bearing_insertion_chamfer"]
        self.tight_clearance_3DP                = self.design_params["tight_clearance_3DP"]
        self.loose_clearance_3DP                = self.design_params["loose_clearance_3DP"]
        self.bearingIDClearance_3DP             = self.design_params["bearingIDClearanceMM"]

        # ── Motor: overall envelope ────────────────────────────────────────
        self.motor_OD     = self.motor.getMotorODMM()
        self.motor_height = self.motor.getMotorHeightMM()

        # ── Motor: stator dimensions ───────────────────────────────────────
        self.stator_OD                    = self.motor.getStatorODMM()
        self.stator_ID                    = self.motor.getStatorIDMM()
        self.stator_height                = self.motor.getStatorHeightMM()
        self.stator_mounting_holes_PCD    = self.motor.getStatorMountingHolePCD()
        self.motor_stator_extrusion_dia   = self.motor.getMotorStatorExtrusionDia()
        self.motor_stator_extrusion_depth = self.motor.getMotorStatorExtrusionDepth()
        self.stator_top_rotor_top_offset = self.motor.getStatorTopRotorTopOffset()
        self.stator_hole_dia             = self.motor.getStatorHoleDia()

        # ── Motor: rotor dimensions ────────────────────────────────────────
        self.Rotor_OD                 = self.motor.getRotorODMM()
        self.Rotor_ID                 = self.motor.getRotorIDMM()
        self.Rotor_height             = self.motor.getRotorHeightMM()
        self.Rotor_bottom_ID          = self.motor.getRotorBottomIDMM()
        self.rotor_bottom_thickness   = self.motor.getRotorBottomThicknessMM()
        self.Rotor_csk_head_upper_dia = self.motor.getRotorCSKHeadUpperDiaMM()
        self.Rotor_csk_head_height    = self.motor.getRotorCSKHeadHeightMM()
        self.rotor_mount_hole_PCD     = self.motor.getRotorMountHolePCDMM()
        self.rotor_mount_hole_dia     = self.motor.getRotorMountHoleDiaMM()
        self.rotor_mount_hole_num     = self.motor.getMotorRotorHoleNum()
        

        # ── Planet shaft & bearing parameters ─────────────────────────────
        self.planet_pin_bolt_dia      = self.design_params["planet_pin_bolt_dia"]
        self.planet_shaft_dia         = self.design_params["planet_shaft_dia"]
        self.planet_shaft_step_offset = self.design_params["planet_shaft_step_offset"]
        self.planet_bearing_OD        = self.design_params["planet_bearing_OD"]
        self.planet_bearing_width     = self.design_params["planet_bearing_width"]
        self.planet_bore              = self.design_params["planet_bore"]

        planet_pin_bolt                  = nuts_and_bolts_dimensions(bolt_dia=self.planet_pin_bolt_dia, bolt_type="socket_head")
        self.planet_pin_socket_head_dia  = planet_pin_bolt.bolt_head_dia
        self.planet_pin_bolt_wrench_size = planet_pin_bolt.nut_width_across_flats

        # ── Sun shaft & bearing parameters ────────────────────────────────
        self.sun_shaft_bearing_ID      = self.design_params["sun_shaft_bearing_ID"]
        self.sun_shaft_bearing_OD      = self.design_params["sun_shaft_bearing_OD"]
        self.sun_shaft_bearing_width   = self.design_params["sun_shaft_bearing_width"]
        self.sun_coupler_hub_thickness = self.design_params["sun_coupler_hub_thickness"]
        self.sun_central_bolt_dia      = self.design_params["sun_central_bolt_dia"]

        sun_central_bolt                      = nuts_and_bolts_dimensions(bolt_dia=self.sun_central_bolt_dia, bolt_type="socket_head")
        self.sun_central_bolt_socket_head_dia = sun_central_bolt.bolt_head_dia

        # ── Bottom casing bearing (motor / sun interface) ──────────────────
        self.sun_gear_rotor_nut_wrench_size      = self.design_params["sun_gear_rotor_nut_wrench_size"]
        self.sun_gear_rotor_nut_height           = self.design_params["sun_gear_rotor_nut_height"]
        
        sun_hub_dia_min = self.rotor_mount_hole_PCD + self.sun_gear_rotor_nut_wrench_size + self.standard_clearance_1_5mm * 4
        
        sun_bottom_casing_bearing_ID_required  = sun_hub_dia_min #self.motor_rotor_base_ID
        sun_bottom_casing_bearing              = bearings_discrete(sun_bottom_casing_bearing_ID_required)
        
        # self.sun_bottom_casing_bearing_height   = self.motor.sun_bottom_casing_bearing_height
        # self.sun_bottom_casing_bearing_ID       = self.motor.sun_bottom_casing_bearing_ID
        # self.sun_bottom_casing_bearing_OD       = self.motor.sun_bottom_casing_bearing_OD
        # self.sun_bottom_casing_bearing_massKG   = self.motor.sun_bottom_casing_bearing_massKG

        self.sun_bottom_casing_bearing_height   = sun_bottom_casing_bearing.getBearingWidthMM()
        self.sun_bottom_casing_bearing_ID       = sun_bottom_casing_bearing.getBearingIDMM()
        self.sun_bottom_casing_bearing_OD       = sun_bottom_casing_bearing.getBearingODMM()
        self.sun_bottom_casing_bearing_massKG   = sun_bottom_casing_bearing.getBearingMassKG()

        # ── Secondary carrier bearing ──────────────────────────────────────
        self.sun_sec_carrier_bearing_height = self.design_params["sun_sec_carrier_bearing_height"]
        self.sun_sec_carrier_bearing_ID     = self.design_params["sun_sec_carrier_bearing_ID"]
        self.sun_sec_carrier_bearing_OD     = self.design_params["sun_sec_carrier_bearing_OD"]

        # ── Bearing retainer ───────────────────────────────────────────────
        self.bearing_retainer_thickness = self.design_params["bearing_retainer_thickness"]
        self.bearing_retainer_hole_dia  = self.design_params["bearing_retainer_hole_dia"]
        self.bearing_retainer_hole_num  = self.design_params["bearing_retainer_hole_num"]

        # ── Carrier geometry ───────────────────────────────────────────────
        self.sec_carrier_thickness                              = self.design_params["sec_carrier_thickness"]
        self.carrier_trapezoidal_support_sun_offset             = self.design_params["carrier_trapezoidal_support_sun_offset"]
        self.carrier_trapezoidal_support_hole_PCD_offset_bearing_ID = self.design_params["carrier_trapezoidal_support_hole_PCD_offset_bearing_ID"]
        self.carrier_trapezoidal_support_hole_dia               = self.design_params["carrier_trapezoidal_support_hole_dia"]
        self.carrier_bearing_step_width                         = self.design_params["carrier_bearing_step_width"]

        carrier_trap_hole = nuts_and_bolts_dimensions(bolt_dia=self.carrier_trapezoidal_support_hole_dia, bolt_type="socket_head")
        self.carrier_trapezoidal_support_hole_socket_head_dia = carrier_trap_hole.bolt_head_dia
        self.carrier_trapezoidal_support_hole_wrench_size     = carrier_trap_hole.nut_width_across_flats

        # ── Case mounting ──────────────────────────────────────────────────
        self.case_mounting_hole_dia              = self.design_params["case_mounting_hole_dia"]
        self.case_mounting_hole_wrench_size      = self.design_params["case_mounting_hole_wrench_size"]
        self.case_mounting_hole_wrench_thickness = self.design_params["case_mounting_hole_wrench_thickness"]

        # ── Casing thickness ───────────────────────────────────────────────
        self.Motor_case_thickness                = self.design_params["Motor_case_thickness"]
        self.ring_gear_thickness_mounting_casing = self.design_params["ring_gear_thickness_mounting_casing"]

        # ── Driver mount (legacy – to be removed later) ────────────────────
        self.driver_mount_PCD                            = self.design_params["driver_mount_PCD"]
        self.driver_mount_hole_dia                       = self.design_params["driver_mount_hole_dia"]
        self.driver_mount_wrench_size                    = self.design_params["driver_mount_wrench_size"]
        self.driver_mount_wrench_thickness               = self.design_params["driver_mount_wrench_thickness"]
        self.case_mounting_wrench_size                   = self.design_params["case_mounting_wrench_size"]
        self.case_mounting_hole_allen_socket_dia         = self.design_params["case_mounting_hole_allen_socket_dia"]
        self.clearance_case_mount_holes_shell_thickness  = self.design_params["clearance_case_mount_holes_shell_thickness"]
        self.motor_case_mounting_hole_dia                = self.design_params["motor_case_mounting_hole_dia"]
        self.motor_case_wrench_size                      = self.design_params["motor_case_wrench_size"]
        self.central_hole_offset_from_motor_mount_PCD   = self.design_params["central_hole_offset_from_motor_mount_PCD"]
        self.driver_mount_thickness                      = self.design_params["driver_mount_thickness"]
        self.driver_mount_inserts_OD                     = self.design_params["driver_mount_inserts_OD"]
        self.driver_upper_holes_dist_from_center         = self.design_params["driver_upper_holes_dist_from_center"]
        self.driver_lower_holes_dist_from_center         = self.design_params["driver_lower_holes_dist_from_center"]
        self.driver_mount_height                         = self.design_params["driver_mount_height"]
        self.motor_mount_driver_hole_num                 = self.design_params["motor_mount_driver_hole_num"]
        self.driver_side_holes_dist_from_center          = self.design_params["driver_side_holes_dist_from_center"]

        # ── Derived / calculated variables ─────────────────────────────────

        # Sun hub diameter (capped at rotor OD with clearance)
        sun_hub_dia_calc = (self.rotor_mount_hole_PCD + self.rotor_mount_hole_dia
                            + self.standard_clearance_1_5mm * 4)
        cap              = self.Rotor_OD - self.standard_clearance_1_5mm * 2
        self.sun_hub_dia = cap if sun_hub_dia_calc > self.Rotor_OD else sun_hub_dia_calc

        # Carrier PCD and outer bearing selection
        self.carrier_PCD    = self.module * (self.Ns + self.Np_b)
        bearing_id_calc     = self.carrier_PCD + self.bearingIDClearance_3DP
        outer_bearing       = bearings_discrete(bearing_id_calc)
        self.bearing_ID     = outer_bearing.getBearingIDMM()
        self.bearing_OD     = outer_bearing.getBearingODMM()
        self.bearing_height = outer_bearing.getBearingWidthMM()

        # Sun face width (driven by geometry; floor applied when stator radial clearance is tight)
        fw_s_used_calc        = (self.standard_clearance_1_5mm * 2
                                 + self.sun_sec_carrier_bearing_height
                                 - (self.sun_bottom_casing_bearing_height + self.standard_clearance_1_5mm - self.sun_coupler_hub_thickness)
                                 + self.sec_carrier_thickness
                                 + self.clearance_planet
                                 + self.fw_p_s
                                 + self.fw_p_b)
        fw_s_used_floor       = self.motor_height
        stator_radial_clearance = (self.stator_ID - self.bearing_OD) / 2
        floor_applies         = stator_radial_clearance < self.standard_clearance_1_5mm * 2

        if floor_applies and fw_s_used_calc < fw_s_used_floor:
            self.fw_s_used = fw_s_used_floor
        else:
            self.fw_s_used = fw_s_used_calc

        # Total actuator axial width and ring OD
        self.actuator_width = (self.fw_s_used
                               + self.bearing_height
                               + self.sun_coupler_hub_thickness
                               + self.standard_clearance_1_5mm * 3.5
                               + self.sun_bottom_casing_bearing_height
                               + self.bearing_retainer_thickness)
        self.ring_OD        = self.stator_ID

    # ══════════════════════════════════════════════════════════════════════
    # CAD equation file generation
    # ══════════════════════════════════════════════════════════════════════
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
            f'"stator_top_rotor_top_offset"= {self.stator_top_rotor_top_offset}\n',
            f'"stator_hole_dia"= {self.stator_hole_dia}\n',
            f'"bearing_retainer_hole_dia"= {self.bearing_retainer_hole_dia}\n',
            f'"bearing_retainer_hole_num"= {self.bearing_retainer_hole_num}\n',
            f'"Rotor_ID"= {self.Rotor_ID}\n',
            f'"Rotor_OD"= {self.Rotor_OD}\n',
            f'"Rotor_height"= {self.Rotor_height}\n',
            f'"Rotor_bottom_ID"= {self.Rotor_bottom_ID}\n',
            f'"rotor_bottom_thickness"= {self.rotor_bottom_thickness}\n',
            f'"Rotor_csk_head_upper_dia"= {self.Rotor_csk_head_upper_dia}\n',
            f'"Rotor_csk_head_height"= {self.Rotor_csk_head_height}\n',
            f'"ring_gear_thickness_mounting_casing"= {self.ring_gear_thickness_mounting_casing}\n',
            f'"motor_casing_thickness"= {self.Motor_case_thickness}\n',
            f'"sun_sec_carrier_bearing_height"= {self.sun_sec_carrier_bearing_height}\n',
            f'"sun_sec_carrier_bearing_ID"= {self.sun_sec_carrier_bearing_ID}\n',
            f'"sun_sec_carrier_bearing_OD"= {self.sun_sec_carrier_bearing_OD}\n',
            f'"motor_height"= {self.motor_height}\n',
            f'"motor_stator_extrusion_dia"= {self.motor_stator_extrusion_dia}\n',
            f'"motor_stator_extrusion_depth"= {self.motor_stator_extrusion_depth}\n',
            f'"case_mounting_hole_dia"= {self.case_mounting_hole_dia}\n',
            f'"case_mounting_hole_wrench_size"= {self.case_mounting_hole_wrench_size}\n',
            f'"case_mounting_hole_wrench_thickness"= {self.case_mounting_hole_wrench_thickness}\n',
            f'"driver_mount_PCD"= {self.driver_mount_PCD}\n',
            f'"driver_mount_hole_dia"= {self.driver_mount_hole_dia}\n',
            f'"driver_mount_wrench_size"= {self.driver_mount_wrench_size}\n',
            f'"driver_mount_wrench_thickness"= {self.driver_mount_wrench_thickness}\n',
            f'"case_mounting_wrench_size"= {self.case_mounting_wrench_size}\n',
            f'"case_mounting_hole_allen_socket_dia"= {self.case_mounting_hole_allen_socket_dia}\n',
            f'"clearance_case_mount_holes_shell_thickness"= {self.clearance_case_mount_holes_shell_thickness}\n',
            f'"motor_case_mounting_hole_dia"= {self.motor_case_mounting_hole_dia}\n',
            f'"motor_case_wrench_size"= {self.motor_case_wrench_size}\n',
            f'"central_hole_offset_from_motor_mount_PCD"= {self.central_hole_offset_from_motor_mount_PCD}\n',
            f'"driver_mount_thickness"= {self.driver_mount_thickness}\n',
            f'"driver_mount_inserts_OD"= {self.driver_mount_inserts_OD}\n',
            f'"driver_upper_holes_dist_from_center"= {self.driver_upper_holes_dist_from_center}\n',
            f'"driver_lower_holes_dist_from_center"= {self.driver_lower_holes_dist_from_center}\n',
            f'"driver_mount_height"= {self.driver_mount_height}\n',
            f'"motor_mount_driver_hole_num"= {self.motor_mount_driver_hole_num}\n',
            f'"driver_side_holes_dist_from_center"= {self.driver_side_holes_dist_from_center}\n',
        ]

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

    # ══════════════════════════════════════════════════════════════════════
    # Gear tooth stress analysis methods  (logic unchanged)
    # ══════════════════════════════════════════════════════════════════════
    def getToothForces(self, constraintCheck=True):
        if constraintCheck:
            if not self.internalcompoundPlanetaryGearbox.geometricConstraint():
                print("Geometric constraint not satisfied"); return
            if not self.internalcompoundPlanetaryGearbox.meshingConstraint():
                print("Meshing constraint not satisfied"); return
            if not self.internalcompoundPlanetaryGearbox.noPlanetInterferenceConstraint():
                print("No planet interference constraint not satisfied"); return

        Ns          = self.internalcompoundPlanetaryGearbox.Ns
        NpBig       = self.internalcompoundPlanetaryGearbox.NpBig
        NpSmall     = self.internalcompoundPlanetaryGearbox.NpSmall
        Nr          = self.internalcompoundPlanetaryGearbox.Nr
        numPlanet   = self.internalcompoundPlanetaryGearbox.numPlanet

        Rs_Mt      = self.internalcompoundPlanetaryGearbox.getPCRadiusSunM()
        RpBig_Mt   = self.internalcompoundPlanetaryGearbox.getPCRadiusPlanetBigM()
        RpSmall_Mt = self.internalcompoundPlanetaryGearbox.getPCRadiusPlanetSmallM()
        Rr_Mt      = self.internalcompoundPlanetaryGearbox.getPCRadiusRingM()

        wSun     = self.motor.getMaxMotorAngVelRadPerSec()
        wPlanet  = (-Ns / (NpBig + NpSmall)) * wSun
        wCarrier = wSun / self.internalcompoundPlanetaryGearbox.gearRatio()

        Ft_sp = (self.serviceFactor * self.motor.getMaxMotorTorque()) / (numPlanet * Rs_Mt)
        Ft_rp = ((self.serviceFactor * self.motor.getMaxMotorTorque()) * RpBig_Mt
                 / (numPlanet * Rs_Mt * RpSmall_Mt))
        return [Ft_sp, Ft_rp]

    def lewisStressAnalysisMinFacewidth(self):
        if not self.internalcompoundPlanetaryGearbox.geometricConstraint():
            print("Geometric constraint not satisfied"); return
        if not self.internalcompoundPlanetaryGearbox.meshingConstraint():
            print("Meshing constraint not satisfied"); return
        if not self.internalcompoundPlanetaryGearbox.noPlanetInterferenceConstraint():
            print("No planet interference constraint not satisfied"); return

        Ns          = self.internalcompoundPlanetaryGearbox.Ns
        NpBig       = self.internalcompoundPlanetaryGearbox.NpBig
        NpSmall     = self.internalcompoundPlanetaryGearbox.NpSmall
        Nr          = self.internalcompoundPlanetaryGearbox.Nr
        numPlanet   = self.internalcompoundPlanetaryGearbox.numPlanet
        moduleBig   = self.internalcompoundPlanetaryGearbox.moduleBig
        moduleSmall = self.internalcompoundPlanetaryGearbox.moduleSmall

        wSun     = self.motor.getMaxMotorAngVelRadPerSec()
        wPlanet  = (-Ns / (NpBig + NpSmall)) * wSun
        wCarrier = wSun / self.internalcompoundPlanetaryGearbox.gearRatio()

        [Ft_sp, Ft_rp] = self.getToothForces(constraintCheck=False)

        ySun         = 0.154 - 0.912/Ns
        yPlanetBig   = 0.154 - 0.912/NpBig
        yPlanetSmall = 0.154 - 0.912/NpSmall
        yRing        = 0.154 - 0.912/Nr

        V_sp = (self.internalcompoundPlanetaryGearbox.getPCRadiusSunM() * wSun)
        V_rp = (wCarrier*(self.internalcompoundPlanetaryGearbox.getPCRadiusSunM() + self.internalcompoundPlanetaryGearbox.getPCRadiusPlanetBigM()) +
                wPlanet*(self.internalcompoundPlanetaryGearbox.getPCRadiusPlanetSmallM()))

        if V_sp <= 7.5:
            Kv_sun      = 3/(3+V_sp)
            Kv_planetBig = 3/(3+V_sp)
        else:
            Kv_sun      = 4.5/(4.5+V_sp)
            Kv_planetBig = 4.5/(4.5+V_sp)

        if V_rp <= 7.5:
            Kv_planetSmall = 3/(3+V_rp)
            Kv_ring        = 3/(3+V_rp)
        elif V_rp > 7.5 and V_rp <= 12.5:
            Kv_planetSmall = 4.5/(4.5+V_rp)
            Kv_ring        = 4.5/(4.5+V_rp)

        P_big   = np.pi * moduleBig   * 0.001
        P_small = np.pi * moduleSmall * 0.001

        bMin_sun         = (self.FOS * Ft_sp / (self.internalcompoundPlanetaryGearbox.maxGearAllowableStressPa * ySun         * Kv_sun         * P_big))
        bMin_planetBig   = (self.FOS * Ft_sp / (self.internalcompoundPlanetaryGearbox.maxGearAllowableStressPa * yPlanetBig   * Kv_planetBig   * P_big))
        bMin_planetSmall = (self.FOS * Ft_rp / (self.internalcompoundPlanetaryGearbox.maxGearAllowableStressPa * yPlanetSmall * Kv_planetSmall * P_small))
        bMin_ring        = (self.FOS * Ft_rp / (self.internalcompoundPlanetaryGearbox.maxGearAllowableStressPa * yRing        * Kv_ring        * P_small))

        if bMin_ring < bMin_planetSmall:
            bMin_ring = bMin_planetSmall
        else:
            bMin_planetSmall = bMin_ring

        self.internalcompoundPlanetaryGearbox.setfwSunMM        (bMin_sun         * 1000)
        self.internalcompoundPlanetaryGearbox.setfwPlanetBigMM  (bMin_planetBig   * 1000)
        self.internalcompoundPlanetaryGearbox.setfwPlanetSmallMM(bMin_planetSmall * 1000)
        self.internalcompoundPlanetaryGearbox.setfwRingMM       (bMin_ring        * 1000)

    def mitStressAnalysisMinFacewidth(self):
        if not self.internalcompoundPlanetaryGearbox.geometricConstraint():
            print("Geometric constraint not satisfied"); return
        if not self.internalcompoundPlanetaryGearbox.meshingConstraint():
            print("Meshing constraint not satisfied"); return
        if not self.internalcompoundPlanetaryGearbox.noPlanetInterferenceConstraint():
            print("No planet interference constraint not satisfied"); return

        Ns          = self.internalcompoundPlanetaryGearbox.Ns
        NpBig       = self.internalcompoundPlanetaryGearbox.NpBig
        NpSmall     = self.internalcompoundPlanetaryGearbox.NpSmall
        Nr          = self.internalcompoundPlanetaryGearbox.Nr
        numPlanet   = self.internalcompoundPlanetaryGearbox.numPlanet
        moduleBig   = self.internalcompoundPlanetaryGearbox.moduleBig
        moduleSmall = self.internalcompoundPlanetaryGearbox.moduleSmall

        wSun     = self.motor.getMaxMotorAngVelRadPerSec()
        wPlanet  = (-Ns / (NpBig + NpSmall)) * wSun
        wCarrier = wSun / self.internalcompoundPlanetaryGearbox.gearRatio()

        [Ft_sp, Ft_rp] = self.getToothForces(constraintCheck=False)

        _, _, CR_SP = self.internalcompoundPlanetaryGearbox.contactRatio_sunPlanet()
        _, _, CR_PR = self.internalcompoundPlanetaryGearbox.contactRatio_planetRing()

        qe1 = 1 / CR_SP
        qe2 = 1 / CR_PR

        qk1 = (7.65734266e-08 * Ns**4    - 2.19500130e-05 * Ns**3
             + 2.33893357e-03 * Ns**2    - 1.13320908e-01 * Ns    + 4.44727778)
        qk2 = (7.65734266e-08 * NpSmall**4 - 2.19500130e-05 * NpSmall**3
             + 2.33893357e-03 * NpSmall**2 - 1.13320908e-01 * NpSmall + 4.44727778)

        bMin_sun_mit         = (self.FOS * Ft_sp * qe1 * qk1 / (self.internalcompoundPlanetaryGearbox.maxGearAllowableStressPa * moduleBig   * 0.001))
        bMin_planetBig_mit   = (self.FOS * Ft_sp * qe1 * qk1 / (self.internalcompoundPlanetaryGearbox.maxGearAllowableStressPa * moduleBig   * 0.001))
        bMin_planetSmall_mit = (self.FOS * Ft_rp * qe2 * qk2 / (self.internalcompoundPlanetaryGearbox.maxGearAllowableStressPa * moduleSmall * 0.001))
        bMin_ring_mit        = (self.FOS * Ft_rp * qe2 * qk2 / (self.internalcompoundPlanetaryGearbox.maxGearAllowableStressPa * moduleSmall * 0.001))

        # Minimum face width constrained by planet bearing accommodation
        if ((bMin_planetBig_mit + bMin_planetSmall_mit) * 1000 < (self.planet_bearing_width*2 + self.standard_clearance_1_5mm * 2 / 3)):
            if (bMin_planetBig_mit   * 1000 < (self.planet_bearing_width + self.standard_clearance_1_5mm * 1 / 3)):
                bMin_planetBig_mit   = (self.planet_bearing_width + self.standard_clearance_1_5mm * 1 / 3) / 1000
            if (bMin_planetSmall_mit * 1000 < (self.planet_bearing_width + self.standard_clearance_1_5mm * 1 / 3)):
                bMin_planetSmall_mit = (self.planet_bearing_width + self.standard_clearance_1_5mm * 1 / 3) / 1000
            bMin_ring_mit = bMin_planetSmall_mit

        self.internalcompoundPlanetaryGearbox.setfwSunMM        (bMin_sun_mit         * 1000)
        self.internalcompoundPlanetaryGearbox.setfwPlanetBigMM  (bMin_planetBig_mit   * 1000)
        self.internalcompoundPlanetaryGearbox.setfwPlanetSmallMM(bMin_planetSmall_mit * 1000)
        self.internalcompoundPlanetaryGearbox.setfwRingMM       (bMin_ring_mit        * 1000)

        return (bMin_sun_mit         * 1000,
                bMin_planetBig_mit   * 1000,
                bMin_planetSmall_mit * 1000,
                bMin_ring_mit        * 1000)

    def AGMAStressAnalysisMinFacewidth(self):
        if not self.internalcompoundPlanetaryGearbox.geometricConstraint():
            print("Geometric constraint not satisfied"); return
        if not self.internalcompoundPlanetaryGearbox.meshingConstraint():
            print("Meshing constraint not satisfied"); return
        if not self.internalcompoundPlanetaryGearbox.noPlanetInterferenceConstraint():
            print("No planet interference constraint not satisfied"); return

        Ns            = self.internalcompoundPlanetaryGearbox.Ns
        NpBig         = self.internalcompoundPlanetaryGearbox.NpBig
        NpSmall       = self.internalcompoundPlanetaryGearbox.NpSmall
        Nr            = self.internalcompoundPlanetaryGearbox.Nr
        numPlanet     = self.internalcompoundPlanetaryGearbox.numPlanet
        moduleBig     = self.internalcompoundPlanetaryGearbox.moduleBig
        moduleSmall   = self.internalcompoundPlanetaryGearbox.moduleSmall
        pressureAngle = self.internalcompoundPlanetaryGearbox.pressureAngleDEG

        wSun     = self.motor.getMaxMotorAngVelRadPerSec()
        wPlanet  = (-Ns / (NpBig + NpSmall)) * wSun
        wCarrier = wSun / self.internalcompoundPlanetaryGearbox.gearRatio()

        [Wt_sp, Wt_rp] = self.getToothForces(constraintCheck=False)

        # Lewis form factor Y = pi*y (pressure angle = 20°)
        Y_sun         = (0.154 - 0.912/Ns)     * np.pi
        Y_planetBig   = (0.154 - 0.912/NpBig)  * np.pi
        Y_planetSmall = (0.154 - 0.912/NpSmall) * np.pi
        Y_ring        = (0.154 - 0.912/Nr)      * np.pi

        V_sp = abs(self.internalcompoundPlanetaryGearbox.getPCRadiusSunM() * wSun)
        V_rp = abs(wCarrier*(self.internalcompoundPlanetaryGearbox.getPCRadiusSunM() + self.internalcompoundPlanetaryGearbox.getPCRadiusPlanetBigM()) +
                   wPlanet*(self.internalcompoundPlanetaryGearbox.getPCRadiusPlanetSmallM()))

        # AGMA 908-B89: fatigue stress concentration factors
        H = 0.331 - (0.436 * np.pi * pressureAngle / 180)
        L = 0.324 - (0.492 * np.pi * pressureAngle / 180)
        M = 0.261 + (0.545 * np.pi * pressureAngle / 180)

        t_planetSmall = (13.5 * Y_planetSmall)**(1/2) * moduleSmall
        r_planetSmall = 0.3  * moduleSmall
        l_planetSmall = 2.25 * moduleSmall
        Kf_planetSmall = H + (t_planetSmall/r_planetSmall)**(L) * (t_planetSmall/l_planetSmall)**(M)

        t_planetBig = (13.5 * Y_planetBig)**(1/2) * moduleBig
        r_planetBig = 0.3  * moduleBig
        l_planetBig = 2.25 * moduleBig
        Kf_planetBig = H + (t_planetBig/r_planetBig)**(L) * (t_planetBig/l_planetBig)**(M)

        t_sun = (13.5 * Y_sun)**(1/2) * moduleBig
        r_sun = 0.3  * moduleBig
        l_sun = 2.25 * moduleBig
        Kf_sun = H + (t_sun/r_sun)**(L) * (t_sun/l_sun)**(M)

        t_ring = (13.5 * Y_ring)**(1/2) * moduleSmall
        r_ring = 0.3  * moduleSmall
        l_ring = 2.25 * moduleSmall
        Kf_ring = H + (t_ring/r_ring)**(L) * (t_ring/l_ring)**(M)

        Yj_planetSmall = Y_planetSmall / Kf_planetSmall
        Yj_planetBig   = Y_planetBig   / Kf_planetBig
        Yj_sun         = Y_sun         / Kf_sun
        Yj_ring        = Y_ring        / Kf_ring

        Qv = 7  # commercial-quality gears (AGMA quality 3–7)
        B  = 0.25*(12-Qv)**(2/3)
        A  = 50 + 56*(1-B)

        Kv_planetSmall = ((A+np.sqrt(200*V_rp))/A)**B
        Kv_planetBig   = ((A+np.sqrt(200*V_sp))/A)**B
        Kv_sun         = ((A+np.sqrt(200*V_sp))/A)**B
        Kv_ring        = ((A+np.sqrt(200*V_rp))/A)**B

        Ks = 1    # size factor (insufficient data)
        Kh = 1.3  # load-distribution factor (less rigid mounting, less accurate gears)
        Kb = 1    # rim-thickness factor (uniform thickness)

        bMin_planetSmall = (self.FOS * Wt_rp * Kv_planetSmall * Ks * Kh * Kb) / (moduleSmall * Yj_planetSmall * self.internalcompoundPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        bMin_planetBig   = (self.FOS * Wt_sp * Kv_planetBig   * Ks * Kh * Kb) / (moduleBig   * Yj_planetBig   * self.internalcompoundPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        bMin_sun         = (self.FOS * Wt_sp * Kv_sun         * Ks * Kh * Kb) / (moduleBig   * Yj_sun         * self.internalcompoundPlanetaryGearbox.maxGearAllowableStressPa * 0.001)
        bMin_ring        = (self.FOS * Wt_rp * Kv_ring        * Ks * Kh * Kb) / (moduleSmall * Yj_ring        * self.internalcompoundPlanetaryGearbox.maxGearAllowableStressPa * 0.001)

        if bMin_ring < bMin_planetSmall:
            bMin_ring = bMin_planetSmall
        else:
            bMin_planetSmall = bMin_ring

        self.internalcompoundPlanetaryGearbox.setfwSunMM        (bMin_sun         * 1000)
        self.internalcompoundPlanetaryGearbox.setfwPlanetBigMM  (bMin_planetBig   * 1000)
        self.internalcompoundPlanetaryGearbox.setfwPlanetSmallMM(bMin_planetSmall * 1000)
        self.internalcompoundPlanetaryGearbox.setfwRingMM       (bMin_ring        * 1000)

    def updateFacewidth(self):
        if   self.stressAnalysisMethodName == "Lewis": self.lewisStressAnalysisMinFacewidth()
        elif self.stressAnalysisMethodName == "AGMA":  self.AGMAStressAnalysisMinFacewidth()
        elif self.stressAnalysisMethodName == "MIT":   self.mitStressAnalysisMinFacewidth()

    # ══════════════════════════════════════════════════════════════════════
    # getMassKG_3DP  –  full 3D-printed actuator mass breakdown
    # ══════════════════════════════════════════════════════════════════════
    def getMassKG_3DP(self):
        """
        Computes total actuator mass (motor + gearbox).

        Each component's geometry is built up step-by-step:
          1. Unit-converted face widths
          2. Planet gear
          3. Sun gear
          4. Secondary carrier
          5. Main carrier
          6. Ring gear
          7. Motor casing
          8. Bearing masses
          9. Component masses → gearbox mass → total mass
        """
        self.setVariables()  # refresh all derived parameters

        density_steel = self.internalcompoundPlanetaryGearbox.densityGears     # kg/m³ steel
        density_alum  = self.internalcompoundPlanetaryGearbox.densityStructure  # kg/m³ aluminium

        # ── Face widths converted from mm to m ─────────────────────────────
        fw_sun_m          = self.fw_s_used / 1000
        fw_planet_big_m   = self.fw_p_b    / 1000
        fw_planet_small_m = self.fw_p_s    / 1000
        fw_ring_m         = (self.fw_r + self.standard_clearance_1_5mm * 2) / 1000

        # ── Small bearing masses (placeholder estimates) ────────────────────
        sun_shaft_bearing_mass        = 4 * 0.001   # 4 small bearings × 1 g each
        planet_bearing_mass_each      = 1 * 0.001   # 1 g per planet bearing
        planet_bearing_count          = self.num_planet * 2
        planet_bearing_combined_mass  = planet_bearing_mass_each * planet_bearing_count

        # ══════════════════════════════════════════════════════════════════
        # 1. PLANET GEAR
        # ══════════════════════════════════════════════════════════════════
        # Radii
        r_planet_big_pitch   = (self.Np_b * self.module / 2) / 1000   # big lobe pitch radius
        r_planet_small_pitch = (self.Np_s * self.module / 2) / 1000   # small lobe pitch radius
        r_planet_bore        = (self.planet_bore / 2)        / 1000   # central through-bore
        r_planet_bearing_OD  = (self.planet_bearing_OD / 2)  / 1000   # bearing seat outer radius

        # Face widths
        fw_planet_bearing_m  = self.planet_bearing_width / 1000
        fw_planet_total_m    = fw_planet_big_m + fw_planet_small_m    # combined lobe width

        # Volume sub-components
        vol_planet_big_lobe   = math.pi * fw_planet_big_m   * r_planet_big_pitch   ** 2
        vol_planet_small_lobe = math.pi * fw_planet_small_m * r_planet_small_pitch ** 2
        vol_planet_bore       = math.pi * fw_planet_total_m * r_planet_bore        ** 2
        vol_planet_bearing    = math.pi * fw_planet_bearing_m * (r_planet_bearing_OD**2 - r_planet_bore**2)

        vol_planet_net = (vol_planet_big_lobe + vol_planet_small_lobe
                          - vol_planet_bore
                          - 2 * vol_planet_bearing)

        # ══════════════════════════════════════════════════════════════════
        # 2. SUN GEAR
        # ══════════════════════════════════════════════════════════════════
        # Radii
        r_sun_pitch         = (self.Ns * self.module / 2)                                   / 1000
        r_sun_base_coupler  = (self.sun_bottom_casing_bearing_ID / 2)                       / 1000
        r_sun_bore          = (self.sun_central_bolt_dia / 2)                               / 1000
        r_sun_removed       = ((self.Rotor_bottom_ID - self.standard_clearance_1_5mm * 4) / 2) / 1000
        r_sun_support_outer = (self.sun_sec_carrier_bearing_ID / 2)                         / 1000

        # Face widths
        fw_sun_base_m     = (self.sun_bottom_casing_bearing_height + self.standard_clearance_1_5mm) / 1000
        fw_sun_removed_m  = (self.sun_bottom_casing_bearing_height + self.standard_clearance_1_5mm
                             - self.sun_coupler_hub_thickness) / 1000
        fw_sun_support_m  = (self.sec_carrier_thickness - self.standard_clearance_1_5mm) / 1000
        fw_sun_total_m    = fw_sun_m + fw_sun_base_m          # teeth + base flange

        # Radii for removed pocket inner wall
        r_sun_sec_carrier_bearing_inner = (self.sun_sec_carrier_bearing_ID / 2) / 1000

        # Volume sub-components
        vol_sun_teeth          = math.pi * fw_sun_m          * r_sun_pitch         ** 2
        vol_sun_base_flange    = math.pi * fw_sun_base_m     * r_sun_base_coupler  ** 2
        vol_sun_bore           = math.pi * fw_sun_total_m    * r_sun_bore          ** 2
        vol_sun_removed_pocket = math.pi * fw_sun_removed_m  * (r_sun_removed**2 - r_sun_sec_carrier_bearing_inner**2)
        vol_sun_support_bulge  = math.pi * fw_sun_support_m  * (r_sun_support_outer**2 - r_sun_bore**2)

        vol_sun_net = (vol_sun_teeth + vol_sun_base_flange
                       - vol_sun_bore
                       - vol_sun_removed_pocket
                       + vol_sun_support_bulge)

        # ══════════════════════════════════════════════════════════════════
        # 3. SECONDARY CARRIER
        # ══════════════════════════════════════════════════════════════════
        # Radii
        r_sec_carrier_inner = ( (self.carrier_PCD / 2)
                                - (self.planet_shaft_dia + self.planet_shaft_step_offset) / 2
                                - self.standard_clearance_1_5mm ) / 1000
        r_sec_carrier_outer = (self.bearing_ID / 2 + self.standard_clearance_1_5mm / 2) / 1000

        r_sec_carrier_sun_support_ID = (self.sun_sec_carrier_bearing_ID / 2) / 1000
        w_sec_carrier_sun_support    = (self.standard_clearance_1_5mm * 4) / 1000   # radial wall width
        r_sec_carrier_sun_support_OD = r_sec_carrier_sun_support_ID + w_sec_carrier_sun_support

        # Face widths
        fw_sec_carrier_m            = self.sec_carrier_thickness / 1000
        fw_sec_carrier_sun_support_m = (self.fw_s_used + self.sun_bottom_casing_bearing_height
                                        + self.standard_clearance_1_5mm
                                        - self.sun_coupler_hub_thickness
                                        - self.fw_p_s - self.fw_p_b
                                        - self.clearance_planet
                                        - self.sec_carrier_thickness) / 1000

        # Volume sub-components
        vol_sec_carrier_disk        = math.pi * fw_sec_carrier_m * (r_sec_carrier_outer**2 - r_sec_carrier_inner**2)
        vol_sec_carrier_sun_support = math.pi * fw_sec_carrier_sun_support_m * (r_sec_carrier_sun_support_OD**2 - r_sec_carrier_sun_support_ID**2)

        vol_sec_carrier_net = vol_sec_carrier_disk + vol_sec_carrier_sun_support

        # ══════════════════════════════════════════════════════════════════
        # 4. MAIN CARRIER
        # ══════════════════════════════════════════════════════════════════
        # Radii
        r_carrier_outer     = (self.bearing_ID / 2) / 1000
        r_carrier_trapezoid = ((self.bearing_ID
                                - (self.Ns * self.module + 2 * self.carrier_trapezoidal_support_sun_offset))
                               / 4) / 1000

        # Face width (same as combined planet lobe span)
        fw_carrier_total_m = fw_planet_big_m + fw_planet_small_m

        # Volume sub-components
        vol_carrier_disk      = math.pi * (self.bearing_height / 1000) * r_carrier_outer     ** 2
        vol_carrier_trapezoid = math.pi * fw_carrier_total_m           * r_carrier_trapezoid ** 2

        vol_carrier_net = vol_carrier_disk + 3 * vol_carrier_trapezoid   # 3 trapezoidal arms

        # ══════════════════════════════════════════════════════════════════
        # 5. RING GEAR
        # ══════════════════════════════════════════════════════════════════
        # Radii
        r_ring_pitch          = (self.Nr * self.module / 2) / 1000
        r_ring_outer          = (self.stator_ID / 2) / 1000
        r_ring_mounting_outer = ((self.Rotor_OD + self.standard_clearance_1_5mm
                                  + self.Motor_case_thickness * 2) / 2) / 1000
        r_ring_bearing_inner  = (self.bearing_OD / 2) / 1000
        r_ring_bearing_outer  = ((self.stator_mounting_holes_PCD
                                  + self.standard_clearance_1_5mm * 5) / 2) / 1000

        # Face widths (all in m)
        fw_ring_mounting_m = self.ring_gear_thickness_mounting_casing / 1000
        fw_ring_teeth_m    = (fw_ring_m
                              - (self.fw_s_used - self.rotor_bottom_thickness
                                 - self.stator_height - self.ring_gear_thickness_mounting_casing) / 1000)
        fw_ring_bearing_m  = (self.bearing_height + self.tight_clearance_3DP) / 1000
        fw_ring_middle_m   = (self.carrier_bearing_step_width + self.clearance_planet
                              + self.fw_s_used - self.rotor_bottom_thickness
                              - self.stator_height - self.ring_gear_thickness_mounting_casing) / 1000
        fw_ring_bolt_m     = (self.ring_gear_thickness_mounting_casing + 3) / 1000  # bolt boss height

        # Volume sub-components
        vol_ring_teeth          = math.pi * fw_ring_teeth_m    * (r_ring_outer**2          - r_ring_pitch**2)
        vol_ring_mounting_flange = math.pi * fw_ring_mounting_m * (r_ring_mounting_outer**2  - r_ring_outer**2)
        vol_ring_bearing_support = math.pi * fw_ring_bearing_m  * (r_ring_bearing_outer**2   - r_ring_bearing_inner**2)
        vol_ring_middle_section  = math.pi * fw_ring_middle_m   * (r_ring_bearing_outer**2   - r_ring_pitch**2)
        vol_ring_bolt_bosses     = 6 * math.pi * fw_ring_bolt_m * ((7.5/2000)**2 - (3/2000)**2)

        vol_ring_net = (vol_ring_teeth + vol_ring_mounting_flange
                        + vol_ring_bearing_support + vol_ring_middle_section
                        + vol_ring_bolt_bosses)

        # ══════════════════════════════════════════════════════════════════
        # 6. MOTOR CASING
        # ══════════════════════════════════════════════════════════════════
        # Radii
        r_casing_inner          = ((self.Rotor_OD + self.standard_clearance_1_5mm * 4) / 2) / 1000
        r_casing_outer          = r_casing_inner + (self.Motor_case_thickness / 1000)
        r_casing_bearing_recess = 10 / 1000   # fixed inner radius of central bearing recess

        # Face widths
        fw_casing_wall_m         = (self.motor_height + self.sun_bottom_casing_bearing_height
                                    + self.loose_clearance_3DP + self.standard_clearance_1_5mm) / 1000
        fw_casing_bearing_bulge_m = (self.sun_bottom_casing_bearing_height + self.loose_clearance_3DP) / 1000
        fw_casing_bottom_m        = self.Motor_case_thickness / 1000

        r_casing_bearing_seat_OD = (self.sun_bottom_casing_bearing_OD / 2) / 1000  # bearing pocket outer r

        # Volume sub-components
        vol_casing_wall          = math.pi * fw_casing_wall_m          * (r_casing_outer**2  - r_casing_inner**2)
        vol_casing_bottom_disk   = math.pi * fw_casing_bottom_m        * (r_casing_outer**2  - r_casing_bearing_recess**2)
        vol_casing_bolt_bosses   = 6 * math.pi * (fw_casing_wall_m + fw_casing_bottom_m) * ((7.5/2000)**2 - (3/2000)**2)
        vol_casing_bearing_bulge = math.pi * fw_casing_bearing_bulge_m * (r_casing_inner**2  - r_casing_bearing_seat_OD**2)

        vol_casing_net = (vol_casing_wall + vol_casing_bottom_disk
                          + vol_casing_bolt_bosses + vol_casing_bearing_bulge)

        # ══════════════════════════════════════════════════════════════════
        # 7. BEARING MASSES
        # ══════════════════════════════════════════════════════════════════
        outer_bearing_lookup  = bearings_discrete(self.bearing_ID)
        outer_bearing_mass    = outer_bearing_lookup.getBearingMassKG()

        self.sun_shaft_bearing_mass       = sun_shaft_bearing_mass
        self.planet_bearing_combined_mass = planet_bearing_combined_mass

        self.bearing_mass = (outer_bearing_mass
                             + self.sun_bottom_casing_bearing_massKG * 2   # 2 bottom-casing bearings
                             + self.planet_bearing_combined_mass
                             + self.sun_shaft_bearing_mass)

        # ══════════════════════════════════════════════════════════════════
        # 8. COMPONENT MASSES
        # ══════════════════════════════════════════════════════════════════
        planet_mass       = self.num_planet * vol_planet_net  * density_steel
        sun_gear_mass     = vol_sun_net                       * density_steel
        ring_gear_mass    = vol_ring_net                      * density_steel
        sec_carrier_mass  = vol_sec_carrier_net               * density_alum
        carrier_mass      = vol_carrier_net                   * density_alum
        motor_casing_mass = vol_casing_net                    * density_alum

        # ══════════════════════════════════════════════════════════════════
        # 9. TOTAL GEARBOX MASS  (store breakdown for reporting)
        # ══════════════════════════════════════════════════════════════════
        gearbox_mass_kg = (planet_mass
                           + sun_gear_mass
                           + ring_gear_mass
                           + sec_carrier_mass
                           + carrier_mass
                           + motor_casing_mass
                           + self.bearing_mass)

        # Store per-component masses for printVolumeAndMassParameters()
        self.planet_mass_kg       = planet_mass
        self.sun_gear_mass_kg     = sun_gear_mass
        self.ring_gear_mass_kg    = ring_gear_mass
        self.sec_carrier_mass_kg  = sec_carrier_mass
        self.carrier_mass_kg      = carrier_mass
        self.motor_casing_mass_kg = motor_casing_mass
        self.gearbox_mass_kg      = gearbox_mass_kg
        self.total_sum_except_motor_and_baering = (planet_mass + sun_gear_mass + ring_gear_mass
                                                   + sec_carrier_mass + carrier_mass + motor_casing_mass)

        return self.motorMassKG + gearbox_mass_kg

    # ── Print helpers ──────────────────────────────────────────────────────
    def printParameters(self):
        print("Ns = ",                           self.Ns)
        print("Np_b = ",                         self.Np_b)
        print("Np_s = ",                         self.Np_s)
        print("Nr = ",                           self.Nr)
        print("Module = ",                       self.module)
        print("Number of planets = ",            self.num_planet)
        print("Face width of sun gear = ",       round(self.fw_s_used, 2), " mm")
        print("Face width of Big planet = ",     round(self.fw_p_b,    2), " mm")
        print("Face width of Small planet = ",   round(self.fw_p_s,    2), " mm")
        print("Mass of the gearbox = ",          round(self.gearbox_mass_kg, 3), " kg")
        print("Efficiency = ",                   round(self.getEfficiency(), 4))
        print("--------------------------------------------------------------------------")

    def printParametersLess(self):
        vars_ = [self.module, self.Ns, self.Np_b, self.Np_s, self.Nr, self.num_planet]
        print("[m, Ns, NpB, NpS, Nr, numPl]:", vars_)
        print("Gear ratio = ",        self.gearRatio())
        print("Efficiency = ",        round(self.getEfficiency(), 4))
        print("Mass (gearbox) = ",    round(self.gearbox_mass_kg, 3), " kg")
        print("--------------------------------------------------------------------------")

    def printVolumeAndMassParameters(self):
        print("── Mass Breakdown (kg) ─────────────────────────────────")
        print("Sun Gear:         ", round(self.sun_gear_mass_kg,     4))
        print("Planets:          ", round(self.planet_mass_kg,       4))
        print("Ring Gear:        ", round(self.ring_gear_mass_kg,    4))
        print("Main Carrier:     ", round(self.carrier_mass_kg,      4))
        print("Secondary Carrier:", round(self.sec_carrier_mass_kg,  4))
        print("Motor Casing:     ", round(self.motor_casing_mass_kg, 4))
        print("Bearings:         ", round(self.bearing_mass,         4))
        print("--------------------------------------------------------------------------")

        total_actuator_mass = self.gearbox_mass_kg + self.motorMassKG
        print("GEARBOX ONLY:  ", round(self.gearbox_mass_kg,   3), " kg")
        print("MOTOR ONLY:    ", round(self.motorMassKG,        3), " kg")
        print("TOTAL ACTUATOR:", round(total_actuator_mass,     3), " kg")
        print("--------------------------------------------------------------------------")

    def print_mass_of_parts_3DP(self):
        print(f"Motor mass: {1000 * self.motorMassKG:.2f} g")
        print("---------------------------------------------------")

    # ── Delegated helpers ──────────────────────────────────────────────────
    def getEfficiency(self): return self.internalcompoundPlanetaryGearbox.getEfficiency()
    def gearRatio(self):     return self.internalcompoundPlanetaryGearbox.gearRatio()


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  OPTIMIZATION OF INTERNAL COMPOUND PLANETARY ACTUATOR                   ║
# ╚══════════════════════════════════════════════════════════════════════════╝
class optimizationInternalCompoundPlanetaryActuator:
    # NOTE: All optimisation logic is intentionally unchanged.
    #       Section comments have been added for navigation only.

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

        # ── Objective weights ──────────────────────────────────────────────
        self.K_Mass  = K_Mass
        self.K_Eff   = K_Eff
        self.K_Width = K_Width

        # ── Search space bounds ────────────────────────────────────────────
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

        # ── State tracking ─────────────────────────────────────────────────
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

    # ── Reporting ──────────────────────────────────────────────────────────
    def printOptimizationParameters(self, Actuator=internalcompoundPlanetaryActuator, log=1, csv=0):
        maxMotorAngVelRPM       = Actuator.motor.getMaxMotorAngVelRPM()
        maxMotorAngVelRadPerSec = Actuator.motor.getMaxMotorAngVelRadPerSec()
        maxMotorTorque          = Actuator.motor.getMaxMotorTorque()
        maxMotorPower           = Actuator.motor.getMaxMotorPower()
        motorMass               = Actuator.motor.getMassKG()
        motorDia                = Actuator.motor.getRotorODMM()
        motorLength             = Actuator.motor.getStatorHeightMM()
        maxGearAllowableStressMPa = Actuator.internalcompoundPlanetaryGearbox.maxGearAllowableStressMPa
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
            iter_           = self.iter
            gearRatio       = Actuator.internalcompoundPlanetaryGearbox.gearRatio()
            moduleBig       = Actuator.internalcompoundPlanetaryGearbox.moduleBig
            moduleSmall     = Actuator.internalcompoundPlanetaryGearbox.moduleSmall
            Ns              = Actuator.internalcompoundPlanetaryGearbox.Ns
            NpBig           = Actuator.internalcompoundPlanetaryGearbox.NpBig
            NpSmall         = Actuator.internalcompoundPlanetaryGearbox.NpSmall
            Nr              = Actuator.internalcompoundPlanetaryGearbox.Nr
            numPlanet       = Actuator.internalcompoundPlanetaryGearbox.numPlanet
            fwSunMM         = round(Actuator.internalcompoundPlanetaryGearbox.fwSunMM,        3)
            fwPlanetBigMM   = round(Actuator.internalcompoundPlanetaryGearbox.fwPlanetBigMM,  3)
            fwPlanetSmallMM = round(Actuator.internalcompoundPlanetaryGearbox.fwPlanetSmallMM,3)
            fwRingMM        = round(Actuator.internalcompoundPlanetaryGearbox.fwRingMM,       3)

            if self.UsePSCasVariable == 1:
                try:
                    Opt_PSC_ring      = self.cspgOpt.model.PSCr.value
                    Opt_PSC_planetBig = self.cspgOpt.model.PSCp1.value
                    Opt_PSC_planetSmall = self.cspgOpt.model.PSCp2.value
                    Opt_PSC_sun       = self.cspgOpt.model.PSCs.value
                    CenterDist_SP, CenterDist_PR = self.cspgOpt.getCenterDistance(Var=False)
                except:
                    Opt_PSC_ring = Opt_PSC_planetBig = Opt_PSC_planetSmall = Opt_PSC_sun = 0
                    CenterDist_SP = ((Ns + NpBig)    / 2) * moduleBig
                    CenterDist_PR = ((Nr - NpSmall)  / 2) * moduleSmall
            else:
                Opt_PSC_ring = Opt_PSC_planetBig = Opt_PSC_planetSmall = Opt_PSC_sun = 0
                CenterDist_SP = ((Ns + NpBig)   / 2) * moduleBig
                CenterDist_PR = ((Nr - NpSmall) / 2) * moduleSmall

            mass           = round(Actuator.getMassKG_3DP(), 3)
            eff            = round(Actuator.internalcompoundPlanetaryGearbox.getEfficiency(), 3)
            peakTorque     = round(Actuator.motor.getMaxMotorTorque()
                                   * Actuator.internalcompoundPlanetaryGearbox.gearRatio(), 3)
            tooth_forces   = Actuator.getToothForces()
            Torque_Density = round(peakTorque / mass, 3)

            if self.UsePSCasVariable == 1:
                try:
                    eff = round(self.cspgOpt.getEfficiency(Var=False), 3)
                except:
                    pass

            Cost               = self.cost(Actuator=Actuator)
            Outer_Bearing_mass = Actuator.bearing_mass
            Actuator_width     = Actuator.actuator_width

            print(iter_, ",", gearRatio, ",", moduleBig, ",", moduleSmall, ",", Ns, ",", NpBig, ",",
                  NpSmall, ",", Nr, ",", numPlanet, ",", fwSunMM, ",", fwPlanetBigMM, ",",
                  fwPlanetSmallMM, ",", fwRingMM, ",", mass, ",", eff, ",", peakTorque, ",",
                  Cost, ",", Torque_Density, ",", Outer_Bearing_mass, ",", Actuator_width)

    # ── Public entry point ─────────────────────────────────────────────────
    def optimizeActuator(self, Actuator=internalcompoundPlanetaryActuator,
                         UsePSCasVariable=0, log=1, csv=0, printOptParams=1, gearRatioReq=0):
        self.UsePSCasVariable = UsePSCasVariable
        self.gearRatioReq     = gearRatioReq
        opt_parameters        = None

        if   UsePSCasVariable == 0:
            totalTime, opt_parameters = self.optimizeActuatorWithoutPSC(
                Actuator=Actuator, log=log, csv=csv, printOptParams=printOptParams)
        elif UsePSCasVariable == 1:
            totalTime = self.optimizeActuatorWithPSC(Actuator=Actuator, log=log, csv=csv)
        else:
            totalTime = 0
            print('ERROR: "UsePSCasVariable" can be either 0 or 1')

        return totalTime, opt_parameters

    # ── Brute-force search (no PSC variable) ──────────────────────────────
    def optimizeActuatorWithoutPSC(self, Actuator=internalcompoundPlanetaryActuator,
                                   log=1, csv=0, printOptParams=1):
        startTime      = time.time()
        opt_parameters = None
        if csv and log:
            log, csv = 0, 1
        elif not csv and not log:
            log, csv = 0, 1
            
        output_dir = os.path.join(os.path.dirname(__file__), 'results', f'results_BruteForce_{Actuator.motor.motorName}')
        os.makedirs(output_dir, exist_ok=True)
        
        if csv:
            fileName = os.path.join(output_dir, f"ICPG_BRUTEFORCE_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}.csv")
        elif log:
            fileName = os.path.join(output_dir, f"ICPG_BRUTEFORCE_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}_LOG.txt")

        with open(fileName, "w") as file1:
            sys.stdout = file1
            if printOptParams:
                self.printOptimizationParameters(Actuator, log, csv)
                print(" ")

            if self.gearRatioReq != 0:
                self.GEAR_RATIO_MIN = self.gearRatioReq - self.GEAR_RATIO_STEP / 2
                self.GEAR_RATIO_MAX = self.gearRatioReq + (self.GEAR_RATIO_STEP / 2 - 1e-6)

            self.gearRatioIter = self.GEAR_RATIO_MIN
            if log:
                print("*****************************************************************")
                print("FOR MINIMUM GEAR RATIO ", self.gearRatioIter)
                print("*****************************************************************\n")
            elif csv:
                print("iter, gearRatio, moduleBig, moduleSmall, Ns, NpBig, NpSmall, Nr, numPlanet, "
                      "fwSunMM, fwPlanetBigMM, fwPanetSmallMM, fwRingMM, mass, eff, peakTorque, "
                      "Cost, Torque_Density, Outer_Bearing_mass, Actuator_width")

            gb = Actuator.internalcompoundPlanetaryGearbox  # shorthand

            while self.gearRatioIter <= self.GEAR_RATIO_MAX:
                opt_done  = 0
                self.iter = 0
                self.Cost = 100000
                MinCost   = self.Cost

                gb.setModuleBig(self.MODULE_BIG_MIN)
                while gb.moduleBig <= self.MODULE_BIG_MAX:

                    gb.setModuleSmall(self.MODULE_SMALL_MIN)
                    while gb.moduleSmall <= self.MODULE_SMALL_MAX:

                        gb.setNs(self.NUM_TEETH_SUN_MIN)
                        while (2 * gb.getPCRadiusSunM() * 1000) <= Actuator.maxGearboxDiameter:

                            gb.setNpBig(self.NUM_TEETH_PLANET_BIG_MIN)
                            while (2 * gb.getPCRadiusPlanetBigM() * 1000) <= Actuator.maxGearboxDiameter / 2:

                                gb.setNpSmall(self.NUM_TEETH_PLANET_SMALL_MIN)
                                while (2 * gb.getPCRadiusPlanetSmallM() * 1000) <= Actuator.maxGearboxDiameter / 2:

                                    gb.setNr(gb.NpSmall + gb.NpBig + gb.Ns)
                                    if (gb.getGearboxOuterDiaMaxM() * 1000) <= Actuator.maxGearboxDiameter:

                                        gb.setNumPlanet(self.NUM_PLANET_MIN)
                                        while gb.numPlanet <= self.NUM_PLANET_MAX:

                                            if (gb.geometricConstraint()
                                                    and gb.meshingConstraint()
                                                    and gb.noPlanetInterferenceConstraint()):
                                                self.totalFeasibleGearboxes += 1

                                                if (gb.gearRatio() >= self.gearRatioIter - 1e-6
                                                        and gb.gearRatio() <= self.gearRatioIter + self.GEAR_RATIO_STEP + 1e-6):
                                                    self.totalGearboxesWithReqGR += 1
                                                    Actuator.updateFacewidth()
                                                    self.Cost = self.cost(Actuator=Actuator)

                                                    if self.Cost < MinCost:
                                                        MinCost  = self.Cost
                                                        opt_done = 1
                                                        self.iter += 1

                                                        if self.gearRatioReq == 0:
                                                            Actuator.genEquationFile(
                                                                motor_name=Actuator.motor.motorName,
                                                                gearRatioLL=round(self.gearRatioIter, 1),
                                                                gearRatioUL=round(self.gearRatioIter + self.GEAR_RATIO_STEP, 1))
                                                        else:
                                                            Actuator.genEquationFile_editCADdirectly()

                                                        opt_parameters = [
                                                            gb.gearRatio(), gb.numPlanet,
                                                            gb.Ns, gb.NpBig, gb.NpSmall, gb.Nr,
                                                            gb.moduleBig, gb.moduleSmall,
                                                            Actuator.getMassKG_3DP(),         # [8]  total
                                                            Actuator.bearing_mass,            # [9]  bearings
                                                            Actuator.sun_gear_mass_kg,        # [10] sun
                                                            Actuator.planet_mass_kg,          # [11] planets
                                                            Actuator.ring_gear_mass_kg,       # [12] ring
                                                            Actuator.carrier_mass_kg,         # [13] carrier
                                                            Actuator.sec_carrier_mass_kg,     # [14] sec carrier
                                                            Actuator.motor_casing_mass_kg,    # [15] motor casing
                                                            Actuator.total_sum_except_motor_and_baering,
                                                        ]

                                                        opt_planetaryGearbox = internalcompoundPlanetaryGearbox(
                                                            design_parameters         = self.design_parameters,
                                                            gear_standard_parameters  = self.gear_standard_parameters,
                                                            Ns=gb.Ns, NpBig=gb.NpBig, NpSmall=gb.NpSmall, Nr=gb.Nr,
                                                            numPlanet=gb.numPlanet,
                                                            moduleBig=gb.moduleBig, moduleSmall=gb.moduleSmall,
                                                            densityGears=gb.densityGears, densityStructure=gb.densityStructure,
                                                            fwSunMM=gb.fwSunMM, fwPlanetBigMM=gb.fwPlanetBigMM,
                                                            fwPlanetSmallMM=gb.fwPlanetSmallMM, fwRingMM=gb.fwRingMM,
                                                            maxGearAllowableStressMPa=gb.maxGearAllowableStressMPa)

                                                        opt_actuator = internalcompoundPlanetaryActuator(
                                                            design_parameters        = self.design_parameters,
                                                            motor                    = Actuator.motor,
                                                            motor_driver_params      = None,
                                                            internalcompoundPlanetaryGearbox = opt_planetaryGearbox,
                                                            FOS                      = Actuator.FOS,
                                                            serviceFactor            = Actuator.serviceFactor,
                                                            maxGearboxDiameter       = Actuator.maxGearboxDiameter,
                                                            stressAnalysisMethodName = "MIT")
                                                        opt_actuator.updateFacewidth()
                                                        opt_actuator.getMassKG_3DP()

                                            gb.setNumPlanet(gb.numPlanet + 1)
                                    gb.setNpSmall(gb.NpSmall + 1)
                                gb.setNpBig(gb.NpBig + 1)
                            gb.setNs(gb.Ns + 1)
                        gb.setModuleSmall(round(gb.moduleSmall + 0.100, 1))
                    gb.setModuleBig(round(gb.moduleBig + 0.100, 1))

                if opt_done:
                    self.printOptimizationResults(opt_actuator, log, csv)

                self.gearRatioIter += self.GEAR_RATIO_STEP

                if log:
                    print("Number of iterations: ",              self.iter)
                    print("Total Feasible Gearboxes:",           self.totalFeasibleGearboxes)
                    print("Total Gearboxes with required GR:",   self.totalGearboxesWithReqGR)
                    print("*****************************************************************")
                    print("----------------------------END----------------------------------\n")

            endTime   = time.time()
            totalTime = endTime - startTime
            if printOptParams:
                print("\nRunning Time (sec)")
                print(totalTime)

        sys.stdout = sys.__stdout__
        return totalTime, opt_parameters

    # ── Brute-force search (with PSC variable) ─────────────────────────────
    def optimizeActuatorWithPSC(self, Actuator=internalcompoundPlanetaryActuator, log=1, csv=0):
        startTime      = time.time()
        opt_parameters = []
        if csv and log:
            log, csv = 0, 1
        elif not csv and not log:
            log, csv = 0, 1

        fileName = (f"CPG_BILEVEL_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}.csv"
                    if csv else
                    f"CPG_BILEVEL_{Actuator.stressAnalysisMethodName}_{Actuator.motor.motorName}_LOG.txt")

        with open(fileName, "w") as file1:
            sys.stdout = file1
            self.printOptimizationParameters(Actuator, log, csv)

            if log:
                print("\n*****************************************************************")
                print("FOR MINIMUM GEAR RATIO ", self.gearRatioIter)
                print("*****************************************************************\n")
            elif csv:
                print("\niter, gearRatio, moduleBig, moduleSmall, Ns, NpBig, NpSmall, Nr, numPlanet, "
                      "fwSunMM, fwPlanetBigMM, fwPanetSmallMM, fwRingMM, PSCs, PSCp1, PSCp2, PSCr, "
                      "CD_SP, CD_PR, mass, eff, peakTorque, Cost, tooth_forces_sp, tooth_forces_rp, Torque_Density")

            gb = Actuator.internalcompoundPlanetaryGearbox  # shorthand

            while self.gearRatioIter <= self.GEAR_RATIO_MAX:
                opt_done  = 0
                self.iter = 0
                self.Cost = 100000
                MinCost   = self.Cost

                gb.setModuleBig(self.MODULE_BIG_MIN)
                while gb.moduleBig <= self.MODULE_BIG_MAX:

                    gb.setModuleSmall(self.MODULE_SMALL_MIN)
                    while gb.moduleSmall <= self.MODULE_SMALL_MAX:

                        gb.setNs(self.NUM_TEETH_SUN_MIN)
                        while (2 * gb.getPCRadiusSunM() * 1000) <= Actuator.maxGearboxDiameter:

                            gb.setNpBig(self.NUM_TEETH_PLANET_BIG_MIN)
                            while (2 * gb.getPCRadiusPlanetBigM() * 1000) <= Actuator.maxGearboxDiameter / 2:

                                gb.setNpSmall(self.NUM_TEETH_PLANET_SMALL_MIN)
                                while (2 * gb.getPCRadiusPlanetSmallM() * 1000) <= Actuator.maxGearboxDiameter / 2:

                                    gb.setNr(gb.NpSmall + gb.NpBig + gb.Ns)
                                    if (gb.getGearboxOuterDiaMaxM() * 1000) <= Actuator.maxGearboxDiameter:

                                        gb.setNumPlanet(self.NUM_PLANET_MIN)
                                        while gb.numPlanet <= self.NUM_PLANET_MAX:

                                            if (gb.geometricConstraint()
                                                    and gb.meshingConstraint()
                                                    and gb.noPlanetInterferenceConstraint()):
                                                self.totalFeasibleGearboxes += 1

                                                if (gb.gearRatio() >= self.gearRatioIter
                                                        and gb.gearRatio() <= self.gearRatioIter + self.GEAR_RATIO_STEP):
                                                    self.totalGearboxesWithReqGR += 1
                                                    Actuator.updateFacewidth()

                                                    effActuator  = gb.getEfficiency()
                                                    massActuator = Actuator.getMassKG_3DP()
                                                    self.Cost    = (self.K_Mass * massActuator
                                                                    + self.K_Eff * effActuator)

                                                    if self.Cost < MinCost:
                                                        MinCost  = self.Cost
                                                        opt_done = 1
                                                        self.iter += 1
                                                        Actuator.genEquationFile()
                                                        opt_parameters = [
                                                            gb.gearRatio(), gb.numPlanet,
                                                            gb.Ns, gb.NpBig, gb.NpSmall, gb.Nr,
                                                            gb.moduleBig, gb.moduleSmall,
                                                        ]
                                                        opt_planetaryGearbox = internalcompoundPlanetaryGearbox(
                                                            design_parameters         = self.design_parameters,
                                                            gear_standard_parameters  = self.gear_standard_parameters,
                                                            Ns=gb.Ns, NpBig=gb.NpBig, NpSmall=gb.NpSmall, Nr=gb.Nr,
                                                            numPlanet=gb.numPlanet,
                                                            moduleBig=gb.moduleBig, moduleSmall=gb.moduleSmall,
                                                            densityGears=gb.densityGears, densityStructure=gb.densityStructure,
                                                            fwSunMM=gb.fwSunMM, fwPlanetBigMM=gb.fwPlanetBigMM,
                                                            fwPlanetSmallMM=gb.fwPlanetSmallMM, fwRingMM=gb.fwRingMM,
                                                            maxGearAllowableStressMPa=gb.maxGearAllowableStressMPa)

                                                        opt_actuator = internalcompoundPlanetaryActuator(
                                                            design_parameters        = self.design_parameters,
                                                            motor                    = Actuator.motor,
                                                            internalcompoundPlanetaryGearbox = opt_planetaryGearbox,
                                                            FOS                      = Actuator.FOS,
                                                            serviceFactor            = Actuator.serviceFactor,
                                                            maxGearboxDiameter       = Actuator.maxGearboxDiameter,
                                                            stressAnalysisMethodName = "Lewis")

                                            gb.setNumPlanet(gb.numPlanet + 1)
                                    gb.setNpSmall(gb.NpSmall + 1)
                                gb.setNpBig(gb.NpBig + 1)
                            gb.setNs(gb.Ns + 1)
                        gb.setModuleSmall(round(gb.moduleSmall + 0.100, 1))
                    gb.setModuleBig(round(gb.moduleBig + 0.100, 1))

                if opt_done:
                    try:
                        self.cspgOpt = optimal_continuous_PSC_cpg(
                            GEAR_RATIO_MIN = opt_parameters[0],
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
                        pass  # external PSC optimizer not available in this environment

                    self.printOptimizationResults(opt_actuator, log, csv)

                self.gearRatioIter += self.GEAR_RATIO_STEP

                if log:
                    print("Number of iterations: ",              self.iter)
                    print("Total Feasible Gearboxes:",           self.totalFeasibleGearboxes)
                    print("Total Gearboxes with required GR:",   self.totalGearboxesWithReqGR)
                    print("*****************************************************************")
                    print("----------------------------END----------------------------------\n")

            endTime   = time.time()
            totalTime = endTime - startTime
            print("\nRunning Time (sec)")
            print(totalTime)

        sys.stdout = sys.__stdout__
        return totalTime

    # ── Objective function ─────────────────────────────────────────────────
    def cost(self, Actuator=internalcompoundPlanetaryActuator):
        K_gearRatio   = 10 if self.gearRatioReq != 0 else 0
        gearRatio_err = np.sqrt((Actuator.internalcompoundPlanetaryGearbox.gearRatio() - self.gearRatioReq)**2)

        mass  = Actuator.getMassKG_3DP()
        eff   = Actuator.internalcompoundPlanetaryGearbox.getEfficiency()
        width = (Actuator.internalcompoundPlanetaryGearbox.fwPlanetBigMM
                 + Actuator.internalcompoundPlanetaryGearbox.fwPlanetSmallMM)

        return (self.K_Mass    * mass
                + self.K_Eff   * eff
                + self.K_Width * width
                + K_gearRatio  * gearRatio_err)