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
    dates = ['2023-09-01', '2023-09-02', '2023-09-03', '2023-09-04']
    amounts = [100, 200, 300, 400]
    currencies = ['USD'] * len(dates)
    df = pd.DataFrame({
        'Дата платежа': pd.to_datetime(dates),
        'Сумма': amounts,
        'Валюта': currencies
    })
    return df