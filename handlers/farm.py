from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import config
import game_logic as gl
import keyboards as kb

router = Router()


async def _render_farm(user_id: int):
    user = await gl.sync_user(user_id)
    rate = gl._farm_rate(user)
    text = (
        f"🏭 <b>Завод лимонов</b> — уровень {user['farm_level']}\n"
        f"Производство: {rate:.0f} 🍋/час (рабочих: {user['farm_workers']})\n\n"
        f"Готово к сбору: <b>{user['pending_lemons']:.0f}</b> 🍋\n"
        f"На складе: {user['lemons']} 🍋\n"
        f"🪙 Монеты: {user['coins']}"
    )
    return text, kb.farm_menu(user)


@router.message(F.text == "🍋 Ферма")
async def farm_menu_msg(message: Message):
    text, markup = await _render_farm(message.from_user.id)
    await message.answer(text, reply_markup=markup)


@router.callback_query(F.data == "farm_tap")
async def farm_tap(call: CallbackQuery):
    res = await gl.tap_lemon(call.from_user.id)
    await call.answer(f"+{res['gained']} 🍋")
    text, markup = await _render_farm(call.from_user.id)
    await call.message.edit_text(text, reply_markup=markup)


@router.callback_query(F.data == "farm_collect")
async def farm_collect(call: CallbackQuery):
    res = await gl.collect_farm(call.from_user.id)
    await call.answer(f"Собрано {res['gained']} 🍋")
    text, markup = await _render_farm(call.from_user.id)
    await call.message.edit_text(text, reply_markup=markup)


@router.callback_query(F.data == "farm_upgrade")
async def farm_upgrade(call: CallbackQuery):
    res = await gl.upgrade_farm(call.from_user.id)
    if not res["ok"]:
        if res["reason"] == "max_level":
            await call.answer("Уже максимальный уровень!", show_alert=True)
        else:
            await call.answer(f"Не хватает монет! Нужно {res['cost']} 🪙", show_alert=True)
        return
    await call.answer(f"Завод улучшен до уровня {res['new_level']}!")
    text, markup = await _render_farm(call.from_user.id)
    await call.message.edit_text(text, reply_markup=markup)


@router.callback_query(F.data == "farm_hire")
async def farm_hire(call: CallbackQuery):
    res = await gl.hire_farm_worker(call.from_user.id)
    if not res["ok"]:
        if res["reason"] == "max_workers":
            await call.answer("Максимум рабочих!", show_alert=True)
        else:
            await call.answer(f"Не хватает монет! Нужно {res['cost']} 🪙", show_alert=True)
        return
    await call.answer(f"Нанят рабочий! Всего: {res['workers']}")
    text, markup = await _render_farm(call.from_user.id)
    await call.message.edit_text(text, reply_markup=markup)


@router.callback_query(F.data == "farm_sell")
async def farm_sell(call: CallbackQuery):
    res = await gl.sell_lemons(call.from_user.id)
    await call.answer(f"Продано! +{res['coins_gained']} 🪙")
    text, markup = await _render_farm(call.from_user.id)
    await call.message.edit_text(text, reply_markup=markup)
