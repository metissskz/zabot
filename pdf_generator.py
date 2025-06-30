from fpdf import FPDF
import os
from datetime import datetime
import math

def format_currency(value):
    try:
        return f"{int(float(value)):,} ₸".replace(",", " ")
    except (ValueError, TypeError):
        return "—"

def safe_get(data, key, default=None):
    return data[key] if key in data else default

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()

    # 🔤 Шрифты
    pdf.add_font('DejaVu', '', './fonts/DejaVuSans.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', './fonts/DejaVuSans-Bold.ttf', uni=True)
    pdf.set_font('DejaVu', '', 11)

    # 📥 Получение данных
    fence_type = safe_get(data, "fence_type", "Не указано")
    try:
        length = float(safe_get(data, "length", 0) or 0)
    except (ValueError, TypeError):
        length = 0
    has_foundation = safe_get(data, "foundation", False)
    slope = safe_get(data, "slope", False)

    # 🧱 Цены
    PROFNASTIL_PRICE = 2300
    LAG_PRICE = 800
    STAKE_PRICE = 1500 * 2.5
    SCREWS_PACK_PRICE = 2000
    CONCRETE_PRICE_M3 = 22000

    SCREWS_PER_SHEET = 15
    SCREWS_PER_PACK = 150

    # 📐 Размеры
    PROFILE_WIDTH = 1.1  # м
    SHEETS_COUNT = math.ceil(length / PROFILE_WIDTH)
    LAG_LENGTH = length * 3
    STAKE_COUNT = int(length / 3) + 1

    screws_needed = SHEETS_COUNT * SCREWS_PER_SHEET
    screw_packs = math.ceil(screws_needed / SCREWS_PER_PACK)

    # 📦 Расчёт материалов
    sheets_total = SHEETS_COUNT * PROFNASTIL_PRICE
    lag_total = LAG_LENGTH * LAG_PRICE
    stake_total = STAKE_COUNT * STAKE_PRICE
    screws_total = screw_packs * SCREWS_PACK_PRICE

    # 📏 Фундамент (если есть)
    FOUNDATION_WIDTH = 0.3  # метра
    FOUNDATION_HEIGHT = 0.2  # метра
    concrete_m3 = length * FOUNDATION_WIDTH * FOUNDATION_HEIGHT if has_foundation else 0
    concrete_total = concrete_m3 * CONCRETE_PRICE_M3

    total_material = sheets_total + lag_total + stake_total + screws_total + concrete_total

    # 📄 Заголовок
    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 10, txt="Коммерческое предложение", ln=True, align="C")
    pdf.ln(8)
    pdf.cell(200, 10, txt=f"Тип забора: {fence_type}", ln=True)
    pdf.cell(200, 10, txt=f"Длина: {length} м", ln=True)
    pdf.cell(200, 10, txt=f"Фундамент: {'Да' if has_foundation else 'Нет'}", ln=True)
    pdf.cell(200, 10, txt=f"Уклон: {'Да' if slope else 'Нет'}", ln=True)
    pdf.ln(5)

    # 🧾 Таблица материалов
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('DejaVu', 'B', 11)
    pdf.cell(60, 10, "Материал", 1, 0, 'C', True)
    pdf.cell(40, 10, "Расход", 1, 0, 'C', True)
    pdf.cell(40, 10, "Цена за ед.", 1, 0, 'C', True)
    pdf.cell(50, 10, "Сумма", 1, 1, 'C', True)
    pdf.set_font('DejaVu', '', 11)

    rows = [
        ("Профнастил", f"{SHEETS_COUNT} лист.", PROFNASTIL_PRICE, sheets_total),
        ("Лаги", f"{int(LAG_LENGTH)} м", LAG_PRICE, lag_total),
        ("Стойки", f"{STAKE_COUNT} шт", STAKE_PRICE, stake_total),
        ("Саморезы", f"{screw_packs} пач. ({screws_needed} шт)", SCREWS_PACK_PRICE, screws_total)
    ]

    if has_foundation:
        rows.append(("Бетон", f"{concrete_m3:.2f} м³", CONCRETE_PRICE_M3, concrete_total))

    for name, qty, price, total in rows:
        pdf.cell(60, 10, name, 1)
        pdf.cell(40, 10, qty, 1)
        pdf.cell(40, 10, format_currency(price), 1)
        pdf.cell(50, 10, format_currency(total), 1)
        pdf.ln(10)

    # 🔢 Итого за материалы
    pdf.set_font('DejaVu', 'B', 11)
    pdf.cell(140, 10, "Итого за материалы:", 1)
    pdf.cell(50, 10, format_currency(total_material), 1, ln=True)

    # 🔧 Стоимость работ
    if length <= 50:
        work_price = 19980 if has_foundation else 13980
    else:
        work_price = 13980 if has_foundation else 9900
    if slope:
        work_price *= 1.1

    work_total = work_price * length

    pdf.ln(5)
    pdf.set_font('DejaVu', '', 11)
    pdf.multi_cell(0, 8, f"💼 Работы под ключ: {format_currency(work_total)}")

    # 📌 Пояснение к работам
    pdf.set_font('DejaVu', size=10)
    lines = [
        "Что входит в стоимость работ:",
        "- Разметка",
        "- Подготовка и копка траншей",
        "- Подсыпка и трамбовка",
        "- Установка опалубки и помощь по аренде",
        "- Армирование",
        "- Заливка фундамента",
        "- Демонтаж опалубки",
        "- Монтаж стоек и лаг",
        "- Крепление профнастила",
        "- Сварочные работы"
    ]
    for line in lines:
        pdf.multi_cell(0, 6, line)

    # 💾 Сохранение
    os.makedirs("output", exist_ok=True)
    filename = f"./output/kp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename
