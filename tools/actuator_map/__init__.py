"""Actuator map for co-design: (motor, gear ratio, material) -> optimal COMPAct actuator.

sweep.py runs the optimiser over a grid; case.py runs one case; geometry.py gives the
whole-actuator width and diameter from the CAD variables. Built only on top of the optimiser
(gearbox_runner), so the normal COMPAct workflow is unchanged.
"""
