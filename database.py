import time
import aiosqlite

import config

DB_PATH = "game.db"

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
    created_at INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    item_id TEXT NOT NULL,
    currency TEXT NOT NULL,
    amount INTEGER NOT NULL,
    created_at INTEGER NOT NULL
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
