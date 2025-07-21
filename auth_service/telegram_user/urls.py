from django.urls import path

from telegram_user.views import TelegramUserAuthView, TelegramUserRefreshTokenView

urlpatterns = [
    path("auth/login/", TelegramUserAuthView.as_view(), name="telegram-login"),
    path("auth/refresh/", TelegramUserRefreshTokenView.as_view(), name="token-refresh"),
]
