from onshape_robotics_toolkit.connect import Client
from onshape_robotics_toolkit.models.document import Document

client = Client(env=".env")

doc = Document.from_url(
    url="https://cad.onshape.com/documents/694cff33a645a3e91b55a810/w/5320e7acc6e095fd21c72f77/e/3af9b6285cf609c07df3c9dd"
    )
print(doc.did, doc.wid , doc.eid)

#try:
variables = client.get_variables(
    did=doc.did,
    wid=doc.wid,
    eid=doc.eid
)
#except Exception as e:
#    print(e)

print(variables)