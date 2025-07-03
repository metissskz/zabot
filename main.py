import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Router
from aiogram.filters import CommandStart
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

class Form(StatesGroup):
    with_fundament = State()
    spacing = State()
    length = State()
    slope = State()
    currency = State()

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🔨 С фундаментом")],
        [KeyboardButton(text="🛠️ Без фундамента")]
    ], resize_keyboard=True)
    await message.answer("Привет! Я бот ZaborOFF. Готов к расчётам!", reply_markup=kb)
    await state.set_state(Form.with_fundament)

@router.message(Form.with_fundament)
async def ask_spacing(message: Message, state: FSMContext):
    await state.update_data(with_fundament=message.text)
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="2 метра")],
        [KeyboardButton(text="3 метра")]
    ], resize_keyboard=True)
    await message.answer("Выберите расстояние между стойками:", reply_markup=kb)
    await state.set_state(Form.spacing)

@router.message(Form.spacing)
async def ask_length(message: Message, state: FSMContext):
    await state.update_data(spacing=message.text)
    await message.answer("Введите длину забора в метрах:")
    await state.set_state(Form.length)

@router.message(Form.length)
async def ask_slope(message: Message, state: FSMContext):
    await state.update_data(length=message.text)
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Да")],
        [KeyboardButton(text="Нет")]
    ], resize_keyboard=True)
    await message.answer("Есть ли уклон на участке?", reply_markup=kb)
    await state.set_state(Form.slope)

@router.message(Form.slope)
async def ask_currency(message: Message, state: FSMContext):
    await state.update_data(slope=message.text)
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="₸ Тенге")],
        [KeyboardButton(text="₽ Рубли")]
    ], resize_keyboard=True)
    await message.answer("Выберите валюту:", reply_markup=kb)
    await state.set_state(Form.currency)

@router.message(Form.currency)
async def complete(message: Message, state: FSMContext):
    data = await state.update_data(currency=message.text)
    await message.answer("Спасибо! Вы завершили ввод. Продолжим в следующем шаге...")
