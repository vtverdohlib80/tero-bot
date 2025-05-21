import os
import logging
import asyncio

from fastapi import FastAPI, Request
import uvicorn

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# --- Налаштування ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
APP_NAME = os.getenv("APP_NAME")  # без https://, наприклад: my-bot-123.onrender.com
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"https://{APP_NAME}{WEBHOOK_PATH}"
PORT = int(os.environ.get("PORT", 10000))

# --- Логування ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Telegram Application ---
app = Application.builder().token(BOT_TOKEN).build()

# --- FastAPI App ---
fastapi_app = FastAPI()


# --- Обробник команди /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("💰 Отримати бонус", callback_data="bonus"),
            InlineKeyboardButton("📊 Статистика", callback_data="stats"),
        ],
        [
            InlineKeyboardButton("👥 Реферали", callback_data="refs"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Привіт! Це тестовий бот із кнопками. Вибери дію нижче:",
        reply_markup=reply_markup
    )


# --- Обробник Callback-кнопок ---
@app.callback_query_handler()
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "bonus":
        await query.edit_message_text("🎁 Ти отримав бонус!")
    elif query.data == "stats":
        await query.edit_message_text("📊 Статистика наразі недоступна.")
    elif query.data == "refs":
        await query.edit_message_text("👥 У тебе поки немає рефералів.")
    else:
        await query.edit_message_text("❓ Невідома дія.")


# --- Webhook endpoint ---
@fastapi_app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    await app.update_queue.put(data)
    return {"ok": True}


# --- Асинхронна функція запуску ---
async def main():
    await app.initialize()
    await app.bot.set_webhook(WEBHOOK_URL)
    logger.info(f"✅ Webhook встановлено: {WEBHOOK_URL}")
    await app.start()
    await app.updater.start_polling()
    await app.run_until_disconnected()


# --- Запуск FastAPI та Telegram ---
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    uvicorn.run(fastapi_app, host="0.0.0.0", port=PORT)
