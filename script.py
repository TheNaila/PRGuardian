from src.azure_review import analyze_diff_with_gpt4o
from src.fetch_pr_diff import fetch_pr_diff
from src.policy_search import get_top_policy_snippets
import os
from dotenv import load_dotenv

load_dotenv()

owner = os.getenv("GITHUB_OWNER")
repo = os.getenv("GITHUB_REPO")
pr_number = int(os.getenv("GITHUB_PR_NUMBER"))

diff_text = fetch_pr_diff(owner, repo, pr_number)

policy_snippets = get_top_policy_snippets(diff_text, top_k=3)

print(policy_snippets)

review = analyze_diff_with_gpt4o(diff_text, policy_snippets)

print(review)