# YandexSpeechkitBot
**Сервис для распознавания голосовых сообщений в Telegram в виде бота**
____

## Описание структуры и файлов

**yandex_speechkit.py** - в файле описаны все функции для работы с сервисами Яндекса (облако, сервис распознавания речи)

**main.py** - файл для запуска telegram-бота

**logger.py** - файл для создания логера и функции оповещения об ошибках в telegram администратору


Скрытые файлы:

authorized_key.json - ключи сервисного аккаунта Yandex Cloud

data.db - файл базы данных для фиксации сообщений и пользователей


Скрытая директория:

voices - директория для временного хранения аудио-файлов голосовых сообщений
