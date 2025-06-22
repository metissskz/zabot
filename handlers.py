from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router
from pdf_generator import generate_pdf
from aiogram.types import FSInputFile

router = Router()

class FenceCalc(StatesGroup):
    choosing_type = State()
    choosing_post = State()
    entering_length = State()
    choosing_foundation = State()
    entering_found_width = State()
    entering_found_height = State()

@router.message(F.text.lower() == "рассчитать забор")
async def start_calc(message: types.Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Профнастил")],
        [KeyboardButton(text="Блоки")]
    ], resize_keyboard=True)
    await message.answer("Выберите тип забора:", reply_markup=kb)
    await state.set_state(FenceCalc.choosing_type)

@router.message(FenceCalc.choosing_type)
async def choose_type(message: types.Message, state: FSMContext):
    await state.update_data(fence_type=message.text)
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Металл")],
        [KeyboardButton(text="Блоки")]
    ], resize_keyboard=True)
    await message.answer("Стойки из металла или блоков?", reply_markup=kb)
    await state.set_state(FenceCalc.choosing_post)

@router.message(FenceCalc.choosing_post)
async def choose_post(message: types.Message, state: FSMContext):
    await state.update_data(post_type=message.text)
    await message.answer("Введите длину забора в метрах:")
    await state.set_state(FenceCalc.entering_length)

@router.message(FenceCalc.entering_length)
async def enter_length(message: types.Message, state: FSMContext):
    try:
        length = float(message.text)
        await state.update_data(length=length)
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Да")],
            [KeyboardButton(text="Нет")]
        ], resize_keyboard=True)
        await message.answer("Нужен ли ленточный фундамент?", reply_markup=kb)
        await state.set_state(FenceCalc.choosing_foundation)
    except ValueError:
        await message.answer("Введите число, например: 30")

@router.message(FenceCalc.choosing_foundation)
async def choose_foundation(message: types.Message, state: FSMContext):
    if message.text.lower() == "да":
        await state.update_data(foundation=True)
        await message.answer("Введите ширину фундамента в метрах:")
        await state.set_state(FenceCalc.entering_found_width)
    else:
        await state.update_data(foundation=False, foundation_volume=0)
        await finish_calc(message, state)

@router.message(FenceCalc.entering_found_width)
async def enter_found_width(message: types.Message, state: FSMContext):
    try:
        width = float(message.text)
        await state.update_data(found_width=width)
        await message.answer("Введите высоту фундамента в метрах:")
        await state.set_state(FenceCalc.entering_found_height)
    except ValueError:
        await message.answer("Введите число, например: 0.3")

@router.message(FenceCalc.entering_found_height)
async def enter_found_height(message: types.Message, state: FSMContext):
    try:
        height = float(message.text)
        data = await state.get_data()
        length = data["length"]
        volume = round(length * data['found_width'] * height, 2)
        await state.update_data(foundation_volume=volume)
        await finish_calc(message, state)
    except ValueError:
        await message.answer("Введите число, например: 0.5")

async def finish_calc(message: types.Message, state: FSMContext):
    data = await state.get_data()
    length = data["length"]

    # Стойки
    num_posts = int(length // 3) + 1
    post_price = 1500 * 2.5  # 2.5 м длина стойки
    total_posts = num_posts * post_price

    # Лаги
    lag_length = length * 3
    lag_price = 800
    total_lags = lag_length * lag_price

    # Профнастил
    prof_sheet_width = 1.1
    num_sheets = int(length / prof_sheet_width) + 1
    prof_price = 14000
    total_prof = num_sheets * prof_price

    # Саморезы
    screw_packs = max(1, num_sheets // 7)
    screw_price = 2000
    total_screws = screw_packs * screw_price

    # Бетон
    concrete_price = 22000
    if data["foundation"]:
        concrete_volume = data["foundation_volume"]
        total_concrete = int(concrete_volume * concrete_price)
    else:
        concrete_volume = 0
        total_concrete = 0

    materials = [
        {"name": "Стойки 60×60×2 мм", "count": num_posts, "price": post_price},
        {"name": "Лаги 40×40×1.5 мм", "count": lag_length, "price": lag_price},
        {"name": "Профнастил 2×1.1 м", "count": num_sheets, "price": prof_price},
        {"name": "Саморезы (пачка)", "count": screw_packs, "price": screw_price}
    ]
    if data['foundation']:
        materials.append({"name": "Бетон М300", "count": concrete_volume, "price": concrete_price})

    data.update({"materials": materials})

    path = generate_pdf(data)
    await message.answer_document(FSInputFile(path), caption="📄 Коммерческое предложение готово!")
    await state.clear()
