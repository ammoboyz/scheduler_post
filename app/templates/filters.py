from aiogram.fsm.state import State, StatesGroup


class AdminState(StatesGroup):
    change_id = State()
    change_description = State()
