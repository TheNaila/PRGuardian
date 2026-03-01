from azure_review import analyze_diff_with_gpt4o
from fetch_pr_diff import fetch_pr_diff
import os
from dotenv import load_dotenv

load_dotenv()

owner = os.getenv("GITHUB_OWNER")
repo = os.getenv("GITHUB_REPO")
pr_number = int(os.getenv("GITHUB_PR_NUMBER"))

diff_text = fetch_pr_diff(owner, repo, pr_number)

review = analyze_diff_with_gpt4o(diff_text)

print(review)