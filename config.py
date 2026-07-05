import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
WEBAPP_URL = os.getenv("WEBAPP_URL", "")
PORT = int(os.getenv("PORT", 8080))

# ---------------------------------------------------------------------------
# ЭКОНОМИКА ИГРЫ (можно свободно менять цифры под баланс)
# ---------------------------------------------------------------------------

# ФЕРМА (завод лимонов): уровень -> (цена апгрейда в монетах, лимонов/час)
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

# Цена одного рабочего фермы (каждый рабочий +20% к rate_per_hour, максимум 10 рабочих)
FARM_WORKER_BASE_COST = 300
FARM_WORKER_COST_GROWTH = 1.6
FARM_MAX_WORKERS = 10
FARM_WORKER_BONUS = 0.20  # +20% производства за рабочего

# Лимоны конвертируются в монеты по этому курсу при продаже
LEMON_SELL_PRICE = 3  # 1 лимон = 3 монеты

# МАЙНИНГ: уровень кирки -> (цена апгрейда в монетах, руды за клик, макс. энергия)
MINER_LEVELS = {
    1: {"upgrade_cost": 0,    "ore_per_click": 1,  "energy_cost": 1},
    2: {"upgrade_cost": 400,  "ore_per_click": 2,  "energy_cost": 1},
    3: {"upgrade_cost": 1200, "ore_per_click": 4,  "energy_cost": 1},
    4: {"upgrade_cost": 3000, "ore_per_click": 8,  "energy_cost": 1},
    5: {"upgrade_cost": 8000, "ore_per_click": 16, "energy_cost": 1},
}
MINER_MAX_LEVEL = max(MINER_LEVELS)

MAX_ENERGY_BASE = 50
ENERGY_REGEN_MINUTES = 3  # +1 энергия каждые 3 минуты

# Авто-майнеры (пассивная добыча руды в час), цена растёт с количеством
AUTO_MINER_BASE_COST = 800
AUTO_MINER_COST_GROWTH = 1.7
AUTO_MINER_ORE_PER_HOUR = 15
AUTO_MINER_MAX = 20

# Руда продаётся по этому курсу
ORE_SELL_PRICE = 5  # 1 руда = 5 монет

# ---------------------------------------------------------------------------
# МАГАЗИН
# ---------------------------------------------------------------------------

# Товары за игровую валюту (монеты)
SHOP_COIN_ITEMS = [
    {"id": "energy_potion", "title": "⚡ Банка энергии (+30)", "price": 250, "type": "energy", "amount": 30},
    {"id": "coin_boost_1h", "title": "🚀 Ускоритель фермы x2 (1 час)", "price": 1000, "type": "boost", "hours": 1},
    {"id": "worker_pack", "title": "👷 Рабочий фермы", "price": FARM_WORKER_BASE_COST, "type": "farm_worker"},
]

# Товары за гемы (премиум-валюта, покупается за Stars)
SHOP_GEM_ITEMS = [
    {"id": "auto_miner", "title": "🤖 Авто-майнер", "price": 15, "type": "auto_miner"},
    {"id": "max_energy_up", "title": "🔋 +20 к макс. энергии навсегда", "price": 25, "type": "max_energy"},
    {"id": "instant_collect", "title": "⏱ Мгновенный сбор со всех локаций", "price": 5, "type": "instant_collect"},
    {"id": "mega_boost_24h", "title": "🔥 Мега-ускоритель x2 (24 часа)", "price": 40, "type": "boost", "hours": 24},
    {"id": "vip_status", "title": "👑 VIP-статус навсегда (+25% ко всей добыче)", "price": 150, "type": "vip"},
]

# Пакеты гемов за Telegram Stars: (гемы, цена в Stars)
STAR_GEM_PACKS = [
    {"id": "gems_50", "gems": 50, "stars": 50, "title": "💎 50 гемов"},
    {"id": "gems_120", "gems": 120, "stars": 100, "title": "💎 120 гемов (+20%)"},
    {"id": "gems_300", "gems": 300, "stars": 220, "title": "💎 300 гемов (+35%)"},
    {"id": "gems_700", "gems": 700, "stars": 450, "title": "💎 700 гемов (+55%)"},
    {"id": "gems_1500", "gems": 1500, "stars": 900, "title": "💎 1500 гемов (+65%)"},
    {"id": "gems_4000", "gems": 4000, "stars": 2000, "title": "💎 4000 гемов (+100%)"},
]

STARTING_COINS = 100
STARTING_GEMS = 5

# Юзернейм бота (без @) — нужен для кнопки "Добавить в группу".
# Впиши сюда имя своего бота, например "lemon_tycoon_bot"
BOT_USERNAME = os.getenv("BOT_USERNAME", "")

# ---------------------------------------------------------------------------
# КОСМОС — третья локация, открывается при уровне завода >= 3
# ---------------------------------------------------------------------------
SPACE_UNLOCK_FARM_LEVEL = 3

SPACE_LEVELS = {
    1: {"upgrade_cost": 0,     "rate_per_hour": 20},
    2: {"upgrade_cost": 1200,  "rate_per_hour": 55},
    3: {"upgrade_cost": 3500,  "rate_per_hour": 130},
    4: {"upgrade_cost": 9000,  "rate_per_hour": 300},
    5: {"upgrade_cost": 22000, "rate_per_hour": 650},
}
SPACE_MAX_LEVEL = max(SPACE_LEVELS)

SPACE_CREW_BASE_COST = 600
SPACE_CREW_COST_GROWTH = 1.65
SPACE_MAX_CREW = 10
SPACE_CREW_BONUS = 0.22

STARDUST_SELL_PRICE = 8  # 1 звёздная пыль = 8 монет

# ---------------------------------------------------------------------------
# БОССЫ — раз в день у каждого игрока появляется новый босс
# ---------------------------------------------------------------------------
BOSS_LIST = [
    {"id": "slime", "name": "🟢 Лимонный слайм", "hp": 150, "reward_coins": 300, "reward_gems": 2},
    {"id": "golem", "name": "🪨 Каменный голем", "hp": 400, "reward_coins": 800, "reward_gems": 4},
    {"id": "dragon", "name": "🐉 Огненный дракон", "hp": 900, "reward_coins": 1800, "reward_gems": 8},
    {"id": "alien", "name": "👽 Космический пришелец", "hp": 1600, "reward_coins": 3500, "reward_gems": 15},
    {"id": "titan", "name": "⚡ Титан бездны", "hp": 3000, "reward_coins": 7000, "reward_gems": 30},
]
BOSS_HIT_DAMAGE = 25       # урон за один тап
BOSS_HIT_ENERGY_COST = 2   # энергии за тап по боссу

# ---------------------------------------------------------------------------
# ДЕЙЛИ-НАГРАДЫ — награда растёт со стриком, сбрасывается при пропуске дня
# ---------------------------------------------------------------------------
DAILY_REWARDS = [
    {"day": 1, "coins": 100, "gems": 0},
    {"day": 2, "coins": 200, "gems": 0},
    {"day": 3, "coins": 350, "gems": 1},
    {"day": 4, "coins": 500, "gems": 1},
    {"day": 5, "coins": 750, "gems": 2},
    {"day": 6, "coins": 1000, "gems": 3},
    {"day": 7, "coins": 2000, "gems": 5},
]

# ---------------------------------------------------------------------------
# ГРУППЫ — бонусы, если бот добавлен в групповой чат
# ---------------------------------------------------------------------------
GROUP_BONUS_MULTIPLIER = 1.15  # +15% ко всей добыче, если игрок состоит в группе с ботом
GROUP_TOP_SIZE = 10

# ---------------------------------------------------------------------------
# ТАП-КЛИКЕР — мгновенный тап прямо в чате/меню фермы
# ---------------------------------------------------------------------------
TAP_LEMON_AMOUNT = 1

# ---------------------------------------------------------------------------
# ЛАВОЧКА / ТОРГОВЫЙ ЦЕНТР — сеть точек, приносящих монеты напрямую
# ---------------------------------------------------------------------------
TRADE_UNLOCK_FARM_LEVEL = 2

TRADE_LEVELS = {
    1: {"upgrade_cost": 0,     "rate_per_hour": 30},
    2: {"upgrade_cost": 800,   "rate_per_hour": 80},
    3: {"upgrade_cost": 2200,  "rate_per_hour": 190},
    4: {"upgrade_cost": 6000,  "rate_per_hour": 420},
    5: {"upgrade_cost": 15000, "rate_per_hour": 900},
}
TRADE_MAX_LEVEL = max(TRADE_LEVELS)

TRADE_OUTLET_BASE_COST = 500
TRADE_OUTLET_COST_GROWTH = 1.55
TRADE_MAX_OUTLETS = 10
TRADE_OUTLET_BONUS = 0.25

# ---------------------------------------------------------------------------
# КВЕСТЫ — разовые задания за прогресс, статус проверяется по счётчикам игрока
# ---------------------------------------------------------------------------
QUESTS = [
    {"id": "lemons_500", "title": "Собери 500 🍋 за всё время", "stat": "lifetime_lemons", "target": 500, "reward_coins": 300, "reward_gems": 2},
    {"id": "ore_300", "title": "Добудь 300 ⛰ руды за всё время", "stat": "lifetime_ore", "target": 300, "reward_coins": 300, "reward_gems": 2},
    {"id": "dust_100", "title": "Собери 100 ✨ звёздной пыли", "stat": "lifetime_dust", "target": 100, "reward_coins": 500, "reward_gems": 3},
    {"id": "boss_3", "title": "Победи 3 боссов", "stat": "boss_kills", "target": 3, "reward_coins": 1000, "reward_gems": 5},
    {"id": "streak_3", "title": "Заходи 3 дня подряд", "stat": "daily_streak", "target": 3, "reward_coins": 500, "reward_gems": 3},
    {"id": "farm_lvl3", "title": "Прокачай завод до 3 уровня", "stat": "farm_level", "target": 3, "reward_coins": 800, "reward_gems": 4},
    {"id": "trade_lvl3", "title": "Прокачай лавочку до 3 уровня", "stat": "trade_level", "target": 3, "reward_coins": 1200, "reward_gems": 6},
]

# Контакт поддержки, показывается в мини-аппе
SUPPORT_CONTACT = os.getenv("SUPPORT_CONTACT", "@your_support_username")
