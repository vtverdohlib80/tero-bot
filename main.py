from flask import Flask, request
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHATGPT_ENDPOINT = "https://api.openai.com/v1/chat/completions"
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Збережемо стан користувача (для простоти — у пам'яті, на проді треба базу)
user_states = {}

@app.route('/')
def index():
    return "Tarot Bot is running!"

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')

        if text == '/start':
            send_welcome(chat_id)
            user_states[chat_id] = None  # Очікуємо вибір теми
        else:
            state = user_states.get(chat_id)
            if state == "awaiting_custom_query":
                # Отримали текст від користувача для кастомного розкладу
                prompt = create_prompt(text)
                gpt_response = ask_chatgpt(prompt)
                send_message(chat_id, gpt_response)
                user_states[chat_id] = None
                send_welcome(chat_id)  # Показуємо меню знову
            else:
                # Якщо натиснули одну з кнопок меню (кохання, фінанси, кар'єра, порада)
                if text.lower() in ["кохання", "фінанси", "кар'єра", "порада на день"]:
                    prompt = create_prompt(text)
                    gpt_response = ask_chatgpt(prompt)
                    send_message(chat_id, gpt_response)
                    send_welcome(chat_id)  # Показуємо меню знову
                elif text == "Ввести свій запит":
                    send_message(chat_id, "Введіть свій запит для розкладу Таро:")
                    user_states[chat_id] = "awaiting_custom_query"
                else:
                    send_message(chat_id, "Будь ласка, виберіть одну з кнопок нижче.")
                    send_welcome(chat_id)
    return {"ok": True}

def send_welcome(chat_id):
    keyboard = {
        "keyboard": [
            ["Кохання", "Фінанси"],
            ["Кар'єра", "Порада на день"],
            ["Ввести свій запит"]
        ],
        "one_time_keyboard": True,
        "resize_keyboard": True
    }
    send_message(chat_id, "Оберіть тему розкладу Таро:", keyboard)

def create_prompt(topic):
    return f"""
    Ти досвідчений таролог. Проведи уявний розклад карт Таро на тему: "{topic}". Вибери випадково 3 карти і поясни їх значення. Потім зроби коротке тлумачення ситуації.
    """

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
     print("OpenAI response:", result)  # <-- додай це для діагностики
   
        return result['choices'][0]['message']['content']
    except Exception:
        return "Вибач, сталася помилка при трактуванні карт 😔"

def send_message(chat_id, text, reply_markup=None):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(url, json=payload)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
