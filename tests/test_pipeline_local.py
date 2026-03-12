from src.app import parse_diff_to_positions
from src.azure_review import review_pr_diff
from src.policy_search import search_policy_snippets
from src.github_actions import build_review_summary

with open("tests/fixtures/sample_pr.diff") as f:
    diff_text = f.read()

positions_map = parse_diff_to_positions(diff_text)
print("Files parsed:", list(positions_map.keys()))

policy_snippets = search_policy_snippets(diff_text)
print("Policies found:", len(policy_snippets))

findings = review_pr_diff(diff_text, policy_snippets=policy_snippets)
print("Findings:", findings)

summary = build_review_summary(findings)
print(summary)