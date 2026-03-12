
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
