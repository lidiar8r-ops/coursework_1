from typing import Dict

import pandas as pd
from pandas import DataFrame

from src import app_logger
from src.config import LIST_OPERATION
from src.utils import write_json

# Настройка логирования
logger = app_logger.get_logger("services.log")


def get_profitable_cashback(data: DataFrame, str_year: str, str_month: str) -> Dict[str, float]:
    """
    Анализирует, какие категории были наиболее выгодными для выбора
    в качестве категорий повышенного кэшбэка.

    :param data: DataFrame с транзакциями. Должен содержать столбцы:
        - "Дата платежа" (datetime или преобразуемый в datetime)
        - "Кэшбэк" (числовой, >= 0)
        - LIST_OPERATION[4] (название категории, str)
    :param str_year: год для анализа (строка, например "2025")
    :param str_month: месяц для анализа (строка, например "11")
    :return: словарь {категория: сумма кэшбэка}, отсортированный по убыванию.
             Пустой dict, если данных нет.
    """
    try:
        logger.info(f"Начало анализа кэшбэка за {str_year}-{str_month}. " f"Всего транзакций: {len(data)}")

        # Преобразование строк в числа
        try:
            year = int(str_year)
            month = int(str_month)
        except ValueError as e:
            logger.error(f"Некорректный формат года/месяца: {str_year}, {str_month}. Ошибка: {e}")
            raise ValueError("Год и месяц должны быть числовыми строками.") from e

        logger.debug(f"Преобразовано: year={year}, month={month}")

        # преобразование столбца "Дата платежа"
        if not pd.api.types.is_datetime64_any_dtype(data["Дата платежа"]):
            logger.info("Столбец 'Дата платежа' не в формате datetime — выполняем преобразование.")
            try:
                data["Дата платежа"] = pd.to_datetime(data["Дата платежа"], dayfirst=True, errors="raise")
            except Exception as e:
                logger.error(f"Ошибка преобразования 'Дата платежа' в datetime: {e}")
                return {}

        # Фильтрация: год, месяц и положительный кэшбэк
        mask = (data["Дата платежа"].dt.year == year) & (data["Дата платежа"].dt.month == month) & (data["Кэшбэк"] > 0)
        filtered_data = data.loc[mask].copy()  # копирование

        logger.info(f"Отфильтровано транзакций за {year}-{month} с кэшбэком > 0: {len(filtered_data)}")

        if filtered_data.empty:
            logger.warning("Нет транзакций с кэшбэком за указанный период.")
            return {}

        # Работа с категориальным столбцом
        category_col = LIST_OPERATION[4]

        # Группировка и суммирование кэшбэка
        cashback_by_category = filtered_data.groupby(category_col, as_index=False)["Кэшбэк"].sum().round(0)

        # Сортировка по убыванию и преобразование в словарь
        cashback_by_category.sort_values("Кэшбэк", ascending=False, inplace=True)
        dict_result = cashback_by_category.set_index(category_col)["Кэшбэк"].to_dict()

        logger.info(f"Найдено категорий с кэшбэком: {len(dict_result)}")
        # logger.info(f"Результаты анализа кэшбэка: {dict_result}")
        write_json(dict_result, "cashback.json")

        return dict_result

    except (ValueError, KeyError, TypeError) as e:
        logger.error(f"Ошибка при анализе кэшбэка: {type(e).__name__}: {e}")
        return {}

    except Exception as e:
        logger.critical(f"Неожиданная ошибка в get_profitable_cashback: {e}")
        return {}
