from typing import Union
from datetime import datetime, timedelta
import logging as lg

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, insert

import settings
from app.utils import func
from app.utils.callback import ScheduleCallbackFactory
from app.templates import filters
from app.database.models import Queue, Config
from app.templates import texts, keyboards


async def admin_menu(
        event: Union[Message, CallbackQuery],
        session: AsyncSession,
        state: FSMContext
):
    await state.set_state()

    config = await session.scalar(
        select(Config)
    )

    queue_list = (await session.scalars(
        select(Queue)
        .where(
            Queue.schedule_date > datetime.now()
        )
    )).all()

    msg_kwargs = {
        "text": texts.ADMIN_MENU.format(
            len(queue_list),
            config.gup_minutes,
            config.channel_id,
            config.description
        ),
        "reply_markup": keyboards.admin_menu(config.gup_minutes),
        "disable_web_page_preview": True
    }

    if isinstance(event, CallbackQuery):
        return await event.message.edit_text(**msg_kwargs)

    if queue_list:
        await event.answer(
            text=texts.QUEUE_LIST.format(
                '\n'.join([
                    f"{i + 1}) <code>{queue_list[i].schedule_date.strftime('%d.%m.%Y %H:%M')} мск</code>"
                    for i in range(len(queue_list))
                ])
            )
        )

    await event.answer(**msg_kwargs)


async def change_gup(
        call: CallbackQuery,
        session: AsyncSession,
        state: FSMContext
):
    new_gap = int(call.data.split(":")[-1])

    await session.execute(
        update(Config)
        .values(gup_minutes=new_gap)
    )

    await admin_menu(call, session, state)


async def change_channel_id(
        call: CallbackQuery,
        state: FSMContext
):
    await state.set_state(filters.AdminState.change_id)

    await call.message.edit_text(
        text=texts.CHANGE_CHANNEL_ID,
        reply_markup=keyboards.back()
    )


async def input_channel_id(
        message: Message,
        session: AsyncSession,
        state: FSMContext
):
    try:
        channel_id = message.forward_from_chat.id
    except:
        return await message.answer(
            text=texts.ERROR_CHANNEL_ID,
            reply_markup=keyboards.back()
        )

    try:
        channel = await message.bot.get_chat(
            chat_id=channel_id
        )
    except TelegramBadRequest:
        return await message.answer(
            text=texts.ERROR_CHANNEL_ID_NONE_BOT,
            reply_markup=keyboards.back()
        )

    await session.execute(
        update(Config)
        .values(
            channel_id=channel_id
        )
    )

    await state.set_state()

    await message.answer(
        text=texts.DONE_CHANNEL_ID.format(channel.full_name),
        reply_markup=keyboards.back()
    )


async def change_description(
        call: CallbackQuery,
        state: FSMContext
):
    await state.set_state(filters.AdminState.change_description)

    await call.message.edit_text(
        text=texts.CHANGE_DESCRIPTION,
        reply_markup=keyboards.back()
    )


async def input_description(
        message: Message,
        session: AsyncSession,
        state: FSMContext
):
    await session.execute(
        update(Config)
        .values(description=message.html_text)
    )

    await state.set_state()

    await message.answer(
        text=texts.INPUT_DESCRIPTION,
        reply_markup=keyboards.back()
    )


async def call_pass(
        call: CallbackQuery
):
    lg.warning(call.data)
    await call.answer()


async def schedule_post(
        call: CallbackQuery,
        session: AsyncSession,
        state: FSMContext
):
    file = await call.message.bot.get_file(call.message.photo[-1].file_id)
    pic_url = f"https://api.telegram.org/file/bot{call.message.bot.token}/{file.file_path}"
    pic_url = await func.aiograph_url(pic_url)
    message_id = call.message.message_id
    prompt = func.get_prompt(call.message.html_text)

    if not prompt:
        await call.answer(
            text=texts.ERROR_PROMPT,
            show_alert=True
        )

    config = await session.scalar(
        select(Config)
    )

    last_queue = await session.scalar(
        select(Queue)
        .where(
            Queue.schedule_date > datetime.now()
        )
        .order_by(Queue.schedule_date.desc())
    )

    if last_queue:
        datetime_now = last_queue.schedule_date
    else:
        datetime_now = datetime.now()

    next_datetime = datetime_now + timedelta(
        minutes=config.gup_minutes
    )

    await state.update_data(**{
        str(message_id): {
            "prompt": prompt,
            "pic_url": pic_url
        }
    })

    await call.message.edit_reply_markup(
        reply_markup=keyboards.schedule_post(
            next_post=next_datetime,
            gup_minutes=config.gup_minutes
        )
    )


async def schedule_post_done(
        call: CallbackQuery,
        callback_data: ScheduleCallbackFactory,
        session: AsyncSession,
        state: FSMContext
):
    fsm_data = await state.get_data()
    post_data: dict = fsm_data.get(
        str(call.message.message_id)
    )

    schedule_date = datetime.fromtimestamp(
        callback_data.timestamp
    ).replace(
        second=0,
        microsecond=0
    )

    await session.execute(
        insert(Queue)
        .values(
            pic_url=post_data.get("pic_url"),
            prompt=post_data.get("prompt"),
            schedule_date=schedule_date,
            message_id=call.message.message_id,
            disable_notification=callback_data.disable_notification
        )
    )

    await call.bot.pin_chat_message(
        chat_id=call.message.chat.id,
        disable_notification=True,
        message_id=call.message.message_id
    )

    await call.message.edit_reply_markup(
        reply_markup=keyboards.schedule_post_done(
            schedule_date,
            callback_data.disable_notification
        )
    )


async def schedule_post_cancel(
        call: CallbackQuery,
        session: AsyncSession
):
    await session.execute(
        delete(Queue)
        .where(Queue.message_id == call.message.message_id)
    )

    await call.bot.unpin_chat_message(
        chat_id=settings.ADMIN_CHAT_ID,
        message_id=call.message.message_id
    )

    await call.message.edit_reply_markup(
        reply_markup=keyboards.schedule_post_cancel()
    )


async def schedule_post_change_date(
        call: CallbackQuery,
        callback_data: ScheduleCallbackFactory,
        session: AsyncSession
):
    config = await session.scalar(
        select(Config)
    )

    next_datetime = datetime.fromtimestamp(
        callback_data.timestamp
    )

    if next_datetime < datetime.now():
        return await call.answer(
            text=texts.OLD_DATE,
            show_alert=True
        )

    await call.message.edit_reply_markup(
        reply_markup=keyboards.schedule_post(
            next_post=next_datetime,
            gup_minutes=config.gup_minutes
        )
    )


async def test(message: Message):
    for i in range(10):
        await message.answer_photo(
            photo="https://telegra.ph/file/b2a33bc3dd4a63e5246a9.jpg",
            caption=f"✏️ <b>Промпт:</b> <code>serious man with with a beard in a hat and in a suit {i}</code>",
            reply_markup=keyboards.schedule_post_cancel()
        )


async def send_post(
        call: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
        callback_data: ScheduleCallbackFactory
):
    config = await session.scalar(
        select(Config)
    )

    fsm_data = await state.get_data()
    post_data: dict = fsm_data.get(
        str(call.message.message_id)
    )

    try:
        post = await call.bot.send_photo(
            chat_id=config.channel_id,
            photo=post_data.get("pic_url"),
            disable_notification=callback_data.disable_notification,
            caption=texts.SEND_POST.format(
                post_data.get("prompt"),
                config.description
            )
        )
    except Exception as e:
        lg.error(f"send_post: {e.__repr__()}")
        return await call.answer(
            text=texts.ERROR_SEND_POST,
            show_alert=True
        )

    await call.message.edit_reply_markup(
        reply_markup=keyboards.send_post_done(
            channel_id=str(config.channel_id)[4:],
            post_id=post.message_id
        )
    )


def register(router: Router):
    router.message.register(admin_menu, Command("admin", "start"))
    router.callback_query.register(admin_menu, F.data == "admin_menu")
    router.callback_query.register(change_gup, F.data.startswith("change:gup:"))
    router.callback_query.register(change_channel_id, F.data == "change:channel_id")
    router.message.register(input_channel_id, filters.AdminState.change_id)

    router.message.register(test, Command("test"))

    router.callback_query.register(change_description, F.data == "change:description")
    router.message.register(input_description, F.text, filters.AdminState.change_description)

    router.callback_query.register(schedule_post, F.data.startswith("reminder_post"))
    router.callback_query.register(schedule_post_cancel, F.data == "schedule_post:cancel")

    router.callback_query.register(
        send_post,
        ScheduleCallbackFactory.filter(F.action == "send")
    )

    router.callback_query.register(
        schedule_post_done,
        ScheduleCallbackFactory.filter(F.action == "done")
    )

    router.callback_query.register(
        schedule_post_change_date,
        ScheduleCallbackFactory.filter(F.action == "change_date")
    )

    router.callback_query.register(call_pass)
