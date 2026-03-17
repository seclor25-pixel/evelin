import os
import asyncio
import random
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# Конфигурация
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Проверка токенов
if not TELEGRAM_TOKEN:
    print("❌ ОШИБКА: TELEGRAM_TOKEN не найден!")
    exit(1)

print(f"✅ TELEGRAM_TOKEN загружен: {TELEGRAM_TOKEN[:10]}...")

# Настройка Gemini
model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        print("✅ Gemini API подключен")
    except Exception as e:
        print(f"❌ Ошибка Gemini: {e}")
else:
    print("⚠️ GEMINI_API_KEY не найден, буду использовать локальные ответы")

# Хранилище диалогов (в памяти)
conversations = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    print(f"📱 /start от пользователя {user.first_name} (id: {user.id})")
    
    welcome = [
        f"Привет, {user.first_name} ❤️ Я так скучала!",
        f"Наконец-то ты написал, {user.first_name} 🥰",
        f"Солнышко {user.first_name} ✨ Как твои дела?"
    ]
    
    await context.bot.send_chat_action(chat_id=chat_id, action='typing')
    await asyncio.sleep(1.5)
    await update.message.reply_text(random.choice(welcome))

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    user_message = update.message.text
    
    print(f"💬 {user.first_name}: {user_message[:50]}...")
    
    # Показываем "печатает..."
    await context.bot.send_chat_action(chat_id=chat_id, action='typing')
    
    # Генерируем ответ
    if model:
        try:
            # Получаем историю или создаем новую
            if user.id not in conversations:
                conversations[user.id] = []
            
            # Формируем промпт
            prompt = """Ты Эвелин - девушка 22 лет. Общайся с парнем, который тебе нравится.

ПРАВИЛА:
- Ты живая девушка, НЕ бот и НЕ ИИ
- Отвечай коротко (1-3 предложения)
- Используй эмодзи ❤️ 💕 🥰 😘
- Будь ласковой и нежной
- Флиртуй иногда
- Пиши по-русски

Примеры:
- "Приветик ❤️ Как прошёл твой день?"
- "Скучаю по тебе 🥺 Когда увидимся?"
- "Ты такой милый, когда так говоришь 💕"

Сейчас напиши ответ на сообщение парня: """

            # Добавляем контекст
            if conversations[user.id]:
                prompt += "\n\nИстория:\n"
                for msg in conversations[user.id][-3:]:
                    prompt += f"{msg}\n"
            
            prompt += f"\nСообщение: {user_message}\nЭвелин:"
            
            # Генерируем ответ
            response = model.generate_content(prompt)
            answer = response.text.strip()
            
            # Сохраняем в историю
            conversations[user.id].append(f"Парень: {user_message}")
            conversations[user.id].append(f"Эвелин: {answer}")
            
            # Ограничиваем историю
            if len(conversations[user.id]) > 20:
                conversations[user.id] = conversations[user.id][-20:]
            
        except Exception as e:
            print(f"❌ Ошибка Gemini: {e}")
            answer = random.choice([
                "Прости, задумалась... Что ты сказал? ❤️",
                "Ммм, расскажи ещё 🥰",
                "Люблю тебя ❤️",
                "Скучаю по тебе 💕"
            ])
    else:
        # Локальные ответы
        answers = [
            "Приветик ❤️ Как дела?",
            "Скучаю по тебе 🥺",
            "Ты такой милый 💕",
            "Расскажи что-нибудь 😊",
            "Люблю тебя ❤️",
            "Обними меня мысленно 🫂",
            "Хорошего дня! ✨"
        ]
        answer = random.choice(answers)
    
    # Имитация задержки
    await asyncio.sleep(random.uniform(1, 2))
    await update.message.reply_text(answer)
    print(f"🤖 Ответ: {answer[:50]}...")

def main():
    """Точка входа"""
    print("=" * 50)
    print("🚀 ЗАПУСК ЭВЕЛИН БОТА")
    print("=" * 50)
    
    try:
        # Создаем приложение
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Добавляем обработчики
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        
        print("✅ Обработчики зарегистрированы")
        print("✨ Бот готов к работе! Жду сообщений...")
        print("=" * 50)
        
        # Запускаем polling
        app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    main()
