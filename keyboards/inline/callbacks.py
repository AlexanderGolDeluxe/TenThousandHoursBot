from aiogram.utils.callback_data import CallbackData


SKILL_SELECTION_CALLBACK = CallbackData("skill selection", "action", "skill_id", "skill_name")
NOTIFICATION_TIME_CALLBACK = CallbackData("notification time", "notification_time")
MANAGE_NOTIFICATION_CALLBACK = CallbackData("manage notification", "is_turn_on")