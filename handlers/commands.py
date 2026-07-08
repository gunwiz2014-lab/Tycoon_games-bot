from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

import config
import database as db
import game_logic as gl
import keyboards as kb
from .mining import _render_mining
from .boss import _render_boss
from .farm import _render_farm
from .space import _render_space

router = Router()


HELP_TEXT = (
    "🆘 <b>Помощь</b>\n\n"
    "Основные кнопки внизу экрана открывают все режимы игры. Команды дублируют их:\n\n"
    "/prof — 👤 Профиль\n"
    "/bal — 💵 Баланс\n"
    "/shop — 🛍 Магазин\n"
    "/mine — ⛏ Добывать руду\n"
    "/bosses — ⚔ Боссы\n"
    "/top — ⭐ Топ (в личке — глобальный, в группе — групповой)\n"
    "/ref — 🔗 Реферальная ссылка\n"
    "/chatref — 💬 Добавить бота в группу\n"
    "/promo — 🎁 Промокоды\n"
    "/miniguide — 📕 Мини-гайд\n"
    "/rules — 📄 Правила проекта\n\n"
    "Если что-то не работает — напиши в поддержку через кнопку «📱 Магазин и поддержка»."
)

RULES_TEXT = (
    "📄 <b>Правила проекта</b>\n\n"
    "1. Один аккаунт Telegram = один игровой профиль.\n"
    "2. Накрутка через ботов/мультиаккаунты и эксплуатация багов запрещены и караются обнулением прогресса.\n"
    "3. Донат (гемы за Telegram Stars) не подлежит возврату после списания, кроме случаев технической ошибки — пиши в поддержку.\n"
    "4. Будь вежлив в общих чатах и группах с ботом.\n\n"
    "Мы можем менять баланс игры (цены, награды) для улучшения игрового опыта."
)

MINIGUIDE_TEXT = (
    "📕 <b>Мини-гайд</b>\n\n"
    "1. 🍋 Ферма — тапай и собирай лимоны, качай уровень и найм рабочих\n"
    "2. ⛏ Шахта — копай руду вручную, найми авто-майнеров для пассивного дохода\n"
    "3. 🚀 Космос — открывается на 3 уровне завода, добывай звёздную пыль\n"
    "4. 🏪 Лавочка — открывается на 2 уровне завода, приносит монеты напрямую\n"
    "5. 👹 Босс — новый босс каждый день, атакуй и получай награду за победу\n"
    "6. 📜 Квесты — выполняй задания за прогресс и забирай награды\n"
    "7. 🎁 Дейли — заходи каждый день, награда растёт до 7 дня\n"
    "8. 🔗 Рефералка — приглашай друзей и получай бонус за каждого\n\n"
    "Всё это — кнопками в чате. Мини-приложение (📱) нужно только для быстрых покупок и поддержки."
)


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(HELP_TEXT)


@router.message(Command("rules"))
async def cmd_rules(message: Message):
    await message.answer(RULES_TEXT)


@router.message(Command("miniguide"))
async def cmd_miniguide(message: Message):
    await message.answer(MINIGUIDE_TEXT)


@router.message(Command("promo"))
async def cmd_promo(message: Message, command: CommandObject):
    if not command.args:
        await message.answer(
            "🎁 <b>Промокоды</b>\n\n"
            "Чтобы активировать промокод, напиши: <code>/promo КОД</code>\n"
            "Например: <code>/promo BOT2026</code>\n\n"
            "Следи за объявлениями проекта — новые промокоды публикуются там."
        )
        return

    res = await gl.redeem_promo(message.from_user.id, command.args)
    if not res["ok"]:
        reasons = {
            "not_found": "Такого промокода не существует или он больше не активен.",
            "already_used": "Ты уже активировал этот промокод раньше.",
        }
        await message.answer(reasons.get(res["reason"], "Не получилось активировать промокод."))
        return

    await message.answer(f"🎉 Промокод активирован! +{res['coins']} 🪙 + {res['gems']} 💎")


@router.message(Command("prof"), F.chat.type == "private")
async def cmd_prof(message: Message):
    user = await gl.sync_user(message.from_user.id)
    text = (
        f"👤 <b>Профиль</b>\n\n"
        f"🪙 Монеты: {user['coins']}\n"
        f"💎 Гемы: {user['gems']}\n"
        f"🏭 Завод: уровень {user['farm_level']}\n"
        f"⛏ Кирка: уровень {user['miner_level']}\n"
        f"🔥 Дейли-стрик: {user['daily_streak']} дн.\n"
        f"🔗 Приглашено друзей: {user['referral_count']}\n"
    )
    await message.answer(text)


@router.message(Command("bal"), F.chat.type == "private")
async def cmd_bal(message: Message):
    user = await gl.sync_user(message.from_user.id)
    await message.answer(f"💵 <b>Баланс</b>\n\n🪙 Монеты: {user['coins']}\n💎 Гемы: {user['gems']}")


@router.message(Command("shop"), F.chat.type == "private")
async def cmd_shop(message: Message):
    await message.answer(
        "🛍 <b>Магазин</b>\n\nПокупай улучшения за монеты и гемы, а гемы — за ⭐ Telegram Stars.",
        reply_markup=kb.shop_menu(),
    )


@router.message(Command("mine"), F.chat.type == "private")
async def cmd_mine(message: Message):
    text, markup = await _render_mining(message.from_user.id)
    await message.answer(text, reply_markup=markup)


@router.message(Command("bosses"), F.chat.type == "private")
async def cmd_bosses(message: Message):
    text, markup = await _render_boss(message.from_user.id)
    await message.answer(text, reply_markup=markup)


@router.message(Command("top"), F.chat.type == "private")
async def cmd_top_global(message: Message):
    leaders = await db.get_global_leaderboard(config.GLOBAL_TOP_SIZE)
    if not leaders:
        await message.answer("Пока рейтинг пуст.")
        return
    medals = ["🥇", "🥈", "🥉"]
    lines = ["⭐ <b>Глобальный топ игроков</b>\n"]
    for i, row in enumerate(leaders):
        medal = medals[i] if i < 3 else f"{i + 1}."
        name = row["username"] or "Игрок"
        lines.append(f"{medal} @{name} — {row['coins']} 🪙")
    await message.answer("\n".join(lines))


@router.message(Command("ref"), F.chat.type == "private")
async def cmd_ref(message: Message):
    user = await db.get_user(message.from_user.id)
    if not config.BOT_USERNAME:
        await message.answer("Реферальная ссылка временно недоступна — попробуй позже.")
        return
    link = f"https://t.me/{config.BOT_USERNAME}?start=ref_{message.from_user.id}"
    await message.answer(
        f"🔗 <b>Твоя реферальная ссылка</b>\n\n{link}\n\n"
        f"За каждого друга, который запустит бота по этой ссылке, ты получишь "
        f"{config.REFERRAL_REWARD_COINS} 🪙 + {config.REFERRAL_REWARD_GEMS} 💎.\n\n"
        f"Уже приглашено: {user['referral_count']} 👥"
    )


@router.message(Command("chatref"), F.chat.type == "private")
async def cmd_chatref(message: Message):
    group_markup = kb.add_to_group_inline(config.BOT_USERNAME)
    if not group_markup:
        await message.answer("Функция временно недоступна.")
        return
    await message.answer(
        "👥 Добавь бота в свою группу — все участники получат +15% к добыче, "
        "а в группе появится команда /top с рейтингом игроков!",
        reply_markup=group_markup,
    )


@router.message(Command("stats"), F.chat.type == "private")
async def cmd_stats(message: Message):
    if not config.OWNER_ID or message.from_user.id != config.OWNER_ID:
        return  # молча игнорируем для всех, кроме владельца

    stats = await db.get_bot_stats()
    text = (
        f"📊 <b>Статистика бота</b>\n\n"
        f"👥 Всего игроков: {stats['total_players']}\n"
        f"🆕 Новых за 24ч: {stats['new_today']}\n"
        f"🆕 Новых за 7 дней: {stats['new_week']}\n\n"
        f"🟢 Активных за 24ч: {stats['active_today']}\n"
        f"🟢 Активных за 7 дней: {stats['active_week']}\n\n"
        f"👥 Групп с ботом: {stats['groups_count']}\n"
        f"👑 VIP-игроков: {stats['vip_count']}\n"
        f"⭐ Потрачено Stars (всего): {stats['stars_spent']}\n"
    )
    await message.answer(text)


@router.message(Command("lemon"), F.chat.type == "private")
async def cmd_lemon(message: Message):
    text, markup = await _render_farm(message.from_user.id)
    await message.answer(text, reply_markup=markup)


@router.message(Command("space"), F.chat.type == "private")
async def cmd_space(message: Message):
    text, markup = await _render_space(message.from_user.id)
    await message.answer(text, reply_markup=markup)


@router.message(Command("lvl"), F.chat.type == "private")
async def cmd_lvl(message: Message):
    user = await gl.sync_user(message.from_user.id)
    text = (
        f"🌟 <b>Уровни</b>\n\n"
        f"🏭 Ферма: {user['farm_level']}/{config.FARM_MAX_LEVEL}\n"
        f"⛏ Кирка: {user['miner_level']}/{config.MINER_MAX_LEVEL}\n"
        f"🚀 Космос: {user['space_level']}/{config.SPACE_MAX_LEVEL}\n"
        f"🏪 Лавочка: {user['trade_level']}/{config.TRADE_MAX_LEVEL}\n"
        f"🍽 Ресторан: {user['restaurant_level']}/{config.RESTAURANT_MAX_LEVEL}\n"
    )
    await message.answer(text)


@router.message(Command("power"), F.chat.type == "private")
async def cmd_power(message: Message):
    user = await gl.sync_user(message.from_user.id)
    level_cfg = config.MINER_LEVELS[user["miner_level"]]
    text = (
        f"🔥 <b>Мощность кирки</b>\n\n"
        f"Уровень: {user['miner_level']}/{config.MINER_MAX_LEVEL}\n"
        f"За клик: {level_cfg['ore_per_click']} руды\n"
        f"Авто-майнеров: {user['auto_miners']}/{config.AUTO_MINER_MAX}"
    )
    await message.answer(text)


@router.message(Command("stars"), F.chat.type == "private")
async def cmd_stars(message: Message):
    await message.answer(
        "⭐ <b>Магазин гемов за Telegram Stars</b>\n\nОплата происходит прямо в Telegram.",
        reply_markup=kb.star_shop_menu(),
    )


@router.message(Command("ecoins"), F.chat.type == "private")
async def cmd_ecoins(message: Message):
    await message.answer(
        "💳 <b>Пополнение</b>\n\nМонеты не покупаются напрямую — зарабатывай их в игре "
        "или улучшай добычу через 💎 гемы (покупаются за ⭐ Stars командой /stars).",
        reply_markup=kb.shop_menu(),
    )


@router.message(Command("resetcoins"), F.chat.type == "private")
async def cmd_resetcoins(message: Message, command: CommandObject):
    if not config.OWNER_ID or message.from_user.id != config.OWNER_ID:
        return

    amount = 0
    if command.args:
        try:
            amount = max(0, int(command.args))
        except ValueError:
            await message.answer("Использование: /resetcoins СУММА (например /resetcoins 0)")
            return

    await db.update_user(message.from_user.id, coins=amount)
    await message.answer(f"✅ Баланс монет сброшен до {amount} 🪙")


# --- Заглушки для систем, которые ещё в разработке ---
COMING_SOON = {
    "clan": "🏰 Кланы",
    "exped": "⛺ Экспедиции",
    "inv": "🎒 Инвентарь",
    "cases": "📦 Кейсы",
    "boosts": "⚡ Бустеры",
    "collections": "🎎 Коллекции",
    "mats": "🎨 Материалы",
    "items": "🧤 Предметы",
    "equip": "🪖 Экипировка",
    "runes": "🀄 Руны",
    "pets": "😻 Питомцы",
    "achiv": "🏆 Ачивки",
    "skins": "🪄 Скины",
}


def _make_coming_soon_handler(title: str):
    async def handler(message: Message):
        await message.answer(f"{title}\n\n🚧 Этот раздел в разработке — скоро будет добавлен!")
    return handler


for _cmd, _title in COMING_SOON.items():
    router.message(Command(_cmd), F.chat.type == "private")(_make_coming_soon_handler(_title))
