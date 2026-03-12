from .app import parse_diff_to_positions
from .azure_review import review_pr_diff
from .fetch_pr_diff import fetch_pr_diff
from .github_actions import run_review_and_label
from .policy_search import search_policy_snippets


def run_pr_guardian_workflow(repo_full_name, pr_number):
    """
    Core PRGuardian workflow orchestrator.

    Flow:
    - fetch PR diff
    - parse diff positions
    - retrieve relevant policy snippets
    - run AI review
    - send findings + positions to GitHub action layer
    """

    diff_text = fetch_pr_diff(repo_full_name, pr_number)
    positions_map = parse_diff_to_positions(diff_text)

    print("\nFetched PR diff successfully.")
    print(f"Diff length: {len(diff_text)} characters")
    print(f"Parsed positions for files: {list(positions_map.keys())}")

    policy_snippets = search_policy_snippets(diff_text)
    print(f"Policy snippets retrieved: {len(policy_snippets)}")

    findings = review_pr_diff(diff_text, policy_snippets=policy_snippets)
    print(f"AI findings returned: {len(findings)}")

    run_review_and_label(
        repo_full_name=repo_full_name,
        pr_number=pr_number,
        ai_suggestions=findings,
        positions_map=positions_map,
    )

    return True