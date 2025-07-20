from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services.tg_user_auth import TelegramUserAuthService
from django.conf import settings
from rest_framework.permissions import IsAuthenticated, AllowAny
import logging
from rest_framework.exceptions import AuthenticationFailed


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
                    'data': {
                        'user': {
                            'telegram_id': user.telegram_id,
                            'username': user.username,
                        },
                        'tokens': {
                            'access': tokens['access'],
                            'refresh': tokens['refresh']
                        }
                    },
                    'message': 'Authentication success!'
                },
                status=status.HTTP_200_OK
            )

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
            auth_header = request.headers.get('Authorization')
            
            if not auth_header or not auth_header.startswith('Bearer '):
                logger.error('Refresh token missing in Authorization header')
                return Response(
                    {'error': 'Authorization header with Bearer token required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            refresh_token = auth_header.split(' ')[1]

            user, new_tokens = TelegramUserAuthService.refresh_user_token(refresh_token)


            response = Response(
                {
                    'data': {
                        'user': {
                            'telegram_id': user.telegram_id,
                            'username': user.username,
                        },
                        'tokens': {
                            'access': new_tokens['access'],
                            'refresh': new_tokens['refresh']
                        }
                    },
                    'message': 'Refresh tokens success!'
                },
                status=status.HTTP_200_OK
            )

            return response
        except AuthenticationFailed as e:
            logger.error(f'Token refresh failed: {e}')
            return Response(
                {'error': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            logger.error(f'Unexpected error during refresh: {e}')
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
