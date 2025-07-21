from datetime import datetime
from unittest.mock import MagicMock
from urllib.parse import parse_qs

import pytest

# Fixtures


@pytest.fixture
def bot_token():
    """Фикстура с тестовым Telegram Bot Token"""
    return "1234567890:FAKE_BOT_TOKEN"


@pytest.fixture
def valid_init_data():
    """Фикстура с тестовой строкой Telegram WebAppInitData"""
    return (
        "query_id=test_query_id_123&"
        "user=%7B%22id%22%3A123456789%2C%22"
        "first_name%22%3A%22Test%22%2C%22"
        "last_name%22%3A%22User%22%2C%22"
        "username%22%3A%22testtguser%22%2C%22"
        "language_code%22%3A%22ru%22%2C%22"
        "is_premium%22%3Atrue%7D&"
        "auth_date=1752871138&"
        "hash=78fa9f5a4ab5ee95d1a5b45bf72d1ddfc3b385d488c7c87bb6a7d6d7760adfd4"
    )


@pytest.fixture
def parsed_valid_data(valid_init_data):
    """Фикстура с тестовой строкой Telegram WebAppInitData в виде словаря"""
    return parse_qs(valid_init_data)


@pytest.fixture
def valid_datetime_mock():
    """Фикстура с временем не позже часа от указанного в тестовой Telegram WebAppInitData"""
    mock = MagicMock()
    mock.now.return_value = datetime.fromtimestamp(1752871138 + 1500)
    mock.fromtimestamp.side_effect = datetime.fromtimestamp
    return mock


@pytest.fixture
def expired_datetime_mock():
    """Фикстура с временем позже часа от указанного в тестовой Telegram WebAppInitData"""
    mock = MagicMock()
    mock.now.return_value = datetime.fromtimestamp(1752871138 + 3601)
    mock.fromtimestamp.side_effect = datetime.fromtimestamp
    return mock
