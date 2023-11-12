import os
import sqlite3
import inspect
import requests
import telebot
from datetime import datetime
from dotenv import load_dotenv
from yandex_speechkit import auth_iam_token, get_s3_session, yandex_uploadfile, auth_speechkit, delete_file
from logger import get_logger, send_error_message


load_dotenv()
logger = get_logger()
TOKEN = os.getenv('test_token')
bot = telebot.TeleBot(TOKEN)

# Создаем обработчик для голосовых сообщений
@bot.message_handler(content_types=['voice'])
def reply_voice_message(message: telebot.types.Message):
    try:
        bot.send_message(message.chat.id, "Голосовое сообщение принято, пожалуйста, подождите немного, пока чат-бот обрабатывает ваш запрос . . .")

        file_info = bot.get_file(message.voice.file_id)  # Получаем информацию о файле
        tg_file_link = 'https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_info.file_path)  # Формируем ссылку на файл
        file = requests.get(tg_file_link)  # Отправляем запрос на получение файла

        # Сохраняем аудиофайл локально
        path_file = f"voices/voice{message.chat.id}_{datetime.now():%d-%m-%Y_%H-%M}.ogg"
        with open(path_file, 'wb') as f:
            f.write(file.content)

        IAM_TOKEN = auth_iam_token() # Получаем IAM_TOKEN
        s3 = get_s3_session() # Получаем сессию s3
        filelink = yandex_uploadfile(path_file, s3) # Загружаем аудиофайл на облако
        text = auth_speechkit(filelink, IAM_TOKEN) # Получаем распознанную речь

        # Отправляем сообщение с распознанной речью в Телеграм отправителю
        bot.send_message(message.chat.id, f"<b>Обработанная речь из сообщения:</b> \n\n{text}", parse_mode='HTML')

        delete_file(path_file, s3) # Удаляем ранее загруженный аудиофайл из облака
        os.remove(path_file) # Удаляем локальный аудиофайл

        # Делаем запись сообщения в базу данных
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO message(date, chat_id, username, link_tg_voice, speech_text) VALUES(?, ?, ?, ?, ?)", 
                    (datetime.now().strftime('%d %B %Y %H:%M:%S'), message.chat.id, message.from_user.username, tg_file_link, text))
        conn.commit()

        # Проверяем наличие пользователя в БД
        cursor.execute(f'SELECT id FROM users WHERE id = {message.chat.id}')
        rows = cursor.fetchall()
        if not rows:
            # Если пользователя нет в БД, то добавляем его
            cursor.execute("INSERT INTO users(id, username, first_name, last_name) VALUES(?, ?, ?, ?)", 
                        (message.from_user.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name))
            conn.commit()

        conn.close()

    except Exception as e:
        logger.error(e)
        send_error_message(os.path.basename(__file__), inspect.currentframe().f_code.co_name, e)

# Создаем обработчик для текстовых сообщений
@bot.message_handler(content_types=['text'])
def send_welcome(message):
    try:
        bot.send_message(message.chat.id, f"Этот бот умеет обрабатывать только голосовое сообщение.")

        # Делаем запись сообщения в БД
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO message(date, chat_id, username, text_mess) VALUES(?, ?, ?, ?)", 
                    (datetime.now().strftime('%d %B %Y %H:%M:%S'), message.chat.id, message.from_user.username, message.text))
        conn.commit()

        # Проверяем наличие пользователя в БД
        cursor.execute(f'SELECT id FROM users WHERE id = {message.chat.id}')
        rows = cursor.fetchall()
        if not rows:
            # Если пользователя нет в БД, то добавляем его
            cursor.execute("INSERT INTO users(id, username, first_name, last_name) VALUES(?, ?, ?, ?)", 
                        (message.from_user.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name))
            conn.commit()

        conn.close()

    except Exception as e:
        logger.error(e)
        send_error_message(os.path.basename(__file__), inspect.currentframe().f_code.co_name, e)


if __name__ == '__main__':
    while True:
        bot.polling(none_stop=True, interval=0)

