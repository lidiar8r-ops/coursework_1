import json
import os

import pandas as pd

from src import app_logger
from src.config import DATA_DIR, LIST_OPERATION
from src.reports import spending_by_weekday
from src.services import get_profitable_cashback
from src.utils import get_list_operation
from src.views import events_operations

path_s = os.path.join(DATA_DIR, LIST_OPERATION[0])
logger = app_logger.get_logger("main.log")


if __name__ == '__main__':
    logger.info("Начало работы программы")

    # Вызов функции считывание данных из файла и фильтруем по статусу операции <<OK>>
    print(f"Считывание данных из файла {LIST_OPERATION[0]}")
    logger.info(f"Считывание данных из файла {LIST_OPERATION[0]}\n")

    df = get_list_operation(path_s, LIST_OPERATION[1])

    if df is None or len(df) == 0:
        logger.error("Нет данных для дальнейшей обработки")

    elif not isinstance(df, pd.DataFrame):
        logger.error("df должен быть pandas.DataFrame")

    else:
        # Вызов функции события events_operations
        print("=" * 20, "Формирование раздела События")
        logger.info("вызов функции events_operations для формирования раздела События")
        try:
            result = events_operations(df, "20.05.2020", "Y")

            print(json.dumps(result, indent=4, ensure_ascii=False))
            if result is None:
                logger.error("Ошибка функции events_operations для раздела События")
        except Exception as e:
                logger.error(f"Ошибка функции events_operations для раздела События - {e}")

        # Вызов функции анадиз повышенного кешбека get_profitable_cashback
        logger.info("вызов функции get_profitable_cashback анализ повышенного кешбека для формирования раздела Сервисы")
        print("=" * 20, "Выгодные категории повышенного кешбэка:")
        result = get_profitable_cashback(df, "2019", "10")
        print(json.dumps(result, indent=4, ensure_ascii=False))

        print("=" * 20, "Траты по дням недели:")
        result = spending_by_weekday(df,"01.01.2022")
        print(json.dumps(result.to_dict('records'), indent=4, ensure_ascii=False))

    print("Завершение работы программы")
    logger.info("Завершение работы программы")
