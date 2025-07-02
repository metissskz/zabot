from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile
from datetime import datetime, timedelta

router = Router()

# Простая in-memory "БД" пользователей (в будущем заменить на PostgreSQL)
USERS = {}  # user_id: {"trial_until": datetime, "access": bool, "is_admin": bool}

ADMIN_IDS = [77022319176]  # Добавь сюда свой Telegram user_id

TRIAL_DAYS = 1
PRICE_PER_KP = 200  # тенге

# Команда /pay
@router.message(Command("pay"))
async def pay_start(message: Message):
    user_id = message.from_user.id
    now = datetime.now()
    user_data = USERS.get(user_id)

    if user_data and user_data.get("access"):
        await message.answer("✅ У вас уже есть активный доступ.")
    else:
        USERS[user_id] = {
            "trial_until": now + timedelta(days=TRIAL_DAYS),
            "access": True,
            "is_admin": user_id in ADMIN_IDS
        }
        await message.answer(f"🆓 Вам выдан тестовый доступ на {TRIAL_DAYS} день.\n
После окончания вы сможете оплатить доступ, отправив чек.")

        await message.answer("💳 Для оплаты доступа переведите 200 ₸ на Kaspi:", reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="Отправить чек", callback_data="send_receipt")]
            ]
        ))

# Обработка отправки чека (фото)
@router.message(F.photo)
async def handle_receipt(message: Message):
    user_id = message.from_user.id
    USERS.setdefault(user_id, {})  # если нет данных, создать пустую

    # Пересылаем фото админу
    for admin_id in ADMIN_IDS:
        await message.bot.send_message(admin_id, f"📥 Новый чек от пользователя {user_id}")
        await message.bot.send_photo(admin_id, photo=message.photo[-1].file_id, caption=f"/approve_{user_id} /deny_{user_id}")

    await message.answer("🕐 Чек отправлен на проверку. Ожидайте подтверждения.")

# Обработка подтверждения оплаты (только админ)
@router.message(F.text.startswith("/approve_"))
async def approve_payment(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    try:
        target_id = int(message.text.split("_")[1])
        USERS.setdefault(target_id, {})
        USERS[target_id]["access"] = True
        USERS[target_id]["trial_until"] = datetime.now() + timedelta(days=30)
        await message.answer(f"✅ Доступ пользователю {target_id} выдан на 30 дней.")
        await message.bot.send_message(target_id, "✅ Ваш платный доступ активирован на 30 дней. Спасибо!")
    except Exception as e:
        await message.answer(f"Ошибка при активации: {e}")

# Обработка отклонения
@router.message(F.text.startswith("/deny_"))
async def deny_payment(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    try:
        target_id = int(message.text.split("_")[1])
        await message.bot.send_message(target_id, "❌ Ваш чек был отклонён. Пожалуйста, проверьте данные и отправьте снова.")
        await message.answer("🚫 Пользователь уведомлён об отказе.")
    except Exception as e:
        await message.answer(f"Ошибка при отказе: {e}")

# Пример проверки доступа
async def has_access(user_id: int) -> bool:
    user = USERS.get(user_id)
    if not user:
        return False
    if user.get("access") and user.get("trial_until", datetime.min) >= datetime.now():
        return True
    return False
