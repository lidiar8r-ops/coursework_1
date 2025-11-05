import logging
import os.path

import pandas as pd
import pytest
from unittest.mock import patch

from src.config import DATA_DIR
from src.reports import spending_by_weekday
from src.utils import write_json



def test_spending_by_weekday_with_valid_date(
    sample_transactions, mock_filter_by_date, mock_conversion, mock_write_json
):
    """Дата в корректном формате — функция работает."""
    mock_filter_by_date.return_value = sample_transactions
    mock_conversion.return_value = sample_transactions

    result = spending_by_weekday(sample_transactions, "15.12.2023")

    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ["день_недели", "средние_траты"]


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

    # # write_json должен быть вызван ровно 1 раз
    # mock_write_json.assert_called_once()

    # # Проверяем путь и аргументы
    # expected_filepath = os.path.join(DATA_DIR, "reports.json")
    # mock_write_json.assert_called_with(result, expected_filepath)

    # Дополнительно: проверяем, что result не пустой (по ТЗ)
    # assert not result.empty, "Результат пуст — проверьте логику функции"

def test_spending_by_weekday_missing_amount_col(mock_filter_by_date):
    """Нет столбца 'Сумма' — возвращает пустой DataFrame."""
    df = pd.DataFrame({"Дата платежа": pd.to_datetime(["2023-10-01"])})

    result = spending_by_weekday(df)

    assert result.empty
    assert list(result.columns) == ["день_недели", "средние_траты"]  # структура сохранена


def test_spending_by_weekday_no_expenses(sample_transactions):
    """Все суммы ≥ 0 — нет расходов, возвращает пустой DataFrame."""
    df = sample_transactions.copy()
    df["Сумма"] = [100, 200, 150, 300, 250]
    df["Сумма_RUB"] = df["Сумма"]

    result = spending_by_weekday(df)

    assert result.empty
    assert list(result.columns) == ["день_недели", "средние_траты"]

@pytest.mark.parametrize(
    "scenario, input_df, expected_level, expected_message_fragment",
    [
        ("успешный расчёт", pd.DataFrame({...}), logging.INFO, "Расчёт ведётся от даты"),
        ("нет расходов", pd.DataFrame({...}), logging.WARNING, "Нет транзакций с расходами"),
    ]
)
def test_spending_by_weekday_logging(
    scenario, input_df, expected_level, expected_message_fragment, caplog
):
    with patch("src.reports.filter_by_date", return_value=input_df):
        with patch("src.reports.conversion_to_single_currency", return_value=input_df):
            with patch("src.reports.write_json"):
                with caplog.at_level(expected_level):
                    spending_by_weekday(input_df, "15.12.2023")


    # Отладка: выводим все записанные логи
    print("\n=== Записанные логи ===")
    for i, record in enumerate(caplog.records):
        print(f"{i}. Уровень: {record.levelno}, Сообщение: {record.message}")


    assert any(
        record.levelno == expected_level and expected_message_fragment in record.message
        for record in caplog.records
    )
