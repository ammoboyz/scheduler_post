from .session import SessionMiddleware
from .user import UserMiddleware

from aiogram import Dispatcher

from sqlalchemy.ext.asyncio import async_sessionmaker


def setup(dp: Dispatcher, sessionmaker: async_sessionmaker):
    """
    Initialises and binds all the middlewares.

    :param Dispatcher dp: Dispatcher (root Router)
    :param async_sessionmaker sessionmaker: Async Sessionmaker
    """

    dp.update.outer_middleware(SessionMiddleware(sessionmaker))
    dp.update.outer_middleware(UserMiddleware())
