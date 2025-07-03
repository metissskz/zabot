import asyncpg
import os
from datetime import datetime, timedelta

DB_URL = os.getenv("DATABASE_URL")  # Пример: postgres://user:pass@host:port/db

class UserDB:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(dsn=DB_URL)

    async def init_table(self):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    trial_until TIMESTAMP,
                    subscription_until TIMESTAMP,
                    credits INTEGER DEFAULT 0
                );
            """)

    async def get_or_create_user(self, user_id: int):
        async with self.pool.acquire() as conn:
            user = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
            if user:
                return user
            trial_days = 7
            now = datetime.utcnow()
            trial_end = now + timedelta(days=trial_days)
            await conn.execute("""
                INSERT INTO users (user_id, trial_until, credits) VALUES ($1, $2, $3)
            """, user_id, trial_end, 0)
            return await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)

    async def has_access(self, user_id: int):
        user = await self.get_or_create_user(user_id)
        now = datetime.utcnow()
        return (user["subscription_until"] and user["subscription_until"] > now) or \
               (user["trial_until"] and user["trial_until"] > now) or \
               (user["credits"] > 0)

    async def use_credit(self, user_id: int):
        async with self.pool.acquire() as conn:
            await conn.execute("UPDATE users SET credits = credits - 1 WHERE user_id = $1 AND credits > 0", user_id)

    async def add_credits(self, user_id: int, count: int):
        async with self.pool.acquire() as conn:
            await conn.execute("UPDATE users SET credits = credits + $1 WHERE user_id = $2", count, user_id)

    async def activate_subscription(self, user_id: int, days: int = 30):
        async with self.pool.acquire() as conn:
            now = datetime.utcnow()
            await conn.execute("""
                UPDATE users
                SET subscription_until = $1
                WHERE user_id = $2
            """, now + timedelta(days=days), user_id)

    async def get_status_text(self, user_id: int):
        user = await self.get_or_create_user(user_id)
        now = datetime.utcnow()
        if user["subscription_until"] and user["subscription_until"] > now:
            left = (user["subscription_until"] - now).days
            return f"🟢 Подписка активна ещё {left} дн."
        elif user["trial_until"] and user["trial_until"] > now:
            left = (user["trial_until"] - now).days
            return f"🟢 Триал: осталось {left} дн."
        elif user["credits"] > 0:
            return f"🟡 Осталось смет: {user['credits']}"
        return "🔴 Доступ ограничен. Оплатите подписку или купите смету."
