from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import json
from .models import TelegramUser

@csrf_exempt  # Disable CSRF protection for simplicity
def save_telegram_user(request):
    """Receives Telegram user data from the Aiogram script and saves it"""
    if request.method == "POST":
        data = json.loads(request.body)
        telegram_id = data.get("telegram_id")
        username = data.get("username", "")
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        default_language = data.get("default_language", "")


        if not telegram_id:
            return JsonResponse({"error": "Missing telegram_id"}, status=400)

        user, created = TelegramUser.objects.update_or_create(
            telegram_id=telegram_id,
            defaults={"username": username, "first_name": first_name, "last_name": last_name, "default_language": default_language},
        )

        return JsonResponse({"message": "User saved", "created": created})

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def get_telegram_user(request, telegram_id):
    """Retrieve a Telegram user's data from Django"""
    print(telegram_id)
    user = get_object_or_404(TelegramUser, telegram_id=telegram_id)

    data = {
        "telegram_id": user.telegram_id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    }
    return JsonResponse(data)