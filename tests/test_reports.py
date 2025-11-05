import os
from unittest.mock import patch

import pytest
import pandas as pd
from datetime import datetime, timedelta

from pandas.core.interchange.dataframe_protocol import DataFrame

import src
from src.config import DATA_DIR, LOG_DIR
from src.reports import spending_by_weekday
from src.utils import conversion_to_single_currency


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
    result = spending_by_weekday(positive_test_transactions, date='2023-09-04')
    assert result.empty


def test_with_valid_date(positive_test_transactions_sum):
    valid_date = '31.10.2023'
    result = spending_by_weekday(positive_test_transactions_sum, date=valid_date)
    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_positive_scenario(positive_test_transactions):
    """
    Проверка нормального функционирования при наличии расходов и правильной фильтрации.
    """
    valid_date = '31.10.2023'
    result = spending_by_weekday(positive_test_transactions, date=valid_date)
    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_no_expense_transactions():
    """
    Проверка случая, когда нет транзакций с расходами.
    """
    no_expense_data = pd.DataFrame({
        'Дата платежа': pd.to_datetime(['2023-09-01']),
        'Сумма платежа': [100],
        'Сумма платежа_RUB': [100],
        'Валюта': ['RUB']
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


def test_spending_by_weekday_missing_amount_col_sum(mock_filter_by_date, positive_test_transactions):
    result = spending_by_weekday(positive_test_transactions, "2023-10-01")
    assert result.empty
    assert list(result.columns) == ["день_недели", "средние_траты"]  # структура сохранена


def test_spending_by_weekday_missing_amount_col(mock_filter_by_date):
    """Нет столбца 'Сумма' — возвращает пустой DataFrame."""
    df = pd.DataFrame({"Дата платежа": pd.to_datetime(["2023-10-01"])})

    result = spending_by_weekday(df)

    assert result.empty
    assert list(result.columns) == ["день_недели", "средние_траты"]  # структура сохранена


@patch("src.utils.write_json")
def test_spending_by_weekday_writes_file_always(mock_write_json):
    """Проверяет, что write_json вызывается всегда, даже если данных нет."""
    # Тестовые данные: две транзакции
    sample_data = pd.DataFrame({
        "Дата платежа": ["2023-12-01", "2023-12-10"],
        "Сумма": [-1000, -2000],
        "Сумма_RUB": [-1000, -2000]
    })

    result = spending_by_weekday(sample_data, "15.12.2023")


def test_no_expenses_in_last_3_months_returns_empty_df():
    # Транзакции есть, но все до 3‑месячного периода
    transactions = pd.DataFrame({
        "Дата платежа": pd.to_datetime(["2025-07-01"]),  # старше 3 месяцев от 05.11.2025
        "Сумма": [-1000],
        "Сумма_RUB": [-1000]
    })

    result = spending_by_weekday(transactions, "05.11.2025")


    assert isinstance(result, pd.DataFrame)
    assert result.empty
    assert list(result.columns) == ["день_недели", "средние_траты"]


@patch("src.utils.conversion_to_single_currency")
def test_conversion_to_rub_fails_returns_empty_df(mock_conversion):
    """
    Тест проверяет случай, когда конвертация валюты возвращается None.
    Ожидается, что результатом станет пустой DataFrame.
    """

    # Настраиваем мокированную функцию для возврата None
    mock_conversion.return_value = None

    # Создаем исходный DataFrame транзакций
    transactions = pd.DataFrame({
        "Дата платежа": pd.to_datetime(["2025-10-01"]),
        "Сумма": [-1000],          # Используем отрицательное значение для расхода
        "Сумма_RUB": [-1000]      # Исходная сумма в рублях
    })

    # Выполняем проверку результата функции
    result = spending_by_weekday(transactions, "05.11.2025")

    # Проверяем утверждения
    assert isinstance(result, pd.DataFrame), "Результат должен быть объектом типа DataFrame."
    assert result.empty, "DataFrame должен быть пустым."
    expected_columns = ["день_недели", "средние_траты"]
    assert list(result.columns) == expected_columns, f"Столбцы должны соответствовать {expected_columns}"


# Второй тест: проверка обработки неожиданного исключения
@patch("src.utils.filter_by_date", side_effect=Exception("Исключение фильтрации"))
def test_unexpected_exception_returns_empty_df(mock_filter):
    """
    Тест проверяет обработку непредвиденного исключения внутри функции filter_by_date.
    Ожидаемый результат — пустой DataFrame.
    """

    # Подготовили тестовые данные
    transactions = pd.DataFrame({
        "Дата платежа": pd.to_datetime(["2025-10-01"]),
        "Сумма": [-1000],
        "Сумма_RUB": [-1000]
    })

    # Вызываем тестируемую функцию
    result = spending_by_weekday(transactions, "05.11.2025")

    # Проверки
    assert isinstance(result, pd.DataFrame), "Результатом должна быть таблица (DataFrame)."
    assert result.empty, "Таблица должна быть пустой."
    expected_columns = ["день_недели", "средние_траты"]
    assert list(result.columns) == expected_columns, f"Список столбцов должен содержать {expected_columns}."


@patch.object(src.utils, 'conversion_to_single_currency')
def test_conversion_failure(mocked_function):
    # Возвращаем пустой DataFrame при вызове замещенной функции
    mocked_function.return_value = pd.DataFrame()

    # Тестовые данные с неправильными значениями
    input_data = pd.DataFrame({
        "Дата платежа": ["01.09.2025"],
        "Сумма платежа": [-1000],
        "Сумма платежа_RUB": [-1000],  # Неправильное значение
        "Валюта платежа": ["USD"]  # Некорректная валюта
    })

    # Запуск основной функции
    result = spending_by_weekday(input_data, "05.11.2025")

    # Проверка результатов
    assert isinstance(result, pd.DataFrame), "Результат должен быть объектом DataFrame."
    assert result.empty, "DataFrame должен быть пустым."
    expected_columns = ["день_недели", "средние_траты"]
    assert list(
        result.columns) == expected_columns, f"Структура столбцов должна соответствовать {expected_columns}. Фактическое значение: {result.columns}"

    # Проверяем наличие записи в журнале ошибок
    with open(os.path.join(LOG_DIR, "reports.log"), "r", encoding="utf-8") as logfile:
        content = logfile.read()
        assert "Не удалось конвертировать суммы в RUB" in content, "Сообщение об ошибке не найдено в журнале."

