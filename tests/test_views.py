import pandas as pd
from unittest.mock import patch
import pytest

from src.views import events_operations


# Тестовые данные
@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "Дата платежа": ["2025-01-01", "2025-01-02"],
        "Сумма платежа": [100, 200],
        "Категория": ["Продукты", "Одежда"],
        "Валюта платежа": ["USD", "RUB"],
    })
# "Тип операции": ["Расход", "Поступление"]

# Тест на корректную работу функции
def test_events_operations(sample_data):
    """
    Тест на корректную работу функции events_operations.
    """
    # Запускаем функцию
    result = events_operations(sample_data, "2025-01-01")

    # Проверяем, что результат не пустой
    assert result is not None, "Результат должен быть не пустым"

    # Проверяем наличие ключевых разделов в результате
    assert "expenses" in result, "Раздел 'expenses' должен быть в результате"
    assert "income" in result, "Раздел 'income' должен быть в результате"
    assert "currency_rates" in result, "Раздел 'currency_rates' должен быть в результате"
    assert "stock_prices" in result, "Раздел 'stock_prices' должен быть в результате"

# Тест на обработку ошибки при отсутствии данных
def test_events_operations_no_data():
    """
    Тест на обработку ошибки при отсутствии данных.
    """
    # Запускаем функцию с пустым DataFrame
    result = events_operations(None, "2025-01-01")

    # Проверяем, что результат содержит сообщение об ошибке
    assert result == "Нет данных в файле", "Должно быть сообщение об ошибке"

# Тест на обработку ошибки при некорректном типе данных
def test_events_operations_incorrect_type(faulty_data):
    """
    Тест на обработку ошибки при некорректном типе данных.
    """
    # Запускаем функцию с некорректным типом данных
    result = events_operations(faulty_data, "2025-01-01")

    # Проверяем, что результат содержит сообщение об ошибке
    assert result is None, "Должно быть сообщение об ошибке"