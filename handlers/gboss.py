from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

import game_logic as gl
import keyboards as kb

router = Router()


def _hp_bar(hp_left: int, hp_max: int, length: int = 12) -> str:
    filled = int(length * max(0, hp_left) / hp_max) if hp_max else 0
    return "🟥" * filled + "⬜" * (length - filled)


async def _render_group_boss(chat_id: int):
    boss = await gl.get_current_group_boss(chat_id)
    bar = _hp_bar(boss["hp_left"], boss["hp_max"])
    fighters = len(boss["contributions"])
    if boss["hp_left"] <= 0:
        text = (
            f"👹 <b>{boss['name']}</b> (общий босс группы)\n\n"
            f"{bar}\n"
            f"HP: 0/{boss['hp_max']}\n\n"
            f"✅ Повержен всей группой! Награда уже распределена по вкладу.\n"
            f"Новый босс придёт завтра."
        )
    else:
        text = (
            f"👹 <b>{boss['name']}</b> (общий босс группы)\n\n"
            f"{bar}\n"
            f"HP: {boss['hp_left']}/{boss['hp_max']}\n"
            f"⚔️ Участников боя: {fighters}\n\n"
            f"Награда за победу делится между всеми по вкладу урона.\n"
            f"Общий призовой фонд: {boss['reward_coins']} 🪙 + {boss['reward_gems']} 💎"
        )
    return text, kb.group_boss_menu()


@router.message(Command("gboss"), F.chat.type.in_({"group", "supergroup"}))
async def group_boss_cmd(message: Message):
    text, markup = await _render_group_boss(message.chat.id)
    await message.answer(text, reply_markup=markup)


@router.callback_query(F.data == "gboss_hit")
async def group_boss_hit(call: CallbackQuery):
    if call.message.chat.type not in ("group", "supergroup"):
        await call.answer("Общий босс доступен только в группах!", show_alert=True)
        return

    res = await gl.hit_group_boss(call.message.chat.id, call.from_user.id, call.from_user.username)
    if not res["ok"]:
        reasons = {
            "already_defeated": "Босс уже повержен! Приходи завтра.",
            "no_energy": "Не хватает энергии для атаки!",
        }
        await call.answer(reasons.get(res["reason"], "Не получилось атаковать"), show_alert=True)
        return

    if res["defeated"]:
        reward = res.get("your_reward") or {"coins": 0, "gems": 0}
        await call.answer(
            f"🎉 Общая победа! Твоя доля: +{reward['coins']} 🪙 +{reward['gems']} 💎",
            show_alert=True,
        )
    else:
        await call.answer(f"−{res['damage']} HP боссу!")

    text, markup = await _render_group_boss(call.message.chat.id)
    await call.message.edit_text(text, reply_markup=markup)
