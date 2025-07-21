from unittest.mock import patch

import pytest
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from telegram_user.models import TelegramUser
from telegram_user.services.tg_user_auth import TelegramUserAuthService


@pytest.mark.django_db
class TestTelegramUserAuthService:

    # Tests for generate_jwt_token method

    def test_generate_jwt_token_success(self, valid_user_obj):
        tokens = TelegramUserAuthService._generate_jwt_token(valid_user_obj)

        # Проверяем структуру возвращаемого словаря
        assert "access" in tokens
        assert "refresh" in tokens
        assert isinstance(tokens["access"], str)
        assert isinstance(tokens["refresh"], str)

        # Проверяем, что access токен валиден
        access = AccessToken(tokens["access"])
        assert access["telegram_id"] == valid_user_obj.telegram_id

        # Проверяем, что refresh токен валиден
        refresh = RefreshToken(tokens["refresh"])
        assert refresh["telegram_id"] == valid_user_obj.telegram_id

    # Tests for authenticate method

    def test_authenticate_success(
        self, valid_user_data, valid_user_obj, valid_jwt_tokens
    ):
        with patch(
            "telegram_user.services.tg_parser.TelegramDataParser.parse_userData",
            return_value=valid_user_data,
        ):
            with patch(
                "telegram_user.services.tg_user_auth.TelegramUserAuthService._generate_jwt_token",
                return_value=valid_jwt_tokens,
            ):
                user, tokens = TelegramUserAuthService.authenticate("valid_initData")

                assert isinstance(user, TelegramUser)
                assert isinstance(tokens, dict)
                assert user.telegram_id == valid_user_obj.telegram_id
                assert user.first_name == valid_user_obj.first_name
                assert user.last_name == valid_user_obj.last_name
                assert user.username == valid_user_obj.username

                db_user = TelegramUser.objects.get(telegram_id=user.telegram_id)
                assert db_user.username == user.username

    # Tests for refresh_user_token method

    def test_refresh_user_token_success(self, valid_user_obj, valid_user_data):
        """Тест успешного обновления токена"""
        original_token = RefreshToken()
        original_token["telegram_id"] = valid_user_obj.telegram_id
        original_token.access_token["telegram_id"] = valid_user_obj.telegram_id
        refresh_token = str(original_token)
        TelegramUser.objects.create(**valid_user_data)
        with patch(
            "telegram_user.services.tg_user_auth.TelegramUserAuthService._generate_jwt_token",
            return_value={"access": "access_token", "refresh": "refresh_token"},
        ):
            # Обновляем токен
            user, new_tokens = TelegramUserAuthService.refresh_user_token(refresh_token)

            # Проверяем результаты
            assert isinstance(user, TelegramUser)
            assert user.telegram_id == valid_user_obj.telegram_id
            assert "access" in new_tokens
            assert "refresh" in new_tokens
