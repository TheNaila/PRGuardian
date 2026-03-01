"""
Test script showing how VJ's mapping works.
This demonstrates converting Azure AI responses to GitHub Review API format.
"""

from app import parse_diff_to_positions, map_ai_response_to_github_format

# Sample diff
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
-    x = 1
+    print("Loading config...")
     return {
         "max_retries": MAX_RETRIES,
         "timeout": TIMEOUT,"""

# Parse the diff
positions_map = parse_diff_to_positions(sample_diff)

print(" LINE NUMBER TO DIFF POSITION MAPPING:")
print("=" * 50)
for file_path, line_map in positions_map.items():
    print(f"\nFile: {file_path}")
    for line_num, position in sorted(line_map.items()):
        print(f"  Line {line_num:3d} -> Diff Position {position:2d}")

# This is what Azure AI would return
azure_ai_response = [
    {
        "file_path": "src/config.py",
        "line_number": 8,
        "severity": "warning",
        "comment": "DEBUG mode should not be False in production"
    },
    {
        "file_path": "src/config.py",
        "line_number": 12,
        "severity": "info",
        "comment": "Consider logging this event for debugging"
    }
]

# Convert to GitHub format
github_comments = map_ai_response_to_github_format(azure_ai_response, positions_map)

print("\n\n4 CONVERTED TO GITHUB FORMAT:")
print("=" * 50)
for comment in github_comments:
    print(f"\nFile: {comment['path']}")
    print(f"Position: {comment['position']}")
    print(f"Body: {comment['body']}")

# Key concepts
print("\n\n KEY CONCEPTS:")
print("=" * 50)
print("""
1. GitHub does not use actual line numbers in reviews - it uses position
   Position = number of lines down from the @@ hunk header

2. The @@ header shows the starting line: @@ -5,10 +5,11 @@
   Position 1 = the first line AFTER @@
   Position 2 = the second line AFTER @@

3. Your job is to:
   - Parse diff with parse_diff_to_positions()
   - Convert AI response with map_ai_response_to_github_format()
   - Submit via GitHub Review API

4. Flow: Azure AI (line#) -> Mapping -> GitHub API (position)
""")

