from .orchestrator import run_pr_guardian_workflow

"""
INTEGRATION: Entry point for running the PRGuardian audit workflow.
"""


def run_pr_audit(repo_full_name, pr_number):
    """
    Main workflow called by GitHub Action.

    Args:
        repo_full_name: "owner/repo"
        pr_number: PR number
    """

    print(f"\n{'='*70}")
    print(f"PRGuardian Audit: {repo_full_name} PR #{pr_number}")
    print(f"{'='*70}\n")

    try:
        result = run_pr_guardian_workflow(
            repo_full_name=repo_full_name,
            pr_number=pr_number,
        )

        print("\nAudit complete!\n")
        return result

    except Exception as e:
        print(f"\nAudit failed: {e}\n")
        return False