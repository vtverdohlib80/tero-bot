import os
import asyncio
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# Стани
ASK_NAME, ASK_AGE = range(2)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Як тебе звати?")
    return ASK_NAME

# Запит імені
async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Скільки тобі років?")
    return ASK_AGE

# Запит віку
async def ask_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data.get("name")
    age = update.message.text
    await update.message.reply_text(f"Дякую, {name}! Тобі {age} років.")
    return ConversationHandler.END

# /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Розмову скасовано.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Основна функція
async def main():
    # Дані з Render
    TOKEN = os.getenv("BOT_TOKEN")  # ОБОВ'ЯЗКОВО додай це до Environment variables на Render
    APP_NAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")  # Render сам додає цю змінну

    if not TOKEN or not APP_NAME:
        print("❌ BOT_TOKEN або RENDER_EXTERNAL_HOSTNAME не задано")
        return

    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_age)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    # Webhook URL
    webhook_url = f"https://{APP_NAME}/webhook/{TOKEN}"
    print(f"✅ Webhook URL: {webhook_url}")

    await app.bot.set_webhook(url=webhook_url)
    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_path=f"/webhook/{TOKEN}",
    )

if __name__ == "__main__":
    asyncio.run(main())
