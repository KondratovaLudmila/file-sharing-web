import pytest
from src.services.hash_handler import hash_password, check_password

@pytest.fixture
def sample_password():
    return "test_password"

def test_hash_password(sample_password):
    # Тестирование хеширования пароля
    password = sample_password
    hashed_password = hash_password(password)
    assert hashed_password is not None
    assert hashed_password != password

def test_check_password(sample_password):
    # Тестирование проверки верификации пароля
    password = sample_password
    hashed_password = hash_password(password)
    result = check_password(password, hashed_password)
    assert result is True

def test_check_password_wrong(sample_password):
    # Тестирование проверки неверного пароля
    password = sample_password
    wrong_password = "wrong_password"
    hashed_password = hash_password(password)
    result = check_password(wrong_password, hashed_password)
    assert result is False