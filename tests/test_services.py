import pytest
import pandas as pd
from unittest.mock import patch, Mock
from src.services import get_profitable_cashback


def test_valid_input(sample_data):
    """Тестирование обычной работы функции."""
    with patch('src.services.app_logger') as mock_logger:
        result = get_profitable_cashback(sample_data, "2025", "01")
        expected = {'Одежда': 300.0, 'Продукты': 151.0, 'Развлечения': 200.0}
        assert result == expected, f"Неправильная обработка валидных данных. Получили: {result}"
        mock_logger.get_logger.return_value.info.assert_called()


def test_no_transactions_in_period(sample_data):
    """Тестирование отсутствия транзакций за указанный период."""
    with patch('src.services.app_logger'):
        result = get_profitable_cashback(sample_data, "2025", "02")
        assert result == {}, "Должен вернуть пустой словарь при отсутствии транзакций."


def test_zero_cashback(sample_data):
    """Тестирование исключения нулевых значений кэшбэка."""
    with patch('src.services.app_logger'):
        result = get_profitable_cashback(sample_data, "2025", "01")
        assert "Транспорт" not in result.keys(), "Категории с нулевым кэшбэком не учитываются."


def test_invalid_year_or_month(sample_data):
    """Тестирование реакции на неправильный формат года или месяца."""
    with patch('src.services.app_logger'):
        with pytest.raises(ValueError):
            get_profitable_cashback(sample_data, "abc", "11")


def test_empty_dataframe():
    """Тестирование передачи пустого DataFrame."""
    empty_df = pd.DataFrame(columns=["Дата платежа", "Кэшбэк", "Категория"])
    with patch('src.services.app_logger'):
        result = get_profitable_cashback(empty_df, "2025", "01")
        assert result == {}, "При пустом DataFrame должен возвращаться пустой словарь."


def test_negative_cashback(sample_data):
    """Тестирование обработки отрицательного кэшбэка."""
    modified_data = sample_data.copy()
    modified_data.at[0, "Кэшбэк"] = -100.5
    with patch('src.services.app_logger'):
        result = get_profitable_cashback(modified_data, "2025", "01")
        expected = {'Одежда': 300.0, 'Продукты': 50.0, 'Развлечения': 200.0}
        assert result == expected, f"Негативные значения кэшбэка игнорируются. Получили: {result}"