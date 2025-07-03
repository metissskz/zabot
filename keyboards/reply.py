from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Кнопки для логотипа и контактных данных
def get_logo_and_contacts_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button_logo = KeyboardButton("Загрузить логотип")
    button_contacts = KeyboardButton("Добавить адрес и телефон")
    keyboard.add(button_logo, button_contacts)
    return keyboard
