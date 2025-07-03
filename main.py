import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler

from db import UserDB  # Новый файл с логикой монетизации
from handlers_monetization import router  # Обновлённый handlers.py с оплатой

# 🛠 Загрузка конфигурации
TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_HOST = os.getenv("RENDER_EXTERNAL_HOSTNAME")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://{WEBAPP_HOST}{WEBHOOK_PATH}"

# 🎛 Инициализация бота и dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)

# 💾 Подключение базы данных
db = UserDB()

async def on_startup_web(app: web.Application):
    # Запуск вебхука на Render
    await bot.set_webhook(WEBHOOK_URL)
    print("🚀 Webhook установлен:", WEBHOOK_URL)
    # Подключение БД
    await db.connect()
    await db.init_table()

async def on_shutdown_web(app: web.Application):
    await bot.delete_webhook()
    await db.pool.close()

# 🌐 Создание веб-приложения (для webhook)
app = web.Application()
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
app.on_startup.append(on_startup_web)
app.on_shutdown.append(on_shutdown_web)

if __name__ == "__main__":
    # 🧪 Для запуска локальной разработки (polling)
    async def start_polling():
        await db.connect()
        await db.init_table()
        from aiogram import executor
        executor.start_polling(dp, skip_updates=True)
    asyncio.run(start_polling())
