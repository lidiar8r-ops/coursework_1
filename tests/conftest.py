import os
import tempfile
import time
from os import remove
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest


# Создаем фикстуру, которая запускается перед каждым тестом
@pytest.fixture
def test_lists() -> list:  # Имя фикстуры — любое
    return [
        {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
        {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
        {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
        {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
    ]


# Создаем фикстуру, которая запускается перед каждым тестом
@pytest.fixture
def test_lists_date_similar() -> list:  # Имя фикстуры — любое
    return [
        {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
        {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
        {"id": 594226726, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
        {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
        {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
    ]


@pytest.fixture
def test_lists_no_correct_key() -> list:  # Имя фикстуры — любое
    return [
        {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
        {"id": 939719570, "state1": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
        {"id": 594226727, "state": "CANCELED", "date1": "2018-09-12T21:27:25.241689"},
        {"id": 939719570, "state": "EXECUTED", "date": "30-01-2018T02:08:58.425572"},
        {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
    ]


@pytest.fixture
def test_lists_no_correct_date() -> list:  # Имя фикстуры — любое
    return [
        {"id": 41428829, "state": "EXECUTED", "date": "2019.23.03"},
        {"id": 939719570, "state": "EXECUTED", "date": "2018-07-30"},
        {"id": 594226726, "state": "CANCELED", "date": "2018/09/12T21:27:25.241689"},
        {"id": 594226727, "state": "CANCELED", "date": None},
        {"id": 594226727, "state": "CANCELED", "date": ""},
        {"id": 939719570, "state": "EXECUTED", "date": "2018.06.30T02:08:58.425572"},
        {"id": 615064591, "state": "CANCELED", "date": "2018"},
    ]


@pytest.fixture
def test_lists_no_correct_no_date() -> list:  # Имя фикстуры — любое
    return [
        {"id": 939719570, "state": "EXECUTED", "date": 2018.101},
        {"id": 939719570, "state": "EXECUTED", "date": True},
        {"id": 939719570, "state": "EXECUTED", "date": None},
        {"id": 939719570, "state": "EXECUTED", "date": ()},
        {"id": 939719570, "state": "EXECUTED", "date": 0},
    ]


@pytest.fixture
def transactions() -> list:  # Имя фикстуры — любое
    return [
        {
            "id": 939719570,
            "state": "EXECUTED",
            "date": "2018-06-30T02:08:58.425572",
            "operationAmount": {"amount": "9824.07", "currency": {"name": "USD", "code": "USD"}},
            "description": "Перевод организации",
            "from": "Счет 75106830613657916952",
            "to": "Счет 11776614605963066702",
        },
        {
            "id": 142264268,
            "state": "EXECUTED",
            "date": "2019-04-04T23:20:05.206878",
            "operationAmount": {"amount": "79114.93", "currency": {"name": "USD", "code": "USD"}},
            "description": "Перевод со счета на счет",
            "from": "Счет 19708645243227258542",
            "to": "Счет 75651667383060284188",
        },
        {
            "id": 873106923,
            "state": "EXECUTED",
            "date": "2019-03-23T01:09:46.296404",
            "operationAmount": {"amount": "43318.34", "currency": {"name": "руб.", "code": "RUB"}},
            "description": "Перевод со счета на счет",
            "from": "Счет 44812258784861134719",
            "to": "Счет 74489636417521191160",
        },
        {
            "id": 895315941,
            "state": "EXECUTED",
            "date": "2018-08-19T04:27:37.904916",
            "operationAmount": {"amount": "56883.54", "currency": {"name": "USD", "code": "USD"}},
            "description": "Перевод с карты на карту",
            "from": "Visa Classic 6831982476737658",
            "to": "Visa Platinum 8990922113665229",
        },
        {
            "id": 594226727,
            "state": "CANCELED",
            "date": "2018-09-12T21:27:25.241689",
            "operationAmount": {"amount": "67314.70", "currency": {"name": "руб.", "code": "RUB"}},
            "description": "Перевод организации",
            "from": "Visa Platinum 1246377376343588",
            "to": "Счет 14211924144426031657",
        },
    ]


@pytest.fixture
def transactions_no_currency() -> list:  # Имя фикстуры — любое
    return [
        {
            "id": 939719570,
            "state": "EXECUTED",
            "date": "2018-06-30T02:08:58.425572",
            "operationAmoun": {"amount": "9824.07", "currency": {"name": "USD", "code": "USD"}},
            "from": "Счет 75106830613657916952",
            "to": "Счет 11776614605963066702",
        },
        {
            "id": 939719571,
            "state": "EXECUTED",
            "date": "2018-06-30T02:08:58.425572",
            "operationAmount": {"amount": "9824.07", "curreny": {"name": "USD", "code": "USD"}},
            "descriptionwww": "Перевод организации",
            "from": "Счет 75106830613657916952",
            "to": "Счет 11776614605963066702",
        },
        {
            "id": 594226727,
            "state": "CANCELED",
            "date": "2018-09-12T21:27:25.241689",
            "operationAmount": {"amount": "67314.70", "currency": {"name": "руб.", "codes": "RUB"}},
            "descriptio_n": "Перевод организации",
            "from": "Visa Platinum 1246377376343588",
            "to": "Счет 14211924144426031657",
        },
        {
            "id": 594226727,
            "state": "CANCELED",
            "date": "2018-09-12T21:27:25.241689",
            "operationAmount": {"amount": "67314.70", "currency": {"name": "руб.", "codes": "RUB"}},
            "description": None,
            "from": "Visa Platinum 1246377376343588",
            "to": "Счет 14211924144426031657",
        },
    ]


@pytest.fixture
def transaction_params_load_rub() -> dict:
    return {
        "id": 41428829,
        "state": "EXECUTED",
        "date": "2019-07-03T18:35:29.512364",
        "operationAmount": {"amount": "100", "currency": {"name": "руб.", "code": "RUB"}},
        "description": "Перевод организации",
        "from": "MasterCard 7158300734726758",
        "to": "Счет 35383033474447895560",
    }


@pytest.fixture
def transaction_params_load_usd() -> dict:
    return {
        "id": 41428829,
        "state": "EXECUTED",
        "date": "2019-07-03T18:35:29.512364",
        "operationAmount": {"amount": "100", "currency": {"name": "USD", "code": "USD"}},
        "description": "Перевод организации",
        "from": "MasterCard 7158300734726758",
        "to": "Счет 35383033474447895560",
    }


# Создание временных файлов
@pytest.fixture(scope="module", autouse=True)
def create_temp_files():
    valid_json_path = None
    invalid_json_path = None
    nonexistent_file_path = r"..\nodata\operations.json"

    # Временный файл с валидным JSON
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as temp_valid_file:
        valid_json_path = temp_valid_file.name
        temp_valid_file.write('[{"id": 1}, {"id": 2}, {"id": 5}]')

    # Временный файл с неправильным форматом JSON
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as temp_invalid_file:
        invalid_json_path = temp_invalid_file.name
        temp_invalid_file.write("{'not-a-valid-json'")

    yield {
        "valid_json_path": valid_json_path,
        "invalid_json_path": invalid_json_path,
        "nonexistent_file_path": nonexistent_file_path,
    }

    # Удаление созданных временных файлов
    if valid_json_path is not None:
        remove(valid_json_path)
    if invalid_json_path is not None:
        remove(invalid_json_path)


@pytest.fixture
def valid_dataframe():
    """Возвращает валидный dataframe для тестирования."""
    return pd.DataFrame(
        [
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
        ]
    )


@pytest.fixture
def csv_temp_file():
    filename = "temp.csv"
    with open(filename, mode="w"):
        pass
    yield filename
    time.sleep(1)  # Даем немного времени освободить ресурс
    os.unlink(filename)


@pytest.fixture(scope="module")
def excel_temp_file():
    """Временный Excel-файл с некорректными данными для ValueError."""
    _, filename = tempfile.mkstemp(suffix=".xlsx")
    with open(filename, mode="wb"):
        pass  # пустой файл
    yield filename
    time.sleep(2)  # Даем немного времени освободить ресурс
    os.unlink(filename)


# Фикстура для минимального DataFrame с одними колонками, но без данных
@pytest.fixture
def empty_columns_dataframe():
    columns = ["id", "state", "date", "amount", "currency_name", "currency_code", "from", "to", "description"]
    return pd.DataFrame(columns=columns)


# Фикстура для  проверки DataFrame на поля
@pytest.fixture
def test_dataframe_valid():
    return pd.DataFrame(
        [{
            "id": 142264268,
            "state": "EXECUTED",
            "date": "2019-04-04T23:20:05.206878",
            "operationAmount": {"amount": "79114.93", "currency": {"name": "USD", "code": "USD"}},
            "description": "Перевод со счета на счет",
            "from": "Счет 19708645243227258542",
            "to": "Счет 75651667383060284188",
        },])


# Утилизатор для удаления временных файлов
@pytest.fixture(autouse=True)
def cleanup():
    files_to_delete = ["test_data.csv", "test_data.xlsx"]
    for file in files_to_delete:
        if os.path.exists(file):
            os.remove(file)


# чтобы управлять существованием файла
@pytest.fixture
def mock_isfile():
    with patch("os.path.isfile") as mock:
        yield mock


@pytest.fixture
def mock_read_csv():
    with patch("pandas.read_csv") as mock:
        yield mock


@pytest.fixture
def mock_read_excel_ok():
    with patch("pandas.read_excel") as mock:
        yield mock


# создает фиктивный DataFrame с нужными колонками и данными.
@pytest.fixture
def mock_df():
    mock_df = MagicMock()
    mock_df.columns = ["id", "state", "date", "amount", "currency_name", "currency_code", "from", "to", "description"]
    mock_df.to_dict.return_value = [
        {
            "id": "1",
            "state": "done",
            "date": "2023-01-01",
            "amount": 100,
            "currency_name": "USD",
            "currency_code": "USD",
            "from": "A",
            "to": "B",
            "description": "Test transaction",
        }
    ]
    return mock_df


@pytest.fixture
def test_bank_transactions() -> list:
    """Фикстура с набором банковских операций."""
    return [
        {
            "id": 142264268,
            "state": "EXECUTED",
            "date": "2019-04-04T23:20:05.206878",
            "operationAmount": {"amount": "79114.93", "currency": {"name": "USD", "code": "USD"}},
            "description": "Перевод со счета на счет",
            "from": "Счет 19708645243227258542",
            "to": "Счет 75651667383060284188",
        },
        {
            "id": 863064926,
            "state": "EXECUTED",
            "date": "2019-12-08T22:46:21.935582",
            "operationAmount": {"amount": "41096.24", "currency": {"name": "USD", "code": "USD"}},
            "description": "Открытие вклада",
            "to": "Счет 90424923579946435907",
        },
        {
            "id": 615064591,
            "state": "CANCELED",
            "date": "2018-10-14T08:21:33.419441",
            "operationAmount": {"amount": "77751.04", "currency": {"name": "руб.", "code": "RUB"}},
            "description": "Перевод с карты на счет",
            "from": "Maestro 3928549031574026",
            "to": "Счет 84163357546688983493",
        },
        {
            "id": 441945890,
            "state": "EXECUTED",
            "date": "2019-08-30T16:30:20.333444",
            # Нет поля description!
        },
        {
            "id": 441945891,
            "state": "EXECUTED",
            "date": "2019-08-31T18:45:55.555666",
            "operationAmount": {"amount": "0.00", "currency": {"name": "руб.", "code": "RUB"}},
            "description": "",  # Пустая строка
        },
        {},
    ]


@pytest.fixture
def test_categories_operations() -> list:
    return ["Перевод со счета на счет", "Открытие вклада", "Перевод с карты на счет", ""]
