import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Стадії розмови
(
    ASK_QUESTION,
    ASK_EMOTION,
    ASK_BIRTHDATE,
    ASK_DECK,
    ASK_TAROLOGIST,
    FINAL,
) = range(6)

# Клавіатури для вибору колоди та таролога
deck_buttons = [
    [InlineKeyboardButton("Класична", callback_data='deck_classic')],
    [InlineKeyboardButton("Універсальна", callback_data='deck_universal')],
    [InlineKeyboardButton("Спеціалізована", callback_data='deck_special')],
]

tarologists_buttons = [
    [InlineKeyboardButton(f"Таролог {i+1}", callback_data=f"tarologist_{i+1}")] for i in range(6)
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привіт! Я твій бот Таро.\n"
        "Натисни кнопку нижче, щоб отримати розклад.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🃏 Отримати розклад від таролога", callback_data='start_reading')]
        ])
    )
    return ConversationHandler.END

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'start_reading':
        await query.message.reply_text("Напиши, будь ласка, своє питання або тему для розкладу:")
        return ASK_QUESTION

    elif query.data.startswith('deck_'):
        context.user_data['deck'] = query.data.replace('deck_', '')
        await query.message.reply_text(f"Ви обрали колоду: {context.user_data['deck'].capitalize()}\n"
                                       "Оберіть таролога:",
                                       reply_markup=InlineKeyboardMarkup(tarologists_buttons))
        return ASK_TAROLOGIST

    elif query.data.startswith('tarologist_'):
        context.user_data['tarologist'] = query.data.replace('tarologist_', '')
        # Тут можна обробити або завершити
        await query.message.reply_text("Дякую! Ваше замовлення прийнято. Скоро отримаєте розклад.")
        # Тут можна викликати логіку розкладу таро за chat_id
        return ConversationHandler.END

    elif query.data == 'cancel':
        await query.message.reply_text("Розмова скасована.")
        return ConversationHandler.END

    return ConversationHandler.END

async def ask_emotion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['question'] = update.message.text
    await update.message.reply_text("Опиши свій емоційний стан:")
    return ASK_EMOTION

async def ask_birthdate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['emotion'] = update.message.text
    await update.message.reply_text("Введи дату народження (формат: ДД.ММ.РРРР):")
    return ASK_BIRTHDATE

async def ask_deck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['birthdate'] = update.message.text
    await update.message.reply_text(
        "Оберіть колоду:",
        reply_markup=InlineKeyboardMarkup(deck_buttons)
    )
    return ASK_DECK

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Розмова скасована.')
    return ConversationHandler.END


def main():
    import os

    TOKEN = "7560668855:AAHwS3FGu0aSCn6fP8JBtcfYNgC96W77k7Q"

    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern='^start_reading$')],
        states={
            ASK_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_emotion)],
            ASK_EMOTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_birthdate)],
            ASK_BIRTHDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_deck)],
            ASK_DECK: [CallbackQueryHandler(button_handler, pattern='^deck_')],
            ASK_TAROLOGIST: [CallbackQueryHandler(button_handler, pattern='^tarologist_')],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=True,
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)

    print("Bot started with polling...")
    application.run_polling()


if __name__ == '__main__':
    main()
