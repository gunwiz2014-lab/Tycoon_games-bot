import json
from pathlib import Path

from aiohttp import web

import config
import database as db
import game_logic as gl
from telegram_auth import validate_init_data

WEBAPP_DIR = Path(__file__).parent / "webapp"


def _user_from_request(data: dict):
    init_data = data.get("initData", "")
    user = validate_init_data(init_data)
    return user


async def api_state(request: web.Request):
    body = await request.json()
    tg_user = _user_from_request(body)
    if not tg_user:
        return web.json_response({"error": "invalid_init_data"}, status=401)

    user_id = tg_user["id"]
    await db.get_or_create_user(user_id, tg_user.get("username"))
    user = await gl.sync_user(user_id)

    farm_cfg = config.FARM_LEVELS[user["farm_level"]]
    miner_cfg = config.MINER_LEVELS[user["miner_level"]]

    return web.json_response({
        "coins": user["coins"],
        "gems": user["gems"],
        "lemons": user["lemons"],
        "ore": user["ore"],
        "energy": user["energy"],
        "max_energy": user["max_energy"],
        "farm_level": user["farm_level"],
        "farm_workers": user["farm_workers"],
        "farm_rate": round(gl._farm_rate(user), 1),
        "pending_lemons": user["pending_lemons"],
        "miner_level": user["miner_level"],
        "auto_miners": user["auto_miners"],
        "pending_ore": user["pending_ore"],
        "next_farm_upgrade_cost": farm_cfg.get("upgrade_cost") if user["farm_level"] < config.FARM_MAX_LEVEL else None,
        "next_miner_upgrade_cost": miner_cfg.get("upgrade_cost") if user["miner_level"] < config.MINER_MAX_LEVEL else None,
        "shop_coin_items": config.SHOP_COIN_ITEMS,
        "shop_gem_items": config.SHOP_GEM_ITEMS,
        "star_packs": config.STAR_GEM_PACKS,
    })


ACTIONS = {
    "farm_collect": lambda uid: gl.collect_farm(uid),
    "farm_upgrade": lambda uid: gl.upgrade_farm(uid),
    "farm_hire": lambda uid: gl.hire_farm_worker(uid),
    "farm_sell": lambda uid: gl.sell_lemons(uid),
    "mine_click": lambda uid: gl.manual_mine_click(uid),
    "mine_collect_auto": lambda uid: gl.collect_auto_miners(uid),
    "mine_upgrade": lambda uid: gl.upgrade_miner(uid),
    "mine_sell": lambda uid: gl.sell_ore(uid),
}


async def api_action(request: web.Request):
    body = await request.json()
    tg_user = _user_from_request(body)
    if not tg_user:
        return web.json_response({"error": "invalid_init_data"}, status=401)

    action = body.get("action")
    user_id = tg_user["id"]

    if action in ACTIONS:
        result = await ACTIONS[action](user_id)
    elif action == "buy_coin":
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
    app.router.add_static("/", path=
