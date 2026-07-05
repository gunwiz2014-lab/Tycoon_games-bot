import os
import time
import aiosqlite

import config

# DB_PATH можно переопределить через переменную окружения, чтобы хранить базу
# на постоянном Railway Volume (иначе при каждом деплое прогресс будет стираться)
DB_PATH = os.getenv("DB_PATH", "game.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    coins INTEGER NOT NULL DEFAULT 0,
    gems INTEGER NOT NULL DEFAULT 0,
    lemons INTEGER NOT NULL DEFAULT 0,
    ore INTEGER NOT NULL DEFAULT 0,
    farm_level INTEGER NOT NULL DEFAULT 1,
    farm_workers INTEGER NOT NULL DEFAULT 0,
    miner_level INTEGER NOT NULL DEFAULT 1,
    auto_miners INTEGER NOT NULL DEFAULT 0,
    energy INTEGER NOT NULL DEFAULT 50,
    max_energy INTEGER NOT NULL DEFAULT 50,
    boost_until INTEGER NOT NULL DEFAULT 0,
    last_farm_collect INTEGER NOT NULL DEFAULT 0,
    last_mine_collect INTEGER NOT NULL DEFAULT 0,
    last_energy_tick INTEGER NOT NULL DEFAULT 0,
    created_at INTEGER NOT NULL DEFAULT 0,
    space_level INTEGER NOT NULL DEFAULT 1,
    space_crew INTEGER NOT NULL DEFAULT 0,
    stardust INTEGER NOT NULL DEFAULT 0,
    last_space_collect INTEGER NOT NULL DEFAULT 0,
    daily_streak INTEGER NOT NULL DEFAULT 0,
    last_daily_claim INTEGER NOT NULL DEFAULT 0,
    boss_id TEXT NOT NULL DEFAULT '',
    boss_hp INTEGER NOT NULL DEFAULT 0,
    boss_date TEXT NOT NULL DEFAULT '',
    trade_level INTEGER NOT NULL DEFAULT 0,
    trade_outlets INTEGER NOT NULL DEFAULT 0,
    last_trade_collect INTEGER NOT NULL DEFAULT 0,
    lifetime_lemons INTEGER NOT NULL DEFAULT 0,
    lifetime_ore INTEGER NOT NULL DEFAULT 0,
    lifetime_dust INTEGER NOT NULL DEFAULT 0,
    boss_kills INTEGER NOT NULL DEFAULT 0,
    quests_claimed TEXT NOT NULL DEFAULT '',
    vip INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    item_id TEXT NOT NULL,
    currency TEXT NOT NULL,
    amount INTEGER NOT NULL,
    created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS group_members (
    chat_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    username TEXT,
    joined_at INTEGER NOT NULL,
    PRIMARY KEY (chat_id, user_id)
);

CREATE TABLE IF NOT EXISTS user_groups (
    user_id INTEGER PRIMARY KEY,
    in_group_count INTEGER NOT NULL DEFAULT 0
);
"""


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA)
        await db.commit()


async def get_or_create_user(user_id: int, username: str | None) -> dict:
    now = int(time.time())
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        if row:
            return dict(row)

        await db.execute(
            """INSERT INTO users
               (user_id, username, coins, gems, energy, max_energy,
                last_farm_collect, last_mine_collect, last_energy_tick, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id, username, config.STARTING_COINS, config.STARTING_GEMS,
                config.MAX_ENERGY_BASE, config.MAX_ENERGY_BASE,
                now, now, now, now,
            ),
        )
        await db.commit()
        cur = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        return dict(row)


async def update_user(user_id: int, **fields):
    if not fields:
        return
    keys = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [user_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE users SET {keys} WHERE user_id = ?", values)
        await db.commit()


async def log_purchase(user_id: int, item_id: str, currency: str, amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO purchases (user_id, item_id, currency, amount, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, item_id, currency, amount, int(time.time())),
        )
        await db.commit()


async def get_user(user_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def register_group_member(chat_id: int, user_id: int, username: str | None):
    now = int(time.time())
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO group_members (chat_id, user_id, username, joined_at)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(chat_id, user_id) DO UPDATE SET username = excluded.username""",
            (chat_id, user_id, username, now),
        )
        await db.execute(
            """INSERT INTO user_groups (user_id, in_group_count) VALUES (?, 1)
               ON CONFLICT(user_id) DO UPDATE SET in_group_count = in_group_count + 1""",
            (user_id,),
        )
        await db.commit()


async def is_user_in_any_group(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT in_group_count FROM user_groups WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        return bool(row and row[0] > 0)


async def get_group_leaderboard(chat_id: int, limit: int = 10) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            """SELECT u.username, u.coins, u.gems
               FROM group_members gm
               JOIN users u ON u.user_id = gm.user_id
               WHERE gm.chat_id = ?
               ORDER BY u.coins DESC
               LIMIT ?""",
            (chat_id, limit),
        )
        rows = await cur.fetchall()
        return [dict(r) for r in rows]
