from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Забираем значение типа str
ADMINS = env.list("ADMINS", subcast=int, delimiter=", ")  # Тут у нас список из админов
ADMIN_LINK = env.str("ADMIN_LINK")  # Строка со ссылкой на админа
IP = env.str("ip")  # Тоже str, но для IP-адреса хоста
