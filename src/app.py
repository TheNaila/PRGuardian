from github import Github
import os

def parse_diff_to_positions(diff_text):
    """
    Parse a Git diff and map each line number to its position in the diff.
    
    Returns a dict: {
        "file_path": {
            line_number: diff_position,
            ...
        }
    }
    
    Important: diff_position starts counting from 1 right after the @@ header.
    """
    positions_map = {}
    current_file = None
    diff_position = 0  # Position counter for current hunk
    start_line = 0  # Current line number in the new file
    
    for line in diff_text.split('\n'):
        # When we hit a new file header (e.g., "diff --git a/file.py b/file.py")
        if line.startswith('diff --git'):
            # Extract just the filename (after b/)
            parts = line.split(' b/')
            if len(parts) == 2:
                current_file = parts[1]
                positions_map[current_file] = {}
            diff_position = 0  # Reset for new file
            start_line = 0
            continue
        
        # When we hit a hunk header (e.g., "@@ -5,10 +5,12 @@")
        if line.startswith('@@'):
            # Extract the target line number (the +X,Y part)
            # Format: @@ -old_line,old_count +new_line,new_count @@
            parts = line.split(' ')
            if len(parts) >= 3:
                new_range = parts[2]  # e.g., "+5,12"
                start_line = int(new_range.split(',')[0][1:])  # Remove '+' and split
            diff_position = 0  # Reset position counter for new hunk
            continue
        
        # Skip file headers and empty diffs
        if current_file is None:
            continue
        
        # Count every line in the hunk (including context, additions, deletions)
        if line and line[0] in ['+', '-', ' ']:
            diff_position += 1
            
            # Track positions only for lines being ADDED or in CONTEXT (not deletions)
            if line[0] in ['+', ' ']:
                # Map the actual line number to diff position
                positions_map[current_file][start_line] = diff_position
                start_line += 1
    
    return positions_map


def map_ai_response_to_github_format(ai_response_json, diff_positions_map):
    """
    Convert Azure AI response to GitHub Review API format.
    
    Input (from Azure AI):
    [
        {"file_path": "src/app.py", "line_number": 10, "severity": "error", "comment": "..."},
        ...
    ]
    
    Output (for GitHub API):
    [
        {"path": "src/app.py", "position": 5, "body": "[ERROR] ..."},
        ...
    ]
    """
    github_comments = []
    
    for issue in ai_response_json:
        file_path = issue.get("file_path")
        line_number = issue.get("line_number")
        severity = issue.get("severity", "info").upper()
        comment = issue.get("comment", "")
        
        # 1. Find the diff position for this line in this file
        if file_path not in diff_positions_map:
            # File not in diff, skip this comment
            print(f"Warning: File {file_path} not found in diff, skipping comment at line {line_number}")
            continue
        
        if line_number not in diff_positions_map[file_path]:
            # This line number isn't in the diff (could be unchanged or deleted)
            print(f"Warning: Line {line_number} in {file_path} not found in diff changes, skipping")
            continue
        
        # 2. Get the position in the diff
        position = diff_positions_map[file_path][line_number]
        
        # 3. Format the comment body with severity badge
        github_comment_body = f"**[{severity}]** {comment}"
        
        # 4. Create the GitHub API comment object
        github_comments.append({
            "path": file_path,
            "position": position,
            "body": github_comment_body
        })
    
    return github_comments


def post_bulk_review(repo_full_name, pr_number, ai_suggestions):
    """
    Post a GitHub PR review with AI suggestions as inline comments.
    
    Args:
        repo_full_name: "owner/repo"
        pr_number: PR number (integer)
        ai_suggestions: List of dicts from Azure AI with keys:
                       ["file_path", "line_number", "severity", "comment"]
    """
    # 1. Connect to GitHub
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo(repo_full_name)
    pr = repo.get_pull(pr_number)
    
    # 2. Get the PR diff
    diff_url = pr.diff_url
    diff_text = g.get_user().get_user(repo.owner.login).get_repo(repo.name).get_pulls(
        state="open"
    )[0].get_issue_comments()  
    
    
    import requests
    headers = {"Accept": "application/vnd.github.v3.diff"}
    headers["Authorization"] = f"token {os.getenv('GITHUB_TOKEN')}"
    diff_response = requests.get(
        f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}",
        headers=headers
    )
    diff_text = diff_response.text
    
    # 3. Parse the diff to map line numbers to positions
    positions_map = parse_diff_to_positions(diff_text)
    
    # 4. Convert AI response to GitHub format
    github_comments = map_ai_response_to_github_format(ai_suggestions, positions_map)
    
    if not github_comments:
        print("No valid comments to post (all lines were out of diff scope)")
        return
    
    # 5. Get the latest commit SHA (required to anchor the review)
    commits = list(pr.get_commits())
    if not commits:
        print("Error: PR has no commits")
        return
    commit_sha = commits[-1].sha  # Latest commit
    
    # 6. Submit the review
    pr.create_review(
        commit_sha=commit_sha,
        body="PRGuardian AI Review: Issues detected",
        event="COMMENT",
        comments=github_comments
    )
    
    print(f"Review posted to PR #{pr_number} with {len(github_comments)} inline comments")


def update_github_labels(repo_name, pr_number, ai_response_text):
    """
    Update GitHub PR labels based on AI response severity.
    
    Rules:
    - Always remove "audit-requested" label first (cleanup)
    - If ANY [HIGH] issues found OR more than 3 [MEDIUM] issues: add "NO-GO"
    - Otherwise: add "GO"
    
    Args:
        repo_name: Repository name (e.g., "owner/repo")
        pr_number: Pull request number (integer)
        ai_response_text: AI response text containing severity markers like [HIGH], [MEDIUM]
    """
    # 1. Connect to GitHub and get the PR
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(int(pr_number))
    
    # 2. Always remove audit-requested label first to prevent loops
    try:
        pr.remove_from_labels("audit-requested")
        print(" Removed 'audit-requested' label")
    except:
        pass  # Label might have already been removed or doesn't exist
    
    # 3. Count severity levels in AI response
    high_count = ai_response_text.count("[HIGH]")
    medium_count = ai_response_text.count("[MEDIUM]")
    
    # 4. Determine which label to apply
    if high_count > 0 or medium_count > 3:
        # Critical issues found - block the PR
        pr.add_to_labels("NO-GO")
        print(f" Critical issues found. Applied NO-GO label.")
        print(f"   - HIGH severity issues: {high_count}")
        print(f"   - MEDIUM severity issues: {medium_count}")
    else:
        # No critical issues - allow the PR
        pr.add_to_labels("GO")
        print(f" No critical issues. Applied GO label.")
        if medium_count > 0:
            print(f"   - Note: {medium_count} medium-severity issues found but within threshold")