from github import Github

from .app import map_ai_response_to_github_format
from .github_app_auth import get_github_token

def build_review_summary(ai_suggestions):
    """
    Build a human-readable PR review summary.
    """
    ai_suggestions = ai_suggestions or []

    counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    for item in ai_suggestions:
        severity = str(item.get("severity", "")).lower()
        if severity in counts:
            counts[severity] += 1

    if counts["critical"] > 0 or counts["high"] > 0:
        decision = "NO-GO"
        risk_level = "High"
    elif counts["medium"] > 0 or counts["low"] > 0:
        decision = "GO WITH CAUTION"
        risk_level = "Moderate"
    else:
        decision = "GO"
        risk_level = "Low"

    summary = (
        f"## PRGuardian AI Review\n\n"
        f"**Decision:** {decision}\n"
        f"**Risk Level:** {risk_level}\n\n"
        f"**Findings Summary**\n"
        f"- Critical: {counts['critical']}\n"
        f"- High: {counts['high']}\n"
        f"- Medium: {counts['medium']}\n"
        f"- Low: {counts['low']}\n"
    )

    return summary

def post_bulk_review(repo_full_name, pr_number, ai_suggestions, positions_map):
    """
    Post a GitHub PR review with AI suggestions as inline comments.

    Args:
        repo_full_name: "owner/repo"
        pr_number: PR number
        ai_suggestions: List of dicts from Azure AI
        positions_map: Parsed diff position map from orchestrator
    """
    try:
        github_token = get_github_token()
    except Exception as e:
        print(f"Error getting GitHub token: {e}")
        return

    g = Github(github_token)
    repo = g.get_repo(repo_full_name)
    pr = repo.get_pull(int(pr_number))

    github_comments = map_ai_response_to_github_format(ai_suggestions, positions_map)

    print("Mapped GitHub comments:", github_comments)

    if not github_comments:
        print("No valid inline comments to post")
        return

    commits = list(pr.get_commits())
    if not commits:
        print("Error: PR has no commits")
        return

    commit = commits[-1]

    review_body = build_review_summary(ai_suggestions)

    pr.create_review(
        commit=commit,
        body=review_body,
        event="COMMENT",
        comments=github_comments,
    )

    print(f"Review posted to PR #{pr_number} with {len(github_comments)} inline comments")


def update_github_labels(repo_full_name, pr_number, labels_to_add=None, labels_to_remove=None):
    """
    Add and/or remove labels on a pull request issue.

    Args:
        repo_full_name: "owner/repo"
        pr_number: PR number
        labels_to_add: list[str]
        labels_to_remove: list[str]
    """
    try:
        github_token = get_github_token()
    except Exception as e:
        print(f"Error getting GitHub token: {e}")
        return

    labels_to_add = labels_to_add or []
    labels_to_remove = labels_to_remove or []

    g = Github(github_token)
    repo = g.get_repo(repo_full_name)
    issue = repo.get_issue(int(pr_number))  # PRs are issues for labels

    existing_labels = [label.name for label in issue.get_labels()]

    for label in labels_to_add:
        if label not in existing_labels:
            issue.add_to_labels(label)
            print(f"Added label: {label}")

    for label in labels_to_remove:
        if label in existing_labels:
            issue.remove_from_labels(label)
            print(f"Removed label: {label}")


def run_review_and_label(repo_full_name, pr_number, ai_suggestions, positions_map):
    """
    Run the PR review workflow:
    1. Post inline review comments
    2. Update PR labels based on severity of issues found
    """
    severities = {
        str(item.get("severity", "")).lower()
        for item in (ai_suggestions or [])
    }

    has_blocking_issues = any(sev in {"critical", "high"} for sev in severities)
    has_non_blocking_issues = any(sev in {"medium", "low"} for sev in severities)

    post_bulk_review(repo_full_name, pr_number, ai_suggestions, positions_map)

    if has_blocking_issues:
        update_github_labels(
            repo_full_name,
            pr_number,
            labels_to_add=["ai-reviewed", "no-go"],
            labels_to_remove=["audit-requested", "go", "risk-found"],
        )
    elif has_non_blocking_issues:
        update_github_labels(
            repo_full_name,
            pr_number,
            labels_to_add=["ai-reviewed", "risk-found"],
            labels_to_remove=["audit-requested", "go", "no-go"],
        )
    else:
        update_github_labels(
            repo_full_name,
            pr_number,
            labels_to_add=["ai-reviewed", "go"],
            labels_to_remove=["audit-requested", "risk-found", "no-go"],
        )