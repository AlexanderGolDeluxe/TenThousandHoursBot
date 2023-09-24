from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import DISP
from data.config import ADMIN_LINK
from utils.misc import prettify_hours, manage_notification
from utils.db_api import Skills, TTHours_User
from states import AddNewSkill, AddTimeToSkill, EnterNotificationTime
from keyboards.default import MAIN_KEYBOARD_MENU
from keyboards.inline import CANCEL_INPUT_BUTTON, create_confirm_keyboard
from keyboards.inline.callbacks import SKILL_SELECTION_CALLBACK
from handlers.errors.exceptions import (
    NotCorrectInput,
    check_valid_text_input,
    parse_time_for_add,
    parse_time)


@DISP.message_handler(state=AddNewSkill.wait_input_skill_name)
async def add_new_skill(message: types.Message, state: FSMContext):
    is_valid_skill_name = await check_valid_text_input(message)
    if is_valid_skill_name:
        skill_name = message.text
        skills_obj = Skills(message.from_user.id)
        existing_skill = skills_obj.check_skill_already_exists(skill_name)
        if existing_skill:
            await state.finish()
            confirm_data = dict(
                callback_data=SKILL_SELECTION_CALLBACK.new(
                    action="add hours",
                    skill_id=existing_skill.id,
                    skill_name=skill_name
                )
            )
            cancel_data = dict(callback_data="back to menu")
            confirm_inline_keyboard = (
                await create_confirm_keyboard(confirm_data, cancel_data)
            )
            await message.answer(
                f"Навык <i>{skill_name}</i> уже существует, на нём "
                f"<b>{prettify_hours(existing_skill.spent_hours)}</b>.\n"
                "Хочешь добавить время к нему?",
                reply_markup=confirm_inline_keyboard
            )
        else:
            await state.update_data(skill_name=skill_name)
            await message.answer(
                f"Новый навык — <i>{skill_name}</i>.\n"
                "Сколько часов ты ему уже уделил?",
                reply_markup=CANCEL_INPUT_BUTTON
            )
            await AddNewSkill.wait_input_skill_time.set()


@DISP.message_handler(state=AddNewSkill.wait_input_skill_time)
async def set_time_for_new_skill(message: types.Message, state: FSMContext):
    try:
        skill_time = max(float(message.text), 0.0)
    except ValueError:
        raise NotCorrectInput()
    else:
        state_data: dict = await state.get_data()
        skills_obj = Skills(message.from_user.id)
        skills_obj.create_skill(
            skill_name=state_data.get("skill_name"),
            spent_hours=skill_time
        )
        confirm_data = dict(
            text="Пока всё",
            callback_data=(
                "choose notification time" if state_data.get("first_launch")
                else "back to menu"
            )
        )
        cancel_data = dict(
            text="Добавить ещё навык",
            callback_data="add another skill"
        )
        add_another_skill_buttons = (
            await create_confirm_keyboard(confirm_data, cancel_data)
        )
        await message.answer(
            "Отлично! Навык добавлен. Хочешь добавить ещё один?",
            reply_markup=add_another_skill_buttons
        )
        await state.reset_state(not state_data.get("first_launch"))


@DISP.message_handler(state=AddTimeToSkill.wait_input_skill_time)
async def set_time_for_skill(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    hours_to_add = await parse_time_for_add(message.text)
    skill_id = state_data.get("skill_id")
    skills_obj = Skills(message.from_user.id)
    spent_hours = skills_obj.add_hours_to_skill(skill_id, hours_to_add)
    confirm_data = dict(text="Пока всё", callback_data="back to menu")
    cancel_data = dict(
        text="Добавить ещё часы для навыка",
        callback_data="add another time to skill"
    )
    add_another_time_to_skill_buttons = (
        await create_confirm_keyboard(confirm_data, cancel_data)
    )
    await message.answer(
        f"Круто! Ты уже уделил <i>{state_data.get('skill_name')}</i> "
        f"<b>{prettify_hours(spent_hours)}</b>\n"
        "Хочешь добавить ещё один навык?",
        reply_markup=add_another_time_to_skill_buttons
    )
    await state.update_data(user_message=message)
    await state.reset_state(with_data=False)


@DISP.message_handler(state=EnterNotificationTime.input_custom_time)
async def save_entered_notification_time(
        message: types.Message, state: FSMContext):
    valid_time = await parse_time(message.text)
    if valid_time:
        TTHours_User(message.from_user).update_notification_time(valid_time)
        await manage_notification(message.from_id)
        await message.answer(
            "Новое время установлено!",
            reply_markup=MAIN_KEYBOARD_MENU
        )
        await state.finish()


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@DISP.message_handler(state=None)
async def bot_echo(message: types.Message):
    await message.answer(
        "Не смог разобрать последнее сообщение:\n"
        f"<code>{message.text}</code>\n\n"
        "Попробуйте воспользоваться одной из этих команд "
        "для понимания моих возможностей.\n/menu\n/help\n\n"
        f"Или обратитесь к <a href='{ADMIN_LINK}'>администратору бота</a>.",
        reply_markup=types.ReplyKeyboardRemove())


# Эхо хендлер, куда летят ВСЕ сообщения с указанным состоянием
@DISP.message_handler(state="*", content_types=types.ContentTypes.ANY)
async def bot_echo_all(message: types.Message, state: FSMContext):
    state = await state.get_state()
    await message.answer(
        f"Эхо в состоянии <code>{state}</code>.\n\nСодержание сообщения:\n"
        f"<code>{message}</code>")
