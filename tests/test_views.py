import pandas as pd
from unittest.mock import patch, Mock
import pytest

from src.views import events_operations


# Тестовые данные
@pytest.fixture
def sample_data_views():
    return pd.DataFrame({
        "Дата платежа": pd.to_datetime(["2025-01-01", "2025-01-02"]),
        "Сумма платежа": [-100, 200],
        "Категория": ["Продукты", "Одежда"],
        "Валюта платежа": ["USD", "RUB"],
        "Сумма платежа_RUB": [-8122.03, 200],
    })

# Тест на корректную работу функции
@patch('src.views.conversion_to_single_currency')
@patch('src.views.get_currency_rates')
@patch('src.views.get_stock_price_sp_500')
def test_events_operations(mocked_stock_price, mocked_currency_rates, mocked_conversion, sample_data_views):
    """
    Тест на корректную работу функции events_operations.
    """
    # Создаем заглушки для функций
    mocked_conversion.return_value = sample_data_views  # Возвращаем исходные данные
    mocked_currency_rates.return_value = [{"currency": "USD", "rate": 81.2203}, {"currency": "EUR", "rate": 93.4094}]
    mocked_stock_price.return_value = [{"stock": "AAPL", "price": 443}, {"stock": "AMZN", "price": 13556},
                                       {"stock": "GOOGL", "price": 22101}, {"stock": "MSFT", "price": 22101},
                                       {"stock": "TSLA", "price": 237}]

    # Запускаем функцию
    result = events_operations(sample_data_views, "2025-01-01")
    print(result)
    # Проверяем, что результат не пустой
    assert result is not None, "Результат должен быть не пустым"

    # Проверяем наличие ключевых разделов в результате
    assert "expenses" in result, "Раздел 'expenses' должен быть в результате"
    assert "income" in result, "Раздел 'income' должен быть в результате"
    assert "currency_rates" in result, "Раздел 'currency_rates' должен быть в результате"
    assert "stock_prices" in result, "Раздел 'stock_prices' должен быть в результате"

    # Проверяем, что функции были вызваны
    mocked_conversion.assert_called_once()
    mocked_currency_rates.assert_called_once()
    mocked_stock_price.assert_called_once()


# Тест на обработку ошибки при отсутствии данных
@patch('src.views.conversion_to_single_currency')
@patch('src.views.get_currency_rates')
@patch('src.views.get_stock_price_sp_500')
def test_events_operations_no_data(mocked_stock_price, mocked_currency_rates, mocked_conversion):
    """
    Тест на обработку ошибки при отсутствии данных.
    """
    # Создаем заглушки для функций
    mocked_conversion.return_value = sample_data_views  # Возвращаем исходные данные
    mocked_currency_rates.return_value = [{"currency": "USD", "rate": 81.2203}, {"currency": "EUR", "rate": 93.4094}]
    mocked_stock_price.return_value = [{"stock": "AAPL", "price": 443}, {"stock": "AMZN", "price": 13556},
                                       {"stock": "GOOGL", "price": 22101}, {"stock": "MSFT", "price": 22101},
                                       {"stock": "TSLA", "price": 237}]

    # Запускаем функцию с пустым DataFrame
    result = events_operations(None, "2025-01-01")

    # Проверяем, что результат содержит сообщение об ошибке
    assert result == "Нет данных в файле", "Должно быть сообщение об ошибке"


# Тест на обработку ошибки при некорректном типе данных
@patch('src.views.conversion_to_single_currency')
@patch('src.views.get_currency_rates')
@patch('src.views.get_stock_price_sp_500')
def test_events_operations_incorrect_type(mocked_stock_price, mocked_currency_rates, mocked_conversion):
    """
    Тест на обработку ошибки при некорректном типе данных.
    """
    # Запускаем функцию с некорректным типом данных
    result = events_operations(None, "01.01.2025")

    # # Проверяем, что результат содержит сообщение об ошибке
    # assert result is None, "Должно быть сообщение об ошибке"

    # Проверка результатов
    assert isinstance(result, pd.DataFrame), "Результат должен быть объектом DataFrame."
    assert result.empty, "DataFrame должен быть пустым."


# Тест на обработку ошибки при неудачной конвертации
@patch('src.views.conversion_to_single_currency', return_value=None)
@patch('src.views.get_currency_rates')
@patch('src.views.get_stock_price_sp_500')
def test_events_operations_conversion_failure(mocked_stock_price, mocked_currency_rates, mocked_conversion, sample_data_views):
    """
    Тест на обработку ошибки при конвертации суммы платежа в RUB.
    """
    # Запускаем функцию
    result = events_operations(sample_data_views, "2025-01-01")

    # Проверяем, что результат равен None
    assert result is None, "Результат должен быть None при неудачной конвертации"


# Тест на обработку ошибки при пустом файле настроек
@patch('src.views.get_user_settings', return_value={})
@patch('src.views.conversion_to_single_currency')
@patch('src.views.get_currency_rates')
@patch('src.views.get_stock_price_sp_500')
def test_events_operations_empty_settings(mocked_stock_price, mocked_currency_rates, mocked_conversion, mocked_settings, sample_data_views):
    """
    Тест на обработку ошибки при пустом файле настроек.
    """
    # Запускаем функцию
    result = events_operations(sample_data_views, "2025-01-01")

    # Проверяем, что результат содержит сообщение об ошибке
    assert result is None, "Должно быть сообщение об ошибке"