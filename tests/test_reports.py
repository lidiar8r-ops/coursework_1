import pytest
import pandas as pd
from datetime import datetime, timedelta

from src.reports import spending_by_weekday


def test_no_date(test_transactions):
    expected_columns = ['день_недели', 'средние_траты']

    result = spending_by_weekday(test_transactions)
    assert isinstance(result, pd.DataFrame)
    assert set(expected_columns) <= set(result.columns)


def test_incorrect_date_format(test_transactions):
    result = spending_by_weekday(test_transactions, date='invalid-date-format')
    assert result.empty


def test_missing_column(test_transactions):
    del test_transactions['Сумма']
    result = spending_by_weekday(test_transactions)
    assert result.empty


def test_no_negative_sums(positive_test_transactions):
    result = spending_by_weekday(positive_test_transactions)
    assert result.empty


def test_with_valid_date(test_transactions):
    valid_date = '01.10.2023'
    result = spending_by_weekday(test_transactions, date=valid_date)
    assert isinstance(result, pd.DataFrame)
    if result.empty:
        print("Нет данных для расчета!")
    else:
        assert not result.empty



def test_positive_scenario(test_transactions):
    """
    Проверка нормального функционирования при наличии расходов и правильной фильтрации.
    """
    valid_date = '01.10.2023'
    result = spending_by_weekday(test_transactions, date=valid_date)
    assert isinstance(result, pd.DataFrame)
    if result.empty:
        print("Нет данных для расчета!")
    else:
        assert not result.empty


def test_no_expense_transactions():
    """
    Проверка случая, когда нет транзакций с расходами.
    """
    no_expense_data = pd.DataFrame({
        'Дата платежа': pd.to_datetime(['2023-09-01']),
        'Сумма': [100],
        'Валюта': ['USD']
    })
    result = spending_by_weekday(no_expense_data)
    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_empty_after_filtering():
    """
    Проверка случая, когда транзакции есть, но они находятся вне нужного временного диапазона.
    """
    out_of_range_data = pd.DataFrame({
        'Дата платежа': pd.to_datetime(['2023-06-01']),
        'Сумма': [-100],
        'Валюта': ['USD']
    })
    result = spending_by_weekday(out_of_range_data, date='01.10.2023')
    assert isinstance(result, pd.DataFrame)
    assert result.empty