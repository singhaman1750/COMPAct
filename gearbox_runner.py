"""
One runner for every gearbox type.

GEARBOXES holds one GearboxSpec per gearbox type: only what differs between types (which
classes, config files, diameter limits, ...). run(gb_type, motor_name, gear_ratio) builds the
motor, gearbox, actuator and optimiser from that spec and runs the optimisation.

The specs keep every existing difference between types on purpose, so results are unchanged;
see ISSUES.md "Unify per-gearbox settings" for the ones to unify later.
"""

import importlib
import json
import os
from dataclasses import dataclass, field
from typing import Callable, Optional

from CommonComponents import load_motor, max_gearbox_dia_mult_factor

CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config_files")
MATERIALS_FILE = "config.json"   # Material_properties for every gearbox type
COST_FILE = "cost.json"          # Cost_gain_parameters for every gearbox type

# Material modes: (gear material, structure material) from Material_properties. The ring gear
# counts as a gear; parts with their own density keyword (rotor coupler etc., see
# GearboxSpec.extra_gearbox_densities) keep their material in both modes.
MATERIAL_MODES = {
    "3dp":   ("PLA", "PLA"),
    "metal": ("Steel", "Aluminum"),
}
# Added to the results file names, so metal runs don't overwrite 3dp results.
RESULTS_SUFFIX = {"3dp": "", "metal": "_metal"}

# Optimiser keyword -> key in the gearbox's optimisation parameters, per optimiser kind.
OPTIMIZER_LIMITS = {
    "single": {
        "MODULE_MIN": "MODULE_MIN", "MODULE_MAX": "MODULE_MAX",
        "NUM_PLANET_MIN": "NUM_PLANET_MIN", "NUM_PLANET_MAX": "NUM_PLANET_MAX",
        "NUM_TEETH_SUN_MIN": "NUM_TEETH_SUN_MIN", "NUM_TEETH_PLANET_MIN": "NUM_TEETH_PLANET_MIN",
    },
    # compound: big and small stage share one module range and one planet-teeth minimum
    "compound": {
        "MODULE_BIG_MIN": "MODULE_MIN", "MODULE_BIG_MAX": "MODULE_MAX",
        "MODULE_SMALL_MIN": "MODULE_MIN", "MODULE_SMALL_MAX": "MODULE_MAX",
        "NUM_PLANET_MIN": "NUM_PLANET_MIN", "NUM_PLANET_MAX": "NUM_PLANET_MAX",
        "NUM_TEETH_SUN_MIN": "NUM_TEETH_SUN_MIN",
        "NUM_TEETH_PLANET_BIG_MIN": "NUM_TEETH_PLANET_MIN",
        "NUM_TEETH_PLANET_SMALL_MIN": "NUM_TEETH_PLANET_MIN",
    },
    "wolfrom": {
        "MODULE_BIG_MIN": "MODULE_BIG_MIN", "MODULE_BIG_MAX": "MODULE_BIG_MAX",
        "MODULE_SMALL_MIN": "MODULE_SMALL_MIN", "MODULE_SMALL_MAX": "MODULE_SMALL_MAX",
        "NUM_PLANET_MIN": "NUM_PLANET_MIN", "NUM_PLANET_MAX": "NUM_PLANET_MAX",
        "NUM_TEETH_SUN_MIN": "NUM_TEETH_SUN_MIN",
        "NUM_TEETH_PLANET_BIG_MIN": "NUM_TEETH_PLANET_BIG_MIN",
        "NUM_TEETH_PLANET_SMALL_MIN": "NUM_TEETH_PLANET_SMALL_MIN",
    },
    "double": {
        "MODULE_STAGE1_MIN": "MODULE_STAGE1_MIN", "MODULE_STAGE1_MAX": "MODULE_STAGE1_MAX",
        "MODULE_STAGE2_MIN": "MODULE_STAGE2_MIN", "MODULE_STAGE2_MAX": "MODULE_STAGE2_MAX",
        "NUM_PLANET_STAGE1_MIN": "NUM_PLANET_STAGE1_MIN", "NUM_PLANET_STAGE1_MAX": "NUM_PLANET_STAGE1_MAX",
        "NUM_PLANET_STAGE2_MIN": "NUM_PLANET_STAGE2_MIN", "NUM_PLANET_STAGE2_MAX": "NUM_PLANET_STAGE2_MAX",
        "NUM_TEETH_SUN_MIN": "NUM_TEETH_SUN_MIN", "NUM_TEETH_PLANET_MIN": "NUM_TEETH_PLANET_MIN",
    },
}
GEAR_RATIO_LIMITS = ("GEAR_RATIO_MIN", "GEAR_RATIO_MAX", "GEAR_RATIO_STEP")

# Driver handling: "OdrivePro" passes that driver, None passes motor_driver_params=None,
# OMIT leaves the argument out.
OMIT = "omit"


@dataclass(frozen=True)
class GearboxSpec:
    module: str                      # file with the gearbox, actuator and optimiser classes
    gearbox_cls: str
    actuator_cls: str
    optimizer_cls: str
    gearbox_arg: str                 # actuator keyword that takes the gearbox
    config_file: str                 # gear standard, MIT factors, cost gains, drivers
    params_file: str
    design_keys: tuple               # sections of params_file merged into the design parameters
    optimization_key: str
    motor_type: str
    optimizer_kind: str              # key of OPTIMIZER_LIMITS
    max_diameter: Optional[Callable] = None        # (motor, design, opt) -> mm; None: not passed
    max_diameter_stage1: Optional[Callable] = None
    driver: Optional[str] = "OdrivePro"
    extra_gearbox_densities: dict = field(default_factory=dict)  # keyword -> material name
    passes_gearbox_type: bool = False              # actuator takes insspg_type=gb_type


def _small_motor_factor(motor, opt):
    return max_gearbox_dia_mult_factor(motor, opt)


# Each formula is written exactly as in the optimiser it replaces (same operation order), so
# floating-point results are identical.
GEARBOXES = {
    "sspg": GearboxSpec(
        "ActuatorAndGearbox", "singleStagePlanetaryGearbox", "singleStagePlanetaryActuator",
        "optimizationSingleStageActuator", "planetaryGearbox",
        "config.json", "sspg_params.json", ("sspg_3DP_design_parameters",), "sspg_optimization_parameters",
        "framed_outrunner", "single",
        max_diameter=lambda m, d, o: (_small_motor_factor(m, o) * m.motorDiaMM - 2*d["ringRadialWidthMM"])),
    "cpg": GearboxSpec(
        "ActuatorAndGearbox", "compoundPlanetaryGearbox", "compoundPlanetaryActuator",
        "optimizationCompoundPlanetaryActuator", "compoundPlanetaryGearbox",
        "config.json", "cpg_params.json", ("cpg_3DP_design_parameters",), "cpg_optimization_parameters",
        "framed_outrunner", "compound",
        max_diameter=lambda m, d, o: _small_motor_factor(m, o) * m.motorDiaMM),
    "wpg": GearboxSpec(
        "ActuatorAndGearbox", "wolfromPlanetaryGearbox", "wolfromPlanetaryActuator",
        "optimizationWolfromPlanetaryActuator", "wolfromPlanetaryGearbox",
        "config.json", "wpg_params.json", ("wpg_3DP_design_parameters",), "wpg_optimization_parameters",
        "framed_outrunner", "wolfrom",
        max_diameter=lambda m, d, o: _small_motor_factor(m, o) * m.motorDiaMM - 2*d["ringRadialWidthMMBig"]),
    "dspg": GearboxSpec(
        "ActuatorAndGearbox", "doubleStagePlanetaryGearbox", "doubleStagePlanetaryActuator",
        "optimizationDoubleStagePlanetaryActuator", "doubleStagePlanetaryGearbox",
        "config.json", "dspg_params.json", ("dspg_design_parameters_3DP",), "dspg_optimization_parameters",
        "framed_outrunner", "double",
        max_diameter=lambda m, d, o: m.motorDiaMM * _small_motor_factor(m, o) - 2*d["ring_radial_thickness"]),
    "isspg_inside": GearboxSpec(
        "ActuatorAndGearbox_ISSPG_inside", "internalsingleStagePlanetaryGearbox",
        "internalsingleStagePlanetaryActuator", "optimizationInternalSingleStageActuator", "planetaryGearbox",
        "config.json", "isspg_params.json", ("isspg_3DP_design_parameters",), "isspg_optimization_parameters",
        "frameless_outrunner", "single"),
    "isspg_compact": GearboxSpec(
        "ActuatorAndGearbox_ISSPG_compact", "internalsingleStagePlanetaryGearbox",
        "internalsingleStagePlanetaryActuator", "optimizationInternalSingleStageActuator", "planetaryGearbox",
        "config.json", "isspg_params.json", ("isspg_3DP_design_parameters",), "isspg_optimization_parameters",
        "frameless_outrunner", "single"),
    "icpg": GearboxSpec(
        "ActuatorandGearbox_ICPG", "internalcompoundPlanetaryGearbox", "internalcompoundPlanetaryActuator",
        "optimizationInternalCompoundPlanetaryActuator", "internalcompoundPlanetaryGearbox",
        "motor_config.json", "icpg_params.json", ("cpg_3DP_design_parameters",), "cpg_optimization_parameters",
        "frameless_outrunner", "compound",
        max_diameter=lambda m, d, o: o["MAX_GB_DIA_MULT_FACTOR"] * m.getStatorIDMM(),   # inside the stator
        driver=OMIT),
    "idspg": GearboxSpec(
        "ActuatorandGearbox_IDSPG", "internaldoubleStagePlanetaryGearbox", "internaldoubleStagePlanetaryActuator",
        "optimizationinternalDoubleStagePlanetaryActuator", "internaldoubleStagePlanetaryGearbox",
        "idspg_motor_config.json", "idspg_params.json", ("idspg_design_parameters_3DP",),
        "idspg_optimization_parameters", "frameless_outrunner", "double",
        max_diameter=lambda m, d, o: (o["MAX_GB_DIA_MULT_FACTOR"]
                                      * (m.getMotorODMM() + d["standard_clearance_1_5mm"]*2)),
        max_diameter_stage1=lambda m, d, o: (m.getStatorIDMM() - d["ring1RadialWidthMM"]*2)),
    "insspg_type_1": GearboxSpec(
        "ActuatorandGearbox_INSSPG", "singleStagePlanetaryGearbox", "singleStagePlanetaryActuator",
        "optimizationSingleStageActuator", "planetaryGearbox",
        "insspg_motor_config.json", "insspg_params.json",
        ("sspg_design_parameters", "sspg_3DP_design_parameters"), "sspg_optimization_parameters",
        "frameless_inrunner", "single",
        max_diameter=lambda m, d, o: (m.getStatorODMM() - d["max_diameter_stator_OD_margin"] - (d["standard_clearance_1_5mm"])*2
                                      - (d["loose_clearance_3DP"])/2),
        driver=None, passes_gearbox_type=True),
    "insspg_type_2": GearboxSpec(
        "ActuatorandGearbox_INSSPG", "singleStagePlanetaryGearbox", "singleStagePlanetaryActuator",
        "optimizationSingleStageActuator", "planetaryGearbox",
        "insspg_motor_config.json", "insspg_params.json",
        ("sspg_design_parameters", "sspg_3DP_design_parameters"), "sspg_optimization_parameters",
        "frameless_inrunner", "single",
        max_diameter=lambda m, d, o: (m.getStatorODMM() - d["max_diameter_stator_OD_margin"] - (d["standard_clearance_1_5mm"])*2
                                      - (d["loose_clearance_3DP"])/2),
        driver=None, passes_gearbox_type=True),
    "incpg_dependent": GearboxSpec(
        "ActuatorAndGearbox_INCPG_dependent", "inrunnerCompoundPlanetaryGearbox",
        "inrunnerCompoundPlanetaryActuator", "optimizationInrunnerCompoundPlanetaryActuator",
        "inrunnerCompoundPlanetaryGearbox",
        "config.json", "incpg_dependent_params.json", ("incpg_3DP_design_parameters",),
        "incpg_optimization_parameters", "frameless_inrunner", "compound",
        max_diameter=lambda m, d, o: o["MAX_GB_DIA_MULT_FACTOR"] * m.motorDiaMM,
        extra_gearbox_densities={"densityAluminum": "Aluminum"}),
    "incpg_independent": GearboxSpec(
        "ActuatorAndGearbox_INCPG_independent", "inrunnerCompoundPlanetaryGearbox",
        "inrunnerCompoundPlanetaryActuator", "optimizationInrunnerCompoundPlanetaryActuator",
        "inrunnerCompoundPlanetaryGearbox",
        "config.json", "incpg_independent_params.json", ("incpg_3DP_design_parameters",),
        "incpg_optimization_parameters", "frameless_inrunner", "compound",
        max_diameter=lambda m, d, o: o["MAX_GB_DIA_MULT_FACTOR"] * m.motorDiaMM,
        extra_gearbox_densities={"densityAluminum": "Aluminum"}),
    "inwpg_dependent": GearboxSpec(
        "ActuatorAndGearbox_INWPG_dependent", "inrunnerWolfromPlanetaryGearbox",
        "inrunnerWolfromPlanetaryActuator", "optimizationInrunnerWolfromPlanetaryActuator",
        "inrunnerWolfromPlanetaryGearbox",
        "config.json", "inwpg_params_dependent.json", ("inwpg_3DP_design_parameters",),
        "inwpg_optimization_parameters", "frameless_inrunner", "wolfrom",
        max_diameter=lambda m, d, o: o["MAX_GB_DIA_MULT_FACTOR"] * m.motorDiaMM,
        extra_gearbox_densities={"densityAluminum": "Aluminum"}),
    "inwpg_independent": GearboxSpec(
        "ActuatorAndGearbox_INWPG_independent", "inrunnerWolfromPlanetaryGearbox",
        "inrunnerWolfromPlanetaryActuator", "optimizationInrunnerWolfromPlanetaryActuator",
        "inrunnerWolfromPlanetaryGearbox",
        "config.json", "inwpg_params_independent.json", ("inwpg_3DP_design_parameters",),
        "inwpg_optimization_parameters", "frameless_inrunner", "wolfrom",
        max_diameter=lambda m, d, o: o["MAX_GB_DIA_MULT_FACTOR"] * m.motorDiaMM,
        extra_gearbox_densities={"densityAluminum": "Aluminum"}),
    "indspg": GearboxSpec(
        "ActuatorandGearbox_INDSPG", "inrunnerdoubleStagePlanetaryGearbox", "inrunnerdoubleStageActuator",
        "optimizationDoubleStageActuator", "inrunnerdoubleStagePlanetaryGearbox",
        "indspg_motor_config.json", "indspg_params.json", ("indspg_design_parameters_3DP",),
        "indspg_optimization_parameters", "frameless_inrunner", "double",
        max_diameter=lambda m, d, o: (o["MAX_GB_DIA_MULT_FACTOR"]
                                      * (m.getStator_wire_OD() - d["ring2RadialWidthMM"]*2)),
        max_diameter_stage1=lambda m, d, o: (m.getRotorIDMM() - d["standard_clearance_1_5mm"]*4),  # inside the rotor
        driver=OMIT, extra_gearbox_densities={"densityRotor": "Aluminum"}),
}


def _load_json(name):
    with open(os.path.join(CONFIG_DIR, name), "r") as json_file:
        return json.load(json_file)


def build(gb_type, motor_name, material="3dp"):
    """Return (actuator, optimizer) for a gearbox type, motor and material mode."""
    if gb_type not in GEARBOXES:
        raise ValueError(f"Unknown gearbox type: {gb_type}. Known types: {', '.join(GEARBOXES)}")
    if material not in MATERIAL_MODES:
        raise ValueError(f"Unknown material mode: {material}. Known modes: {', '.join(MATERIAL_MODES)}")
    spec   = GEARBOXES[gb_type]
    config = _load_json(spec.config_file)
    params = _load_json(spec.params_file)
    design = {}
    for key in spec.design_keys:
        design.update(params[key])
    gains = _load_json(COST_FILE)["Cost_gain_parameters"]   # one set of gains for every type
    design["K_torque_shortfall"] = gains["K_torque_shortfall"]  # read by ISSPG, ICPG, INWPG
    opt       = params[spec.optimization_key]
    materials = _load_json(MATERIALS_FILE)["Material_properties"]   # one table for every type
    gear_material, structure_material = (materials[name] for name in MATERIAL_MODES[material])
    gear_std  = config["Gear_standard_parameters"]
    module    = importlib.import_module(spec.module)
    single    = spec.optimizer_kind == "single"
    design_kw = "design_params" if single else "design_parameters"

    motor = load_motor(motor_name, motor_type=spec.motor_type)

    gearbox = getattr(module, spec.gearbox_cls)(
        **{design_kw: design},
        gear_standard_parameters  = gear_std,
        maxGearAllowableStressMPa = gear_material["maxAllowableStressMPa"],
        densityGears              = gear_material["density"],
        densityStructure          = structure_material["density"],
        **{kw: materials[name]["density"] for kw, name in spec.extra_gearbox_densities.items()})

    actuator_kwargs = {design_kw: design, "motor": motor, spec.gearbox_arg: gearbox}
    if spec.driver == OMIT:
        pass
    elif spec.driver is None:
        actuator_kwargs["motor_driver_params"] = None
    else:
        actuator_kwargs["motor_driver_params"] = config["Motor_drivers"][spec.driver]
    actuator_kwargs.update(FOS=config["MIT_params"]["FOS"], serviceFactor=config["MIT_params"]["serviceFactor"],
                           stressAnalysisMethodName="MIT")
    if spec.max_diameter is not None:
        actuator_kwargs["maxGearboxDiameter"] = spec.max_diameter(motor, design, opt)
    if spec.max_diameter_stage1 is not None:
        actuator_kwargs["maxGearboxDiameter_Stg1"] = spec.max_diameter_stage1(motor, design, opt)
    if spec.passes_gearbox_type:
        actuator_kwargs["insspg_type"] = gb_type
    actuator = getattr(module, spec.actuator_cls)(**actuator_kwargs)
    actuator.results_suffix = RESULTS_SUFFIX[material]

    optimizer = getattr(module, spec.optimizer_cls)(
        **{design_kw: design},
        # the single-stage optimisers spell this keyword "paramaeters"
        **{("gear_standard_paramaeters" if single else "gear_standard_parameters"): gear_std},
        K_Mass=gains["K_Mass"], K_Eff=gains["K_Eff"], K_Width=gains["K_Width"],
        **{kw: opt[key] for kw, key in OPTIMIZER_LIMITS[spec.optimizer_kind].items()},
        **{key: opt[key] for key in GEAR_RATIO_LIMITS})
    return actuator, optimizer


def run(gb_type, motor_name, gear_ratio, material="3dp"):
    """Optimise gearbox type `gb_type` for `motor_name` in a material mode ("3dp" or "metal");
    returns (total_time, opt_parameters)."""
    actuator, optimizer = build(gb_type, motor_name, material)
    return optimizer.optimizeActuator(actuator,
                                      UsePSCasVariable = 0,
                                      log              = 0,
                                      csv              = 1,
                                      printOptParams   = 1,
                                      gearRatioReq     = gear_ratio)
