import datetime
import json
import logging
import os

import pandas as pd
from pandas import DataFrame, period_range

from src.config import DATA_DIR, LIST_OPERATION, PARENT_DIR
from src.utils import get_list_operation


# Формируем абсолютный путь к папке log (которая находится на уровень выше)
LOG_DIR = os.path.join(PARENT_DIR,  "logs")
log_file_path = os.path.join(LOG_DIR, "views.log")

# Настройка логирования
logger_views = logging.getLogger("views")
file_handler_views = logging.FileHandler(log_file_path, "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler_views.setFormatter(file_formatter)
logger_views.addHandler(file_handler_views)
logger_views.setLevel(logging.DEBUG)

path_s = os.path.join(DATA_DIR, LIST_OPERATION[0])


def events_operations(df : DataFrame, str_date: str, range_data: str = "M") -> str:
    """Реализуйте набор функций и главную функцию, принимающую на вход строку с датой и второй .
    Цифры по тратам и поступлениям округлите до целых.
    @param str_date: необязательный параметр — диапазон данных.
        По умолчанию диапазон равен одному месяцу (с начала месяца, на который выпадает дата, по саму дату)
        Возможные значения второго необязательного параметра:
        W - неделя, на которую приходится дата;
        M - месяц, на который приходится дата;
        Y - год, на который приходится дата;
        ALL - все данные до указанной даты.
    @param range_data: JSON-ответ содержит следующие данные:
        «Расходы»:
            Общая сумма расходов.
            Раздел «Основные», в котором траты по категориям отсортированы по убыванию. Данные предоставляются по 7
            категориям с наибольшими тратами, траты по остальным категориям суммируются и попадают в категорию
            «Остальное».
            Раздел «Переводы и наличные», в котором сумма по категориям «Наличные» и «Переводы» отсортирована
            по убыванию.
        «Поступления»:
            Общая сумма поступлений.
            Раздел «Основные», в котором поступления по категориям отсортированы по убыванию.
        Курс валют.
        Стоимость акций из S&P 500.
    """
    ###### СТРАНИЦА «СОБЫТИЯ»
    df = get_list_operation(path_s, LIST_OPERATION[1])

    if df is None:
        logger_views.info("Нет данных в файле")
        return f"Нет данных в файле"
    elif not isinstance(df, pd.DataFrame):
        logger_views.error("df должен быть pandas.DataFrame")


    # # Обработка полученных данных
    list_dict = df.to_dict(orient="records")

    if str_date is None:
        logger_views.error("не указана ")
        str_date = datetime.now().strftime("%d-%m-%Y")

    # вычисляем период
    if range_data is None:
        range_data = "M"
    if range_data == "W":
    elif range_data = "M":
    elif range_data = "Y"
    else:
        range_data_from
        range_data_to

    # раздел «Расходы»:




    return list_dict




############
# Вызов функции считывание данных из файла
result = events_operations("20.05.2020", "M")
# print("=" * 20)
# print(json.dumps(result, indent=4, ensure_ascii=False))
# print("=" * 20)