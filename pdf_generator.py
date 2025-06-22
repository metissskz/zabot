from fpdf import FPDF
import os
from datetime import datetime

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Helvetica', size=12)

    fence_type = data.get("fence_type", "Не указано")
    length = data.get("length", 0)
    has_foundation = data.get("foundation", False)
    slope = data.get("slope", False)

    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 10, txt="Коммерческое предложение", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Тип забора: {fence_type}", ln=True)
    pdf.cell(200, 10, txt=f"Длина: {length} м", ln=True)
    pdf.cell(200, 10, txt=f"Фундамент: {'Да' if has_foundation else 'Нет'}", ln=True)
    pdf.cell(200, 10, txt=f"Уклон: {'Да' if slope else 'Нет'}", ln=True)
    pdf.ln(10)

    PROFNASTIL_PRICE = 2300
    PROFILE_WIDTH = 1.1
    PROFILE_HEIGHT = 2
    SHEETS_COUNT = int((length / PROFILE_WIDTH) + 0.5)
    sheets_price = SHEETS_COUNT * PROFNASTIL_PRICE

    LAG_LENGTH = length * 3
    LAG_PRICE_M = 800
    lag_total = LAG_LENGTH * LAG_PRICE_M

    STAKE_DISTANCE = 3
    stake_count = int(length / STAKE_DISTANCE) + 1
    stake_price = 1500 * 2.5 * stake_count

    screws = 2000
    total_material = sheets_price + lag_total + stake_price + screws

    if has_foundation:
        concrete_m3 = length * 0.3 * 0.2
        concrete_price = concrete_m3 * 22000
    else:
        concrete_m3 = 0
        concrete_price = 0

    total_material += concrete_price

    pdf.cell(200, 10, txt=f"Профнастил ({SHEETS_COUNT} листов): {sheets_price:,} ₸", ln=True)
    pdf.cell(200, 10, txt=f"Лаги ({LAG_LENGTH} м): {lag_total:,} ₸", ln=True)
    pdf.cell(200, 10, txt=f"Стойки ({stake_count} шт): {int(stake_price):,} ₸", ln=True)
    pdf.cell(200, 10, txt=f"Саморезы: {screws:,} ₸", ln=True)
    if has_foundation:
        pdf.cell(200, 10, txt=f"Бетон ({concrete_m3:.2f} м³): {int(concrete_price):,} ₸", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"💰 Итого за материалы: {int(total_material):,} ₸", ln=True)

    if length <= 50:
        work_price = 19980 if has_foundation else 13980
    else:
        work_price = 13980 if has_foundation else 9900
    if slope:
        work_price *= 1.1

    work_total = length * work_price
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"💼 Работы под ключ: {int(work_total):,} ₸", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt=\"\"\"В стоимость входит:
- Разметка
- Подготовка траншеи
- Подсыпка, утрамбовка
- Опалубка, аренда и доставка
- Армирование, обвязка арматуры
- Заливка бетона
- Монтаж и демонтаж опалубки
- Монтаж забора, сварочные работы
""")
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, txt="ZaborOFF — расчет и монтаж заборов", align="C")

    filename = f"/mnt/data/kp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename
