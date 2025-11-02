import os.path
import pandas as pd
from pandas import DataFrame

from src import app_logger
from src.config import DATA_DIR
from src.utils import conversion_to_single_currency, get_data_from_expensess, get_exchange_rate, get_data_receipt

logger = app_logger.get_logger("views.log")


def events_operations(df: DataFrame, str_date: str, range_data: str = "M") -> str:
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
    ###### СТРАНИЦА «СОБЫТИЯ»
    logger.info("Начало работы функции")

    if df is None:
        logger.info("Нет данных в файле")
        return f"Нет данных в файле"
    elif not isinstance(df, pd.DataFrame):
        logger.error("df должен быть pandas.DataFrame")

    # # Обработка полученных данных
    # фильтрация данных по периоду
    result_df = conversion_to_single_currency(df, "RUB")
    if result_df is None:
        logger.error("Не удачная попытка конвертации суммы платежа в RUB")
        return None

    # формирование раздела «Расходы»:
    result_list = get_data_from_expensess(df)

    # раздел «Поступления»:
    # из result_list получаем сумму поступлений по категориям и общую
    result_list.append(get_data_receipt(df))

    #######
    # считываем из user_settings.json данные получаем список с данными list_settings
    file_path = os.path.join(DATA_DIR, "user_settings.json")

    list_settings = ''
    # Считываем существующие данные (если файл есть)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                list_settings = json.load(f)
        except Exception as e:
            logger.error(f"Ошибка {e}")
            list_settings = []
    else:
        list_settings = []
        logger.error(f'файл {file_path} не найден')

    if list_settings !=[]:
        # раздел «Курс валют»0:
        get_data_receipt = get_data_receipt(df, list_settings)

    # раздел «Стоимость акций из S&P 500>>
    # получаем через api данные акций (указанных в list_settings) на дату текущую

    #######
    # выводим в json файл все полученные данные по разделам

    # вывод в консоль об окончании отработки функции и что получен такой-то файл.json
    logger.info("Завершение работы функции")
    return result_list
