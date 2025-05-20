from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)

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

# Дані для вибору
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
        await query.message.reply_text(
            "❓ Введи чітке або приблизне питання чи тему, на яку хочеш отримати відповідь:"
        )
        return WAIT_QUESTION

    # Обробка вибору колоди
    if data.startswith("deck_"):
        deck_choice = data.split("_")[1]
        context.user_data["deck"] = DECKS[int(deck_choice)]
        # Наступний крок - вибір таролога
        keyboard = [
            [InlineKeyboardButton(t, callback_data=f"tarolog_{i}")]
            for i, t in enumerate(TAROLOGS)
        ]
        await query.message.reply_text(
            "🎴 Обери таролога:", reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return WAIT_TAROLOG

    # Обробка вибору таролога
    if data.startswith("tarolog_"):
        tarolog_choice = data.split("_")[1]
        context.user_data["tarolog"] = TAROLOGS[int(tarolog_choice)]

        # Підсумок і запит на підтвердження
        question = context.user_data.get("question")
        emotion = context.user_data.get("emotion")
        birthdate = context.user_data.get("birthdate")
        personal = context.user_data.get("personal")
        deck = context.user_data.get("deck")
        tarolog = context.user_data.get("tarolog")

        summary = (
            f"📝 Твій розклад:\n"
            f"Питання: {question}\n"
            f"Емоційний стан: {emotion}\n"
            f"Дата народження: {birthdate}\n"
            f"Інша інформація: {personal}\n"
            f"Колода: {deck}\n"
            f"Таролог: {tarolog}\n\n"
            "✅ Якщо все вірно, напиши 'Підтверджую', або 'Скасувати' для скасування."
        )
        await query.message.reply_text(summary)
        return CONFIRMATION


async def question_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("Будь ласка, введи питання або тему.")
        return WAIT_QUESTION
    context.user_data["question"] = text
    await update.message.reply_text("😊 Опиши свій емоційний стан:")
    return WAIT_EMOTION


async def emotion_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("Будь ласка, опиши свій емоційний стан.")
        return WAIT_EMOTION
    context.user_data["emotion"] = text
    await update.message.reply_text("📅 Введи дату народження (формат: ДД.ММ.РРРР):")
    return WAIT_BIRTHDATE


async def birthdate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    # Проста валідація дати
    import re

    if not re.match(r"\d{2}\.\d{2}\.\d{4}", text):
        await update.message.reply_text(
            "Некоректний формат. Введи дату у форматі ДД.MM.РРРР, наприклад 25.05.1990"
        )
        return WAIT_BIRTHDATE
    context.user_data["birthdate"] = text
    await update.message.reply_text(
        "ℹ️ Введи додаткову персональну інформацію, якщо хочеш (або напиши 'нема'):"
    )
    return WAIT_PERSONAL


async def personal_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text:
        text = "нема"
    context.user_data["personal"] = text

    # Пропонуємо вибір колоди
    keyboard = [
        [InlineKeyboardButton(deck, callback_data=f"deck_{i}")]
        for i, deck in enumerate(DECKS)
    ]
    await update.message.reply_text(
        "🃏 Обери колоду карт:", reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return WAIT_DECK


async def confirmation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().strip()
    if text == "підтверджую":
        # Тут ти можеш підключити генерацію відповіді таролога, а поки заглушка:
        await update.message.reply_text(
            "✨ Дякую за підтвердження! Твій розклад готується...\n(тут буде відповідь таролога)"
        )
        # Очистка userdata
        context.user_data.clear()
        return ConversationHandler.END
    elif text == "скасувати":
        await update.message.reply_text("❌ Розклад скасовано. Якщо хочеш, спробуй ще раз /start")
        context.user_data.clear()
        return ConversationHandler.END
    else:
        await update.message.reply_text("Напиши 'Підтверджую' або 'Скасувати'.")
        return CONFIRMATION


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Дія скасована. Якщо хочеш, почни заново командою /start")
    context.user_data.clear()
    return ConversationHandler.END


def main():
    TOKEN = "7560668855:AAHwS3FGu0aSCn6fP8JBtcfYNgC96W77k7Q"

    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), CallbackQueryHandler(button_handler, pattern="^start_reading$")],
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
    )

    app.add_handler(conv_handler)
    print("Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
