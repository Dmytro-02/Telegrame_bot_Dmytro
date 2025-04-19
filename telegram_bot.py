from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import random

import os
TOKEN = os.getenv("TOKEN")


user_data = {}


# Игра где я угадываю число 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = random.randint(1, 100)
    user_data[update.effective_user.id] = {"number": number, "attempts": 0}
    await update.message.reply_text("🎯 Я загадал число от 1 до 100. Угадай!") # Hádej, číslo jsem si vybral od 1 do 100!

async def guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text

    if not message.isdigit():
        await update.message.reply_text("❌ Введи число.") # Zadej číslo!
        return

    guess = int(message)
    target = user_data.get(user_id, {}).get("number")

    if target is None:
        await update.message.reply_text("Сначала напиши /start.") # Nejprve napiš. /start
        return

    user_data[user_id]["attempts"] += 1

    if guess < target:
        await update.message.reply_text("📉 Слишком мало.") # Příliš málo.
    elif guess > target:
        await update.message.reply_text("📈 Слишком много.") # Příliš mnoho
    else:
        tries = user_data[user_id]["attempts"]
        await update.message.reply_text(f"🎉 Ты угадал за {tries} попыток!") # Uhádl jsi za {tries} pokusů!
        user_data.pop(user_id)


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, guess))

    app.run_polling()



if __name__ == '__main__':
    main()
