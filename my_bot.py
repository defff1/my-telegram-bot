import asyncio
import logging
import google.generativeai as genai

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
# Важно добавить этот импорт, чтобы бот показывал "Печатает..."
from aiogram.enums import ChatAction

# Включаем логирование, чтобы видеть, что происходит
logging.basicConfig(level=logging.INFO)

# --- ВАЖНО: ВСТАВЬ СВОИ ДАННЫЕ НИЖЕ ---

# Вставь сюда свой API-ключ от Google AI Studio
# Никогда не выкладывай этот файл с ключом в открытый доступ!
GOOGLE_API_KEY = '' 

# Вставь сюда токен твоего бота
BOT_TOKEN = ''

# --- КОНЕЦ ВАЖНОЙ ЧАСТИ ---

# ... (код выше не меняется)

# Настраиваем подключение к Gemini
try:
 genai.configure(api_key=GOOGLE_API_KEY)
 # ИЗМЕНЯЕМ ТОЛЬКО ЭТУ СТРОКУ
 model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
 logging.critical(f"Не удалось настроить Gemini API. Проверь ключ. Ошибка: {e}")
 exit()

# ... (остальной код не меняется)



# Объект бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
 await message.answer("Привет! Я твой бот-собеседник. Просто напиши мне что-нибудь.")

# Этот обработчик будет срабатывать на ЛЮБОЕ текстовое сообщение
@dp.message()
async def handle_text_message(message: types.Message):
 # Проверяем, что сообщение содержит текст, а не стикер или фото
 if not message.text:
   return

 try:
  # Показываем пользователю, что мы "печатаем"
  # Это дает понять, что бот не завис, а думает
  await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

  # Отправляем текст пользователя в модель Gemini
  # Используем асинхронную версию, чтобы не блокировать бота
  response = await model.generate_content_async(message.text)

  # Отправляем ответ от ИИ пользователю
  await message.answer(response.text)

 except Exception as e:
  logging.error(f"Ошибка при обработке сообщения: {e}")
  await message.answer("Извините, произошла ошибка при обращении к ИИ. Попробуйте еще раз позже.")

async def main():
 # Перед запуском бота, можно вывести в консоль сообщение
 logging.info("Бот запускается...")
 await dp.start_polling(bot)

if __name__ == "__main__":
 asyncio.run(main())

