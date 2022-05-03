import asyncio
from typing import List
from datetime import datetime, timedelta

from db import db
from loader import DISP
from utils.db_api import Skills
from keyboards.inline import create_skills_keyboard


def count_delay_to_midnight():
    """Возвращает оставшееся время до полуночи в секундах"""
    time_now = datetime.now().time()
    current_time = timedelta(
        hours=time_now.hour,
        minutes=time_now.minute,
        seconds=time_now.second,
        microseconds=time_now.microsecond
    )
    return timedelta.max.seconds - current_time.seconds


async def send_notification(user_id: int):
    """Отправляет сообщение пользователю согласно переданному ID"""
    all_skills = Skills(user_id).get_all_skills()
    skills_inline_keyboard = (
        await create_skills_keyboard(all_skills, "add hours")
    )
    await DISP.current_state(user=user_id).finish()
    await DISP.bot.send_message(
        chat_id=user_id,
        text="Привет, над чем ты сегодня работал?",
        reply_markup=skills_inline_keyboard
    )
    await asyncio.sleep(1)


async def get_nearest_notifications(columns: List[str] = ["*"]):
    """Получает ближайшее по времени напоминание из БД"""
    db_cursor = db.get_cursor()
    columns_joined = ", ".join(columns)
    diff_time_command = (
        "strftime('%s', notification_time) - "
        "strftime('%s', TIME('now', 'localtime'))"
    )
    db_cursor.execute(
        f"SELECT {columns_joined}, "
        f"{diff_time_command} AS nearest_time "
        "FROM users "
        "WHERE is_notification_on = TRUE AND "
        "nearest_time = ("
			f"SELECT min({diff_time_command}) "
			"FROM users "
			f"WHERE {diff_time_command} >= 0"
		");"
    )
    return db_cursor.fetchall()


async def check_data_relevance(nearest_notifications: list):
    """Проверяет актуально ли напоминание к отправке"""
    db_cursor = db.get_cursor()
    values_joined = ", ".join(
        map(str, (row["user_id"] for row in nearest_notifications))
    )
    db_cursor.execute(
        "SELECT user_id, is_notification_on, "
        "strftime('%s', notification_time) - "
        "strftime('%s', TIME('now', 'localtime')) AS nearest_time "
        "FROM users "
        f"WHERE user_id IN ({values_joined}) AND is_notification_on "
        "AND -60 < nearest_time AND nearest_time < 60"
    )
    return db_cursor.fetchall()


async def launch_notification(nearest_notifications: list):
    """Выполняет планировку отправки напоминаний"""
    columns = ["user_id"]
    if nearest_notifications:
        nearest_notifications = (
            await check_data_relevance(nearest_notifications)
        )
        for notification_row in nearest_notifications:
            await send_notification(notification_row["user_id"])

    nearest_notifications = await get_nearest_notifications(columns)
    delay_to_midnight = count_delay_to_midnight()
    if (nearest_notifications and
        delay_to_midnight > nearest_notifications[0]["nearest_time"]):
        notification_delay = nearest_notifications[0]["nearest_time"]
    else:
        notification_delay = delay_to_midnight
    
    DISP.loop.call_later(
        notification_delay,
        create_notification_task,
        nearest_notifications)


def create_notification_task(nearest_notifications: list):
    """Создаёт задачу по отправке напоминания"""
    asyncio.create_task(
        launch_notification(nearest_notifications))
