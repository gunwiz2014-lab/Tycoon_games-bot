from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, WebAppInfo,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

import config


def main_menu(webapp_url: str) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="🍋 Ферма"), KeyboardButton(text="⛏ Майнинг")],
        [KeyboardButton(text="🛒 Магазин"), KeyboardButton(text="👤 Профиль")],
    ]
    if webapp_url:
        rows.append([KeyboardButton(text="📱 Открыть мини-приложение", web_app=WebAppInfo(url=webapp_url))])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def farm_menu(user: dict) -> InlineKeyboardMarkup:
    level = user["farm_level"]
    rows = [
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
