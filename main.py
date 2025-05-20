import os
from flask import Flask, request
import requests
from dotenv import load_dotenv
import json

load_dotenv()

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
# Замінюємо ":" на "_" для шляху webhook
WEBHOOK_PATH = TELEGRAM_TOKEN.replace(":", "_")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Словники для станів та даних користувачів
user_states = {}
user_data = {}

# Кнопка для початку
start_button = [["Отримати розклад від таролога"]]

# Кнопки для вибору колоди карт
deck_buttons = [["Класична"], ["Універсальна"], ["Спеціалізована"]]

# Кнопки для вибору таролога (6 варіантів)
tarot_readers_buttons = [
    ["Таролог 1", "Таролог 2"],
    ["Таролог 3", "Таролог 4"],
    ["Таролог 5", "Таролог 6"]
]

def send_message(chat_id, text, reply_markup=None):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    requests.post(url, json=payload)

def get_keyboard(buttons, one_time=False):
    return {
        "keyboard": buttons,
        "resize_keyboard": True,
        "one_time_keyboard": one_time
    }

@app.route(f"/{WEBHOOK_PATH}", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data:
        return {"ok": True}

    if "message" not in data:
        return {"ok": True}

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    # Якщо користувач новий або не у процесі опитування
    if chat_id not in user_states or user_states[chat_id] == "start":
        if text == "Отримати розклад від таролога":
            user_states[chat_id] = "waiting_for_question"
            user_data[chat_id] = {}
            send_message(chat_id, "Введіть, будь ласка, ваше питання або тему, на яку хочете отримати відповідь.")
        else:
            send_message(chat_id, "Привіт! Натисніть кнопку нижче, щоб отримати розклад від таролога.", reply_markup=get_keyboard(start_button))
        return {"ok": True}

    # Кроки опитування
    if user_states[chat_id] == "waiting_for_question":
        user_data[chat_id]["question"] = text
        user_states[chat_id] = "waiting_for_emotion"
        send_message(chat_id, "Опишіть ваш емоційний стан на даний момент.")
        return {"ok": True}

    if user_states[chat_id] == "waiting_for_emotion":
        user_data[chat_id]["emotion"] = text
        user_states[chat_id] = "waiting_for_birthdate"
        send_message(chat_id, "Введіть, будь ласка, вашу дату народження (формат: ДД.MM.РРРР).")
        return {"ok": True}

    if user_states[chat_id] == "waiting_for_birthdate":
        user_data[chat_id]["birthdate"] = text
        user_states[chat_id] = "waiting_for_deck"
        send_message(chat_id, "Оберіть колоду карт:", reply_markup=get_keyboard(deck_buttons, one_time=True))
        return {"ok": True}

    if user_states[chat_id] == "waiting_for_deck":
        if text not in ["Класична", "Універсальна", "Спеціалізована"]:
            send_message(chat_id, "Будь ласка, оберіть один з варіантів колоди, натиснувши кнопку.")
            return {"ok": True}
        user_data[chat_id]["deck"] = text
        user_states[chat_id] = "waiting_for_tarot_reader"
        send_message(chat_id, "Оберіть таролога:", reply_markup=get_keyboard(tarot_readers_buttons, one_time=True))
        return {"ok": True}

    if user_states[chat_id] == "waiting_for_tarot_reader":
        valid_readers = sum(tarot_readers_buttons, [])  # список всіх тарологів
        if text not in valid_readers:
            send_message(chat_id, "Будь ласка, оберіть таролога з кнопок нижче.")
            return {"ok": True}
        user_data[chat_id]["tarot_reader"] = text
        user_states[chat_id] = "completed"

        print(f"Нове замовлення від {chat_id}: {user_data[chat_id]}")

        send_message(chat_id, "Дякую! Ваш запит прийнято. Таролог незабаром з вами зв'яжеться.")
        send_message(chat_id, "Якщо хочете зробити новий запит, натисніть кнопку нижче.", reply_markup=get_keyboard(start_button))

        # Очистка стану для нового запиту
        user_states[chat_id] = "start"
        user_data[chat_id] = {}
        return {"ok": True}

    send_message(chat_id, "Вибачте, сталася помилка. Спробуйте почати заново.", reply_markup=get_keyboard(start_button))
    user_states[chat_id] = "start"
    user_data[chat_id] = {}
    return {"ok": True}

@app.route("/")
def index():
    return "Tarot Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
