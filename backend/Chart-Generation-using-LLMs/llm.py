import os
from mistralai import Mistral
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("MISTRAL_API_KEY not found in environment variables")

model = "mistral-large-latest"
client = Mistral(api_key=api_key)

chat_response = client.chat.complete(
    model=model,
    messages=[
        {
            "role": "user",
            "content": "What is the best French cheese?",
        },
    ]
)
print(chat_response.choices[0].message.content)

