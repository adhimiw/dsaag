from mistralai import Mistral
from dotenv import load_dotenv
import os

# 1) Load env vars
load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")
print("API Key found:", "Yes" if api_key else "No")
print("API Key raw repr:", repr(api_key))

if not api_key:
    print("Error: MISTRAL_API_KEY is empty.")
    exit(1)

# 2) Init client
client = Mistral(api_key=api_key)

# 3) Single, correct embeddings call
print("Attempting embedding with 'inputs'...")
try:
    res = client.embeddings.create(
        model="mistral-embed",
        inputs=["hello world"],   # correct param name
    )
    print("Success with 'inputs'!")
    print(res)
    exit(0)
except Exception as e:
    print(f"Failed with 'inputs': {e}")

print("All attempts failed.")
