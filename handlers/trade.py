from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import config
import game_logic as gl
import keyboards as kb

router = Router()


async def _render_trade(user_id: int):
    user = await gl.sync_user(user_id)
    if not user["trade_unlocked"]:
        need = config.TRADE_UNLOCK_FARM_LEVEL
        return (
            f"🏪 <b>Лавочка / Торговый центр</b>\n\n"
            f"🔒 Заблокировано! Прокачай завод лимонов до уровня {need}, чтобы открыть лавочку.",
            None,
        )

    if user["trade_level"] < 1:
        return (
            f"🏪 <b>Лавочка / Торговый центр</b>\n\n"
            f"Открой свою первую точку — это бесплатно!",
            kb.trade_menu(user),
        )

    rate = gl._trade_rate(user)
    text = (
        f"🏪 <b>Торговый центр</b> — уровень {user['trade_level']}\n"
        f"Выручка: {rate:.0f} 🪙/час (точек: {user['trade_outlets']})\n\n"
        f"Готово к сбору: <b>{user['pending_trade_coins']:.0f}</b> 🪙\n"
        f"🪙 Монеты: {user['coins']}"
    )
    return text, kb.trade_menu(user)


@router.message(F.text == "🏪 Лавочка")
async def trade_menu_msg(message: Message):
    text, markup = await _render_trade(message.from_user.id)
    await message.answer(text, reply_markup=markup)


@router.callback_query(F.data == "trade_collect")
async def trade_collect(call: CallbackQuery):
    res = await gl.collect_trade(call.from_user.id)
    if not res["ok"]:
        await call.answer("Лавочка ещё заблокирована!", show_alert=True)
        return
    await call.answer(f"Собрано {res['gained']} 🪙")
    text, markup = await _render_trade(call.from_user.id)
    await call.message.edit_text(text, reply_markup=markup)


@router.callback_query(F.data == "trade_upgrade")
async def trade_upgrade(call: CallbackQuery):
    res = await gl.upgrade_trade(call.from_user.id)
    if not res["ok"]:
        reasons = {
            "locked": "Лавочка ещё заблокирована!",
            "max_level": "Уже максимальный уровень!",
        }
        await call.answer(reasons.get(res["reason"], f"Не хватает монет! Нужно {res.get('cost')} 🪙"), show_alert=True)
        return
    msg = "Лавочка открыта! 🎉" if res["new_level"] == 1 else f"Лавочка улучшена до уровня {res['new_level']}!"
    await call.answer(msg)
    text, markup = await _render_trade(call.from_user.id)
    await call.message.edit_text(text, reply_markup=markup)


@router.callback_query(F.data == "trade_hire")
async def trade_hire(call: CallbackQuery):
    res = await gl.hire_trade_outlet(call.from_user.id)
    if not res["ok"]:
        reasons = {"max_outlets": "Уже максимум точек!", "locked": "Сначала открой лавочку!"}
        await call.answer(reasons.get(res["reason"], f"Не хватает монет! Нужно {res.get('cost')} 🪙"), show_alert=True)
        return
    await call.answer(f"Арендована новая точка! Всего: {res['outlets']}")
    text, markup = await _render_trade(call.from_user.id)
    await call.message.edit_text(text, reply_markup=markup)
