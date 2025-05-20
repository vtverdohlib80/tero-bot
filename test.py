import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHATGPT_ENDPOINT = "https://api.openai.com/v1/chat/completions"

def ask_chatgpt(prompt):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "Ти досвідчений таролог."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.9
    }

    response = requests.post(CHATGPT_ENDPOINT, headers=headers, json=data)

    print("Status code:", response.status_code)
    print("Response text:", response.text)

    if response.status_code != 200:
        return "Помилка API OpenAI"

    result = response.json()
    return result['choices'][0]['message']['content']

prompt = "Поясни три карти Таро, які символізують кохання."
print(ask_chatgpt(prompt))
