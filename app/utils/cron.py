from datetime import datetime
import pytz
import logging as lg

from aiogram import Bot
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.templates import texts, keyboards
from app.database.models import Queue, Config
import settings


async def send_post(
        bot: Bot,
        sessionmaker: async_sessionmaker
) -> None:
    datetime_now = datetime.now().replace(
        second=0,
        microsecond=0
    )

    async with sessionmaker() as session:
        async with session.begin():
            session: AsyncSession

            config = await session.scalar(
                select(Config)
            )

            last_queue = await session.scalar(
                select(Queue)
                .where(Queue.schedule_date <= datetime_now)
                .where(Queue.is_sended == False)
                .order_by(Queue.schedule_date.asc())
            )

            if not last_queue:
                return

            await session.execute(
                update(Queue)
                .where(Queue.id == last_queue.id)
                .values(
                    is_sended=True
                )
            )

            await bot.unpin_chat_message(
                chat_id=settings.ADMIN_CHAT_ID,
                message_id=last_queue.message_id
            )

            try:
                post = await bot.send_photo(
                    chat_id=config.channel_id,
                    photo=last_queue.pic_url,
                    disable_notification=last_queue.disable_notification,
                    caption=texts.SEND_POST.format(
                        last_queue.prompt,
                        config.description
                    )
                )
            except Exception as e:
                return await bot.send_message(
                    chat_id=settings.ADMIN_CHAT_ID,
                    text=texts.ERROR_SEND_POST
                )

            await bot.edit_message_reply_markup(
                chat_id=settings.ADMIN_CHAT_ID,
                message_id=last_queue.message_id,
                reply_markup=keyboards.send_post_done(
                    channel_id=str(config.channel_id)[4:],
                    post_id=post.message_id
                )
            )


async def schedule_tasks(
        bot: Bot,
        sessionmaker: async_sessionmaker
) -> None:
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        func=send_post,
        trigger="cron",
        minute="*",
        args=[bot, sessionmaker]
    )

    scheduler.start()
