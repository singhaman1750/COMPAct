from onshape_robotics_toolkit.connect import Client, HTTP
from onshape_robotics_toolkit.models.document import Document

client = Client(env=".env")

doc = Document.from_url(
    url="https://cad.onshape.com/documents/694cff33a645a3e91b55a810/w/5320e7acc6e095fd21c72f77/e/3af9b6285cf609c07df3c9dd"
)

print("=== BEFORE ===")
response = client.request(
    method=HTTP.GET,
    path=f"/api/variables/d/{doc.did}/w/{doc.wid}/e/{doc.eid}/variables"
)
print(response.json())

print("\n=== SETTING VARIABLE ===")


# [{"name": "one", "type": "LENGTH", "expression": "120 mm"},
#              {"name": "two", "type": "LENGTH", "expression": "120 mm"},
#              {"name": "three", "type": "LENGTH", "expression": "120 mm"},
#              {"name" : "four", "type": "LENGTH", "expression": "120 mm"}
#             ]


variables = [{'name': 'five', 'type': 'LENGTH', 'expression': '120mm'},
             {'name': 'six', 'type': 'LENGTH', 'expression': '120mm'},
             {'name': 'thee', 'type': 'LENGTH', 'expression': '120mm'},
             {'name' : 'four', 'type': 'LENGTH', 'expression': '120mm'}
            ]
print(type(variables))

response = client.request(
    method=HTTP.POST,
    path=f"/api/variables/d/{doc.did}/w/{doc.wid}/e/{doc.eid}/variables",
    body= variables
)
print(f"Status: {response.status_code}")

print("\n=== AFTER ===")
response = client.request(
    method=HTTP.GET,
    path=f"/api/variables/d/{doc.did}/w/{doc.wid}/e/{doc.eid}/variables"
)
print(response.json())