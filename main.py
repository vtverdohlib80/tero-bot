import os
import sqlite3
from flask import Flask, request
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Ініціалізація бази
conn = sqlite3.connect('tarot_requests.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,
    username TEXT,
    query TEXT,
    status TEXT DEFAULT 'new',
    answer TEXT
)
''')
conn.commit()

# Функція для надсилання повідомлень
def send_message(chat_id, text, reply_markup=None):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(url, json=payload)

# Меню з кнопками
def main_menu():
    keyboard = {
        "inline_keyboard": [
            [{"text": "❤️ Кохання", "callback_data": "love"}],
            [{"text": "💰 Фінанси", "callback_data": "finance"}],
            [{"text": "💼 Кар'єра", "callback_data": "career"}],
            [{"text": "📩 Ввести власний запит", "callback_data": "custom_query"}],
        ]
    }
    return keyboard

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    data = request.get_json()
    if 'message' in data:
        message = data['message']
        chat_id = message['chat']['id']
        username = message['chat'].get('username', '')

        # Користувач натиснув /start
        if 'text' in message:
            text = message['text']
            if text == '/start':
                send_message(chat_id, "Вітаю! Обери тему таро або введи власний запит:", reply_markup=main_menu())
                return {"ok": True}

            # Перевірка чи це відповідь адміністратора на запит (через команду /answer)
            if text.startswith('/answer'):
                # Формат: /answer <chat_id> <текст відповіді>
                parts = text.split(' ', 2)
                if len(parts) < 3:
                    send_message(chat_id, "Неправильний формат команди. Використання:\n/answer <chat_id> <текст відповіді>")
                    return {"ok": True}

                target_chat_id = parts[1]
                answer_text = parts[2]

                # Надіслати відповідь користувачу
                send_message(target_chat_id, f"Відповідь таролога:\n{answer_text}")

                # Оновити статус у базі
                cursor.execute("UPDATE requests SET status = 'answered', answer = ? WHERE chat_id = ? AND status = 'new'", (answer_text, target_chat_id))
                conn.commit()

                send_message(chat_id, f"Відповідь надіслана користувачу {target_chat_id}.")
                return {"ok": True}

            # Якщо це звичайний текст — зберігаємо як власний запит
            cursor.execute("INSERT INTO requests (chat_id, username, query) VALUES (?, ?, ?)", (chat_id, username, text))
            conn.commit()

            # Повідомляємо адміністратора (тебе) про новий запит
            admin_chat_id = int(os.getenv("ADMIN_CHAT_ID"))  # Твій Telegram chat_id, де ти отримуватимеш повідомлення
            send_message(admin_chat_id, f"Новий запит від @{username} (chat_id: {chat_id}):\n{text}")

            send_message(chat_id, "Запит прийнято! Очікуйте відповідь таролога.")
            return {"ok": True}

    elif 'callback_query' in data:
        query = data['callback_query']
        chat_id = query['message']['chat']['id']
        username = query['from'].get('username', '')
        data_cb = query['data']

        if data_cb == 'custom_query':
            send_message(chat_id, "Введіть свій запит у вільній формі.")
            return {"ok": True}
        else:
            # Зберігаємо вибраний запит від кнопки
            cursor.execute("INSERT INTO requests (chat_id, username, query) VALUES (?, ?, ?)", (chat_id, username, data_cb))
            conn.commit()

            admin_chat_id = int(os.getenv("ADMIN_CHAT_ID"))
            send_message(admin_chat_id, f"Новий запит від @{username} (chat_id: {chat_id}):\n{data_cb}")

            send_message(chat_id, "Запит прийнято! Очікуйте відповідь таролога.")
            return {"ok": True}

    return {"ok": True}

@app.route('/')
def index():
    return "Tarot bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
