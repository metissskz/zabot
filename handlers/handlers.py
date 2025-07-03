from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from states import FenceCalc
from pdf_generator import generate_pdf
from db import db  # Инициализированный экземпляр UserDB

router = Router()

# Главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📀 Рассчитать забор")],
        [KeyboardButton(text="🧠 Задать вопрос GPT")],
        [KeyboardButton(text="📄 Получить PDF")],
        [KeyboardButton(text="🌐 Открыть сайт")],
        [KeyboardButton(text="📞 Связаться с нами")],
        [KeyboardButton(text="📦 Мои настройки")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие:"
)

# Кнопки Да / Нет
yes_no_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Да"), KeyboardButton(text="Нет")]],
    resize_keyboard=True
)

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    status = await db.get_status_text(message.from_user.id)
    await message.answer(
        f"Привет! Я бот ZaborOFF \U0001f916\n\n{status}\n\nВыберите действие:",
        reply_markup=main_menu
    )

@router.message(F.text == "🌐 Открыть сайт")
async def open_site(message: types.Message):
    await message.answer("\ud83c\udf10 Перейдите на сайт: https://zaboroff.kz")

@router.message(F.text == "📞 Связаться с нами")
async def contact_us(message: types.Message):
    await message.answer("\ud83d\udcf1 Напишите нам в WhatsApp: https://wa.me/77022319176")

@router.message(F.text == "📄 Получить PDF")
async def get_pdf(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if not await db.has_access(user_id):
        await message.answer("\u274c У вас закончился доступ. Оплатите подписку или купите смету.")
        return

    data = await state.get_data()
    required_fields = ["fence_type", "length", "foundation", "slope"]

    if not all(k in data for k in required_fields):
        await message.answer("❗️Недостаточно данных. Сначала рассчитайте забор 📀")
        return

    try:
        file_path = generate_pdf(data)
        await db.use_credit(user_id)
        await message.answer_document(types.FSInputFile(file_path), caption="📄 Ваше коммерческое предложение")
    except Exception as e:
        await message.answer(f"❌ Ошибка при генерации PDF: {e}")

@router.message(F.text == "📀 Рассчитать забор")
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
        await message.answer("Будет ли ленточный фундамент?", reply_markup=yes_no_kb)
        await state.set_state(FenceCalc.foundation)
    except ValueError:
        await message.answer("Введите число, например: 50")

@router.message(FenceCalc.foundation)
async def ask_foundation(message: types.Message, state: FSMContext):
    answer = message.text.strip().lower()
    if answer not in ("да", "нет"):
        await message.answer("Пожалуйста, нажмите кнопку Да или Нет.", reply_markup=yes_no_kb)
        return
    await state.update_data(foundation=(answer == "да"))
    await message.answer("Есть ли уклон на участке?", reply_markup=yes_no_kb)
    await state.set_state(FenceCalc.slope)

@router.message(FenceCalc.slope)
async def ask_slope(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if not await db.has_access(user_id):
        await message.answer("❌ У вас закончился доступ. Оплатите подписку (2 999 ₸) или одну смету (700 ₸).")
        return

    answer = message.text.strip().lower()
    if answer not in ("да", "нет"):
        await message.answer("Пожалуйста, нажмите кнопку Да или Нет.", reply_markup=yes_no_kb)
        return

    await state.update_data(slope=(answer == "да"))
    data = await state.get_data()

    await message.answer("✅ Данные приняты. Формирую расчёт...")

    try:
        file_path = generate_pdf(data)
        await db.use_credit(user_id)  # списание сметы
        await message.answer_document(types.FSInputFile(file_path), caption="📄 Ваше коммерческое предложение")
    except Exception as e:
        await message.answer(f"❌ Ошибка при генерации PDF: {e}")
