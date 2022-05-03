from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


MAIN_KEYBOARD_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Мои результаты")],
        [KeyboardButton(text="Добавить часы")],
        [KeyboardButton(text="Добавить ещё навык")],
        [KeyboardButton(text="Удалить навык")],
        [KeyboardButton(text="Настроить напоминание")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Выберите действие или запустите команду"
)
