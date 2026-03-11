from onshape_robotics_toolkit.connect import Client
from onshape_robotics_toolkit.models.document import Document

# Initialize the client
client = Client(
    env="./.env"
)

# Create a Document object from a URL
doc = Document.from_url(
    url="https://cad.onshape.com/documents/694cff33a645a3e91b55a810/w/5320e7acc6e095fd21c72f77/e/6e6f59608d9e212b2b2e7d4a"
)

# Retrieve the assembly and its JSON representation
assembly = client.get_assembly(
    did=doc.did,
    wtype=doc.wtype,
    wid=doc.wid,
    eid=doc.eid
)

# Print the assembly details
print(assembly)