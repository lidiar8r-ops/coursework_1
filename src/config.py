# Настройки БД
import os

# from typing import Union
#
# DATABASE_URL = "sqlite:///app.db"
# MAX_CONNECTIONS = 10
#
# # Логирование
# LOG_LEVEL = "DEBUG"
# # LOG_FILE = "app.log"
#
# # # Функциональные флаги
# # DEBUG = True
# # ENABLE_CACHING = False

# Пути к файлам
current_dir = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(current_dir, ".."))
LOG_DIR = os.path.join(PARENT_DIR, "logs")
DATA_DIR = os.path.join(PARENT_DIR, "data")
# TEMP_DIR = os.path.join(CURRENT_DIR, "tmp")

# определим список с именем обрабатываемого файла (operations.xlsx) и его поля
LIST_OPERATION = [
    "operations_short.xlsx",
    [
        "Дата операции",
        "Дата платежа",
        "Номер карты",
        "Статус",
        "Сумма операции",
        "Валюта операции",
        "Сумма платежа",
        "Валюта платежа",
        "Кэшбэк",
        "Категория",
        "MCC",
        "Описание",
        "Бонусы (включая кэшбэк)",
        "Округление на инвесткопилку",
        "Сумма операции с округлением",
    ],
]
