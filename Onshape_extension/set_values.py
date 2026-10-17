"""
Push an optimiser result (CADs/<FAMILY>/<family>_equations_onshape.txt) into the
gearbox's Onshape Variable Studio.

Set up once:
  - Onshape_extension/.env                 your API keys (ONSHAPE_ACCESS_KEY / ONSHAPE_SECRET_KEY)
  - Onshape_extension/onshape_models.json  one Variable Studio URL per gearbox type
                                           (copy onshape_models.example.json)

Then:
    python Onshape_extension/set_values.py --gb_type sspg
or optimise and push in one go:
    python actOpt.py --motor U8_Lite --gb_type sspg --gr 6.5 --onshape

Before writing, an Onshape version (a named snapshot you can roll back to) is saved,
unless --no-version is given. After writing, the values are read back and any variable
that did not take is listed.
"""

import argparse
import datetime
import json
import os
import re
import sys

EXT_DIR     = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT   = os.path.dirname(EXT_DIR)
MODELS_JSON = os.path.join(EXT_DIR, "onshape_models.json")
ENV_FILE    = os.path.join(EXT_DIR, ".env")

# Variants share their family's CAD folder and equations file.
_VARIANT_SUFFIX = re.compile(r"_(type_\d+|dependent|independent|inside|compact)$")


def gearbox_family(gb_type):
    return _VARIANT_SUFFIX.sub("", gb_type).upper()


def equations_file(gb_type):
    """The Onshape equations file the optimiser writes for this gearbox type."""
    family = gearbox_family(gb_type)
    return os.path.join(REPO_ROOT, "CADs", family, f"{family.lower()}_equations_onshape.txt")


def model_url(gb_type, path=MODELS_JSON):
    """The Variable Studio URL of your Onshape copy for this gearbox type."""
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"{path} not found. Copy onshape_models.example.json to onshape_models.json "
            "and paste your Variable Studio URLs into it.")
    with open(path, "r") as models_file:
        urls = json.load(models_file)
    url = urls.get(gb_type, "")
    if not url.startswith("https://"):
        raise ValueError(f"No Onshape model set for {gb_type!r} in {path}.")
    return url


def _variables_by_name(response_json):
    """name -> expression from a Variable Studio GET response (any nesting)."""
    found = {}

    def walk(node):
        if isinstance(node, dict):
            if "name" in node and "expression" in node:
                found[node["name"]] = node["expression"]
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(response_json)
    return found


def _same_expression(a, b):
    return re.sub(r"\s+", "", str(a)) == re.sub(r"\s+", "", str(b))


def push_to_onshape(gb_type, save_version=True, models_json=MODELS_JSON):
    """Write the gearbox type's equations file into its Onshape Variable Studio.

    Returns the names of variables whose value in Onshape does not match afterwards.
    """
    if EXT_DIR not in sys.path:
        sys.path.insert(0, EXT_DIR)
    from parse_variables_txt import parse_variable_file
    from src.onshape_client import HTTP, Client, Document

    url = model_url(gb_type, models_json)
    doc = Document.from_url(url)
    if doc.wtype != "w":
        raise ValueError(f"The URL for {gb_type!r} points to a version, not a workspace (/w/): {url}")
    eq_file = equations_file(gb_type)
    variables = parse_variable_file(eq_file)
    client = Client(env=ENV_FILE)
    variables_path = f"/api/variables/d/{doc.did}/w/{doc.wid}/e/{doc.eid}/variables"

    shown = os.path.relpath(eq_file, REPO_ROOT) if eq_file.startswith(REPO_ROOT) else eq_file
    print(f"Onshape: pushing {len(variables)} variables from {shown}")
    if save_version:
        name = f"before {gb_type} push {datetime.datetime.now():%Y-%m-%d %H:%M:%S}"
        response = client.request(
            HTTP.POST, f"/api/documents/d/{doc.did}/versions",
            body={"documentId": doc.did, "workspaceId": doc.wid, "name": name},
            log_response=False)
        if not 200 <= response.status_code < 300:
            raise RuntimeError(f"Could not save a version before writing (HTTP {response.status_code}): "
                               f"{response.text[:300]}. Nothing was changed.")
        print(f"Onshape: saved version '{name}'")

    response = client.request(HTTP.POST, variables_path, body=variables, log_response=False)
    if not 200 <= response.status_code < 300:  # Onshape answers 204 (no content) on success
        raise RuntimeError(f"Onshape rejected the variables (HTTP {response.status_code}): {response.text[:300]}")

    response = client.request(HTTP.GET, variables_path, log_response=False)
    in_onshape = _variables_by_name(response.json())
    mismatched = [v["name"] for v in variables
                  if v["name"] not in in_onshape or not _same_expression(in_onshape[v["name"]], v["expression"])]
    print(f"Onshape: {len(variables) - len(mismatched)} of {len(variables)} variables set")
    for name in mismatched:
        print(f"  not set as expected: {name} = {in_onshape.get(name, '(missing in Onshape)')}")
    return mismatched


def main(argv=None):
    parser = argparse.ArgumentParser(description="Push an optimiser result into its Onshape model.")
    parser.add_argument("--gb_type", required=True, help="Gearbox type, e.g. sspg, icpg, insspg_type_1")
    parser.add_argument("--no-version", action="store_true", help="do not save an Onshape version first")
    args = parser.parse_args(argv)
    push_to_onshape(args.gb_type, save_version=not args.no_version)


if __name__ == "__main__":
    main()
