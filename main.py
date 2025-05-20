from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

import logging

# ====== ВСТАВ СЮДИ СВОЇ ДАНІ ======
BOT_TOKEN = "123456789:ABCdefGhijkLMNOPqrstuVWXYZ1234567890"
WEBHOOK_URL = "https://yourdomain.com/webhook"  # або ngrok URL
# =================================

# Логування
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Стан
ASK_NAME = 1

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Запустити", callback_data="start_clicker")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Вітаю! Натисни кнопку нижче для старту гри.", reply_markup=reply_markup)

# Обробка кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "start_clicker":
        await query.message.reply_text("Гра почалась! Введи своє ім'я:")
        return ASK_NAME

# Отримання імені
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.text
    await update.message.reply_text(f"Привіт, {user_name}! 🎮 Тепер натискай кнопку, щоб майнити!")
    return ConversationHandler.END

# Помилка
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error(msg="Виникла помилка:", exc_info=context.error)

# Головна функція
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        },
        fallbacks=[],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_error_handler(error_handler)

    app.run_webhook(
        listen="0.0.0.0",
        port=8443,
        url_path="webhook",
        webhook_url=f"{WEBHOOK_URL}/webhook"
    )

if __name__ == "__main__":
    main()
