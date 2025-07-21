import hashlib
import hmac
import json
import logging
import os
from datetime import datetime, timedelta
from urllib.parse import parse_qs

from django.core.exceptions import ValidationError
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("telegram_user")


class TelegramDataParser:
    """Класс для валидации и парсинга данных WebAppInitData из Telegram Mini App."""

    INITDATA_MAX_AGE = timedelta(hours=1)

    @classmethod
    def _check_hash(cls, parsedData: dict, bot_token: str) -> bool:
        """Проверяет наличие и подлинность хэша в WebAppInitData Telegram Mini App."""
        try:
            if "hash" not in parsedData.keys():
                logger.error("WebAppInitData doesn't have a 'hash' field")
                raise KeyError("WebAppInitData doesn't have a 'hash' field")

            received_hash = parsedData["hash"][0]
            filtered_data = {k: v[0] for k, v in parsedData.items() if k != "hash"}
            data_check_string = "\n".join(
                f"{k}={v}" for k, v in sorted(filtered_data.items())
            )

            secret_key = hmac.new(
                key=b"WebAppData", msg=bot_token.encode(), digestmod=hashlib.sha256
            ).digest()

            computed_hash = hmac.new(
                key=secret_key, msg=data_check_string.encode(), digestmod=hashlib.sha256
            ).hexdigest()

            return computed_hash == received_hash
        except (IndexError, AttributeError) as e:
            logger.error(f"Invalid hash data format: {e}")
            raise ValidationError(f"Invalid hash data format: {e}")
        except (UnicodeEncodeError, TypeError) as e:
            logger.error(f"Encoding error during hash validation: {e}")
            raise ValidationError(f"Encoding error during hash validation: {e}")

    @classmethod
    def _validate_and_parse(cls, initData: str) -> dict:
        """Общая валидация WebAppInitData для всех методов парсинга."""
        try:
            bot_token = os.getenv("BOT_TOKEN")
            if not bot_token:
                logger.critical("BOT_TOKEN is not configured")
                raise ValidationError("BOT_TOKEN is not configured")

            parsedData = parse_qs(initData)

            auth_date = int(parsedData.get("auth_date")[0])
            if (
                datetime.now() - datetime.fromtimestamp(auth_date)
                > cls.INITDATA_MAX_AGE
            ):
                logger.warning("initData is too old")
                raise ValidationError("initData is too old")

            if not cls._check_hash(parsedData, bot_token):
                logger.warning("Invalid hash signature received")
                raise ValidationError("Invalid hash signature")

            return parsedData
        except KeyError as e:
            logger.error(f"Missing required field: {e}")
            raise ValidationError(f"Missing required field: {e}")
        except ValueError as e:
            logger.error(f"Invalid data format: {e}")
            raise ValidationError(f"Invalid data format: {e}")
        except AttributeError as e:
            logger.error(f"Invalid input data: {e}")
            raise ValidationError(f"Invalid input data: {e}")

    @classmethod
    def parse_userData(cls, initData: str) -> dict:
        """
        Парсит и валидирует WebAppUser Telegram Mini App.
        Возвращает словарь с данными о telegram пользователе.
        """
        try:
            parsedData = cls._validate_and_parse(initData)

            userData = json.loads(parsedData["user"][0])

            return {
                "telegram_id": userData["id"],
                "first_name": userData.get("first_name", ""),
                "last_name": userData.get("last_name", ""),
                "username": userData.get("username", ""),
            }
        except json.JSONDecodeError as e:
            logger.error(f"Invalid user data JSON: {e}")
            raise ValidationError(f"Invalid user data JSON: {e}")
        except IndexError as e:
            logger.error(f"Invalid user data format: {e}")
            raise ValidationError(f"Invalid user data format: {e}")
        except KeyError as e:
            logger.error(f"Missing required user field: {e}")
            raise ValidationError(f"Missing required user field: {e}")
