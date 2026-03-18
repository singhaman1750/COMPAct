from src.onshape_client import Client, HTTP, Document
from parse_variables_txt import parse_variable_file

import os

# Configuration: Specify the gearbox type or full path
GEARBOX_TYPE = "SSPG"  # Options: SSPG, DSPG, CPG, WPG
# Or use full path: EQUATIONS_PATH = "/absolute/path/to/equations.txt"

# Get the path to the equations file relative to project root
current_dir = os.path.dirname(__file__)
project_root = os.path.dirname(current_dir)
equations_file = os.path.join(project_root, "CADs", GEARBOX_TYPE.upper(), f"{GEARBOX_TYPE.lower()}_equations.txt")

client = Client(env=os.path.join(os.path.dirname(__file__), ".env"))

doc = Document.from_url(
    url="https://cad.onshape.com/documents/c1aac326515ba734f63b9b3f/w/f9cccd7b90ce6d7934076c7c/e/11d494d64974a13f1ae2def2"
)

print("=== BEFORE ===")
response = client.request(
    method=HTTP.GET,
    path=f"/api/variables/d/{doc.did}/w/{doc.wid}/e/{doc.eid}/variables"
)
print(response.json())

print("\n=== SETTING VARIABLE ===")

variables_to_set = parse_variable_file(equations_file)

response = client.request(
    method=HTTP.POST,
    path=f"/api/variables/d/{doc.did}/w/{doc.wid}/e/{doc.eid}/variables",
    body=variables_to_set
)
print(f"Status: {response.status_code}")

print("\n=== AFTER ===")
response = client.request(
    method=HTTP.GET,
    path=f"/api/variables/d/{doc.did}/w/{doc.wid}/e/{doc.eid}/variables"
)
print(response.json())










