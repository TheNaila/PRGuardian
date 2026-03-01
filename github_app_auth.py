from __future__ import annotations

import os
import time
from pathlib import Path

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
      1) Sign a short-lived JWT with your App's private key
      2) Exchange that JWT for an installation access token
    """
    load_dotenv()

    app_id = _require_env("GITHUB_APP_ID")
    installation_id = _require_env("GITHUB_INSTALLATION_ID")
    key_path = Path(_require_env("GITHUB_PRIVATE_KEY_PATH")).expanduser()

    if not key_path.exists():
        raise RuntimeError(f"Private key file not found at: {key_path}")

    private_key_pem = key_path.read_text(encoding="utf-8")

    now = int(time.time())
    payload = {
        "iat": now - 60,          # backdate 60s to avoid clock skew issues
        "exp": now + 9 * 60,      # GitHub requires exp <= 10 minutes
        "iss": app_id,            # App ID (numeric)
    }

    app_jwt = jwt.encode(payload, private_key_pem, algorithm="RS256")

    url = f"{GITHUB_API}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    resp = requests.post(url, headers=headers, timeout=60)
    if resp.status_code >= 400:
        raise RuntimeError(f"Failed to create installation token: {resp.status_code} {resp.text}")

    data = resp.json()
    token = data.get("token")
    if not token:
        raise RuntimeError(f"No token returned. Response: {data}")

    return token


if __name__ == "__main__":
    tok = get_installation_access_token()
    print("✅ Installation access token acquired.")
    print(tok[:8] + "..." + tok[-6:])  # don't print full token