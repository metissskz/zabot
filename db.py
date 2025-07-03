# db.py
from datetime import datetime, timedelta
import asyncpg

class Database:
    def __init__(self, dsn):
        self.dsn = dsn
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(dsn=self.dsn)

    async def close(self):
        await self.pool.close()

    async def get_or_create_user(self, telegram_id):
        async with self.pool.acquire() as conn:
            user = await conn.fetchrow("""
                SELECT * FROM users WHERE telegram_id = $1
            """, telegram_id)
            if user:
                return user

            trial_end = datetime.utcnow() + timedelta(days=7)
            await conn.execute("""
                INSERT INTO users (telegram_id, trial_ends_at, is_subscribed, balance, created_at)
                VALUES ($1, $2, false, 0, now())
            """, telegram_id, trial_end)
            return await conn.fetchrow("SELECT * FROM users WHERE telegram_id = $1", telegram_id)

    async def is_trial_active(self, telegram_id):
        async with self.pool.acquire() as conn:
            result = await conn.fetchval("""
                SELECT trial_ends_at > now() FROM users WHERE telegram_id = $1
            """, telegram_id)
            return result

    async def get_user(self, telegram_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("SELECT * FROM users WHERE telegram_id = $1", telegram_id)

    async def decrement_balance(self, telegram_id, amount):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE users SET balance = balance - $2 WHERE telegram_id = $1
            """, telegram_id, amount)

    async def set_subscribed(self, telegram_id, status: bool):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE users SET is_subscribed = $2 WHERE telegram_id = $1
            """, telegram_id, status)
