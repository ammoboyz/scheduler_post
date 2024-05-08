import os
import asyncio
import logging

import settings
from app import middlewares, handlers
from app.utils import cron
from app.database import create_sessionmaker

from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.redis import RedisStorage, Redis


log = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logging.getLogger(
        'aiogram.event',
    ).setLevel(logging.WARNING)

    log.info("Starting bot...")

    os.environ['TZ'] = settings.TZ

    log.info('Set timesone to "%s"' % settings.TZ)

    redis: Redis = Redis(host=settings.REDIS)
    storage: RedisStorage = RedisStorage(redis=redis)
    sessionmaker = await create_sessionmaker()

    bot = Bot(
        token=settings.TOKEN,
        parse_mode="HTML"
    )
    dp = Dispatcher(storage=storage)

    middlewares.setup(dp, sessionmaker)
    handlers.setup(dp)

    bot_info = await bot.me()
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(settings.COMMANDS)

    router = Router()
    dp.include_router(router)

    await cron.schedule_tasks(bot, sessionmaker)

    try:
        await dp.start_polling(
            bot,
            router=router,
            dp=dp,
            bot_info=bot_info,
            allowed_updates=[
                "message",
                "callback_query",
                "my_chat_member"
            ]
        )
    finally:
        await dp.fsm.storage.close()


try:
    asyncio.run(main())
except (
    KeyboardInterrupt,
    SystemExit,
):
    log.critical("Bot stopped")
