import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

# Подключение к PostgreSQL через переменную окружения
DATABASE_URL = os.getenv("DATABASE_URL")


# 📥 Получение всех настроек пользователя
async def get_user_settings(user_id: int) -> dict:
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow("SELECT * FROM user_settings WHERE user_id = $1", user_id)

    # Если пользователь не найден — создаём с дефолтными настройками
    if not row:
        await conn.execute("INSERT INTO user_settings (user_id) VALUES ($1)", user_id)
        row = await conn.fetchrow("SELECT * FROM user_settings WHERE user_id = $1", user_id)

    await conn.close()
    return dict(row)


# ✏️ Обновление одного параметра
async def update_user_setting(user_id: int, key: str, value):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute(f"UPDATE user_settings SET {key} = $1 WHERE user_id = $2", value, user_id)
    await conn.close()


# 🔁 Сброс настроек до значений по умолчанию
async def reset_user_settings(user_id: int):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("DELETE FROM user_settings WHERE user_id = $1", user_id)
    await conn.execute("INSERT INTO user_settings (user_id) VALUES ($1)", user_id)
    await conn.close()
