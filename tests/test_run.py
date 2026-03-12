from src.integration import run_pr_audit

# Fake Azure AI output
ai_response = [
    {
        "file_path": "src/app.py",
        "line_number": 15,
        "severity": "error",
        "comment": "Variable may be undefined before use"
    },
    {
        "file_path": "src/app.py",
        "line_number": 30,
        "severity": "warning",
        "comment": "Consider adding logging"
    }
]

repo_full_name = "Microsoft-AI-Hackathon-PRGuardian/aether-systems"
pr_number = 1

run_pr_audit(repo_full_name, pr_number, ai_response)