import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
import logging
from flask import Flask, request

# Логування
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Константи
TOKEN = "7560668855:AAHwS3FGu0aSCn6fP8JBtcfYNgC96W77k7Q"
WEBHOOK_URL = "https://tero-bot-33.onrender.com"

# Стадії діалогу
(
    WAIT_QUESTION,
    WAIT_EMOTION,
    WAIT_BIRTHDATE,
    WAIT_PERSONAL,
    WAIT_DECK,
    WAIT_TAROLOG,
    CONFIRMATION,
) = range(7)

DECKS = ["Класична 🃏", "Універсальна 🔮", "Спеціалізована 🌟"]
TAROLOGS = [
    "Таролог 1 🧙‍♂️",
    "Таролог 2 🧙‍♀️",
    "Таролог 3 🧙",
    "Таролог 4 🧙‍♂️",
    "Таролог 5 🧙‍♀️",
    "Таролог 6 🧙",
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"👋 Вітаю, {user.first_name}! Я твій Таро-бот.\n\n"
        "Натисни кнопку нижче, щоб отримати розклад від таролога."
    )
    keyboard = [
        [InlineKeyboardButton("🃏 Отримати розклад від таролога", callback_data="start_reading")]
    ]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard))


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "start_reading":
        await query.message.reply_text("❓ Введи чітке або приблизне питання чи тему:")
        return WAIT_QUESTION

    if data.startswith("deck_"):
        deck_choice = int(data.split("_")[1])
        context.user_data["deck"] = DECKS[deck_choice]
        keyboard = [[InlineKeyboardButton(t, callback_data=f"tarolog_{i}")] for i, t in enumerate(TAROLOGS)]
        await query.message.reply_text("🎴 Обери таролога:", reply_markup=InlineKeyboardMarkup(keyboard))
        return WAIT_TAROLOG

    if data.startswith("tarolog_"):
        tarolog_choice = int(data.split("_")[1])
        context.user_data["tarolog"] = TAROLOGS[tarolog_choice]

        summary = (
            f"📝 Твій розклад:\n"
            f"Питання: {context.user_data.get('question')}\n"
            f"Емоційний стан: {context.user_data.get('emotion')}\n"
            f"Дата народження: {context.user_data.get('birthdate')}\n"
            f"Інша інформація: {context.user_data.get('personal')}\n"
            f"Колода: {context.user_data.get('deck')}\n"
            f"Таролог: {context.user_data.get('tarolog')}\n\n"
            "✅ Якщо все вірно, напиши 'Підтверджую', або 'Скасувати'."
        )
        await query.message.reply_text(summary)
        return CONFIRMATION


async def question_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["question"] = update.message.text.strip()
    await update.message.reply_text("😊 Опиши свій емоційний стан:")
    return WAIT_EMOTION


async def emotion_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["emotion"] = update.message.text.strip()
    await update.message.reply_text("📅 Введи дату народження (ДД.ММ.РРРР):")
    return WAIT_BIRTHDATE


async def birthdate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import re
    text = update.message.text.strip()
    if not re.match(r"\d{2}\.\d{2}\.\d{4}", text):
        await update.message.reply_text("❗ Формат дати має бути ДД.ММ.РРРР. Наприклад, 25.05.1990")
        return WAIT_BIRTHDATE
    context.user_data["birthdate"] = text
    await update.message.reply_text("ℹ️ Введи додаткову персональну інформацію (або 'нема'):")
    return WAIT_PERSONAL


async def personal_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["personal"] = update.message.text.strip()
    keyboard = [[InlineKeyboardButton(deck, callback_data=f"deck_{i}")] for i, deck in enumerate(DECKS)]
    await update.message.reply_text("🃏 Обери колоду карт:", reply_markup=InlineKeyboardMarkup(keyboard))
    return WAIT_DECK


async def confirmation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().strip()
    if text == "підтверджую":
        await update.message.reply_text("🔮 Розклад готується...\n(Тут зʼявиться відповідь)")
        context.user_data.clear()
        return ConversationHandler.END
    elif text == "скасувати":
        await update.message.reply_text("❌ Розклад скасовано.")
        context.user_data.clear()
        return ConversationHandler.END
    else:
        await update.message.reply_text("Напиши 'Підтверджую' або 'Скасувати'.")
        return CONFIRMATION


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Дію скасовано.")
    context.user_data.clear()
    return ConversationHandler.END


def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(button_handler, pattern="^start_reading$"),
        ],
        states={
            WAIT_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, question_handler)],
            WAIT_EMOTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, emotion_handler)],
            WAIT_BIRTHDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, birthdate_handler)],
            WAIT_PERSONAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, personal_handler)],
            WAIT_DECK: [CallbackQueryHandler(button_handler, pattern="^deck_")],
            WAIT_TAROLOG: [CallbackQueryHandler(button_handler, pattern="^tarolog_")],
            CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirmation_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
        per_message=True,
    )

    app.add_handler(conv_handler)

    # Webhook запуск
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=f"{WEBHOOK_URL}/webhook"
    )


if __name__ == "__main__":
    main()
