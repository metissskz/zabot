from aiogram.fsm.state import StatesGroup, State

class FenceCalc(StatesGroup):
    choosing_type = State()
    entering_length = State()
    entering_gates = State()
