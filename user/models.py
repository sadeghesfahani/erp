from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class TelegramUser(models.Model):
    """Stores Telegram user data independently from Aiogram"""
    telegram_id = models.BigIntegerField(unique=True)  # Unique Telegram user ID
    username = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    default_language = models.CharField(max_length=20, blank=True, null=True)

    # Optional link to Django user (for authenticated users)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} (@{self.username}) - {self.telegram_id}"