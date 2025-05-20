import os
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    CallbackQueryHandler, ConversationHandler
)


async def on_startup(app):
    webhook_url = os.environ["WEBHOOK_URL"]
    await app.bot.set_webhook(url=webhook_url)

def main():
    TOKEN = os.environ["BOT_TOKEN"]

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

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_path="/webhook",
        on_startup=on_startup
    )

if __name__ == "__main__":
    main()
