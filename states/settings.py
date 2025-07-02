from aiogram.fsm.state import State, StatesGroup

class SettingsFSM(StatesGroup):
    choosing_option = State()
    updating_price = State()
    updating_address = State()
    uploading_logo = State()
