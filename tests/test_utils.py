# import os
# import json
# import pytest
# import responses
# import pandas as pd
# from src.utils import *
# from src.config import DATA_DIR, LIST_OPERATION, URL_EXCHANGE, URL_EXCHANGE_SP_500
#
# # Установим временный каталог для тестов
# TEST_DATA_DIR = "./tests/data/"
# os.makedirs(TEST_DATA_DIR, exist_ok=True)
#
# # Вспомогательная фикстура для удаления временных файлов после тестов
# @pytest.fixture(autouse=True)
# def cleanup():
#     yield
#     shutil.rmtree(TEST_DATA_DIR, ignore_errors=True)
#
# # -------------------------------------------------------------
# # Тесты на базовые функции логики приложения
# # -------------------------------------------------------------
#
# def test_get_list_operation():
#     """Проверяет чтение и фильтрацию данных из файла"""
#     path_filename = TEST_DATA_DIR + "sample.csv"
#     df = pd.DataFrame({
#         "Название": ["Операция 1", "Операция 2"],
#         "Категория": ["Оплата", "Доход"],
#         "Сумма": [-100, 200],
#         "Валюта": ["RUB", "USD"],
#         "Дата оплаты": ["2023-01-01", "2023-01-02"],
#         "Статус": ["OK", "OK"]
#     })
#     df.to_csv(path_filename, index=False)
#
#     result_df = get_list_operation(path_filename, LIST_OPERATION)
#     assert isinstance(result_df, pd.DataFrame)
#     assert len(result_df) == 2  # обе операции ОК
#
#
# def test_get_period_operation():
#     """Проверяет получение интервала дат по разным критериям"""
#     cases = [
#         ("2023-01-01", "W", [datetime(2022, 12, 26), datetime(2023, 1, 2)]),
#         ("2023-01-01", "M", [datetime(2023, 1, 1), datetime(2023, 1, 2)]),
#         ("2023-01-01", "Y", [datetime(2023, 1, 1), datetime(2023, 1, 2)])
#     ]
#     for case in cases:
#         period = get_period_operation(case[0], case[1])
#         assert isinstance(period, list)
#         assert len(period) == 2
#         assert period == case[2]
#
#
# def test_filter_by_date():
#     """Проверяет фильтрацию данных по датам"""
#     df = pd.DataFrame({
#         "Дата платежа": ["2023-01-01", "2023-01-02", "2023-01-03"],
#         "Сумма": [-100, 200, -50]
#     })
#     df["Дата платежа"] = pd.to_datetime(df["Дата платежа"])
#
#     list_period = [datetime(2023, 1, 1), datetime(2023, 1, 3)]
#     filtered_df = filter_by_date(df, list_period)
#     assert isinstance(filtered_df, pd.DataFrame)
#     assert len(filtered_df) == 3  # все данные попали в фильтр
#
#
# def test_get_exchange_rate():
#     """Имитация внешнего сервиса для проверки получения курса валют"""
#     with responses.RequestsMock() as rsps:
#         rsps.add(responses.GET, URL_EXCHANGE, json={"conversion_rate": 75.0}, status=200)
#         rate = get_exchange_rate("USD")
#         assert rate == 75.0
#
#
# def test_conversion_to_single_currency():
#     """Проверяет конвертацию валют"""
#     df = pd.DataFrame({
#         "Код валюты": ["USD", "EUR", "RUB"],
#         "Сумма": [100, 200, 300]
#     })
#     converted_df = conversion_to_single_currency(df)
#     assert isinstance(converted_df, pd.DataFrame)
#     assert "Сумма_RUB" in converted_df.columns
#
#
# def test_get_data_from_expensess():
#     """Проверяет формирование отчёта по расходам"""
#     df = pd.DataFrame({
#         "Сумма_RUB": [-100, -200, -50],
#         "Категория": ["Еда", "Транспорт", "Связь"]
#     })
#     report = get_data_from_expensess(df)
#     assert isinstance(report, dict)
#     assert "expenses" in report.keys()
#
#
# def test_get_data_from_income():
#     """Проверяет формирование отчёта по доходам"""
#     df = pd.DataFrame({
#         "Сумма_RUB": [100, 200, 50],
#         "Категория": ["Зарплата", "Продажа", "Проценты"]
#     })
#     report = get_data_from_income(df)
#     assert isinstance(report, dict)
#     assert "income" in report.keys()
#
#
# # -------------------------------------------------------------
# # Интеграционные тесты
# # -------------------------------------------------------------
#
# def test_get_user_settings():
#     """Проверяет загрузку настроек пользователя"""
#     settings_file = TEST_DATA_DIR + "settings.json"
#     user_settings = {"user_currencies": ["USD", "EUR"]}
#     with open(settings_file, "w") as f:
#         json.dump(user_settings, f)
#
#     loaded_settings = get_user_settings(settings_file)
#     assert isinstance(loaded_settings, dict)
#     assert "user_currencies" in loaded_settings.keys()
#
#
# def test_get_currency_rates():
#     """Имитация загрузки курсов валют"""
#     with responses.RequestsMock() as rsps:
#         rsps.add(responses.GET, URL_EXCHANGE, json={"conversion_rate": 75.0}, status=200)
#         rates = get_currency_rates({"user_currencies": ["USD"]})
#         assert isinstance(rates, list)
#         assert len(rates) == 1
#         assert rates[0]["currency"] == "USD"
#
#
# def test_get_stock_price_sp_500():
#     """Имитация загрузки текущих цен акций SP500"""
#     with responses.RequestsMock() as rsps:
#         rsps.add(responses.GET, URL_EXCHANGE_SP_500, json=[{"symbol": "AAPL", "price": 150}], status=200)
#         prices = get_stock_price_sp_500({"user_stocks": ["AAPL"]})
#         assert isinstance(prices, list)
#         assert len(prices) == 1
#         assert prices[0]["stock"] == "AAPL"
#
#
# def test_write_json():
#     """Проверяет запись данных в JSON-файл"""
#     data = {"key": "value"}
#     write_json(data, "test_answer.json")
#     assert os.path.exists(TEST_DATA_DIR + "test_answer.json")
