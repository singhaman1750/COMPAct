"""Actuator map: the best COMPAct actuator for a motor at any gear ratio, for co-design.

Standalone: needs only numpy and a map's fits.json (written by fit.py), so this file and a map
folder can be copied into another project.

    from map import ActuatorMap            # or: from tools.actuator_map.map import ActuatorMap
    amap = ActuatorMap("tools/actuator_map/runs/pilot")   # a run folder or a released map folder
    a = amap.actuator("U8_Lite", 14.6, "3dp")
    a.gb_type, a.mass, a.width, a.peak_torque, a.reflected_inertia

All values are SI: kg, m, N m, rad/s (speeds also in rpm), kg m^2. Output torque, speed and
reflected inertia are computed from the motor (values stored in fits.json):
    peak_torque   = motor peak torque x ratio x efficiency x torque_fraction
    rated_torque  = min(motor rated torque, torque_fraction x motor peak torque) x ratio x efficiency
    speeds        = motor speed / ratio
    reflected_inertia = ratio^2 x motor rotor inertia   (the gears' own inertia is not included)

The best type at a ratio: every type valid there gets the real-width score from its fitted values,
a type whose gears carry less than 80 % of the peak torque is only chosen if no type carries 80 %,
and the lowest score wins (rule="compact_cost": the optimiser's own cost instead).

method="fit" (default) uses the smooth fits (polynomial pieces, differentiable within a piece);
method="interp" interpolates linearly between the swept designs of the chosen type (exact at the
designs). derivative=True also returns d(value)/d(ratio) for every value.
"""
import json
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

RPM_TO_RAD_S = 2 * math.pi / 60
SUPPORTED_FORMATS = (1,)
FITTED = ("mass_kg", "width_body_m", "width_with_driver_m", "dia_body_m", "dia_widest_m",
          "efficiency", "torque_carried_fraction", "compact_cost")


@dataclass
class Actuator:
    motor: str
    material: str
    gb_type: str
    ratio: float
    mass: float                 # kg, whole actuator (motor included)
    width: float                # m, along the axis, with the motor-driver mount
    width_body: float           # m, without the driver mount
    dia: float                  # m, body (largest round part)
    dia_widest: float           # m, incl. casing ears / bulges
    efficiency: float
    torque_fraction: float      # share of the motor's peak torque the gears carry (< 1: capped)
    peak_torque: float          # N m at the output
    rated_torque: float         # N m at the output (None if the motor has no rated torque)
    no_load_speed: float        # rad/s at the output
    rated_speed: float          # rad/s at the output (None if the motor has no rated speed)
    reflected_inertia: float    # kg m^2, ratio^2 x rotor inertia (None if unknown)
    score: float                # real-width score (or the optimiser's cost with rule="compact_cost")
    flags: dict = field(default_factory=dict)
    derivatives: dict = field(default_factory=dict)   # d(value)/d(ratio), with derivative=True

    @property
    def no_load_speed_rpm(self):
        return self.no_load_speed / RPM_TO_RAD_S

    @property
    def rated_speed_rpm(self):
        return None if self.rated_speed is None else self.rated_speed / RPM_TO_RAD_S


# ---- one fitted quantity ------------------------------------------------------------------------

def _piece(fit, x):
    return fit["pieces"][sum(1 for b in fit.get("breaks", []) if x >= b)]


def _poly(coef, x):
    return float(sum(c * x ** k for k, c in enumerate(coef)))


def _dpoly(coef, x):
    return float(sum(k * c * x ** (k - 1) for k, c in enumerate(coef) if k))


def _fit_value(fit, x, method):
    """(value, d/dx) of one quantity at ratio x."""
    if method == "interp":
        xs, ys = np.asarray(fit["x"]), np.asarray(fit["y"])
        value = float(np.interp(x, xs, ys))
        i = int(np.clip(np.searchsorted(xs, x, side="right") - 1, 0, len(xs) - 2)) if len(xs) > 1 else 0
        slope = 0.0 if len(xs) < 2 or xs[i + 1] == xs[i] else float((ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]))
        return value, slope
    coef = _piece(fit, x)["coef"]
    return _poly(coef, x), _dpoly(coef, x)


# ---- the map ------------------------------------------------------------------------------------

class ActuatorMap:
    def __init__(self, path):
        path = Path(path)
        data = json.loads((path / "fits.json" if path.is_dir() else path).read_text(encoding="utf-8"))
        meta = data["meta"]
        if meta.get("format") not in SUPPORTED_FORMATS:
            raise ValueError(f"fits.json format {meta.get('format')} not supported by this map.py "
                             f"(supports {SUPPORTED_FORMATS}); use the map.py of the same COMPAct version")
        self.meta = meta
        self.gains = meta["gains"]
        self.min_fraction = meta["min_carried_fraction_for_best"]
        self.near_rel = meta["near_best_rel"]
        self._motors = meta["motors"]
        self._fits = data["motors"]

    # -- lookup helpers --
    def motors(self):
        return sorted(self._fits)

    def materials(self, motor):
        return sorted(self._entry(motor, None))

    def types(self, motor, material):
        return sorted(self._entry(motor, material)["types"])

    def valid_range(self, motor, material, gb_type=None):
        """[[low, high], ...] ratio intervals where the type (or any type) has designs."""
        types = self._entry(motor, material)["types"]
        names = [gb_type] if gb_type else list(types)
        return sorted(iv for n in names for iv in self._type(motor, material, n)["valid_intervals"])

    def covered(self, motor, material, gb_type=None):
        """The valid ranges merged into non-overlapping [low, high] intervals."""
        merged = []
        for lo, hi in self.valid_range(motor, material, gb_type):
            if merged and lo <= merged[-1][1] + 1e-9:
                merged[-1][1] = max(merged[-1][1], hi)
            else:
                merged.append([lo, hi])
        return merged

    def best_types(self, motor, material, rule="real_width"):
        """[[from, to, type], ...] over the swept range, and the switch ratios (from fit.py)."""
        e = self._entry(motor, material)
        key = "real_width" if rule == "real_width" else "compact"
        return e[f"best_{key}"], e[f"switches_{key}"]

    def _entry(self, motor, material):
        if motor not in self._fits:
            raise KeyError(f"motor {motor!r} not in this map; motors: {', '.join(self.motors())}")
        if material is None:
            return self._fits[motor]
        if material not in self._fits[motor]:
            raise KeyError(f"{motor}: no {material!r} map; materials: {', '.join(sorted(self._fits[motor]))}")
        return self._fits[motor][material]

    def _type(self, motor, material, gb_type):
        types = self._entry(motor, material)["types"]
        if gb_type not in types:
            raise KeyError(f"{motor} {material}: no type {gb_type!r}; types: {', '.join(sorted(types))}")
        return types[gb_type]

    @staticmethod
    def _valid(type_fit, x):
        return any(lo - 1e-9 <= x <= hi + 1e-9 for lo, hi in type_fit["valid_intervals"])

    def _values(self, type_fit, x, method):
        vals, ders = {}, {}
        for q, fit in type_fit["quantities"].items():
            vals[q], ders[q] = _fit_value(fit, x, method)
        if "torque_carried_fraction" in vals:
            f = vals["torque_carried_fraction"]
            if f >= 1.0 or f <= 0.0:
                vals["torque_carried_fraction"], ders["torque_carried_fraction"] = min(1.0, max(0.0, f)), 0.0
        return vals, ders

    def _score(self, vals, rule):
        if rule == "compact_cost":
            return vals["compact_cost"]
        g = self.gains
        return (g["K_Mass"] * vals["mass_kg"] + g["K_Eff"] * vals["efficiency"]
                + g["K_Width_real"] * vals["width_with_driver_m"] * 1000
                + g["K_torque_shortfall"] * (1 - vals.get("torque_carried_fraction", 1.0)))

    def ranking(self, motor, ratio, material, types=None, rule="real_width"):
        """Valid types at this ratio, best first: [(score, gb_type, torque_fraction), ...], with the
        80 % torque rule applied (types below it come after every type that reaches it)."""
        entry = self._entry(motor, material)
        scored = []
        for gb, tf in entry["types"].items():
            if (types and gb not in types) or not self._valid(tf, ratio):
                continue
            vals, _ = self._values(tf, ratio, "fit")
            if rule == "real_width" and "width_with_driver_m" not in vals:
                continue
            scored.append((self._score(vals, rule), gb, vals.get("torque_carried_fraction", 1.0)))
        return sorted(scored, key=lambda s: (s[2] < self.min_fraction, s[0], s[1]))

    # -- the main call --
    def actuator(self, motor, ratio, material="3dp", gb_type=None, types=None, rule="real_width",
                 method="fit", derivative=False):
        """The actuator at `ratio`: the best type (or `gb_type`), with every value in SI units.

        types:  only consider these gearbox types for "best"
        rule:   "real_width" (default) or "compact_cost"
        method: "fit" (smooth) or "interp" (exact at the swept designs)
        Raises ValueError if no (allowed) type has designs at this ratio.
        """
        if rule not in ("real_width", "compact_cost"):
            raise ValueError("rule must be 'real_width' or 'compact_cost'")
        if method not in ("fit", "interp"):
            raise ValueError("method must be 'fit' or 'interp'")
        ratio = float(ratio)
        ranking = self.ranking(motor, ratio, material, types, rule)
        if gb_type is None:
            if not ranking:
                ranges = ", ".join(f"{lo:.2f}-{hi:.2f}" for lo, hi in self.covered(motor, material, None))
                if types:
                    ranges += f" (any type; allowed types: {', '.join(types)})"
                raise ValueError(f"{motor} {material}: no design at ratio {ratio:g}; map covers {ranges}")
            gb_type = ranking[0][1]
        tf = self._type(motor, material, gb_type)
        if not self._valid(tf, ratio):
            ranges = ", ".join(f"{lo:.2f}-{hi:.2f}" for lo, hi in tf["valid_intervals"])
            raise ValueError(f"{motor} {material} {gb_type}: no design at ratio {ratio:g}; valid {ranges}")

        v, d = self._values(tf, ratio, method)
        m = self._motors[motor]
        eta, f = v["efficiency"], v.get("torque_carried_fraction", 1.0)
        deta, df = d["efficiency"], d.get("torque_carried_fraction", 0.0)
        tp, tr = m["peak_torque_Nm"], m.get("rated_torque_Nm")
        w0, wr, j = m["no_load_speed_rpm"] * RPM_TO_RAD_S, m.get("rated_speed_rpm"), m.get("rotor_inertia_kgm2")
        wr = None if wr is None else wr * RPM_TO_RAD_S

        peak = tp * ratio * eta * f
        dpeak = tp * (eta * f + ratio * deta * f + ratio * eta * df)
        if tr is None:
            rated = drated = None
        elif tr <= f * tp:  # the gears carry the rated torque in full
            rated, drated = tr * ratio * eta, tr * (eta + ratio * deta)
        else:  # capped below the rated torque: the gears carry f x peak, which is the peak output
            rated, drated = peak, dpeak
        best_score = ranking[0][0] if ranking else None
        own = next((s for s in ranking if s[1] == gb_type), None)
        near = [gb for s, gb, _ in ranking if best_score is not None and s <= best_score + self.near_rel * abs(best_score)]
        flags = {
            "torque_capped": f < 1 - 1e-9,
            "no_full_torque_design": bool(ranking) and all(s[2] < self.min_fraction for s in ranking),
            "near_best": near,
            "cad_issues": tf.get("cad_issues", []),
            "geometry_approx": any(abs(r - ratio) <= self.meta.get("grid_step", 1.0) for r in tf.get("geometry_approx_ratios", [])),
            "rotor_inertia_basis": m.get("rotor_inertia_basis"),
            "method": method, "rule": rule, "best": gb_type == (ranking[0][1] if ranking else None),
        }
        act = Actuator(
            motor=motor, material=material, gb_type=gb_type, ratio=ratio,
            mass=v["mass_kg"], width=v["width_with_driver_m"], width_body=v["width_body_m"],
            dia=v["dia_body_m"], dia_widest=v["dia_widest_m"], efficiency=eta, torque_fraction=f,
            peak_torque=peak, rated_torque=rated, no_load_speed=w0 / ratio,
            rated_speed=None if wr is None else wr / ratio,
            reflected_inertia=None if j is None else ratio ** 2 * j,
            score=own[0] if own else self._score(v, rule), flags=flags)
        if derivative:
            act.derivatives = {
                "mass": d["mass_kg"], "width": d["width_with_driver_m"], "width_body": d["width_body_m"],
                "dia": d["dia_body_m"], "dia_widest": d["dia_widest_m"], "efficiency": deta,
                "torque_fraction": df, "peak_torque": dpeak, "rated_torque": drated,
                "no_load_speed": -w0 / ratio ** 2, "rated_speed": None if wr is None else -wr / ratio ** 2,
                "reflected_inertia": None if j is None else 2 * ratio * j}
        return act
