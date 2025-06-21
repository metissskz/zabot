from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from states import FenceCalc

router = Router()

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Рассчитать забор")]
    ],
    resize_keyboard=True
)

type_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Профнастил"), KeyboardButton(text="Блоки")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

pillar_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Металл"), KeyboardButton(text="Блоки")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

foundation_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

@router.message(F.text.lower() == "рассчитать забор")
async def start_calc(message: types.Message, state: FSMContext):
    await message.answer("Выберите тип забора:", reply_markup=type_keyboard)
    await state.set_state(FenceCalc.choosing_type)

@router.message(FenceCalc.choosing_type)
async def choose_type(message: types.Message, state: FSMContext):
    await state.update_data(fence_type=message.text.lower())
    await message.answer("Выберите тип стоек:", reply_markup=pillar_keyboard)
    await state.set_state(FenceCalc.choosing_pillar)

@router.message(FenceCalc.choosing_pillar)
async def choose_pillar(message: types.Message, state: FSMContext):
    await state.update_data(pillar_type=message.text.lower())
    await message.answer("Будет ли ленточный фундамент?", reply_markup=foundation_keyboard)
    await state.set_state(FenceCalc.ask_foundation)

@router.message(FenceCalc.ask_foundation)
async def ask_foundation(message: types.Message, state: FSMContext):
    await state.update_data(has_foundation=message.text.lower())
    if message.text.lower() == "да":
        await message.answer("Введите размеры фундамента в формате: длина ширина высота (в метрах)")
        await state.set_state(FenceCalc.entering_foundation_size)
    else:
        await message.answer("Введите длину забора в метрах:")
        await state.set_state(FenceCalc.entering_length)

@router.message(FenceCalc.entering_foundation_size)
async def enter_foundation_size(message: types.Message, state: FSMContext):
    try:
        l, w, h = map(float, message.text.strip().split())
        concrete_volume = l * w * h
        await state.update_data(concrete_volume=concrete_volume)
        await message.answer("Введите длину забора в метрах:")
        await state.set_state(FenceCalc.entering_length)
    except Exception:
        await message.answer("Формат: длина ширина высота, например: 50 0.3 0.5")

@router.message(FenceCalc.entering_length)
async def enter_length(message: types.Message, state: FSMContext):
    try:
        length = float(message.text)
        await state.update_data(length=length)
        await message.answer("Сколько ворот и калиток нужно?")
        await state.set_state(FenceCalc.entering_gates)
    except ValueError:
        await message.answer("Введите число в метрах, например: 50")

@router.message(FenceCalc.entering_gates)
async def enter_gates(message: types.Message, state: FSMContext):
    try:
        gates = int(message.text)
        data = await state.get_data()
        fence_type = data["fence_type"]
        length = data["length"]
        pillar_type = data["pillar_type"]
        concrete_volume = data.get("concrete_volume", 0)

        price_per_meter = {
            "профнастил": 5000,
            "блоки": 8000
        }.get(fence_type, 5000)

        gate_price = 50000
        concrete_price = 22000  # за м3

        total = length * price_per_meter + gates * gate_price + concrete_volume * concrete_price

        await message.answer(
            f"Тип: {fence_type}\n"
            f"Стойки: {pillar_type}\n"
            f"Длина: {length} м\n"
            f"Ворота/калитки: {gates}\n"
            f"Бетон: {concrete_volume:.2f} м³\n\n"
            f"Итог: {int(total):,} ₸"
        )
        await state.clear()
    except ValueError:
        await message.answer("Введите целое число — количество ворот/калиток.")
