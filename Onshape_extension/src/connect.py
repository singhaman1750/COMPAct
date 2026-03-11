import hmac
import hashlib
import base64
import os
from datetime import datetime
from urllib.parse import urlparse
import requests
from dotenv import load_dotenv


class HTTP:
    """HTTP method constants"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class Document:
    """Parse and store Onshape document information from URL"""
    
    def __init__(self, did, wid, eid):
        self.did = did  # document ID
        self.wid = wid  # workspace ID
        self.eid = eid  # element ID
    
    @classmethod
    def from_url(cls, url):
        """
        Extract document IDs from Onshape URL
        
        URL format: https://cad.onshape.com/documents/{DID}/w/{WID}/e/{EID}
        """
        try:
            # Remove query parameters if any
            url = url.split('?')[0]
            
            # Parse the URL path
            parts = url.split('/')
            
            # Find indices of 'documents', 'w', and 'e'
            doc_idx = parts.index('documents')
            w_idx = parts.index('w')
            e_idx = parts.index('e')
            
            # Extract IDs
            did = parts[doc_idx + 1]
            wid = parts[w_idx + 1]
            eid = parts[e_idx + 1]
            
            return cls(did, wid, eid)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid Onshape URL format: {url}") from e
    
    def __repr__(self):
        return f"Document(did={self.did}, wid={self.wid}, eid={self.eid})"


class Client:
    """Onshape API client with HMAC authentication"""
    
    BASE_URL = "https://api.onshape.com"
    
    def __init__(self, env=None, api_key=None, api_secret=None):
        """
        Initialize Onshape API client
        
        Args:
            env: Path to .env file (default: ".env")
            api_key: API key (if not using .env)
            api_secret: API secret (if not using .env)
        """
        if api_key and api_secret:
            self.api_key = api_key
            self.api_secret = api_secret
        else:
            # Load from .env file
            env_file = env or ".env"
            load_dotenv(env_file)
            self.api_key = os.getenv("ONSHAPE_ACCESS_KEY")
            self.api_secret = os.getenv("ONSHAPE_SECRET_KEY")
            
            if not self.api_key or not self.api_secret:
                raise ValueError(
                    "API key and secret not found. "
                    "Set ONSHAPE_ACCESS_KEY and ONSHAPE_SECRET_KEY in .env file"
                )
    
    def _get_auth_header(self, method, path, body=None):
        """
        Generate HMAC-SHA256 authorization header for Onshape API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path (e.g., /api/variables/...)
            body: Request body (dict or JSON string)
        
        Returns:
            Authorization header value
        """
        # Get current timestamp in RFC 3339 format (Onshape requirement)
        now = datetime.utcnow()
        date_str = now.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
        
        # Convert body to string if needed
        if body is None:
            body_str = ""
        elif isinstance(body, dict):
            import json
            body_str = json.dumps(body)
        else:
            body_str = str(body)
        
        # Create signature string: METHOD\nPATH\nDATE\nBODYHASH
        body_hash = hashlib.sha256(body_str.encode()).hexdigest()
        signature_string = f"{method}\n{path}\n{date_str}\n{body_hash}"
        
        # Create HMAC-SHA256 signature
        signature = hmac.new(
            self.api_secret.encode(),
            signature_string.encode(),
            hashlib.sha256
        ).digest()
        signature_b64 = base64.b64encode(signature).decode()
        
        # Format authorization header
        auth_header = f"On {self.api_key}:HmacSHA256:{signature_b64}"
        
        return auth_header, date_str
    
    def request(self, method, path, body=None, **kwargs):
        """
        Make authenticated request to Onshape API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            path: API path (e.g., /api/variables/d/{did}/w/{wid}/e/{eid}/variables)
            body: Request body (dict or JSON)
            **kwargs: Additional arguments to pass to requests
        
        Returns:
            Response object
        """
        url = self.BASE_URL + path
        
        # Generate authentication
        auth_header, date_str = self._get_auth_header(method, path, body)
        
        # Prepare headers
        headers = {
            "Authorization": auth_header,
            "X-Onshape-API-Date": date_str,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Add any additional headers from kwargs
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))
        
        # Make the request
        if method == HTTP.GET:
            response = requests.get(url, headers=headers, **kwargs)
        elif method == HTTP.POST:
            response = requests.post(url, json=body, headers=headers, **kwargs)
        elif method == HTTP.PUT:
            response = requests.put(url, json=body, headers=headers, **kwargs)
        elif method == HTTP.DELETE:
            response = requests.delete(url, headers=headers, **kwargs)
        elif method == HTTP.PATCH:
            response = requests.patch(url, json=body, headers=headers, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        return response
    
    def get_variables(self, did, wid, eid):
        """
        Get all variables from a document
        
        Args:
            did: Document ID
            wid: Workspace ID
            eid: Element ID
        
        Returns:
            JSON response with variables
        """
        path = f"/api/variables/d/{did}/w/{wid}/e/{eid}/variables"
        response = self.request(HTTP.GET, path)
        response.raise_for_status()  # Raise error if request failed
        return response.json()
    
    def set_variables(self, did, wid, eid, variables):
        """
        Set variables in a document
        
        Args:
            did: Document ID
            wid: Workspace ID
            eid: Element ID
            variables: List of variable dicts with 'name', 'type', 'expression'
        
        Returns:
            Response object
        """
        path = f"/api/variables/d/{did}/w/{wid}/e/{eid}/variables"
        response = self.request(HTTP.POST, path, body=variables)
        response.raise_for_status()
        return response
