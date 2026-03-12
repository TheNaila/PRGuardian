import json
import os

from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
    api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
)


def review_pr_diff(diff_text: str, policy_snippets=None) -> list[dict]:
    """
    Analyze a PR diff and return standardized findings.

    Returns:
        list of findings in this format:
        [
            {
                "file_path": "src/app.py",
                "line_number": 15,
                "severity": "high",
                "comment": "Possible undefined variable before use"
            }
        ]
    """
    policy_snippets = policy_snippets or []

    formatted_policies = "\n\n".join(
        [f"Policy Snippet {i + 1}:\n{snippet}" for i, snippet in enumerate(policy_snippets[:3])]
    )

    response = client.chat.completions.create(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI DevOps and SRE code review agent. "
                    "Analyze the pull request diff against the provided engineering policy snippets. "
                    "Return ONLY valid JSON as an array of findings. "
                    "Each finding must use this exact schema: "
                    '[{"file_path":"string","line_number":123,"severity":"critical|high|medium|low","comment":"string"}]. '
                    "Do not include markdown fences. Do not include explanations outside the JSON. "
                    "Only include findings that can be tied to a specific changed file and line number."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Here is the PR diff:\n\n{diff_text}\n\n"
                    f"Top relevant policy snippets:\n\n{formatted_policies}"
                ),
            },
        ],
        max_tokens=2000,
        temperature=0.1,
        top_p=1.0,
    )

    content = response.choices[0].message.content.strip()

    try:
        findings = json.loads(content)
        if isinstance(findings, list):
            return findings
        print("Azure review did not return a list. Returning empty findings.")
        return []
    except json.JSONDecodeError:
        print("Failed to parse Azure review response as JSON.")
        print("Raw model response:")
        print(content)
        return []