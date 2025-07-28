import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Загружаем переменные окружения (нужно для токена)
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Настраиваем логирование, чтобы видеть в логах Railway, что бот работает
logging.basicConfig(
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  level=logging.INFO
)

# --- НАШИ КОМАНДЫ ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  """Обрабатывает команду /start."""
  # Я немного обновил текст, так как бот больше не ИИ-собеседник
  start_text = "Привет! Я информационный бот. Используй /help, чтобы увидеть список всех команд."
  await update.message.reply_text(start_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  """Обрабатывает команду /help."""
  help_text = (
    "Здравствуйте, это бот для информации об услугах lonely. \n\n"
    "Вот список команд:\n"
    "• /price - узнать стоимость услуг.\n"
    "• /subscribe - получить ссылки на наши телеграмм каналы."
  )
  await update.message.reply_text(help_text)

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  """Отправляет прайс-лист по команде /price."""
  price_list = (
    "Прайс-лист на видео:\n\n"
    "1. Изи видео - 100р\n"
    "2. Медиум видео - 150р\n"
    "3. Хард видео - 200р"
  )
  await update.message.reply_text(price_list)

async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  """Отправляет ссылки на каналы по команде /subscribe."""
  subscribe_text = (
    "Вот список наших телеграмм каналов:\n\n"
    "https://t.me/lonelyinformati0n\n"
    "https://t.me/lonelyn3ws"
  )
  await update.message.reply_text(subscribe_text)

def main() -> None:
  """Основная функция для запуска бота."""
  logging.info("Бот запускается в режиме команд...")

  application = Application.builder().token(BOT_TOKEN).build()

  # Регистрируем все наши команды
  application.add_handler(CommandHandler("start", start_command))
  application.add_handler(CommandHandler("help", help_command))
  application.add_handler(CommandHandler("price", price_command))
  application.add_handler(CommandHandler("subscribe", subscribe_command))

  # Запускаем бота
  application.run_polling()

if __name__ == '__main__':
  main()

