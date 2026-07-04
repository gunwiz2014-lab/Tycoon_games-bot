import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
WEBAPP_URL = os.getenv("WEBAPP_URL", "")
PORT = int(os.getenv("PORT", 8080))

FARM_LEVELS = {
    1: {"upgrade_cost": 0,     "rate_per_hour": 10},
    2: {"upgrade_cost": 500,   "rate_per_hour": 25},
    3: {"upgrade_cost": 1500,  "rate_per_hour": 60},
    4: {"upgrade_cost": 4000,  "rate_per_hour": 140},
    5: {"upgrade_cost": 10000, "rate_per_hour": 320},
    6: {"upgrade_cost": 25000, "rate_per_hour": 700},
    7: {"upgrade_cost": 60000, "rate_per_hour": 1500},
}
FARM_MAX_LEVEL = max(FARM_LEVELS)

FARM_WORKER_BASE_COST = 300
FARM_WORKER_COST_GROWTH = 1.6
FARM_MAX_WORKERS = 10
FARM_WORKER_BONUS = 0.20

LEMON_SELL_PRICE = 3

MINER_LEVELS = {
    1: {"upgrade_cost": 0,    "ore_per_click": 1,  "energy_cost": 1},
    2: {"upgrade_cost": 400,  "ore_per_click": 2,  "energy_cost": 1},
    3: {"upgrade_cost": 1200, "ore_per_click": 4,  "energy_cost": 1},
    4: {"upgrade_cost": 3000, "ore_per_click": 8,  "energy_cost": 1},
    5: {"upgrade_cost": 8000, "ore_per_click": 16, "energy_cost": 1},
}
MINER_MAX_LEVEL = max(MINER_LEVELS)

MAX_ENERGY_BASE = 50
ENERGY_REGEN_MINUTES = 3

AUTO_MINER_BASE_COST = 800
AUTO_MINER_COST_GROWTH = 1.7
AUTO_MINER_ORE_PER_HOUR = 15
AUTO_MINER_MAX = 20

ORE_SELL_PRICE = 5

SHOP_COIN_ITEMS = [
    {"id": "energy_potion", "title": "⚡ Банка энергии (+30)", "price": 250, "type": "energy", "amount": 30},
    {"id": "coin_boost_1h", "title": "🚀 Ускоритель фермы x2 (1 час)", "price": 1000, "type": "boost", "hours": 1},
    {"id": "worker_pack", "title": "👷 Рабочий фермы", "price": FARM_WORKER_BASE_COST, "type": "farm_worker"},
]

SHOP_GEM_ITEMS = [
    {"id": "auto_miner", "title": "🤖 Авто-майнер", "price": 15, "type": "auto_miner"},
    {"id": "max_energy_up", "title": "🔋 +20 к макс. энергии навсегда", "price": 25, "type": "max_energy"},
    {"id": "instant_collect", "title": "⏱ Мгновенный сбор фермы и шахты", "price": 5, "type": "instant_collect"},
]

STAR_GEM_PACKS = [
    {"id": "gems_50", "gems": 50, "stars": 50, "title": "💎 50 гемов"},
    {"id": "gems_120", "gems": 120, "stars": 100, "title": "💎 120 гемов (+20%)"},
    {"id": "gems_300", "gems": 300, "stars": 220, "title": "💎 300 гемов (+35%)"},
    {"id": "gems_700", "gems": 700, "stars": 450, "title": "💎 700 гемов (+55%)"},
]

STARTING_COINS = 100
STARTING_GEMS = 5
