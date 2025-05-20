import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Етапи сценарію
WAIT_QUESTION, WAIT_EMOTION, WAIT_BIRTHDATE, WAIT_PERSONAL, WAIT_DECK, WAIT_TAROLOG = range(6)

# Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Почати розклад 🃏", callback_data="start_reading")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привіт! Натисни, щоб почати:", reply_markup=reply_markup)

# Обробка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start_reading":
        await query.edit_message_text("Яке у тебе питання?")
        return WAIT_QUESTION

    elif query.data.startswith("deck_"):
        await query.edit_message_text("Твій розклад готовий ✅")
        return ConversationHandler.END

    elif query.data.startswith("tarolog_"):
        await query.edit_message_text("Дякуємо! Таролог скоро з вами зв'яжеться.")
        return ConversationHandler.END

# Питання користувача
async def question_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["question"] = update.message.text
    await update.message.reply_text("Яку емоцію ти зараз відчуваєш?")
    return WAIT_EMOTION

# Емоція
async def emotion_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["emotion"] = update.message.text
    await update.message.reply_text("Введи свою дату народження (ДД.ММ.РРРР):")
    return WAIT_BIRTHDATE

# Дата народження
async def birthdate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["birthdate"] = update.message.text
    await update.message.reply_text("Напиши щось про себе (коротко):")
    return WAIT_PERSONAL

# Особиста інформація
async def personal_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["personal"] = update.message.text

    keyboard = [
        [InlineKeyboardButton("🔮 Колода Таро 1", callback_data="deck_1")],
        [InlineKeyboardButton("🧿 Колода Таро 2", callback_data="deck_2")],
    ]
    await update.message.reply_text("Оберіть колоду:", reply_markup=InlineKeyboardMarkup(keyboard))
    return WAIT_DECK

# Команда cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Скасовано.")
    return ConversationHandler.END

# Основна функція
def main():
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://yourdomain.com/webhook

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAIT_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, question_handler)],
            WAIT_EMOTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, emotion_handler)],
            WAIT_BIRTHDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, birthdate_handler)],
            WAIT_PERSONAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, personal_handler)],
            WAIT_DECK: [CallbackQueryHandler(button_handler, pattern="^deck_")],
            WAIT_TAROLOG: [CallbackQueryHandler(button_handler, pattern="^tarolog_")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
        allow_reentry=True,
    )

    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^start_reading$"))

    # Запуск у режимі webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 10000)),
        url_path="/webhook",
        webhook_url=f"{WEBHOOK_URL}/webhook"
    )

if __name__ == "__main__":
    main()
