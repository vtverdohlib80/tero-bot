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
    print("Incoming update:", data)

    if 'message' in data and 'text' in data['message']:
        chat_id = data['message']['chat']['id']
        text = data['message']['text']

        # Обробка кнопок і звичайних повідомлень
        if text == '/start':
            send_welcome_buttons(chat_id)
        elif text in ['Кохання', 'Фінанси', "Кар'єра", 'Порада на день']:
            prompt = f"""Ти досвідчений таролог. Проведи розклад на тему "{text}". 
            Вибери випадково 3 карти і поясни їх значення. Потім дай коротке тлумачення."""
            gpt_response = ask_chatgpt(prompt)
            send_message(chat_id, gpt_response)
        elif text == 'Ввести свій запит':
            send_message(chat_id, "Напиши своє питання, і я зроблю розклад карт Таро.")
        else:
            # Тут вважаємо, що це власний запит користувача
            prompt = f"""Ти досвідчений таролог. Проведи уявний розклад карт Таро на тему:
            "{text}". Вибери випадково 3 карти і поясни їх значення. Потім зроби коротке тлумачення ситуації."""
            gpt_response = ask_chatgpt(prompt)
            send_message(chat_id, gpt_response)

    return {"ok": True}

def send_welcome_buttons(chat_id):
    keyboard = {
        "keyboard": [
            [{"text": "Кохання"}, {"text": "Фінанси"}],
            [{"text": "Кар'єра"}, {"text": "Порада на день"}],
            [{"text": "Ввести свій запит"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": True
    }
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "Обери тему розкладу або введи свій запит:",
        "reply_markup": keyboard
    }
    requests.post(url, json=payload)

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

    if response.status_code != 200:
        print(f"OpenAI API error: {response.status_code} - {response.text}")
        return "Вибач, сталася помилка при трактуванні карт 😔"

    try:
        result = response.json()
        print("OpenAI response:", result)
        return result['choices'][0]['message']['content']
    except Exception as e:
        print("Error parsing OpenAI response:", e)
        return "Вибач, сталася помилка при трактуванні карт 😔"

def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
