from django.urls import path
from .views import save_telegram_user, get_telegram_user, add_friends, get_friends

urlpatterns = [
    path("save_telegram_user/", save_telegram_user, name="save_telegram_user"),
    path("<int:telegram_id>/", get_telegram_user, name="get_telegram_user"),
    path("<int:telegram_id>/add_friend/", add_friends, name="add_friends"),
    path("<int:telegram_id>/get_friends/", get_friends, name="get_friends"),


]
