import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
    api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
)

def analyze_diff_with_gpt4o(diff_text: str) -> str:
    response = client.chat.completions.create(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI technical due diligence agent. "
                    "Analyze the PR diff and provide: "
                    "1. Overall risk score "
                    "2. Go / No-Go recommendation "
                    "3. Architecture risks "
                    "4. Scalability risks "
                    "5. Security concerns "
                    "6. Code quality issues. "
                    "Categorize findings as [CRITICAL], [HIGH], and [MEDIUM]."
                ),
            },
            {
                "role": "user",
                "content": f"Here is the PR diff:\n\n{diff_text}",
            },
        ],
        max_tokens=4096,
        temperature=0.2,
        top_p=1.0,
    )

    return response.choices[0].message.content