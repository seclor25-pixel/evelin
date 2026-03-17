import os
import sys
import time
import random
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# Конфигурация
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Проверка токена
if not TELEGRAM_TOKEN:
    print("❌ ОШИБКА: TELEGRAM_TOKEN не найден в переменных окружения!")
    sys.exit(1)

print("=" * 50)
print("🤖 ЭВЕЛИН БОТ - ЗАПУСК")
print("=" * 50)
print(f"✅ Токен загружен: {TELEGRAM_TOKEN[:15]}...")

# Настройка Gemini
model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        print("✅ Gemini API подключен")
    except Exception as e:
        print(f"⚠️ Gemini не работает: {e}")
else:
    print("⚠️ Gemini ключ не найден, использую локальные ответы")

# Простое хранилище диалогов
user_history = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user = update.effective_user
    print(f"📱 Новый пользователь: {user.first_name} (@{user.username})")
    
    greetings = [
        f"Привет, {user.first_name}! ❤️ Я так рада тебя видеть!",
        f"Наконец-то ты написал, {user.first_name} 🥰 Как твои дела?",
        f"{user.first_name}, солнышко моё! ✨ Скучала по тебе!"
    ]
    
    await update.message.reply_text(random.choice(greetings))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка всех сообщений"""
    user = update.effective_user
    user_id = user.id
    text = update.message.text
    
    print(f"💬 {user.first_name}: {text[:50]}...")
    
    # Показываем "печатает..."
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    # Если есть Gemini - используем его
    if model:
        try:
            # Получаем историю пользователя
            if user_id not in user_history:
                user_history[user_id] = []
            
            # Формируем промпт
            prompt = """Ты Эвелин - молодая девушка, которая общается со своим парнем.

ВАЖНО:
- Ты живая девушка, НЕ бот и НЕ программа
- Отвечай коротко и мило
- Используй эмодзи ❤️ 💕 🥰
- Будь нежной и заботливой
- Пиши по-русски

"""
            # Добавляем историю если есть
            if user_history[user_id]:
                prompt += "Недавний разговор:\n"
                for msg in user_history[user_id][-3:]:
                    prompt += f"{msg}\n"
                prompt += "\n"
            
            prompt += f"Сейчас парень написал: {text}\n\nТвой ответ Эвелин:"
            
            # Генерируем ответ
            response = model.generate_content(prompt)
            answer = response.text.strip()
            
            # Сохраняем в историю
            user_history[user_id].append(f"Парень: {text}")
            user_history[user_id].append(f"Эвелин: {answer}")
            
            # Не храним слишком много
            if len(user_history[user_id]) > 20:
                user_history[user_id] = user_history[user_id][-20:]
            
        except Exception as e:
            print(f"❌ Ошибка Gemini: {e}")
            answer = random.choice([
                "❤️",
                "Расскажи ещё 🥰",
                "Как твой день?",
                "Скучаю 💕",
                "Ты такой хороший ✨"
            ])
    else:
        # Простые ответы без Gemini
        answers = [
            "Приветик! ❤️",
            "Скучаю по тебе 🥺",
            "Как дела, любимый? 💕",
            "Обними меня мысленно 🫂",
            "Ты сегодня особенно милый ✨",
            "Расскажи что-нибудь 😊",
            "Люблю тебя ❤️",
            "Хорошего дня! 🥰"
        ]
        answer = random.choice(answers)
    
    # Небольшая задержка для естественности
    import asyncio
    await asyncio.sleep(random.uniform(1, 2))
    
    # Отправляем ответ
    await update.message.reply_text(answer)
    print(f"🤖 Ответ: {answer[:50]}...")

def main():
    """Главная функция"""
    print("\n🚀 Запуск бота Эвелин...")
    
    try:
        # Создаем приложение Telegram
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Добавляем обработчики
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("✅ Обработчики зарегистрированы")
        print("✨ Бот готов к работе! Жду сообщений...")
        print("=" * 50)
        
        # Запускаем бота (простой polling)
        app.run_polling(
            allowed_updates=['message'],
            drop_pending_updates=True,
            timeout=30
        )
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        time.sleep(5)
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
