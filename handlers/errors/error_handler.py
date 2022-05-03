import logging
from aiogram.types.update import Update
from aiogram.utils.exceptions import (
    TelegramAPIError,
    MessageNotModified,
    CantParseEntities)

from loader import DISP
from handlers.errors.exceptions import (
    NotCorrectInput,
    NotCorrectTimeInput)


@DISP.errors_handler()
async def errors_handler(update: Update, exception):
    """
    Exceptions handler. Catches all exceptions within task factory tasks.
    :param dispatcher:
    :param update:
    :param exception:
    :return: stdout logging
    """


    if isinstance(exception, NotCorrectInput):
        await update.message.answer(
            "Вы ввели неверные данные.\n"
            "Пожалуйста, повторите ввод")
        return True

    if isinstance(exception, NotCorrectTimeInput):
        await update.message.answer(
            "Вы ввели время неверно.\n"
            "Проследите за тем, чтобы оно было в диапазоне"
            "<code> 00:00-23:59 </code>и повторите ввод")
        return True

    if isinstance(exception, MessageNotModified):
        logging.exception('Message is not modified')
        # do something here?
        return True
      
    if isinstance(exception, CantParseEntities):
        # or here
        logging.exception(f'CantParseEntities: {exception} \nUpdate: {update}')
        return True
      
    #  MUST BE THE  LAST CONDITION (ЭТО УСЛОВИЕ ВСЕГДА ДОЛЖНО БЫТЬ В КОНЦЕ)
    if isinstance(exception, TelegramAPIError):
        logging.exception(f'TelegramAPIError: {exception} \nUpdate: {update}')
        return True
    
    # At least you have tried.
    logging.exception(f'Update: {update} \n{exception}')
