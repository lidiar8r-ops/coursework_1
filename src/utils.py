import os
import re

import pandas as pd
from typing import Dict, List

from pandas import DataFrame

from src import app_logger

# Настройка логирования
logger = app_logger.get_logger("utils.log")

def get_list_operation(path_filename: str, list_operation: list, filter_str: str = 'Статус') -> DataFrame:
    """
    Функция читает файл CSV или Excel, преобразовывая содержимое в словарь и сформировать список словарей
    :param path_filename: путь к файлу CSV или XLX, XLSX
    :return: словарь с данными
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

        result_df = result_df.loc[result_df[filter_str] == "OK"]
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



def filter_list(input_list: List[Dict], fields: str = "Категория") -> List[Dict]:
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




def get_currency_exchange(transaction: dict) -> float:
    """
    принимает на вход транзакцию и возвращает сумму транзакции (amount) в рублях, тип данных —float.
    Если транзакция была в USD или EUR, происходит обращение к внешнему API для получения текущего курса валют и
    конвертации суммы операции в рубли.
    :param transaction: транзакция
    :return: сумма транзакции
    """
#{
#   "expenses": {
#     "total_amount": 32101,
#     "main": [
#       {
#         "category": "Супермаркеты",
#         "amount": 17319
#       },
#       {
#         "category": "Фастфуд",
#         "amount": 3324
#   },
#       {
#         "category": "Топливо",
#         "amount": 2289
#       },
#       {
#         "category": "Развлечения",
#         "amount": 1850
#       },
#       {
#         "category": "Медицина",
#         "amount": 1350
#       },
#       {
#         "category": "Остальное",
#         "amount": 2954
#       }
#     ],
#     "transfers_and_cash": [
#       {
#         "category": "Наличные",
#         "amount": 500
#       },
#       {
#         "category": "Переводы",
#         "amount": 200
#       }
#     ]
#   },
#   "income": {
#     "total_amount": 54271,
#     "main": [
#       {
#         "category": "Пополнение_BANK007",
#         "amount": 33000
#       },
#       {
#         "category": "Проценты_на_остаток",
#         "amount": 1242
#       },
#       {
#         "category": "Кэшбэк",
#         "amount": 29
#       }
#     ]
#   },
#   "currency_rates": [
#     {
#       "currency": "USD",
#       "rate": 73.21
#     },
#     {
#       "currency": "EUR",
#       "rate": 87.08
#     }
#   ],
#   "stock_prices": [
#     {
#       "stock": "AAPL",
#       "price": 150.12
#     },
#     {
#       "stock": "AMZN",
#       "price": 3173.18
#     },
#     {
#       "stock": "GOOGL",
#       "price": 2742.39
#     },
#     {
#       "stock": "MSFT",
#       "price": 296.71
#     },
#     {
#       "stock": "TSLA",
#       "price": 1007.08
#     }
#   ]
# }
    try:
        carrency_code = transaction.get("operationAmount", {}).get("currency", {}).get("code", "")
        if carrency_code == "RUB":
            return float(transaction.get("operationAmount", {}).get("amount", 0))
        else:
            amount_transaction = transaction.get("operationAmount", {}).get("amount", 0)
            if not amount_transaction == 0:
                params_load = {"amount": amount_transaction, "from": carrency_code, "to": "RUB"}
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
            else:
                return 0
    except Exception as e:
        raise (e)

