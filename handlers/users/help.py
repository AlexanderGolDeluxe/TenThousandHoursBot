from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import DISP


@DISP.message_handler(CommandHelp())
async def bot_help(message: types.Message):
	"""Отправляет сообщение со списком всех команд бота"""
	bot_commands: list[types.BotCommand] = (
		await message.bot.get_my_commands()
	)
	commands_joined = "\n".join(
		f"<pre>/{command.command}</pre> – {command.description}"
		for command in bot_commands
	)
	await message.answer("<b>Список команд:</b>\n" + commands_joined)
