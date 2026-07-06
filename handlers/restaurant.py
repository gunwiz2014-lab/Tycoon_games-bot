from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import config
import game_logic as gl
import keyboards as kb

router = Router()


async def _render_restaurant(user_id: int):
    user = await gl.sync_user(user_id)
    if not user["restaurant_unlocked"]:
        need = config.RESTAURANT_UNLOCK_SPACE_LEVEL
        return (
            f"🍽 <b>Ресторан</b>\n\n"
            f"🔒 Заблокировано! Прокачай космическую станцию до уровня {need}, чтобы открыть ресторан.",
            None,
        )

    if user["restaurant_level"] < 1:
        return (
            f"🍽 <b>Ресторан</b>\n\nОткрой свой первый ресторан — это бесплатно!",
            kb.restaurant_menu(user),
        )

    rate = gl._restaurant_rate(user)
    text = (
        f"🍽 <b>Ресторан</b> — уровень {user['restaurant_level']}\n"
        f"Готовит: {rate:.0f} 🍲/час (поваров: {user['restaurant_staff']})\n\n"
        f"Готово к сбору: <b>{user['pending_dishes']:.0f}</b> 🍲\n"
        f"На складе: {user['dishes']} 🍲\n"
        f"🪙 Монеты: {user['coins']}"
    )
    return text, kb.restaurant_menu(user)


@router.message(F.text == "🍽 Ресторан")
async def restaurant_menu_msg(message: Message):
    text, markup = await _render_restaurant(message.from_user.id)
    await message.answer(text, reply_markup=markup)


@router.callback_query(F.data == "restaurant_collect")
async def restaurant_collect(call: CallbackQuery):
    res = await gl.collect_restaurant(call.from_user.id)
    if not res["ok"]:
        await call.answer("Ресторан ещё заблокирован!", show_alert=True)
        return
    await call.answer(f"Собрано {res['gained']} 🍲")
    text, markup = await _render_restaurant(call.from_user.id)
    await call.message.edit_text(text, reply_markup=markup)


@router.callback_query(F.data == "restaurant_upgrade")
async def restaurant_upgrade(call: CallbackQuery):
    res = await gl.upgrade_restaurant(call.from_user.id)
    if not res["ok"]:
        reasons = {"locked": "Ресторан ещё заблокирован!", "max_level": "Уже максимальный уровень!"}
        await call.answer(reasons.get(res["reason"], f"Не хватает монет! Нужно {res.get('cost')} 🪙"), show_alert=True)
        return
    msg = "Ресторан открыт! 🎉" if res["new_level"] == 1 else f"Ресторан улучшен до уровня {res['new_level']}!"
    await call.answer(msg)
    text, markup = await _render_restaurant(call.from_user.id)
    await call.message.edit_text(text, reply_markup=markup)


@router.callback_query(F.data == "restaurant_hire")
async def restaurant_hire(call: CallbackQuery):
    res = await gl.hire_restaurant_staff(call.from_user.id)
    if not res["ok"]:
        reasons = {"max_staff": "Уже максимум поваров!", "locked": "Сначала открой ресторан!"}
        await call.answer(reasons.get(res["reason"], f"Не хватает монет! Нужно {res.get('cost')} 🪙"), show_alert=True)
        return
    await call.answer(f"Нанят повар! Всего: {res['staff']}")
    text, markup = await _render_restaurant(call.from_user.id)
    await call.message.edit_text(text, reply_markup=markup)


@router.callback_query(F.data == "restaurant_sell")
async def restaurant_sell(call: CallbackQuery):
    res = await gl.sell_dishes(call.from_user.id)
    await call.answer(f"Продано! +{res['coins_gained']} 🪙")
    text, markup = await _render_restaurant(call.from_user.id)
    await call.message.edit_text(text, reply_markup=markup)
