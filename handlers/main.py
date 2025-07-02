from aiogram import Router, types
from aiogram.filters import CommandStart

router = Router()

@router.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer("Привет! Я бот ZaborOFF. Готов к расчётам!")
@router.message()
async def echo_message(message: types.Message):
    await message.answer(f"Вы написали: {message.text}")
