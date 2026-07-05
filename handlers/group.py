from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

import config
import database as db

router = Router()


@router.message(Command("top"), F.chat.type.in_({"group", "supergroup"}))
async def group_top(message: Message):
    leaders = await db.get_group_leaderboard(message.chat.id, config.GROUP_TOP_SIZE)
    if not leaders:
        await message.answer("Пока в рейтинге группы никого нет — напишите /start боту в личку, чтобы начать игру!")
        return

    medals = ["🥇", "🥈", "🥉"]
    lines = ["🏆 <b>Рейтинг группы по монетам</b>\n"]
    for i, row in enumerate(leaders):
        medal = medals[i] if i < 3 else f"{i + 1}."
        name = row["username"] or "Игрок"
        lines.append(f"{medal} @{name} — {row['coins']} 🪙")

    await message.answer("\n".join(lines))


@router.message(F.chat.type.in_({"group", "supergroup"}))
async def track_group_member(message: Message):
    """Регистрирует любого написавшего в группе как участника (для бонуса и рейтинга)."""
    if message.from_user and not message.from_user.is_bot:
        await db.get_or_create_user(message.from_user.id, message.from_user.username)
        await db.register_group_member(message.chat.id, message.from_user.id, message.from_user.username)
