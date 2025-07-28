import asyncio
import logging
import os # <-- ДОБАВИЛИ ЭТОТ ВАЖНЫЙ ИМПОРТ

import google.generativeai as genai
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ChatAction
from aiogram.filters.command import Command

logging.basicConfig(level=logging.INFO)

# --- ИЗМЕНИЛИ ЭТОТ БЛОК ---
# Теперь ключи берутся из "переменных окружения" сервера
# Это безопасный способ, чтобы не светить ключи в  коде
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
BOT_TOKEN = os.getenv('BOT_TOKEN')
# -------------------------

# Проверка, что ключи вообще существуют
if not GOOGLE_API_KEY or not BOT_TOKEN:
  logging.critical("Ключи GOOGLE_API_KEY или BOT_TOKEN не найдены в окружении!")
  exit()

# Настраиваем подключение к Gemini
try:
  genai.configure(api_key=GOOGLE_API_KEY)
  model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
  logging.critical(f"Не удалось настроить Gemini API: {e}")
  exit()

# Объект бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
  await message.answer("Привет! Я твой бот-собеседник. Просто напиши мне что-нибудь.")

# Обработчик текстовых сообщений
@dp.message()
async def handle_text_message(message: types.Message):
  if not message.text:
    return

  try:
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    response = await model.generate_content_async(message.text)
    await message.answer(response.text)
  except Exception as e:
    logging.error(f"Ошибка при обработке сообщения: {e}")
    await message.answer("Извините, произошла ошибка при обращении к ИИ. Попробуйте еще раз позже.")

async def main():
  logging.info("Бот запускается...")
  await dp.start_polling(bot)

if __name__ == "__main__":
  asyncio.run(main())


