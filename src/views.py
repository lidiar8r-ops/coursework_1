import os.path

import pandas as pd
from pandas import DataFrame

from src import app_logger
from src.config import DATA_DIR
from src.utils import (conversion_to_single_currency, filter_by_date, get_currency_rates, get_data_from_expensess,
                       get_data_from_income, get_period_operation, get_stock_price_sp_500, get_user_settings,
                       write_json)

logger = app_logger.get_logger("views.log")


def events_operations(df: DataFrame, str_date: str, range_data: str = "M") -> dict:
    """Реализуйте набор функций и главную функцию, принимающую на вход строку с датой и второй .
    Цифры по тратам и поступлениям округлите до целых.
    @param str_date: дата в строков виде
    @param range_data: необязательный параметр — диапазон данных.
        По умолчанию диапазон равен одному месяцу (с начала месяца, на который выпадает дата, по саму дату)
        Возможные значения второго необязательного параметра:
        W - неделя, на которую приходится дата;
        M - месяц, на который приходится дата;
        Y - год, на который приходится дата;
        ALL - все данные до указанной даты.
    @param range_data:
    return: JSON-ответ, который содержит следующие данные:
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
    #  СТРАНИЦА «СОБЫТИЯ»
    logger.info("Начало работы функции")

    if df is None:
        logger.info("Нет данных в файле")
        return "Нет данных в файле"
    elif not isinstance(df, pd.DataFrame):
        logger.error("df должен быть pandas.DataFrame")
        return "Нет данных"

    # # Обработка полученных данных
    # фильтрация данных по периоду
    list_period = get_period_operation(str_date, range_data)
    result_df_p = filter_by_date(df, list_period)

    # получаем сумму платежа в рублях
    result_df = conversion_to_single_currency(result_df_p, "RUB")
    if result_df is None:
        logger.error("Не удачная попытка конвертации суммы платежа в RUB")
        return None

    # формирование раздела «Расходы»:
    result_dict = get_data_from_expensess(result_df)

    # раздел «Поступления»:
    # из df получаем сумму поступлений по категориям и общую
    result_dict["income"] = get_data_from_income(result_df)

    #######
    dict_settings = get_user_settings(os.path.join(DATA_DIR, "user_settings.json"))

    if dict_settings == {}:
        logger.error("Файл с настройками для пользователя пуст или не существует (подробнее в файле utils.log)")
    else:
        # раздел «Курс валют»:
        list_receipt = get_currency_rates(dict_settings)
        result_dict["currency_rates"] = list_receipt

        # раздел «Стоимость акций из S&P 500>>
        list_receipt = get_stock_price_sp_500(dict_settings)
        result_dict["stock_prices"] = list_receipt

    # получаем через api данные акций (указанных в list_settings) на дату текущую

    #######
    # выводим в json файл все полученные данные по разделам
    write_json(result_dict)

    # вывод в консоль об окончании отработки функции и что получен такой-то файл.json
    print("Завершение работы функции - получен файл answer.json")
    logger.info("Завершение работы функции - получен answer.json")
    return result_dict
