from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

class JWTAuthMiddleware(MiddlewareMixin):
    """Проверяет JWT из куки и аутентифицирует пользователя"""

    def process_request(self, request):
        if request.path in ['/auth/login/']:
            return

        access_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])
        
        if access_token:
            try:
                jwt_auth = JWTAuthentication()
                validated_token = jwt_auth.get_validated_token(access_token)
                request.user = jwt_auth.get_user(validated_token)
            except AuthenticationFailed:
                pass  # Пользователь не аутентифицирован