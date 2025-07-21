import logging

from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .services.tg_user_auth import TelegramUserAuthService

logger = logging.getLogger("telegram_user")


class TelegramUserAuthView(APIView):
    """Класс для обработки запросов на аутентификацию пользователей из Telegram Web App"""

    permission_classes = [AllowAny]

    def post(self, request):
        """Аутентификация через Telegram Mini App"""
        try:
            if not (init_data := request.data.get("initData")):
                logger.error("initData has not been sent")
                return Response(
                    {"error": "initData required"}, status=status.HTTP_400_BAD_REQUEST
                )

            user, tokens = TelegramUserAuthService.authenticate(init_data)

            response = Response(
                {
                    "data": {
                        "user": {
                            "telegram_id": user.telegram_id,
                            "username": user.username,
                        },
                        "tokens": {
                            "access": tokens["access"],
                            "refresh": tokens["refresh"],
                        },
                    },
                    "message": "Authentication success!",
                },
                status=status.HTTP_200_OK,
            )

            return response
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return Response(
                {"error": str(e), "message": "Authentication failed!"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class TelegramUserRefreshTokenView(APIView):
    """Класс для обработки запросов на обновление токенов пользователей из Telegram Web App"""

    permission_classes = [AllowAny]

    """Обновление JWT токенов"""

    def post(self, request):
        try:
            if not (refresh_token := request.data.get("refresh_token")):
                logger.error("Refresh token has not been sent")
                return Response(
                    {"error": "Refresh token required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user, new_tokens = TelegramUserAuthService.refresh_user_token(refresh_token)

            response = Response(
                {
                    "data": {
                        "user": {
                            "telegram_id": user.telegram_id,
                            "username": user.username,
                        },
                        "tokens": {
                            "access": new_tokens["access"],
                            "refresh": new_tokens["refresh"],
                        },
                    },
                    "message": "Refresh tokens success!",
                },
                status=status.HTTP_200_OK,
            )

            return response
        except AuthenticationFailed as e:
            logger.error(f"Token refresh failed: {e}")
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error(f"Unexpected error during refresh: {e}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
