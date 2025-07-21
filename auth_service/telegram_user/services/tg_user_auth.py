import logging

from django.core.exceptions import ValidationError
from django.db import DatabaseError, IntegrityError
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import TelegramUser
from .tg_parser import TelegramDataParser

logger = logging.getLogger("telegram_user")


class TelegramUserAuthService:
    """Класс для аутентификации Telegram пользователей и управления JWT токенами."""

    @classmethod
    def authenticate(cls, initData: str) -> tuple:
        """Валидация initData и получение данных пользователя или его создание/изменение"""
        try:
            userData = TelegramDataParser.parse_userData(initData)

            user, _ = TelegramUser.objects.update_or_create(
                telegram_id=userData["telegram_id"],
                defaults={
                    "first_name": userData["first_name"],
                    "last_name": userData["last_name"],
                    "username": userData["username"],
                },
            )

            tokens = cls._generate_jwt_token(user)

            return (user, tokens)
        except ValidationError as e:
            logger.error(f"Telegram data validation failed: {e}")
            raise AuthenticationFailed(f"Telegram data validation failed: {e}")
        except IntegrityError as e:
            logger.error(f"Database integrity error: {e}")
            raise AuthenticationFailed(f"Database integrity error: {e}")
        except DatabaseError as e:
            logger.error(f"Database operation failed: {e}")
            raise AuthenticationFailed(f"Database operation failed: {e}")

    @classmethod
    def _generate_jwt_token(cls, user: TelegramUser) -> dict:
        """Генерация JWT пары (access + refresh)"""
        if not isinstance(user, TelegramUser):
            logger.error(f"Expected TelegramUser, got {type(user)}")
            raise TypeError("user must be a TelegramUser")

        refresh = RefreshToken()

        refresh.access_token["telegram_id"] = user.telegram_id
        refresh["telegram_id"] = user.telegram_id

        return {"access": str(refresh.access_token), "refresh": str(refresh)}

    @classmethod
    def refresh_user_token(cls, refresh_token: str) -> tuple:
        try:
            refresh = RefreshToken(refresh_token)
            if refresh.token_type != "refresh":
                raise InvalidToken("Invalid token type")
            tg_id = refresh.get("telegram_id")
            if not isinstance(tg_id, int):
                raise InvalidToken(
                    f"Field 'telegram_id' expected a number but got {type(tg_id)}"
                )

            user = TelegramUser.objects.get(telegram_id=tg_id)

            refresh.blacklist()

            new_tokens = cls._generate_jwt_token(user)

            return (user, new_tokens)
        except InvalidToken as e:
            logger.error(f"Invalid refresh token: {e}")
            raise AuthenticationFailed("Invalid or expired refresh token")
        except TelegramUser.DoesNotExist:
            logger.error(f"User with telegram_id={tg_id} not found")
            raise AuthenticationFailed("User not found")
        except TokenError as e:
            logger.error(f"Refresh token processing failed: {e}")
            raise AuthenticationFailed("Token processing error")


# @classmethod
# def set_auth_cookies(cls, response, tokens: dict) -> None:
#     """Устанавливает JWT + CSRF cookies с настройками из settings.py"""
#     try:
#         # Access Token
#         response.set_cookie(
#             key=settings.SIMPLE_JWT['AUTH_COOKIE'],
#             value=tokens['access'],
#             httponly=True,
#             secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
#             samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
#             max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
#             path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH']
#         )

#         # Refresh Token
#         response.set_cookie(
#             key=settings.SIMPLE_JWT['REFRESH_COOKIE'],
#             value=tokens['refresh'],
#             httponly=True,
#             secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
#             samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
#             max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
#             path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH']
#         )

#         # CSRF Token
#         response.set_cookie(
#             key='csrftoken',
#             value=csrf.get_token(response.request),
#             secure=settings.CSRF_COOKIE_SECURE,
#             samesite='Strict',
#             httponly=False
#         )
#     except KeyError as e:
#         logger.error(f"Set auth cookies failed: {e}")
#         raise ValidationError(f"Set auth cookies failed: {e}")
