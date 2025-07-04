import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from db import UserDB
from handlers import router  # handlers.py с логикой монетизации

# 🔐 Токен бота
TOKEN = os.getenv("BOT_TOKEN")

# 🤖 Инициализация
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)

# 📦 База данных
db = UserDB()

async def main():
    # Подключение к базе
    await db.connect()
    await db.init_table()

    # Запуск бота в режиме polling
    print("🚀 Бот запущен в режиме polling")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
