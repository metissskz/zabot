from fpdf import FPDF
import os
from datetime import datetime

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

    # ✅ Добавляем шрифты (DejaVuSans.ttf и DejaVuSans-Bold.ttf должны быть в папке fonts/)
    pdf.add_font("DejaVu", "", "./fonts/DejaVuSans.ttf", uni=True)
    pdf.add_font("DejaVu", "B", "./fonts/DejaVuSans-Bold.ttf", uni=True)
    pdf.set_font("DejaVu", "", 11)

    # ✅ Логотип (если есть)
    logo_path = "./logo.png"
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=8, w=30)

    # ✅ Реквизиты
    pdf.set_xy(140, 10)
    pdf.set_font("DejaVu", "", 9)
    pdf.multi_cell(60, 5, "ZaborOFF.kz\nСамал-2, ул. Бектурова, 77а\nг. Алматы, Казахстан\n+7 702 231 91 76", align="R")

    pdf.ln(25)
    pdf.set_font("DejaVu", "B", 13)
    pdf.cell(0, 10, "Коммерческое предложение", ln=True, align="C")
    pdf.set_font("DejaVu", "", 11)

    # Данные
    fence_type = safe_get(data, "fence_type", "Не указано")
    try:
        length = float(safe_get(data, "length", 0) or 0)
    except (ValueError, TypeError):
        length = 0
    has_foundation = safe_get(data, "foundation", False)
    slope = safe_get(data, "slope", False)

    pdf.ln(5)
    pdf.cell(0, 8, f"Тип забора: {fence_type}", ln=True)
    pdf.cell(0, 8, f"Длина: {length} м", ln=True)
    pdf.cell(0, 8, f"Фундамент: {'Да' if has_foundation else 'Нет'}", ln=True)
    pdf.cell(0, 8, f"Уклон: {'Да' if slope else 'Нет'}", ln=True)
    pdf.ln(5)

    # Цены
    PROFNASTIL_PRICE = 2300
    LAG_PRICE = 800
    STAKE_PRICE = 1500 * 2.5
    SCREWS_PACK_PRICE = 2000
    CONCRETE_PRICE_M3 = 22000

    # Расчёты
    profile_width = 1.1
    sheets_count = int(length / profile_width + 0.5)
    lag_length = length * 3
    stake_count = int(length / 3) + 1
    concrete_m3 = length * 0.3 * 0.2 if has_foundation else 0

    sheets_total = sheets_count * PROFNASTIL_PRICE
    lag_total = lag_length * LAG_PRICE
    stake_total = stake_count * STAKE_PRICE
    screws_total = SCREWS_PACK_PRICE
    concrete_total = concrete_m3 * CONCRETE_PRICE_M3
    total_material = sheets_total + lag_total + stake_total + screws_total + concrete_total

    # Таблица
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(60, 10, "Материал", 1, 0, "C", True)
    pdf.cell(40, 10, "Расход", 1, 0, "C", True)
    pdf.cell(40, 10, "Цена за ед.", 1, 0, "C", True)
    pdf.cell(50, 10, "Сумма", 1, 1, "C", True)
    pdf.set_font("DejaVu", "", 11)

    def row(label, qty, price, total):
        pdf.cell(60, 10, label, 1)
        pdf.cell(40, 10, qty, 1)
        pdf.cell(40, 10, format_currency(price), 1)
        pdf.cell(50, 10, format_currency(total), 1)
        pdf.ln(10)

    row("Профнастил", f"{sheets_count} лист.", PROFNASTIL_PRICE, sheets_total)
    row("Лаги", f"{int(lag_length)} м", LAG_PRICE, lag_total)
    row("Стойки", f"{stake_count} шт", STAKE_PRICE, stake_total)
    row("Саморезы", "1 пачка", SCREWS_PACK_PRICE, screws_total)
    if has_foundation:
        row("Бетон", f"{concrete_m3:.2f} м³", CONCRETE_PRICE_M3, concrete_total)

    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(140, 10, "Итого за материалы:", 1)
    pdf.cell(50, 10, format_currency(total_material), 1, ln=True)

    # Работы
    pdf.ln(5)
    if length <= 50:
        work_price = 19980 if has_foundation else 13980
    else:
        work_price = 13980 if has_foundation else 9900
    if slope:
        work_price *= 1.1

    work_total = work_price * length
    pdf.set_font("DejaVu", "", 11)
    pdf.multi_cell(0, 8, f"💼 Работы под ключ: {format_currency(work_total)}")

    pdf.set_font("DejaVu", size=10)
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

    os.makedirs("output", exist_ok=True)
    filename = f"./output/kp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename
