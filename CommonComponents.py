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
