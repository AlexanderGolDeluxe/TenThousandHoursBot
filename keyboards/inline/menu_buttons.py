from typing import List, Tuple
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.db_api import Skill
from keyboards.inline.callbacks import (
    SKILL_SELECTION_CALLBACK,
    NOTIFICATION_TIME_CALLBACK,
    MANAGE_NOTIFICATION_CALLBACK)


CANCEL_INPUT_BUTTON = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Отмена", callback_data="cancel input")]
    ]
)


async def create_skills_keyboard(all_skills: List[Skill], action_func: str):
    """Возвращает клавиатуру — перечень всех навыков пользователя и 
    несколько вспомогательных кнопок в зависимости от указанного действия"""
    skills_inline_keyboard: list[list[InlineKeyboardButton]] = []
    for skill in all_skills:
        skills_inline_keyboard.append(
            [InlineKeyboardButton(
                text=skill.name,
                callback_data=SKILL_SELECTION_CALLBACK.new(
                    action=action_func,
                    skill_id=skill.id,
                    skill_name=skill.name
                )
            )]
        )
    if action_func == "add hours":
        skills_inline_keyboard.extend((
            [InlineKeyboardButton(
                text="Добавить новый навык",
                callback_data="add another skill")],
            [InlineKeyboardButton(
                text="Меню",
                callback_data="back to menu")]
        ))
    elif action_func == "delete skill":
        skills_inline_keyboard.append(
            [InlineKeyboardButton(
                text="Назад",
                callback_data="delete message")]
        )
    return InlineKeyboardMarkup(inline_keyboard=skills_inline_keyboard)


async def create_notification_time_keyboard(
    time_options: Tuple[Tuple], is_notification_on: bool = True):
    """Возвращает клавиатуру для настройки напоминаний — список вариантов
    времени уведомлений, которые были переданы,
    кнопку для ввода вручную и вкл./откл. напоминаний"""
    notification_time_keyboard: list[list[InlineKeyboardButton]] = []
    for time_options_block in time_options:
        keyboard_line = []
        for time_option in time_options_block:
            keyboard_line.append(
                InlineKeyboardButton(
                    text=f"{time_option}:00",
                    callback_data=NOTIFICATION_TIME_CALLBACK.new(
                        notification_time=time_option)
                )
            )
        notification_time_keyboard.append(keyboard_line)
        
    notification_time_keyboard.extend((
        [InlineKeyboardButton(
            text="Ввести своё время",
            callback_data="enter custom time")],
        [InlineKeyboardButton(
            text=("В", "Вы")[is_notification_on] + "ключить напоминание",
            callback_data=MANAGE_NOTIFICATION_CALLBACK.new(
                is_turn_on=is_notification_on))]
    ))
    return InlineKeyboardMarkup(inline_keyboard=notification_time_keyboard)


async def create_confirm_keyboard(confirm_data: dict, cancel_data: dict):
    """Возвращает две кнопки с указанными текстом и дальнейшими действиями"""
    confirm_inline_keyboard = [
        [InlineKeyboardButton(
            text=confirm_data.get("text", "Да"),
            callback_data=confirm_data.get("callback_data"))],
        [InlineKeyboardButton(
            text=cancel_data.get("text", "Нет"),
            callback_data=cancel_data.get("callback_data"))]
    ]
    return InlineKeyboardMarkup(inline_keyboard=confirm_inline_keyboard)
