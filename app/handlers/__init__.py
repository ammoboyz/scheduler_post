from . import (
    menu
)

from aiogram import Dispatcher, Router


def setup(dp: Dispatcher):
    """
    Setup all the handlers and routers, bind filters

    :param Dispatcher dp: Dispatcher (root Router)
    """

    admin_router = Router()

    dp.include_router(admin_router)

    menu.register(admin_router)
