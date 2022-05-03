from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Запустить бота"),
            types.BotCommand("menu", "Отобразить меню действий"),
            types.BotCommand("total_hours", "Мои результаты"),
            types.BotCommand("add_hours", "Добавить часы"),
            types.BotCommand("add_skill", "Добавить ещё навык"),
            types.BotCommand("delete_skill", "Удалить навык"),
            types.BotCommand("notifications", "Настроить напоминание"),
            types.BotCommand("help", "Вывести справку")
        ]
    )
