"""
Minimal Onshape API client — extracted from onshape-robotics-toolkit.

Contains only what's needed to:
  - Authenticate and make signed API requests
  - Parse a Document from a CAD URL

Classes:
    HTTP     — HTTP method enum (GET, POST, DELETE)
    Document — Parses an Onshape URL into its did/wtype/wid/eid parts
    Client   — Signs and sends requests to the Onshape REST API
"""

import base64
import datetime
import hashlib
import hmac
import os
import secrets
import string
import requests
from enum import Enum
from typing import Any, Optional, Union
from urllib.parse import parse_qs, urlencode, urlparse



# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_URL = "https://cad.onshape.com"
ONSHAPE_ACCESS_KEY = "ONSHAPE_ACCESS_KEY"
ONSHAPE_SECRET_KEY = "ONSHAPE_SECRET_KEY"


# ---------------------------------------------------------------------------
# HTTP enum
# ---------------------------------------------------------------------------

class HTTP(str, Enum):
    """Enumerates the possible HTTP methods."""
    GET    = "get"
    POST   = "post"
    DELETE = "delete"


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------

class Document:
    """
    Represents an Onshape document parsed from its CAD URL.

    Attributes:
        did   (str): Document ID
        wtype (str): Workspace type — 'w' (workspace), 'v' (version), or 'm' (microversion)
        wid   (str): Workspace / version / microversion ID
        eid   (str): Element ID
        url   (str): Original URL

    Examples:
        >>> doc = Document.from_url(
        ...     "https://cad.onshape.com/documents/c1aac326515ba734f63b9b3f"
        ...     "/w/f9cccd7b90ce6d7934076c7c/e/11d494d64974a13f1ae2def2"
        ... )
        >>> doc.did
        'c1aac326515ba734f63b9b3f'
    """

    def __init__(self, did: str, wtype: str, wid: str, eid: str, url: str = "") -> None:
        self.did   = did
        self.wtype = wtype
        self.wid   = wid
        self.eid   = eid
        self.url   = url

    @classmethod
    def from_url(cls, url: str) -> "Document":
        """
        Parse an Onshape document URL into its component IDs.

        The expected URL format is:
            https://cad.onshape.com/documents/{did}/{wtype}/{wid}/e/{eid}

        Args:
            url: Full Onshape document URL.

        Returns:
            Document instance.

        Raises:
            ValueError: If the URL cannot be parsed into the expected segments.
        """
        parsed = urlparse(url)
        parts  = parsed.path.strip("/").split("/")

        # Expected: ['documents', did, wtype, wid, 'e', eid]
        try:
            doc_idx = parts.index("documents")
            did     = parts[doc_idx + 1]
            wtype   = parts[doc_idx + 2]   # 'w', 'v', or 'm'
            wid     = parts[doc_idx + 3]
            # next segment should be 'e'
            eid     = parts[doc_idx + 5]
        except (ValueError, IndexError) as exc:
            raise ValueError(
                f"Could not parse Onshape URL: {url!r}. "
                "Expected format: .../documents/{{did}}/{{wtype}}/{{wid}}/e/{{eid}}"
            ) from exc

        return cls(did=did, wtype=wtype, wid=wid, eid=eid, url=url)

    def __repr__(self) -> str:
        return (
            f"Document(did={self.did!r}, wtype={self.wtype!r}, "
            f"wid={self.wid!r}, eid={self.eid!r})"
        )


# ---------------------------------------------------------------------------
# Key loading helpers
# ---------------------------------------------------------------------------

def _load_from_env_file(env_path: str, key: str) -> str:
    """Read a key=value pair from a .env file."""
    if not os.path.isfile(env_path):
        raise FileNotFoundError(f"Environment file not found: {env_path!r}")

    with open(env_path) as fh:
        for line in fh:
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            if k.strip() == key:
                return v.strip().strip('"').strip("'")

    raise ValueError(f"Key {key!r} not found in {env_path!r}")


def _load_keys(env: Optional[str]) -> tuple[str, str]:
    """Return (access_key, secret_key) from a .env file or environment variables."""
    if env is not None:
        access = _load_from_env_file(env, ONSHAPE_ACCESS_KEY)
        secret = _load_from_env_file(env, ONSHAPE_SECRET_KEY)
    else:
        access = os.environ.get(ONSHAPE_ACCESS_KEY, "")
        secret = os.environ.get(ONSHAPE_SECRET_KEY, "")

    if not access or not secret:
        raise ValueError(
            f"Missing Onshape API keys. "
            f"Set {ONSHAPE_ACCESS_KEY} and {ONSHAPE_SECRET_KEY} in your environment or .env file."
        )

    return access, secret


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class Client:
    """
    Minimal Onshape REST API client with HMAC-SHA256 authentication.

    Args:
        env      (str | None): Path to a .env file containing API keys.
                               If None, keys are read from environment variables.
        base_url (str):        Onshape API base URL.

    Examples:
        >>> client = Client(env=".env")
        >>> response = client.request(HTTP.GET, "/api/documents/abc123")
    """

    def __init__(
        self,
        env: Optional[str] = None,
        base_url: str = BASE_URL,
    ) -> None:
        self._url = base_url
        self._access_key, self._secret_key = _load_keys(env)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def request(
        self,
        method: HTTP,
        path: str,
        query: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, Any]] = None,
        body: Optional[Union[dict, list]] = None,
        base_url: Optional[str] = None,
        log_response: bool = True,
        timeout: int = 50,
    ) -> requests.Response:
        """
        Send a signed request to the Onshape API.

        Args:
            method:       HTTP method (HTTP.GET / HTTP.POST / HTTP.DELETE).
            path:         API path, e.g. '/api/variables/d/{did}/w/{wid}/e/{eid}/variables'.
            query:        Optional query-string parameters.
            headers:      Optional extra request headers.
            body:         Optional JSON body (dict or list).
            base_url:     Override the base URL for this request.
            log_response: Print a brief status line after the call.
            timeout:      Request timeout in seconds.

        Returns:
            requests.Response
        """
        query    = query   or {}
        headers  = headers or {}
        base_url = base_url or self._url

        req_headers = self._make_headers(method, path, query, headers)
        url         = base_url + path + "?" + urlencode(query)

        response = requests.request(
            method,
            url,
            headers=req_headers,
            json=body,
            allow_redirects=False,
            stream=True,
            timeout=timeout,
        )

        # Follow a single 307 redirect (Onshape sometimes re-routes requests)
        if response.status_code == 307:
            response = self._handle_redirect(response, method, headers, log_response, timeout)

        if log_response:
            print(f"[{method.upper()}] {path}  →  {response.status_code}")

        return response

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _handle_redirect(
        self,
        res: requests.Response,
        method: HTTP,
        headers: dict[str, Any],
        log_response: bool,
        timeout: int,
    ) -> requests.Response:
        location    = urlparse(res.headers["Location"])
        querystring = parse_qs(location.query)
        new_query   = {k: v[0] for k, v in querystring.items()}
        new_base    = location.scheme + "://" + location.netloc
        return self.request(
            method,
            location.path,
            query=new_query,
            headers=headers,
            base_url=new_base,
            log_response=log_response,
            timeout=timeout,
        )

    def _make_nonce(self) -> str:
        chars = string.digits + string.ascii_letters
        return "".join(secrets.choice(chars) for _ in range(25))

    def _make_auth(
        self,
        method: HTTP,
        date: str,
        nonce: str,
        path: str,
        query: dict[str, Any],
        ctype: str = "application/json",
    ) -> str:
        query_string = urlencode(query)
        # Must match original exactly: method + "\n" + nonce + "\n" + date + "\n" +
        # ctype + "\n" + path + "\n" + query_string + "\n", then lowercased as a whole
        hmac_str = (
            str(method + "\n" + nonce + "\n" + date + "\n" + ctype + "\n" + path + "\n" + query_string + "\n")
            .lower()
            .encode("utf-8")
        )
        signature = base64.b64encode(
            hmac.new(self._secret_key.encode("utf-8"), hmac_str, digestmod=hashlib.sha256).digest()
        )
        return "On " + self._access_key + ":HmacSHA256:" + signature.decode("utf-8")

    def _make_headers(
        self,
        method: HTTP,
        path: str,
        query: dict[str, Any],
        extra_headers: dict[str, Any],
    ) -> dict[str, Any]:
        date  = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        nonce = self._make_nonce()
        ctype = extra_headers.get("Content-Type", "application/json")

        headers = {
            "Content-Type": "application/json",
            "Date":         date,
            "On-Nonce":     nonce,
            "Authorization": self._make_auth(method, date, nonce, path, query, ctype),
            "User-Agent":   "Onshape Python Client",
            "Accept":       "application/json",
        }
        headers.update(extra_headers)
        return headers