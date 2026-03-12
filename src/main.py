import os

from .integration import run_pr_audit


def main():
    repo_full_name = os.getenv("TEST_REPO_FULL_NAME")
    pr_number = os.getenv("TEST_PR_NUMBER")

    if not repo_full_name:
        raise ValueError("Missing TEST_REPO_FULL_NAME")
    if not pr_number:
        raise ValueError("Missing TEST_PR_NUMBER")

    run_pr_audit(
        repo_full_name=repo_full_name,
        pr_number=int(pr_number),
    )


if __name__ == "__main__":
    main()