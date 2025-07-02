import os
from dotenv import load_dotenv
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# 1. Загрузка переменных окружения из .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
RENDER_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://{RENDER_HOSTNAME}{WEBHOOK_PATH}"

# 2. Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# 3. Импорт и регистрация роутеров
from handlers.main import router as main_router
from handlers.settings import router as settings_router
dp.include_router(main_router)
dp.include_router(settings_router)

# 4. Запуск вебхука
async def on_startup(app: web.Application):
    await bot.set_webhook(WEBHOOK_URL)
    print("🚀 Webhook установлен:", WEBHOOK_URL)

# 5. Создание и запуск aiohttp-приложения
app = web.Application()
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
app.on_startup.append(on_startup)

# 6. Запуск через web.run_app
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    web.run_app(app, port=port)
