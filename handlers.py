from aiogram import F, types
from aiogram.fsm.context import FSMContext
from states import FenceCalc
from aiogram import Router

router = Router()

@router.message(F.text.lower() == "рассчитать забор")
async def start_calc(message: types.Message, state: FSMContext):
    await message.answer("Выберите тип забора: профнастил, сетка, блок.")
    await state.set_state(FenceCalc.choosing_type)

@router.message(FenceCalc.choosing_type)
async def choose_type(message: types.Message, state: FSMContext):
    await state.update_data(fence_type=message.text)
    await message.answer("Введите длину забора в метрах:")
    await state.set_state(FenceCalc.entering_length)

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

        price_per_meter = {
            "профнастил": 5000,
            "сетка": 3000,
            "блок": 8000
        }.get(fence_type.lower(), 5000)

        gate_price = 50000
        total = length * price_per_meter + gates * gate_price

        await message.answer(
            f"Тип: {fence_type}\nДлина: {length} м\nВорота/калитки: {gates}\n\nИтог: {int(total):,} ₸"
        )
        await state.clear()
    except ValueError:
        await message.answer("Введите целое число — количество ворот/калиток.")
