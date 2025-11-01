import datetime
import json
import logging
import os

from pandas import DataFrame

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
    if df is None:
        df = pd.DataFrame()
    elif not isinstance(df, pd.DataFrame):
        logger_views.error("df должен быть pandas.DataFrame")
    return

    if str_date is None:

        str_date = datetime.now().strftime("%Y%m%d")



    pass


############
# Вызов функции считывание данных из файла
data_list = get_list_operation(path_s, LIST_OPERATION[1])
print("=" * 20)
print(json.dumps(data_list, indent=4, ensure_ascii=False))

events_operations(data_list, "20.05.2020", "M")
