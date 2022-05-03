from aiogram import Dispatcher

from loader import DISP
from .throttling import ThrottlingMiddleware


if __name__ == "middlewares":
    DISP.middleware.setup(ThrottlingMiddleware())
