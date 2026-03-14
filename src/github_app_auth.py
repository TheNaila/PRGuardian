from __future__ import annotations

import os
import time
from pathlib import Path
import logging
import jwt  # PyJWT
import requests
from dotenv import load_dotenv


GITHUB_API = "https://api.github.com"


def _require_env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing env var: {name}")
    return v


def get_installation_access_token() -> str:
    """
    GitHub App auth flow:
    1) Sign a short-lived JWT with your App's private key (from Env Var)
    2) Exchange that JWT for an installation access token
    """
    
    # 1. Fetch credentials from Azure Environment Variables
    # Note: GITHUB_CLIENT_ID should be your App ID (numeric)
    client_id = os.environ.get("GITHUB_CLIENT_ID")
    installation_id = os.environ.get("GITHUB_INSTALLATION_ID")
    private_key_pem = os.environ.get("GITHUB_PRIVATE_KEY")

    if not all([client_id, installation_id, private_key_pem]):
        missing = [k for k, v in {
            "GITHUB_CLIENT_ID": client_id,
            "GITHUB_INSTALLATION_ID": installation_id,
            "GITHUB_PRIVATE_KEY": private_key_pem
        }.items() if not v]
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    # 2. Fix potential newline squashing from Azure Portal
    if "\\n" in private_key_pem:
        private_key_pem = private_key_pem.replace("\\n", "\n")

    # 3. Create the JWT
    now = int(time.time())
    payload = {
        "iat": now - 60,           # Backdate 60s to avoid clock skew
        "exp": now + 9 * 60,       # Max 10 mins
        "iss": client_id,          # Your App ID
    }

    try:
        app_jwt = jwt.encode(payload, private_key_pem, algorithm="RS256")
    except Exception as e:
        logging.error(f"Failed to encode JWT. Check if private key format is valid: {e}")
        raise

    # 4. Exchange JWT for an Installation Access Token
    url = f"{GITHUB_API}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    resp = requests.post(url, headers=headers, timeout=60)
    
    if resp.status_code >= 400:
        logging.error(f"GitHub Auth Error: {resp.status_code} - {resp.text}")
        raise RuntimeError(f"Failed to create installation token: {resp.status_code}")

    # 5. Extract and return the token
    data = resp.json()
    token = data.get("token")

    if not token:
        raise RuntimeError(f"No token returned from GitHub. Response: {data}")

    return token

def get_github_token() -> str:
    """
    Standard token accessor for the rest of the app.
    Currently uses GitHub App installation auth.
    """
    return get_installation_access_token()
