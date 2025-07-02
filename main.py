import os
from dotenv import load_dotenv
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler

# Загружаем переменные из .env
load_dotenv()

# Токен и вебхук
TOKEN = os.getenv("BOT_TOKEN")
RENDER_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://{RENDER_HOSTNAME}{WEBHOOK_PATH}"

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Подключение роутеров
from handlers import router as main_router
from handlers.settings import router as settings_router

dp.include_router(main_router)
dp.include_router(settings_router)

# Запуск вебхука
async def on_startup(app: web.Application):
    await bot.set_webhook(WEBHOOK_URL)

app = web.Application()
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
app.on_startup.append(on_startup)

# Запуск приложения
if __name__ == "__main__":
    web.run_app(app, port=int(os.getenv('PORT', 8080)))
