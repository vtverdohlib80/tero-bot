import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Змінні середовища - встановіть перед запуском
TOKEN = os.getenv("BOT_TOKEN")      # Ваш Telegram Bot Token
APP_NAME = os.getenv("APP_NAME")    # Ваш домен без https://, наприклад: tero-bot-33.onrender.com
PORT = int(os.getenv("PORT", 8443)) # Порт для вебхука (Render автоматично виставляє PORT)

if not TOKEN or not APP_NAME:
    logger.error("Встановіть змінні середовища BOT_TOKEN і APP_NAME!")
    exit(1)

# Команда /start — показує кнопки
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Кнопка 1", callback_data='button1')],
        [InlineKeyboardButton("Кнопка 2", callback_data='button2')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привіт! Оберіть кнопку:", reply_markup=reply_markup)

# Обробка натискання кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'button1':
        await query.edit_message_text(text="Ви натиснули кнопку 1")
    elif query.data == 'button2':
        await query.edit_message_text(text="Ви натиснули кнопку 2")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Додаємо обробники
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    # Запускаємо вебхук
    await app.start()
    await app.updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://{APP_NAME}/webhook/{TOKEN}"
    )
    logger.info(f"✅ Webhook URL: https://{APP_NAME}/webhook/{TOKEN}")

    # Чекаємо сигналів для завершення
    await app.updater.idle()

if __name__ == "__main__":
    asyncio.run(main())
