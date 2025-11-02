import os
import re
from datetime import date, datetime, timedelta
from typing import Dict, List

import pandas as pd
import requests
from dotenv import load_dotenv
from pandas import DataFrame

from src import app_logger
from src.config import LIST_OPERATION, URL_EXCHANGE

# Настройка логирования
logger = app_logger.get_logger("utils.log")


# Загрузка переменных из .env-файла,3
load_dotenv()
headers = {"apikey": os.getenv("API_KEY")}


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

    # 4. Преобразование границ  с и по в pd.Timestamp для сравнения с datetime
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


def get_exchange_rate(carrency_code: str, target_currency: str = "RUB") -> float:
    """
    Для получения текущего курса валют
    принимает на вход название валюты, если валюта была не RUB, происходит обращение к внешнему API для получения
    текущего курса валют в рублях.
    :param transaction: название валюты
    :return: сумму в рублях по курсу, тип данных —float.
    """
    carrency_code = carrency_code.upper()
    try:
        if carrency_code == target_currency:
            return 1
        else:
            params_load = {"amount": 1, "from": carrency_code, "to": "RUB"}
            response = requests.get(url=URL_EXCHANGE, params=params_load, headers=headers)
            # print(response)
            if response.status_code == 200:
                try:
                    return float(response.json()["result"])
                except json.decoder.JSONDecodeError as e:
                    logger.error(f"Ошибка при получении курса валюты: {e}")
                    return 0
            else:
                print(f" Ошибка статус - код: {str(response.status_code)}")
                return 0

    except Exception as e:
        logger.error(f"Ошибка при получении курса валюты: {e}")
        return 0


def conversion_to_single_currency(df: pd.DataFrame, target_currency: str = "RUB") -> pd.DataFrame:
    """
    Преобразует суммы платежей в единую валюту (по умолчанию — RUB).
    :param df: DataFrame с транзакциями. Должен содержать столбцы:
        - LIST_OPERATION[2] — код валюты (например, 'USD', 'EUR')
        - LIST_OPERATION[3] — сумма платежа (числовой тип)
    :param target_currency: целевая валюта для конвертации (по умолчанию 'RUB')
    :return: DataFrame с пересчитанными суммами в целевой валюте
    """
    # Проверяем наличие нужных столбцов
    currency_col = LIST_OPERATION[2]
    amount_col = LIST_OPERATION[3]

    # Убедимся, что сумма — числовая
    if not pd.api.types.is_numeric_dtype(df[amount_col]):
        try:
            df[amount_col] = pd.to_numeric(df[amount_col], errors='coerce')
        except Exception as e:
            logger.error(f"Не удалось преобразовать столбец '{amount_col}' в число: {e}")
            return None

    # Создаём новый столбец для сумм  (dropna() исключает строки без указанной валюты)
    new_amount_col = f"{amount_col}_{target_currency}"
    df[new_amount_col] = df[amount_col].copy()

    # Получаем уникальные валюты в данных
    unique_currencies = df[currency_col].dropna().unique()

    for currency in unique_currencies:
        if currency == target_currency:
            # Если валюта уже в RUB — ничего не делаем
            continue

        try:
            # Получаем курс конвертации (get_exchange_rate возвращает число)
            rate = get_exchange_rate(currency, target_currency)
            if pd.isna(rate) or rate <= 0:
                logger.error(f"Недопустимый курс для валюты {currency}: {rate}")

            # Конвертируем суммы для данной валюты
            mask = df[currency_col] == currency
            df.loc[mask, new_amount_col] = df.loc[mask, amount_col] * rate

        except Exception as e:
            logger.error(f"Ошибка при конвертации валюты {currency}: {e}")
            # Оставляем исходные значения для проблемных строк
            continue

    return df


def get_data_from_expensess(df: pd.DataFrame) -> List[Dict]:
    """
    Формирование раздела «Расходы»: суммирует отрицательные значения в колонке суммы (в RUB).

    :param df: DataFrame с колонкой суммы в RUB (например, 'Сумма_RUB')
    :return: список словарей с итоговыми расходами
    """
    # Название колонки с суммой в RUB
    new_amount_col = f"{LIST_OPERATION[3]}_RUB"

    # Проверка наличия колонки
    if new_amount_col not in df.columns:
        logger.error(f"Колонка '{new_amount_col}' не найдена в DataFrame")
        # raise KeyError(f"Колонка '{new_amount_col}' не найдена в DataFrame")
        return []

    # Убедимся, что колонка — числовая
    if not pd.api.types.is_numeric_dtype(df[new_amount_col]):
        try:
            df[new_amount_col] = pd.to_numeric(df[new_amount_col], errors='coerce')
        except Exception as e:
            logger.errorr(f"Не удалось преобразовать колонку '{new_amount_col}' в число: {e}")
            # raise ValueError(f"Не удалось преобразовать колонку '{new_amount_col}' в число: {e}")
            return []

    # Фильтруем отрицательные значения (расходы) и суммируем
    expenses = df.loc[df[new_amount_col] < 0, new_amount_col]
    sum_amount = expenses.sum()

    # вычисляем Сумму трат по каждой категориям, т.е. получаем уникальные категории
    unique_categories = df[LIST_OPERATION[4]].dropna().unique()

    result_list = []
    for category in unique_categories:
        df_category = df.loc[df[new_amount_col] < 0, new_amount_col]
        sum_amount_category = df_category.sum()
        result_list.append({
            "category": category,
            "amount": round(sum_amount_category * (-1)),
        })

    # берем только первые 7 категорий, остальные в категорию <<Остальное>>
    # Сортируем список по убыванию
    sorted_list = sorted(result_list, key=lambda x: x["amount"], reverse=True)

    if len(sorted_list) >7:
        # осатвляем первые
        top_7 = sorted_list[:7]

        # Берём остальные (после 7‑го) и суммируем поле `amount`
        rest = sorted_list[7:]
        if rest:
            total_amount = sum(item["amount"] for item in rest)
            # Формируем итоговую запись
            summed_item = {
                "category": "Остальное",
                "amount": round(total_amount)  # округляем до целого
            }

            top_7.append(summed_item)

    else:
        top_7 = sorted_list

    # Формируем результат как список словарей
    result = [
        {
            "expenses": {
            "total_amount": round(sum_amount * (-1)),
            "main": top_7,
        }}
    ]

    return result


def get_data_receipt(df: DataFrame, list_settings: list) -> List[Dict]:
    """
    Функция получает через api данные курса валют (указанных в list_settings) на дату текущую
    и формирует сумму поступлений по категориям и общую
    :param df:
    :param df:
    """
    # из result_list получаем сумму поступлений по категориям и общую
    return []

