import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")  # або встав свій токен сюди рядком
APP_NAME = os.getenv("APP_NAME")  # https-адреса твого рендера без https://

# Обробник команди /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Кнопка 1", callback_data='btn1'),
            InlineKeyboardButton("Кнопка 2", callback_data='btn2'),
        ],
        [
            InlineKeyboardButton("Кнопка 3", callback_data='btn3'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Привіт! Це тестовий бот з кнопками. Обери кнопку нижче:",
        reply_markup=reply_markup
    )

# Обробник натискання кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # підтверджуємо натискання

    data = query.data
    if data == 'btn1':
        text = "Ви натиснули кнопку 1!"
    elif data == 'btn2':
        text = "Ви натиснули кнопку 2!"
    elif data == 'btn3':
        text = "Ви натиснули кнопку 3!"
    else:
        text = "Невідома кнопка."

    await query.edit_message_text(text=text)

# Основна функція запуску бота
async def main():
    if not TOKEN or not APP_NAME:
        logger.error("Встановіть BOT_TOKEN і APP_NAME у змінних середовища!")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    webhook_url = f"https://{APP_NAME}/webhook/{TOKEN}"
    print(f"✅ Webhook URL: {webhook_url}")

    await app.bot.set_webhook(url=webhook_url)

    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        path=f"/webhook/{TOKEN}",
    )

if __name__ == "__main__":
    asyncio.run(main())
