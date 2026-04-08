import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

API_KEY=os.getenv("ONSHAPE_ACCESS_KEY")
API_SECRET_KEY=os.getenv("ONSHAPE_SECRET_KEY")

if API_KEY is None or API_SECRET_KEY is None:
    raise RuntimeError("API keys not found. Check your .env file.")
