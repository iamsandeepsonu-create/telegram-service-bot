from aiogram.fsm.state import State, StatesGroup

class OrderPlacement(StatesGroup):
    waiting_for_requirements = State()
    waiting_for_attachment = State()
    confirm_order = State()

class AdminAddService(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_duration = State()

class AdminBroadcast(StatesGroup):
    waiting_for_message = State()
