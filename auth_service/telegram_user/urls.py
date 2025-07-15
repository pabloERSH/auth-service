from django.urls import path
from .views import (
    TelegramUserAuthView,
    TelegramUserRefreshTokenView,
    TelegramUserLogoutView
)

urlpatterns = [
    # Аутентификация
    path('auth/login/', TelegramUserAuthView.as_view(), name='telegram-login'),
    
    # Обновление токенов
    path('auth/refresh/', TelegramUserRefreshTokenView.as_view(), name='token-refresh'),
    
    # Выход из системы
    path('auth/logout/', TelegramUserLogoutView.as_view(), name='logout'),
]