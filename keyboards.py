from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, WebAppInfo,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

import config


def main_menu(webapp_url: str) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="🍋 Ферма"), KeyboardButton(text="⛏ Майнинг")],
        [KeyboardButton(text="🚀 Космос"), KeyboardButton(text="🏪 Лавочка")],
        [KeyboardButton(text="👹 Босс"), KeyboardButton(text="📜 Квесты")],
        [KeyboardButton(text="🎁 Дейли"), KeyboardButton(text="🛒 Магазин")],
        [KeyboardButton(text="👤 Профиль")],
    ]
    if webapp_url:
        rows.append([KeyboardButton(text="📱 Магазин и поддержка", web_app=WebAppInfo(url=webapp_url))])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def add_to_group_inline(bot_username: str) -> InlineKeyboardMarkup | None:
    if not bot_username:
        return None
    url = f"https://t.me/{bot_username}?startgroup=true"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить бота в группу (+15% к добыче)", url=url)]
    ])


def farm_menu(user: dict) -> InlineKeyboardMarkup:
    level = user["farm_level"]
    rows = [
        [InlineKeyboardButton(text="👆 Тапнуть (+1 🍋)", callback_data="farm_tap")],
        [InlineKeyboardButton(text="🌾 Собрать лимоны", callback_data="farm_collect")],
    ]
    if level < config.FARM_MAX_LEVEL:
        cost = config.FARM_LEVELS[level + 1]["upgrade_cost"]
        rows.append([InlineKeyboardButton(text=f"⬆️ Улучшить завод ({cost} монет)", callback_data="farm_upgrade")])
    if user["farm_workers"] < config.FARM_MAX_WORKERS:
        from game_logic import farm_worker_cost
        cost = farm_worker_cost(user["farm_workers"])
        rows.append([InlineKeyboardButton(text=f"👷 Нанять рабочего ({cost} монет)", callback_data="farm_hire")])
    rows.append([InlineKeyboardButton(text="💰 Продать все лимоны", callback_data="farm_sell")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def mining_menu(user: dict) -> InlineKeyboardMarkup:
    level = user["miner_level"]
    rows = [
        [InlineKeyboardButton(text="⛏ Копать (1 клик)", callback_data="mine_click")],
        [InlineKeyboardButton(text="📦 Забрать с авто-майнеров", callback_data="mine_collect_auto")],
    ]
    if level < config.MINER_MAX_LEVEL:
        cost = config.MINER_LEVELS[level + 1]["upgrade_cost"]
        rows.append([InlineKeyboardButton(text=f"⬆️ Улучшить кирку ({cost} монет)", callback_data="mine_upgrade")])
    rows.append([InlineKeyboardButton(text="💰 Продать всю руду", callback_data="mine_sell")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def space_menu(user: dict) -> InlineKeyboardMarkup:
    level = user["space_level"]
    rows = [[InlineKeyboardButton(text="✨ Собрать звёздную пыль", callback_data="space_collect")]]
    if level < config.SPACE_MAX_LEVEL:
        cost = config.SPACE_LEVELS[level + 1]["upgrade_cost"]
        rows.append([InlineKeyboardButton(text=f"⬆️ Улучшить станцию ({cost} монет)", callback_data="space_upgrade")])
    if user["space_crew"] < config.SPACE_MAX_CREW:
        from game_logic import space_crew_cost
        cost = space_crew_cost(user["space_crew"])
        rows.append([InlineKeyboardButton(text=f"👨‍🚀 Нанять астронавта ({cost} монет)", callback_data="space_hire")])
    rows.append([InlineKeyboardButton(text="💰 Продать всю пыль", callback_data="space_sell")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def boss_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚔️ Атаковать", callback_data="boss_hit")]
    ])


def daily_menu(claimed_today: bool) -> InlineKeyboardMarkup:
    if claimed_today:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Уже забрал сегодня", callback_data="daily_noop")]
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Забрать награду", callback_data="daily_claim")]
    ])


def shop_menu() -> InlineKeyboardMarkup:
    rows = []
    for item in config.SHOP_COIN_ITEMS:
        rows.append([InlineKeyboardButton(text=f"{item['title']} — {item['price']}🪙", callback_data=f"buy_coin_{item['id']}")])
    for item in config.SHOP_GEM_ITEMS:
        rows.append([InlineKeyboardButton(text=f"{item['title']} — {item['price']}💎", callback_data=f"buy_gem_{item['id']}")])
    rows.append([InlineKeyboardButton(text="⭐ Купить гемы за Telegram Stars", callback_data="open_star_shop")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def star_shop_menu() -> InlineKeyboardMarkup:
    rows = []
    for pack in config.STAR_GEM_PACKS:
        rows.append([InlineKeyboardButton(text=f"{pack['title']} — {pack['stars']}⭐", callback_data=f"buy_stars_{pack['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def trade_menu(user: dict) -> InlineKeyboardMarkup:
    level = user["trade_level"]
    rows = []
    if level < 1:
        rows.append([InlineKeyboardButton(text="🏪 Открыть лавочку (бесплатно)", callback_data="trade_upgrade")])
        return InlineKeyboardMarkup(inline_keyboard=rows)

    rows.append([InlineKeyboardButton(text="💰 Собрать выручку", callback_data="trade_collect")])
    if level < config.TRADE_MAX_LEVEL:
        cost = config.TRADE_LEVELS[level + 1]["upgrade_cost"]
        rows.append([InlineKeyboardButton(text=f"⬆️ Улучшить лавочку ({cost} монет)", callback_data="trade_upgrade")])
    if user["trade_outlets"] < config.TRADE_MAX_OUTLETS:
        from game_logic import trade_outlet_cost
        cost = trade_outlet_cost(user["trade_outlets"])
        rows.append([InlineKeyboardButton(text=f"🏬 Арендовать точку ({cost} монет)", callback_data="trade_hire")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def quests_menu(quests: list) -> InlineKeyboardMarkup:
    rows = []
    for q in quests:
        if q["claimed"]:
            continue
        label = f"🎁 Забрать: {q['title']}" if q["done"] else f"🔒 {q['title']} ({q['progress']}/{q['target']})"
        rows.append([InlineKeyboardButton(
            text=label,
            callback_data=f"quest_claim_{q['id']}" if q["done"] else "quest_locked",
        )])
    if not rows:
        rows.append([InlineKeyboardButton(text="✅ Все квесты выполнены!", callback_data="quest_locked")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
