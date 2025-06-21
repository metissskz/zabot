from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Рассчитать забор")]
    ],
    resize_keyboard=True
)

fence_type_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Профнастил"), KeyboardButton(text="Сетка")],
        [KeyboardButton(text="Блок")],
    ],
    resize_keyboard=True
)
