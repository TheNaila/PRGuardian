from __future__ import annotations

import os
import requests
from dotenv import load_dotenv

from github_app_auth import get_installation_access_token


def fetch_pr_diff(owner: str, repo: str, pr_number: int) -> str:
    token = get_installation_access_token()
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.diff",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    # GitHub returns the diff when you request the PR endpoint with diff media type
    resp = requests.get(url, headers=headers, timeout=60)
    resp.raise_for_status()
    if not resp.text.strip():
        raise RuntimeError("Empty diff returned.")
    return resp.text


if __name__ == "__main__":
    load_dotenv()
    owner = os.environ["GITHUB_OWNER"]
    repo = os.environ["GITHUB_REPO"]
    pr_number = int(os.environ["GITHUB_PR_NUMBER"])

    diff = fetch_pr_diff(owner, repo, pr_number)
    print("✅ Diff length:", len(diff))
    print(diff[:1000])  # preview