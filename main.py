from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    CallbackQueryHandler, ConversationHandler, ContextTypes
)

BOT_TOKEN = "встав_тут_свій_токен"

WAIT_QUESTION, WAIT_EMOTION, WAIT_BIRTHDATE, WAIT_PERSONAL, WAIT_DECK, WAIT_TAROLOG, CONFIRMATION = range(7)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Почати розклад", callback_data="start_reading")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привіт! Я бот таро. Натисни кнопку нижче, щоб почати:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start_reading":
        await query.message.reply_text("Напиши питання, яке тебе турбує:")
        return WAIT_QUESTION

    elif query.data.startswith("deck_"):
        await query.message.reply_text("Тепер обери таролога:")
        # Можна додати список кнопок
        return WAIT_TAROLOG

    elif query.data.startswith("tarolog_"):
        await query.message.reply_text("Дякую! Ось твій розклад: 🔮 ...")
        return ConversationHandler.END

async def question_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["question"] = update.message.text
    await update.message.reply_text("Як ти себе почуваєш?")
    return WAIT_EMOTION

async def emotion_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["emotion"] = update.message.text
    await update.message.reply_text("Напиши свою дату народження:")
    return WAIT_BIRTHDATE

async def birthdate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["birthdate"] = update.message.text
    await update.message.reply_text("Як тебе звати?")
    return WAIT_PERSONAL

async def personal_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    keyboard = [[InlineKeyboardButton("Таро Долі", callback_data="deck_fate")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Обери колоду:", reply_markup=reply_markup)
    return WAIT_DECK

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Розклад скасовано.")
    return ConversationHandler.END

async def on_startup(app):
    webhook_url = "https://твоє-посилання-на-render.onrender.com/webhook"  # заміни на своє
    await app.bot.set_webhook(webhook_url)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(button_handler, pattern="^start_reading$")
        ],
        states={
            WAIT_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, question_handler)],
            WAIT_EMOTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, emotion_handler)],
            WAIT_BIRTHDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, birthdate_handler)],
            WAIT_PERSONAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, personal_handler)],
            WAIT_DECK: [CallbackQueryHandler(button_handler, pattern="^deck_")],
            WAIT_TAROLOG: [CallbackQueryHandler(button_handler, pattern="^tarolog_")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    app.add_handler(conv_handler)

    app.run_webhook(
        listen="0.0.0.0",
        port=10000,
        webhook_path="/webhook",
        on_startup=on_startup
    )

if __name__ == "__main__":
    main()
