from aiogram import Router, F
from aiogram.types import (
    CallbackQuery, Message, LabeledPrice, PreCheckoutQuery,
)

import config
import game_logic as gl

router = Router()


@router.callback_query(F.data.startswith("buy_stars_"))
async def buy_stars_pack(call: CallbackQuery):
    pack_id = call.data.removeprefix("buy_stars_")
    pack = next((p for p in config.STAR_GEM_PACKS if p["id"] == pack_id), None)
    if not pack:
        await call.answer("Пакет не найден.", show_alert=True)
        return

    await call.message.answer_invoice(
        title=pack["title"],
        description=f"{pack['gems']} гемов для Lemon Tycoon",
        payload=f"gems:{pack_id}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label=pack["title"], amount=pack["stars"])],
    )
    await call.answer()


@router.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    pack_id = payload.split(":", 1)[1]
    pack = next((p for p in config.STAR_GEM_PACKS if p["id"] == pack_id), None)
    if not pack:
        await message.answer("Оплата прошла, но пакет не распознан. Напиши в поддержку.")
        return

    await gl.credit_gems_from_stars(
        message.from_user.id,
        gems=pack["gems"],
        stars_paid=message.successful_payment.total_amount,
        pack_id=pack_id,
    )
    await message.answer(
        f"✅ Оплата прошла! Начислено {pack['gems']} 💎\n"
        f"Спасибо за поддержку Lemon Tycoon ⭐"
    )
