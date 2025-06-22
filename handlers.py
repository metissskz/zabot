from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from states import FenceCalc
from pdf_generator import generate_pdf
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import os

router = Router()

# Главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📐 Рассчитать забор")],
        [KeyboardButton(text="🧠 Задать вопрос GPT")],
        [KeyboardButton(text="📄 Получить PDF")],
        [KeyboardButton(text="🌐 Открыть сайт")],
        [KeyboardButton(text="📞 Связаться с нами")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие:"
)

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет! Я бот ZaborOFF — помогу рассчитать забор и сформировать КП.
Выберите действие:",
        reply_markup=main_menu
    )

@router.message(F.text == "🌐 Открыть сайт")
async def open_site(message: types.Message):
    await message.answer("🌐 Перейдите на сайт: https://zaboroff.kz")

@router.message(F.text == "📞 Связаться с нами")
async def contact_us(message: types.Message):
    await message.answer("📱 Напишите нам в WhatsApp: https://wa.me/77022319176")

@router.message(F.text == "📄 Получить PDF")
async def get_pdf(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if not data:
        await message.answer("Сначала рассчитайте забор 📐")
        return
    file_path = generate_pdf(data)
    await message.answer_document(types.FSInputFile(file_path), caption="📄 Ваше коммерческое предложение")
    await message.answer("Что дальше?", reply_markup=main_menu)

@router.message(F.text == "📐 Рассчитать забор")
async def start_calc(message: types.Message, state: FSMContext):
    await message.answer("Выберите тип забора:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Профнастил")],
            [KeyboardButton(text="Блоки")]
        ],
        resize_keyboard=True
    ))
    await state.set_state(FenceCalc.choosing_type)

@router.message(FenceCalc.choosing_type)
async def choose_type(message: types.Message, state: FSMContext):
    await state.update_data(fence_type=message.text)
    await message.answer("Введите длину забора в метрах:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(FenceCalc.entering_length)

@router.message(FenceCalc.entering_length)
async def enter_length(message: types.Message, state: FSMContext):
    try:
        length = float(message.text)
        await state.update_data(length=length)
        await message.answer("Будет ли ленточный фундамент? (Да/Нет)")
        await state.set_state(FenceCalc.foundation)
    except ValueError:
        await message.answer("Введите число, например: 50")

@router.message(FenceCalc.foundation)
async def ask_foundation(message: types.Message, state: FSMContext):
    answer = message.text.strip().lower()
    if answer not in ("да", "нет"):
        await message.answer("Пожалуйста, введите Да или Нет.")
        return
    has_foundation = answer == "да"
    await state.update_data(foundation=has_foundation)
    await message.answer("Есть ли уклон на участке? (Да/Нет)")
    await state.set_state(FenceCalc.slope)

@router.message(FenceCalc.slope)
async def ask_slope(message: types.Message, state: FSMContext):
    answer = message.text.strip().lower()
    if answer not in ("да", "нет"):
        await message.answer("Пожалуйста, введите Да или Нет.")
        return
    slope = answer == "да"
    await state.update_data(slope=slope)
    await message.answer("✅ Данные приняты. Формирую расчёт...", reply_markup=main_menu)
    # Можно дополнительно показать итоги расчета тут
