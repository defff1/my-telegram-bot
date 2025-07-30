import logging
import os
import sqlite3
import time
import shlex
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# --- НАСТРОЙКИ ---

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID') 

logging.basicConfig(
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  level=logging.INFO
)

# --- РАБОТА С БАЗОЙ ДАННЫХ ---

def initialize_db():
  """Создает базу данных и таблицу пользователей, если их нет."""
  con = sqlite3.connect('users.db')
  cur = con.cursor()
  # Используем тройные кавычки для надежности
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
  # ИСПРАВЛЕНО: Запрос обернут в тройные кавычки, чтобы избежать ошибок копирования
  cur.execute(
    '''INSERT OR IGNORE INTO users (chat_id, username) VALUES (?, ?)''',
    (chat_id, username)
  )
  con.commit()
  con.close()

def get_all_user_ids():
  """Возвращает список ID всех пользователей из БД."""
  con = sqlite3.connect('users.db')
  cur = con.cursor()
  cur.execute('''SELECT chat_id FROM users''')
  user_ids = [item[0] for item in cur.fetchall()]
  con.close()
  return user_ids

def get_all_users_with_username():
  """Возвращает список (chat_id, username) всех пользователей из БД."""
  con = sqlite3.connect('users.db')
  cur = con.cursor()
  cur.execute('''SELECT chat_id, username FROM users''')
  users = cur.fetchall()
  con.close()
  return users

# --- КОМАНДЫ БОТА ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  user = update.effective_user
  add_user_to_db(user.id, user.username)
  start_text = "Привет! Я информационный бот. Используй /help, чтобы увидеть список команд. Теперь ты будешь получать уведомления о важных обновлениях."
  await update.message.reply_text(start_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  help_text = (
    "Здравствуйте, это бот для информации об услугах lonely. \n\n"
    "Вот список команд:\n"
    "• /price - узнать стоимость услуг.\n"
    "• /subscribe - получить ссылки на наши телеграмм каналы."
  )
  await update.message.reply_text(help_text)

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  price_list = (
    "Прайс-лист на видео:\n\n"
    "1. Изи видео - 100р\n"
    "2. Медиум видео - 150р\n"
    "3. Хард видео - 200р"
  )
  await update.message.reply_text(price_list)

async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  subscribe_text = (
    "Вот список наших телеграмм каналов:\n\n"
    "https://t.me/lonelyinformati0n\n"
    "https://t.me/lonelyn3ws"
  ) 
 await update.message.reply_text(subscribe_text)

# --- АДМИНСКИЕ КОМАНДЫ ---

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  user_id = str(update.effective_user.id)
  if user_id != ADMIN_ID:
    await update.message.reply_text("У вас нет прав для выполнения этой команды.")
    return

  message_to_send = ' '.join(context.args)
  if not message_to_send:
    await update.message.reply_text("Пожалуйста, укажите текст для рассылки. Пример: /broadcast Привет всем!")
    return

  user_ids = get_all_user_ids()
  await update.message.reply_text(f"Начинаю рассылку для {len(user_ids)} пользователей.")
  success_count = 0
  for chat_id in user_ids:
    try:
      await context.bot.send_message(chat_id=chat_id, text=message_to_send)
      success_count += 1
      time.sleep(0.1)
    except Exception as e:
      logging.error(f"Не удалось отправить сообщение пользователю {chat_id}: {e}")
  await update.message.reply_text(f"Рассылка завершена. Успешно отправлено {success_count} пользователям.")

async def list_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  user_id = str(update.effective_user.id)
  if user_id != ADMIN_ID:
    await update.message.reply_text("У вас нет прав для выполнения этой команды.")
    return

  users_data = get_all_users_with_username()
  if not users_data:
    await update.message.reply_text("В базе данных пока нет пользователей.")
    return

  user_list_text = f"👥 Список пользователей в базе ({len(users_data)}):\n\n"
  for i, (chat_id, username) in enumerate(users_data, 1):
    display_name = f"@{username}" if username else f"ID: {chat_id}"
    user_list_text += f"{i}. {display_name}\n"
  await update.message.reply_text(user_list_text)

async def poll_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  user_id = str(update.effective_user.id)
  if user_id != ADMIN_ID:
    await update.message.reply_text("У вас нет прав для выполнения этой команды.")
    return

  command_args_text = update.message.text.replace('/poll', '', 1).strip()
  if not command_args_text:
    await update.message.reply_text("Ошибка: вы не указали параметры для опроса.\n\nИспользуйте формат:\n`/poll \"Вопрос\" \"Ответ 1\" \"Ответ 2\"`", parse_mode='Markdown')
    return

  try:
    poll_args = shlex.split(command_args_text)
  except ValueError:
    await update.message.reply_text("Ошибка в синтаксисе. Убедитесь, что все кавычки закрыты правильно.")
    return

  if len(poll_args) < 3:
    await update.message.reply_text("Ошибка: нужен минимум 1 вопрос и 2 варианта ответа.\n\nИспользуйте формат:\n`/poll \"Вопрос\" \"Ответ 1\" \"Ответ 2\"`", parse_mode='Markdown')
    return

  question = poll_args[0]
  options = poll_args[1:11] # Ограничиваем 10 вариантами

  user_ids = get_all_user_ids()
  await update.message.reply_text(f"Начинаю рассылку опроса для {len(user_ids)} пользователей...")
  success_count = 0
  for chat_id in user_ids:
    try:
      await context.bot.send_poll(chat_id=chat_id, question=question, options=options, is_anonymous=True)
      success_count += 1
      time.sleep(0.1)
    except Exception as e:
      logging.error(f"Не удалось отправить опрос пользователю {chat_id}: {e}")
  await update.message.reply_text(f"Рассылка опроса завершена. Успешно отправлено {success_count} пользователям.")

def main() -> None:
  """Основная функция для запуска бота."""
  initialize_db()

  application = Application.builder().token(BOT_TOKEN).build()

  application.add_handler(CommandHandler("start", start_command))
  application.add_handler(CommandHandler("help", help_command))
  application.add_handler(CommandHandler("price", price_command))
  application.add_handler(CommandHandler("subscribe", subscribe_command))

  application.add_handler(CommandHandler("broadcast", broadcast_command))
  application.add_handler(CommandHandler("listusers", list_users_command))
  application.add_handler(CommandHandler("poll", poll_command))

  logging.info("Бот успешно запущен.")
  application.run_polling()

if __name__ == '__main__':
  main()



