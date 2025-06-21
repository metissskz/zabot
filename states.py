from aiogram.fsm.state import State, StatesGroup

class FenceCalc(StatesGroup):
    choosing_type = State()
    choosing_post_type = State()
    asking_length = State()
    asking_gate = State()
    asking_foundation = State()
    asking_found_length = State()
    asking_found_width = State()
    asking_found_height = State()
