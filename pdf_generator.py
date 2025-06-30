from fpdf import FPDF
import os
from datetime import datetime

LOGO_PATH = "./logo.jpg"  # предварительно сохрани изображение под этим именем в папке проекта

def format_currency(value):
    try:
        return f"{int(float(value)):,} ₸".replace(",", " ")
    except (ValueError, TypeError):
        return "—"

def safe_get(data, key, default=None):
    return data.get(key, default)

class PDF(FPDF):
    def header(self):
        if os.path.exists(LOGO_PATH):
            self.image(LOGO_PATH, 10, 8, 25)
        self.set_font("DejaVu", "B", 12)
        self.cell(0, 10, "Коммерческое предложение", ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-20)
        self.set_font("DejaVu", "", 9)
        self.set_text_color(100)
        self.cell(0, 6, "Zaboroff.kz | Самал-2, ул. Бектурова, д. 77а", ln=True, align="C")
        self.cell(0, 6, "2GIS г. Алматы, Казахстан | 📞 +77022319176", align="C")

def generate_pdf(data):
    pdf = PDF()
    pdf.add_page()

    # Шрифты
    pdf.add_font("DejaVu", "", "./fonts/DejaVuSans.ttf", uni=True)
    pdf.add_font("DejaVu", "B", "./fonts/DejaVuSans-Bold.ttf", uni=True)
    pdf.set_font("DejaVu", "", 11)

    # Данные
    fence_type = safe_get(data, "fence_type", "Не указано")
    try:
        length = float(safe_get(data, "length", 0) or 0)
    except (ValueError, TypeError):
        length = 0
    has_foundation = safe_get(data, "foundation", False)
    slope = safe_get(data, "slope", False)

    # Основные параметры
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Тип забора: {fence_type}", ln=True)
    pdf.cell(0, 10, f"Длина: {length} м", ln=True)
    pdf.cell(0, 10, f"Фундамент: {'Да' if has_foundation else 'Нет'}", ln=True)
    pdf.cell(0, 10, f"Уклон: {'Да' if slope else 'Нет'}", ln=True)
    pdf.ln(5)

    # Цены
    PROFNASTIL_PRICE = 2300
    LAG_PRICE = 800
    STAKE_PRICE = 1500 * 2.5
    SCREWS_PACK_PRICE = 2000
    CONCRETE_PRICE_M3 = 22000

    # Расчёт
    profile_width = 1.1
    sheets_count = int(length / profile_width + 0.5)
    lag_length = length * 3
    stake_count = int(length / 3) + 1
    screws_total = SCREWS_PACK_PRICE  # 1 пачка на забор < 100 м
    concrete_m3 = length * 0.3 * 0.2 if has_foundation else 0

    sheets_total = sheets_count * PROFNASTIL_PRICE
    lag_total = lag_length * LAG_PRICE
    stake_total = stake_count * STAKE_PRICE
    concrete_total = concrete_m3 * CONCRETE_PRICE_M3
    total_material = sheets_total + lag_total + stake_total + screws_total + concrete_total

    # Таблица
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("DejaVu", "B", 10)
    pdf.cell(65, 8, "Материал", 1, 0, "C", True)
    pdf.cell(35, 8, "Расход", 1, 0, "C", True)
    pdf.cell(35, 8, "Цена за ед.", 1, 0, "C", True)
    pdf.cell(55, 8, "Сумма", 1, 1, "C", True)
    pdf.set_font("DejaVu", "", 10)

    def add_row(name, qty, price, total):
        pdf.cell(65, 8, name, 1)
        pdf.cell(35, 8, qty, 1)
        pdf.cell(35, 8, format_currency(price), 1)
        pdf.cell(55, 8, format_currency(total), 1, ln=True)

    add_row("Профнастил", f"{sheets_count} лист.", PROFNASTIL_PRICE, sheets_total)
    add_row("Лаги", f"{int(lag_length)} м", LAG_PRICE, lag_total)
    add_row("Стойки", f"{stake_count} шт", STAKE_PRICE, stake_total)
    add_row("Саморезы", "1 пачка", SCREWS_PACK_PRICE, screws_total)
    if has_foundation:
        add_row("Бетон", f"{concrete_m3:.2f} м³", CONCRETE_PRICE_M3, concrete_total)

    pdf.set_font("DejaVu", "B", 10)
    pdf.cell(135, 8, "Итого за материалы:", 1)
    pdf.cell(55, 8, format_currency(total_material), 1, ln=True)

    # Работы
    if length <= 50:
        work_price = 19980 if has_foundation else 13980
    else:
        work_price = 13980 if has_foundation else 9900
    if slope:
        work_price *= 1.1
    work_total = work_price * length

    pdf.ln(5)
    pdf.set_font("DejaVu", "", 11)
    pdf.multi_cell(0, 8, f"💼 Работы под ключ: {format_currency(work_total)}")

    pdf.set_font("DejaVu", "", 10)
    pdf.multi_cell(0, 6, "Что входит в стоимость работ:\n"
                         "- Разметка\n"
                         "- Подготовка и копка траншей\n"
                         "- Подсыпка и трамбовка\n"
                         "- Установка опалубки и помощь по аренде\n"
                         "- Армирование\n"
                         "- Заливка фундамента\n"
                         "- Демонтаж опалубки\n"
                         "- Монтаж стоек и лаг\n"
                         "- Крепление профнастила\n"
                         "- Сварочные работы")

    # Сохраняем PDF
    os.makedirs("output", exist_ok=True)
    filename = f"./output/kp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename
