from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import ReplyKeyboardRemove
from aiogram.types import InputFile
from keyboards.reply import get_main_keyboard
from utils.calculations import calculate_total, generate_pdf

# Шаг для добавления логотипа и контактов
async def step_add_logo_and_contacts(message: types.Message, state: FSMContext):
    # Запрос на логотип
    await message.answer("Загрузите ваш логотип (если есть):", reply_markup=ReplyKeyboardRemove())
    await state.set_state("waiting_for_logo")

# Обработка загрузки логотипа
async def process_logo(message: types.Message, state: FSMContext):
    if message.photo:
        # Сохраняем логотип
        logo_file = await message.photo[-1].download(destination_file=f"logos/{message.from_user.id}_logo.jpg")
        # Сохраняем данные о логотипе в FSM
        await state.update_data(logo=logo_file.name)
        await message.answer("Теперь добавьте ваш адрес и телефон для сметы:", reply_markup=ReplyKeyboardRemove())
        await state.set_state("waiting_for_contact_details")
    else:
        await message.answer("Пожалуйста, отправьте изображение логотипа.")

# Обработка контактов (адрес и телефон)
async def process_contact_details(message: types.Message, state: FSMContext):
    contact_data = message.text.split("\n")
    if len(contact_data) == 2:
        address, phone = contact_data
        await state.update_data(address=address, phone=phone)
        await message.answer("Контакты добавлены успешно. Нажмите /finish для завершения.", reply_markup=get_main_keyboard())
        await state.set_state("waiting_for_finish")
    else:
        await message.answer("Пожалуйста, введите данные в следующем формате:\nАдрес\nТелефон")
