from aiogram import Router

from . import start, farm, mining, shop, payments, space, boss, daily, group, trade, quests, commands, restaurant, gboss


def get_root_router() -> Router:
    root = Router()
    root.include_router(start.router)
    root.include_router(commands.router)
    root.include_router(farm.router)
    root.include_router(mining.router)
    root.include_router(space.router)
    root.include_router(trade.router)
    root.include_router(restaurant.router)
    root.include_router(boss.router)
    root.include_router(gboss.router)
    root.include_router(daily.router)
    root.include_router(quests.router)
    root.include_router(shop.router)
    root.include_router(payments.router)
    root.include_router(group.router)
    return root
