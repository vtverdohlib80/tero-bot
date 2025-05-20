import os
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

        if text == '/start':
            welcome_text = "🔮 Вітаю! Я бот-таролог. Обери запит або напиши власне питання:"
            reply_markup = {
                "keyboard": [
                    [{"text": "Кохання ❤️"}, {"text": "Фінанси 💰"}],
                    [{"text": "Кар'єра 👔"}, {"text": "Порада на день 🌞"}]
                ],
                "resize_keyboard": True,
                "one_time_keyboard": False
            }
            send_message(chat_id, welcome_text, reply_markup)
        else:
            prompt = f"""
            Ти досвідчений таролог. Проведи уявний розклад карт Таро на тему:
            "{text}". Випадково обери 3 карти, поясни їх значення і дай коротке тлумачення ситуації.
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
        "model": "gpt-3.5-turbo",
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

def send_message(chat_id, text, reply_markup=None):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(url, json=payload)
