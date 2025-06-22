from fpdf import FPDF
import os
from datetime import datetime

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()

    # Добавление шрифта, поддерживающего кириллицу
    font_path = "fonts/DejaVuSans.ttf"
    if not os.path.exists(font_path):
        raise FileNotFoundError("❌ Шрифт fonts/DejaVuSans.ttf не найден")

    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.set_font("DejaVu", size=12)

    fence_type = data.get("fence_type", "Не указано")
    length = data.get("length", 0)
    has_foundation = data.get("foundation", False)
    slope = data.get("slope", False)

    pdf.cell(200, 10, txt="Коммерческое предложение", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Тип забора: {fence_type}", ln=True)
    pdf.cell(200, 10, txt=f"Длина: {length} м", ln=True)
    pdf.cell(200, 10, txt=f"Фундамент: {'Да' if has_foundation else 'Нет'}", ln=True)
    pdf.cell(200, 10, txt=f"Уклон: {'Да' if slope else 'Нет'}", ln=True)
    pdf.ln(10)

    # Расчёты ...
    # (оставь как у тебя, они не влияют на эту ошибку)

    pdf.multi_cell(0, 10, txt="""В стоимость входит:
- Разметка
- Подготовка траншеи
- Подсыпка, утрамбовка
- Опалубка, аренда и доставка
- Армирование, обвязка арматуры
- Заливка бетона
- Монтаж и демонтаж опалубки
- Монтаж забора, сварочные работы
""")

    pdf.set_font("DejaVu", size=10)
    pdf.cell(0, 10, txt="ZaborOFF — расчет и монтаж заборов", align="C")

    os.makedirs("output", exist_ok=True)
    filename = f"./output/kp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename
