from unittest.mock import patch

import pandas as pd

from src.get_csv_xls import get_csv_xlsx_reader_transaction


def test_valid_csv(valid_dataframe, test_dataframe_valid):
    """Тест успешного чтения CSV-файла с разделителем ';'."""
    with patch("pandas.read_csv", return_value=valid_dataframe) as mock_read_csv, \
            patch("os.path.isfile", return_value=True):
        result = get_csv_xlsx_reader_transaction("test.csv")

        # Проверки результата
        assert isinstance(result, list), "Результат должен быть списком"
        assert len(result) == 1, "Должна быть одна запись"

        row = result[0]

        # Проверка наличия всех обязательных колонок
        missing_keys = [key for key in test_dataframe_valid if key not in row]
        assert not missing_keys, f"Отсутствуют ключи: {missing_keys}"

        # Проверка типов данных
        assert isinstance(row["id"], int), "id должен быть целым числом"
        assert isinstance(row['operationAmount']["amount"], (int, float)), "amount должен быть числом"
        assert isinstance(row["date"], str), "date должен быть строкой"

        # Проверка вызова мока
        mock_read_csv.assert_called_once_with("test.csv", delimiter=";")


def test_valid_xlsx(valid_dataframe, test_dataframe_valid):
    """Тест  успешное чтение из Excel файла"""
    with patch("pandas.read_excel", return_value=valid_dataframe) as mock_read_xls, \
            patch("os.path.isfile", return_value=True):
        result = get_csv_xlsx_reader_transaction("test.xlsx")

        # Проверки результата
        assert isinstance(result, list), "Результат должен быть списком"
        assert len(result) == 1, "Должна быть одна запись"

        row = result[0]

        # Проверка наличия всех обязательных колонок
        missing_keys = [key for key in test_dataframe_valid if key not in row]
        assert not missing_keys, f"Отсутствуют ключи: {missing_keys}"

        # Проверка типов данных
        assert isinstance(row["id"], int), "id должен быть целым числом"
        assert isinstance(row['operationAmount']["amount"], (int, float)), "amount должен быть числом"
        assert isinstance(row["date"], str), "date должен быть строкой"

        # Проверка вызова мока
        mock_read_xls.assert_called_once_with("test.xlsx")


def test_nonexistent_file():
    """Тест  обработка ситуации, когда файл не существует"""
    with patch("os.path.isfile", return_value=False):
        result = get_csv_xlsx_reader_transaction("nonexistent.csv")
        assert result == []


def test_incorrect_extension():
    """Тест обработка файла с неправильным расширением"""
    with patch("os.path.isfile", return_value=True):
        result = get_csv_xlsx_reader_transaction("invalid.txt")
        assert result == []


def test_pandas_exception():
    """Тест обработка исключения при работе с Pandas"""
    with patch("pandas.read_csv", side_effect=Exception("Pandas read exception")), patch(
        "os.path.isfile", return_value=True
    ):
        result = get_csv_xlsx_reader_transaction("test.csv")
        assert result == []


def test_empty_file():
    """Тест  обработка пустого файла"""
    with patch("pandas.read_csv", return_value=pd.DataFrame()), patch("os.path.isfile", return_value=True):
        result = get_csv_xlsx_reader_transaction("empty.csv")
        assert result == []


def test_missing_column():
    """Тест обработка отсутствующих колонок"""
    incomplete_dataframe = [
        {
            "id": 1,
            "state": "CANCELED",
            "date": "2023-09-15",
            "amount": 100,
            "currency_name": "RUB",
            "currency_code": "RUB",
            "description": "Test transaction",
            "from": "Bank A",
            "to": "Bank B",
        }
    ]  # колонка "to" удалена!
    with patch("pandas.read_csv", return_value=incomplete_dataframe), patch("os.path.isfile", return_value=True):
        result = get_csv_xlsx_reader_transaction("missing_column.csv")
        assert result == []  # "Функция должна вернуть пустой список при отсутствии обязательных полей."


def test_file_not_found():
    """Тест на отсутствие файла (FileNotFoundError)."""
    assert get_csv_xlsx_reader_transaction("non_existing_file.xls") == []


def test_value_error_with_incorrect_csv(csv_temp_file):
    """Тест на неправильное значение (ValueError) в CSV-файле."""
    assert get_csv_xlsx_reader_transaction(csv_temp_file) == []


@patch("pandas.read_csv")
def test_generic_exception(mock_read_csv):
    """Тест на общее исключение (искусственно вызвано в read_csv)."""
    mock_read_csv.side_effect = Exception("Test exception")
    assert get_csv_xlsx_reader_transaction("fake.csv") == []


@patch("pandas.read_excel")
def test_generic_exception_on_excel(mock_read_excel):
    """Тест на общее исключение (искусственно вызвано в read_excel)."""
    mock_read_excel.side_effect = Exception("Test exception")
    assert get_csv_xlsx_reader_transaction("fake.xlsx") == []


# Тест проверяющий создание DataFrame
def test_valid_dataframe(valid_dataframe):
    assert isinstance(valid_dataframe, pd.DataFrame)
    assert len(valid_dataframe.columns) == 9
    assert valid_dataframe.shape == (1, 9)


@patch("src.get_csv_xls.pd.read_excel")
def test_empty_data_but_fields_exist(mock_read_excel, empty_columns_dataframe):
    mock_read_excel.return_value = empty_columns_dataframe

    file_path = "empty_file.xlsx"
    result = get_csv_xlsx_reader_transaction(file_path)

    assert result == [], "Функция должна вернуть пустой список, если файл пуст"


@patch("src.get_csv_xls.pd.read_excel")
def test_reader_empty_file(mock_read_excel, empty_columns_dataframe):
    # Заменяем реальную функцию pd.read_excel на макет
    mock_read_excel.return_value = empty_columns_dataframe

    # Выполняем проверку функции
    result = get_csv_xlsx_reader_transaction("fake_file.xlsx")

    # Проверяем, что результатом обработки пустого файла является пустой список
    assert result == []  # "При обработке пустого файла должен возвращаться пустой список"

    # Дополнительно проверяем, что макет был вызван
    assert mock_read_excel.called is False  # "Макетированный метод не был вызван"


# Тест на отсутствие данных в файле
def test_no_data_in_file(empty_columns_dataframe):
    with patch("src.get_csv_xls.pd.read_excel", return_value=empty_columns_dataframe):
        result = get_csv_xlsx_reader_transaction("empty_file.xlsx")
        assert result == []


def test_headers_only_with_mock(empty_columns_dataframe):
    """Проверяет, что функция возвращает пустой список, когда данных нет.Но заголовки есть"""

    # Создаем DataFrame с только заголовками (пустой)
    with patch("os.path.isfile") as mock_isfile, patch("pandas.read_csv") as mock_read_csv, patch(
            "pandas.read_excel"
    ) as mock_read_excel:
        mock_isfile.return_value = True

        # В зависимости от расширения, вызовется нужная функция
        # Для CSV
        mock_read_csv.return_value = empty_columns_dataframe
        # Для Excel
        mock_read_excel.return_value = empty_columns_dataframe

        # Вызов для CSV
        result_csv = get_csv_xlsx_reader_transaction("empty_date.csv")
        assert result_csv == []

        # Вызов для Excel
        result_xlsx = get_csv_xlsx_reader_transaction("empty_date.xlsx")
        assert result_xlsx == []

