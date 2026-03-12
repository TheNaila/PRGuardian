import requests

from .github_app_auth import get_github_token


def fetch_pr_diff(repo_full_name: str, pr_number: int) -> str:
    """
    Retrieve the raw diff for a pull request.

    Args:
        repo_full_name: "owner/repo"
        pr_number: PR number

    Returns:
        Raw diff text
    """

    github_token = get_github_token()

    headers = {
        "Accept": "application/vnd.github.v3.diff",
        "Authorization": f"token {github_token}",
    }

    url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}"

    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to fetch PR diff: {response.status_code} {response.text}"
        )

    return response.text