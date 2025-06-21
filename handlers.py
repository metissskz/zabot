from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from states import FenceCalc

router = Router()

# Кнопки выбора
def get_keyboard(options):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=o)] for o in options],
        resize_keyboard=True,
        one_time_keyboard=True
    )

@router.message(F.text.lower() == "рассчитать забор")
async def start_calc(message: types.Message, state: FSMContext):
    await message.answer("Выберите тип забора:", reply_markup=get_keyboard(["Профнастил", "Блоки"]))
    await state.set_state(FenceCalc.choosing_type)

@router.message(FenceCalc.choosing_type)
async def choose_type(message: types.Message, state: FSMContext):
    fence_type = message.text.lower()
    if fence_type not in ["профнастил", "блоки"]:
        return await message.answer("Пожалуйста, выберите из списка.")
    await state.update_data(fence_type=fence_type)
    await message.answer("Стойки будут из:", reply_markup=get_keyboard(["Металл", "Блоки"]))
    await state.set_state(FenceCalc.choosing_post_type)

@router.message(FenceCalc.choosing_post_type)
async def choose_post_type(message: types.Message, state: FSMContext):
    post_type = message.text.lower()
    if post_type not in ["металл", "блоки"]:
        return await message.answer("Пожалуйста, выберите из списка.")
    await state.update_data(post_type=post_type)
    await message.answer("Введите длину забора в метрах:")
    await state.set_state(FenceCalc.asking_length)

@router.message(FenceCalc.asking_length)
async def input_length(message: types.Message, state: FSMContext):
    try:
        length = float(message.text)
        await state.update_data(length=length)
        await message.answer("Сколько ворот и калиток нужно?")
        await state.set_state(FenceCalc.asking_gate)
    except ValueError:
        await message.answer("Введите число. Например: 50")

@router.message(FenceCalc.asking_gate)
async def input_gates(message: types.Message, state: FSMContext):
    try:
        gates = int(message.text)
        await state.update_data(gates=gates)
        await message.answer("Будет ли ленточный фундамент?", reply_markup=get_keyboard(["Да", "Нет"]))
        await state.set_state(FenceCalc.asking_foundation)
    except ValueError:
        await message.answer("Введите целое число. Например: 1")

@router.message(FenceCalc.asking_foundation)
async def foundation_decision(message: types.Message, state: FSMContext):
    if message.text.lower() == "да":
        await message.answer("Введите длину фундамента в метрах:")
        await state.set_state(FenceCalc.asking_found_length)
    else:
        await finish_calc(message, state, include_foundation=False)

@router.message(FenceCalc.asking_found_length)
async def found_length(message: types.Message, state: FSMContext):
    try:
        length = float(message.text)
        await state.update_data(found_length=length)
        await message.answer("Введите ширину фундамента в метрах:")
        await state.set_state(FenceCalc.asking_found_width)
    except ValueError:
        await message.answer("Введите число. Например: 30")

@router.message(FenceCalc.asking_found_width)
async def found_width(message: types.Message, state: FSMContext):
    try:
        width = float(message.text)
        await state.update_data(found_width=width)
        await message.answer("Введите высоту фундамента в метрах:")
        await state.set_state(FenceCalc.asking_found_height)
    except ValueError:
        await message.answer("Введите число. Например: 0.3")

@router.message(FenceCalc.asking_found_height)
async def found_height(message: types.Message, state: FSMContext):
    try:
        height = float(message.text)
        await state.update_data(found_height=height)
        await finish_calc(message, state, include_foundation=True)
    except ValueError:
        await message.answer("Введите число. Например: 0.5")

# Финальный расчёт
async def finish_calc(message: types.Message, state: FSMContext, include_foundation: bool):
    data = await state.get_data()

    fence_type = data["fence_type"]
    post_type = data["post_type"]
    length = data["length"]
    gates = data["gates"]

    # Цены за метр
    prices = {
        "профнастил": 5000,
        "блоки": 8000
    }
    post_price = 3000 if post_type == "металл" else 5000
    gate_price = 50000

    fence_price = length * prices[fence_type]
    post_count = int(length / 2.5) + 1
    posts_total = post_count * post_price
    gates_total = gates * gate_price

    total = fence_price + posts_total + gates_total
    result = f"Тип забора: {fence_type}\nДлина: {length} м\nСтойки: {post_type} — {post_count} шт\nВорота/калитки: {gates} шт\n"

    if include_foundation:
        f_length = data["found_length"]
        f_width = data["found_width"]
        f_height = data["found_height"]
        volume = f_length * f_width * f_height
        concrete_price_per_m3 = 22000
        concrete_total = volume * con*_
