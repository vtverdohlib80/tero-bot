import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

TOKEN = os.environ.get("BOT_TOKEN")

ASK_TOPIC, ASK_EMOTION, ASK_BIRTH, ASK_DECK, ASK_TAROLOGIST = range(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! 🧙‍♀️ Я бот таролога. Натисни '🃏 Отримати розклад від таролога'", 
        reply_markup=ReplyKeyboardMarkup([["🃏 Отримати розклад від таролога"]], resize_keyboard=True))

async def ask_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Яке у тебе питання або тема для розкладу?")
    return ASK_TOPIC

async def ask_emotion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['topic'] = update.message.text
    await update.message.reply_text("Який у тебе емоційний стан?")
    return ASK_EMOTION

async def ask_birth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['emotion'] = update.message.text
    await update.message.reply_text("Введи дату народження або персональну інформацію")
    return ASK_BIRTH

async def ask_deck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['birth'] = update.message.text
    await update.message.reply_text("Оберіть колоду:",
        reply_markup=ReplyKeyboardMarkup([["Класична", "Універсальна", "Спеціалізована"]], resize_keyboard=True))
    return ASK_DECK

async def ask_tarologist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['deck'] = update.message.text
    await update.message.reply_text("Оберіть таролога:",
        reply_markup=ReplyKeyboardMarkup([
            ["Таролог 1", "Таролог 2", "Таролог 3"],
            ["Таролог 4", "Таролог 5", "Таролог 6"]
        ], resize_keyboard=True))
    return ASK_TAROLOGIST

async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['tarologist'] = update.message.text
    user_id = update.effective_chat.id

    result = (
        f"🃏 Розклад:\n"
        f"Тема: {context.user_data['topic']}\n"
        f"Стан: {context.user_data['emotion']}\n"
        f"Народження: {context.user_data['birth']}\n"
        f"Колода: {context.user_data['deck']}\n"
        f"Таролог: {context.user_data['tarologist']}\n"
        f"Chat ID: {user_id}"
    )
    await update.message.reply_text(result)
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🃏 Отримати розклад від таролога$"), ask_topic)],
        states={
            ASK_TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_emotion)],
            ASK_EMOTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_birth)],
            ASK_BIRTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_deck)],
            ASK_DECK: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_tarologist)],
            ASK_TAROLOGIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, finish)],
        },
        fallbacks=[],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    app.run_polling()

if __name__ == "__main__":
    main()
