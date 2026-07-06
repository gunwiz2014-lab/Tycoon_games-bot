from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message

import config
import database as db
import game_logic as gl
import keyboards as kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):
    is_new = await db.get_user(message.from_user.id) is None
    user = await db.get_or_create_user(message.from_user.id, message.from_user.username)

    ref_bonus_text = ""
    if is_new and command.args and command.args.startswith("ref_"):
        try:
            referrer_id = int(command.args.removeprefix("ref_"))
            credited = await gl.process_referral(message.from_user.id, referrer_id)
            if credited:
                ref_bonus_text = "\n🎉 Ты пришёл по приглашению — другу уже начислена награда!"
        except ValueError:
            pass

    await message.answer(
        "🍋 <b>Lemon Tycoon</b> — добро пожаловать на завод!\n\n"
        "Выращивай лимоны, копай руду, летай в космос и бей боссов.\n"
        "Используй кнопки внизу или открой мини-приложение для покупок и поддержки.\n\n"
        f"Стартовый баланс: {user['coins']} 🪙 и {user['gems']} 💎"
        f"{ref_bonus_text}",
        reply_markup=kb.main_menu(config.WEBAPP_URL),
    )
    group_markup = kb.add_to_group_inline(config.BOT_USERNAME)
    if group_markup:
        await message.answer(
            "👥 Добавь бота в свою группу — все участники получат +15% к добыче, "
            "а в группе появится команда /top с рейтингом игроков!",
            reply_markup=group_markup,
        )


@router.message(F.text == "👤 Профиль")
async def profile(message: Message):
    user = await gl.sync_user(message.from_user.id)
    text = (
        f"👤 <b>Профиль</b>\n\n"
        f"🪙 Монеты: {user['coins']}\n"
        f"💎 Гемы: {user['gems']}\n"
        f"🍋 Лимоны (не проданы): {user['lemons']}\n"
        f"⛰ Руда (не продана): {user['ore']}\n\n"
        f"🏭 Завод: уровень {user['farm_level']}, рабочих {user['farm_workers']}\n"
        f"⛏ Кирка: уровень {user['miner_level']}, авто-майнеров {user['auto_miners']}\n"
        f"🚀 Космос: {'уровень ' + str(user['space_level']) if user['space_unlocked'] else 'заблокирован'}\n"
        f"🏪 Лавочка: {'уровень ' + str(user['trade_level']) if user['trade_level'] >= 1 else 'не открыта'}\n"
        f"⚡ Энергия: {user['energy']}/{user['max_energy']}\n"
        f"🔥 Дейли-стрик: {user['daily_streak']} дн.\n"
        f"👥 В группе с ботом: {'да (+15% к добыче)' if user['in_group'] else 'нет'}\n"
        f"👑 VIP: {'да (+25% к добыче)' if user['vip'] else 'нет'}\n"
        f"🔗 Приглашено друзей: {user['referral_count']}\n"
    )
    await message.answer(text)
