from django.urls import path
from .views import (
    TelegramUserAuthView,
    TelegramUserRefreshTokenView,
    TelegramUserLogoutView
)

urlpatterns = [
    path('auth/login/', TelegramUserAuthView.as_view(), name='telegram-login'),
    path('auth/refresh/', TelegramUserRefreshTokenView.as_view(), name='token-refresh'),
]
