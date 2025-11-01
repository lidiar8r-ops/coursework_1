import logging
import os
import re

import pandas as pd
from typing import Any, Dict, List
from src.config import DATA_DIR


# Получаем директорию текущего файла (т.е. папку src)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Формируем абсолютный путь к папке log (которая находится на уровень выше)
LOG_DIR = os.path.join(CURRENT_DIR, "..", "logs")
log_file_path = os.path.join(LOG_DIR, "utils.log")

# Настройка логирования
logger_utils = logging.getLogger("utils")
file_handler_utils = logging.FileHandler(log_file_path, "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler_utils.setFormatter(file_formatter)
logger_utils.addHandler(file_handler_utils)
logger_utils.setLevel(logging.DEBUG)



def get_list_operation(path_filename: str, list_operation: list) -> list:
    """
    Функция читает файл CSV или Excel, преобразовывая содержимое в словарь и сформировать список словарей
    :param path_filename: путь к файлу CSV или XLX, XLSX
    :return: словарь с данными
    """
    result_list: List[Dict[str, Any]] = []
    try:
        # Проверка существования файла
        if not os.path.isfile(path_filename):
            logger_utils.error(f"Не найден файл {path_filename}")
            return result_list

        # Проверка расширения файла
        extension = os.path.splitext(path_filename)[1].upper()
        pattern = r"\.(XLS|XLSX|CSV)"

        if not re.search(pattern, extension, re.IGNORECASE):
            logger_utils.error(f"Файл {os.path.basename(path_filename)} не соответствует расширению CSV или XLSX,XLX")
            return result_list

        # Выбор способа открытия файла
        if extension == ".CSV":
            df = pd.read_csv(path_filename, delimiter=",")
        else:
            df = pd.read_excel(path_filename)

        logger_utils.info(f"Чтение данных из файла {os.path.basename(path_filename)} ")

        # print(df.columns)

        # Прверим, что все колонки присутствуют
        index_column = list_operation
        if len(df.columns) != len(index_column):
            logger_utils.error(f"Ошибка в данных, отсутствует колонка {set(index_column) - set(df.columns)}")
            return result_list

        # Преобразование прочитанного в словарь
        dict_df_get = df.to_dict(orient="records")
        logger_utils.info("Преобразование прочитанного в словарь")

        # Если файл только с заголовками, а данных нет
        if len(dict_df_get) == 0:
            logger_utils.error(f"Нет информации в файле {path_filename} ")
            return result_list

        # # Обработка полученных данных
        result_list = df.to_dict(orient="records")

        logger_utils.info("Сформирован список словарей с транзакциями")
        return result_list

    except ValueError as e:
        logger_utils.error(e)
        return result_list

    except Exception as ex:
        logger_utils.error(f"Необработанная ошибка: {ex}")
        return result_list
