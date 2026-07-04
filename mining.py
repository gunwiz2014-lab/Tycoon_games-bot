from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import config
import game_logic as gl
import keyboards as kb

router = Router()


async def _render_mining(user_id: int):
    user = await gl.sync_user(user_id)
    level_cfg = config.MINER_LEVELS[user["miner_level"]]
    text = (
        f"⛏ <b>Шахта</b> — кирка уровня {user['miner_level']}\n"
        f"За клик: {level_cfg['ore_per_click']} руды (−{level_cfg['energy_cost']} ⚡)\n"
        f"Авто-майнеров: {user['auto_miners']} (готово к сбору: {user['pending_ore']:.0f} руды)\n\n"
        f"⚡ Энергия: {user['energy']}/{user['max_energy']}\n"
        f"⛰ Руда на складе: {user['ore']}\n"
        f"🪙 Монеты: {user['coins']}"
    )
    return text, kb.mining_menu(user)


@router.message(F.text == "⛏ Майнинг")
async def mining_menu_msg(message: Message):
    text, markup = await _render_mining(message.from_user.id)
    await message.answer(text, reply_markup=markup)


@router.callback_query(F.data == "mine_click")
async def mine_click(call: CallbackQuery):
    res = await gl.manual_mine_click(call.from_user.id)
    if not res["ok"]:
        await call.answer("Не хватает энергии! Подожди восстановления или купи в магазине.", show_alert=True)
        return
    await call.answer(f"+{res['ore_gain']} руды!")
    text, markup = await _render_mining(call.from_user.id)
    await call.message.edit_text(text, reply_markup=markup)


@router.callback_query(F.data == "mine_collect_auto")
async def mine_collect_auto(call: CallbackQuery):
    res = await gl.collect_auto_miners(call.from_user.id)
    await call.answer(f"Собрано {res['gained']} руды с авто-майнеров")
    text, markup = await _render_mining(call.from_user.id)
    await call.message.edit_text(text, reply_markup=markup)


@router.callback_query(F.data == "mine_upgrade")
async def mine_upgrade(call: CallbackQuery):
    res = await gl.upgrade_miner(call.from_user.id)
    if not res["ok"]:
        if res["reason"] == "max_level":
            await call.answer("Уже максимальный уровень!", show_alert=True)
        else:
            await call.answer(f"Не хватает монет! Нужно {res['cost']} 🪙", show_alert=True)
        return
    await call.answer(f"Кирка улучшена до уровня {res['new_level']}!")
    text, markup = await _render_mining(call.from_user.id)
    await call.message.edit_text(text, reply_markup=markup)


@router.callback_query(F.data == "mine_sell")
async def mine_sell(call: CallbackQuery):
    res = await gl.sell_ore(call.from_user.id)
    await call.answer(f"Продано! +{res['coins_gained']} 🪙")
    text, markup = await _render_mining(call.from_user.id)
    await call.message.edit_text(text, reply_markup=markup)
