import time
import math

import config
import database as db


def _regen_energy(user: dict) -> dict:
    """Считает регенерацию энергии по времени с последнего тика."""
    now = int(time.time())
    elapsed_min = (now - user["last_energy_tick"]) / 60
    gained = int(elapsed_min // config.ENERGY_REGEN_MINUTES)
    if gained > 0:
        user["energy"] = min(user["max_energy"], user["energy"] + gained)
        user["last_energy_tick"] = user["last_energy_tick"] + gained * config.ENERGY_REGEN_MINUTES * 60
    return user


def _farm_rate(user: dict) -> float:
    base = config.FARM_LEVELS[user["farm_level"]]["rate_per_hour"]
    bonus = 1 + user["farm_workers"] * config.FARM_WORKER_BONUS
    boost = 2 if user["boost_until"] > time.time() else 1
    return base * bonus * boost


def _mine_rate_passive(user: dict) -> float:
    """Пассивная добыча руды в час от авто-майнеров."""
    return user["auto_miners"] * config.AUTO_MINER_ORE_PER_HOUR


async def sync_user(user_id: int) -> dict:
    """Подтягивает пользователя, начисляет пассивный доход (ферма + авто-майнеры) и энергию."""
    user = await db.get_user(user_id)
    if not user:
        return user

    now = int(time.time())
    user = _regen_energy(user)

    elapsed_hours_farm = (now - user["last_farm_collect"]) / 3600
    pending_lemons = elapsed_hours_farm * _farm_rate(user)

    elapsed_hours_mine = (now - user["last_mine_collect"]) / 3600
    pending_ore = elapsed_hours_mine * _mine_rate_passive(user)

    await db.update_user(
        user_id,
        lemons=user["lemons"],
        energy=user["energy"],
        last_energy_tick=user["last_energy_tick"],
    )

    user["pending_lemons"] = round(pending_lemons, 1)
    user["pending_ore"] = round(pending_ore, 1)
    return user


async def collect_farm(user_id: int) -> dict:
    user = await sync_user(user_id)
    now = int(time.time())
    gained = int(user["pending_lemons"])
    new_lemons = user["lemons"] + gained
    await db.update_user(user_id, lemons=new_lemons, last_farm_collect=now)
    return {"gained": gained, "total_lemons": new_lemons}


async def collect_auto_miners(user_id: int) -> dict:
    user = await sync_user(user_id)
    now = int(time.time())
    gained = int(user["pending_ore"])
    new_ore = user["ore"] + gained
    await db.update_user(user_id, ore=new_ore, last_mine_collect=now)
    return {"gained": gained, "total_ore": new_ore}


async def manual_mine_click(user_id: int) -> dict:
    user = await sync_user(user_id)
    level_cfg = config.MINER_LEVELS[user["miner_level"]]
    cost = level_cfg["energy_cost"]
    if user["energy"] < cost:
        return {"ok": False, "reason": "no_energy"}

    ore_gain = level_cfg["ore_per_click"]
    await db.update_user(
        user_id,
        energy=user["energy"] - cost,
        ore=user["ore"] + ore_gain,
    )
    return {"ok": True, "ore_gain": ore_gain, "energy_left": user["energy"] - cost}


def farm_worker_cost(farm_workers: int) -> int:
    return int(config.FARM_WORKER_BASE_COST * (config.FARM_WORKER_COST_GROWTH ** farm_workers))


def auto_miner_cost(auto_miners: int) -> int:
    return int(config.AUTO_MINER_BASE_COST * (config.AUTO_MINER_COST_GROWTH ** auto_miners))


async def upgrade_farm(user_id: int) -> dict:
    user = await db.get_user(user_id)
    level = user["farm_level"]
    if level >= config.FARM_MAX_LEVEL:
        return {"ok": False, "reason": "max_level"}
    cost = config.FARM_LEVELS[level + 1]["upgrade_cost"]
    if user["coins"] < cost:
        return {"ok": False, "reason": "no_coins", "cost": cost}
    await db.update_user(user_id, coins=user["coins"] - cost, farm_level=level + 1)
    return {"ok": True, "new_level": level + 1, "cost": cost}


async def hire_farm_worker(user_id: int) -> dict:
    user = await db.get_user(user_id)
    if user["farm_workers"] >= config.FARM_MAX_WORKERS:
        return {"ok": False, "reason": "max_workers"}
    cost = farm_worker_cost(user["farm_workers"])
    if user["coins"] < cost:
        return {"ok": False, "reason": "no_coins", "cost": cost}
    await db.update_user(user_id, coins=user["coins"] - cost, farm_workers=user["farm_workers"] + 1)
    return {"ok": True, "cost": cost, "workers": user["farm_workers"] + 1}


async def upgrade_miner(user_id: int) -> dict:
    user = await db.get_user(user_id)
    level = user["miner_level"]
    if level >= config.MINER_MAX_LEVEL:
        return {"ok": False, "reason": "max_level"}
    cost = config.MINER_LEVELS[level + 1]["upgrade_cost"]
    if user["coins"] < cost:
        return {"ok": False, "reason": "no_coins", "cost": cost}
    await db.update_user(user_id, coins=user["coins"] - cost, miner_level=level + 1)
    return {"ok": True, "new_level": level + 1, "cost": cost}


async def buy_auto_miner_with_gems(user_id: int) -> dict:
    user = await db.get_user(user_id)
    if user["auto_miners"] >= config.AUTO_MINER_MAX:
        return {"ok": False, "reason": "max_auto_miners"}
    price = next(i for i in config.SHOP_GEM_ITEMS if i["id"] == "auto_miner")["price"]
    if user["gems"] < price:
        return {"ok": False, "reason": "no_gems", "cost": price}
    await db.update_user(user_id, gems=user["gems"] - price, auto_miners=user["auto_miners"] + 1)
    return {"ok": True, "cost": price, "auto_miners": user["auto_miners"] + 1}


async def sell_lemons(user_id: int) -> dict:
    user = await db.get_user(user_id)
    coins_gained = user["lemons"] * config.LEMON_SELL_PRICE
    await db.update_user(user_id, lemons=0, coins=user["coins"] + coins_gained)
    return {"coins_gained": coins_gained}


async def sell_ore(user_id: int) -> dict:
    user = await db.get_user(user_id)
    coins_gained = user["ore"] * config.ORE_SELL_PRICE
    await db.update_user(user_id, ore=0, coins=user["coins"] + coins_gained)
    return {"coins_gained": coins_gained}


async def buy_coin_item(user_id: int, item_id: str) -> dict:
    item = next((i for i in config.SHOP_COIN_ITEMS if i["id"] == item_id), None)
    if not item:
        return {"ok": False, "reason": "not_found"}
    user = await db.get_user(user_id)

    price = item["price"]
    if item["type"] == "farm_worker":
        price = farm_worker_cost(user["farm_workers"])
        if user["farm_workers"] >= config.FARM_MAX_WORKERS:
            return {"ok": False, "reason": "max_workers"}

    if user["coins"] < price:
        return {"ok": False, "reason": "no_coins", "cost": price}

    updates = {"coins": user["coins"] - price}
    if item["type"] == "energy":
        updates["energy"] = min(user["max_energy"], user["energy"] + item["amount"])
    elif item["type"] == "boost":
        updates["boost_until"] = int(time.time()) + item["hours"] * 3600
    elif item["type"] == "farm_worker":
        updates["farm_workers"] = user["farm_workers"] + 1

    await db.update_user(user_id, **updates)
    await db.log_purchase(user_id, item_id, "coins", price)
    return {"ok": True, "cost": price}


async def buy_gem_item(user_id: int, item_id: str) -> dict:
    item = next((i for i in config.SHOP_GEM_ITEMS if i["id"] == item_id), None)
    if not item:
        return {"ok": False, "reason": "not_found"}
    user = await db.get_user(user_id)
    price = item["price"]
    if user["gems"] < price:
        return {"ok": False, "reason": "no_gems", "cost": price}

    updates = {"gems": user["gems"] - price}
    extra = {}
    if item["type"] == "auto_miner":
        if user["auto_miners"] >= config.AUTO_MINER_MAX:
            return {"ok": False, "reason": "max_auto_miners"}
        updates["auto_miners"] = user["auto_miners"] + 1
    elif item["type"] == "max_energy":
        updates["max_energy"] = user["max_energy"] + 20
    elif item["type"] == "instant_collect":
        farm_res = await collect_farm(user_id)
        mine_res = await collect_auto_miners(user_id)
        extra = {"farm": farm_res, "mine": mine_res}

    await db.update_user(user_id, **updates)
    await db.log_purchase(user_id, item_id, "gems", price)
    return {"ok": True, "cost": price, **extra}


async def credit_gems_from_stars(user_id: int, gems: int, stars_paid: int, pack_id: str):
    user = await db.get_user(user_id)
    await db.update_user(user_id, gems=user["gems"] + gems)
    await db.log_purchase(user_id, pack_id, "stars", stars_paid)
