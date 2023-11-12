import os
import logging
import logging.handlers
import telebot
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()

def get_logger() -> logging.Logger:
    logger_ = logging.getLogger("exception_logger")
    logger_.setLevel(level=logging.INFO)

    # Создаем форматтер
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Создаем обработчик
    file_handler = logging.handlers.RotatingFileHandler(f"logs.log", maxBytes=3000, backupCount=0)
    file_handler.setLevel(logging.INFO)

    # Назначаем форматтер обработчику
    file_handler.setFormatter(formatter)

    logger_.addHandler(file_handler)

    return logger_


# Уведомление администратору в телеграм от технического бота при появлении ошибок в функциях
def send_error_message(module_name, func_name, e):
    bot = telebot.TeleBot(token=os.getenv('tg_notif_token'))
    text_message = f"""
<b>ERROR</b>: {os.getenv("app_title")}

<b>date</b>: {datetime.now():%d.%m.%Y %H:%M}
<b>module</b>: {module_name}
<b>func</b>: {func_name}

{e}
    """

    bot.send_message(os.getenv('tg_admin'), text_message, parse_mode='HTML')

