from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from datetime import datetime

# Подключаем шрифт (должен лежать рядом в проекте)
pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))

def generate_pdf(data: dict, path: str = "kpsmeta.pdf"):
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    c.translate(10 * mm, height - 20 * mm)

    # Заголовок
    c.setFont("DejaVu", 18)
    c.drawString(0, 0, "ZaborOFF")
    c.setFont("DejaVu", 12)
    c.drawString(0, -10, "Коммерческое предложение")
    c.drawString(0, -25, f"Дата: {datetime.now().strftime('%d.%m.%Y')}")

    # Общие данные
    c.setFont("DejaVu", 12)
    c.drawString(0, -45, "• Информация о заборе")
    y = -60
    c.setFont("DejaVu", 11)
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

    # Материалы
    y -= 30
    c.setFont("DejaVu", 12)
    c.drawString(0, y, "• Расчет по материалам")
    y -= 20

    c.setFont("DejaVu", 11)
    c.drawString(0, y, "Наименование")
    c.drawString(90 * mm, y, "Кол-во × Цена")
    c.drawString(140 * mm, y, "Сумма")
    total = 0
    y -= 15
    c.setFont("DejaVu", 10)
    for m in data['materials']:
        name = m['name']
        quantity = f"{m['count']} × {int(m['price'])} ₸"
        subtotal = int(m['count'] * m['price'])
        total += subtotal
        c.drawString(0, y, name)
        c.drawString(90 * mm, y, quantity)
        c.drawString(140 * mm, y, f"{subtotal:,} ₸".replace(",", " "))
        y -= 15

    # Итого
    y -= 15
    c.setFont("DejaVu", 12)
    c.drawString(0, y, f"ИТОГО: {total:,} ₸".replace(",", " "))

    c.save()
    return path
