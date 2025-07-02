from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from states.settings import SettingsFSM
from db import get_user_settings, update_user_setting, reset_user_settings
from handlers import main_menu  # 🔄 Импорт вынесен наверх

router = Router()

# 📋 Меню настроек
settings_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✏️ Изменить цены"), KeyboardButton(text="🏠 Изменить адрес")],
        [KeyboardButton(text="🖼 Загрузить логотип"), KeyboardButton(text="♻️ Сбросить настройки")],
        [KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True
)

# 🚪 Вход в настройки
@router.message(F.text == "📦 Мои настройки")
async def settings_start(message: types.Message, state: FSMContext):
    await state.set_state(SettingsFSM.choosing_option)
    await message.answer("🔧 Что вы хотите настроить?", reply_markup=settings_menu)

# ✏️ Изменение цен
@router.message(SettingsFSM.choosing_option, F.text == "✏️ Изменить цены")
async def ask_prices(message: types.Message, state: FSMContext):
    await state.set_state(SettingsFSM.updating_price)
    await message.answer(
        "Введите новые цены через запятую:\n`профнастил, лаги, стойки, саморезы, бетон`\n\nПример:\n`2300, 800, 3750, 2000, 22000`",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(SettingsFSM.updating_price)
async def save_prices(message: types.Message, state: FSMContext):
    try:
        values = list(map(int, message.text.replace(" ", "").split(",")))
        if len(values) != 5:
            raise ValueError
        keys = ["profnastil_price", "lag_price", "stake_price", "screw_pack_price", "concrete_price"]
        for k, v in zip(keys, values):
            await update_user_setting(message.from_user.id, k, v)
        await message.answer("✅ Цены обновлены", reply_markup=settings_menu)
        await state.set_state(SettingsFSM.choosing_option)
    except Exception:
        await message.answer("⚠️ Неверный формат. Попробуйте ещё раз.")

# 🏠 Адрес
@router.message(SettingsFSM.choosing_option, F.text == "🏠 Изменить адрес")
async def ask_address(message: types.Message, state: FSMContext):
    await message.answer("Введите новый адрес и контактные данные:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(SettingsFSM.updating_address)

@router.message(SettingsFSM.updating_address)
async def save_address(message: types.Message, state: FSMContext):
    await update_user_setting(message.from_user.id, "address", message.text)
    await message.answer("✅ Адрес обновлён", reply_markup=settings_menu)
    await state.set_state(SettingsFSM.choosing_option)

# 🖼 Логотип
@router.message(SettingsFSM.choosing_option, F.text == "🖼 Загрузить логотип")
async def ask_logo(message: types.Message, state: FSMContext):
    await message.answer("📤 Отправьте изображение логотипа (JPG/PNG):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(SettingsFSM.uploading_logo)

@router.message(SettingsFSM.uploading_logo, F.photo)
async def save_logo(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await update_user_setting(message.from_user.id, "logo_file_id", file_id)
    await message.answer("✅ Логотип сохранён", reply_markup=settings_menu)
    await state.set_state(SettingsFSM.choosing_option)

# ♻️ Сброс
@router.message(SettingsFSM.choosing_option, F.text == "♻️ Сбросить настройки")
async def reset_settings(message: types.Message, state: FSMContext):
    await reset_user_settings(message.from_user.id)
    await message.answer("🔁 Настройки сброшены по умолчанию", reply_markup=settings_menu)

# 🔙 Назад
@router.message(SettingsFSM.choosing_option, F.text == "🔙 Назад")
async def back_to_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("🔙 Главное меню:", reply_markup=main_menu)
