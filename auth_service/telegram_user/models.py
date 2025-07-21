from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """Абстрактная модель с полями даты создания и обновления."""

    created_at = models.DateTimeField(
        _("created at"),
        auto_now_add=True,
        help_text=_("Date when the object was created"),
    )
    updated_at = models.DateTimeField(
        _("updated at"),
        auto_now=True,
        help_text=_("Date when the object was last updated"),
    )

    class Meta:
        abstract = True


class TelegramUser(TimeStampedModel):
    """Модель для хранения данных о telegram пользователях"""

    telegram_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "auth_telegram_user"
        indexes = [
            models.Index(fields=["telegram_id"], name="telegram_user_telegram_id_idx"),
        ]

    def __str__(self):
        return f"tg_id={self.telegram_id} first_name={self.first_name} last_name={self.last_name} username={self.username}"
