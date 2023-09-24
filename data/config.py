from datetime import datetime

from environs import Env
from pytz import timezone

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Забираем значение типа str
ADMINS = env.list("ADMINS", subcast=int, delimiter=", ")  # Тут у нас список из админов
ADMIN_LINK = env.str("ADMIN_LINK")  # Строка со ссылкой на админа
TIME_ZONE = timezone(env.str("TIME_ZONE"))  # Тоже str, для определения часового пояса
datetime_now = lambda: datetime.now(TIME_ZONE)  # Текущее время относительно установленного часового пояса
