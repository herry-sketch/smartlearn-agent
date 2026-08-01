import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise SystemExit(
        "OPENROUTER_API_KEY is missing. Add it to .env and try again."
    )

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

response = client.chat.completions.create(
    model="google/gemma-4-26b-a4b-it:free",
    messages=[
        {
            "role": "user",
            "content": "What is Python in 2 sentences?",
        }
    ],
    temperature=0,
    max_tokens=200,
)

print(response.choices[0].message.content)
