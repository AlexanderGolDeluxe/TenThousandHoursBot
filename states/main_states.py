from aiogram.dispatcher.filters.state import StatesGroup, State


class AddTimeToSkill(StatesGroup):
    wait_input_skill_time = State()


class AddNewSkill(StatesGroup):
    wait_input_skill_name = State()
    wait_input_skill_time = State()


class EnterNotificationTime(StatesGroup):
    input_custom_time = State()