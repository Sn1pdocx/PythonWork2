import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Завантажування токену із файлу .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Обробка команди /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Васап чувак!")

# Команда /scream, яка вмикає режим великих літер
async def scream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data["screaming"] = True
    await update.message.reply_text("ВААААААЗААААП, ЧУВААААК!!")


# Команда /whisper, яка повертає звичайний режим
async def whisper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data["screaming"] = False
    await update.message.reply_text("Все, тихо, тихо...")

    # Обробка текстових повідомлень
async def echo (update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if context.chat_data.get("screaming", False):
        text = text.upper()

    await update.message.reply_text(text)

# Команда /menu
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Перевірка поточного режиму роботи
    if context.chat_data.get("screaming", False):
        mode = "Крик"
    else:
        mode = "Звичайний"

    # Створення кнопки
    keyboard = [
        [
            InlineKeyboardButton("Scream", callback_data="scream"),
            InlineKeyboardButton("Whisper", callback_data="whisper")
        ]
    ]

    # Відправлення меню
    await update.message.reply_text(
        f"Меню керування ботом\n\nПоточний режим: {mode}\n\nОбери потрібний режим:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Обробка натискань кнопок меню
async def button_tap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Перевірка натиснутої кнопки
    if query.data == "scream":
        context.chat_data["screaming"] = True
        mode = "Крик"

    elif query.data == "whisper":
        context.chat_data["screaming"] = False
        mode = "Звичайний"

    else:
        return

    # Створення клавіатури
    keyboard = [
        [
            InlineKeyboardButton("Scream", callback_data="scream"),
            InlineKeyboardButton("Whisper", callback_data="whisper")
        ]
    ]

    # Формування оновлений текст меню
    text = f"Меню керування ботом\n\nПоточний режим: {mode}\n\nОбери потрібний режим:"

    # Оновлення повідомлення, якщо його текст змінився
    if query.message.text != text:
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# Запуск бота
def main():
    if not TOKEN:
        raise ValueError("Не знайдено BOT_TOKEN у файлі .env")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("scream", scream))
    app.add_handler(CommandHandler("whisper", whisper))
    app.add_handler(CommandHandler("menu", menu))

    app.add_handler(CallbackQueryHandler(button_tap))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Бот запущений!")
    app.run_polling()

if __name__ == "__main__":
    main()