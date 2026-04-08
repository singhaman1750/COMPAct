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
        "ring_OD",
        "Nr_b",
        "Nr_s",
        "small_ring_output_wall_to_bearing_shaft_attachement_hole_num"
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
