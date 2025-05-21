import asyncio
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler
)

import os

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # типу https://tero-bot.onrender.com

async def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            'ASK_NAME': [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            'ASK_AGE': [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_age)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    app.add_handler(conv_handler)

    # 🔴 Встановлюємо webhook явно
    await app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")

    # 🔵 Запускаємо бота на вебхуку
    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=f"{WEBHOOK_URL}/webhook"
    )

if __name__ == "__main__":
    asyncio.run(main())
