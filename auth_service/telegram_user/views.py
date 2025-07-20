from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services.tg_user_auth import TelegramUserAuthService
from django.conf import settings
from rest_framework.permissions import IsAuthenticated, AllowAny
import logging


logger = logging.getLogger('telegram_user')


class TelegramUserAuthView(APIView):
    """Класс для обработки запросов на аутентификацию пользователей из Telegram Web App"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Аутентификация через Telegram Mini App"""
        try:
            if not (init_data := request.data.get('initData')):
                logger.critical("initData has not been sent")
                return Response(
                    {'error': 'initData required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
            user, tokens = TelegramUserAuthService.authenticate(init_data)

            response = Response(
                {
                    'user': {
                        'telegram_id': user.telegram_id,
                        'username': user.username,
                    },
                    'message': 'Authentication success!'
                },
                status=status.HTTP_200_OK
            )

            TelegramUserAuthService.set_auth_cookies(response, tokens)

            return response
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return Response(
                {'error': str(e),
                 'message': 'Authentication failed!'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
class TelegramUserRefreshTokenView(APIView):
    permission_classes = [IsAuthenticated]

    """Обновление JWT токенов"""
    def post(self, request):
        try:
            refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['REFRESH_COOKIE'])

            if not refresh_token:
                logger.error("Refresh token has not been sent!")
                return Response(
                    {'error': 'Refresh token is missing'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            new_tokens = TelegramUserAuthService.refresh_user_token(refresh_token)

            response = Response(
                {'message': "Tokens successfully refreshed"},
                status=status.HTTP_200_OK
                )

            TelegramUserAuthService.set_auth_cookies(response, new_tokens)
            
            return response
        except Exception as e:
            logger.error(f'Refresh tokens failed: {e}')
            return Response(
                {'error': str(e),
                 'message': 'Refresh tokens failed!'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
class TelegramUserLogoutView(APIView):
    """Выход из системы (logout) - очищение cookie."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        response = Response(
            {'message': 'Successfully logged out'},
            status=status.HTTP_200_OK
        )
        
        response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
        response.delete_cookie(settings.SIMPLE_JWT['REFRESH_COOKIE'])
        response.delete_cookie('csrftoken')
        
        return response
    