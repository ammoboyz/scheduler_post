from datetime import datetime

from typing import Optional
from aiogram.filters.callback_data import CallbackData


class ScheduleCallbackFactory(CallbackData, prefix="schedule"):
    action: str
    disable_notification: bool = False
    timestamp: float
