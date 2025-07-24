import aiosqlite
import os

DB_PATH = "data/game.db"

async def init_db():
    os.makedirs("data", exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                time_left INTEGER DEFAULT 0,
                active INTEGER DEFAULT 1,
                chat_id INTEGER,  -- Добавляем поле для chat_id
                message_id INTEGER  -- Добавляем поле для message_id
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS state (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        await db.commit()

async def add_user(user_id, name, chat_id):  # Добавляем chat_id
    async with aiosqlite.connect(DB_PATH) as db:
        # Проверяем, существует ли активный пользователь с таким именем
        async with db.execute("SELECT user_id FROM users WHERE name = ? AND active = 1", (name,)) as cursor:
            if await cursor.fetchone():
                return False  # Имя уже занято
        default_time = 7200  # 120 минут
        await db.execute("""
            INSERT OR REPLACE INTO users (user_id, name, time_left, active, chat_id, message_id)
            VALUES (?, ?, ?, 1, ?, NULL)
        """, (user_id, name, default_time, chat_id))
        await db.commit()
        return True

async def get_active_users():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id, name, time_left, chat_id, message_id FROM users WHERE active = 1") as cursor:
            return await cursor.fetchall()

async def deactivate_user(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET active = 0 WHERE user_id = ?", (user_id,))
        await db.commit()

async def set_user_time(user_id, seconds):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET time_left = ? WHERE user_id = ?", (seconds, user_id))
        await db.commit()

async def get_user_by_name(name):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM users WHERE name = ? AND active = 1", (name,)) as cursor:
            return await cursor.fetchone()

async def get_user_time(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT time_left FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def update_user_time(user_id, delta):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET time_left = time_left - ? WHERE user_id = ?", (delta, user_id))
        await db.commit()

async def set_game_state(key, value):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO state (key, value) VALUES (?, ?)", (key, value))
        await db.commit()

async def get_game_state(key):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT value FROM state WHERE key = ?", (key,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def delete_user_by_id(user_id):
    """Удаляет пользователя из базы данных по его user_id."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        await db.commit()

async def set_message_id(user_id, message_id):
    """Устанавливает message_id для пользователя."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET message_id = ? WHERE user_id = ?", (message_id, user_id))
        await db.commit()

async def format_active_players():
    users = await get_active_users()
    if not users:
        return "Нет активных участников."
    return "\n".join(
        f"{u[1]}: {u[2]//60:02}:{u[2]%60:02}" for u in users
    )

async def reset_message_ids():
    """Сбрасывает message_id для всех активных пользователей."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET message_id = NULL WHERE active = 1")
        await db.commit()