from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import config
import game_logic as gl
import keyboards as kb

router = Router()


@router.message(F.text == "🛒 Магазин")
async def shop_menu_msg(message: Message):
    await message.answer(
        "🛒 <b>Магазин</b>\n\n"
        "Покупай улучшения за монеты 🪙, редкие бонусы за гемы 💎, "
        "а гемы — за ⭐ Telegram Stars (кнопка внизу списка).",
        reply_markup=kb.shop_menu(),
    )


@router.callback_query(F.data.startswith("buy_coin_"))
async def buy_coin(call: CallbackQuery):
    item_id = call.data.removeprefix("buy_coin_")
    res = await gl.buy_coin_item(call.from_user.id, item_id)
    if not res["ok"]:
        reasons = {
            "no_coins": f"Не хватает монет! Нужно {res.get('cost')} 🪙",
            "max_workers": "Уже максимум рабочих!",
            "not_found": "Товар не найден.",
        }
        await call.answer(reasons.get(res["reason"], "Ошибка покупки"), show_alert=True)
        return
    await call.answer(f"Куплено за {res['cost']} 🪙 ✅")


@router.callback_query(F.data.startswith("buy_gem_"))
async def buy_gem(call: CallbackQuery):
    item_id = call.data.removeprefix("buy_gem_")
    res = await gl.buy_gem_item(call.from_user.id, item_id)
    if not res["ok"]:
        reasons = {
            "no_gems": f"Не хватает гемов! Нужно {res.get('cost')} 💎",
            "max_auto_miners": "Уже максимум авто-майнеров!",
            "not_found": "Товар не найден.",
        }
        await call.answer(reasons.get(res["reason"], "Ошибка покупки"), show_alert=True)
        return
    await call.answer(f"Куплено за {res['cost']} 💎 ✅")


@router.callback_query(F.data == "open_star_shop")
async def open_star_shop(call: CallbackQuery):
    await call.message.answer(
        "⭐ <b>Магазин гемов за Telegram Stars</b>\n\n"
        "Оплата происходит прямо в Telegram, без сторонних сервисов и карт.",
        reply_markup=kb.star_shop_menu(),
    )
    await call.answer()
