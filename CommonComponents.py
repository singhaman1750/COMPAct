import numpy as np

# -------------------------------------------------------------------------
# class material
# -------------------------------------------------------------------------


class material:
    def __init__(
        self,
        density,
        maxAllowableStressMPa=400,
        bhn=2,
        youngsModulus=10
    ):

        self.maxAllowableStressMPa = maxAllowableStressMPa
        self.bhn = bhn
        self.youngsModulus = youngsModulus
        self.density = density


# -------------------------------------------------------------------------
# class bearings
# -------------------------------------------------------------------------


class bearings_discrete:
    def __init__(self, idRequiredMM, odRequiredMM=0):
        # Bearing dataset entered according to e1102 in 
        # [idMM,odMM,widthMM,massKG] format pg no b10-12
        if odRequiredMM != 0:
            self.data_bearings = [
               [10, 19, 5, 0.005],
               [12, 21, 5, 0.006],
               [15, 24, 5, 0.007],
               [17, 26, 5, 0.007],
               [20, 32, 7, 0.017],
               [25, 37, 7, 0.021],
               [30, 42, 7, 0.024],
               [35, 47, 7, 0.027],
               [40, 52, 7, 0.031],
               [44.45, 53.975, 6.35, 0.031],
               [45, 58, 7, 0.038],
               [50, 62, 6, 0.036],
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
               [160, 200, 20, 1.23]
            ]
            self.indexBearing = 0
            while (self.indexBearing < len(self.data_bearings) - 1
                   and self.data_bearings[self.indexBearing][1] < odRequiredMM):
                self.indexBearing += 1
        else:
            self.data_bearings = [[10, 19, 5, 0.005],
                                  [12, 21, 5, 0.006],
                                  [15, 24, 5, 0.007],
                                  [17, 26, 5, 0.007],
                                  [20, 32, 7, 0.017],
                                  [25, 32, 4, 0.021],
                                  [25, 37, 7, 0.021],
                                  [28, 52, 12, 0.096],
                                  [30, 42, 7, 0.024],
                                  [32, 58, 13, 0.122],
                                  [35, 47, 7, 0.027],
                                  [40, 50, 6, 0.023],
                                  [40, 52, 7, 0.031],
                                  [45, 58, 7, 0.038],
                                  [50, 65, 7, 0.050],
                                  [55, 72, 9, 0.081],
                                  [60, 78, 10, 0.103],
                                  [65, 85, 10, 0.128],
                                  [70, 90, 10, 0.134],
                                  [75, 95, 10, 0.149],
                                  [76.2, 88.9, 6.35, 0.07],
                                  [80, 100, 10, 0.151],
                                  [85, 110, 13, 0.263],
                                  [88.9, 101.6, 6.35, 0.0816],
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
            while (self.indexBearing < len(self.data_bearings) - 1
                   and self.data_bearings[self.indexBearing][0] < self.idRequiredMM):
                self.indexBearing += 1
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


# -------------------------------------------------------------------------
# Nuts and bolts class
# -------------------------------------------------------------------------


class nuts_and_bolts_dimensions:
    def __init__(self, bolt_dia, bolt_type="socket_head"):
        self.bolt_dia = bolt_dia
        self.bolt_type = bolt_type
        self.bolt_head_dia, self.bolt_head_height = self.get_bolt_head_dimensions(diameter=self.bolt_dia,
                                                                                  bolt_type=self.bolt_type)
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


# -------------------------------------------------------------------------
# Motor Driver class
# -------------------------------------------------------------------------
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


# =========================================================================
# Motor classes (5 distinct motor construction types)
# =========================================================================

# -------------------------------------------------------------------------
# Framed Outrunner motor — used by SSPG, CPG, DSPG, WPG (from ActuatorAndGearbox.py)
# -------------------------------------------------------------------------
class motor_framed_outrunner:
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
        
        # Name of the motor
        self.motorName                  = motorName

        # Electrical and performance parameters of the motor
        self.maxMotorAngVelRPM          = maxMotorAngVelRPM
        self.maxMotorAngVelRadPerSec    = maxMotorAngVelRPM * (2 * np.pi / 60)
        self.maxMotorTorque             = maxMotorTorque
        self.maxMotorPower              = maxMotorPower
        self.massKG                     = motorMass     # kg
        
        # Geometrical parameters of the motor
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

    def getMaxMotorAngVelRadPerSec(self): return self.maxMotorAngVelRadPerSec # Maximum motor angular velocity in rad/s
    def getMaxMotorPower(self): return self.maxMotorPower # Maximum motor power in W
    def getMaxMotorTorque(self): return self.maxMotorTorque # Maximum motor torque in Nm
    def getMassKG(self): return self.massKG # Mass of the motor in kg
    def getDiaMM(self): return self.motorDiaMM # dimension of the motor in MM
    
    def getLengthMM(self): return self.motorLengthMM

    #dimensions of Stator
    def getStatorIDMM(self): return self.motorStatorIDMM
    def getStatorODMM(self): return self.motorStatorODMM
    def getStatorHeight(self): return self.motorStatorHeightMM
    
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


# -------------------------------------------------------------------------
# Frameless Outrunner motor (from ActuatorandGearbox_ICPG.py / ActuatorAndGearbox_ISSPG_inside.py / ActuatorAndGearbox_ISSPG_compact.py)
# -------------------------------------------------------------------------
class motor_frameless_outrunner:
    """
    Stores all motor geometry and performance data.

    Sections
    ─────────
    • Identification
    • Performance parameters (Kv, torque, speed)
    • Stator dimensions
    • Rotor dimensions
    • Compatibility aliases
    """

    def __init__(self,
                 maxMotorAngVelRPM               = 2640,  # RPM
                 maxMotorTorque                  = 20 / (55 * 2*np.pi/60),  # Nm
                 maxMotorPower                   = 4560,  # W
                 motorMass                       = 0.352, # KG
                 # ── Stator ──────────────────────────────────────────────
                 stator_OD                       = 81,
                 stator_ID                       = 55,
                 stator_height                   = 23.8,
                 stator_hole_PCD                 = 63,
                 motor_stator_extrusion_dia      = 88,
                 motor_stator_extrusion_depth    = 2,
                 # ── Rotor ───────────────────────────────────────────────
                 motor_OD                        = 92.6,
                 rotor_ID                        = 82.6,
                 rotor_height                    = 21.6,
                 motor_rotor_base_ID             = 51,
                 motor_rotor_base_thickness      = 2.6,
                 rotorCSKHeadUpperDiaMM          = 8,
                 rotorCSKHeadHeightMM            = 2.3,
                 motor_rotor_hole_PCD            = 62,
                 motor_rotor_hole_dia            = 4,
                 stator_top_rotor_top_offset  = 4.8,
                 stator_hole_dia              = 3,
                 motor_rotor_hole_num         = 6,
                 # ── Overall envelope ────────────────────────────────────
                 motor_height                    = 36.2,
                 motorName                       = "RO100"):

        # ── Identification ─────────────────────────────────────────────────
        self.motorName = motorName

        # ── Performance parameters ─────────────────────────────────────────
        self.maxMotorAngVelRPM       = maxMotorAngVelRPM
        self.maxMotorAngVelRadPerSec = maxMotorAngVelRPM * (2 * np.pi / 60)
        self.maxMotorTorque          = maxMotorTorque
        self.maxMotorPower           = maxMotorPower
        self.massKG                  = motorMass

        # ── Stator dimensions ──────────────────────────────────────────────
        self.stator_OD                     = stator_OD
        self.stator_ID                     = stator_ID
        self.stator_height                 = stator_height
        self.stator_hole_PCD               = stator_hole_PCD
        self.motor_stator_extrusion_dia   = motor_stator_extrusion_dia
        self.motor_stator_extrusion_depth = motor_stator_extrusion_depth

        # ── Rotor dimensions ───────────────────────────────────────────────
        self.motor_OD                      = motor_OD
        self.rotor_ID                       = rotor_ID
        self.rotor_height                   = rotor_height
        self.motor_rotor_base_ID           = motor_rotor_base_ID
        self.motor_rotor_base_thickness    = motor_rotor_base_thickness
        self.motor_rotor_hole_PCD          = motor_rotor_hole_PCD
        self.motor_rotor_hole_dia          = motor_rotor_hole_dia

        # ── Overall envelope ───────────────────────────────────────────────
        self.motor_height  = motor_height

        # ── Compatibility aliases (used by Actuator class) ─────────────────
        self.motorDiaMM    = motor_OD
        self.motorLengthMM = motor_height

        # ---------------Extra missing parameters from The other version-----
        self.rotorCSKHeadUpperDiaMM   = rotorCSKHeadUpperDiaMM

        # -----------------Variables needed ------------------
        # TODO:not used in CAD
        self.motor_rotor_hole_num = motor_rotor_hole_num
        self.stator_top_rotor_top_offset = stator_top_rotor_top_offset
        self.stator_hole_dia = stator_hole_dia
        self.rotorCSKHeadHeightMM = rotorCSKHeadHeightMM


    # ── Getters ────────────────────────────────────────────────────────────
    def getMaxMotorAngVelRadPerSec(self): return self.maxMotorAngVelRadPerSec
    def getMaxMotorAngVelRPM(self):       return self.maxMotorAngVelRPM
    def getMaxMotorPower(self):           return self.maxMotorPower
    def getMaxMotorTorque(self):          return self.maxMotorTorque
    def getMassKG(self):                  return self.massKG
    def getMotorODMM(self):               return self.motorDiaMM
    def getMotorHeightMM(self):           return self.motorLengthMM

    # ─ Stator getters
    def getStatorODMM(self):              return self.stator_OD
    def getStatorIDMM(self):              return self.stator_ID
    def getStatorHeightMM(self):          return self.stator_height
    def getStatorMountingHolePCD(self):   return self.stator_hole_PCD
    def getMotorStatorExtrusionDia(self): return self.motor_stator_extrusion_dia
    def getMotorStatorExtrusionDepth(self): return self.motor_stator_extrusion_depth
    def getStatorTopRotorTopOffset(self): return self.stator_top_rotor_top_offset
    def getStatorHoleDia(self):           return self.stator_hole_dia

    # ─ Rotor getters
    def getRotorODMM(self):               return self.motor_OD
    def getRotorIDMM(self):               return self.rotor_ID
    def getRotorHeightMM(self):           return self.rotor_height
    def getRotorBottomIDMM(self):         return self.motor_rotor_base_ID
    def getRotorBottomThicknessMM(self):  return self.motor_rotor_base_thickness
    def getRotorCSKHeadUpperDiaMM(self):  return self.rotorCSKHeadUpperDiaMM
    def getRotorCSKHeadHeightMM(self):    return self.rotorCSKHeadHeightMM
    def getRotorMountHolePCDMM(self):     return self.motor_rotor_hole_PCD
    def getRotorMountHoleDiaMM(self):     return self.motor_rotor_hole_dia
    def getMotorRotorHoleNum(self):       return self.motor_rotor_hole_num

    # ── Print ──────────────────────────────────────────────────────────────
    def printParameters(self):
        print("Maximum motor angular velocity = ", round(self.maxMotorAngVelRPM, 2),         " RPM")
        print("Maximum motor power            = ", self.maxMotorPower,                        " W")
        print("Maximum continuous torque      = ", round(self.maxMotorTorque, 3),             " Nm")
        print("Maximum angular velocity       = ", round(self.maxMotorAngVelRadPerSec, 2),    " rad/s")
        print("Mass                           = ", self.massKG,                               " kg")
        print("── Stator ──────────────────────────────────────────────")
        print("  Outer Diameter = ", self.stator_OD, " mm")
        print("  Inner Diameter = ", self.stator_ID, " mm")
        print("  Height         = ", self.stator_height, " mm")
        print("── Rotor ───────────────────────────────────────────────")
        print("  Outer Diameter = ", self.motor_OD, " mm")
        print("  Inner Diameter = ", self.rotor_ID, " mm")
        print("  Height         = ", self.rotor_height, " mm")


# -------------------------------------------------------------------------
# Frameless Inrunner motor — INSSPG version (from ActuatorandGearbox_INSSPG.py)
# -------------------------------------------------------------------------
class motor_frameless_inrunner_mahi:
    def __init__(self,
                 Kv                               = 55,
                 maxContinuousCurrent             = 20,
                 ratedVoltage                     = 48,
                 power                            = 838,
                 massKG                           = 0.50,
                 Stator_ID                        = 57.0,
                 Stator_OD                        = 104.0,
                 stator_height                    = 24.5,
                 Rotor_height                     = 15.0,
                 Rotor_OD                         = 55.6,
                 Rotor_ID                         = 45.0,
                 rotor_mount_hole_dia             = 4.0,
                 rotor_mount_hole_CSK_OD          = 8.0,
                 rotor_mount_hole_CSK_head_hight  = 3.0,
                 motorName                        = "RI100"):

        self.motorName = motorName

        self.Kv                   = Kv
        self.maxContinuousCurrent = maxContinuousCurrent
        self.ratedVoltage         = ratedVoltage
        self.maxMotorPower        = power
        self.massKG               = massKG

        self.maxMotorAngVelRPM       = Kv * ratedVoltage
        self.maxMotorAngVelRadPerSec = self.maxMotorAngVelRPM * (2 * np.pi / 60)
        self.maxMotorTorque          = maxContinuousCurrent / (Kv * 2 * np.pi / 60)

        self.Stator_ID                        = Stator_ID
        self.Stator_OD                        = Stator_OD
        self.stator_height                    = stator_height

        self.Rotor_height                     = Rotor_height
        self.Rotor_OD                         = Rotor_OD
        self.Rotor_ID                         = Rotor_ID
        self.rotor_mount_hole_dia             = rotor_mount_hole_dia
        self.rotor_mount_hole_CSK_OD          = rotor_mount_hole_CSK_OD
        self.rotor_mount_hole_CSK_head_hight  = rotor_mount_hole_CSK_head_hight

        self.motorDiaMM    = Stator_OD
        self.motorLengthMM = stator_height

    def getMaxMotorAngVelRadPerSec(self): return self.maxMotorAngVelRadPerSec
    def getMaxMotorPower(self):           return self.maxMotorPower
    def getMaxMotorTorque(self):          return self.maxMotorTorque
    def getMassKG(self):                  return self.massKG
    def getDiaMM(self):                   return self.motorDiaMM
    def getLengthMM(self):                return self.motorLengthMM
    def getStatorODMM(self):              return self.Stator_OD
    def getStatorIDMM(self):              return self.Stator_ID
    def getStatorHeightMM(self):          return self.stator_height
    def getRotorODMM(self):               return self.Rotor_OD
    def getRotorIDMM(self):               return self.Rotor_ID
    def getRotorHeightMM(self):           return self.Rotor_height

    def printParameters(self):
        print("Maximum motor angular velocity = ", round(self.maxMotorAngVelRPM, 2),         " RPM")
        print("Maximum motor power            = ", self.maxMotorPower,                       " W")
        print("Maximum continuous torque      = ", round(self.maxMotorTorque, 3),            " Nm")
        print("Maximum angular velocity       = ", round(self.maxMotorAngVelRadPerSec, 2),    " rad/s")
        print("Mass                           = ", self.massKG,                              " kg")


# -------------------------------------------------------------------------
# Frameless Inrunner motor — INCPG version (from ActuatorAndGearbox_INCPG_dependent.py / ActuatorAndGearbox_INCPG_independent.py)
# -------------------------------------------------------------------------
class motor_frameless_inrunner_suyash:
    
    def __init__(self,
                 rotor_OD                     = 55.6,
                 stator_ID                    = 57,
                 rotor_height                 = 15,
                 rotor_ID                     = 45,
                 stator_height                = 24.5,
                 stator_OD                    = 104,
                 stator_hole_dia              = 3,
                 stator_top_height            = 7,
                 stator_mid_height            = 13,
                 stator_bottom_height         = 4.5,
                 stator_inside_OD             = 101,
                 stator_hole_num              = 4,
                 stator_inside_ID             = 58,
                 maxMotorAngVelRPM            = 5040,  # RPM
                 maxMotorTorque               = 1.3,   # Nm
                 maxMotorPower                = 1.3 * 5040 * 2*np.pi/60,  # W
                 motorMass                    = 0.265, # KG
                 motorName                    = "RO100"):

        self.motorName = motorName

        # Physical geometry
        self.rotor_OD                     = rotor_OD
        self.stator_ID                    = stator_ID
        self.rotor_height                 = rotor_height
        self.rotor_ID                     = rotor_ID
        self.stator_height                = stator_height
        self.stator_OD                    = stator_OD
        self.stator_hole_dia              = stator_hole_dia
        self.stator_top_height            = stator_top_height
        self.stator_mid_height            = stator_mid_height
        self.stator_bottom_height         = stator_bottom_height
        self.stator_inside_OD             = stator_inside_OD
        self.stator_hole_num              = stator_hole_num
        self.stator_inside_ID             = stator_inside_ID
        self.motorDiaMM                   =  self.stator_OD
        self.motorLengthMM                = self.stator_top_height + self.stator_mid_height + self.stator_bottom_height 

        #Motor other param
        self.maxMotorAngVelRPM            = maxMotorAngVelRPM
        self.maxMotorAngVelRadPerSec      = maxMotorAngVelRPM * (2 * np.pi / 60)
        self.maxMotorTorque               = maxMotorTorque
        self.maxMotorPower                = maxMotorPower
        self.massKG                       = motorMass     # kg

    # ------------------------------------------------------------------
    # Convenience getters (mirror reference code style)
    # ------------------------------------------------------------------
    
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

    def getDiaMM(self):
       return self.motorDiaMM

    def getLengthMM(self): 
        return self.motorLengthMM

    def getRotorIDMM(self):  
        return self.rotor_ID

    def printParameters(self):
        print(f"Motor: {self.motorName}")
        print(f"  rotor_OD              = {self.rotor_OD} mm")
        print(f"  stator_ID             = {self.stator_ID} mm")
        print(f"  rotor_height          = {self.rotor_height} mm")
        print(f"  rotor_ID              = {self.rotor_ID} mm")
        print(f"  stator_height         = {self.stator_height} mm")
        print(f"  stator_OD             = {self.stator_OD} mm")
        print(f"  stator_hole_dia       = {self.stator_hole_dia} mm")
        print(f"  stator_top_height     = {self.stator_top_height} mm")
        print(f"  stator_mid_height     = {self.stator_mid_height} mm")
        print(f"  stator_bottom_height  = {self.stator_bottom_height} mm")
        print(f"  stator_inside_OD      = {self.stator_inside_OD} mm")
        print(f"  stator_hole_num       = {self.stator_hole_num}")
        print(f"  stator_inside_ID      = {self.stator_inside_ID} mm")
