from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

import config
import database as db
import game_logic as gl
import keyboards as kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = await db.get_or_create_user(message.from_user.id, message.from_user.username)
    await message.answer(
        "🍋 <b>Lemon Tycoon</b> — добро пожаловать на завод!\n\n"
        "Выращивай лимоны, копай руду, нанимай рабочих и прокачивай производство.\n"
        "Используй кнопки внизу или открой мини-приложение для наглядного управления.\n\n"
        f"Стартовый баланс: {user['coins']} 🪙 и {user['gems']} 💎",
        reply_markup=kb.main_menu(config.WEBAPP_URL),
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
        f"⚡ Энергия: {user['energy']}/{user['max_energy']}\n"
    )
    await message.answer(text)
