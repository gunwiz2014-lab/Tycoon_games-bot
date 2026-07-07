import time
import math
import json

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


def _group_bonus(user: dict) -> float:
    mult = config.GROUP_BONUS_MULTIPLIER if user.get("in_group") else 1
    if user.get("vip"):
        mult *= 1.25
    return mult


def _farm_rate(user: dict) -> float:
    base = config.FARM_LEVELS[user["farm_level"]]["rate_per_hour"]
    bonus = 1 + user["farm_workers"] * config.FARM_WORKER_BONUS
    boost = 2 if user["boost_until"] > time.time() else 1
    return base * bonus * boost * _group_bonus(user)


def _mine_rate_passive(user: dict) -> float:
    """Пассивная добыча руды в час от авто-майнеров."""
    return user["auto_miners"] * config.AUTO_MINER_ORE_PER_HOUR * _group_bonus(user)


def _space_rate(user: dict) -> float:
    base = config.SPACE_LEVELS[user["space_level"]]["rate_per_hour"]
    bonus = 1 + user["space_crew"] * config.SPACE_CREW_BONUS
    return base * bonus * _group_bonus(user)


def _trade_rate(user: dict) -> float:
    if user["trade_level"] < 1:
        return 0
    base = config.TRADE_LEVELS[user["trade_level"]]["rate_per_hour"]
    bonus = 1 + user["trade_outlets"] * config.TRADE_OUTLET_BONUS
    return base * bonus * _group_bonus(user)


def _restaurant_rate(user: dict) -> float:
    if user["restaurant_level"] < 1:
        return 0
    base = config.RESTAURANT_LEVELS[user["restaurant_level"]]["rate_per_hour"]
    bonus = 1 + user["restaurant_staff"] * config.RESTAURANT_STAFF_BONUS
    return base * bonus * _group_bonus(user)


async def sync_user(user_id: int) -> dict:
    """Подтягивает пользователя, начисляет пассивный доход (ферма/шахта/космос) и энергию."""
    user = await db.get_user(user_id)
    if not user:
        return user

    now = int(time.time())
    user = _regen_energy(user)
    user["in_group"] = await db.is_user_in_any_group(user_id)

    elapsed_hours_farm = min((now - user["last_farm_collect"]) / 3600, config.MAX_OFFLINE_HOURS)
    pending_lemons = elapsed_hours_farm * _farm_rate(user)

    elapsed_hours_mine = min((now - user["last_mine_collect"]) / 3600, config.MAX_OFFLINE_HOURS)
    pending_ore = elapsed_hours_mine * _mine_rate_passive(user)

    elapsed_hours_space = min((now - user["last_space_collect"]) / 3600, config.MAX_OFFLINE_HOURS)
    pending_dust = elapsed_hours_space * _space_rate(user)

    elapsed_hours_trade = min((now - user["last_trade_collect"]) / 3600, config.MAX_OFFLINE_HOURS)
    pending_trade_coins = elapsed_hours_trade * _trade_rate(user)

    elapsed_hours_restaurant = min((now - user["last_restaurant_collect"]) / 3600, config.MAX_OFFLINE_HOURS)
    pending_dishes = elapsed_hours_restaurant * _restaurant_rate(user)

    await db.update_user(
        user_id,
        lemons=user["lemons"],  # оставляем как есть, копим отдельно как "накопленное к сбору"
        energy=user["energy"],
        last_energy_tick=user["last_energy_tick"],
        last_seen=now,
    )

    user["pending_lemons"] = round(pending_lemons, 1)
    user["pending_ore"] = round(pending_ore, 1)
    user["pending_dust"] = round(pending_dust, 1)
    user["pending_trade_coins"] = round(pending_trade_coins, 1)
    user["pending_dishes"] = round(pending_dishes, 1)
    user["space_unlocked"] = user["farm_level"] >= config.SPACE_UNLOCK_FARM_LEVEL
    user["trade_unlocked"] = user["farm_level"] >= config.TRADE_UNLOCK_FARM_LEVEL
    user["restaurant_unlocked"] = user["space_level"] >= config.RESTAURANT_UNLOCK_SPACE_LEVEL
    return user


async def collect_farm(user_id: int) -> dict:
    user = await sync_user(user_id)
    now = int(time.time())
    gained = int(user["pending_lemons"])
    new_lemons = user["lemons"] + gained
    await db.update_user(user_id, lemons=new_lemons, last_farm_collect=now, lifetime_lemons=user["lifetime_lemons"] + gained)
    return {"gained": gained, "total_lemons": new_lemons}


async def collect_auto_miners(user_id: int) -> dict:
    user = await sync_user(user_id)
    now = int(time.time())
    gained = int(user["pending_ore"])
    new_ore = user["ore"] + gained
    await db.update_user(user_id, ore=new_ore, last_mine_collect=now, lifetime_ore=user["lifetime_ore"] + gained)
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
        lifetime_ore=user["lifetime_ore"] + ore_gain,
    )
    return {"ok": True, "ore_gain": ore_gain, "energy_left": user["energy"] - cost}


async def tap_lemon(user_id: int) -> dict:
    """Мгновенный тап-кликер: +N лимонов без затрат энергии."""
    user = await db.get_user(user_id)
    gain = config.TAP_LEMON_AMOUNT
    new_lemons = user["lemons"] + gain
    await db.update_user(user_id, lemons=new_lemons, lifetime_lemons=user["lifetime_lemons"] + gain)
    return {"gained": gain, "total_lemons": new_lemons}


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
        space_res = await collect_space(user_id)
        trade_res = await collect_trade(user_id)
        extra = {"farm": farm_res, "mine": mine_res, "space": space_res, "trade": trade_res}
    elif item["type"] == "boost":
        updates["boost_until"] = int(time.time()) + item["hours"] * 3600
    elif item["type"] == "vip":
        updates["vip"] = 1

    await db.update_user(user_id, **updates)
    await db.log_purchase(user_id, item_id, "gems", price)
    return {"ok": True, "cost": price, **extra}


async def credit_gems_from_stars(user_id: int, gems: int, stars_paid: int, pack_id: str):
    user = await db.get_user(user_id)
    await db.update_user(user_id, gems=user["gems"] + gems)
    await db.log_purchase(user_id, pack_id, "stars", stars_paid)


# ---------------------------------------------------------------------------
# КОСМОС
# ---------------------------------------------------------------------------

def space_crew_cost(space_crew: int) -> int:
    return int(config.SPACE_CREW_BASE_COST * (config.SPACE_CREW_COST_GROWTH ** space_crew))


async def collect_space(user_id: int) -> dict:
    user = await sync_user(user_id)
    if not user["space_unlocked"]:
        return {"ok": False, "reason": "locked"}
    now = int(time.time())
    gained = int(user["pending_dust"])
    new_dust = user["stardust"] + gained
    await db.update_user(user_id, stardust=new_dust, last_space_collect=now, lifetime_dust=user["lifetime_dust"] + gained)
    return {"ok": True, "gained": gained, "total_dust": new_dust}


async def upgrade_space(user_id: int) -> dict:
    user = await db.get_user(user_id)
    if user["farm_level"] < config.SPACE_UNLOCK_FARM_LEVEL:
        return {"ok": False, "reason": "locked"}
    level = user["space_level"]
    if level >= config.SPACE_MAX_LEVEL:
        return {"ok": False, "reason": "max_level"}
    cost = config.SPACE_LEVELS[level + 1]["upgrade_cost"]
    if user["coins"] < cost:
        return {"ok": False, "reason": "no_coins", "cost": cost}
    await db.update_user(user_id, coins=user["coins"] - cost, space_level=level + 1)
    return {"ok": True, "new_level": level + 1, "cost": cost}


async def hire_space_crew(user_id: int) -> dict:
    user = await db.get_user(user_id)
    if user["space_crew"] >= config.SPACE_MAX_CREW:
        return {"ok": False, "reason": "max_crew"}
    cost = space_crew_cost(user["space_crew"])
    if user["coins"] < cost:
        return {"ok": False, "reason": "no_coins", "cost": cost}
    await db.update_user(user_id, coins=user["coins"] - cost, space_crew=user["space_crew"] + 1)
    return {"ok": True, "cost": cost, "crew": user["space_crew"] + 1}


async def sell_stardust(user_id: int) -> dict:
    user = await db.get_user(user_id)
    coins_gained = user["stardust"] * config.STARDUST_SELL_PRICE
    await db.update_user(user_id, stardust=0, coins=user["coins"] + coins_gained)
    return {"coins_gained": coins_gained}


# ---------------------------------------------------------------------------
# БОССЫ — один активный босс в сутки на игрока, ротация по дню года
# ---------------------------------------------------------------------------

def _today_str() -> str:
    return time.strftime("%Y-%m-%d")


def _boss_for_today(user_id: int) -> dict:
    day_index = (int(time.strftime("%j")) + user_id) % len(config.BOSS_LIST)
    return config.BOSS_LIST[day_index]


async def get_current_boss(user_id: int) -> dict:
    user = await db.get_user(user_id)
    today = _today_str()
    boss_cfg = _boss_for_today(user_id)

    if user["boss_date"] != today:
        # новый день — новый босс с полным HP
        await db.update_user(user_id, boss_id=boss_cfg["id"], boss_hp=boss_cfg["hp"], boss_date=today)
        hp_left = boss_cfg["hp"]
    else:
        hp_left = user["boss_hp"]

    return {**boss_cfg, "hp_left": hp_left, "hp_max": boss_cfg["hp"]}


async def hit_boss(user_id: int) -> dict:
    boss = await get_current_boss(user_id)
    user = await sync_user(user_id)

    if boss["hp_left"] <= 0:
        return {"ok": False, "reason": "already_defeated"}
    if user["energy"] < config.BOSS_HIT_ENERGY_COST:
        return {"ok": False, "reason": "no_energy"}

    new_hp = max(0, boss["hp_left"] - config.BOSS_HIT_DAMAGE)
    updates = {
        "energy": user["energy"] - config.BOSS_HIT_ENERGY_COST,
        "boss_hp": new_hp,
    }

    defeated = new_hp <= 0
    reward_coins = 0
    reward_gems = 0
    if defeated:
        reward_coins = boss["reward_coins"]
        reward_gems = boss["reward_gems"]
        updates["coins"] = user["coins"] + reward_coins
        updates["gems"] = user["gems"] + reward_gems
        updates["boss_kills"] = user["boss_kills"] + 1

    await db.update_user(user_id, **updates)
    return {
        "ok": True,
        "damage": config.BOSS_HIT_DAMAGE,
        "hp_left": new_hp,
        "defeated": defeated,
        "reward_coins": reward_coins,
        "reward_gems": reward_gems,
    }


# ---------------------------------------------------------------------------
# ДЕЙЛИ-НАГРАДЫ
# ---------------------------------------------------------------------------

async def claim_daily(user_id: int) -> dict:
    user = await db.get_user(user_id)
    today = _today_str()
    last_claim = user["last_daily_claim"]

    if last_claim:
        last_date = time.strftime("%Y-%m-%d", time.localtime(last_claim))
        if last_date == today:
            return {"ok": False, "reason": "already_claimed"}
        yesterday = time.strftime("%Y-%m-%d", time.localtime(time.time() - 86400))
        streak = user["daily_streak"] + 1 if last_date == yesterday else 1
    else:
        streak = 1

    cycle_day = ((streak - 1) % len(config.DAILY_REWARDS)) + 1
    reward = next(r for r in config.DAILY_REWARDS if r["day"] == cycle_day)

    await db.update_user(
        user_id,
        coins=user["coins"] + reward["coins"],
        gems=user["gems"] + reward["gems"],
        daily_streak=streak,
        last_daily_claim=int(time.time()),
    )
    return {"ok": True, "streak": streak, "coins": reward["coins"], "gems": reward["gems"]}


async def daily_status(user_id: int) -> dict:
    user = await db.get_user(user_id)
    today = _today_str()
    claimed_today = False
    if user["last_daily_claim"]:
        last_date = time.strftime("%Y-%m-%d", time.localtime(user["last_daily_claim"]))
        claimed_today = last_date == today
    cycle_day = (user["daily_streak"] % len(config.DAILY_REWARDS)) + 1 if not claimed_today else (
        ((user["daily_streak"] - 1) % len(config.DAILY_REWARDS)) + 1
    )
    next_reward = next(r for r in config.DAILY_REWARDS if r["day"] == cycle_day)
    return {
        "streak": user["daily_streak"],
        "claimed_today": claimed_today,
        "next_reward": next_reward,
    }


# ---------------------------------------------------------------------------
# ЛАВОЧКА / ТОРГОВЫЙ ЦЕНТР — приносит монеты напрямую, без продажи
# ---------------------------------------------------------------------------

def trade_outlet_cost(trade_outlets: int) -> int:
    return int(config.TRADE_OUTLET_BASE_COST * (config.TRADE_OUTLET_COST_GROWTH ** trade_outlets))


async def collect_trade(user_id: int) -> dict:
    user = await sync_user(user_id)
    if not user["trade_unlocked"]:
        return {"ok": False, "reason": "locked"}
    now = int(time.time())
    gained = int(user["pending_trade_coins"])
    await db.update_user(user_id, coins=user["coins"] + gained, last_trade_collect=now)
    return {"ok": True, "gained": gained}


async def upgrade_trade(user_id: int) -> dict:
    user = await db.get_user(user_id)
    if user["farm_level"] < config.TRADE_UNLOCK_FARM_LEVEL:
        return {"ok": False, "reason": "locked"}
    level = user["trade_level"]
    next_level = level + 1 if level >= 1 else 1
    if level >= config.TRADE_MAX_LEVEL:
        return {"ok": False, "reason": "max_level"}
    cost = config.TRADE_LEVELS[next_level]["upgrade_cost"]
    if user["coins"] < cost:
        return {"ok": False, "reason": "no_coins", "cost": cost}
    await db.update_user(user_id, coins=user["coins"] - cost, trade_level=next_level)
    return {"ok": True, "new_level": next_level, "cost": cost}


async def hire_trade_outlet(user_id: int) -> dict:
    user = await db.get_user(user_id)
    if user["trade_level"] < 1:
        return {"ok": False, "reason": "locked"}
    if user["trade_outlets"] >= config.TRADE_MAX_OUTLETS:
        return {"ok": False, "reason": "max_outlets"}
    cost = trade_outlet_cost(user["trade_outlets"])
    if user["coins"] < cost:
        return {"ok": False, "reason": "no_coins", "cost": cost}
    await db.update_user(user_id, coins=user["coins"] - cost, trade_outlets=user["trade_outlets"] + 1)
    return {"ok": True, "cost": cost, "outlets": user["trade_outlets"] + 1}


# ---------------------------------------------------------------------------
# КВЕСТЫ
# ---------------------------------------------------------------------------

async def get_quests_status(user_id: int) -> list[dict]:
    user = await sync_user(user_id)
    claimed_ids = set(user["quests_claimed"].split(",")) if user["quests_claimed"] else set()
    result = []
    for q in config.QUESTS:
        progress = user.get(q["stat"], 0)
        done = progress >= q["target"]
        result.append({
            **q,
            "progress": min(progress, q["target"]),
            "done": done,
            "claimed": q["id"] in claimed_ids,
        })
    return result


async def claim_quest(user_id: int, quest_id: str) -> dict:
    quests = await get_quests_status(user_id)
    quest = next((q for q in quests if q["id"] == quest_id), None)
    if not quest:
        return {"ok": False, "reason": "not_found"}
    if quest["claimed"]:
        return {"ok": False, "reason": "already_claimed"}
    if not quest["done"]:
        return {"ok": False, "reason": "not_done"}

    user = await db.get_user(user_id)
    claimed_ids = user["quests_claimed"].split(",") if user["quests_claimed"] else []
    claimed_ids.append(quest_id)

    await db.update_user(
        user_id,
        coins=user["coins"] + quest["reward_coins"],
        gems=user["gems"] + quest["reward_gems"],
        quests_claimed=",".join(claimed_ids),
    )
    return {"ok": True, "reward_coins": quest["reward_coins"], "reward_gems": quest["reward_gems"]}


# ---------------------------------------------------------------------------
# РЕФЕРАЛЬНАЯ СИСТЕМА
# ---------------------------------------------------------------------------

async def process_referral(new_user_id: int, referrer_id: int) -> bool:
    """Начисляет награду пригласившему, если новый пользователь ещё не был привязан к рефереру."""
    if new_user_id == referrer_id:
        return False
    referrer = await db.get_user(referrer_id)
    if not referrer:
        return False
    linked = await db.set_referrer(new_user_id, referrer_id)
    if not linked:
        return False
    await db.update_user(
        referrer_id,
        coins=referrer["coins"] + config.REFERRAL_REWARD_COINS,
        gems=referrer["gems"] + config.REFERRAL_REWARD_GEMS,
    )
    return True


# ---------------------------------------------------------------------------
# РЕСТОРАН
# ---------------------------------------------------------------------------

def restaurant_staff_cost(staff: int) -> int:
    return int(config.RESTAURANT_STAFF_BASE_COST * (config.RESTAURANT_STAFF_COST_GROWTH ** staff))


async def collect_restaurant(user_id: int) -> dict:
    user = await sync_user(user_id)
    if not user["restaurant_unlocked"]:
        return {"ok": False, "reason": "locked"}
    now = int(time.time())
    gained = int(user["pending_dishes"])
    new_dishes = user["dishes"] + gained
    await db.update_user(user_id, dishes=new_dishes, last_restaurant_collect=now)
    return {"ok": True, "gained": gained, "total_dishes": new_dishes}


async def upgrade_restaurant(user_id: int) -> dict:
    user = await db.get_user(user_id)
    if user["space_level"] < config.RESTAURANT_UNLOCK_SPACE_LEVEL:
        return {"ok": False, "reason": "locked"}
    level = user["restaurant_level"]
    next_level = level + 1
    if level >= config.RESTAURANT_MAX_LEVEL:
        return {"ok": False, "reason": "max_level"}
    cost = config.RESTAURANT_LEVELS[next_level]["upgrade_cost"]
    if user["coins"] < cost:
        return {"ok": False, "reason": "no_coins", "cost": cost}
    await db.update_user(user_id, coins=user["coins"] - cost, restaurant_level=next_level)
    return {"ok": True, "new_level": next_level, "cost": cost}


async def hire_restaurant_staff(user_id: int) -> dict:
    user = await db.get_user(user_id)
    if user["restaurant_level"] < 1:
        return {"ok": False, "reason": "locked"}
    if user["restaurant_staff"] >= config.RESTAURANT_MAX_STAFF:
        return {"ok": False, "reason": "max_staff"}
    cost = restaurant_staff_cost(user["restaurant_staff"])
    if user["coins"] < cost:
        return {"ok": False, "reason": "no_coins", "cost": cost}
    await db.update_user(user_id, coins=user["coins"] - cost, restaurant_staff=user["restaurant_staff"] + 1)
    return {"ok": True, "cost": cost, "staff": user["restaurant_staff"] + 1}


async def sell_dishes(user_id: int) -> dict:
    user = await db.get_user(user_id)
    coins_gained = user["dishes"] * config.DISH_SELL_PRICE
    await db.update_user(user_id, dishes=0, coins=user["coins"] + coins_gained)
    return {"coins_gained": coins_gained}


# ---------------------------------------------------------------------------
# ПРОМОКОДЫ
# ---------------------------------------------------------------------------

async def redeem_promo(user_id: int, code: str) -> dict:
    code = code.strip().upper()
    reward = config.PROMO_CODES.get(code)
    if not reward:
        return {"ok": False, "reason": "not_found"}

    user = await db.get_user(user_id)
    used = user["promo_redeemed"].split(",") if user["promo_redeemed"] else []
    if code in used:
        return {"ok": False, "reason": "already_used"}

    used.append(code)
    await db.update_user(
        user_id,
        coins=user["coins"] + reward["coins"],
        gems=user["gems"] + reward["gems"],
        promo_redeemed=",".join(used),
    )
    return {"ok": True, "coins": reward["coins"], "gems": reward["gems"]}


# ---------------------------------------------------------------------------
# ГРУППОВОЙ БОСС — общий враг на чат, бьют все участники вместе
# ---------------------------------------------------------------------------

def _group_boss_for_today(chat_id: int) -> dict:
    day_index = (int(time.strftime("%j")) + chat_id) % len(config.BOSS_LIST)
    cfg = config.BOSS_LIST[day_index]
    return {**cfg, "hp": cfg["hp"] * config.GROUP_BOSS_HP_MULTIPLIER}


async def get_current_group_boss(chat_id: int) -> dict:
    row = await db.get_group_boss_row(chat_id)
    today = _today_str()
    cfg = _group_boss_for_today(chat_id)

    if not row or row["date"] != today:
        contributions = "{}"
        await db.upsert_group_boss(chat_id, cfg["id"], cfg["hp"], cfg["hp"], today, contributions)
        hp_left = cfg["hp"]
        contrib_map = {}
    else:
        hp_left = row["hp"]
        contrib_map = json.loads(row["contributions"])

    return {**cfg, "hp_left": hp_left, "hp_max": cfg["hp"], "contributions": contrib_map}


async def hit_group_boss(chat_id: int, user_id: int, username: str | None) -> dict:
    boss = await get_current_group_boss(chat_id)
    user = await sync_user(user_id)

    if boss["hp_left"] <= 0:
        return {"ok": False, "reason": "already_defeated"}
    if user["energy"] < config.GROUP_BOSS_HIT_ENERGY_COST:
        return {"ok": False, "reason": "no_energy"}

    await db.update_user(user_id, energy=user["energy"] - config.GROUP_BOSS_HIT_ENERGY_COST)

    damage = config.GROUP_BOSS_HIT_DAMAGE
    new_hp = max(0, boss["hp_left"] - damage)
    contributions = boss["contributions"]
    key = str(user_id)
    contributions[key] = contributions.get(key, 0) + damage

    defeated = new_hp <= 0
    rewards_given = {}
    if defeated:
        total_damage = sum(contributions.values()) or 1
        for uid_str, dmg in contributions.items():
            uid = int(uid_str)
            share = dmg / total_damage
            coins_reward = int(boss["reward_coins"] * share)
            gems_reward = int(boss["reward_gems"] * share)
            contributor = await db.get_user(uid)
            if contributor:
                await db.update_user(
                    uid,
                    coins=contributor["coins"] + coins_reward,
                    gems=contributor["gems"] + gems_reward,
                )
                rewards_given[uid_str] = {"coins": coins_reward, "gems": gems_reward}

    await db.upsert_group_boss(
        chat_id, boss["id"], new_hp, boss["hp_max"], _today_str(), json.dumps(contributions)
    )

    return {
        "ok": True,
        "damage": damage,
        "hp_left": new_hp,
        "hp_max": boss["hp_max"],
        "defeated": defeated,
        "your_reward": rewards_given.get(str(user_id)),
    }
