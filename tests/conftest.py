from unittest.mock import patch

import pytest
import pandas as pd

@pytest.fixture(scope='module')
def test_transactions():
    dates = [
        '2023-07-01', '2023-07-15', '2023-08-01', '2023-08-15',
        '2023-09-01', '2023-09-15', '2023-10-01', '2023-10-15'
    ]
    amounts = [-100, -200, -300, -400, -500, -600, -700, -800]
    currencies = ['USD', 'EUR', 'RUB', 'GBP', 'USD', 'EUR', 'RUB', 'GBP']
    df = pd.DataFrame({
        'Дата платежа': pd.to_datetime(dates),
        'Сумма': amounts,
        'Валюта': currencies
    })
    return df


@pytest.fixture(scope='module')
def positive_test_transactions():
    dates = ['2023-09-01', '2023-09-02', '2023-09-03', '2023-09-04',
    '2023-09-01', '2023-09-15', '2023-10-01', '2025-10-15']
    amounts = [100, 200, 300, 400, 500, 600, 700, -800]
    currencies = ['USD'] * len(dates)
    df = pd.DataFrame({
        'Дата платежа': pd.to_datetime(dates),
        'Сумма': amounts,
        'Валюта': currencies
    })
    return df



# Фиктивные данные для тестов
@pytest.fixture
def sample_transactions():
    return pd.DataFrame({
        "Дата платежа": pd.to_datetime([
            "2023-10-01",  # воскресенье
            "2023-10-02",  # понедельник
            "2023-10-05",  # четверг
            "2023-11-15",  # среда
            "2023-12-20",  # вторник
        ]),
        "Сумма": [-1000, -2000, -1500, -3000, -2500],
        "Сумма_RUB": [-1000, -2000, -1500, -3000, -2500],
    })

@pytest.fixture
def mock_logger():
    with patch("src.app_logger.get_logger") as mock:
        logger = MagicMock()
        mock.return_value = logger
        yield logger

@pytest.fixture
def mock_filter_by_date():
    with patch("src.utils.filter_by_date") as mock:
        yield mock

@pytest.fixture
def mock_conversion():
    with patch("src.utils.conversion_to_single_currency") as mock:
        yield mock

@pytest.fixture
def mock_write_json():
    with patch("src.utils.write_json") as mock:
        yield mock
