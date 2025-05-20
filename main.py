import os
from flask import Flask, request, abort
import requests
import openai

app = Flask(__name__)

# Завантажуємо токени з .env (або можна вставити тут напряму)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # Telegram Bot Token
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # OpenAI API Key

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise RuntimeError("TELEGRAM_TOKEN та OPENAI_API_KEY мають бути встановлені у середовищі")

openai.api_key = OPENAI_API_KEY

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, json=payload)
    return response.ok

def generate_tarot_reading(question):
    prompt = (
        "Ти — досвідчений таролог. Користувач задає питання:\n"
        f"{question}\n"
        "Зроби розклад Таро, дай зрозумілу і доброзичливу відповідь українською мовою."
    )
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7,
        )
        answer = completion.choices[0].message['content'].strip()
        return answer
    except Exception as e:
        print("OpenAI error:", e)
        return None

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.json

    if "message" not in data:
        return "ok"

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if not text:
        send_message(chat_id, "Вибач, я не зрозумів твоє повідомлення 😔")
        return "ok"

    reading = generate_tarot_reading(text)
    if reading:
        send_message(chat_id, reading)
    else:
        send_message(chat_id, "Вибач, сталася помилка при трактуванні карт 😔")

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
