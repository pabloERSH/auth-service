from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def valid_init_data():
    return {"initData": "valid_init_data_string"}


@pytest.mark.django_db
class TestTelegramUserAuthView:
    url = reverse("telegram-login")

    def test_authentication_success(
        self, valid_user_obj, valid_jwt_tokens, api_client, valid_init_data
    ):
        with patch(
            "telegram_user.services.tg_user_auth.TelegramUserAuthService.authenticate",
            return_value=(valid_user_obj, valid_jwt_tokens),
        ):
            response = api_client.post(self.url, data=valid_init_data)

            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["message"] == "Authentication success!"
            assert (
                response_data["data"]["user"]["telegram_id"]
                == valid_user_obj.telegram_id
            )
            assert response_data["data"]["user"]["username"] == valid_user_obj.username
            assert (
                response_data["data"]["tokens"]["access"] == valid_jwt_tokens["access"]
            )
            assert (
                response_data["data"]["tokens"]["refresh"]
                == valid_jwt_tokens["refresh"]
            )

    def test_authentication_missing_data(self, api_client):
        response = api_client.post(self.url, data={})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert response_data["error"] == "initData required"

    def test_authentication_invalid_data(self, api_client):
        with patch(
            "telegram_user.services.tg_user_auth.TelegramUserAuthService.authenticate",
            side_effect=ValidationError("Invalid initData"),
        ):
            response = api_client.post(self.url, data={"initData": "invalid initData"})

            assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTelegramUserRefreshTokenView:
    url = reverse("token-refresh")

    def test_token_refresh_success(self, api_client, valid_user_obj, valid_jwt_tokens):
        with patch(
            "telegram_user.services.tg_user_auth.TelegramUserAuthService.refresh_user_token",
            return_value=(valid_user_obj, valid_jwt_tokens),
        ):
            response = api_client.post(
                self.url, data={"refresh_token": "valid refresh token"}
            )

            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["message"] == "Refresh tokens success!"
            assert (
                response_data["data"]["user"]["telegram_id"]
                == valid_user_obj.telegram_id
            )
            assert response_data["data"]["user"]["username"] == valid_user_obj.username
            assert (
                response_data["data"]["tokens"]["access"] == valid_jwt_tokens["access"]
            )
            assert (
                response_data["data"]["tokens"]["refresh"]
                == valid_jwt_tokens["refresh"]
            )

    def test_token_refresh_missing_refresh(self, api_client):
        response = api_client.post(self.url, data={})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_token_refresh_invalid_refresh(self, api_client):
        with patch(
            "telegram_user.services.tg_user_auth.TelegramUserAuthService.refresh_user_token",
            side_effect=AuthenticationFailed("Invalid refresh token"),
        ):
            response = api_client.post(
                self.url, data={"refresh_token": "invalid refresh token"}
            )

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
