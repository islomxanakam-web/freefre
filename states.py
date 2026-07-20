from aiogram.fsm.state import State, StatesGroup


class AdminPost(StatesGroup):
    choosing_button = State()
    waiting_content = State()
