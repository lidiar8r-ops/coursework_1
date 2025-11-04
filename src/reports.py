from datetime import datetime, timedelta
from typing import Optional
import pandas as pd

from src import app_logger
from src.config import LIST_OPERATION
from src.utils import conversion_to_single_currency, filter_by_date, write_json

# Настройка логирования
logger = app_logger.get_logger("reports.log")


def spending_by_weekday(
    transactions: pd.DataFrame,
    date: Optional[str] = None
) -> pd.DataFrame:
    """
    Возвращает средние траты в каждый из дней недели за последние три месяца (от переданной даты).

    :param transactions: DataFrame с транзакциями. Должен содержать:
        - столбец с датой (предполагается "Дата платежа")
        - столбец с суммой (new_amount_col, например "Сумма")
    :param date: строка в формате "дд.мм.гггг" (опционально). Если не указана — берётся текущая дата.
    :return: DataFrame с колонками: "день_недели", "средние_траты"
    """
    try:
        new_amount_col = f"{LIST_OPERATION[3]}_RUB"
        amount_col = LIST_OPERATION[3]

        # Проверка входной даты
        if not date or not date.strip():
            logger.info("Дата не указана, берём текущую")
            today_dt = datetime.now()
        else:
            try:
                today_dt = datetime.strptime(date, "%d.%m.%Y")
            except ValueError as e:
                logger.error(f"Некорректный формат даты: {date}. Ошибка: {e}")
                return pd.DataFrame(columns=["день_недели", "средние_траты"])

        today_date = today_dt.date()
        logger.debug(f"Расчёт ведётся от даты: {today_date}")

        # Вычисление границы периода (последние 3 месяца)
        data_from = today_date - pd.DateOffset(months=3)
        data_to = today_date + timedelta(days=1)  # до конца текущего дня
        list_period = [data_from, data_to]
        logger.debug(f"Период анализа: {data_from} – {data_to}")

        # Фильтрация транзакций: только расходы (сумма < 0)
        if amount_col not in transactions.columns:
            logger.error(f"Столбец '{amount_col}' не найден в данных.")
            return pd.DataFrame(columns=["день_недели", "средние_траты"])

        df_expenses = transactions[transactions[amount_col] < 0]
        if df_expenses.empty:
            logger.warning("Нет транзакций с расходами за указанный период.")
            return pd.DataFrame(columns=["день_недели", "средние_траты"])

        # Фильтрация по периоду
        df_filtered = filter_by_date(df_expenses, list_period)
        if df_filtered.empty:
            logger.warning("Нет расходов за последние 3 месяца.")
            return pd.DataFrame(columns=["день_недели", "средние_траты"])

        # Конвертация в RUB (если нужно)
        result_df = conversion_to_single_currency(df_filtered, "RUB")
        if result_df is None or result_df.empty:
            logger.error("Не удалось конвертировать суммы в RUB.")
            return pd.DataFrame(columns=["день_недели", "средние_траты"])

        # Расчёт дня недели
        result_df["день_недели"] = result_df["Дата платежа"].dt.weekday

        # Группировка и расчёт среднего (гарантируем DataFrame)
        avg_spending = (
            result_df
            .groupby("день_недели", as_index=False)
            [new_amount_col]
            .mean()
            .round(2)
            .abs()
        )

        # Переименование колонки (без inplace)
        # avg_spending = avg_spending.rename(columns={new_amount_col: "средние_траты"})
        avg_spending = avg_spending.assign(средние_траты=avg_spending[new_amount_col])
        avg_spending = avg_spending[["день_недели", "средние_траты"]]  # оставляем только нужные столбцы

        # Сортировка (без inplace)
        avg_spending = avg_spending.sort_values(by="день_недели")

        # Маппинг чисел на названия дней
        days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        day_map = {i: day for i, day in enumerate(days_of_week)}
        avg_spending["день_недели"] = avg_spending["день_недели"].map(day_map)

        logger.info("Рассчитаны средние траты по дням недели")

        # Явное указание типа (для mypy)
        result_dataframe: pd.DataFrame = avg_spending.copy()

        # Преобразование в словарь (исправленный orient)
        result_dict = result_dataframe.to_dict(orient="records")

        # Запись результата в JSON
        write_json(result_dict, "reports.json")

        return result_dataframe

    except Exception as e:
        logger.critical(f"Неожиданная ошибка в spending_by_weekday: {type(e).__name__}: {e}")
        return pd.DataFrame(columns=["день_недели", "средние_траты"])
