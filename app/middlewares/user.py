from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware, types
from sqlalchemy.ext.asyncio import AsyncSession

import settings


class UserMiddleware(BaseMiddleware):
    """
    Middleware for registering user.
    """

    async def __call__(
        self,
        handler: Callable[[types.Update, Dict[str, Any]], Awaitable[Any]],
        event: types.Update,
        data: Dict[str, Any],
    ) -> Any:
        event_user: Optional[types.User] = data.get("event_from_user")
        session: AsyncSession = data['session']

        if not event.message and not event.callback_query:
            return

        message = (
            event.message
            if event.message
            else event.callback_query.message
        )

        if message.chat.id != settings.ADMIN_CHAT_ID:
            return

        return await handler(event, data)
