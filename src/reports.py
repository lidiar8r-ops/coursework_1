import pandas as pd
from datetime import datetime, timedelta
from typing import Optional

from src import app_logger
from src.config import LIST_OPERATION
from src.utils import conversion_to_single_currency, filter_by_date, write_json

# Настройка логирования
logger = app_logger.get_logger("reports.log")


def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """
    Возвращает средние траты в каждый из дней недели за последние три месяца (от переданной даты).


    :param transactions: DataFrame с транзакциями. Должен содержать:
        - столбец с датой (предполагается "Дата платежа")
        - столбец с суммой (new_amount_col, например "Сумма")
    :param date: строка в формате "дд.мм.гггг" (опционально). Если не указана — берётся текущая дата.
    :return: DataFrame с колонками: "день_недели" (0–6), "средние_траты"
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
                return pd.DataFrame()  # Возвращаем пустой DataFrame при ошибке

        today_date = today_dt.date()
        logger.debug(f"Расчёт ведётся от даты: {today_date}")

        # Вычисление границы периода (последние 3 месяца) — вычитаем ~90 дней
        data_from = today_date - timedelta(days=90)
        data_to = today_date + timedelta(days=1)  # до конца текущего дня
        list_period = [data_from, data_to]
        logger.debug(f"Период анализа: {data_from} – {data_to}")

        # Фильтрация транзакций: только расходы (сумма < 0)
        if amount_col not in transactions.columns:
            logger.error(f"Столбец '{amount_col}' не найден в данных.")
            return pd.DataFrame()

        df_expenses = transactions[transactions[amount_col] < 0].copy()
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
            return pd.DataFrame()

        # Расчёт средних трат по дням недели
        result_df["день_недели"] = result_df["Дата платежа"].dt.weekday

        avg_spending = (
            result_df
            .groupby("день_недели", as_index=False)[new_amount_col]
            .mean()
            .round(2)
            .abs()
        )

        # Переименовываем колонку для ясности
        avg_spending.rename(columns={new_amount_col: "средние_траты"}, inplace=True)

        # Сортируем по дню недели
        avg_spending.sort_values("день_недели", inplace=True)

        days_of_week = [
            "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"
        ]
        # Создаём словарь: число → название дня
        day_map = {i: day for i, day in enumerate(days_of_week)}

        # Заменяем числа на строки
        avg_spending["день_недели"] = avg_spending["день_недели"].map(day_map)
        # print(avg_spending)
        logger.info(f"Рассчитаны средние траты по дням недели: {avg_spending.to_dict('records')}")

        # Запись результата в JSON
        write_json(avg_spending.to_dict('records'), "reportss.json")


        return avg_spending

    except Exception as e:
        logger.critical(f"Неожиданная ошибка в spending_by_weekday: {type(e).__name__}: {e}")
        return pd.DataFrame()
