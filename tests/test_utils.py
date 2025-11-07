import json
import os
import shutil
import tempfile
from datetime import date
from unittest.mock import patch

import pandas as pd
import pytest

from src.utils import (
    conversion_to_single_currency,
    filter_by_date,
    get_currency_rates,
    get_data_from_expensess,
    get_data_from_income,
    get_exchange_rate,
    get_list_operation,
    get_period_operation,
    get_stock_price_sp_500,
    get_user_settings,
    write_json,
)

# Подготовим временные папки и тестовые файлы
TEST_DATA_DIR = tempfile.mkdtemp(prefix="test_data_")
DATA_FILE_PATH = os.path.join(TEST_DATA_DIR, "test_data.xlsx")


@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    request.addfinalizer(lambda: shutil.rmtree(TEST_DATA_DIR))


# Тестируем функцию get_list_operation
def test_get_list_operation_existing_file():
    df_expected = pd.DataFrame([{"Название": "Test", "Сумма платежа": 100}], columns=["Название", "Сумма платежа"])
    df_expected.to_excel(DATA_FILE_PATH, index=False)
    result = get_list_operation(DATA_FILE_PATH, ["Название", "Сумма платежа"])
    assert isinstance(result, pd.DataFrame)
    assert not result.empty


def test_get_list_operation_nonexistent_file():
    nonexistent_path = os.path.join(TEST_DATA_DIR, "nonexistent.xls")
    result = get_list_operation(nonexistent_path, ["Название", "Сумма платежа"])
    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_get_list_operation_wrong_format():
    wrong_format_path = os.path.join(TEST_DATA_DIR, "wrong.txt")
    with open(wrong_format_path, "w") as f:
        f.write("Test")
    result = get_list_operation(wrong_format_path, ["Название", "Сумма платежа"])
    assert isinstance(result, pd.DataFrame)
    assert result.empty


# Тест на обработку ошибки при отсутствии колонок
@patch("src.utils.logger")
def test_get_list_operation_missing_columns(mocked_logger, faulty_data):
    """
    Тест на обработку ошибки при отсутствии колонок.
    """
    # Создаем временный файл с отсутствующими колонками
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".xlsx") as temp_file:
        temp_file_path = temp_file.name
        faulty_data.drop(columns=["Категория"]).to_excel(temp_file_path, index=False, engine="openpyxl")

    # Запускаем функцию
    result = get_list_operation(temp_file_path, ["Дата платежа", "Сумма платежа", "Кэшбэк"], "OK")
    print("\n!!! = ", result)

    # Удаляем временный файл
    os.remove(temp_file_path)

    # Проверяем, что результат пустой
    assert result.empty, "Результат должен быть пустым"

    # Проверяем, что было сообщение об ошибке
    mocked_logger.error.assert_called_once_with("Ошибка в данных, отсутствует колонка {'Сумма платежа'}")


# Тест на обработку ValueError
@patch("src.utils.logger")
def test_get_list_operation_no_data(mocked_logger):
    """
    Тест на обработку ошибки при отсутствии данных.
    """
    # Создаем временный файл с колонками, но без данных
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".xlsx") as temp_file:
        temp_file.write("Дата платежа,Сумма платежа,Категория\n")
        temp_file.write("Дата платежа,Сумма платежа,Категория\n")
        temp_file_path = temp_file.name

    # Запускаем функцию
    result = get_list_operation(temp_file_path, ["Дата платежа", "Сумма платежа", "Категория"], "OK")

    # Удаляем временный файл
    os.remove(temp_file_path)

    # Проверяем, что результат пустой
    assert result.empty, "Результат должен быть пустым"

    # Проверяем, что было сообщение об ошибке

    mocked_logger.error.assert_called()


#
# def test_get_list_operation_csv():
#     # Создаем временный CSV-файл с известными данными
#     df_test = pd.DataFrame({"Название": ["Продукт А", "Продукт B"], "Цена": [100, 200], "Статус": ["OK", "OK"]})
#
#     # Создаем временный файл CSV
#     _, temp_csv_path = tempfile.mkstemp(suffix=".csv")
#     df_test.to_csv(temp_csv_path, index=False)
#
#     # Определяем список необходимых колонок
#     required_columns = ["Название", "Цена", "Статус"]
#
#     # Читаем данные с помощью get_list_operation
#     result_df = get_list_operation(temp_csv_path, required_columns)
#
#     # Проверяем, что получили верный DataFrame
#     assert isinstance(result_df, pd.DataFrame)
#     assert len(result_df) == 2  # Две строки в исходном DataFrame
#     assert result_df.equals(df_test)  # Проверяем точное соответствие данных
#
#     # Чистим временный файл
#     os.unlink(temp_csv_path)


def test_get_period_operation_logging():
    # Патчим метод info логгера
    with patch("src.utils.logger.info") as mock_info:
        # Вызываем функцию, которая вызывает логгер
        get_period_operation("", "M")

        # Проверяем, что логгер получил определенное сообщение
        mock_info.assert_called_once_with("Дата не указана, берём текущую")


# Тестируем функцию get_period_operation
def test_get_period_operation_month():
    result = get_period_operation("01.01.2025", "M")
    assert len(result) == 2
    assert isinstance(result[0], date)
    assert isinstance(result[1], date)


# Тестируем функцию get_period_operation
def test_get_period_operation_year():
    result = get_period_operation("01.01.2025", "Y")
    assert len(result) == 2
    assert isinstance(result[0], date)
    assert isinstance(result[1], date)


# Тестируем функцию get_period_operation
def test_get_period_operation_week():
    result = get_period_operation("01.01.2025", "W")
    assert len(result) == 2
    assert isinstance(result[0], date)
    assert isinstance(result[1], date)


def test_get_period_operation_all():
    result = get_period_operation("01.01.2025", "ALL")
    assert len(result) == 2
    assert isinstance(result[0], date)
    assert isinstance(result[1], date)


# Тестируем функцию filter_by_date
def test_filter_by_date():
    df_input = pd.DataFrame([{"Дата платежа": "01.01.2025"}, {"Дата платежа": "01.02.2025"}])
    result = filter_by_date(df_input, ["2025-01-01", "2025-01-31"])
    assert isinstance(result, pd.DataFrame)
    assert len(result.index) == 1


def test_filter_by_date_with_incorrect_date_format():
    # Создаем тестовый DataFrame с некорректными значениями в столбце дат
    df_input = pd.DataFrame(
        {
            "Дата платежа": ["01.33.2025"],
            "Сумма платежа": [
                100,
            ],
        }
    )

    # Период фильтрации (включаются только корректные даты)
    period_dates = ["2025-01-01", "2025-01-31"]

    # Проводим фильтрацию
    result = filter_by_date(df_input, period_dates)

    # Проверяем, что результат — DataFrame
    assert isinstance(result, pd.DataFrame)


# Тестируем функцию get_exchange_rate с заглушкой
@patch("requests.get")
def test_get_exchange_rate_success(mock_get):
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {"conversion_rate": 1.2}

    result = get_exchange_rate("USD")
    assert isinstance(result, float)
    assert result == 1.2


@patch("requests.get")
def test_get_exchange_rate_failure(mock_get):
    mock_response = mock_get.return_value
    mock_response.status_code = 404
    mock_response.json.return_value = {}

    result = get_exchange_rate("USD")
    assert isinstance(result, int)
    assert result == 0


# Тест на ошибку JSON (JSONDecodeError)
@patch("requests.get")
def test_get_exchange_rate_json_error(mock_get):
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.side_effect = json.decoder.JSONDecodeError("Invalid JSON", "", 0)

    result = get_exchange_rate("USD")
    assert isinstance(result, int)
    assert result == 0


# Тест на одинаковые валюты
def test_get_exchange_rate_same_currency():
    result = get_exchange_rate("USD", "USD")
    assert isinstance(result, int)
    assert result == 1.0


# Тестируем функцию conversion_to_single_currency
@patch("src.utils.get_exchange_rate")
def test_conversion_to_single_currency(mock_get_exchange_rate):
    mock_get_exchange_rate.return_value = 1.2

    df_input = pd.DataFrame(
        [{"Валюта платежа": "USD", "Сумма платежа": 100}, {"Валюта платежа": "EUR", "Сумма платежа": 200}]
    )
    result = conversion_to_single_currency(df_input)
    assert isinstance(result, pd.DataFrame)
    assert "Сумма платежа_RUB" in result.columns


@patch("requests.get")
def test_conversion_to_single_currency_fail_convert(mock_get_exchange_rate):
    # Готовим тестовый DataFrame с некорректными значениями в денежном столбце
    df_input = pd.DataFrame(
        {"Валюта платежа": ["USD", "EUR"], "Сумма платежа": ["abc", "xyz"]}  # Некорректные значения
    )
    mock_get_exchange_rate.return_value = 1.2

    # Пробуем провести конвертацию
    result = conversion_to_single_currency(df_input)

    # Проверяем, что все значения в результирующем столбце стали NaN
    assert isinstance(result, pd.DataFrame)
    assert result["Сумма платежа"].isnull().all(), "Все значения должны стать NaN"


def test_conversion_to_single_currency_exception_handling():
    # Эмуляция ошибочного сценария для одной валюты
    def mock_get_exchange_rate(currency, target_currency="RUB"):
        if currency == "ERR_CURRENCY":
            raise Exception("Искусственная ошибка конверсии валюты!")
        else:
            return 1.2  # Обычная ставка для валидной валюты

    # Создаём тестовый DataFrame с разными валютами
    df_input = pd.DataFrame({"Валюта платежа": ["USD", "ERR_CURRENCY"], "Сумма платежа": [100, 200]})

    # Устанавливаем заглушку на функцию get_exchange_rate
    with patch("src.utils.get_exchange_rate", side_effect=mock_get_exchange_rate):
        # Пробуем провести конвертацию
        result = conversion_to_single_currency(df_input)

    # Проверяем, что результат — DataFrame с правильным количеством строк
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2

    # Проверяем, что первая строка (валидная валюта) сохранилась
    first_row = result.iloc[0]
    assert first_row["Валюта платежа"] == "USD"
    assert first_row["Сумма платежа_RUB"] == 120.0  # Сумма умноженная на коэффициент конверсии

    # Вторая строка (ошибочная валюта) должна оставаться неизменённой
    second_row = result.iloc[1]
    assert second_row["Валюта платежа"] == "ERR_CURRENCY"


# Тестируем функцию get_data_from_expensess
def test_get_data_from_expensess():
    df_input = pd.DataFrame(
        [{"Категория": "Еда", "Сумма платежа_RUB": -100}, {"Категория": "Транспорт", "Сумма платежа_RUB": -200}]
    )
    result = get_data_from_expensess(df_input)
    assert isinstance(result, dict)
    assert "expenses" in result.keys()


def test_get_data_from_expensess_failed_conversion():
    # Готовим тестовый DataFrame с некорректными значениями в колонке сумм
    df_input = pd.DataFrame(
        {
            "Категория": ["Еда", "Транспорт"],
            "Сумма платежа": ["abc", "xyz"],  # Некорректные значения
            "Сумма платежа_RUB": [None, "8"],  # Некорректные значения
        }
    )

    # Пробуем обработать расходы
    result = get_data_from_expensess(df_input)

    # Проверяем, что результат содержит структуру с main=[] и total_amount=0
    assert isinstance(result, dict)
    assert result == {
        "expenses": {"main": [], "total_amount": 0}
    }, "Функция должна вернуть минимальный результат при наличии NaN!"


def test_get_data_from_expensess_grouping():
    # Генерируем тестовый DataFrame с различными категориями расходов
    df_input = pd.DataFrame(
        {
            "Категория": [
                "Еда",
                "Транспорт",
                "Развлечения",
                "Коммунальные услуги",
                "Интернет",
                "Связь",
                "Путешествия",
                "Медицина",
                "Образование",
            ],
            "Сумма платежа_RUB": [-1000, -500, -800, -1200, -300, -700, -900, -400, -600],
        }
    )

    # Приводим данные к виду, необходимому для анализа расходов
    result = get_data_from_expensess(df_input)

    # Проверяем, что итоговый результат содержит ровно восемь категорий
    # Первые семь уникальных категорий плюс группа "Остальное"
    assert len(result["expenses"]["main"]) == 8, "Количество категорий должно быть равно восьми!"

    # Проверяем, что последняя категория — это "Остальное"
    last_category = result["expenses"]["main"][-1]["category"]
    assert last_category == "Остальное", 'Последней категорией должна быть "Остальное"!'

    # Проверяем, что сумма группы "Остальное" равна правильному значению
    # Группа "Остальное" содержит сумму трёх последних расходов
    expected_sum = abs(-300 - 400)  # Складываем последние три малых расхода
    assert result["expenses"]["main"][-1]["amount"] == expected_sum, 'Сумма группы "Остальное" неверна!'


# Тестируем функцию get_data_from_income
def test_get_data_from_income():
    df_input = pd.DataFrame(
        [{"Категория": "Зарплата", "Сумма платежа_RUB": 1000}, {"Категория": "Подработка", "Сумма платежа_RUB": 500}]
    )
    result = get_data_from_income(df_input)
    assert isinstance(result, dict)
    assert "income" in result.keys()


def test_get_data_from_income_incorrect_date_format():
    # Создаем тестовый DataFrame с некорректными значениями в столбце дат
    df_input = pd.DataFrame(
        {
            "Дата платежа": ["01.01.2025"],
            "Сумма платежа": [
                100,
            ],
            "Категория": ["Продукты"],
            "Сумма платежа_RUB": [
                "",
            ],
        }
    )

    result = get_data_from_income(df_input)
    # print("\nresult = ", result)

    # Проверяем, что результат — DataFrame
    assert result == {"income": {"total_amount": 0, "main": []}}


def test_get_list_operation_csv_():
    # Создаем временный CSV-файл с известными данными
    df_test = pd.DataFrame({"Название": ["Продукт А", "Продукт B"], "Цена": [100, 200], "Статус": ["OK", "OK"]})

    # Создаем временный файл CSV с помощью менеджера контекста
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".csv", delete=False) as temp_file:
        df_test.to_csv(temp_file.name, index=False)
        temp_csv_path = temp_file.name

    # Определяем список необходимых колонок
    required_columns = ["Название", "Цена", "Статус"]

    # Читаем данные с помощью get_list_operation
    result_df = get_list_operation(temp_csv_path, required_columns)

    # Проверяем, что получили верный DataFrame
    assert isinstance(result_df, pd.DataFrame)
    assert len(result_df) == 2  # Две строки в исходном DataFrame
    assert result_df.equals(df_test)  # Проверяем точное соответствие данных

    # Чистим временный файл
    os.unlink(temp_csv_path)


# Тестируем функцию get_user_settings
def test_get_user_settings_existing_file():
    settings_path = os.path.join(TEST_DATA_DIR, "settings.json")
    with open(settings_path, "w") as f:
        f.write('{"user_currencies": ["USD", "EUR"]}')
    result = get_user_settings(settings_path)
    assert isinstance(result, dict)
    assert "user_currencies" in result.keys()


def test_get_user_settings_nonexistent_file():
    nonexistent_path = os.path.join(TEST_DATA_DIR, "nonexistent.json")
    result = get_user_settings(nonexistent_path)
    assert isinstance(result, dict)
    assert not result


# Тестируем функцию get_currency_rates
def test_get_currency_rates():
    user_settings = {"user_currencies": ["USD", "EUR"]}
    result = get_currency_rates(user_settings)
    assert isinstance(result, list)
    assert len(result) == 2


# Тестируем функцию get_stock_price_sp_500 с заглушкой
@patch("requests.get")
def test_get_stock_price_sp_500(mock_get):
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = [{"symbol": "AAPL", "price": 100.0}, {"symbol": "GOOG", "price": 200.0}]

    user_settings = {"user_stocks": ["AAPL", "GOOG"]}
    result = get_stock_price_sp_500(user_settings)
    assert isinstance(result, list)
    assert len(result) == 2


# Тестируем функцию write_json
def test_write_json():
    output_path = os.path.join(TEST_DATA_DIR, "output.json")
    data = {"key": "value"}
    write_json(data, output_path)
    assert os.path.exists(output_path)
    with open(output_path, "r") as f:
        content = f.read()
        assert '"key": "value"' in content
