from src.onshape_client import Client, HTTP, Document
from parse_variables_txt import parse_variable_file

import os


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

variables_to_set = parse_variable_file("sspg_equations.txt")

# variables_to_set = [{'name': 'five', 'type': 'LENGTH', 'expression': '120mm'},
#              {'name': 'six', 'type': 'LENGTH', 'expression': '120mm'},
#              {'name': 'thee', 'type': 'LENGTH', 'expression': '120mm'},
#              {'name' : 'four', 'type': 'LENGTH', 'expression': '120mm'}
#             ]

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










