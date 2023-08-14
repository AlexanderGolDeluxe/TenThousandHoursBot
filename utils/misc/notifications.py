import asyncio
from datetime import datetime

from db import db
from loader import DISP
from utils.db_api import Skills
from keyboards.inline import create_skills_keyboard

FORMAT_NOTIFICATION_TASK_NAME = "Alarm for User-%d"


def count_notification_delay(string_notification_time: str):
    """Высчитывает задержку до отправки сообщения в секундах"""
    notification_delay = (
        datetime.strptime(string_notification_time, "%H:%M:%S") -
        datetime.now()
    )
    return notification_delay.seconds


async def send_notification(user_id: int, send_time_string: str):
    """Отправляет сообщение пользователю согласно переданному времени"""
    all_skills = Skills(user_id).get_all_skills()
    skills_inline_keyboard = (
        await create_skills_keyboard(all_skills, "add hours")
    )
    while not asyncio.current_task().cancelling():
        timedelta_to_sleep = count_notification_delay(send_time_string)
        if timedelta_to_sleep > 0:
            await asyncio.sleep(timedelta_to_sleep + 1)

        await DISP.current_state(user=user_id).finish()
        await DISP.bot.send_message(
            chat_id=user_id,
            text="Привет, над чем ты сегодня работал?",
            reply_markup=skills_inline_keyboard)


async def get_user_notification_time(user_id: int):
    """Получает время напоминания для пользователя из БД"""
    db_cursor = db.get_cursor()
    db_cursor.execute(
        "SELECT notification_time FROM users WHERE user_id = :user_id",
        dict(user_id=user_id)
    )
    return db_cursor.fetchone()["notification_time"]


async def manage_notification(user_id: int, is_turn_on: bool = True):
    """Выполняет планировку отправки напоминания пользователю"""
    task_name = FORMAT_NOTIFICATION_TASK_NAME % user_id
    await cancel_notification(task_name)
    if is_turn_on:
        notification_time = await get_user_notification_time(user_id)
        if notification_time:
            asyncio.create_task(
                send_notification(user_id, notification_time),
                name=task_name)


async def create_notification_tasks():
    """Создаёт задачи по отправке напоминаний"""
    users_rows = db.fetchall(
        table="users",
        columns=["user_id", "notification_time"],
        where_params=dict(is_notification_on=1)
    )
    for user_id, notification_time in users_rows:
        asyncio.create_task(
            send_notification(user_id, notification_time),
            name=FORMAT_NOTIFICATION_TASK_NAME % user_id)


async def cancel_notification(task_name: str):
    """Отменяет задачи отправки напоминаний пользователю"""
    notification_tasks = filter(
        lambda task: task.get_name() == task_name, asyncio.all_tasks()
    )
    for notification_task in notification_tasks:
        notification_task.cancel()
