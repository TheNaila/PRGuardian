"""
MODULE: github_review_api.py

Complete reference implementation for VJ's GitHub Review API integration.
This shows exact API payloads and authentication.
"""

import requests
import json
import os


class GitHubReviewAPI:
    """
    Wrapper for GitHub Pull Request Review API.
    Handles authentication and formatting for posting reviews.
    """
    
    def __init__(self, github_token):
        """
        Initialize with GitHub token.
        
        Args:
            github_token: GitHub Personal Access Token or GITHUB_TOKEN env var
        """
        self.token = github_token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {github_token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    
    def get_pr_diff(self, owner, repo, pull_number):
        """
        Fetch the raw diff of a pull request.
        
        Returns the diff as plain text that can be parsed.
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pull_number}"
        
        # Important: Override Accept header for diff
        headers = self.headers.copy()
        headers["Accept"] = "application/vnd.github.v3.diff"
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    
    def post_review(self, owner, repo, pull_number, commit_sha, review_body, comments, event="COMMENT"):
        """
        Post a review with inline comments to a GitHub PR.
        
        Args:
            owner: Repository owner
            repo: Repository name  
            pull_number: PR number
            commit_sha: Latest commit SHA to anchor review to
            review_body: Main review message (shown above inline comments)
            comments: List of comment dicts with 'path', 'position', 'body'
            event: One of "COMMENT", "APPROVE", "REQUEST_CHANGES"
        
        Example comments list:
        [
            {
                "path": "src/app.py",
                "position": 5,
                "body": "**[ERROR]** This line has a bug"
            },
            {
                "path": "src/utils.py", 
                "position": 12,
                "body": "**[WARNING]** Consider refactoring"
            }
        ]
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pull_number}/reviews"
        
        payload = {
            "commit_id": commit_sha,
            "body": review_body,
            "event": event,
            "comments": comments
        }
        
        print(f"   Posting review to {owner}/{repo} PR #{pull_number}")
        print(f"   Commit: {commit_sha}")
        print(f"   Event: {event}")
        print(f"   Comments: {len(comments)}")
        
        response = requests.post(url, headers=self.headers, json=payload)
        
        if response.status_code != 200:
            print(f" Error: {response.status_code}")
            print(response.json())
            response.raise_for_status()
        
        result = response.json()
        print(f" Review posted! ID: {result.get('id')}")
        return result


# ============================================================================
# EXAMPLE: How to use this module
# ============================================================================

if __name__ == "__main__":
    # Setup
    github_token = os.getenv("GITHUB_TOKEN")
    api = GitHubReviewAPI(github_token)
    
    # Parameters
    owner = "your-org"
    repo = "your-repo"
    pull_number = 42
    
    # Step 1: Get the diff
    print("1.  Fetching PR diff...")
    diff = api.get_pr_diff(owner, repo, pull_number)
    
    # Step 2: Parse diff and map line numbers to positions
    # (This would use parse_diff_to_positions from app.py)
    print("2️.  Parsing diff to map positions...")
    # positions_map = parse_diff_to_positions(diff)
    
    # Step 3: Create comments from AI suggestions
    # (This would use map_ai_response_to_github_format)
    print("3️.  Converting AI suggestions to GitHub format...")
    # comments = [
    #     {
    #         "path": "src/app.py",
    #         "position": 5,
    #         "body": "**[ERROR]** Variable not defined"
    #     }
    # ]
    
    # Step 4: Post the review
    # print("4️.  Posting review to GitHub...")
    # commit_sha = "abcdef123456"  # Get from PR commits
    # api.post_review(
    #     owner, repo, pull_number, commit_sha,
    #     "PRGuardian AI Review",
    #     comments,
    #     event="COMMENT"
    # )
    
    print("\n  This is a reference implementation. See app.py for full integration.")


# ============================================================================
# GITHUB API REFERENCE
# ============================================================================

"""
POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews

Request Body:
{
  "commit_id": "sha-of-commit",
  "body": "Overall review message",
  "event": "COMMENT|APPROVE|REQUEST_CHANGES",
  "comments": [
    {
      "path": "file/path.py",
      "position": 4,
      "body": "Inline comment text"
    }
  ]
}

Response (201 Created or 200 OK):
{
  "id": 80143981,
  "node_id": "PRR_kwDOCZi3K84H0MjJ",
  "user": {...},
  "body": "Overall review message",
  "state": "COMMENTED",
  "html_url": "https://github.com/owner/repo/pull/123#pullrequestreview-80143981",
  "pull_request_url": "https://api.github.com/repos/owner/repo/pulls/123",
  "submitted_at": "2024-01-15T10:30:00Z",
  "commit_id": "abc123def456",
  "author_association": "COLLABORATOR"
}

Common Errors:
- 422: Invalid position (out of diff range)
- 422: Path not in PR diff
- 403: Insufficient permissions
- 404: PR not found
"""
