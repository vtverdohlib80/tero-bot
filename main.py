import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from flask import Flask, request
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

TOKEN = "7560668855:AAHwS3FGu0aSCn6fP8JBtcfYNgC96W77k7Q"
WEBHOOK_URL = "https://tero-bot-33.onrender.com"

# Flask app
flask_app = Flask(__name__)

# Стадії ConversationHandler
(
    CHOOSING,
    QUESTION,
    EMOTION,
    BIRTHDATE,
    CHOOSE_DECK,
    CHOOSE_TAROLOGIST,
    DONE,
) = range(7)

# Тимчасове сховище для даних юзерів, ключ — chat_id
user_data_store = {}

# Привітання
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_data_store[chat_id] = {}

    welcome_text = (
        "👋 Вітаю! Я твій Таролог-бот 🃏\n\n"
        "Натисни кнопку нижче, щоб отримати розклад від таролога."
    )
    keyboard = [
        [InlineKeyboardButton("🃏 Отримати розклад від таролога", callback_data="start_reading")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

# Обробка кнопки "Отримати розклад"
async def start_reading_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id

    user_data_store[chat_id] = {}

    await query.message.reply_text("Будь ласка, напиши своє питання або тему розкладу:")
    return QUESTION

# Прийом питання/теми
async def question_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text
    user_data_store[chat_id]["question"] = text

    await update.message.reply_text("Опиши свій емоційний стан (наприклад: радісний, сумний, стурбований):")
    return EMOTION

# Прийом емоційного стану
async def emotion_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text
    user_data_store[chat_id]["emotion"] = text

    await update.message.reply_text("Вкажи дату народження у форматі ДД.ММ.РРРР (наприклад, 25.05.1990):")
    return BIRTHDATE

# Прийом дати народження
async def birthdate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text
    # Можна додати валідацію дати, поки просто зберігаємо
    user_data_store[chat_id]["birthdate"] = text

    # Вибір колоди
    keyboard = [
        [
            InlineKeyboardButton("Класична", callback_data="deck_classic"),
            InlineKeyboardButton("Універсальна", callback_data="deck_universal"),
            InlineKeyboardButton("Спеціалізована", callback_data="deck_special"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Оберіть колоду:", reply_markup=reply_markup)
    return CHOOSE_DECK

# Вибір колоди
async def choose_deck_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    user_data_store[chat_id]["deck"] = query.data.replace("deck_", "")

    # Вибір таролога
    keyboard = [
        [
            InlineKeyboardButton("Таролог 1", callback_data="tarologist_1"),
            InlineKeyboardButton("Таролог 2", callback_data="tarologist_2"),
        ],
        [
            InlineKeyboardButton("Таролог 3", callback_data="tarologist_3"),
            InlineKeyboardButton("Таролог 4", callback_data="tarologist_4"),
        ],
        [
            InlineKeyboardButton("Таролог 5", callback_data="tarologist_5"),
            InlineKeyboardButton("Таролог 6", callback_data="tarologist_6"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Оберіть таролога:", reply_markup=reply_markup)
    return CHOOSE_TAROLOGIST

# Вибір таролога
async def choose_tarologist_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    user_data_store[chat_id]["tarologist"] = query.data.replace("tarologist_", "")

    # ТУТ можна відправити на обробку або просто підтвердити прийом даних
    data = user_data_store[chat_id]
    response = (
        "Дякую! Твій запит прийнято:\n\n"
        f"❓ Питання: {data.get('question')}\n"
        f"😌 Емоційний стан: {data.get('emotion')}\n"
        f"🎂 Дата народження: {data.get('birthdate')}\n"
        f"🃏 Колода: {data.get('deck')}\n"
        f"🔮 Таролог: {data.get('tarologist')}\n\n"
        "Незабаром ти отримаєш розклад від таролога."
    )
    await query.edit_message_text(response)
    # Тут можна додати логіку звернення до бази або API таролога

    return ConversationHandler.END

# Команда /cancel для відміни
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_data_store.pop(chat_id, None)
    await update.message.reply_text("Розклад скасовано. Якщо хочеш, почни спочатку з /start")
    return ConversationHandler.END

# Flask route для Telegram webhook
@flask_app.route("/", methods=["POST"])
def webhook():
    from telegram import Update
    update = Update.de_json(request.get_json(force=True), app.bot)
    app.update_queue.put_nowait(update)
    return "OK", 200

# Налаштування Application та ConversationHandler
app = Application.builder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_reading_handler, pattern="^start_reading$")],
    states={
        QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, question_handler)],
        EMOTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, emotion_handler)],
        BIRTHDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, birthdate_handler)],
        CHOOSE_DECK: [CallbackQueryHandler(choose_deck_handler, pattern="^deck_")],
        CHOOSE_TAROLOGIST: [CallbackQueryHandler(choose_tarologist_handler, pattern="^tarologist_")],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_message=False,
)

app.add_handler(CommandHandler("start", start))
app.add_handler(conv_handler)

def main():
    # Запуск webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        webhook_url=WEBHOOK_URL,
    )

if __name__ == "__main__":
    main()
