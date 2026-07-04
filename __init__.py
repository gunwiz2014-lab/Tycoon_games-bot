from aiogram import Router

from . import start, farm, mining, shop, payments


def get_root_router() -> Router:
    root = Router()
    root.include_router(start.router)
    root.include_router(farm.router)
    root.include_router(mining.router)
    root.include_router(shop.router)
    root.include_router(payments.router)
    return root
