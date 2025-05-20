import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext

# === ОБОВ'ЯЗКОВО ЗАМІНИ ЦЕ НА СВІЙ ТОКЕН ===
TOKEN = "7560668855:AAHwS3FGu0aSCn6fP8JBtcfYNgC96W77k7Q"
bot = Bot(token=TOKEN)

# Flask-додаток
app = Flask(__name__)

# Dispatcher для обробки повідомлень
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)

# Обробник /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привіт! Я твій Telegram бот. Все працює 😉")

# Додаємо обробник в Dispatcher
dispatcher.add_handler(CommandHandler("start", start))

# Обробка webhook запитів
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

# Тестовий корінь (не обов'язково)
@app.route("/")
def index():
    return "Бот працює ✅"

# Запуск Flask-сервера
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
