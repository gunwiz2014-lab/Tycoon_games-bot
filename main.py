import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web

import config
import database as db
from handlers import get_root_router
from webapi import build_app

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("lemon-tycoon-bot")


async def start_bot_polling(app: web.Application):
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(get_root_router())

    await db.init_db()

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
