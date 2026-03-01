"""
INTEGRATION: How all the pieces work together in the GitHub Action workflow
"""

import os
import json
from app import parse_diff_to_positions, map_ai_response_to_github_format, post_bulk_review


def run_pr_audit(repo_full_name, pr_number, azure_ai_response_json):
    """
    Complete workflow: from Azure AI response to GitHub PR review.
    
    This is what your GitHub Action will call!
    
    Args:
        repo_full_name: "owner/repo"
        pr_number: 123
        azure_ai_response_json: JSON from Azure AI with findings
    """
    
    print(f"\n{'='*70}")
    print(f" PRGuardian Audit: {repo_full_name} PR #{pr_number}")
    print(f"{'='*70}\n")
    
    try:
        # Step 1: Call post_bulk_review which internally:
        #   - Fetches the diff
        #   - Parses it to positions
        #   - Converts AI response
        #   - Posts to GitHub
        post_bulk_review(repo_full_name, pr_number, azure_ai_response_json)
        
        print(f"\n Audit complete!\n")
        return True
        
    except Exception as e:
        print(f"\n Audit failed: {e}\n")
        return False


# ═════════════════════════════════════════════════════════════════════════════
# EXAMPLE: What your GitHub Action workflow will look like
# ═════════════════════════════════════════════════════════════════════════════

"""
In .github/workflows/audit.yml:

name: PRGuardian Audit
on:
  pull_request:
    types: [labeled]

jobs:
  audit:
    if: github.event.label.name == 'audit-requested'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install PyGithub azure-ai-projects requests
      
      - name: Run PRGuardian audit
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          AZURE_API_KEY: ${{ secrets.AZURE_API_KEY }}
        run: |
          python -c "
import json
import os
from app import parse_diff_to_positions, map_ai_response_to_github_format, post_bulk_review

# 1. Naila: Fetch PR diff
# (Naila's responsibility - shown here for context)
# diff = fetch_pr_diff(...)

# 2. Naila: Send to Azure
# (Naila's responsibility)
# ai_response = call_azure_api(diff, system_prompt)

# 3. Amy: Receive from Azure
# Example response from Azure:
ai_response = [
    {
        'file_path': 'src/app.py',
        'line_number': 15,
        'severity': 'error',
        'comment': 'Variable not defined before use'
    },
    {
        'file_path': 'tests/test_app.py',
        'line_number': 8,
        'severity': 'warning',
        'comment': 'Missing docstring for function'
    }
]

# 4. VJ: Convert and post
repo_full_name = '${{ github.repository }}'
pr_number = ${{ github.event.pull_request.number }}

from integration import run_pr_audit
run_pr_audit(repo_full_name, pr_number, ai_response)
          "
"""


# ═════════════════════════════════════════════════════════════════════════════
# TESTING: Simulate the entire workflow locally
# ═════════════════════════════════════════════════════════════════════════════

def test_complete_workflow():
    """
    Test the complete workflow with fake data.
    """
    
    # Simulate what Azure AI would return
    azure_ai_findings = [
        {
            "file_path": "src/config.py",
            "line_number": 8,
            "severity": "error",
            "comment": "DEBUG mode should be False for production"
        },
        {
            "file_path": "src/config.py",
            "line_number": 12,
            "severity": "info",
            "comment": "Consider adding error handling"
        }
    ]
    
    # Simulate a sample diff
    sample_diff = """diff --git a/src/config.py b/src/config.py
index 1234567..abcdefg 100644
--- a/src/config.py
+++ b/src/config.py
@@ -5,10 +5,11 @@ import os
 # Configuration file
 MAX_RETRIES = 3
 TIMEOUT = 30
-DEBUG = True
+DEBUG = False
 
 def load_config():
     \"\"\"Load configuration from environment.\"\"\"
+    print("Loading config...")
     return {
         "max_retries": MAX_RETRIES,
         "timeout": TIMEOUT,
"""
    
    print(" TEST: Simulating complete workflow")
    print("=" * 70)
    
    # Step 1: Parse diff
    print("\n1️.  Parsing diff...")
    positions_map = parse_diff_to_positions(sample_diff)
    
    for file_path, line_map in positions_map.items():
        print(f"   {file_path}:")
        for line_num, pos in sorted(line_map.items()):
            print(f"     Line {line_num:3d} → Position {pos:2d}")
    
    # Step 2: Convert AI response
    print("\n2️.  Converting AI response to GitHub format...")
    github_comments = map_ai_response_to_github_format(azure_ai_findings, positions_map)
    
    for i, comment in enumerate(github_comments, 1):
        print(f"\n   Comment {i}:")
        print(f"   Path: {comment['path']}")
        print(f"   Position: {comment['position']}")
        print(f"   Body: {comment['body']}")
    
    # Step 3: Show what would be posted
    print("\n3️.  Review that would be posted to GitHub:")
    payload = {
        "commit_id": "abc123def456example",
        "body": "PRGuardian AI Review: Issues detected",
        "event": "COMMENT",
        "comments": github_comments
    }
    print(json.dumps(payload, indent=2))
    
    print("\n TEST PASSED!")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("PRGuardian VJ Integration Module")
    print("="*70)
    print("\nRunning local workflow test...\n")
    test_complete_workflow()
    print("\n" + "="*70)
    print("Ready for GitHub Actions integration!")
    print("="*70)
