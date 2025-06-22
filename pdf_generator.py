from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from datetime import datetime
import os

def generate_pdf(data: dict, path: str = "kpsmeta.pdf"):
    """
    data = {
        "fence_type": "Профнастил",
        "length": 40,
        "post_type": "металл",
        "foundation": True,
        "foundation_volume": 6.5,
        "materials": [
            {"name": "Стойки 60×60×2 мм", "count": 14, "price": 3750},
            {"name": "Лаги 40×40×1.5 мм", "count": 120, "price": 800},
            {"name": "Профнастил 2×1.1 м", "count": 20, "price": 14000},
            {"name": "Саморезы", "count": 3, "price": 2000},
            {"name": "Бетон М300", "count": 6.5, "price": 22000},
        ]
    }
    """
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    c.translate(10 * mm, height - 20 * mm)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(0, 0, "ZaborOFF")
    c.setFont("Helvetica", 12)
    c.drawString(0, -10, "Коммерческое предложение")
    c.drawString(0, -25, f"Дата: {datetime.now().strftime('%d.%m.%Y')}")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(0, -45, "\u2022 Информация о заборе")
    c.setFont("Helvetica", 11)
    y = -60
    c.drawString(0, y, f"Тип забора: {data['fence_type']}")
    y -= 15
    c.drawString(0, y, f"Длина: {data['length']} м")
    y -= 15
    c.drawString(0, y, f"Стойки: {data['post_type']}")
    y -= 15
    c.drawString(0, y, f"Фундамент: {'да' if data['foundation'] else 'нет'}")
    if data['foundation']:
        y -= 15
        c.drawString(0, y, f"Объем бетона: {data['foundation_volume']} м³")

    y -= 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(0, y, "\u2022 Расчет по материалам")
    y -= 20

    c.setFont("Helvetica-Bold", 11)
    c.drawString(0, y, "Наименование")
    c.drawString(90 * mm, y, "Кол-во × Цена")
    c.drawString(140 * mm, y, "Сумма")
    c.setFont("Helvetica", 10)
    total = 0

    for m in data['materials']:
        y -= 15
        line = m['name']
        quantity = f"{m['count']} × {int(m['price'])} ₸"
        subtotal = int(m['count'] * m['price'])
        total += subtotal
        c.drawString(0, y, line)
        c.drawString(90 * mm, y, quantity)
        c.drawString(140 * mm, y, f"{subtotal:,} ₸".replace(",", " "))

    y -= 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(0, y, f"ИТОГО: {total:,} ₸".replace(",", " "))

    c.save()
    return path
