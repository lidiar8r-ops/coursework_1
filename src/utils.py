import json
import os
import re
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Union

import pandas as pd
import requests
from dotenv import load_dotenv
from pandas import DataFrame

from src import app_logger
from src.config import DATA_DIR, LIST_OPERATION, URL_EXCHANGE, URL_EXCHANGE_SP_500

# import yfinance as yf

# Настройка логирования
logger = app_logger.get_logger("utils.log")


# Загрузка переменных из .env-файла,3
load_dotenv()
# headers = {"apikey": os.getenv("API_KEY")}
# headers_sp_500 = {
#     "apikey": os.getenv("API_KEY_SP_500"),
# }


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
            result_df = pd.read_excel(path_filename, engine="openpyxl")

        logger.info(f"Чтение данных из файла {os.path.basename(path_filename)} ")

        # Прверим, что все колонки присутствуют
        index_column = list_operation
        if len(result_df.columns) != len(index_column):
            logger.error(f"Ошибка в данных, отсутствует колонка {set(index_column) - set(result_df.columns)}")
            return pd.DataFrame()

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


def get_period_operation(str_date: str, range_data: str = "M") -> list:
    """
    Получает период и возвращает список даты с и по.
    :param str_date: дата в строковом виде (например, "19.05.2025")
    :param range_data: диапазон данных:
        "W" — неделя, на которую приходится дата;
        "M" — месяц, на который приходится дата (по умолчанию);
        "Y" — год, на который приходится дата;
        "ALL" — все данные до указанной даты.
    :return: список словарей (записи DataFrame)
    """
    # Проверка и нормализация входной даты
    if not str_date or str_date.strip() == "":
        logger.info("Дата не указана, берём текущую")
        str_date = datetime.now().strftime("%d.%m.%Y")

    try:
        # Преобразуем строку в объект datetime
        today_dt = datetime.strptime(str_date, "%d.%m.%Y")
        today_date = today_dt.date()  # работаем с датой (без времени)
    except ValueError as e:
        logger.error(f"Некорректный формат даты: {str_date}. Ошибка: {e}")
        str_date = datetime.now().strftime("%d.%m.%Y")
        return [str_date, str_date]

    # Нормализация range_data
    range_data = (range_data or "M").upper()

    #  Вычисление границы периода
    if range_data == "W":
        # Начало недели (понедельник )
        data_from = today_date - timedelta(days=today_date.weekday())
        # Конец диапазона: текущий день + 1 (чтобы включить текущий день полностью)
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

    return [data_from, data_to]


def filter_by_date(df: pd.DataFrame, list_period: List) -> DataFrame:
    """
    Фильтрует данные по периоду и возвращает список словарей.

    :param df: DataFrame с колонкой "Дата платежа" в формате ДД.ММ.ГГГГ
    :param list_period: список с периодами дат
    :return: список словарей (записи DataFrame)
    #"""
    #  Преобразование границ  с и по в pd.Timestamp для сравнения с datetime
    data_from_ts = pd.Timestamp(list_period[0])
    data_to_ts = pd.Timestamp(list_period[1])

    # Преобразование столбца "Дата платежа" в datetime
    try:
        df.loc[:, "Дата платежа"] = pd.to_datetime(
            df.loc[:, "Дата платежа"], format="%d.%m.%Y", errors="coerce"  # некорректные значения → NaT
        )
    except Exception as e:
        logger.error(f"Ошибка при преобразовании столбца 'Дата платежа': {e}")
        # return list_dict
        return pd.DataFrame()

    # Фильтрация
    mask = (df["Дата платежа"] >= data_from_ts) & (df["Дата платежа"] < data_to_ts)
    filtered_df = df.loc[mask]

    return filtered_df


def get_exchange_rate(carrency_code: str, target_currency: str = "RUB") -> float:
    """
    Для получения текущего курса валют
    принимает на вход название валюты, если валюта была не RUB, происходит обращение к внешнему API для получения
    текущего курса валют в рублях.
    :param carrency_code: из какой валюты
    :param target_currency: в какую валюту
    :return: сумму в рублях по курсу, тип данных —float.
    """
    carrency_code = carrency_code.upper()
    try:
        if carrency_code == target_currency:
            return 1
        else:
            response = requests.get(f"{URL_EXCHANGE}{os.getenv('API_KEY')}/pair/{carrency_code}/{target_currency}")
            # response.raise_for_status()
            # data = response.json()
            # return {
            #     "base": data["base"],
            #     "rates": data["rates"],
            #     "date": data["date"]
            # }

            # params_load = {"amount": 1, "from": carrency_code, "to": "RUB"}
            # response = requests.get(url=URL_EXCHANGE, params=params_load, headers=headers)

            if response.status_code == 200:
                try:
                    # return float(response.json()["result"])
                    return float(response.json()["conversion_rate"])
                except json.decoder.JSONDecodeError as e:
                    logger.error(f"Ошибка при получении курса валюты: {e}")
                    return 0
            else:
                logger.error(f" Ошибка статус - код: {str(response.status_code)}")
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
    #
    currency_col = LIST_OPERATION[2]
    amount_col = str(LIST_OPERATION[3])

    # Убедимся, что сумма — числовая
    if not pd.api.types.is_numeric_dtype(df[amount_col]):
        # try:
        df[amount_col] = pd.to_numeric(df[amount_col], errors="coerce")
        # except Exception as e:
        #     logger.error(f"Не удалось преобразовать столбец '{amount_col}' в число: {e}")
        #     return pd.DataFrame()

    # Создаём новый столбец для сумм  (dropna() исключает строки без указанной валюты)
    new_amount_col = f"{amount_col}_{target_currency}"
    # df[new_amount_col] = df[amount_col].copy()
    df = df.copy()
    df[new_amount_col] = df[amount_col]
    # df = df.assign(**{new_amount_col: df[amount_col]})

    # Получаем уникальные валюты в данных
    unique_currencies = df["Валюта платежа"].dropna().unique()

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


def get_data_from_expensess(df: pd.DataFrame) -> Dict:
    """
    Формирование раздела «Расходы»: суммирует отрицательные значения в колонке суммы (в RUB).

    :param df: DataFrame с колонкой суммы в RUB (например, 'Сумма_RUB')
    :return: список словарей с итоговыми расходами
    """
    # Название колонки с суммой в RUB
    new_amount_col = f"{LIST_OPERATION[3]}_RUB"
    category_col = LIST_OPERATION[4]

    # Проверка наличия колонки
    if new_amount_col not in df.columns:
        logger.error(f"Колонка '{new_amount_col}' не найдена в DataFrame")
        # raise KeyError(f"Колонка '{new_amount_col}' не найдена в DataFrame")
        return {}

    # Убедимся, что колонка — числовая
    if not pd.api.types.is_numeric_dtype(df[new_amount_col]):
        # try:
        df[new_amount_col] = pd.to_numeric(df[new_amount_col], errors="coerce")
        # except Exception as e:
        #     logger.error(f"Не удалось преобразовать колонку '{new_amount_col}' в число: {e}")
        #     # raise ValueError(f"Не удалось преобразовать колонку '{new_amount_col}' в число: {e}")
        #     return {}

    # Фильтруем отрицательные значения (расходы) и суммируем
    expenses = df.loc[df[new_amount_col] < 0, new_amount_col]
    sum_amount = expenses.sum()

    # вычисляем Сумму трат по каждой категориям, т.е. получаем уникальные категории
    unique_categories = df[df[new_amount_col] < 0]["Категория"].dropna().unique()

    result_list = []
    for category in unique_categories:
        df_category = df.loc[(df[new_amount_col] < 0) & (df[category_col] == category), new_amount_col]
        sum_amount_category = df_category.sum()
        result_list.append(
            {
                "category": category,
                "amount": round(sum_amount_category * (-1)),
            }
        )

    # берем только первые 7 категорий, остальные в категорию <<Остальное>>
    # Сортируем список по убыванию
    sorted_list = sorted(result_list, key=lambda x: x["amount"], reverse=True)

    if len(sorted_list) > 7:
        # осатвляем первые
        top_7 = sorted_list[:7]

        # Берём остальные (после 7‑го) и суммируем поле `amount`
        rest = sorted_list[7:]
        if rest:
            total_amount = sum(item["amount"] for item in rest)
            # Формируем итоговую запись
            summed_item = {"category": "Остальное", "amount": round(total_amount)}  # округляем до целого

            top_7.append(summed_item)

    else:
        top_7 = sorted_list

    # Формируем итоговый словарь
    result = {
        "expenses": {
            "total_amount": round(sum_amount * (-1)),  # общая сумма расходов (положительная)
            "main": top_7,  # топ-7 категорий + «Остальное»
        }
    }

    return result


def get_data_from_income(df: pd.DataFrame) -> Dict:
    """
    Формирование раздела «Поступления»: суммирует положительные значения в колонке суммы (в RUB).

    :param df: DataFrame с колонкой суммы в RUB (например, 'Сумма_RUB')
    :return: список словарей с итоговыми поступлениями
    """
    # Название колонки с суммой в RUB
    new_amount_col = f"{LIST_OPERATION[3]}_RUB"
    category_col = LIST_OPERATION[4]

    # Проверка наличия колонки
    if new_amount_col not in df.columns:
        logger.error(f"Колонка '{new_amount_col}' не найдена в DataFrame")
        # raise KeyError(f"Колонка '{new_amount_col}' не найдена в DataFrame")
        return {}

    # Убедимся, что колонка — числовая
    if not pd.api.types.is_numeric_dtype(df[new_amount_col]):
        # try:
        df[new_amount_col] = pd.to_numeric(df[new_amount_col], errors="coerce")
        # except Exception as e:
        #     logger.error(f"Не удалось преобразовать колонку '{new_amount_col}' в число: {e}")
        #     # raise ValueError(f"Не удалось преобразовать колонку '{new_amount_col}' в число: {e}")
        #     return {}

    # Фильтруем Положительные значения (доходы) и суммируем
    income = df.loc[df[new_amount_col] > 0, new_amount_col]
    sum_amount = income.sum()

    # вычисляем Сумму трат по каждой категориям, т.е. получаем уникальные категории
    unique_categories = df[df[new_amount_col] > 0]["Категория"].dropna().unique()

    result_list = []
    for category in unique_categories:
        df_category = df.loc[(df[new_amount_col] > 0) & (df[category_col] == category), new_amount_col]
        sum_amount_category = df_category.sum()
        result_list.append(
            {
                "category": category,
                "amount": round(sum_amount_category),
            }
        )

    # Сортируем список по убыванию
    sorted_list = sorted(result_list, key=lambda x: x["amount"], reverse=True)

    # Формируем итоговый словарь
    result = {
        "income": {
            "total_amount": round(sum_amount),  # общая сумма расходов (положительная)
            "main": sorted_list,  # топ-7 категорий + «Остальное»
        }
    }

    return result


def get_user_settings(file_path: str) -> Dict:
    """"""
    # считываем из file_path данные получаем словарь с данными data
    # Считываем существующие данные (если файл есть)
    data: dict[Any, Any] = {}

    if os.path.exists(file_path):

        try:
            with open(file_path, "r") as f:
                data = json.load(f)

        except Exception as e:
            logger.error(f"Ошибка {e}")
            return {}
    else:
        logger.error(f"файл {file_path} не найден")
        return {}

    return data


def get_currency_rates(dict_user: Dict) -> List[Dict]:
    """
    Функция получает курсы валют.

    :param dict_user: словарь с настройками пользователя, должен содержать:
        - "user_currencies": список валют (например, ["USD", "EUR"])
    :return: список словарей с полями 'currency' и 'rate'
    """
    stock_data: list[dict[str, Any]] = []  # Результат: данные по валютам

    # Список валют из настроек пользователя
    currencies = dict_user.get("user_currencies", [])
    if not currencies:
        logger.error("Ошибка: список валют 'user_currencies' не указан в настройках.")
        return stock_data

    # Получение курсов для каждой валюты
    for currency in currencies:
        try:
            exchange_rate = get_exchange_rate(currency)
            stock_data.append({"currency": currency, "rate": exchange_rate})
        except Exception as e:
            logger.error(f"Ошибка при получении курса для {currency}: {e}")
            continue  # Продолжаем обработку остальных валют

    return stock_data


def get_stock_price_sp_500(dict_user: dict) -> List[Dict]:
    """
    Функция получает через API FMP текущие цены указанных акций.
    Возвращает только тикер (stock) и цену (price).

    :param dict_user: словарь с настройками пользователя, должен содержать:
        - "user_stocks": список тикеров акций (например, ["AAPL", "MSFT"])
    :return: список словарей с полями 'stock' и 'price'
    """
    stock_data: list[dict[str, Any]] = []  # Результат: данные по акциям

    # Проверка API-ключа
    api_key = os.getenv("API_KEY_SP_500")
    if not api_key:
        logger.error("Ошибка: API_KEY_SP_500 не установлен в переменных окружения.")
        return stock_data

    # Список акций из настроек пользователя
    stocks = dict_user.get("user_stocks", [])
    if not stocks:
        logger.error("Ошибка: список акций 'user_stocks' не указан в настройках.")
        return stock_data

    for stock in stocks:
        # Нормализуем тикер
        symbol = stock.strip().upper()

        params = {"symbol": symbol, "apikey": api_key}

        try:
            response = requests.get(URL_EXCHANGE_SP_500, params=params, timeout=10)

            # Логируем URL для отладки
            # logger.info(f"Запрос к API: {response.url}")

            # Проверка HTTP‑статуса
            if response.status_code == 200:
                data = response.json()

                # FMP возвращает список объектов (даже для одного тикера)
                if isinstance(data, list) and len(data) > 0:
                    quote = data[0]  # Первый элемент списка — данные по акции
                    try:
                        exchange_rate = get_exchange_rate("USD")
                        price_from = quote["price"]
                        price = round(float(price_from * exchange_rate))
                        stock_data.append(
                            {
                                "stock": symbol,
                                # 'price_from': price_from,
                                # 'exchange_rate': exchange_rate,
                                "price": price,
                            }
                        )
                        logger.info(f"Акция {symbol}: цена {price}")
                    except (KeyError, ValueError) as e:
                        logger.error(f"Ошибка извлечения цены для {symbol}: {e}")
                else:
                    logger.warning(f"Данные по акции {symbol} не найдены в ответе API.")
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"HTTP‑ошибка для {symbol}: {error_msg}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса для {symbol}: {e}")
        except Exception as e:
            logger.critical(f"Неожиданная ошибка для {symbol}: {e}")

    return stock_data


def write_json(dict_wr: Union[Dict[str, Any], List[Dict[Any, Any]]], name_file: str = "answer.json") -> None:
    """
    Выводит в JSON‑файл все полученные данные по разделам.

    :param dict_wr: словарь с данными для записи. Ключи должны быть строками.
    :return: None
    """
    file_path = os.path.join(DATA_DIR, name_file)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(dict_wr, f, ensure_ascii=False, indent=4)
        logger.info(f"Данные успешно записаны в {file_path}")
    except (IOError, OSError) as e:
        logger.error(f"Ошибка при записи файла {file_path}: {e}")
        raise
    except TypeError as e:
        logger.error(f"Неподдерживаемый тип данных в словаре: {e}")
        raise

    return None
