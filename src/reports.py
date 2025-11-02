import pandas as pd


# траты по дням недели
def spending_by_weekday(transactions: pd.DataFrame,
                        date: Optional[str] = None) -> pd.DataFrame:
    """
    Функция возвращает средние траты в каждый из дней недели за последние три месяца (от переданной даты).
    :param transactions: датафрейм с транзакциями,
    :param date: опциональную дату
    """

    # фильтруем по периоду и статусу операции <<OK>> в результат result_list
    # вычисляем период
    if date is None:
        date = datetime.datetime.now()
    range_data_from = date -90 дней
    range_data_to = date

    # фильтруем по периоду и статусу операции <<OK>> в результат result_list

    # полученный список передаем в функцию с днем недели, где фильтруем и получаем среднее значение по дню
    # формируем  вывод в файл/консоль
    pass



