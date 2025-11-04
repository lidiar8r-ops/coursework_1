import pandas as pd

from src import app_logger
from src.utils import conversion_to_single_currency, filter_by_date

# Настройка логирования
logger = app_logger.get_logger("services.log")

# траты по дням недели
def spending_by_weekday(transactions: pd.DataFrame,
                        date: Optional[str] = None) -> pd.DataFrame:
     """
    Возвращает средние траты в каждый из дней недели за последние три месяца (от переданной даты).

    :param transactions: DataFrame с транзакциями. Должен содержать:
        - столбец с датой (предполагается "Дата платежа")
        - столбец с суммой (new_amount_col, например "Сумма")
    :param date: строка в формате "дд.мм.гггг" (опционально). Если не указана — берётся текущая дата.
    :return: DataFrame с колонками: "день_недели" (0–6), "средние_траты"
    """
    try:
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

        # Вычисление границы периода (последние 3 месяца) вычитаем ~90 дней
        data_from = today_date - timedelta(days=90)
        data_to = today_date + timedelta(days=1)  # до конца текущего дня
        logger.debug(f"Период анализа: {data_from} – {data_to}")

        # отфильтровать данные по тратам
        df_expenses = df.loc[df[new_amount_col] < 0, new_amount_col]
        # отфильтровать данные с и по
        filter_by_date(df_expenses, list_period)

    # перевести валютные платежи в рубли
    result_df = conversion_to_single_currency(result_df_p, "RUB")

    if result_df is None:
        logger.error("Не удачная попытка конвертации суммы платежа в RUB")
        return None

    # полученный список передаем фильтруем по дню недели и получаем среднее значение по дню
    for _ to range(7):

        if len(df_expenses) == 0:
    # формируем  вывод в файл/консоль

    return result_df



