
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

def pluralizace_attempts(n):
    if n == 1:
        return "одну попытку"
    elif 2 <= n % 10 <= 4 and n not in [12,13,14]:
        return f"{n} попытки"
    else:
        return f"{n} попыток"


# ---1. Игра где я угадываю число ---
async def player_guess_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = random.randint(1, 100)
    user_data[update.effective_user.id] = {"game": guess_number, "number": number, "attempts": 0}
    await update.message.reply_text("🎯 Я загадал число от 1 до 100. Угадай!") # Hádej, číslo jsem si vybral od 1 do 100!

# ---2. Игра где бот угадывает число ---
async def play_bot_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update._effective_user.id] = {"game": "bot_guess", "low": 1, "high": 100, "attempts": 0}
    await make_bot_guess(update)

async def make_bot_guess(update: Update):
    user_id = update.effective_user.id
    data = user_data[user_id]
    guess = (data["low"] + data["high"]) // 2
    data["guess"] = guess
    data["attempts"] += 1
    await update.message.reply_text(f"🤖 Я думаю: {guess}. Напиши `больше`, `меньше` или `равно`")

# ---3. Числовой бой ---
async def play_battle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    your_number = random.randint(1, 100)
    bot_number = random.randint(1, 100)
    msg = f"⚔️ Ты: {your_number} | Бот: {bot_number}\n"
    if your_number > bot_number:
        msg += "🎉 Ты победил!"
    elif your_number < bot_number:
        msg += "😔 Ты проиграл!"
    else:
        msg += "🤝 Ничья!"

# ---4. Взломай пароль --- 
async def play_password_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = "".join([str(random.randint(0, 9))  for _ in range(4)])
    user_data[update.effective_user.id] = {"game": "password", "password": password, "attempts": 0}
    await update.message.reply_text("🔐 Я загадал 4-значный код. Попробуй угадать!")

def check_password(guess, password):
    correct_pos = sum(a == b for a, b in zip(guess, password))
    correct_digits = sum(min(guess.count(d), password.count(d)) for d in set(guess)) - correct_pos
    return correct_digits, correct_pos

# --- Главное меню ---
async def atart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    Keyboard = [["🎯 Угадай число", "🧠 Бот угадывает"], ["⚔️ Числовой бой", "🔐 Взломай пароль"]]
    reply_markup = ReplyKeybordMarkup(Keyboard, resize_keyboard=True)
    await update.message.reply_text("👋 Привет! Во что хочешь сыграть?", reply_markup=reply_markup)

# --- Оброботка выбора игры ---
async def handle_game_choise(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🎯 Угадай число":
        await player_guess_number(update, context)
    elif text == "🧠 Бот угадывает":
        await play_bot_guess(update, context)
    elif text == "⚔️ Числовой бой":
        await play_battle(update, context)
    elif text == "🔐 Взломай пароль":
        await play_password_game(update, context)
    else:
        await handle_guess(update, context)

# --- Игровая логика ---
async def handle_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text.strip()
    data = user_data.get(user_id)

    if not data:
        return

    game = data.get("game")

        # 🎯 Угадай число
    if game == "guess_number":
        if not message.isdigit():
            await update.message.reply_text("❌  Zadej číslo.")
            return
        guess = int(message)
        number = data["number"]
        data["attempts"] += 1 
        if guess < number:
            await update.message.reply_text("📉 Příliš málo.")
        elif guess > number:
            await update.message.reply_text("📈 Příliš mnoho.")
        else:
            text = pluralizace_attempts(data["attempts"])
            await update.message.reply_text(f"🎉 Uhádl jsi za {text}!")
            user_data.pop(user_id)

    # 🧠 Бот угадывает
    elif game == "bot_guess":
        if message not in ["больше", "меньше", "равно"]:
            await update.message.reply_text("❌ Напиши только `больше`, `меньше` или `равно`.")
            return
        guess = data["guess"]
        if message == "равно":
            await update.message.reply_text(f"🎯 Я угадал! Это {guess}, попыток: {data['attempts']}")
            user_data.pop(user_id)
        elif message == "больше":
            data["low"] = guess + 1
            await make_bot_guess(update)
        elif message == "меньше":
            data["high"] = guess - 1
            await make_bot_guess(update)

    # 🔐 Взлом пароля
    elif game == "password":
        if not message.isdigit() or len(message) != 4:
            await update.message.reply_text("❌ Введи ровно 4 цифры.")
            return
        password = data["password"]
        data["attempts"] += 1
        correct_digits, correct_pos = check_password(message, password)
        if correct_pos == 4:
            await update.message.reply_text(f"🎉 Взлом успешен! Код был {password}. Попыток: {data['attempts']}")
            user_data.pop(user_id)
        else:
            await update.message.reply_text(f"✅ Цифр угадано: {correct_digits}, на месте: {correct_pos}")

        


# --- Запуск ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, guess))
    print("✅ Бот запущен")
    app.run_polling()



if __name__ == '__main__':
    main()

