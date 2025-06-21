from aiogram import Bot, Dispatcher, types, executor
import logging
import os

API_TOKEN = os.getenv("BOT_TOKEN") or "PASTE_YOUR_TOKEN_HERE"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.answer("Добро пожаловать в ZABOROFF калькулятор!
Введите длину забора в метрах:")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)