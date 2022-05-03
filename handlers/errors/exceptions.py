"""Кастомные исключения, генерируемые приложением"""
from datetime import time
from aiogram import types

class NotCorrectInput(Exception):
    """Некорректное сообщение ввода текста, которое не удалось распарсить"""
    pass

class NotCorrectTimeInput(Exception):
    """Некорректное сообщение ввода времени, которое не удалось распарсить"""
    pass


async def check_valid_text_input(message: types.Message):
    """Проверяет введённое название на отсутствие команд бота.
    При ошибках вызывает исключение NotCorrectInput"""
    if message.text.startswith("/"):
        raise NotCorrectInput()
    else:
        bot_commands: list[types.BotCommand] = (
            await message.bot.get_my_commands()
        )
        if any(
            message.text.lower() == command.description.lower()
            for command in bot_commands):
                raise NotCorrectInput()
        else:
            return True


async def parse_time_for_add(message_text: str):
    """Форматирует введённые часы в вещественное число.
    При ошибках вызывает исключение NotCorrectInput"""
    if len(message_text) > 1 and message_text.startswith(("+", "-")):
        text_to_parse = message_text[0] + (
            message_text[1:].strip().replace(",", ".")
        )
        try:
            time_for_add = float(text_to_parse)
        except ValueError:
            raise NotCorrectInput()
        else:
            return time_for_add
    else:
        raise NotCorrectInput()


async def parse_time(message_text: str):
    """Парсит введённое время в формате HH или HH:MM.
    При ошибках вызывает исключение NotCorrectTimeInput"""
    if message_text.isdigit():
        notification_time = int(message_text)
        if 0 <= notification_time < 24:
            return time(hour=notification_time)
        else:
            raise NotCorrectTimeInput()
    else:
        try:
            notification_time = (
                "{:02d}:{:02d}".format(*map(int, message_text.split(":")))
            )
            return time.fromisoformat(notification_time)
        except ValueError:
            raise NotCorrectTimeInput()
