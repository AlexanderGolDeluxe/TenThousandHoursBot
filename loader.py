import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data import config

LOOP = asyncio.get_event_loop()
BOT = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
STORAGE = MemoryStorage()
DISP = Dispatcher(BOT, storage=STORAGE, loop=LOOP)
