import os
import re
from datetime import date, datetime, timedelta
from typing import Dict, List

import pandas as pd
from pandas import DataFrame

from src import app_logger

# Настройка логирования
logger = app_logger.get_logger("utils.log")


def get_list_operation(
    path_filename: str, list_operation: list, filter_str: str = "OK", name_field: str = "Статус"
) -> DataFrame:
    """
    Функция читает файл CSV или Excel, и передает полученный FataFrame
    :param path_filename: путь к файлу CSV или XLX, XLSX
    :param list_operation: список обязательных полей
    :param filter_str: статус операции, по умолчанию "OK"
    :param name_field: имя колонки, по умолчанию "Статус"
    :return: DataFrame словарь с данными
    """
    result_df: DataFrame = pd.DataFrame()
    try:
        # Проверка существования файла
        if not os.path.isfile(path_filename):
            logger.error(f"Не найден файл {path_filename}")
            return result_df

        # Проверка расширения файла
        extension = os.path.splitext(path_filename)[1].upper()
        pattern = r"\.(XLS|XLSX|CSV)"

        if not re.search(pattern, extension, re.IGNORECASE):
            logger.error(f"Файл {os.path.basename(path_filename)} не соответствует расширению CSV или XLSX,XLX")
            return result_df

        # Выбор способа открытия файла
        if extension == ".CSV":
            result_df = pd.read_csv(path_filename, delimiter=",")
        else:
            result_df = pd.read_excel(path_filename)

        logger.info(f"Чтение данных из файла {os.path.basename(path_filename)} ")

        # Прверим, что все колонки присутствуют
        index_column = list_operation
        if len(result_df.columns) != len(index_column):
            logger.error(f"Ошибка в данных, отсутствует колонка {set(index_column) - set(result_df.columns)}")
            return result_df

        # Если файл только с заголовками, а данных нет
        if len(result_df) == 0:
            logger.error(f"Нет информации в файле {path_filename} ")
            return result_df

        # фильтруем полученный df по столбцу с заданным параметром
        result_df = result_df.loc[result_df[name_field] == filter_str]

        logger.info("Получение DataFrame")
        return result_df

    except ValueError as e:
        logger.error(e)
        return result_df

    except Exception as ex:
        logger.error(f"Необработанная ошибка: {ex}")
        return result_df


def get_date(date_str: str) -> str:
    """
    функция, которая принимает на вход строку с датой и возвращает строку с датой
    :param date_str: строка с датой в формате "2024-03-11T02:26:18.671407"
    :rtype: str возвращает строку с датой в формате "ДД.ММ.ГГГГ" ("11.03.2024").
    """
    try:
        formatted_datetime = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        # formatted_datetime = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        logger_widget.error(f"Не соответствует формату даты {date_str}")
        # raise ValueError("Не соответствует формату даты")
        return ""
    except TypeError:
        logger_widget.error(f"Не соответствует формату даты {date_str}")
        # raise TypeError("Не соответствует типу даты")
        # logger_widget.info("Невозможно декодировать JSON-данные")
        return ""

    return formatted_datetime.strftime("%d.%m.%Y")


def filter_by_date(df: pd.DataFrame, str_date: str, range_data: str = "M") -> DataFrame:
    """
    Фильтрует данные по периоду и возвращает список словарей.

    :param df: DataFrame с колонкой "Дата платежа" в формате ДД.ММ.ГГГГ
    :param str_date: дата в строковом виде (например, "19.05.2025")
    :param range_data: диапазон данных:
        "W" — неделя, на которую приходится дата;
        "M" — месяц, на который приходится дата (по умолчанию);
        "Y" — год, на который приходится дата;
        "ALL" — все данные до указанной даты.
    :return: список словарей (записи DataFrame)
    """
    # list_dict: List[Dict] = []

    # 1. Проверка и нормализация входной даты
    if not str_date or str_date.strip() == "":
        logger.info("Дата не указана, берём текущую")
        str_date = datetime.now().strftime("%d.%m.%Y")

    try:
        # Преобразуем строку в объект datetime
        today_dt = datetime.strptime(str_date, "%d.%m.%Y")
        today_date = today_dt.date()  # работаем с датой (без времени)
    except ValueError as e:
        logger.error(f"Некорректный формат даты: {str_date}. Ошибка: {e}")
        return df

    # 2. Нормализация range_data
    range_data = (range_data or "M").upper()

    # 3. Вычисление границы периода
    if range_data == "W":
        # Начало недели (понедельник)
        start_of_week = today_date - timedelta(days=today_date.weekday())
        data_from = start_of_week
        data_to = today_date + timedelta(days=1)

    elif range_data == "M":
        # Начало месяца
        data_from = date(today_date.year, today_date.month, 1)
        data_to = today_date + timedelta(days=1)

    elif range_data == "Y":
        # Начало года
        data_from = date(today_date.year, 1, 1)
        data_to = today_date + timedelta(days=1)

    else:  # "ALL"
        # Берём очень раннюю дату как нижнюю границу
        data_from = date(1800, 1, 1)
        data_to = today_date + timedelta(days=1)

    # 4. Преобразование границ в pd.Timestamp для сравнения с datetime64[ns]
    data_from_ts = pd.Timestamp(data_from)
    data_to_ts = pd.Timestamp(data_to)

    # 5. Преобразование столбца "Дата платежа" в datetime
    try:
        df["Дата платежа"] = pd.to_datetime(
            df["Дата платежа"], format="%d.%m.%Y", errors="coerce"  # некорректные значения → NaT
        )
    except Exception as e:
        logger.error(f"Ошибка при преобразовании столбца 'Дата платежа': {e}")
        # return list_dict
        return list_dict

    # 6. Фильтрация
    mask = (df["Дата платежа"] >= data_from_ts) & (df["Дата платежа"] < data_to_ts)
    filtered_df = df.loc[mask]

    # # 7. Преобразование в список словарей
    # list_dict = filtered_df.to_dict(orient="records")

    return filtered_df
    # return list_dict


def get_exchange_rate(carrency_code: str) -> float:
    """
    Для получения текущего курса валют
    принимает на вход название валюты, если валюта была не RUB, происходит обращение к внешнему API для получения
    текущего курса валют в рублях.
    :param transaction: название валюты
    :return: сумму в рублях по курсу, тип данных —float.
    """
    carrency_code = carrency_code.upper()
    try:
        if carrency_code == "RUB":
            return 1
        else:
            params_load = {"amount": 1, "from": carrency_code, "to": "RUB"}
            response = requests.get(url=url, params=params_load, headers=headers)
            # print(response)
            if response.status_code == 200:
                try:
                    return float(response.json()["result"])
                except json.decoder.JSONDecodeError as e:
                    raise (e)
            else:
                print(f" Ошибка статус - код: {str(response.status_code)}")
                return 0

    except Exception as e:
        logger.error(f"Ошибка при получении курса валюты: {e}")
        return 0


def filter_by_category(input_list: List[Dict], fields: str = "Категория") -> List[Dict]:
    """
    функция фильтрует список словарей по значение ключа и возвращает новый список словарей
    :param input_list: список словарей
    :param fields:  опционально значение для ключа fields, по умолчанию 'Категория'
    :return: list  возвращает список словарей, содержащий только те словари, у которых ключ fields соответствует
    указанному значению.
    """
    field = fields.upper()
    for current_dict in input_list:
        if field not in current_dict.keys():
            logger_processing.error(f"Не найден ключ {fields} для транзакции {current_dict}")

    return [current_dict for current_dict in input_list if current_dict.get(field, {}) == field]


def sort_by_date(input_list: List[Dict], sorting: bool = True) -> List[Dict]:
    """
    Возвращает список словарей, отсортированный по дате.
    :param input_list: список словарей, каждый должен содержать ключ "date" со строкой в формате
    ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)
    :param sorting: порядок сортировки (True — убывание, False — возрастание)
    :return: отсортированный по дате список словарей
    """
    for current_dict in input_list:
        if "date" not in current_dict.keys():
            logger_processing.error(f"Не найден ключ date для транзакции {current_dict}")
            # raise KeyError("В словаре не удалось найти ключ date")

        if not isinstance(current_dict.get("date"), str):
            logger_processing.error(f"Ошибка типа данных в транзакции {current_dict}")
            # raise TypeError("Ошибка типа данных")

        try:
            if datetime.fromisoformat(current_dict.get("date", "").replace("Z", "+00:00")) is None:
                logger_processing.error(
                    f"Не соответствует формату даты {str(current_dict.get('date'))} в транзакции {current_dict}"
                )
        except ValueError:
            logger_processing.error(
                f"Не соответствует формату даты {str(current_dict.get('date'))} в транзакции {current_dict}"
            )
            # raise ValueError("Не соответствует формату даты")

    return sorted(input_list, key=lambda current_dict: current_dict.get("date", ""), reverse=sorting)
