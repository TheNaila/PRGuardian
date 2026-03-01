from dotenv import load_dotenv
import os
load_dotenv()

api_key = os.getenv("GITHUB_TOKEN")
print(api_key)