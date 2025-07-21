import pytest

# Fixtures


@pytest.fixture(autouse=True)
def db_cleanup(request):
    """Очистка БД после теста"""
    if "django_db" in request.keywords:
        yield
        from telegram_user.models import TelegramUser

        TelegramUser.objects.all().delete()
    else:
        yield


@pytest.fixture
def valid_user_data():
    return {
        "telegram_id": 123456789,
        "first_name": "Test",
        "last_name": "User",
        "username": "testtguser",
    }


@pytest.fixture
def valid_user_obj(valid_user_data, request):
    """Фикстура с объектом пользователя в БД (только для тестов, требующих БД)"""
    if "django_db" in request.keywords:
        from telegram_user.models import TelegramUser

        return TelegramUser(**valid_user_data)
    else:
        return valid_user_data


@pytest.fixture
def valid_jwt_tokens():
    return {"access": "access_token", "refresh": "refresh_token"}
