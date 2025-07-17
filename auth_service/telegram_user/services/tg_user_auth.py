from ..models import TelegramUser
from .tg_parser import TelegramDataParser
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.middleware import csrf
from rest_framework_simplejwt.exceptions import TokenError
from django.core.exceptions import ValidationError
from django.db import IntegrityError, DatabaseError
import logging


logger = logging.getLogger('telegram_user')


class TelegramUserAuthService:
    """Класс для аутентификации Telegram пользователей и управления JWT токенами."""
    @classmethod
    def authenticate(cls, initData: str) -> TelegramUser:
        """Валидация initData и получение данных пользователя или его создание/изменение"""
        try:
            userData = TelegramDataParser.parse_userData(initData)

            user, _ = TelegramUser.objects.update_or_create(
                telegram_id = userData['telegram_id'],
                defaults={
                    'first_name': userData['first_name'],
                    'last_name': userData['last_name'],
                    'username': userData['username']
                }
            ) 

            return user
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
    def generate_jwt_token(cls, user: TelegramUser) -> dict:
        """Генерация JWT пары (access + refresh)"""
        if not isinstance(user, TelegramUser):
            logger.error(f"Expected TelegramUser, got {type(user)}")
            raise TypeError("user must be a TelegramUser")

        refresh = RefreshToken.for_user(user)

        refresh['telegram_id'] = user.telegram_id

        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }
    
    @classmethod
    def set_auth_cookies(cls, response, tokens: dict) -> None:
        """Устанавливает JWT + CSRF cookies с настройками из settings.py"""
        try:
            # Access Token
            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                value=tokens['access'],
                httponly=True,
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
                path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH']
            )

            # Refresh Token
            response.set_cookie(
                key=settings.SIMPLE_JWT['REFRESH_COOKIE'],
                value=tokens['refresh'],
                httponly=True,
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
                path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH']
            )

            # CSRF Token
            response.set_cookie(
                key='csrftoken',
                value=csrf.get_token(response.request),
                secure=settings.CSRF_COOKIE_SECURE,
                samesite='Strict',
                httponly=False
            )
        except KeyError as e:
            logger.error(f"Set auth cookies failed: {e}")
            raise ValidationError(f"Set auth cookies failed: {e}")

    @classmethod
    def logout(cls, response) -> None:
        """Очистка auth cookies"""
        response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
        response.delete_cookie(settings.SIMPLE_JWT['REFRESH_COOKIE'])

    @classmethod
    def refresh_user_token(cls, refresh_token: str) -> dict:
        try:
            refresh = RefreshToken(refresh_token)
            tg_id = refresh.get('telegram_id')
            if not tg_id:
                raise TokenError('Telegram ID not found in token')

            user = TelegramUser.objects.get(telegram_id = tg_id)

            new_tokens = cls.generate_jwt_token(user)
            return new_tokens
        except TokenError as e:
            logger.error(f"Refresh user token failed: {e}")
            raise TokenError(f"Refresh user token failed: {e}")
