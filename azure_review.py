import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
    api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
)

def analyze_diff_with_gpt4o(diff_text: str, policy_snippets: list[str]) -> str:
    formatted_policies = "\n\n".join(
        [f"Policy Snippet {i + 1}:\n{snippet}" for i, snippet in enumerate(policy_snippets[:3])]
    )

    response = client.chat.completions.create(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI technical due diligence agent. "
                    "Analyze the PR diff against the provided engineering policy snippets. "
                    "Provide: "
                    "1. Overall risk score "
                    "2. Go / No-Go recommendation "
                    "3. Architecture risks "
                    "4. Scalability risks "
                    "5. Security concerns "
                    "6. Code quality issues "
                    "7. Policy compliance issues. "
                    "Categorize findings as [CRITICAL], [HIGH], and [MEDIUM]. "
                    "When relevant, reference which policy snippet was violated."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Here is the PR diff:\n\n{diff_text}\n\n"
                    f"Top 3 relevant policy snippets:\n\n{formatted_policies}"
                ),
            },
        ],
        max_tokens=4096,
        temperature=0.2,
        top_p=1.0,
    )

    return response.choices[0].message.content
