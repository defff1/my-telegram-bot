import logging
import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем ключи из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Настраиваем логирование
logging.basicConfig(
 format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
 level=logging.INFO
)

# Настраиваем Gemini API
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
chat = model.start_chat(history=[])

# --- НОВАЯ ВЕРСИЯ КОМАНДЫ /price ---
async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
 """Отправляет статический прайс-лист."""
 price_list = (
  "Прайс-лист на видео:\n\n"
  "1. Изи видео - 100р\n"
  "2. Медиум видео - 150р\n"
  "3. Хард видео - 200р"
 )
 await update.message.reply_text(price_list)

# --- Старые команды, которые остаются без изменений ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
 """Отправляет приветственное сообщение при команде /start."""
 await update.message.reply_text('Привет! Я твой AI-собеседник. Просто напиши мне что-нибудь.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
 """Обрабатывает все текстовые сообщения, отправляя их в Gemini."""
 user_text = update.message.text
 logging.info(f"Получено сообщение от пользователя: {user_text}")

 await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

 try:
  response = chat.send_message(user_text)
  await update.message.reply_text(response.text)
 except Exception as e:
  logging.error(f"Ошибка при обращении к Gemini API: {e}")
  await update.message.reply_text("Произошла ошибка, не могу сейчас ответить. Попробуй позже.")

def main() -> None:
 """Запуск бота."""
 logging.info("Бот запускается...")

 application = Application.builder().token(BOT_TOKEN).build()

 # Добавляем обработчики команд
 application.add_handler(CommandHandler("start", start))
 application.add_handler(CommandHandler("price", price_command)) # Эта команда теперь вызывает новую функцию

 # Добавляем обработчик для всех остальных текстовых сообщений
 application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

 # Запускаем бота
 application.run_polling()

if __name__ == '__main__':
 main()


