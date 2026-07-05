from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import game_logic as gl
import keyboards as kb

router = Router()


async def _render_daily(user_id: int):
    status = await gl.daily_status(user_id)
    reward = status["next_reward"]

    if status["claimed_today"]:
        reward_line = "✅ Сегодня уже забрано."
    else:
        reward_line = f"Награда за день {reward['day']}: {reward['coins']} 🪙"
        if reward["gems"]:
            reward_line += f" + {reward['gems']} 💎"

    text = (
        f"🎁 <b>Ежедневная награда</b>\n\n"
        f"🔥 Стрик: {status['streak']} дн.\n\n"
        f"{reward_line}\n\n"
        f"Заходи каждый день без пропусков — награда растёт до 7 дня, потом цикл повторяется."
    )
    return text, kb.daily_menu(status["claimed_today"])


@router.message(F.text == "🎁 Дейли")
async def daily_menu_msg(message: Message):
    text, markup = await _render_daily(message.from_user.id)
    await message.answer(text, reply_markup=markup)


@router.callback_query(F.data == "daily_claim")
async def daily_claim(call: CallbackQuery):
    res = await gl.claim_daily(call.from_user.id)
    if not res["ok"]:
        await call.answer("Ты уже забрал награду сегодня, приходи завтра!", show_alert=True)
        return
    await call.answer(f"🎉 +{res['coins']} 🪙 +{res['gems']} 💎 (стрик {res['streak']} дн.)", show_alert=True)
    text, markup = await _render_daily(call.from_user.id)
    await call.message.edit_text(text, reply_markup=markup)


@router.callback_query(F.data == "daily_noop")
async def daily_noop(call: CallbackQuery):
    await call.answer("Возвращайся завтра за новой наградой 🎁")
