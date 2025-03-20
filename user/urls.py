from django.urls import path
from .views import save_telegram_user

urlpatterns = [
    path("save_telegram_user/", save_telegram_user, name="save_telegram_user"),
]