import asyncpg

async def get_user_settings(user_id):
    conn = await asyncpg.connect(...)
    row = await conn.fetchrow("SELECT * FROM user_settings WHERE user_id = $1", user_id)
    if not row:
        await conn.execute("INSERT INTO user_settings (user_id) VALUES ($1)", user_id)
        row = await conn.fetchrow("SELECT * FROM user_settings WHERE user_id = $1", user_id)
    await conn.close()
    return dict(row)

async def update_user_setting(user_id, key, value):
    conn = await asyncpg.connect(...)
    await conn.execute(f"UPDATE user_settings SET {key} = $1 WHERE user_id = $2", value, user_id)
    await conn.close()

async def reset_user_settings(user_id):
    conn = await asyncpg.connect(...)
    await conn.execute("DELETE FROM user_settings WHERE user_id = $1", user_id)
    await conn.execute("INSERT INTO user_settings (user_id) VALUES ($1)", user_id)
    await conn.close()
