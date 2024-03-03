from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import StateFilter

storage = MemoryStorage()


class States(StatesGroup):
    default = default_state
    input_money = State()
    input_date = State()
    input_new_category = State()
