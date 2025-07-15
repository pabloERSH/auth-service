from rest_framework import APIView
from rest_framework.response import Response
from rest_framework import status
from .services.tg_user_auth import TelegramUserAuthService
from ..auth_service import settings
from rest_framework.permissions import IsAuthenticated, AllowAny


class TelegramUserAuthView(APIView):
    """Класс для обработки запросов на аутентификацию пользователей из Telegram Web App"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Аутентификация через Telegram Mini App"""
        if not (init_data := request.data.get('initData')):
            return Response(
                {'error': 'initData required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = TelegramUserAuthService.authenticate(init_data)
            tokens = TelegramUserAuthService.generate_jwt_token(user)

            response = Response(
                {
                    'user': {
                        'telegram_id': user.telegram_id,
                        'username': user.username,
                    }
                },
                status=status.HTTP_200_OK
            )

            TelegramUserAuthService.set_auth_cookies(response, tokens)

            return response
        except Exception as e:
            return Response(
                {'error': str(e),
                 'message': 'Authentication failed!'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
class TelegramUserRefreshTokenView(APIView):
    permission_classes = [IsAuthenticated]

    """Обновление JWT токенов"""
    def post(self, request):
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['REFRESH_COOKIE'])

        if not refresh_token:
            return Response(
                {'error': 'Refresh token is missing'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            new_tokens = TelegramUserAuthService.refresh_user_token(refresh_token)

            response = Response(
                {'message': "Tokens succesfully refreshed"},
                status=status.HTTP_200_OK
                )

            TelegramUserAuthService.set_auth_cookies(response, new_tokens)
            
            return response
        except Exception as e:
            return Response(
                {'error': str(e),
                 'msg': 'Refresh tokens failed!'}, 
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