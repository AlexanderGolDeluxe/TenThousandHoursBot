from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import DISP
from utils.db_api import TTHours_User
from handlers.users.echo import add_skill_command


@DISP.message_handler(CommandStart())
async def bot_start(message: types.Message, state: FSMContext):
    """Отправляет приветственное сообщение,
    отправляет на добавление нового навыка и
    сохраняет в БД пользователя, запустившего бот"""
    await message.answer(
        f"Привет, {message.from_user.full_name}!\n"
        "Слышал о том, чтобы стать экспертом в какой-то деятельности, "
        "нужно заниматься ею <b>10 000 часов</b>?"
    )
    await add_skill_command(message)
    await state.update_data(first_launch=True)
    TTHours_User(message.from_user)
