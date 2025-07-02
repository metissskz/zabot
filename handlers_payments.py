# handlers_payments.py
from aiogram import Router, F, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from db import add_pending_payment, get_pending_payments, confirm_payment, reject_payment

router = Router()

ADMINS = [77022319176]  # Замени на свой Telegram ID

@router.message(F.text == "💰 Пополнить баланс")
async def pay_by_qr(message: types.Message):
    await message.answer_photo(
        photo="https://example.com/kaspi_qr.png",  # Заменить на свой QR
        caption=(
            "📲 Отсканируйте QR в Kaspi и отправьте чек.

"
            "💵 Стоимость 1 КП: *200 ₸*
"
            "После оплаты напишите: `Оплатил 200` или отправьте фото чека."
        ),
        parse_mode="Markdown"
    )

@router.message(F.text.startswith("Оплатил"))
async def save_payment_request(message: types.Message):
    amount_str = message.text.replace("Оплатил", "").strip()
    try:
        amount = int(amount_str)
        await add_pending_payment(message.from_user.id, amount, None)
        await message.answer("✅ Заявка принята. Ожидайте подтверждения админом.")
    except:
        await message.answer("❌ Не удалось распознать сумму. Укажите число, например: `Оплатил 200`.")

@router.message(F.photo)
async def save_payment_photo(message: types.Message):
    file_id = message.photo[-1].file_id
    await add_pending_payment(message.from_user.id, 200, file_id)
    await message.answer("✅ Фото чека получено. Ожидайте подтверждения.")

@router.message(F.text == "/платежи")
async def list_payments(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    payments = await get_pending_payments()
    if not payments:
        await message.answer("📬 Нет заявок.")
        return
    for p in payments:
        text = f"📏 Заявка #{p['id']}\n👤 {p['telegram_id']}\n💸 {p['amount']} ₸\n⏰ {p['created_at']}"
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=f"✅ Подтвердить {p['id']}")],
                [KeyboardButton(text=f"❌ Отклонить {p['id']}")]
            ],
            resize_keyboard=True
        )
        await message.answer(text, reply_markup=markup)

@router.message(F.text.startswith("\u2705 \u041f\u043e\u0434\u0442\u0432\u0435\u0440\u0434\u0438\u0442\u044c"))
async def confirm_payment_cmd(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    pid = int(message.text.split()[-1])
    await confirm_payment(pid)
    await message.answer("\u2705 \u041f\u043e\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u0435 \u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u043e.")

@router.message(F.text.startswith("\u274c \u041e\u0442\u043a\u043b\u043e\u043d\u0438\u0442\u044c"))
async def reject_payment_cmd(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    pid = int(message.text.split()[-1])
    await reject_payment(pid)
    await message.answer("\u274c \u0417\u0430\u044f\u0432\u043a\u0430 \u043e\u0442\u043a\u043b\u043e\u043d\u0435\u043d\u0430.")
