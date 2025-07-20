from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

class JWTAuthMiddleware(MiddlewareMixin):
    """Проверяет JWT токены и аутентифицирует пользователя"""
    def process_request(self, request):
        if request.path in ['/auth/login/', '/auth/refresh/']:
            return

        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            access_token = auth_header.split(' ')[1]
            try:
                jwt_auth = JWTAuthentication()
                validated_token = jwt_auth.get_validated_token(access_token)
                request.user = jwt_auth.get_user(validated_token)
            except AuthenticationFailed:
                pass
            