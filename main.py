import os
import requests
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

TOKEN = "тут_твій_токен_бота"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"

def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Failed to send message:", e)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        print("Received data:", data)

        if not data:
            return jsonify({"ok": False, "error": "No JSON data"}), 400

        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"]["text"]

            # Тут можна обробляти команди чи тексти
            if text.lower() == "/start":
                send_message(chat_id, "Вітаю! Це твій бот.")
            else:
                send_message(chat_id, f"Ти написав: {text}")

        else:
            print("Unsupported update type")
            # Можна додатково обробити callback_query або інші типи

        return jsonify({"ok": True})

    except Exception as e:
        print("Error in webhook:", e)
        # Можна також надіслати повідомлення про помилку користувачу, якщо хочеш
        return jsonify({"ok": True})  # щоб Telegram не повторював запити

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

