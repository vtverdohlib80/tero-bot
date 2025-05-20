from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Токен твого бота (постав свій)
BOT_TOKEN = '7560668855:AAHwS3FGu0aSCn6fP8JBtcfYNgC96W77k7Q'
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'

def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Failed to send message: {e}")

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        print("Update received:", data)  # Лог для дебагу

        message = data.get('message')
        if not message:
            return 'ok', 200  # Якщо нема повідомлення, просто відповідаємо 200

        chat_id = message['chat']['id']
        text = message.get('text', '')

        # Простий приклад логіки — відповідаємо на будь-який текст
        if text:
            # Тут можна додати твою обробку карт або інших команд
            send_message(chat_id, f"Ви написали: {text}")
        else:
            send_message(chat_id, "Вибач, сталася помилка при трактуванні карт 😔")

        return 'ok', 200

    except Exception as e:
        print(f"Error processing update: {e}")
        # Відповідаємо 200, щоб Telegram не повторював webhook
        return 'ok', 200

if __name__ == '__main__':
    # Запускаємо сервер на всіх інтерфейсах, порт 5000
    app.run(host='0.0.0.0', port=5000)
