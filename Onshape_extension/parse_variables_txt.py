import re

def parse_variable_file(filepath):
    variables = []

    NUMBER_VARS = {
        "pattern_num_bulge",
        "motor_mount_hole_num",
        "Ns",
        "Np",
        "Nr",
        "Np_b",
        "Np_s",
        "num_planet",
        "motor_output_hole_num",
        "Nr_b",
        "Nr_s",
        "small_ring_output_wall_to_bearing_shaft_attachement_hole_num",
        "a1_pattern_num_bulge",
        "a2_pattern_num_bulge",
        "a1_motor_output_hole_num",
        "a1_motor_mount_hole_num",
        "a1_num_planet",
        "a1_Nr",
        "a2_Nr",
        "a2_Nr1",
        "a1_Nr2",
        "a1_Np",
        "a2_Np",
        "a2_Np1",
        "a1_Np2",
        "a1_Ns",
        "a2_Ns",
        "a2_Ns1",
        "a1_Ns2",
        "a2_num_planet",
        "motor_rotor_hole_num",
        "stator_ring_hub_hole_num",
        "magnet_mount_num_hole",
        "ring_hub_to_case_hole_num",
        "magnet_pattern_bulge_number",
        "motor_mount_driver_hole_num",
    }

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()

            if not line or line in ["{", "}"]:
                continue

            match = re.match(r'"(.+?)"\s*=\s*(.+)', line)
            if not match:
                continue

            name = match.group(1)
            value = match.group(2).strip()

            if name in NUMBER_VARS:
                variables.append({
                    "name": name,
                    "type": "NUMBER",
                    "expression": value
                })
                continue


            if "deg" in value:
                var_type = "ANGLE"
                expression = value
            else:
                var_type = "LENGTH"

                if not any(u in value for u in ["mm", "cm", "m", "in"]):
                    expression = f"{value} mm"
                else:
                    expression = value

            variables.append({
                "name": name,
                "type": var_type,
                "expression": expression
            })

    return variables
