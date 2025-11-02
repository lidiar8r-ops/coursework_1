import os

import pandas as pd

from src import app_logger
from src.config import DATA_DIR, LIST_OPERATION
from src.services import get_profitable_cashback
from src.utils import get_list_operation
from src.views import events_operations

path_s = os.path.join(DATA_DIR, LIST_OPERATION[0])
logger = app_logger.get_logger("main.log")


if __name__ == '__main__':
    logger.info("Начало работы программы")

    # Вызов функции считывание данных из файла
    logger.info("вызов функции считывание данных из файла get_list_operation")
    df = get_list_operation(path_s, LIST_OPERATION[1])
    if df is None or len(df) == 0:
        logger.error("Нет данных для дальнейшей обработки")
    elif not isinstance(df, pd.DataFrame):
        logger.error("df должен быть pandas.DataFrame")
    else:
        # Вызов функции события events_operations
        logger.info("вызов функции events_operations для формирования раздела События")
        result = events_operations(df, "20.05.2020", "M")
        # print("=" * 20)

        # Вызов функции события get_profitable_cashback
        logger.info("вызов функции get_profitable_cashback для формирования раздела События")
        result = get_profitable_cashback(df, "2020", "5")
        # print("=" * 20)
        # print(json.dumps(result, indent=4, ensure_ascii=False))
        # print("=" * 20)

    logger.info("Завершение работы программы")
