from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    first_name = models.CharField(
        verbose_name='name',
        max_length=100, default=None,
        blank=True, null=True
    )
    last_name = models.CharField(
        verbose_name='surname',
        max_length=100, default=None,
        blank=True, null=True
    )

    telegram_id = models.CharField(
        max_length=50, verbose_name="Telegram ID",
        blank=True, null=True
    )

    def __str__(self):
        return str(self.username)
