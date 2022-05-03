from datetime import time
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, Text

from loader import DISP
from utils.misc import prettify_hours
from utils.db_api import Skills, TTHours_User
from keyboards.default import MAIN_KEYBOARD_MENU
from states import AddTimeToSkill, AddNewSkill, EnterNotificationTime
from keyboards.inline import (
    CANCEL_INPUT_BUTTON,
    create_skills_keyboard,
    create_notification_time_keyboard,
    create_confirm_keyboard
)
from keyboards.inline.callbacks import (
    SKILL_SELECTION_CALLBACK,
    NOTIFICATION_TIME_CALLBACK,
    MANAGE_NOTIFICATION_CALLBACK)


@DISP.message_handler(Command("menu"))
async def show_menu_command(message: types.Message):
    """Выводит клавиатуру со списком доступных действий"""
    await message.answer(
        "<b>Меню</b>\n\nЧто нужно сделать?",
        reply_markup=MAIN_KEYBOARD_MENU)


@DISP.message_handler(Command("total_hours"))
@DISP.message_handler(Text(equals=["Результаты", "Мои результаты"]))
async def show_total_hours_command(message: types.Message):
    """Отправляет отчёт по навыкам"""
    all_skills = Skills(message.from_user.id).get_all_skills()
    all_hours = sum(skill.spent_hours for skill in all_skills)
    total_results = "\n".join(
        f"<i>{skill.name}</i> — "
        f"<b>{prettify_hours(skill.spent_hours)}</b>"
        for skill in all_skills
    )
    await message.answer(
        f"Ты уже вложил <b>{prettify_hours(all_hours)}</b> "
        f"во все навыки. А вот сколько конкретно\n\n{total_results}",
        reply_markup=MAIN_KEYBOARD_MENU)


@DISP.message_handler(Command("add_hours"))
@DISP.message_handler(text="Добавить часы")
async def add_hours_command(message: types.Message):
    """Запускает процедуру добавления времени к навыкам"""
    all_skills = Skills(message.from_user.id).get_all_skills()
    skills_inline_keyboard = (
        await create_skills_keyboard(all_skills, "add hours")
    )
    await message.answer(
        "К какому навыку хочешь добавить время?",
        reply_markup=skills_inline_keyboard)


@DISP.message_handler(Command("add_skill"))
@DISP.message_handler(Text(equals=["Добавить навык", "Добавить ещё навык"]))
async def add_skill_command(message: types.Message):
    """Запускает процедуру создания нового навыка"""
    await message.answer(
        "Давай добавим навык, часы которого будем считать.\n\n"
        "Введи название навыка",
        reply_markup=CANCEL_INPUT_BUTTON
    )
    await AddNewSkill.wait_input_skill_name.set()


@DISP.message_handler(Command("delete_skill"))
@DISP.message_handler(text="Удалить навык")
async def delete_skill_command(message: types.Message):
    """Запускает процедуру удаления навыка"""
    all_skills = Skills(message.from_user.id).get_all_skills()
    skills_inline_keyboard = (
        await create_skills_keyboard(all_skills, "delete skill")
    )
    await message.answer(
        "Какой навык хочешь удалить?",
        reply_markup=skills_inline_keyboard)


@DISP.message_handler(Command("notifications"))
@DISP.message_handler(
    Text(equals=["Уведомление", "Напоминание", "Настроить напоминание"]))
async def enter_notification_time(message: types.Message):
    """Выводит информацию для настройки напоминаний"""
    is_turn_on = TTHours_User(message.from_user).check_notification_on()
    notification_time_keyboard = (
        await create_notification_time_keyboard(
            time_options=(("16", "18"), ("20", "22")),
            is_notification_on=is_turn_on
        )
    )
    await message.answer(
        "Выберите время когда будет приходить напоминание или введите своё.",
        reply_markup=notification_time_keyboard)


@DISP.callback_query_handler(
    SKILL_SELECTION_CALLBACK.filter(action="add hours"))
async def enter_skill_time(
    call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """Реагирует на выбор навыка для добавления часов,
    после чего запрашивает время"""
    await call.answer(cache_time=60)
    selected_skill_name = callback_data.get('skill_name')
    await call.message.answer(
        f"<i>{selected_skill_name}</i>\nСколько часов ты ему уже уделил?\n\n"
        "Напиши<code> + кол-во часов</code>, которое ты уделил навыку.\n"
        "Если ошибся, напиши<code> - кол-во часов</code>",
        reply_markup=CANCEL_INPUT_BUTTON
    )
    await AddTimeToSkill.wait_input_skill_time.set()
    await state.update_data(
        skill_id=callback_data.get("skill_id"),
        skill_name=selected_skill_name)


@DISP.callback_query_handler(
    SKILL_SELECTION_CALLBACK.filter(action="delete skill"))
async def confirm_to_delete_skill(
    call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """Реагирует на выбор навыка для удаления, просит подтверждение"""
    await call.answer(cache_time=60)
    selected_skill_id = callback_data.get("skill_id")
    confirm_data = dict(
        text="Да, точно",
        callback_data="deletion skill confirmed"
    )
    cancel_data = dict(
        text="Нет, я передумал",
        callback_data="delete message"
    )
    confirm_inline_keyboard = (
        await create_confirm_keyboard(confirm_data, cancel_data)
    )
    selected_skill = Skills(call.from_user.id).get_skill(selected_skill_id)
    await call.message.answer(
        "Ты уверен? Ты уже уделил "
        f"<b>{prettify_hours(selected_skill.spent_hours)}</b> "
        f"на <i>{callback_data.get('skill_name')}</i>, "
        "точно хочешь безвозвратно удалить этот навык?",
        reply_markup=confirm_inline_keyboard
    )
    await state.update_data(skill_id=selected_skill_id)


@DISP.callback_query_handler(text="deletion skill confirmed")
async def delete_skill(call: types.CallbackQuery, state: FSMContext):
    """Окончательно удаляет навык после полученного подтверждения"""
    await call.answer(cache_time=60)
    state_data = await state.get_data()
    Skills(call.from_user.id).delete_skill(state_data.get("skill_id"))
    await call.message.answer("Навык удален", reply_markup=MAIN_KEYBOARD_MENU)
    await call.message.delete()
    await state.reset_data()


@DISP.callback_query_handler(text="choose notification time")
async def choose_notification_time(call: types.CallbackQuery):
    """Проводит первое знакомство с напоминаниями и их настройкой"""
    await call.answer(cache_time=60)
    notification_time_keyboard = (
        await create_notification_time_keyboard((("16", "18"), ("20", "22")))
    )
    await call.message.answer(
        "Остался последний шаг\n\n"
        "Каждый день вечером бот будет спрашивать "
        "сколько времени вы уделили какому-то новыку\n\n"
        "Выберите время когда будет приходить напоминание или введите своё. "
        "Позже вы сможете его изменить",
        reply_markup=notification_time_keyboard)


@DISP.callback_query_handler(NOTIFICATION_TIME_CALLBACK.filter())
async def save_selected_notification_time(
    call: types.CallbackQuery, callback_data: dict):
    """Сохраняет указанное по кнопке время напоминания"""
    await call.answer(cache_time=60)
    await call.message.edit_reply_markup()
    notification_time = callback_data.get('notification_time', '22:00')
    notification_time = time.fromisoformat(notification_time)
    TTHours_User(call.from_user).update_notification_time(notification_time)
    await call.message.answer(
        "Отлично. Первое сообщение придёт уже завтра "
        f"в <b>{notification_time.isoformat('minutes')}</b>.\n\nУдачи",
        reply_markup=MAIN_KEYBOARD_MENU)


@DISP.callback_query_handler(MANAGE_NOTIFICATION_CALLBACK.filter())
async def change_notification_state(
    call: types.CallbackQuery, callback_data: dict):
    """Реагирует на нажатие кнопки вкл./откл. напоминания"""
    await call.answer(cache_time=60)
    is_turn_on = callback_data.get("is_turn_on") == "False"
    TTHours_User(call.from_user).manage_notification(is_turn_on)
    await call.message.answer(
        "Напоминание " + ("отключено", "включено")[is_turn_on],
        reply_markup=MAIN_KEYBOARD_MENU
    )
    await call.message.edit_reply_markup()


@DISP.callback_query_handler(text="back to menu", state="*")
async def add_another_skill(call: types.CallbackQuery, state: FSMContext):
    """Отправляет на команду вывода меню действий"""
    await call.answer(cache_time=60)
    await show_menu_command(call.message)
    await call.message.edit_reply_markup()
    await state.finish()


@DISP.callback_query_handler(text="add another skill")
async def add_another_skill(call: types.CallbackQuery):
    """Отправляет на команду создания навыка"""
    await call.answer(cache_time=60)
    await add_skill_command(call.message)
    await call.message.edit_reply_markup()


@DISP.callback_query_handler(text="add another time to skill")
async def add_another_time_to_skill(
    call: types.CallbackQuery, state: FSMContext):
    """Отправляет на команду добавления часам к навыку"""
    await call.answer(cache_time=60)
    state_data = await state.get_data()
    await add_hours_command(state_data.get("user_message"))
    await call.message.edit_reply_markup()
    await state.reset_data()


@DISP.callback_query_handler(text="enter custom time")
async def enter_custom_time(call: types.CallbackQuery):
    """Реагирует на кнопку для ввода времени вручную.
    Запрашивает время в формате HH или HH:MM"""
    await call.answer(cache_time=60)
    await call.message.edit_reply_markup()
    await call.message.answer(
        "Впишите время когда будет удобно получать "
        "напоминание в формате<code> HH </code>или<code> HH:MM</code>",
        reply_markup=CANCEL_INPUT_BUTTON
    )
    await EnterNotificationTime.input_custom_time.set()


@DISP.callback_query_handler(text="delete message")
async def delete_message(call: types.CallbackQuery):
    """Удаляет сообщение с клавиатурой"""
    await call.message.delete()


@DISP.callback_query_handler(text="cancel input", state="*")
async def cancel_input(call: types.CallbackQuery, state: FSMContext):
    """Отменяет начатую процедуру и удаляет сопутствующие сообщение"""
    await call.answer("Отменено")
    await call.message.delete()
    await state.finish()
