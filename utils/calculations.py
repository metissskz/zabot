from fpdf import FPDF
import os

def generate_pdf(user_data):
    pdf = FPDF()
    pdf.add_page()
    
    # Логотип
    if "logo" in user_data:
        pdf.image(f"logos/{user_data['logo']}", x=10, y=10, w=50)
    
    pdf.set_font("Arial", size=12)
    
    # Контактные данные
    pdf.ln(60)  # Отступ от логотипа
    pdf.cell(200, 10, txt=f"Адрес: {user_data.get('address', 'Не указан')}", ln=True)
    pdf.cell(200, 10, txt=f"Телефон: {user_data.get('phone', 'Не указан')}", ln=True)

    # Другие данные из расчёта
    pdf.ln(20)
    pdf.cell(200, 10, txt=f"Стоимость: {user_data.get('total_cost', 'Не рассчитано')}")

    # Сохранить PDF
    pdf_output = f"output/{user_data['user_id']}_smeta.pdf"
    pdf.output(pdf_output)
    
    return pdf_output
