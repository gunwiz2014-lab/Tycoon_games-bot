from pathlib import Path

from aiohttp import web

import config
import database as db
import game_logic as gl
from telegram_auth import validate_init_data

WEBAPP_DIR = Path(__file__).parent / "webapp"


def _user_from_request(data: dict):
    init_data = data.get("initData", "")
    return validate_init_data(init_data)


async def api_state(request: web.Request):
    """Мини-апп теперь отвечает только за магазин и поддержку —
    вся игра (ферма/шахта/космос/лавочка/босс/дейли/квесты) идёт кнопками в чате."""
    body = await request.json()
    tg_user = _user_from_request(body)
    if not tg_user:
        return web.json_response({"error": "invalid_init_data"}, status=401)

    user_id = tg_user["id"]
    await db.get_or_create_user(user_id, tg_user.get("username"))
    user = await db.get_user(user_id)

    return web.json_response({
        "coins": user["coins"],
        "gems": user["gems"],
        "vip": bool(user["vip"]),
        "shop_coin_items": config.SHOP_COIN_ITEMS,
        "shop_gem_items": config.SHOP_GEM_ITEMS,
        "star_packs": config.STAR_GEM_PACKS,
        "support_contact": config.SUPPORT_CONTACT,
    })


async def api_action(request: web.Request):
    body = await request.json()
    tg_user = _user_from_request(body)
    if not tg_user:
        return web.json_response({"error": "invalid_init_data"}, status=401)

    action = body.get("action")
    user_id = tg_user["id"]

    if action == "buy_coin":
        result = await gl.buy_coin_item(user_id, body.get("item_id", ""))
    elif action == "buy_gem":
        result = await gl.buy_gem_item(user_id, body.get("item_id", ""))
    else:
        return web.json_response({"error": "unknown_action"}, status=400)

    return web.json_response(result)


def build_app() -> web.Application:
    app = web.Application()
    app.router.add_post("/api/state", api_state)
    app.router.add_post("/api/action", api_action)
    app.router.add_static("/", path=WEBAPP_DIR, name="webapp", show_index=True)
    return app
