from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import game_logic as gl
import keyboards as kb

router = Router()


async def _render_quests(user_id: int):
    quests = await gl.get_quests_status(user_id)
    done_count = sum(1 for q in quests if q["claimed"])
    lines = [f"📜 <b>Квесты</b> ({done_count}/{len(quests)} выполнено)\n"]
    for q in quests:
        if q["claimed"]:
            mark = "✅"
        elif q["done"]:
            mark = "🎁"
        else:
            mark = "⏳"
        lines.append(f"{mark} {q['title']} — {q['progress']}/{q['target']} ({q['reward_coins']} 🪙 + {q['reward_gems']} 💎)")
    return "\n".join(lines), kb.quests_menu(quests)


@router.message(F.text == "📜 Квесты")
async def quests_menu_msg(message: Message):
    text, markup = await _render_quests(message.from_user.id)
    await message.answer(text, reply_markup=markup)


@router.callback_query(F.data.startswith("quest_claim_"))
async def quest_claim(call: CallbackQuery):
    quest_id = call.data.removeprefix("quest_claim_")
    res = await gl.claim_quest(call.from_user.id, quest_id)
    if not res["ok"]:
        reasons = {
            "already_claimed": "Награда уже забрана!",
            "not_done": "Квест ещё не выполнен!",
            "not_found": "Квест не найден.",
        }
        await call.answer(reasons.get(res["reason"], "Не получилось"), show_alert=True)
        return
    await call.answer(f"🎉 +{res['reward_coins']} 🪙 +{res['reward_gems']} 💎", show_alert=True)
    text, markup = await _render_quests(call.from_user.id)
    await call.message.edit_text(text, reply_markup=markup)


@router.callback_query(F.data == "quest_locked")
async def quest_locked(call: CallbackQuery):
    await call.answer("Квест ещё не выполнен")
