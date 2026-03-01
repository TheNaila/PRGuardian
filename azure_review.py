from __future__ import annotations

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()


def analyze_diff_with_gpt4o(diff_text: str) -> str:
    """
    Sends PR diff to Azure GPT-4o via Azure AI Foundry (AIProjectClient).
    Requires:
      - PROJECT_ENDPOINT (Foundry project endpoint URL)
      - MODEL_DEPLOYMENT_NAME (your Azure OpenAI deployment name)
      - AZURE_OPENAI_API_VERSION (optional; if omitted, set OPENAI_API_VERSION)
    """
    if not diff_text.strip():
        raise ValueError("diff_text is empty")

    project_endpoint = os.environ["PROJECT_ENDPOINT"]
    deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION")  # optional

    # Per docs: AIProjectClient(endpoint: str, credential: TokenCredential, **kwargs)
    project_client = AIProjectClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(),
    )

    # Per docs: get_openai_client(api_version=..., connection_name=...)
    # If api_version is not provided here, you must set OPENAI_API_VERSION.
    openai_client = project_client.get_openai_client(
        api_version=api_version
    )

    system_prompt = (
        "You are a senior software architect performing technical due diligence.\n"
        "Analyze the provided PR diff and return:\n"
        "- Overall Risk: Low/Medium/High\n"
        "- Go / No-Go recommendation\n"
        "- Issues grouped by severity: [CRITICAL], [HIGH], [MEDIUM]\n"
        "- Include file/line references when possible.\n"
    )

    resp = openai_client.chat.completions.create(
        model=deployment_name,  # deployment name in Azure OpenAI / Foundry
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"PR diff:\n\n{diff_text}"},
        ],
        temperature=0.2,
    )

    return resp.choices[0].message.content