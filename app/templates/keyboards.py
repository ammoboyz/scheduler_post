from datetime import datetime

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

from app.utils.callback import ScheduleCallbackFactory


def admin_menu(already_gap: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="-",
        callback_data=(
            f"change:gup:{already_gap - 5}"
            if already_gap > 5
            else "pass"
        )
    )

    builder.button(
        text=str(already_gap),
        callback_data="pass"
    )

    builder.button(
        text="+",
        callback_data=(
            f"change:gup:{already_gap + 5}"
            if already_gap < 200
            else "pass"
        )
    )

    builder.button(
        text="Изменить ID канала",
        callback_data="change:channel_id"
    )

    builder.button(
        text="Изменить описание",
        callback_data="change:description"
    )

    builder.adjust(3, 1, 1)
    return builder.as_markup()


def back() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Назад",
        callback_data="admin_menu"
    )

    return builder.as_markup()


def schedule_post(next_post: datetime, gup_minutes: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=f"Постинг в: {next_post.strftime('%d.%m.%Y %H:%M')} мск",
        callback_data="pass"
    )

    builder.button(
        text=f"- {gup_minutes} мин",
        callback_data=ScheduleCallbackFactory(
            action="change_date",
            timestamp=next_post.timestamp() - gup_minutes * 60
        )
    )

    builder.button(
        text=f"+ {gup_minutes} мин",
        callback_data=ScheduleCallbackFactory(
            action="change_date",
            timestamp=next_post.timestamp() + gup_minutes * 60
        )
    )

    builder.button(
        text=f"- 12 часов",
        callback_data=ScheduleCallbackFactory(
            action="change_date",
            timestamp=next_post.timestamp() - 60 * 60 * 12
        )
    )

    builder.button(
        text=f"+ 12 часов",
        callback_data=ScheduleCallbackFactory(
            action="change_date",
            timestamp=next_post.timestamp() + 60 * 60 * 12
        )
    )

    builder.button(
        text="✓ Подтвердить дату",
        callback_data=ScheduleCallbackFactory(
            action="done",
            disable_notification=False,
            timestamp=next_post.timestamp()
        )
    )

    builder.button(
        text="✓ Подтвердить дату (без звука)",
        callback_data=ScheduleCallbackFactory(
            action="done",
            disable_notification=True,
            timestamp=next_post.timestamp()
        )
    )

    builder.button(
        text="✓ Запостить сейчас",
        callback_data=ScheduleCallbackFactory(
            action="send",
            disable_notification=False,
            timestamp=next_post.timestamp()
        )
    )

    builder.button(
        text="✓ Запостить сейчас (без звука)",
        callback_data=ScheduleCallbackFactory(
            action="send",
            disable_notification=True,
            timestamp=next_post.timestamp()
        )
    )

    builder.button(
        text="× Отмена",
        callback_data="schedule_post:cancel"
    )

    builder.adjust(1, 2, 2, 1, 1, 1, 1, 1)
    return builder.as_markup()


def schedule_post_done(
        schedule_date: datetime,
        disable_notification: bool
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    notification = (
        "(без звука)"
        if disable_notification
        else ""
    )

    builder.button(
        text=f"✓ Постинг в: {schedule_date.strftime('%d.%m.%Y %H:%M')} мск {notification}",
        callback_data="pass"
    )

    builder.button(
        text="× Отмена",
        callback_data="schedule_post:cancel"
    )

    builder.adjust(1)
    return builder.as_markup()


def schedule_post_cancel() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Запланировать пост",
        callback_data="reminder_post"
    )

    return builder.as_markup()


def send_post_done(
        channel_id: str,
        post_id: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="✓ Пост успешно отправлен",
        url=f"https://t.me/c/{channel_id}/{post_id}"
    )

    return builder.as_markup()
