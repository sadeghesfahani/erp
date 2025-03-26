from django.urls import path
from .views import save_telegram_user, get_telegram_user

urlpatterns = [
    path("save_telegram_user/", save_telegram_user, name="save_telegram_user"),
    path("<int:telegram_id>/", get_telegram_user, name="get_telegram_user"),

]
