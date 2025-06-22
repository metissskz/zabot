from fpdf import FPDF
import os
from datetime import datetime

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)

    fence_type = data.get("fence_type", "Не указано")
    length = data.get("length", 0)
    has_foundation = data.get("foundation", False)
    slope = data.get("slope", False)

    # Расчётные параметры
    PROFILE_WIDTH = 1.1
    PROFNASTIL_PRICE = 2300
    LAG_PRICE = 800
    STAKE_PRICE_M = 1500
    STAKE_LENGTH = 2.5
    STAKE_PRICE = STAKE_PRICE_M * STAKE_LENGTH
    SCREW_PRICE = 2000
    CONCRETE_PRICE_M3 = 22000

    # Расчёты
    sheets_count = int(length / PROFILE_WIDTH + 0.5)
    sheets_cost = sheets_count * PROFNASTIL_PRICE

    lag_length = length * 3
    lag_cost = lag_length * LAG_PRICE

    stake_count = int(length / 3) + 1
    stake_cost = stake_count * STAKE_PRICE

    screw_count = 1
    screw_cost = SCREW_PRICE

    if has_foundation:
        concrete_volume = round(length * 0.3 * 0.2, 2)
        concrete_cost = concrete_volume * CONCRETE_PRICE_M3
    else:
        concrete_volume = 0
        concrete_cost = 0

    # Общая сумма за материалы
    total_material = sheets_cost + lag_cost + stake_cost + screw_cost + concrete_cost

    # Монтажные работы
    if length <= 50:
        work_price_per_m = 19980 if has_foundation else 13980
    else:
        work_price_per_m = 13980 if has_foundation else 9900
    if slope:
        work_price_per_m *= 1.1

    work_total = int(length * work_price_per_m)

    # Заголовок
    pdf.cell(200, 10, txt="Коммерческое предложение", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Тип забора: {fence_type}", ln=True)
    pdf.cell(200, 10, txt=f"Длина: {length} м", ln=True)
    pdf.cell(200, 10, txt=f"Фундамент: {'Да' if has_foundation else 'Нет'}", ln=True)
    pdf.cell(200, 10, txt=f"Уклон: {'Да' if slope else 'Нет'}", ln=True)
    pdf.ln(10)

    # Таблица материалов
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.cell(60, 10, "Материал", 1)
    pdf.cell(40, 10, "Расход", 1)
    pdf.cell(45, 10, "Цена за ед.", 1)
    pdf.cell(45, 10, "Сумма", 1, ln=True)
    pdf.set_font("Helvetica", size=12)

    pdf.cell(60, 10, "Профнастил", 1)
    pdf.cell(40, 10, f"{sheets_count} листов", 1)
    pdf.cell(45, 10, f"{PROFNASTIL_PRICE:,} ₸", 1)
    pdf.cell(45, 10, f"{sheets_cost:,} ₸", 1, ln=True)

    pdf.cell(60, 10, "Лаги", 1)
    pdf.cell(40, 10, f"{lag_length} м", 1)
    pdf.cell(45, 10, f"{LAG_PRICE:,} ₸", 1)
    pdf.cell(45, 10, f"{lag_cost:,} ₸", 1, ln=True)

    pdf.cell(60, 10, "Стойки", 1)
    pdf.cell(40, 10, f"{stake_count} шт", 1)
    pdf.cell(45, 10, f"{int(STAKE_PRICE):,} ₸", 1)
    pdf.cell(45, 10, f"{int(stake_cost):,} ₸", 1, ln=True)

    pdf.cell(60, 10, "Саморезы", 1)
    pdf.cell(40, 10, f"{screw_count} пачка", 1)
    pdf.cell(45, 10, f"{screw_cost:,} ₸", 1)
    pdf.cell(45, 10, f"{screw_cost:,} ₸", 1, ln=True)

    if has_foundation:
        pdf.cell(60, 10, "Бетон", 1)
        pdf.cell(40, 10, f"{concrete_volume} м³", 1)
        pdf.cell(45, 10, f"{CONCRETE_PRICE_M3:,} ₸", 1)
        pdf.cell(45, 10, f"{int(concrete_cost):,} ₸", 1, ln=True)

    pdf.set_font("Helvetica", style="B", size=12)
    pdf.cell(145, 10, "Итого за материалы:", 1)
    pdf.cell(45, 10, f"{int(total_material):,} ₸", 1, ln=True)
    pdf.ln(5)

    # Монтаж
    pdf.set_font("Helvetica", size=12)
    pdf.cell(200, 10, txt=f"💼 Монтажные работы: {work_total:,} ₸", ln=True)
    pdf.multi_cell(0, 10, txt="""
В стоимость работ под ключ входит:
- Разметка
- Подготовка и копка траншей
- Подсыпка и трамбовка
- Установка опалубки и помощь по аренде
- Армирование
- Заливка фундамента
- Демонтаж опалубки
- Монтаж стоек и лаг
- Крепление профнастила
- Сварочные работы
    """)

    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 10, txt="ZaborOFF — расчет и монтаж заборов", align="C")

    os.makedirs("output", exist_ok=True)
    filename = f"./output/kp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename
