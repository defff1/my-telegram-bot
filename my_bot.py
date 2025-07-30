import logging
import os
import sqlite3
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# --- НАСТРОЙКИ ---

# Загружаем переменные окружения
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
# Загружаем ID админа. Убедись, что добавил его в переменные на Railway!
ADMIN_ID = os.getenv('ADMIN_ID') 

# Настраиваем логирование
logging.basicConfig(
 format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
 level=logging.INFO
)

# --- РАБОТА С БАЗОЙ ДАННЫХ ---

def initialize_db():
 """Создает базу данных и таблицу пользователей, если их нет."""
 # Файл БД будет создан прямо в проекте на Railway
 con = sqlite3.connect('users.db')
 cur = con.cursor()
 # Создаем таблицу, если она не существует. 
 # UNIQUE гарантирует, что один и тот же ID не будет добавлен дважды.
 cur.execute('''
  CREATE TABLE IF NOT EXISTS users (
   chat_id INTEGER PRIMARY KEY,
   username TEXT
  )
 ''')
 con.commit()
 con.close()
 logging.info("База данных успешно инициализирована.")

def add_user_to_db(chat_id: int, username: str):
 """Добавляет нового пользователя в БД."""
 con = sqlite3.connect('users.db')
 cur = con.cursor()
 # Пытаемся вставить нового пользователя. Если он уже есть, ничего не произойдет.
 cur.execute("INSERT OR IGNORE INTO users (chat_id, username) VALUES (?, ?)", (chat_id, username))
 con.commit()
 con.close()

def get_all_users():
 """Возвращает список ID всех пользователей из БД."""
 con = sqlite3.connect('users.db')
 cur = con.cursor()
 cur.execute("SELECT chat_id FROM users")
 # fetchall() возвращает список кортежей [(123,), (456,)], поэтому извлекаем первые элементы
 user_ids = [item[0] for item in cur.fetchall()]
 con.close()
 return user_ids

# --- КОМАНДЫ БОТА ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
 """Обрабатывает /start и добавляет пользователя в базу."""
 user = update.effective_user
 # Добавляем пользователя в нашу базу данных
 add_user_to_db(user.id, user.username)

 start_text = "Привет! Я информационный бот. Используй /help, чтобы увидеть список команд. Теперь ты будешь получать уведомления о важных обновлениях."
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

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
 """
 Команда для рассылки. ДОСТУПНА ТОЛЬКО АДМИНУ.
 Пример использования: /broadcast Новая команда /info добавлена в бота!
 """
 user_id = str(update.effective_user.id)

 # Проверяем, является ли отправитель админом
 if user_id != ADMIN_ID:
  await update.message.reply_text("У вас нет прав для выполнения этой команды.")
  return

 # Получаем текст для рассылки
 message_to_send = ' '.join(context.args)
 if not message_to_send:
  await update.message.reply_text("Пожалуйста, укажите текст для рассылки после команды. Например: /broadcast Привет всем!")
  return

 # Получаем всех пользователей и отправляем им сообщение
 user_ids = get_all_users()
 logging.info(f"Начинаю рассылку для {len(user_ids)} пользователей.")
 await update.message.reply_text(f"Начинаю рассылку. Пользователей в базе: {len(user_ids)}")

 success_count = 0
 for chat_id in user_ids:
  try:
   await context.bot.send_message(chat_id=chat_id, text=message_to_send)
   success_count += 1
   # Добавляем небольшую задержку, чтобы не попасть под лимиты Telegram
   time.sleep(0.1) 
  except Exception as e:
   logging.error(f"Не удалось отправить сообщение пользователю {chat_id}: {e}")

 await update.message.reply_text(f"Рассылка завершена. Сообщение успешно отправлено {success_count} пользователям.")

def main() -> None:
 """Основная функция для запуска бота."""
 # При запуске бота сразу инициализируем БД
 initialize_db()

 logging.info("Бот запускается в режиме с рассылкой...")

 application = Application.builder().token(BOT_TOKEN).build()

 # Регистрируем все команды, включая новую команду для рассылки
 application.add_handler(CommandHandler("start", start_command))
 application.add_handler(CommandHandler("help", help_command))
 application.add_handler(CommandHandler("price", price_command))
 application.add_handler(CommandHandler("subscribe", subscribe_command))
 application.add_handler(CommandHandler("broadcast", broadcast_command))

 # Запускаем бота
 application.run_polling()

if __name__ == '__main__':
 main()


