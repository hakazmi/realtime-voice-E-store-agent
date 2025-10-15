import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("🚀 Testing regular text completion API...\n")

resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Say 'Hello world from HTTP API!'"},
    ],
)

print("💬 Response:", resp.choices[0].message.content)







