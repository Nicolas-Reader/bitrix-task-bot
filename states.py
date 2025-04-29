from aiogram.fsm.state import StatesGroup, State


class EnterPhoto(StatesGroup):
    attach_files = State()
