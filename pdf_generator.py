from fpdf import FPDF
import os
from datetime import datetime

def format_currency(value):
    try:
        return f"{int(float(value)):,} ₸".replace(",", " ")
    except (ValueError, TypeError):
        return "—"

def safe_get(data, key, default=None):
    return data.get(key, default)

def calculate_screws(sheets_count):
    screws_per_sheet = 4 * 3  # 4 точки × 3 лаги
    total_screws = sheets_count * screws_per_sheet
    packs_needed = max(1, round(total_screws / 150 + 0.49))  # 150 в пачке
    return packs_needed

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()

    # 🖋️ Шрифты
    pdf.add_font('DejaVu', '', './fonts/DejaVuSans.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', './fonts/DejaVuSans-Bold.ttf', uni=True)
    pdf.set_font('DejaVu', '', 11)

    # 🧾 Входные данные
    fence_type = safe_get(data, "fence_type", "Не указано")
    try:
        length = float(safe_get(data, "length", 0) or 0)
    except (ValueError, TypeError):
        length = 0
    has_foundation = safe_get(data, "foundation", False)
    slope = safe_get(data, "slope", False)

    # 🔧 Цены (можно задать в админке)
    profnastil_price = safe_get(data, "profnastil_price", 2300)
    lag_price = safe_get(data, "lag_price", 800)
    stake_price = safe_get(data, "stake_price", 1500 * 2.5)
    screw_pack_price = safe_get(data, "screw_pack_price", 2000)
    concrete_price = safe_get(data, "concrete_price", 22000)

    # 📍 Расчёты
    profile_width = 1.1
    sheets_count = int(length / profile_width + 0.5)
    sheets_total = sheets_count * profnastil_price

    lag_length = length * 3
    lag_total = lag_length * lag_price

    stake_count = int(length / 3) + 1
    stake_total = stake_count * stake_price

    screw_packs = calculate_screws(sheets_count)
    screws_total = screw_packs * screw_pack_price

    concrete_m3 = length * 0.3 * 0.2 if has_foundation else 0
    concrete_total = concrete_m3 * concrete_price

    total_material = sheets_total + lag_total + stake_total + screws_total + concrete_total

    # 👤 Адрес и номер КП
    address = safe_get(data, "address", "Zaboroff.kz\nСамал-2, ул. Бектурова, д. 77а\nг. Алматы, Казахстан\n+77022319176")
    offer_number = datetime.now().strftime("%Y%m%d-%H%M")

    # 🖼 Логотип
    logo_path = "./logo.png"
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=150, y=10, w=40)
    pdf.set_font('DejaVu', 'B', 11)
    pdf.cell(200, 10, txt="Коммерческое предложение", ln=True, align="C")
    pdf.set_font('DejaVu', '', 10)
    pdf.cell(200, 10, txt=f"Номер предложения: {offer_number}", ln=True, align="C")
    pdf.ln(8)

    # 📋 Параметры
    pdf.set_font('DejaVu', '', 11)
    pdf.cell(200, 10, f"Тип забора: {fence_type}", ln=True)
    pdf.cell(200, 10, f"Длина: {length} м", ln=True)
    pdf.cell(200, 10, f"Фундамент: {'Да' if has_foundation else 'Нет'}", ln=True)
    pdf.cell(200, 10, f"Уклон: {'Да' if slope else 'Нет'}", ln=True)
    pdf.ln(5)

    # 📊 Таблица
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('DejaVu', 'B', 11)
    pdf.cell(60, 10, "Материал", 1, 0, 'C', True)
    pdf.cell(40, 10, "Расход", 1, 0, 'C', True)
    pdf.cell(40, 10, "Цена за ед.", 1, 0, 'C', True)
    pdf.cell(50, 10, "Сумма", 1, 1, 'C', True)
    pdf.set_font('DejaVu', '', 11)

    rows = [
        ("Профнастил", f"{sheets_count} лист.", profnastil_price, sheets_total),
        ("Лаги", f"{int(lag_length)} м", lag_price, lag_total),
        ("Стойки", f"{stake_count} шт", stake_price, stake_total),
        ("Саморезы", f"{screw_packs} пач.", screw_pack_price, screws_total)
    ]
    if has_foundation:
        rows.append(("Бетон", f"{concrete_m3:.2f} м³", concrete_price, concrete_total))

    for name, qty, unit_price, total in rows:
        pdf.cell(60, 10, name, 1)
        pdf.cell(40, 10, qty, 1)
        pdf.cell(40, 10, format_currency(unit_price), 1)
        pdf.cell(50, 10, format_currency(total), 1)
        pdf.ln(10)

    # 🔢 Итого
    pdf.set_font('DejaVu', 'B', 11)
    pdf.cell(140, 10, "Итого за материалы:", 1)
    pdf.cell(50, 10, format_currency(total_material), 1, ln=True)

    # 💼 Монтаж
    pdf.set_font('DejaVu', '', 11)
    if length <= 50:
        work_price = 19980 if has_foundation else 13980
    else:
        work_price = 13980 if has_foundation else 9900
    if slope:
        work_price *= 1.1
    work_total = work_price * length

    pdf.ln(5)
    pdf.multi_cell(0, 8, f"💼 Работы под ключ: {format_currency(work_total)}")

    pdf.set_font('DejaVu', size=9)
    lines = [
        "Что входит в стоимость работ:",
        "- Разметка", "- Подготовка и копка траншей", "- Подсыпка и трамбовка",
        "- Установка опалубки и помощь по аренде", "- Армирование", "- Заливка фундамента",
        "- Демонтаж опалубки", "- Монтаж стоек и лаг", "- Крепление профнастила", "- Сварочные работы"
    ]
    for line in lines:
        pdf.multi_cell(0, 6, line)

    # 📍 Адрес
    pdf.ln(4)
    pdf.set_font('DejaVu', '', 9)
    for line in address.split("\n"):
        pdf.cell(0, 7, line.strip(), ln=True)

    # 💾 Сохраняем
    os.makedirs("output", exist_ok=True)
    filename = f"./output/kp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename
