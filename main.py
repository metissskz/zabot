from handlers import router
import os
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

@dp.message()
async def handle_message(message: types.Message):
    await message.answer("Привет! Я работаю через Webhook на Render!")

# Установка webhook при старте
async def on_startup(app: web.Application):
    await bot.set_webhook(WEBHOOK_URL)

# Подключаем webhook handler
app = web.Application()
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
app.on_startup.append(on_startup)

# Запуск сервера на нужном порту
if __name__ == "__main__":
    web.run_app(app, port=int(os.getenv('PORT', 8080)))
