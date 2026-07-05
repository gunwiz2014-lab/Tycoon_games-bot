from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import game_logic as gl
import keyboards as kb

router = Router()


def _hp_bar(hp_left: int, hp_max: int, length: int = 12) -> str:
    filled = int(length * max(0, hp_left) / hp_max) if hp_max else 0
    return "🟥" * filled + "⬜" * (length - filled)


async def _render_boss(user_id: int):
    boss = await gl.get_current_boss(user_id)
    bar = _hp_bar(boss["hp_left"], boss["hp_max"])
    if boss["hp_left"] <= 0:
        text = (
            f"👹 <b>{boss['name']}</b>\n\n"
            f"{bar}\n"
            f"HP: 0/{boss['hp_max']}\n\n"
            f"✅ Босс повержен! Награда уже получена.\n"
            f"Новый босс придёт завтра."
        )
    else:
        text = (
            f"👹 <b>{boss['name']}</b>\n\n"
            f"{bar}\n"
            f"HP: {boss['hp_left']}/{boss['hp_max']}\n\n"
            f"Награда за победу: {boss['reward_coins']} 🪙 + {boss['reward_gems']} 💎\n"
            f"Атака: −{gl.config.BOSS_HIT_DAMAGE} HP, −{gl.config.BOSS_HIT_ENERGY_COST} ⚡ за тап"
        )
    return text, kb.boss_menu()


@router.message(F.text == "👹 Босс")
async def boss_menu_msg(message: Message):
    text, markup = await _render_boss(message.from_user.id)
    await message.answer(text, reply_markup=markup)


@router.callback_query(F.data == "boss_hit")
async def boss_hit(call: CallbackQuery):
    res = await gl.hit_boss(call.from_user.id)
    if not res["ok"]:
        reasons = {
            "already_defeated": "Босс уже повержен! Приходи завтра.",
            "no_energy": "Не хватает энергии для атаки!",
        }
        await call.answer(reasons.get(res["reason"], "Не получилось атаковать"), show_alert=True)
        return

    if res["defeated"]:
        await call.answer(f"🎉 Победа! +{res['reward_coins']} 🪙 +{res['reward_gems']} 💎", show_alert=True)
    else:
        await call.answer(f"−{res['damage']} HP боссу!")

    text, markup = await _render_boss(call.from_user.id)
    await call.message.edit_text(text, reply_markup=markup)
