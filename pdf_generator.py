from fpdf import FPDF
import os
from datetime import datetime

def format_currency(value):
    try:
        return f"{int(float(value)):,} ₸".replace(",", " ")
    except (ValueError, TypeError):
        return "—"

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()

    # Добавляем шрифты
    pdf.add_font('DejaVu', '', './fonts/DejaVuSans.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', './fonts/DejaVuSans-Bold.ttf', uni=True)
    pdf.set_font('DejaVu', '', 11)

    # Безопасно извлекаем данные
    fence_type = data.get("fence_type", "Не указано")
    try:
        length = float(data.get("length", 0) or 0)
    except (ValueError, TypeError):
        length = 0
    has_foundation = data.get("foundation", False)
    slope = data.get("slope", False)

    # Заголовок
    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 10, txt="Коммерческое предложение", ln=True, align="C")
    pdf.ln(8)
    pdf.cell(200, 10, txt=f"Тип забора: {fence_type}", ln=True)
    pdf.cell(200, 10, txt=f"Длина: {length} м", ln=True)
    pdf.cell(200, 10, txt=f"Фундамент: {'Да' if has_foundation else 'Нет'}", ln=True)
    pdf.cell(200, 10, txt=f"Уклон: {'Да' if slope else 'Нет'}", ln=True)
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
    sheets_total = sheets_count * PROFNASTIL_PRICE

    lag_length = length * 3
    lag_total = lag_length * LAG_PRICE

    stake_count = int(length / 3) + 1
    stake_total = stake_count * STAKE_PRICE

    screws_total = SCREWS_PACK_PRICE

    concrete_m3 = length * 0.3 * 0.2 if has_foundation else 0
    concrete_total = concrete_m3 * CONCRETE_PRICE_M3

    total_material = sheets_total + lag_total + stake_total + screws_total + concrete_total

    # Таблица
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('DejaVu', 'B', 11)
    pdf.cell(60, 10, "Материал", 1, 0, 'C', True)
    pdf.cell(40, 10, "Расход", 1, 0, 'C', True)
    pdf.cell(40, 10, "Цена за ед.", 1, 0, 'C', True)
    pdf.cell(50, 10, "Сумма", 1, 1, 'C', True)
    pdf.set_font('DejaVu', '', 11)

    pdf.cell(60, 10, "Профнастил", 1, 0)
    pdf.cell(40, 10, f"{sheets_count} лист.", 1, 0)
    pdf.cell(40, 10, format_currency(PROFNASTIL_PRICE), 1, 0)
    pdf.cell(50, 10, format_currency(sheets_total), 1, 1)

    pdf.cell(60, 10, "Лаги", 1, 0)
    pdf.cell(40, 10, f"{int(lag_length)} м", 1, 0)
    pdf.cell(40, 10, format_currency(LAG_PRICE), 1, 0)
    pdf.cell(50, 10, format_currency(lag_total), 1, 1)

    pdf.cell(60, 10, "Стойки", 1, 0)
    pdf.cell(40, 10, f"{stake_count} шт", 1, 0)
    pdf.cell(40, 10, format_currency(STAKE_PRICE), 1, 0)
    pdf.cell(50, 10, format_currency(stake_total), 1, 1)

    pdf.cell(60, 10, "Саморезы", 1, 0)
    pdf.cell(40, 10, "1 пачка", 1, 0)
    pdf.cell(40, 10, format_currency(SCREWS_PACK_PRICE), 1, 0)
    pdf.cell(50, 10, format_currency(screws_total), 1, 1)

    if has_foundation:
        pdf.cell(60, 10, "Бетон", 1, 0)
        pdf.cell(40, 10, f"{concrete_m3:.2f} м³", 1, 0)
        pdf.cell(40, 10, format_currency(CONCRETE_PRICE_M3), 1, 0)
        pdf.cell(50, 10, format_currency(concrete_total), 1, 1)

    pdf.set_font('DejaVu', 'B', 11)
    pdf.cell(140, 10, "Итого за материалы:", 1)
    pdf.cell(50, 10, format_currency(total_material), 1, 1)

    # Работы
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
    pdf.set_font('DejaVu', size=10)
    pdf.multi_cell(0, 7, """Что входит в стоимость работ:
- Разметка
- Подготовка и копка траншей
- Подсыпка и трамбовка
- Установка опалубки и помощь по аренде
- Армирование
- Заливка фундамента
- Демонтаж опалубки
- Монтаж стоек и лаг
- Крепление профнастила
- Сварочные работы""")

    os.makedirs("output", exist_ok=True)
    filename = f"./output/kp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename
