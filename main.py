import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeAllGroupChats
from aiohttp import web

import config
import database as db
from handlers import get_root_router
from webapi import build_app

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("lemon-tycoon-bot")


PRIVATE_COMMANDS = [
    BotCommand(command="start", description="🎮 Меню"),
    BotCommand(command="miniguide", description="📕 Мини-гайд"),
    BotCommand(command="promo", description="🎁 Активные промокоды"),
    BotCommand(command="prof", description="👤 Профиль"),
    BotCommand(command="shop", description="🛍 Магазин"),
    BotCommand(command="mine", description="⛏ Добывать руду"),
    BotCommand(command="lemon", description="🍋 Ферма (второй тайкон)"),
    BotCommand(command="space", description="🚀 Космос (третий тайкон)"),
    BotCommand(command="top", description="⭐ Топы"),
    BotCommand(command="clan", description="🏰 Кланы"),
    BotCommand(command="bosses", description="⚔ Боссы"),
    BotCommand(command="exped", description="⛺ Экспедиции"),
    BotCommand(command="inv", description="🎒 Инвентарь"),
    BotCommand(command="bal", description="💵 Баланс"),
    BotCommand(command="stars", description="⭐ Звёзды"),
    BotCommand(command="lvl", description="🌟 Уровень"),
    BotCommand(command="power", description="🔥 Мощность кирки"),
    BotCommand(command="cases", description="📦 Кейсы"),
    BotCommand(command="boosts", description="⚡ Бустеры"),
    BotCommand(command="collections", description="🎎 Коллекции"),
    BotCommand(command="mats", description="🎨 Материалы"),
    BotCommand(command="items", description="🧤 Предметы"),
    BotCommand(command="equip", description="🪖 Экипировка"),
    BotCommand(command="runes", description="🀄 Руны"),
    BotCommand(command="pets", description="😻 Питомцы"),
    BotCommand(command="achiv", description="🏆 Ачивки"),
    BotCommand(command="skins", description="🪄 Скины"),
    BotCommand(command="ref", description="🔗 Рефка"),
    BotCommand(command="ecoins", description="💳 Пополнить"),
    BotCommand(command="chatref", description="💬🎁 Добавь бота в группу"),
    BotCommand(command="rules", description="📄 Правила проекта"),
    BotCommand(command="help", description="🆘 Помощь"),
]

GROUP_COMMANDS = [
    BotCommand(command="top", description="⭐ Топ группы"),
    BotCommand(command="gboss", description="⚔ Общий босс группы"),
]


async def start_bot_polling(app: web.Application):
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(get_root_router())

    await db.init_db()
    await bot.set_my_commands(PRIVATE_COMMANDS, scope=BotCommandScopeDefault())
    await bot.set_my_commands(GROUP_COMMANDS, scope=BotCommandScopeAllGroupChats())

    app["bot_task"] = asyncio.create_task(dp.start_polling(bot))
    log.info("Bot polling started")


async def stop_bot_polling(app: web.Application):
    task = app.get("bot_task")
    if task:
        task.cancel()


def create_app() -> web.Application:
    app = build_app()
    app.on_startup.append(start_bot_polling)
    app.on_cleanup.append(stop_bot_polling)
    return app


if __name__ == "__main__":
    if not config.BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN не задан. Проверь переменные окружения (.env или Railway Variables).")
    web.run_app(create_app(), port=config.PORT)
