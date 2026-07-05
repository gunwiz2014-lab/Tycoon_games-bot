from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import config
import game_logic as gl
import keyboards as kb

router = Router()


async def _render_space(user_id: int):
    user = await gl.sync_user(user_id)
    if not user["space_unlocked"]:
        need = config.SPACE_UNLOCK_FARM_LEVEL
        return (
            f"🚀 <b>Космическая станция</b>\n\n"
            f"🔒 Заблокировано! Прокачай завод лимонов до уровня {need}, чтобы открыть космос.",
            None,
        )

    rate = gl._space_rate(user)
    text = (
        f"🚀 <b>Космическая станция</b> — уровень {user['space_level']}\n"
        f"Добыча: {rate:.0f} ✨/час (экипаж: {user['space_crew']})\n\n"
        f"Готово к сбору: <b>{user['pending_dust']:.0f}</b> ✨\n"
        f"На складе: {user['stardust']} ✨\n"
        f"🪙 Монеты: {user['coins']}"
    )
    return text, kb.space_menu(user)


@router.message(F.text == "🚀 Космос")
async def space_menu_msg(message: Message):
    text, markup = await _render_space(message.from_user.id)
    await message.answer(text, reply_markup=markup)


@router.callback_query(F.data == "space_collect")
async def space_collect(call: CallbackQuery):
    res = await gl.collect_space(call.from_user.id)
    if not res["ok"]:
        await call.answer("Космос ещё заблокирован!", show_alert=True)
        return
    await call.answer(f"Собрано {res['gained']} ✨")
    text, markup = await _render_space(call.from_user.id)
    await call.message.edit_text(text, reply_markup=markup)


@router.callback_query(F.data == "space_upgrade")
async def space_upgrade(call: CallbackQuery):
    res = await gl.upgrade_space(call.from_user.id)
    if not res["ok"]:
        reasons = {
            "locked": "Станция ещё заблокирована!",
            "max_level": "Уже максимальный уровень!",
        }
        await call.answer(reasons.get(res["reason"], f"Не хватает монет! Нужно {res.get('cost')} 🪙"), show_alert=True)
        return
    await call.answer(f"Станция улучшена до уровня {res['new_level']}!")
    text, markup = await _render_space(call.from_user.id)
    await call.message.edit_text(text, reply_markup=markup)


@router.callback_query(F.data == "space_hire")
async def space_hire(call: CallbackQuery):
    res = await gl.hire_space_crew(call.from_user.id)
    if not res["ok"]:
        reasons = {"max_crew": "Уже максимум экипажа!"}
        await call.answer(reasons.get(res["reason"], f"Не хватает монет! Нужно {res.get('cost')} 🪙"), show_alert=True)
        return
    await call.answer(f"Нанят астронавт! Всего: {res['crew']}")
    text, markup = await _render_space(call.from_user.id)
    await call.message.edit_text(text, reply_markup=markup)


@router.callback_query(F.data == "space_sell")
async def space_sell(call: CallbackQuery):
    res = await gl.sell_stardust(call.from_user.id)
    await call.answer(f"Продано! +{res['coins_gained']} 🪙")
    text, markup = await _render_space(call.from_user.id)
    await call.message.edit_text(text, reply_markup=markup)
