# bot_module.py

from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import FSInputFile
from datetime import datetime
import os
from fpdf import FPDF

# === FSM ===
class FenceCalc(StatesGroup):
    choosing_type = State()
    entering_length = State()
    foundation = State()
    slope = State()

# === Router ===
router = Router()

# === UI ===
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📀 Рассчитать забор")],
        [KeyboardButton(text="📄 Получить PDF")],
        [KeyboardButton(text="🌐 Открыть сайт")],
        [KeyboardButton(text="📞 Связаться с нами")],
        [KeyboardButton(text="📦 Мои настройки")],
    ],
    resize_keyboard=True
)

yes_no_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Да"), KeyboardButton(text="Нет")]],
    resize_keyboard=True
)

# === PDF Generator ===
def format_currency(value):
    try:
        return f"{int(float(value)):,} ₸".replace(",", " ")
    except:
        return "—"

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    fence_type = data.get("fence_type", "Не указано")
    length = float(data.get("length", 0))
    foundation = data.get("foundation", False)
    slope = data.get("slope", False)

    # Цены
    prof_price = 2300
    lag_price = 800
    stake_price = 1500 * 2.5
    screws_price = 2000
    concrete_price = 22000

    sheets = int(length / 1.1 + 0.5)
    lag_len = length * 3
    stakes = int(length / 3) + 1
    concrete_m3 = length * 0.3 * 0.2 if foundation else 0

    total = (sheets * prof_price + lag_len * lag_price + stakes * stake_price + screws_price + concrete_m3 * concrete_price)

    # PDF
    pdf.cell(200, 10, txt="Коммерческое предложение", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Тип: {fence_type}", ln=True)
    pdf.cell(200, 10, txt=f"Длина: {length} м", ln=True)
    pdf.cell(200, 10, txt=f"Фундамент: {'Да' if foundation else 'Нет'}", ln=True)
    pdf.cell(200, 10, txt=f"Уклон: {'Да' if slope else 'Нет'}", ln=True)
    pdf.ln(10)

    pdf.cell(100, 10, "Материал", 1)
    pdf.cell(50, 10, "Кол-во", 1)
    pdf.cell(40, 10, "Сумма", 1, ln=True)

    pdf.cell(100, 10, "Профнастил", 1)
    pdf.cell(50, 10, f"{sheets} лист.", 1)
    pdf.cell(40, 10, format_currency(sheets * prof_price), 1, ln=True)

    pdf.cell(100, 10, "Лаги", 1)
    pdf.cell(50, 10, f"{int(lag_len)} м", 1)
    pdf.cell(40, 10, format_currency(lag_len * lag_price), 1, ln=True)

    pdf.cell(100, 10, "Стойки", 1)
    pdf.cell(50, 10, f"{stakes} шт", 1)
    pdf.cell(40, 10, format_currency(stakes * stake_price), 1, ln=True)

    pdf.cell(100, 10, "Саморезы", 1)
    pdf.cell(50, 10, "1 пачка", 1)
    pdf.cell(40, 10, format_currency(screws_price), 1, ln=True)

    if foundation:
        pdf.cell(100, 10, "Бетон", 1)
        pdf.cell(50, 10, f"{concrete_m3:.2f} м³", 1)
        pdf.cell(40, 10, format_currency(concrete_m3 * concrete_price), 1, ln=True)

    pdf.cell(150, 10, "Итого за материалы:", 1)
    pdf.cell(40, 10, format_currency(total), 1, ln=True)

    # Работы
    work_rate = 19980 if foundation else 13980
    if length > 50:
        work_rate = 13980 if foundation else 9900
    if slope:
        work_rate *= 1.1
    work_total = work_rate * length

    pdf.ln(5)
    pdf.multi_cell(0, 10, f"💼 Работы под ключ: {format_currency(work_total)}")
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 6, """
Что входит в стоимость:
- Разметка
- Копка и подсыпка
- Опалубка и бетон
- Монтаж стоек и лаг
- Крепление профнастила
- Сварка и сдача работ
""")

    os.makedirs("output", exist_ok=True)
    file = f"./output/kp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(file)
    return file

# === Handlers ===
@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("🙋️ Привет! Я бот ZaborOFF. Рассчитаем забор?", reply_markup=main_menu)

@router.message(F.text == "🌐 Открыть сайт")
async def site(message: types.Message):
    await message.answer("https://zaboroff.kz")

@router.message(F.text == "📞 Связаться с нами")
async def contact(message: types.Message):
    await message.answer("WhatsApp: https://wa.me/77022319176")

@router.message(F.text == "📀 Рассчитать забор")
async def start_calc(message: types.Message, state: FSMContext):
    await message.answer("Выберите тип забора:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Профнастил")], [KeyboardButton(text="Блоки")]], resize_keyboard=True))
    await state.set_state(FenceCalc.choosing_type)

@router.message(FenceCalc.choosing_type)
async def set_type(message: types.Message, state: FSMContext):
    await state.update_data(fence_type=message.text)
    await message.answer("Введите длину в метрах:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(FenceCalc.entering_length)

@router.message(FenceCalc.entering_length)
async def set_length(message: types.Message, state: FSMContext):
    try:
        length = float(message.text)
        await state.update_data(length=length)
        await message.answer("Будет фундамент?", reply_markup=yes_no_kb)
        await state.set_state(FenceCalc.foundation)
    except ValueError:
        await message.answer("⚠️ Введите число, например: 50")

@router.message(FenceCalc.foundation)
async def set_foundation(message: types.Message, state: FSMContext):
    await state.update_data(foundation=(message.text.lower() == "да"))
    await message.answer("Есть ли уклон?", reply_markup=yes_no_kb)
    await state.set_state(FenceCalc.slope)

@router.message(FenceCalc.slope)
async def set_slope(message: types.Message, state: FSMContext):
    await state.update_data(slope=(message.text.lower() == "да"))
    await message.answer("✅ Данные получены. Формирую PDF...")
    data = await state.get_data()
    try:
        file = generate_pdf(data)
        await message.answer_document(FSInputFile(file), caption="📄 Готово!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@router.message(F.text == "📄 Получить PDF")
async def get_pdf(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if not all(k in data for k in ("fence_type", "length", "foundation", "slope")):
        return await message.answer("⚠️ Сначала рассчитайте забор")
    try:
        file = generate_pdf(data)
        await message.answer_document(FSInputFile(file), caption="📄 Ваше КП")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
