import os
from unittest.mock import patch
import pandas as pd
import pytest
from src.reports import spending_by_weekday


@pytest.mark.parametrize("date_input, expected_result", [
    ('invalid-date-format', True),
    ('2023-09-04', False)
])
def test_invalid_date_formats(date_input, expected_result, test_transactions):
    result = spending_by_weekday(test_transactions, date=date_input)
    if expected_result:
        assert result.empty
    else:
        assert isinstance(result, pd.DataFrame)


def test_missing_column(test_transactions):
    del test_transactions['Сумма платежа']
    result = spending_by_weekday(test_transactions)
    assert result.empty


def test_no_negative_sums(positive_test_transactions):
    result = spending_by_weekday(positive_test_transactions, date='2023-09-04')
    assert result.empty


def test_valid_date_processing(positive_test_transactions):
    valid_date = '31.10.2023'
    result = spending_by_weekday(positive_test_transactions, date=valid_date)
    assert isinstance(result, pd.DataFrame)
    assert not result.empty  # Изменён порядок проверки


def test_no_expense_transactions():
    no_expense_data = pd.DataFrame({
        'Дата платежа': pd.to_datetime(['2023-09-01']),
        'Сумма платежа': [100],
        'Сумма платежа_RUB': [100],
        'Валюта платежа': ['RUB']
    })
    result = spending_by_weekday(no_expense_data)
    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_out_of_range_transactions():
    out_of_range_data = pd.DataFrame({
        'Дата платежа': pd.to_datetime(['2023-06-01']),
        'Сумма платежа': [-100],
        'Валюта платежа': ['USD']
    })
    result = spending_by_weekday(out_of_range_data, date='01.10.2023')
    assert isinstance(result, pd.DataFrame)
    assert result.empty


@patch('src.reports.conversion_to_single_currency')
def test_conversion_failure(mocked_function,sample_transactions):
    # Возвращаем пустой DataFrame при вызове замещенной функции
    mocked_function.return_value = pd.DataFrame()

    # Запуск основной функции
    result = spending_by_weekday(sample_transactions, "05.11.2025")

    # Проверка результатов
    assert isinstance(result, pd.DataFrame), "Результат должен быть объектом DataFrame."
    assert result.empty, "DataFrame должен быть пустым."
    expected_columns = ["день_недели", "средние_траты"]
    assert list(
        result.columns) == expected_columns, \
        f"Структура столбцов должна соответствовать {expected_columns}. Фактическое значение: {result.columns}"


def test_weekday_calculation():
    test_dates = ['2023-08-01', '2023-08-02', '2023-08-03']
    expected_days = [1, 2, 3]
    result = pd.Series(pd.to_datetime(test_dates)).dt.weekday.tolist()
    assert expected_days == result


def test_grouping_and_avg_calculation():
    data = {
        'Дата платежа': ['2023-08-01', '2023-08-02', '2023-08-03'],
        "Сумма платежа_RUB": [-100, -200, -300],
    }
    df = pd.DataFrame(data)
    df['Дата платежа'] = pd.to_datetime(df['Дата платежа'])
    df['день_недели'] = df['Дата платежа'].dt.weekday

    result = (
        df.groupby('день_недели')["Сумма платежа_RUB"].mean().reset_index().assign(
            средние_траты=lambda x: abs(x["Сумма платежа_RUB"])
        ).drop(columns=['Сумма платежа_RUB']).sort_values(by='день_недели')
    )

    expected_result = pd.DataFrame({
        'день_недели': [1, 2, 3],
        'средние_траты': [100., 200., 300.]
    })
    pd.testing.assert_frame_equal(expected_result, result, check_dtype=False)


def test_column_selection():
    result = pd.DataFrame({'день_недели': [], 'средние_траты': []})
    expected_columns = ['день_недели', 'средние_траты']
    assert set(expected_columns) == set(result.columns)


def test_day_mapping():
    test_data = {'Дата платежа': ['2023-08-01', '2023-08-02', '2023-08-03'], 'Сумма': [-100, -200, -300]}
    df = pd.DataFrame(test_data)
    df['Дата платежа'] = pd.to_datetime(df['Дата платежа'])
    df['день_недели'] = df['Дата платежа'].dt.weekday

    days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    day_map = {i: day for i, day in enumerate(days_of_week)}
    mapped_days = df['день_недели'].map(day_map).tolist()
    expected_mapped_days = ['Вторник', 'Среда', 'Четверг']
    assert mapped_days == expected_mapped_days


#  проверка обработки неожиданного исключения
@patch("src.reports.filter_by_date", side_effect=Exception("Исключение фильтрации"))
def test_unexpected_exception_returns_empty_df(mock_filter, sample_transactions):
    """
    Тест проверяет обработку Неожиданная ошибка в spending_by_weekday.
    Ожидаемый результат — pd.DataFrame(columns=["день_недели", "средние_траты"])
    """
    # Запуск основной функции
    result = spending_by_weekday(sample_transactions, "05.11.2025")

    # Проверки
    assert isinstance(result, pd.DataFrame), "Результатом должна быть таблица (DataFrame)."
    assert result.empty, "Таблица должна быть пустой."
    expected_columns = ["день_недели", "средние_траты"]
    assert list(result.columns) == expected_columns, f"Список столбцов должен содержать {expected_columns}."
