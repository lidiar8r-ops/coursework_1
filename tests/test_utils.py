import pytest

from src.utils import get_list_transaction


# Тест успешного считывания данных
@pytest.mark.parametrize("expected", [[{"id": 1}, {"id": 2}, {"id": 5}]])
def test_get_list_transaction_valid(create_temp_files, expected):
    actual_result = get_list_transaction(create_temp_files["valid_json_path"])
    assert isinstance(actual_result, list)
    assert len(actual_result) > 0
    assert actual_result == expected


# Тест обработки неправильного формата JSON
def test_get_list_transaction_invalid_json(create_temp_files):
    result = get_list_transaction(create_temp_files["invalid_json_path"])
    assert isinstance(result, list)
    assert len(result) == 0


# Тест обработки несуществующего файла
def test_get_list_transaction_nonexistent_file(create_temp_files):
    result = get_list_transaction(create_temp_files["nonexistent_file_path"])
    assert isinstance(result, list)
    assert len(result) == 0
