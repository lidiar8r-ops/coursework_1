from pandas import DataFrame

from src import app_logger

# Настройка логирования
logger = app_logger.get_logger("services.log")


def get_profitable_cashback(data: DataFrame, str_year: str, str_month: object) -> str:
    """позволяет проанализировать, какие категории были наиболее выгодными для выбора
    в качестве категорий повышенного кешбэка.
    :param data: данные с транзакциями;
    :param str_year: год, за который проводится анализ;
    :param str_month: месяц, за который проводится анализ.
    """
    # офильтровываем по году и месяцу
    #
    pass
