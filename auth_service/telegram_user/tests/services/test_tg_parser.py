from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError
from telegram_user.services.tg_parser import TelegramDataParser


def test_check_hash_valid(parsed_valid_data, bot_token):
    result = TelegramDataParser._check_hash(parsed_valid_data, bot_token)
    assert result is True


def test_check_hash_invalid(parsed_valid_data, bot_token):
    parsed_valid_data["hash"] = ["qwertyuiop123asdfghjkl456"]
    result = TelegramDataParser._check_hash(parsed_valid_data, bot_token)
    assert result is False


def test_check_hash_missing_hash(parsed_valid_data, bot_token):
    del parsed_valid_data["hash"]
    with pytest.raises(KeyError, match="WebAppInitData doesn't have a 'hash' field"):
        TelegramDataParser._check_hash(parsed_valid_data, bot_token)


def test_validate_and_parse_valid(
    valid_init_data, bot_token, parsed_valid_data, valid_datetime_mock
):
    with patch("os.getenv", return_value=bot_token):
        with patch("telegram_user.services.tg_parser.datetime", valid_datetime_mock):
            with patch(
                "telegram_user.services.tg_parser.TelegramDataParser._check_hash",
                return_value=True,
            ):
                result = TelegramDataParser._validate_and_parse(valid_init_data)
                assert result == parsed_valid_data


def test_validate_and_parse_no_bot_token(valid_init_data):
    with patch("os.getenv", return_value=None):
        with pytest.raises(ValidationError, match="BOT_TOKEN is not configured"):
            TelegramDataParser._validate_and_parse(valid_init_data)


def test_validate_and_parse_old_date(valid_init_data, bot_token, expired_datetime_mock):
    with patch("os.getenv", return_value=bot_token):
        with patch("telegram_user.services.tg_parser.datetime", expired_datetime_mock):
            with pytest.raises(ValidationError, match="initData is too old"):
                TelegramDataParser._validate_and_parse(valid_init_data)


def test_validate_and_parse_bad_hash(valid_init_data, bot_token, valid_datetime_mock):
    with patch("os.getenv", return_value=bot_token):
        with patch(
            "telegram_user.services.tg_parser.TelegramDataParser._check_hash",
            return_value=False,
        ):
            with patch(
                "telegram_user.services.tg_parser.datetime", valid_datetime_mock
            ):
                with pytest.raises(ValidationError, match="Invalid hash signature"):
                    TelegramDataParser._validate_and_parse(valid_init_data)


def test_parse_userData_valid(parsed_valid_data, valid_init_data, valid_user_data):
    with patch(
        "telegram_user.services.tg_parser.TelegramDataParser._validate_and_parse",
        return_value=parsed_valid_data,
    ):
        result = TelegramDataParser.parse_userData(valid_init_data)
        assert result == valid_user_data


def test_parse_userData_missing_user(parsed_valid_data, valid_init_data):
    del parsed_valid_data["user"]
    with patch(
        "telegram_user.services.tg_parser.TelegramDataParser._validate_and_parse",
        return_value=parsed_valid_data,
    ):
        with pytest.raises(
            ValidationError, match="Missing required user field: 'user'"
        ):
            TelegramDataParser.parse_userData(valid_init_data)


def test_parse_userData_missing_id(parsed_valid_data, valid_init_data, valid_user_data):
    del valid_user_data["telegram_id"]
    with patch(
        "telegram_user.services.tg_parser.TelegramDataParser._validate_and_parse",
        return_value=parsed_valid_data,
    ):
        with patch("json.loads", return_value=valid_user_data):
            with pytest.raises(
                ValidationError, match="Missing required user field: 'id'"
            ):
                TelegramDataParser.parse_userData(valid_init_data)
