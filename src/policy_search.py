import os
from typing import List

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv

load_dotenv()

search_client = SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name=os.environ["AZURE_SEARCH_INDEX_NAME"],
    credential=AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"])
)


def search_policy_snippets(query_text: str, top_k: int = 100) -> List[str]:
    results = search_client.search(
        search_text=query_text,
        top=top_k
    )

    snippets = []

    for r in results:
        text = r.get("text") or r.get("chunk") or ""
        text = text.strip()

        if not text:
            continue

        snippets.append(text)

    return snippets