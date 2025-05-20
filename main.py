import os
import random
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHATGPT_ENDPOINT = "https://api.openai.com/v1/chat/completions"
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

@app.route('/')
def index():
    return "Tarot Bot is running!"

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def telegram_webhook():
    data = request.get_json()

    if 'message' in data and 'text' in data['message']:
        chat_id = data['message']['chat']['id']
        text = data['message']['text']

        # Створення prompt для ChatGPT
        prompt = f"""
        Ти досвідчений таролог. Проведи уявний розклад карт Таро на тему:
        "{text}". Вибери випадково 3 карти і поясни їх значення. 
        Потім зроби коротке тлумачення ситуації.
        """

        gpt_response = ask_chatgpt(prompt)

        send_message(chat_id, gpt_response)

    return {"ok": True}

def ask_chatgpt(prompt):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",  # або "gpt-4" якщо маєш доступ
        "messages": [
            {"role": "system", "content": "Ти досвідчений таролог."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.9
    }

    response = requests.post(CHATGPT_ENDPOINT, headers=headers, json=data)
    result = response.json()

    try:
        return result['choices'][0]['message']['content']
    except Exception as e:
        return "Вибач, сталася помилка при трактуванні карт 😔"

def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
