import pytest
import pandas as pd
from unittest.mock import patch, Mock
from src.services import get_profitable_cashback


@patch('src.services.write_json')
@patch('src.services.logger')
def test_valid_input(mock_logger, mock_write_json, sample_data):
    """Тестирование нормальной работы функции."""
    # Запускаем тестируемую функцию
    result = get_profitable_cashback(sample_data, "2025", "01")

    # Проверяем, что функция возвращает верный результат
    expected = {'Одежда': 300.0, 'Продукты': 151.0, 'Развлечения': 200.0}
    assert result == expected, f"Неправильный результат обработки данных."

    # Проверяем, что логгер вызвал метод info хотя бы один раз
    mock_logger.info.assert_called()


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


#  проверка обработки даты платежа вызвать исключение
@patch("pandas.to_datetime", side_effect=ValueError("Некорректный формат даты"))  # Моделируем ошибку преобразования
def test_unexpected_exception_returns_df(mock_to_datetime, sample_data):
    """
    Тестируем обработку неправильного формата даты при вызове функции get_profitable_cashback.
    Ожидаемый результат — пустой словарь {} при ошибке преобразования.
    """
    # Применяем нашу функцию с неправильными данными
    result = get_profitable_cashback(sample_data, "0001", "9")

    # Проверяем результат
    assert isinstance(result, dict), "Результат должен быть экземпляром класса dict"
    assert len(result) == 0, "Результат должен быть пустым словарем"


# Тест на возникновение ошибки при записи в файл
def test_write_json_failure(sample_data):
    """
    Тест на возникновение ошибки при записи в файл.
    """
    # Патч для функции write_json, чтобы симулировать ошибку
    with patch("src.services.write_json", side_effect=Exception("Искусственная ошибка записи в файл")):
        with patch("src.services.logger.critical") as mock_critical:
            with pytest.raises(Exception):
                get_profitable_cashback(sample_data, "2025", "01")

            # Проверка вызова метода critical
            mock_critical.assert_called_once()
