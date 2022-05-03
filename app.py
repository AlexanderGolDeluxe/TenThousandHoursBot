from aiogram import executor, Dispatcher

from loader import DISP
import middlewares, filters, handlers
from utils.misc import create_notification_task
from utils.notify_admins import on_startup_notify, on_shutdown_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher: Dispatcher):
    # Устанавливаем дефолтные команды
    await set_default_commands(dispatcher)

    # Уведомляет про запуск
    await on_startup_notify(dispatcher)
    
    # Создание задачи оповещения
    create_notification_task([])


async def on_shutdown(dispatcher: Dispatcher):
    await on_shutdown_notify(dispatcher)


if __name__ == '__main__':
    executor.start_polling(
        DISP,
        loop=DISP.loop,
        on_startup=on_startup,
        on_shutdown=on_shutdown)
