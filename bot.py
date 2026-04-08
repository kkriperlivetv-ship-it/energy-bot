import telebot
from telebot import types, apihelper
from datetime import datetime
import os
import time
from dotenv import load_dotenv

BOT_TOKEN = os.getenv('BOT_TOKEN', 'TOKEN_FROM_RENDER')

# Если токен не найден, но мы на Render — он подставится
if BOT_TOKEN == 'TOKEN_FROM_RENDER':
    print("⚠️ ВНИМАНИЕ: Токен не установлен! Бот не запустится.")
    exit(1)

apihelper.API_URL = 'https://telegg.uno/orig/bot{0}/{1}'
bot = telebot.TeleBot(BOT_TOKEN)

bot = telebot.TeleBot(BOT_TOKEN)

# Хранилище выбора пользователя
user_choice = {}

# --- Клавиатуры ---
def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("📋 Каталог")
    btn2 = types.KeyboardButton("🛒 Купить (по кодовому слову)")
    keyboard.add(btn1, btn2)
    return keyboard

def flavors_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🔥 Burn Сочная энергия")
    btn2 = types.KeyboardButton("🍏🥝 Burn Яблоко-Киви")
    keyboard.add(btn1, btn2)
    return keyboard

# --- Команда /start ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "⚡ *Добро пожаловать в Energy Shop!* ⚡\n\n"
        "У нас вы можете приобрести мощные энергетики Burn.\n"
        "💰 *Оплата:* одно магическое слово: `пж, кедамчик`\n\n"
        "📌 *Каталог:*\n"
        "• Burn «Сочная энергия» (цитрус+мята)\n"
        "• Burn «Яблоко Киви» (свежесть зелёного сада)\n\n"
        "🔽 *Как получить:*\n"
        "1. Напишите `пж, кедамчик`\n"
        "2. Выберите вкус\n"
        "3. Получите чек и скачайте его\n\n"
        "👇 Используйте кнопки:",
        reply_markup=main_keyboard(),
        parse_mode='Markdown'
    )

# --- Команда /info ---
@bot.message_handler(commands=['info'])
def send_info(message):
    bot.send_message(
        message.chat.id,
        "ℹ️ *Energy Shop Bot*\n\n"
        "🤖 Версия: 1.0\n"
        "⚡ Продажа энергетиков Burn\n"
        "💰 Оплата: слово \"пж, кедамчик\"\n"
        "🧾 Выдаём официальный чек\n\n"
        "🚀 Работает 24/7 на Render.com",
        parse_mode='Markdown'
    )

# --- Обработка кнопки "Каталог" ---
@bot.message_handler(func=lambda message: message.text == "📋 Каталог")
def show_catalog(message):
    bot.send_message(
        message.chat.id,
        "📦 *Ассортимент Energy Shop:*\n\n"
        "1️⃣ *Burn «Сочная энергия»* — 450 мл\n"
        "   🔥 Взрывной цитрус + освежающая мята.\n"
        "   💰 Цена: `пж, кедамчик`\n\n"
        "2️⃣ *Burn «Яблоко Киви»* — 450 мл\n"
        "   🍏🥝 Сочное яблоко и кислинка киви.\n"
        "   💰 Цена: `пж, кедамчик`\n\n"
        "Напишите `пж, кедамчик` и выберите вкус!",
        parse_mode='Markdown',
        reply_markup=main_keyboard()
    )

# --- Обработка кнопки "Купить" ---
@bot.message_handler(func=lambda message: message.text == "🛒 Купить (по кодовому слову)")
def buy_prompt(message):
    bot.send_message(
        message.chat.id,
        "🔐 *Подтверждение покупки*\n\n"
        "Пожалуйста, введите кодовое слово:\n"
        "`пж, кедамчик`",
        parse_mode='Markdown'
    )

# --- Волшебное слово ---
@bot.message_handler(func=lambda message: message.text and message.text.lower().strip() == "пж, кедамчик")
def magic_word(message):
    user_choice[message.chat.id] = None
    bot.send_message(
        message.chat.id,
        "✨ *Кодовое слово принято!* ✨\n\n"
        "Выбери вкус энергетика:",
        reply_markup=flavors_keyboard(),
        parse_mode='Markdown'
    )

# --- Выбор вкуса ---
@bot.message_handler(func=lambda message: message.text in ["🔥 Burn Сочная энергия", "🍏🥝 Burn Яблоко-Киви"])
def process_flavor(message):
    user_id = message.chat.id
    flavor = "Burn Сочная энергия" if "Сочная" in message.text else "Burn Яблоко-Киви"
    user_choice[user_id] = flavor
    
    # Генерируем чек
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    username = message.from_user.username or message.from_user.first_name
    full_name = message.from_user.full_name
    
    receipt_text = f"""
╔══════════════════════════════════════╗
║          🧾 ЭНЕРГЕТИК ЧЕК 🧾         ║
╠══════════════════════════════════════╣
║  Покупатель: {full_name} (@{username})
║  Telegram ID: {user_id}
║  Дата: {now}
║  Товар: {flavor}
║  Оплачено: "пж, кедамчик" ✅
║  Сумма: 0.00 руб. (акция)
║  Статус: ОПЛАЧЕН (волшебное слово)
╚══════════════════════════════════════╝
Спасибо за покупку! Желаем энергии 🔥
"""
    
    # Сохраняем в файл
    filename = f"receipt_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(receipt_text)
    
    # Отправляем подтверждение
    bot.send_message(
        user_id,
        f"✅ *{flavor}* выдан!\n\nВот ваш официальный чек:",
        parse_mode='Markdown'
    )
    
    # Отправляем файл чека
    with open(filename, "rb") as f:
        bot.send_document(
            user_id,
            f,
            caption="🧾 Сохраните чек как подтверждение покупки"
        )
    
    # Удаляем временный файл
    os.remove(filename)
    
    # Возвращаем главное меню
    bot.send_message(
        user_id,
        "Что дальше?",
        reply_markup=main_keyboard()
    )

# --- Обработка всего остального ---
@bot.message_handler(func=lambda message: True)
def fallback(message):
    bot.send_message(
        message.chat.id,
        "❓ Не понял команду.\n"
        "Напишите `пж, кедамчик` или используйте кнопки.",
        parse_mode='Markdown',
        reply_markup=main_keyboard()
    )

# --- Запуск бота ---
if __name__ == "__main__":
    print("🚀 Бот Energy Shop запущен на Render.com")
    print(f"🤖 Токен: {BOT_TOKEN[:10]}...")
    print("📡 Используется зеркало API для России")
    print("✅ Бот готов к работе!")
    
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            time.sleep(15)